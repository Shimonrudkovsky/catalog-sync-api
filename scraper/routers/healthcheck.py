from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

router = APIRouter()


class Checks(BaseModel):
    db: bool = Field(False, example=True)


class HealthCheck(BaseModel):
    is_sick: bool = Field(..., example=False)
    checks: Checks
    version: str = Field(default="0.1.0")
    start_time: datetime = Field(..., example=datetime.now())
    up_time: timedelta = Field(..., example=timedelta(seconds=1))


async def check_health(request: Request) -> HealthCheck:
    db_check = request.app.state.db.pool.get_size() > 0

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
