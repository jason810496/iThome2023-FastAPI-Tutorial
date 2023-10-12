import redis

REDIS_URL = "redis://localhost:6379"

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)

    value = 'bar'
    redis_connection.set('foo', value )
    result = redis_connection.get('foo')
    redis_connection.close()

    assert result.decode() == value

def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    
    value = 'bar2'
    redis_connection.set('foo2', value)
    value = redis_connection.get('foo2')
    redis_connection.close()

    assert value.decode() == 'bar2'

def test_redis_delete():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    redis_connection.set('foo3', 'bar3')
    redis_connection.delete('foo3')
    assert redis_connection.exists('foo3') == 0
    redis_connection.close()

# def test_redis_pipeline():
#     redis_connection = redis.Redis.from_url(REDIS_URL)
#     with redis_connection.pipeline(transaction=True) as pipe:
#         ok = pipe.set('foo', 'bar').execute() # return [True]
#         print("pip exe ok",ok)
#         value = pipe.get('foo').execute() #return ['bar']
#         print("pipe value",value)
#     redis_connection.close()

# def test_redis_transaction():
#     redis_connection = redis.Redis.from_url(REDIS_URL)
#     with redis_connection.pipeline(transaction=True) as pipe:
#         try:
#             pipe.watch('foo')
#             pipe.multi()
#             pipe.set('foo', 'bar')
#             pipe.execute()
#         except redis.WatchError:
#             print("WatchError")
#             pass
#     redis_connection.close()

# if __name__ == "__main__":
#     test_redis_connection()