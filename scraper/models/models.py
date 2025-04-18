from asyncio import Queue as AsyncQueue
from asyncio import Semaphore
from enum import Enum
from typing import Optional
from urllib.parse import ParseResult as ParsedUrl

from db.database import Postgres
from httpx import AsyncClient as HttpAsyncClient
from pydantic import BaseModel, ConfigDict, Field

REQUEST_DELAY = 0.5  # seconds


class CatalogueLevels(str, Enum):
    MAKERS = "allmakes"
    CATEGORIES = "allcategories"
    MODELS = "allmodels"
    PARTS = "allparts"


class CataloguePart(BaseModel):
    number: str
    category: str
    url: str


class PartDetails(BaseModel):
    maker: Optional[str]
    category: Optional[str]
    model: Optional[str]
    part: Optional[CataloguePart]


class ScraperContext(BaseModel):
    semaphore: Semaphore
    visited_urls: set
    queue: AsyncQueue
    http_client: HttpAsyncClient
    db_connection: Postgres
    scan_id: int

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class CatalogueLink(BaseModel):
    url: ParsedUrl
    directory: dict[CatalogueLevels, str] = Field(default=dict())


class ScraperPayload(BaseModel):
    link: CatalogueLink
    level: CatalogueLevels
    attempt: int = Field(default=1)
    delay: float = Field(default=REQUEST_DELAY)
