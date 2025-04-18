from typing import Optional

from db import requests as db_requests
from fastapi import APIRouter, Query
from schemas import MakerSchema, PartSchema

router = APIRouter()


@router.get("/parts", response_model=list[PartSchema])
async def read_parts(
    maker: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
):
    parts = await db_requests.get_parts(maker=maker, category=category, model=model)
    return [
        PartSchema(
            maker=p.maker.maker,
            category=p.category.category,
            model=p.model.model,
            part_number=p.part_number,
            part_category=p.part_category,
            url=p.url,
            scan_id=p.scan.id,
        )
        for p in parts
    ]


@router.get("/makers", response_model=list[MakerSchema])
async def read_makers():
    makers = await db_requests.get_makers()
    return makers
