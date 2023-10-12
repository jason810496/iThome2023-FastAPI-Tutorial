import redis
from setting.config import get_settings

settings = get_settings()


redis_pool = redis.ConnectionPool.from_url(settings.redis_url,decode_responses=True)


def check_has_all_keys(result:dict,cls:object):
    '''
    check whether redis_result has all required field of current response schema
    '''
    result_keys = result.keys()
    for key in cls.__annotations__.keys():
        if key not in result_keys:
            return False
    return True

def sql_query_row_to_dict(row):
    '''
    deal with datetime object
    '''

    row = dict(row)
    if row.get('birthday'):
        row['birthday'] = row['birthday'].strftime("%Y-%m-%d")
    return row

def generic_cache_get(prefix:str,key:str,cls:object):
    '''
    prefix: namspace for redis key ( such as `user` 、`item` 、`article` )
    key: **parameter name** in caller function ( such as `user_id` 、`email` 、`item_id` )
    cls: **response schema** in caller function ( such as `UserSchema.UserRead` 、`UserSchema.UserId` 、`ItemSchema.ItemRead` )
    '''

    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):

            # must pass parameter with key in caller function
            value_key = kwargs.get(key) 
            if not value_key:
                return await func(*args, **kwargs)
            
            # key for redis cache 
            cache_key = f"{prefix}:{value_key}"

            # use try-except to improve performance instead of using `rc.exists(cache_key)`
            try:
                redis_result:dict = rc.hgetall(cache_key)

                # we still have to check whether redis_result has all required field of current response schema
                if check_has_all_keys(redis_result,cls): # cache hit !
                    return cls(**redis_result) 
            except:
                pass
            
            sql_result = await func(*args, **kwargs) 
            if not sql_result:
                return None
            
            rc.hset(cache_key, mapping=sql_query_row_to_dict(sql_result))
            return sql_result
            
        return wrapper
    return inner

def generic_cache_update(prefix:str,key:str):

    # redis connection
    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            
            sql_result = await func(*args, **kwargs)

            if not sql_result:
                return None
            
            cache_key = f"{prefix}:{value_key}"
            rc.hset(cache_key, mapping=sql_query_row_to_dict(sql_result)) # 1 hour
            
            return sql_result
        return wrapper
    return inner

def generic_cache_delete(prefix:str,key:str):
    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if not value_key:
                return await func(*args, **kwargs)
            
            cache_key = f"{prefix}:{value_key}"

            try:
                rc.delete(cache_key)
            except:
                pass

            return await func(*args, **kwargs)
        return wrapper
    return inner

def user_cache_delete(prefix:str,key:str):

    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if value_key:
                cache_key = f"{prefix}:{value_key}"
                if rc.exists(cache_key):
                    redis_dict:dict = rc.hgetall(cache_key)

                    rc.delete( f"{prefix}:{redis_dict['email']}"  )
                    rc.delete( cache_key )

            return await func(*args, **kwargs)
        return wrapper
    return inner
