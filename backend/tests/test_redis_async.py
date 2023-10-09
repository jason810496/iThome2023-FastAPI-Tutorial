import pytest
import redis.asyncio as redis

REDIS_URL = "redis://:fastapi_redis_password@localhost:6379"

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

@pytest.mark.asyncio
async def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)
    value = 'bar_async'
    await redis_connection.set('foo_async', value )
    result = await redis_connection.get('foo_async')
    redis_connection.close()

    assert result.decode() == value

@pytest.mark.asyncio
async def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    
    value = 'bar_async2'
    await redis_connection.set('foo_async2', value)
    result = await redis_connection.get('foo_async2')
    redis_connection.close()

    assert result.decode() == value