from app.scraper import run_scraper
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/run")
async def scrape(request: Request) -> bool:
    await run_scraper(request.app.state.db)
    return True
