import pytest
from redis_om import get_redis_connection
from redis_om import JsonModel , HashModel , Migrator , Field
from redis_om import NotFoundError
from typing import Optional , List

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

class UserListHashCache( HashModel ):
    list : List[UserHashCache] = Field(index=True)


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

def test_update_user_json():
    user_be_updated = UserJsonCache.find( UserJsonCache.id==1 ).first()
    user_be_updated.name = "json_user_updated"
    user_be_updated.save()

    assert user_be_updated.name == "json_user_updated"

def test_update_user_hash():
    user_be_updated = UserHashCache.find( UserHashCache.id==2 ).first()
    user_be_updated.name = "hash_user_updated"
    user_be_updated.save()

    assert user_be_updated.name == "hash_user_updated"

def test_delete_user_json():
    be_deleted = UserJsonCache.find( UserJsonCache.id==1 ).first()
    UserJsonCache.delete(be_deleted.pk)
    
    with pytest.raises(NotFoundError) as e:
        UserJsonCache.find( UserJsonCache.id==1 ).first()
    assert e.type == NotFoundError

def test_delete_user_hash():
    be_deleted = UserHashCache.find( UserHashCache.id==2 ).first()
    UserHashCache.delete(be_deleted.pk)

    with pytest.raises(NotFoundError) as e:
        UserHashCache.find( UserHashCache.id==2 ).first()

    assert e.type == NotFoundError

def test_create_user_list_hash():
    # new_user1 = UserHashCache(id=3,name="hash_user1",email="hash_user1@email.com")
    # new_user2 = UserHashCache(id=4,name="hash_user2",email="hash_user2@email.com")
    # user_list = UserListHashCache(list=[ new_user1 , new_user2 ])

    # user_list.save()
    # pk = user_list.pk

    # assert UserListHashCache.get(pk) == user_list

    # try:
    #     be_deleted = UserHashCache.find( UserHashCache.id==2 ).first()
    #     UserHashCache.delete(be_deleted.pk)


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



# test_delete_user_hash()