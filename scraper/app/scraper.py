import asyncio
import urllib
import urllib.parse
from datetime import datetime

import httpx
from asyncpg import PostgresError
from bs4 import BeautifulSoup
from httpx import HTTPError
from loguru import logger

from db.database import Postgres
from db.queries import GET_NEW_SCAN_ID, INSERT_DATA_QUERY, SCAN_ENDED
from models import (
    REQUEST_DELAY,
    CatalogueLevels,
    CatalogueLink,
    CataloguePart,
    PartDetails,
    ScraperContext,
    ScraperPayload,
    ScrapingStatus,
)

CONCURRENT_REQUESTS = 10


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
    for li in list_items:
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
        splitted_link = link.directory[CatalogueLevels.PARTS].split(" - ")
        part_number = splitted_link[0]
        part_category = " - ".join(splitted_link[1:])
        part = CataloguePart(number=part_number, category=part_category, url=link.url.geturl())
        part_info = PartDetails(
            maker=link.directory[CatalogueLevels.MAKERS],
            category=link.directory[CatalogueLevels.CATEGORIES],
            model=link.directory[CatalogueLevels.MODELS],
            part=part,
        )
        parsed_parts.append(part_info)

    return parsed_parts


async def insert_parts(parts: list[PartDetails], ctx: ScraperContext):
    try:
        parts_set = set(
            [(p.maker, p.category, p.model, p.part.number, p.part.category, p.part.url, ctx.scan_id) for p in parts]
        )
        await ctx.db_connection.executemany(
            INSERT_DATA_QUERY,
            parts_set,
        )
        if len(parts) > len(parts_set):
            logger.warning(f"duplicates in bulk insert: {len(parts) - len(parts_set)}")
        logger.debug(f"insert query complete items: {len(parts_set)}")
    except PostgresError as err:
        logger.error(f"db insertion failed: items: {len(parts_set)}")
        raise err


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
        if payload.attempt <= 3:
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
        await insert_parts(parts=parts, ctx=ctx)

    ctx.visited_urls.add(url)


async def scraper_worker(ctx: ScraperContext):
    ctx.scraping_status.scraping = True
    while not ctx.queue.empty():
        payload = await ctx.queue.get()
        try:
            await process_page(payload, ctx)
            ctx.scraping_status.scraping_counter += 1
        except Exception as err:
            logger.error(err)
        finally:
            ctx.queue.task_done()


async def run_scraper(database: Postgres, status: ScrapingStatus):
    logger.info("running scraping...")
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)
    base_url = "https://www.urparts.com/"
    url = f"{base_url}index.cfm/page/catalogue"

    scan_id = await database.fetchval(GET_NEW_SCAN_ID, datetime.now())

    async with httpx.AsyncClient() as http_client:
        context = ScraperContext(
            semaphore=semaphore,
            visited_urls=set(),
            queue=queue,
            http_client=http_client,
            db_connection=database,
            scan_id=scan_id,
            scraping_status=status,
        )
        link = CatalogueLink(url=urllib.parse.urlparse(url))
        status.scraping = True
        try:
            await queue.put(ScraperPayload(link=link, level=CatalogueLevels.MAKERS, attempt=1, delay=REQUEST_DELAY))
            tasks = [asyncio.create_task(scraper_worker(ctx=context)) for _ in range(CONCURRENT_REQUESTS)]
            await queue.join()
            for task in tasks:
                task.cancel()
        finally:
            status.scraping = False

    await database.execute(SCAN_ENDED, scan_id, datetime.now())
