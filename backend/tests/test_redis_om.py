import pytest
from redis_om import get_redis_connection
from redis_om import JsonModel , HashModel , Migrator , Field
from typing import Optional

REDIS_URL = "redis://:fastapi_redis_password@localhost:6379"

redis = get_redis_connection(url=REDIS_URL)


class UserReadCache( HashModel ):
    id: int = Field(index=True)
    name : str = Field(index=True)
    email: str = Field(index=True)
    avatar:Optional[str] =  None

    class Meta:
        database = redis


print(UserReadCache.__dict__)


Migrator().run()

def test_create_user():
    new_user = UserReadCache(id=1,name="user1",email="user1@email.com")
    new_user.save()
    pk = new_user.pk
    assert redis.get(pk) == new_user

# try:
#     print("Add new User")
#     new_user = UserReadCache(id=1,name="user1",email="user1@email.com")
#     new_user.save()

#     print("PK" , new_user.pk )
#     print("Use pk to find user")
#     print( UserReadCache.get( new_user.pk ).dict() )
#     # print( new_user.pk )
# except Exception as e:
#     print(e)
#     pass

# try:
#     print( redis.get("user:1") )
#     print( redis.get("01HCA25H214RBP3SV522N4QBPH"))
#     res = UserReadCache.find( UserReadCache.name == "user1" ).all()
#     print(res)

# except Exception as e:
#     print(e)
#     print("not found")
#     pass

