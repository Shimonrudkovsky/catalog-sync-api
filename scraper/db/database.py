from typing import Optional

import asyncpg


class Postgres:
    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
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
            raise err  # TODO: logging

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        try:
            async with self.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except asyncpg.PostgresError as err:
            raise err  # TODO: logging
