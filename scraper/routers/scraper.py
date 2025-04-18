from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.scraper import run_scraper
from models import ScrapingStatus

router = APIRouter()


@router.get("/run")
async def scrape(request: Request, background_tasks: BackgroundTasks) -> str:
    if request.app.state.scraping_status.scraping:
        raise HTTPException(
            status_code=400,
            detail="scraping is running",
        )
    background_tasks.add_task(run_scraper, request.app.state.db, request.app.state.scraping_status)
    return "Scraper started successfully"


@router.get("/status")
async def status(request: Request) -> ScrapingStatus:
    return request.app.state.scraping_status
