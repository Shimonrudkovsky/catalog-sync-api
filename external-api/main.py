import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from config import AppConfig, DbConfig
from db.postgres import close_db, init_db, register_db
from fastapi import FastAPI
from loguru import logger
from routers.api import router as api_router
from routers.healthcheck import router as healthcheck_router

logger.remove()
logger.add(sys.stderr, level="DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(db_config=app.state.app_config.db)
    logger.info("Database initialized.")

    yield

    await close_db()


db_config = DbConfig(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "parts_catalogue"),
    user=os.getenv("DB_USER", "user"),
    password=os.getenv("DB_PASS", "pass"),
)
app_config = AppConfig(
    port=int(os.getenv("APP_PORT", 8081)),
    db=db_config,
)
app = FastAPI(lifespan=lifespan)

register_db(app, db_config)


def init_app(app: FastAPI, app_config: AppConfig):
    app.include_router(healthcheck_router)
    app.include_router(api_router)

    app.state.start_time = datetime.now()
    app.state.app_config = app_config

    logger.info("Application initialized.")


init_app(app=app, app_config=app_config)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
