from pydantic import BaseModel


class PartSchema(BaseModel):
    maker: str
    category: str
    model: str
    part_number: str
    part_category: str
    url: str
    scan_id: int

    class Config:
        orm_mode = True


class MakerSchema(BaseModel):
    id: int
    maker: str

    class Config:
        orm_mode = True
