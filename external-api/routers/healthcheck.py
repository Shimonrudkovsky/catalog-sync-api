from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from tortoise.connection import connections

router = APIRouter()


class Checks(BaseModel):
    db: bool = Field(default=False)


class HealthCheck(BaseModel):
    is_sick: bool = Field(default=True)
    checks: Checks
    version: str = Field(default="0.1.0")
    start_time: datetime = Field(...)
    up_time: timedelta = Field(...)


async def check_health(request: Request) -> HealthCheck:
    db_check = len(connections.all()) > 0

    checks = Checks(
        db=db_check,
    )

    is_sick = not all(checks.model_dump().values())

    return HealthCheck(
        is_sick=is_sick,
        checks=checks,
        version=request.app.version,
        start_time=request.app.state.start_time,
        up_time=datetime.now() - request.app.state.start_time,
    )


@router.get("/")
@router.get(
    "/health",
    tags=["Health check"],
    summary="Returns server status.",
    response_class=JSONResponse,
    include_in_schema=False,
)
async def health(request: Request) -> HealthCheck:
    """Handler to get server status"""
    return await check_health(request=request)
