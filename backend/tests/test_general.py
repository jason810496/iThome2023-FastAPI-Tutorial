import json 
import pytest
from functools import lru_cache
import random

USER_AMOUNT = 500
QUERY_AMOUNT = 50000
UPDATE_AMOUNT = 50

@lru_cache()
def get_user_data():
    data = []

    for i in range(USER_AMOUNT):
        data.append({
            "name": f"bench_user_{i}",
            "email": f"bench_user_{i}@email.com",
            "password" : "123456",
            "avatar": "avatar_url",
            "age": 10,
            "birthday": "2000-01-01"
        })

    return data


def get_random_user_list():
    user_list = get_user_data()
    data = []
    for i in range(QUERY_AMOUNT):
        data.append(random.choice(user_list))

    return data

def get_random_user_list_for_update():
    user_list = get_user_data()
    data = []
    for i in range(UPDATE_AMOUNT):
        data.append(random.choice(user_list))

    return data

def get_random_page_range_list():
    data = []
    for i in range(QUERY_AMOUNT):
        l = random.randrange(0,USER_AMOUNT-2)
        r = random.randrange(l+1,USER_AMOUNT-1)
        # l = 0
        # r = 50
        data.append( ( l, r ) )

    return data


async def get_user_id(async_client,user):
    response = await async_client.get(f"/api/users?last=0&limit=50&keyword={user['name']}")
    assert response.status_code == 200
    return response.json()[0]["id"]

async def get_access_token(async_client,user):
    payload = {
        "grant_type" : "",
        "username": user["email"],
        "password": user["password"],
        "scope": "",
        "client_id": "",
        "client_secret": ""
    }
    response = await async_client.post("/api/auth/login",data=payload,headers={"Content-Type": "application/x-www-form-urlencoded"})

    assert response.status_code == 200
    access_token = response.json()["access_token"]
    return access_token


@pytest.mark.parametrize("user",get_user_data())
@pytest.mark.asyncio
async def test_create_user(async_client,user):
    response = await async_client.post("/api/users",json=user)

    assert response.status_code == 201
    assert response.json()["name"] == user["name"]
    assert response.json()["email"] == user["email"]
    assert response.json()["id"] == await get_user_id(async_client,user)


@pytest.mark.parametrize("l,r",get_random_page_range_list())
@pytest.mark.asyncio
async def test_get_users(async_client,l,r):
    limit = r - l
    print("l" , l)
    print("limit" , limit)

    response = await async_client.get(f"/api/users?last={l}&limit={limit}")
    

    assert response.status_code == 200

    if len(response.json()) == 0:
        assert response.json() == []
        return

    assert list(response.json()[0].keys()) == [ "name","id","email","avatar"]

@pytest.mark.parametrize("user",get_random_user_list())
@pytest.mark.asyncio
async def test_get_user_by_id(async_client,user):
    user_id = await get_user_id(async_client,user)
    response = await async_client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert list(response.json().keys()) == [ "name","id","birthday","age","avatar"]


@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user_list_for_update())
async def test_update_user(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    
    payload = user.copy()
    payload["avatar"] = "avatar_url_updated" + str(random.randint(0,100))
    payload["age"] = random.randint(1,99)

    response = await async_client.put(f"/api/users/{user_id}",json=payload,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["avatar"] == payload["avatar"]
    assert response.json()["age"] == payload["age"]

    # reset
    await async_client.put(f"/api/users/{user_id}",json=user.copy(),headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


@pytest.mark.parametrize("user",get_random_user_list())
@pytest.mark.asyncio
async def test_get_user_by_id_2(async_client,user):
    user_id = await get_user_id(async_client,user)
    response = await async_client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert list(response.json().keys()) == [ "name","id","birthday","age","avatar"]


@pytest.mark.parametrize("l,r",get_random_page_range_list())
@pytest.mark.asyncio
async def test_get_users_2(async_client,l,r):
    limit = r - l
    print("l" , l)
    print("limit" , limit)

    response = await async_client.get(f"/api/users?last={l}&limit={limit}")
    

    assert response.status_code == 200
    assert list(response.json()[0].keys()) == [ "name","id","email","avatar"]



@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_user_data())
async def test_delete_user(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    
    response = await async_client.delete(f"/api/users/{user_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
