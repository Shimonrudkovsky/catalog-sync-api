import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from loguru import logger

from config.settings import AppConfig, DbConfig
from db.database import Postgres
from db.utils import initialize_database
from models import ScrapingStatus
from routers.healthcheck import router as healthcheck_router
from routers.scraper import router as scraper_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init db
    database = Postgres(db_config=app.state.app_config.db)
    await database.connect()
    await initialize_database(db=database)
    app.state.db = database
    logger.info("Database initialized.")

    yield

    await database.disconnect()


db_config = DbConfig(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "parts_catalogue"),
    user=os.getenv("DB_USER", "user"),
    password=os.getenv("DB_PASS", "pass"),
)
app_config = AppConfig(
    port=int(os.getenv("APP_PORT", 8080)),
    db=db_config,
)
app = FastAPI(lifespan=lifespan)


def init_app(app: FastAPI, app_config: AppConfig):
    app.include_router(healthcheck_router)
    app.include_router(scraper_router)

    app.state.start_time = datetime.now()
    app.state.app_config = app_config
    app.state.scraping_status = ScrapingStatus()

    logger.info("Application initialized.")


init_app(app, app_config)

if __name__ == "__main__":

    async def main():
        uvicorn.run("main:app", host="0.0.0.0", port=app_config.port, reload=True)

    asyncio.run(main())
