from unittest.mock import patch
from urllib.parse import urlparse

import pytest
from app.scraper import enqueue_links, extract_links, fetch_html, insert_parts, parse_parts, process_page
from bs4 import BeautifulSoup
from models.models import CatalogueLevels, CatalogueLink, CataloguePart, PartDetails, ScraperPayload


@pytest.mark.asyncio
async def test_fetch_html_success(fake_context):
    fake_context.http_client.get.return_value.status_code = 200
    fake_context.http_client.get.return_value.text = "<html></html>"

    url = "https://example.com"
    link = CatalogueLink(url=urlparse(url))
    payload = ScraperPayload(
        link=link,
        level=CatalogueLevels.CATEGORIES,
    )

    html = await fetch_html(payload, fake_context)

    assert html == "<html></html>"
    fake_context.http_client.get.assert_called_once_with(url)


def test_extract_links_success():
    html_text = """
    <div class="c_container allmakes">
        <li><a href="/link1">Link 1</a></li>
        <li><a href="/link2">Link 2</a></li>
    </div>
    """
    soup = BeautifulSoup(html_text, "lxml")
    payload = ScraperPayload(
        link=CatalogueLink(url=urlparse("https://example.com"), directory={}),
        level=CatalogueLevels.MAKERS,
    )

    links = extract_links(soup, payload)

    assert len(links) == 2
    assert links[0].url.path == "/link1"
    assert links[0].directory[CatalogueLevels.MAKERS] == "Link 1"
    assert links[1].url.path == "/link2"
    assert links[1].directory[CatalogueLevels.MAKERS] == "Link 2"


@pytest.mark.asyncio
async def test_enqueue_links_success(fake_context):
    links = [CatalogueLink(url=urlparse("https://example.com"), directory={})]

    await enqueue_links(links, CatalogueLevels.CATEGORIES, fake_context)

    result = await fake_context.queue.get()
    expected = ScraperPayload(link=links[0], level=CatalogueLevels.CATEGORIES)
    assert result == expected


def test_parse_parts_success():
    directory = {
        CatalogueLevels.MAKERS: "MAKER1",
        CatalogueLevels.CATEGORIES: "CATEGORY1",
        CatalogueLevels.MODELS: "MODEL1",
        CatalogueLevels.PARTS: "4242 - FOO",
    }
    links = [CatalogueLink(url=urlparse("https://example.com"), directory=directory)]

    result = parse_parts(links=links)
    expected = [
        PartDetails(
            maker="MAKER1",
            category="CATEGORY1",
            model="MODEL1",
            part=CataloguePart(number="4242", category="FOO", url="https://example.com"),
        )
    ]

    assert result == expected


@pytest.mark.asyncio
async def test_insert_parts_success(fake_context):
    # fake_context.db_connection.execute
    parts = [
        PartDetails(
            maker="MAKER1",
            category="CATEGORY1",
            model="MODEL1",
            part=CataloguePart(number="4242", category="FOO", url="https://example.com"),
        )
    ]

    await insert_parts(parts=parts, ctx=fake_context)

    assert fake_context.db_connection.execute.assert_called


@pytest.mark.asyncio
async def test_process_page(fake_context):
    # Mock fetch_html and extract_links
    links = [
        CatalogueLink(url=urlparse("https://example.com/link1")),
        CatalogueLink(url=urlparse("https://example.com/link2")),
    ]
    with patch("app.scraper.fetch_html", return_value="<html></html>"):
        with patch("app.scraper.extract_links", return_value=links):

            payload = ScraperPayload(
                link=CatalogueLink(url=urlparse("https://example.com"), directory={}),
                level=CatalogueLevels.MAKERS,
            )

            await process_page(payload, fake_context)

            assert "https://example.com" in fake_context.visited_urls
