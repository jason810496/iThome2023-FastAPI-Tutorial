import pytest
import redis.asyncio as redis

REDIS_URL = "redis://localhost:6379"

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
    existed = await redis_connection.exists('foo_async2')
    assert existed == 1

    result = await redis_connection.get('foo_async2')
    redis_connection.close()

    assert result.decode() == value

@pytest.mark.asyncio
async def test_redis_delete():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    await redis_connection.set('foo_async3', 'bar_async3')
    await redis_connection.delete('foo_async3')
    existed = await redis_connection.exists('foo_async3')
    assert existed == 0
    redis_connection.close()

@pytest.mark.asyncio
async def test_redis_update():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    await redis_connection.set('foo_async4', 'bar_async4')
    await redis_connection.set('foo_async4', 'bar_async4_updated')
    result = await redis_connection.get('foo_async4')
    redis_connection.close()

    assert result.decode() == 'bar_async4_updated'