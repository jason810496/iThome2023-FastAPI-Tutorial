from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , update , delete


from database.generic import crud_class_decorator
from models.user import User as UserModel 
from schemas import users as UserSchema

from auth.passwd import get_password_hash
from database.redis_cahe import  generic_cache_get , user_cache_delete , generic_cache_update , generic_pagenation_cache_get


@crud_class_decorator
class UserCrudManager:

    @generic_pagenation_cache_get(prefix="user",key="id",cls=UserSchema.UserRead)
    async def get_users(self,last:int=0,limit:int=50,keyword:str=None,db_session:AsyncSession=None):
        # async with get_db() as db_session:
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)

        result = await db_session.execute(stmt)
        users = result.all()

        return users
    
    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserInfor)
    async def get_user_infor_by_id(self,user_id:int ,db_session:AsyncSession) -> UserSchema.UserInfor:
        stmt = select(UserModel.name,UserModel.id,UserModel.birthday,UserModel.age,UserModel.avatar).where(UserModel.id == user_id)
        user = (await db_session.execute(stmt)).first()
        if user:
            return UserSchema.UserInfor(**user._asdict())
            
        return None
    
    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserRead)
    async def get_user_by_id(self,user_id:int, db_session:AsyncSession=None) -> UserSchema.CurrentUser:
        stmt = select(UserModel.email,UserModel.name,UserModel.id).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.CurrentUser(**user._asdict())
            
        return None

    @generic_cache_get(prefix="user",key="email",cls=UserSchema.UserId)
    async def get_user_id_by_email(self,email:str ,db_session:AsyncSession=None) -> UserSchema.UserId:
        stmt = select(UserModel.id).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.UserId(id=user.id)
            
        return None

    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserId)
    async def get_user_id_by_id(self,user_id:int ,db_session:AsyncSession=None) -> UserSchema.UserId:
        stmt = select(UserModel.id).where(UserModel.id == user_id)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.UserId(id=user.id)
            
        return None
    
    @generic_cache_get(prefix="user",key="email",cls=UserSchema.UserInDB)
    async def get_user_in_db(self,email:str , db_session:AsyncSession=None) -> UserSchema.UserInDB :
        stmt = select(UserModel.id,UserModel.name,UserModel.password).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return UserSchema.UserInDB(**user._asdict())
            
        return None



    async def create_user(self,newUser:UserSchema.UserCreate , db_session:AsyncSession=None ):
        user = UserModel(
            name=newUser.name,
            password=get_password_hash(newUser.password),
            age=newUser.age,
            birthday=newUser.birthday,
            email=newUser.email,
            avatar=newUser.avatar
        )

        db_session.add(user)
        await db_session.commit()

        return user


    @generic_cache_update(prefix="user",key="user_id")
    async def update_user(self,newUser:UserSchema.UserUpdate , user_id:int , db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            name=newUser.name,
            age=newUser.age,
            birthday=newUser.birthday,
            avatar=newUser.avatar
        )

        await db_session.execute(stmt)
        await db_session.commit()

        return newUser
    
    @generic_cache_update(prefix="user",key="user_id")
    async def update_user_password(self,newUser:UserSchema.UserUpdatePassword, user_id:int , db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            password=get_password_hash(newUser.password)
        )

        await db_session.execute(stmt)
        await db_session.commit()

        return
    
    @user_cache_delete(prefix="user",key="user_id")
    async def delete_user(self,user_id:int, db_session:AsyncSession=None):
        stmt = delete(UserModel).where(UserModel.id == user_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return 