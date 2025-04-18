import os
from asyncio import Queue as AsyncQueue
from asyncio import Semaphore

from httpx import AsyncClient as HttpAsyncClient
from pydantic import BaseModel, ConfigDict, Field

from db.database import Postgres

from .catalogue import CatalogueLevels, CatalogueLink

REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))  # seconds


class ScrapingStatus(BaseModel):
    scraping: bool = Field(default=False)
    scraping_counter: int = Field(default=0)


class ScraperContext(BaseModel):
    semaphore: Semaphore
    visited_urls: set
    queue: AsyncQueue
    http_client: HttpAsyncClient
    db_connection: Postgres
    scan_id: int
    scraping: bool = Field(default=False)
    scraping_status: ScrapingStatus

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class ScraperPayload(BaseModel):
    link: CatalogueLink
    level: CatalogueLevels
    attempt: int = Field(default=1)
    delay: float = Field(default=REQUEST_DELAY)
