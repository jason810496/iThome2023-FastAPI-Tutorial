from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , update , delete
import hashlib


from database.generic import get_db , crud_class_decorator
from models.user import User as UserModel 
from schemas import users as UserSchema



@crud_class_decorator
class UserCrudManager:

    async def get_users(self,keyword:str=None,last:int=0,limit:int=50,db_session:AsyncSession=None):
        # async with get_db() as db_session:
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)

        result = await db_session.execute(stmt)
        users = result.all()

        return users

    async def get_user_infor_by_id(self,user_id: int,db_session:AsyncSession):

        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()
        if user:
            return user
            
        return None
    
    async def get_user_by_id(self,user_id: int,db_session:AsyncSession=None):
        stmt = select(UserModel.email,UserModel.name,UserModel.id).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user
            
        return None

    async def get_user_id_by_email(self,email: str,db_session:AsyncSession=None):
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user
            
        return None

    async def get_user_id_by_id(self,user_id: int,db_session:AsyncSession=None):
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user
            
        return None
    
    async def get_user_in_db(self,email: str,db_session:AsyncSession=None) -> UserSchema.UserInDB :
        stmt = select(UserModel.id,UserModel.name,UserModel.password).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user
            
        return None


    async def create_user(self,newUser: UserSchema.UserCreate, db_session:AsyncSession=None ):
        user = UserModel(
            name=newUser.name,
            password=newUser.password,
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar
        )

        db_session.add(user)
        await db_session.commit()

        return user

    async def update_user(self,newUser: UserSchema.UserUpdate,user_id:int, db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            name=newUser.name,
            password=newUser.password,
            age=newUser.age,
            birthday=newUser.birthday,
            avatar=newUser.avatar
        )

        await db_session.execute(stmt)
        await db_session.commit()

        return newUser
    
    async def update_user_password(self,newUser:UserSchema.UserUpdatePassword,user_id:int, db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            password=hashlib.md5(b'secret'+newUser.password.encode().hexdigest())
        )

        await db_session.execute(stmt)
        await db_session.commit()

        return
    
    async def delete_user(self,user_id:int, db_session:AsyncSession=None):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return