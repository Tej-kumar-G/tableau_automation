# conftest.py
import os
import sys
from pathlib import Path

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

from base_setup.utils.common_utils import setup_logging

# Setup base path and logging once
base_setup_path = str(Path(__file__).parent.parent / 'base_setup')
sys.path.append(base_setup_path)
setup_logging(os.path.join(base_setup_path, 'config', 'logging_config.yaml'))


@pytest_asyncio.fixture(scope="session")
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
