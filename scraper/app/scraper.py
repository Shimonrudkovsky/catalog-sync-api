import asyncio
import urllib
import urllib.parse

import httpx
from asyncpg import PostgresError
from bs4 import BeautifulSoup
from db.queries import INSERT_DATA_QUERY
from httpx import HTTPError
from loguru import logger
from models.models import (
    REQUEST_DELAY,
    CatalogueLevels,
    CatalogueLink,
    CataloguePart,
    PartDetails,
    ScraperContext,
    ScraperPayload,
)

CONCURRENT_REQUESTS = 5


async def fetch_html(payload: ScraperPayload, ctx: ScraperContext) -> str:
    async with ctx.semaphore:
        await asyncio.sleep(payload.delay)
        try:
            url = payload.link.url.geturl()
            logger.debug(f"fetching {url}")
            resp = await ctx.http_client.get(url)
            resp.raise_for_status()
            return resp.text
        except HTTPError as err:
            logger.error(f"failed to fetch {url}: {err}")
            raise err


def extract_links(soup: BeautifulSoup, payload: ScraperPayload) -> list[CatalogueLink]:
    catalogue_divs = [i for i in soup.find_all("div") if i.get("class") and i.get("class")[-1] == payload.level]
    list_items = catalogue_divs[0].find_all("li")
    parsed_links = []
    for li in list_items[:2]:  # TODO: don't forget to remove
        a_tag = li.find("a")
        if a_tag:
            link = a_tag.get("href")
            catalogue_link = CatalogueLink(url=payload.link.url._replace(path=link), directory=payload.link.directory)
            text = a_tag.text.strip()
            catalogue_link.directory[payload.level] = text
            parsed_links.append(catalogue_link)

    return parsed_links


async def enqueue_links(links: list[CatalogueLink], next_level: CatalogueLevels, ctx: ScraperContext) -> None:
    for link in links:
        new_payload = ScraperPayload(link=link, level=next_level)
        logger.debug(f"queue put {new_payload}")
        await ctx.queue.put(new_payload)


def parse_parts(links: list[CatalogueLink]) -> list[PartDetails]:
    parsed_parts = []
    for link in links:
        part_number, part_category = link.directory[CatalogueLevels.PARTS].split(" - ")
        part = CataloguePart(number=part_number, category=part_category, url=link.url.geturl())
        part_info = PartDetails(
            maker=link.directory[CatalogueLevels.MAKERS],
            category=link.directory[CatalogueLevels.CATEGORIES],
            model=link.directory[CatalogueLevels.MODELS],
            part=part,
        )
        parsed_parts.append(part_info)

    return parsed_parts


async def process_page(payload: ScraperPayload, ctx: ScraperContext) -> None:
    url = payload.link.url.geturl()
    level = payload.level
    if url in ctx.visited_urls:
        logger.debug(f"visited url: {url}")
        return

    try:
        html_text = await fetch_html(payload, ctx)
    except HTTPError as err:
        payload.attempt += 1
        payload.delay *= 2
        logger.debug(f"retrying fetch {url.geturl()} - attempt:{payload.attempt}, delay: {payload.delay}, error: {err}")
        await ctx.queue.put(payload)

    soup = BeautifulSoup(html_text, "lxml")
    links = extract_links(soup=soup, payload=payload)

    if level == CatalogueLevels.MAKERS:
        await enqueue_links(links=links, next_level=CatalogueLevels.CATEGORIES, ctx=ctx)
    elif level == CatalogueLevels.CATEGORIES:
        await enqueue_links(links=links, next_level=CatalogueLevels.MODELS, ctx=ctx)
    elif level == CatalogueLevels.MODELS:
        await enqueue_links(links=links, next_level=CatalogueLevels.PARTS, ctx=ctx)
    elif level == CatalogueLevels.PARTS:
        parts = parse_parts(links=links)
        for part in parts:
            try:
                logger.debug(f"query: {INSERT_DATA_QUERY}, args: {part}")
                await ctx.db_connection.execute(
                    INSERT_DATA_QUERY,
                    part.maker,
                    part.category,
                    part.model,
                    part.part.number,
                    part.part.category,
                    part.part.url,
                )
                logger.debug(f"insert query complete args: {part}")
            except PostgresError as err:
                raise err  # TODO: raise another

    ctx.visited_urls.add(url)


async def scraper_worker(ctx: ScraperContext):
    while not ctx.queue.empty():
        payload = await ctx.queue.get()
        try:
            await process_page(payload, ctx)
        except Exception as err:
            logger.error(err)
            raise
        finally:
            ctx.queue.task_done()


async def run_scraper(database):
    # init scraper
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    base_url = "https://www.urparts.com/"
    url = f"{base_url}index.cfm/page/catalogue"
    async with httpx.AsyncClient() as http_client:
        context = ScraperContext(
            semaphore=semaphore,
            visited_urls=set(),
            queue=queue,
            http_client=http_client,
            db_connection=database,
        )
        link = CatalogueLink(url=urllib.parse.urlparse(url))
        await queue.put(ScraperPayload(link=link, level=CatalogueLevels.MAKERS, attempt=1, delay=REQUEST_DELAY))
        tasks = [asyncio.create_task(scraper_worker(ctx=context)) for _ in range(CONCURRENT_REQUESTS)]
        await queue.join()
        for task in tasks:
            task.cancel()
