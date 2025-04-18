import os
import sys
from asyncio import Queue, Semaphore
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

# Add parent directory to the sys.path to resolve relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import Postgres
from models.models import ScraperContext


@pytest.fixture(scope='module')
def fake_context():
    # Mock the HTTP client
    mock_http_client = AsyncMock(spec=AsyncClient)

    # Mock the database client
    mock_db_client = AsyncMock(spec=Postgres)

    # Create a mock context
    ctx = ScraperContext(
        semaphore=Semaphore(1),
        visited_urls=set(),
        queue=Queue(),
        http_client=mock_http_client,
        db_connection=mock_db_client,
        scan_id=1,
    )

    return ctx
