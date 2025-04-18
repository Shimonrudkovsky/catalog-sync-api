from typing import List, Optional

from db.models import Categories, Makers, Models, Parts, Scans
from fastapi import HTTPException
from loguru import logger
from tortoise.exceptions import OperationalError


async def get_parts(maker: Optional[str] = None, category: Optional[str] = None, model: Optional[str] = None):
    try:
        logger.info("Querying parts with filters - maker: {}, category: {}, model: {}", maker, category, model)
        query = Parts.all().prefetch_related("maker", "category", "model", "scan")

        if maker:
            query = query.filter(maker__maker__icontains=maker)
        if category:
            query = query.filter(category__category__icontains=category)
        if model:
            query = query.filter(model__model__icontains=model)

        parts = await query

        if not parts:
            logger.warning("No parts found for the given filters.")
            raise HTTPException(status_code=404, detail="No parts found or table is empty.")

        logger.info("{} parts found.", len(parts))
        return parts

    except OperationalError as err:
        logger.error("OperationalError querying parts: {}", str(err))
        raise HTTPException(status_code=500, detail="Parts table does not exist. Please check the database schema.")


async def get_makers() -> List[Makers]:
    try:
        logger.info("Querying all makers")
        makers = await Makers.all()

        if not makers:
            logger.warning("No makers found.")
            raise HTTPException(status_code=404, detail="No makers found or table is empty.")

        logger.info("{} makers found.", len(makers))
        return makers

    except OperationalError as err:
        logger.error("OperationalError querying makers: {}", str(err))
        raise HTTPException(status_code=500, detail="Makers table does not exist. Please check the database schema.")
