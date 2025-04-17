from .database import Postgres
from .queries import CREATE_TABLES_QUERY


async def initialize_database(db: Postgres):
    """Initialize the database: create table if not exist"""
    await db.execute(CREATE_TABLES_QUERY)
