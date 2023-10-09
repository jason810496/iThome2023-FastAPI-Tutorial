from redis_om import get_redis_connection
from redis_om import JsonModel , HashModel , Migrator , Field
from typing import Optional

REDIS_URL = "redis://localhost:6379"

redis = get_redis_connection(url=REDIS_URL)


class UserJsonCache( JsonModel ):
    id: int = Field(index=True)
    name : str = Field(index=True)
    email: str = Field(index=True)
    avatar:Optional[str] =  Field(index=False)

    class Meta:
        database = redis

class UserHashCache( HashModel ):
    id: int = Field(index=True)
    name : str = Field(index=True)
    email: str = Field(index=True)
    avatar:Optional[str] =  Field(index=False)

    class Meta:
        database = redis


Migrator().run()

def test_create_user_json():
    new_user = UserJsonCache(id=1,name="json_user",email="json_user@email.com",avatar="image_url")
    new_user.save()
    pk = new_user.pk
    assert UserJsonCache.get(pk) == new_user

def test_find_user_json():
    user_be_found = UserJsonCache(id=1,name="json_user",email="json_user@email.com",avatar="image_url")
    res = UserJsonCache.find( UserJsonCache.id==1 ).first()

    assert res.id == user_be_found.id
    assert res.name == user_be_found.name
    assert res.email == user_be_found.email
    assert res.avatar == user_be_found.avatar
    '''
    We can't use assert `res == user_be_found` because `pk` is different
    '''


def test_create_user_hash():
    new_user = UserHashCache(id=2,name="hash_user",email="hash_user@email.com",avatar="image_url")
    new_user.save()
    pk = new_user.pk
    assert UserHashCache.get(pk) == new_user

def test_find_user_hash():
    user_be_found = UserHashCache(id=2,name="hash_user",email="hash_user@email.com",avatar="image_url")
    res = UserHashCache.find( UserHashCache.id==2 ).first()
    assert res.id == user_be_found.id
    assert res.name == user_be_found.name
    assert res.email == user_be_found.email
    assert res.avatar == user_be_found.avatar

# try:
#     print("Add new User")
#     new_user = UserJsonCache(id=1,name="json_user",email="json_user@email.com")
#     new_user.save()

#     print("PK" , new_user.pk )
#     print("Use pk to find user")
#     print( UserJsonCache.get( new_user.pk ).dict() )
#     # print( new_user.pk )
# except Exception as e:
#     print(e)
#     pass

# try:
#     print( redis.get("user:1") )
#     print( redis.get("01HCA25H214RBP3SV522N4QBPH"))
#     res = UserJsonCache.find( UserJsonCache.name == "json_user" ).all()
#     print(res)

# except Exception as e:
#     print(e)
#     print("not found")
#     pass

