from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PartSchema(BaseModel):
    maker: str
    category: str
    model: str
    part_number: str
    part_category: str
    url: str

    class Config:
        orm_mode = True


class MakerSchema(BaseModel):
    id: int
    maker: str

    class Config:
        orm_mode = True


class CategorySchema(BaseModel):
    id: int
    category: str

    class Config:
        orm_mode = True


class ModelSchema(BaseModel):
    id: int
    model: str

    class Config:
        orm_mode = True


class ScanSchema(BaseModel):
    id: int
    time_start: datetime
    time_end: Optional[datetime]

    class Config:
        orm_mode = True
