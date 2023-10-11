# import redis

# import redis.asyncio as redis_async

from redis_om import get_redis_connection
from redis_om import Field , HashModel , Migrator
from redis_om import NotFoundError
from typing import Optional , List


from setting.config import get_settings

# redis_connection = redis.Redis(host='localhost', port=6379, db=0)

settings = get_settings()


redis = get_redis_connection(url=settings.redis_url)

from redis import Redis , ConnectionPool

redis_pool = ConnectionPool.from_url(settings.redis_url)


class UserCache( HashModel ):
    id: Optional[int] = Field(index=True)
    name:Optional[str] = Field(index=True)
    password:Optional[str] = Field(index=False)
    name: Optional[str] = Field(index=True)
    avatar: Optional[str] = Field(index=False)
    age: Optional[int] = Field(index=False,default=0)
    email: Optional[str] = Field(index=True)
    birthday: Optional[str] = Field(index=False)

    class Meta:
        database = redis

def get_user_cache_by_id(user_id:int):
    try:
        user = UserCache.find( UserCache.id==user_id ).first()
        return user
    except NotFoundError:
        return None
    
def get_user_cache_by_email(email:str):
    try:
        user = UserCache.find( UserCache.email==email ).first()
        return user
    except NotFoundError:
        return None
    
async def delete_user_cache_by_id(user_id:int):
    try:
        user = UserCache.find( UserCache.id==user_id ).first()
        user.delete()
        return True
    except NotFoundError:
        return None
    
Migrator().run()

def user_redis_cache_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        print("redis_cache_decorator:func_name",func_name)

        verb = func_name.split('_')[0]
        subject = func_name.split('_')[1]

        if verb == 'get':
            if subject == 'users':
                pass
            else: # user
                # by user_id
                user_id = kwargs.get('user_id')
                if user_id:
                    print("kwargs['user_id']",kwargs['user_id'])
                    user = get_user_cache_by_id(kwargs['user_id'])
                    print("user in cache:" , user)
                    if user:
                        print("hit cache:" , user)
                        return user
                    else: # not found in cache
                        result = await func(*args, **kwargs)
                        user_dict = vars(result)
                        user = UserCache(id=user_dict.get('id'),name=user_dict.get('name'),password=user_dict.get('password'),avatar=user_dict.get('avatar'),age=user_dict.get('age',0),email=user_dict.get('email'),birthday=user_dict.get('birthday'))
                        user.save()
                        print("set cache:",user)
                        return result
                # by email
                email = kwargs.get('email')
                if email:
                    user = get_user_cache_by_email(email)
                    if user:
                        print("hit cache:" , user)
                        return user
                    else:
                        result = await func(*args, **kwargs)
                        user_dict = vars(result)
                        user_cache = UserCache(**user_dict)
                        user_cache.save()
                        print("set cache:",user_cache)
                        return result
        elif verb == 'update':
            user_id = kwargs.get('user_id')
            if user_id:
                user = get_user_cache_by_id(kwargs['user_id'])
                # print("user in cache update:" , user)
                # if user:
                #     print("hit cache:" , user)
                #     result 
                #     return user
                # else: # not found in cache
                #     result = await func(*args, **kwargs)
                #     user_dict = vars(result)
                #     user = UserCache(**user_dict)
                #     user.save()
                #     print("set cache in update:",user)
                #     return result
                result = await func(*args, **kwargs)
                user_dict = vars(result)
                user = UserCache(**user_dict)
                user.save()
                print("set cache in update:",user)
                return result
        elif verb == 'delete':
            await delete_user_cache_by_id(kwargs['user_id'])

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

def user_cache_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            # setattr(cls, name, user_redis_cache_decorator(method))
            pass
    # print("out db_class_decorator")
    return cls


import ast

# def generic_cache_get(prefix:str,key:str,cls):
#     print("in generic_cache")
#     print("generic_cache:prefix",prefix)
#     print("generic_cache:key",key)

#     redis_connection = Redis(connection_pool=redis_pool)

#     def inner(func):
#         async def wrapper(*args, **kwargs):
#             value_key = kwargs.get(key)
#             if value_key:
#                 cache_key = f"{prefix}:{value_key}"
#                 if redis_connection.exists(cache_key):
#                     print("get from cache")
#                     redis_result:str = redis.get(cache_key)
#                     redis_result:dict = ast.literal_eval(redis_result)
#                     # print("redis_result , type",redis_result,type(redis_result))
#                     return cls(**redis_result)
#                 else:
#                     print("set cache")
#                     result = await func(*args, **kwargs)
#                     if not result:
#                         return result
                    
#                     result_str = str(result.model_dump())
#                     redis_connection.set(cache_key, result_str)
#                     return result
#         return wrapper
#     return inner

# def generic_cache_update(prefix:str,key:str,cls):
#     print("in generic_cache_update")
#     print("generic_cache_update:prefix",prefix)
#     print("generic_cache_update:key",key)

#     redis_connection = Redis(connection_pool=redis_pool)

#     def inner(func):
#         async def wrapper(*args, **kwargs):
#             value_key = kwargs.get(key)
#             result = await func(*args, **kwargs)
#             redis_dict = None
            
#             cache_key = f"{prefix}:{value_key}"
#             if redis_connection.exists(cache_key):
#                 print("get from cache")
#                 redis_str:str = redis.get(cache_key)
#                 redis_dict:dict = ast.literal_eval(redis_str)
#                 # update redis cache with new value
#                 # print("result.model_dump()" , result.model_dump())
#                 # print("type",type(result.model_dump()))
#                 # for k,v in result.model_dump():
#                 #     redis_dict.update({k:v})
#                 redis_dict.update(result.model_dump())
#                 # var_dict = vars(result.copy())
#                 # for k,v in var_dict.items():
#                 #     redis_dict.update({k:v})

#             print("set cache")
#             redis_str = str(redis_dict)
#             print("redis_str",redis_str)
#             redis_connection.set(cache_key, redis_str)
#             return result
#         return wrapper
#     return inner

# def generic_cache_delete(prefix:str,key:str):
#     print("in generic_cache_delete")
#     print("generic_cache_delete:prefix",prefix)
#     print("generic_cache_delete:key",key)

#     redis_connection = Redis(connection_pool=redis_pool)

#     def inner(func):
#         async def wrapper(*args, **kwargs):
#             value_key = kwargs.get(key)
#             if value_key:
#                 cache_key = f"{prefix}:{value_key}"
#                 if redis_connection.exists(cache_key):
#                     print("delete cache")
#                     redis_connection.delete(cache_key)

#             return await func(*args, **kwargs)
#         return wrapper
#     return inner