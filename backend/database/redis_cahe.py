# import redis

import redis.asyncio as redis_async



# redis_connection = redis.Redis(host='localhost', port=6379, db=0)


redis_connection_pool = redis_async.ConnectionPool("redis://default@localhost:6379",decode_responses=True)
r = redis_async.from_url("redis://default@localhost:6379",decode_responses=True)

async def test_redis():
    # client = redis_async.Redis(connection_pool=redis_connection_pool)
    # client.set('foo', 'bar')
    # value = client.get('foo')
    # print(value)
    # await client.close()
    async with r.pipeline(transaction=True) as pipe:
        ok = await pipe.set('foo', 'bar').execute() # return [True]
        print("pip exe ok",ok)
        value = await pipe.get('foo').execute() #return ['bar']
        print("pipe value",value)

def redis_cache_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        await test_redis()
        func_name = func.__name__
        print("redis_cache_decorator:func_name",func_name)

        verb = func_name.split('_')[0]
        subject = func_name.split('_')[1]

        # print key valye pair of kwargs
        print("redis_cache_decorator:args",args)
        print("redis_cache_decorator:kwargs",kwargs)

        print("redis_cache_decorator:verb",verb)
        print("redis_cache_decorator:subject",subject)

        print("redis_cache_decorator:kwargs",kwargs)
        prefix_key = ''
        for k,v in kwargs.items():
            if k != 'db_session' and v is not None:
                prefix_key += f"{k}:{v}:"

        print("redis_cache_decorator:prefix_key",prefix_key)

        result = await func(*args, **kwargs)

        print("result",result)
        return result
        # if kwargs:
        #     key += str(kwargs)
        # if redis_connection.exists(key):
        #     print("get from cache")
        #     return redis.get(key)
        # else:
        #     result = func(*args, **kwargs)
        #     redis_connection.set(key, result)
        #     return result


    # print("out db_context_decorator")
    return wrapper

def crud_cache_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, redis_cache_decorator(method))
    # print("out db_class_decorator")
    return cls