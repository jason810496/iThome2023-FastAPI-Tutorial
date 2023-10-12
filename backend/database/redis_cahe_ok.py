import redis
from setting.config import get_settings

settings = get_settings()


redis_pool = redis.ConnectionPool.from_url(settings.redis_url,decode_responses=True)


def check_has_all_keys(result:dict,cls:object):
    result_keys = result.keys()
    for key in cls.__annotations__.keys():
        if key not in result_keys:
            return False
    return True

import ast

def update_redis_cache_with_dict(redis_dict:dict,new_dict:dict):
    for k,v in new_dict.items():
        redis_dict.update({k:v})
    return redis_dict

def sql_query_row_to_dict(row):
    row = dict(row)
    if row.get('birthday'):
        row['birthday'] = row['birthday'].strftime("%Y-%m-%d")
    return row

def generic_cache_get(prefix:str,key:str,cls):
    print("in generic_cache")
    print("generic_cache:prefix",prefix)
    print("generic_cache:key",key)

    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            if value_key:
                cache_key = f"{prefix}:{value_key}"
                if rc.exists(cache_key):
                    redis_result:str = rc.get(cache_key)
                    redis_result:dict = ast.literal_eval(redis_result)

                    if check_has_all_keys(redis_result,cls):
                        print("hit cache")
                        return cls(**redis_result)
                    else:
                        print("hit cache but not all keys")
                        sql_result = await func(*args, **kwargs) # sql query row
                        if not sql_result:
                            return None
                        
                        print("update cache")
                        redis_result = update_redis_cache_with_dict(redis_result,sql_query_row_to_dict(sql_result))
                        redis_str = str(redis_result)
                        rc.set(cache_key, redis_str)
                        return sql_result
                else:
                    print("set cache in get")
                    sql_result = await func(*args, **kwargs)
                    if not sql_result:
                        return sql_result
                    
                    result_str = str(sql_query_row_to_dict(sql_result))
                    rc.set(cache_key, result_str)
                    return sql_result
        return wrapper
    return inner

def generic_cache_update(prefix:str,key:str,cls):
    print("in generic_cache_update")
    print("generic_cache_update:prefix",prefix)
    print("generic_cache_update:key",key)

    # redis connection
    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            value_key = kwargs.get(key)
            sql_result = await func(*args, **kwargs)

            if not sql_result:
                return None

            redis_dict = None
            
            cache_key = f"{prefix}:{value_key}"
            if rc.exists(cache_key):
                print("get from cache")
                redis_str:str = rc.get(cache_key)
                redis_dict:dict = ast.literal_eval(redis_str)

                sql_dict = sql_query_row_to_dict(sql_result)
                redis_dict.update(sql_dict)

            print("set cache in update")
            redis_str = str(redis_dict)
            print("redis_str",redis_str)
            rc.set(cache_key, redis_str, ex=60*60) # 1 hour
            return sql_result
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
                    print("delete cache" , cache_key)
                    redis_str:str = rc.get(cache_key)
                    redis_dict:dict = ast.literal_eval(redis_str)

                    rc.delete( f"{prefix}:{redis_dict['email']}" , cache_key )

            return await func(*args, **kwargs)
        return wrapper
    return inner
