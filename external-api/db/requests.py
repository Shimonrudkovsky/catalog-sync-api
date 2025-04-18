from typing import List, Optional, Type

from db.models import Categories, Makers, Models, Parts, Scans
from fastapi import HTTPException
from loguru import logger
from tortoise.exceptions import OperationalError
from tortoise.models import Model as TortoiseModel


async def query_model(
    model: Type[TortoiseModel],
    filters: Optional[dict] = None,
    prefetch_related: Optional[List[str]] = None,
    distinct: bool = False,
) -> List[TortoiseModel]:
    try:
        query = model.all()
        if filters:
            query = query.filter(**filters)
        if prefetch_related:
            query = query.prefetch_related(*prefetch_related)
        if distinct:
            query = query.distinct()
        results = await query

        if not results:
            logger.warning("No results found for model: {}", model.__name__)
            raise HTTPException(status_code=404, detail=f"No {model.__name__.lower()} found or table is empty.")

        logger.info("{} {}s found.", len(results), model.__name__.lower())
        return results
    except OperationalError as err:
        logger.error("OperationalError querying {}: {}", model.__name__, str(err))
        raise HTTPException(
            status_code=500, detail=f"{model.__name__} table does not exist. Please check the database schema."
        )


async def get_latest_scan_id() -> int:
    latest_scan = await Scans.all().order_by("-time_end").first()
    if not latest_scan:
        raise HTTPException(status_code=404, detail="No scans found in the database.")
    return latest_scan.id


async def search_parts(
    maker: Optional[str] = None,
    category: Optional[str] = None,
    model: Optional[str] = None,
    part_number: Optional[str] = None,
    part_category: Optional[str] = None,
    scan_id: Optional[int] = None,
):
    if not scan_id:
        scan_id = await get_latest_scan_id()

    filters = {"scan_id": scan_id}
    if maker:
        filters["maker__maker__icontains"] = maker
    if category:
        filters["category__category__icontains"] = category
    if model:
        filters["model__model__icontains"] = model
    if part_number:
        filters["part_number__icontains"] = part_number
    if part_category:
        filters["part_category__icontains"] = part_category

    return await query_model(Parts, filters=filters, prefetch_related=["maker", "category", "model", "scan"])


async def get_makers() -> List[Makers]:
    return await query_model(Makers)


async def get_categories(maker_name: Optional[str] = None):
    filters = {}
    if maker_name:
        filters["parts__maker__maker__icontains"] = maker_name
    return await query_model(Categories, filters=filters, distinct=True)


async def get_models(maker_name: Optional[str] = None, category_name: Optional[str] = None):
    filters = {}
    if maker_name:
        filters["parts__maker__maker__icontains"] = maker_name
    if category_name:
        filters["parts__category__category__icontains"] = category_name
    return await query_model(Models, filters=filters)


async def get_scans():
    return await query_model(Scans)
