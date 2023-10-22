import pytest
from redis_om import get_redis_connection
from redis_om import JsonModel , HashModel , Migrator , Field
from redis_om import NotFoundError
from typing import Optional , List

from pydantic import EmailStr
from datetime import date

# from schemas.users import 

REDIS_URL = "redis://localhost:6379"

redis = get_redis_connection(url=REDIS_URL)


class UserCache( HashModel ):
    id: int = Field(index=True)
    name:str = Field(index=True)
    password:Optional[str] = Field(index=False)
    name: Optional[str] = Field(index=True)
    avatar: Optional[str] = Field(index=False)
    age: Optional[int] = Field(index=False,default=0)
    email: str = Field(index=True)
    birthday: Optional[str] = Field(index=False)

    # def __init__(self, id: int, name: str, email: str, avatar: Optional[str] = None, age: Optional[int] = None, birthday: Optional[str] = None):
    #     self.id = id
    #     self.name = name
    #     self.email = email
    #     self.avatar = avatar
    #     self.age = age
    #     self.birthday = birthday

    class Meta:
        database = redis


Migrator().run()

def test_create_user():
    new_user = UserCache(id=1,name="user",email="user@email.com" , avatar="image_url" , password=None, age=0, birthday=None)
    new_user.save()

    pk = new_user.pk
    assert UserCache.get(pk) == new_user

def test_find_user_by_id():
    user_id = 1
    user_be_found = UserCache.find( UserCache.id==user_id ).first()
    assert user_be_found.id == user_id

    print("condition",UserCache.id==user_id)   
    print("password condition",UserCache.password==None) 




