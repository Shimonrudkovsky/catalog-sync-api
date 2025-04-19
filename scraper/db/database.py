from typing import Optional

import asyncpg
from loguru import logger

from config.settings import DbConfig


class Postgres:
    def __init__(self, db_config: DbConfig):
        self.host = db_config.host
        self.port = db_config.port
        self.database = db_config.database
        self.user = db_config.user
        self.password = db_config.password
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize the connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=f"postgres://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}",
                min_size=1,
                max_size=10,
            )
        except asyncpg.PostgresError as err:
            logger.error("connection to db failed")
            raise err

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except asyncpg.PostgresError as err:
            logger.error(f"request to db failed. query: {query}, args: {args}")
            raise err

    async def executemany(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                return await connection.executemany(query, *args)
        except asyncpg.PostgresError as err:
            logger.error(f"request to db failed {err}")
            raise err

    async def fetchval(self, query: str, *args):
        """Fetch a single value."""
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)
