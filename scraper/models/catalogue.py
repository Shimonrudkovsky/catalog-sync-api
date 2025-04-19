import os
from enum import Enum
from typing import Optional
from urllib.parse import ParseResult as ParsedUrl

from pydantic import BaseModel, Field

REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.5"))  # seconds


class CatalogueLevels(str, Enum):
    MAKERS = "allmakes"
    CATEGORIES = "allcategories"
    MODELS = "allmodels"
    PARTS = "allparts"


class CataloguePart(BaseModel):
    number: str
    category: str
    url: str

    class Config:
        frozen = True


class PartDetails(BaseModel):
    maker: Optional[str]
    category: Optional[str]
    model: Optional[str]
    part: Optional[CataloguePart]

    class Config:
        frozen = True


class CatalogueLink(BaseModel):
    url: ParsedUrl
    directory: dict[CatalogueLevels, str] = Field(default=dict())
