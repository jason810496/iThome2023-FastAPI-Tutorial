import redis
from setting.config import get_settings

settings = get_settings()


redis_pool = redis.ConnectionPool.from_url(settings.redis_url,decode_responses=True)

from sqlalchemy.engine.row import Row


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



def generic_pagenation_cache_get(prefix:str,key:str,cls:object):
    '''
    pageation cache using redis sorted set
    '''
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
                redis_result:list = rc.zrange(name=cache_key,start=left,end=right,withscores=False)
                # print("get redis cache" , prefix , left , right)
                # print("redis_result" , redis_result)
                if redis_result:
                    data = []
                    for row_str in redis_result:
                        # hash_dict = rc.hgetall(row_str)
                        # if check_has_all_keys(hash_dict,cls):
                        #     data.append(cls(**hash_dict))

                        # print("row_str" , row_str)
                        row_dict = ast.literal_eval(row_str)
                        # print("row_dict" , row_dict)
                        data.append(cls(**row_dict))

                    return data
                
            except Exception as e:
                print("redis error")
                print(e)
                pass

            sql_result = await func(*args, **kwargs)
            if not sql_result:
                return None
            
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

            return await func(*args, **kwargs)
        
        return wrapper
    return inner

def update_pagenation_cache(prefix:str,score:int,upd:dict):
    rc = redis.Redis(connection_pool=redis_pool)
    rc.zadd(name=prefix,mapping={ str(upd) :score} , xx=True )

def delete_pagenation_cache(prefix:str,score:int):
    rc = redis.Redis(connection_pool=redis_pool)
    rc.zremrangebyscore(name=prefix,min=score,max=score)


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
            sql_dict = sql_query_row_to_dict(sql_result)
            rc.hset(cache_key, mapping=sql_dict) # 1 hour

            page_key = f"{prefix}_page"
            rc.zadd(name=page_key,mapping={ str( merge_dict(sql_dict, {key:value_key}) ) : value_key}  )
            
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
