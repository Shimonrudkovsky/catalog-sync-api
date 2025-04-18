from app.scraper import run_scraper
from fastapi import APIRouter, BackgroundTasks, Request

router = APIRouter()


@router.get("/run")
async def scrape(request: Request, background_tasks: BackgroundTasks) -> str:
    background_tasks.add_task(run_scraper, request.app.state.db)
    return "Scraper started successfully"
