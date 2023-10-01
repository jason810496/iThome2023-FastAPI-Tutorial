from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , update , delete
import hashlib


from database.generic import get_db
from models.user import User as UserModel 
from schemas import users as UserSchema


# async def get_users(db_session:AsyncSession,keyword:str=None,last:int=0,limit:int=50):
#     stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
#     if keyword:
#         stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
#     stmt = stmt.offset(last).limit(limit)
#     result = await db_session.execute(stmt)
#     users = result.all()

#     return users

from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    async with get_db() as db_session:
        yield db_session

# db_session:AsyncSession = get_db_session()

def db_context_decorator(func):
    print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        async with get_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    print("out db_context_decorator")
    return wrapper

def db_class_decorator(cls):
    print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_context_decorator(method))
    print("out db_class_decorator")
    return cls

from fastapi import Depends

@db_class_decorator
class UserCrudManager:
    # def __init__(self):
    #     self.db_session = None

    # async def execute(self,stmt):
    #     if not self.db_session:
    #         async with get_db() as db_session:
    #             self.db_session = db_session
    #             result = await self.db_session.execute(stmt)
    #             print("new db session")
    #             return result

    #     # async with get_db() as db_session:  
    #     print("old db session")
    #     result = await self.db_session.execute(stmt)
    #     return result
    # @db_context_decorator
    async def get_users(self,db_session:AsyncSession,keyword:str=None,last:int=0,limit:int=50):
        # async with get_db() as db_session:
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)
        # result = await self.db_session.execute(stmt)
        result = await db_session.execute(stmt)
        users = result.all()

        return users

    async def get_user_by_id(self,user_id: int):

        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar).where(UserModel.id == user_id)
        user = await self.db_session.execute(stmt).first()
        if user:
            return user
            
        return None

    async def get_user_id_by_email(self,email: str):
        stmt = select(UserModel.id).where(UserModel.email == email)
        user = await self.db_session.execute(stmt).first()
        if user:
            return user
            
        return None

    async def get_user_id_by_id(self,user_id: int):
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        user = await self.db_session.execute(stmt).first()
        if user:
            return user
            
        return None


    async def create_user(self,newUser: UserSchema.UserCreate ):
        user = UserModel(
            name=newUser.name,
            password=newUser.password,
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar
        )

        self.db_session.add(user)
        await self.db_session.commit()
        await self.db_session.refresh(user)

        return user

    async def update_user(self,newUser: UserSchema.UserUpdate,user_id:int):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            name=newUser.name,
            password=newUser.password,
            age=newUser.age,
            birthday=newUser.birthday,
            avatar=newUser.avatar
        )

        await self.db_session.execute(stmt)
        await self.db_session.commit()

        return newUser


async def get_user_crud_manager():
    async with get_db() as db_session:
        user_crud_manager = UserCrudManager(db_session)
        yield user_crud_manager



async def get_users(keyword:str=None,last:int=0,limit:int=50):
    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
    if keyword:
        stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
    stmt = stmt.offset(last).limit(limit)
    result = await db_session.execute(stmt)
    users = result.all()

    return users

def get_user_by_id(user_id: int):

    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    return None

def get_user_id_by_email(email: str):
    stmt = select(UserModel.id).where(UserModel.email == email)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    return None

def get_user_id_by_id(user_id: int):
    stmt = select(UserModel.id).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    return None


def create_user(newUser: UserSchema.UserCreate ):
    user = UserModel(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        email=newUser.email,
        avatar=newUser.avatar
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user

def update_user(newUser: UserSchema.UserUpdate,user_id:int):
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        avatar=newUser.avatar
    )

    db_session.execute(stmt)
    db_session.commit()

    return newUser

def update_user_password(user_id:int,password:str):
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        password=hashlib.md5(password.encode()+b'secret').hexdigest()
    )

    db_session.execute(stmt)
    db_session.commit()

    return True

def delete_user(user_id:int):
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return True