from config import DbConfig
from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise


async def init_db(db_config: DbConfig):
    dsn = f"postgres://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
    await Tortoise.init(
        db_url=dsn,
        modules={"models": ["db.models"]},
    )


async def close_db():
    await Tortoise.close_connections()


def register_db(app: FastAPI, db_config: DbConfig):
    dsn = f"postgres://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"
    register_tortoise(
        app,
        db_url=dsn,
        modules={"models": ["db.models"]},
        generate_schemas=False,
        add_exception_handlers=True,
    )
