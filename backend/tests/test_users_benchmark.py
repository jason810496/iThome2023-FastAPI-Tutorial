import json 
import pytest
from functools import lru_cache
import random


@lru_cache()
def get_user_data():
    data = []

    for i in range(100):
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
    for i in range(50000):
        data.append(random.choice(user_list))

    return data


def get_random_user():
    return [ random.choice(get_user_data()) ]

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


@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_invalid_email_user(async_client,user):
    payload = user.copy()
    payload["email"] = "wr@ong@email.com"
    response = await async_client.post("/api/users",json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_invalid_name_user(async_client,user):
    payload = user.copy()
    payload["name"] = "ab"
    response = await async_client.post("/api/users",json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_invalid_password_user(async_client,user):
    payload = user.copy()
    payload["password"] = "abc"
    response = await async_client.post("/api/users",json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_invalid_age_user(async_client,user):
    payload = user.copy()
    payload["age"] = 0
    response = await async_client.post("/api/users",json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_invalid_birthday_user(async_client,user):
    payload = user.copy()
    payload["birthday"] = "00-00-0000"
    response = await async_client.post("/api/users",json=payload)
    assert response.status_code == 422

@pytest.mark.parametrize("user",get_random_user())
@pytest.mark.asyncio
async def test_create_duplicate_user(async_client,user):
    response = await async_client.post("/api/users",json=user)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_get_users(async_client):
    response = await async_client.get("/api/users")

    assert response.status_code == 200
    assert list(response.json()[0].keys()) == [ "name","id","email","avatar"]

@pytest.mark.parametrize("user",get_random_user_list())
@pytest.mark.asyncio
async def test_get_user_by_id(async_client,user):
    user_id = await get_user_id(async_client,user)
    response = await async_client.get(f"/api/users/{user_id}")

    assert response.status_code == 200
    assert list(response.json().keys()) == [ "name","id","birthday","age","avatar"]

@pytest.mark.asyncio
async def test_get_user_not_found(async_client):
    response = await async_client.get(f"/api/users/0")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_update_user(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    
    payload = user.copy()
    payload["name"] += " Updated"
    payload["avatar"] = "avatar_url_updated"
    payload["age"] = 20

    response = await async_client.put(f"/api/users/{user_id}",json=payload,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_update_invalid_schema(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    
    payload = user.copy()
    payload["age"] = "-1"

    response = await async_client.put(f"/api/users/{user_id}",json=payload,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 422


@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_update_user_unauthorized(async_client,user):
    user_id = await get_user_id(async_client,user)
    payload = user.copy()

    response = await async_client.put(f"/api/users/{user_id}",json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_update_user_password(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    payload = {
        "password": user["password"],
    }

    response = await async_client.put(f"/api/users/{user_id}/password",json=payload,headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204

@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_update_user_password_unauthorized(async_client,user):
    user_id = await get_user_id(async_client,user)
    payload = {
        "password": user["password"],
    }

    response = await async_client.put(f"/api/users/{user_id}/password",json=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_random_user())
async def test_delete_user_unauthorized(async_client,user):
    user_id = await get_user_id(async_client,user)
    response = await async_client.delete(f"/api/users/{user_id}")
    assert response.status_code == 401

@pytest.mark.asyncio
@pytest.mark.parametrize("user",get_user_data())
async def test_delete_user(async_client,user):
    user_id = await get_user_id(async_client,user)
    access_token = await get_access_token(async_client,user)
    
    response = await async_client.delete(f"/api/users/{user_id}",headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 204
