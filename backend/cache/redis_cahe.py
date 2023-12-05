from setting.config import get_settings
import redis


settings = get_settings()


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

def merge_dict(dict1:dict,dict2:dict):
    '''
    merge dict2 into dict1
    '''
    for k,v in dict2.items():
        dict1[k] = v
    return dict1

import ast

def generic_pagenation_cache_get(prefix:str,cls:object):
    if settings.redis_url == None:
        def inner(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return inner
    '''
    pageation cache using redis sorted set
    '''
    from .redis_pool import redis_pool
    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            #  dont cache when set keyword
            if kwargs.get('keyword'):
                return await func(*args, **kwargs)

            # must pass parameter with key in caller function
            left = kwargs.get('last')
            limit = kwargs.get('limit')
            right = left + limit

            cache_key = f"{prefix}_page"

            try:
                redis_result:list = rc.zrange(name=cache_key,start=left,end=right,withscores=False,byscore=False)
                str_result = ""
        
                if len(redis_result) > 0:
                    
                    for row_str in redis_result: # concat user string
                        str_result += row_str + ","

                    # convert string to list of dict
                    return ast.literal_eval(f"[{str_result[:-1]}]")
                
            except Exception as e:
                print("redis error")
                print(e)
                pass

            
            sql_result = await func(*args, **kwargs)
            if not sql_result:
                return sql_result
            
            # print("set redis cache" , prefix , left , right)
            for row in sql_result:
                # print("row" , row)
                # print("row type" , type(row) ) # <class 'sqlalchemy.engine.row.Row'>
                # print("row.__dict__" , row.__dict__)
                # row:Row = row
                # row._asdict()

                # row_dict = row._asdict()
                # row_key_value = row_dict.get(key)
                # rc.zadd(name=prefix,mapping={ f"{prefix}:{row_key_value }":row.id})
                # rc.hset(f"{prefix}:{row_key_value }", mapping=sql_query_row_to_dict(row_dict) )

                rc.zadd(name=cache_key,mapping={ str(row._asdict()) :row.id} )


            # print(last,limit,right)
            print("sql_result" , sql_result)
            return sql_result
        
        return wrapper
    return inner


def generic_cache_get(prefix:str,key:str,cls:object):
    if settings.redis_url == None:
        def inner(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return inner
    '''
    prefix: namspace for redis key ( such as `user` 、`item` 、`article` )
    key: **parameter name** in caller function ( such as `user_id` 、`email` 、`item_id` )
    cls: **response schema** in caller function ( such as `UserSchema.UserRead` 、`UserSchema.UserId` 、`ItemSchema.ItemRead` )
    '''
    from .redis_pool import redis_pool
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

def generic_cache_update(prefix:str,key:str,update_with_page:bool=False,pagenation_key:str=None):
    if settings.redis_url == None:
        def inner(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return inner
    # redis connection
    from .redis_pool import redis_pool
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
            sql_dict = sql_query_row_to_dict(sql_result)
            rc.hset(cache_key, mapping=sql_dict) # 1 hour

            # handel update pagenation cache
            if update_with_page:
                try:
                    page_key = f"{prefix}_page"
                    old_redis_result:str = rc.zrange(name=page_key,start=value_key,end=value_key,withscores=False,byscore=True)[0]
                    print("old_redis_result" , old_redis_result)
                    rc.zremrangebyscore(name=page_key,min=value_key,max=value_key)
                    print("updated:", str( merge_dict( merge_dict( ast.literal_eval(old_redis_result) , sql_dict) , {pagenation_key:value_key} ) ) )
                    rc.zadd(name=page_key,mapping={ str( merge_dict( merge_dict( ast.literal_eval(old_redis_result) , sql_dict ), {pagenation_key:value_key}) ) : value_key} ,nx=True   )
                except Exception as e:
                    print("redis error")
                    print(e)
                    pass
            
            return sql_result
        return wrapper
    return inner

def generic_cache_delete(prefix:str,key:str):
    if settings.redis_url == None:
        def inner(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return inner
    
    from .redis_pool import redis_pool
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

            try:
                page_key = f"{prefix}_page"
                rc.zremrangebyscore(name=page_key,min=value_key,max=value_key)
            except:
                pass

            return await func(*args, **kwargs)
        return wrapper
    return inner

def user_cache_delete(prefix:str,key:str):
    if settings.redis_url == None:
        def inner(func):
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return wrapper
        return inner

    from .redis_pool import redis_pool
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

                try:
                    page_key = f"{prefix}_page"
                    rc.zremrangebyscore(name=page_key,min=redis_dict['id'],max=redis_dict['id'])
                except:
                    pass

            return await func(*args, **kwargs)
        return wrapper
    return inner
