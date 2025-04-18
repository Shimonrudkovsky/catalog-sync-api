from typing import Optional

import httpx
from db import requests as db_requests
from fastapi import APIRouter, HTTPException, Query, Request
from schemas import CategorySchema, MakerSchema, ModelSchema, PartSchema, ScanSchema

router = APIRouter()


@router.get("/parts", response_model=list[PartSchema])
async def search_parts(
    manufacturer: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    part_number: Optional[str] = Query(None),
    part_category: Optional[str] = Query(None),
    scan_id: Optional[int] = Query(None),
):
    parts = await db_requests.search_parts(
        maker=manufacturer,
        category=category,
        model=model,
        part_number=part_number,
        part_category=part_category,
        scan_id=scan_id,
    )
    return [
        PartSchema(
            maker=p.maker.maker,
            category=p.category.category,
            model=p.model.model,
            part_number=p.part_number,
            part_category=p.part_category,
            url=p.url,
        )
        for p in parts
    ]


@router.get("/manufacturers", response_model=list[MakerSchema])
async def get_makers():
    makers = await db_requests.get_makers()
    return makers


@router.get("/categories", response_model=list[CategorySchema])
async def get_categories(manufacturer: Optional[str] = Query(None)):
    categories = await db_requests.get_categories(maker_name=manufacturer)
    return categories


@router.get("/models", response_model=list[ModelSchema])
async def get_models(
    manufacturer: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    models = await db_requests.get_models(maker_name=manufacturer, category_name=category)
    return models


@router.get("/scans", response_model=list[ScanSchema])
async def get_scans():
    scans = await db_requests.get_scans()
    return scans


@router.get("/scraper/run")
async def run_scraper(request: Request):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(request.app.state.app_config.scraper_addr)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to run scraper: {response.text}",
                )
            return {"message": "Scraper started successfully", "details": response.json()}
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to scraper service: {str(exc)}",
        )
