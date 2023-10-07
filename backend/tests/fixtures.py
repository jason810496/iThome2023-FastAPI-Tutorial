from httpx import AsyncClient
import pytest_asyncio
import json
from functools import lru_cache


@pytest_asyncio.fixture(scope="module")
async def async_client(dependencies) -> AsyncClient:
    from .app import app
    async with AsyncClient(app=app,base_url="http://test") as client:
        yield client


@lru_cache()
@pytest_asyncio.fixture(scope="module")
async def user_data():
    async def read_data():
        with open("data/user_data.json") as f:
            data = json.load(f)
        return data
    
    return await read_data()