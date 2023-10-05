from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete
import hashlib


from sync.database.generic import get_db
from models.user import User as UserModel 
from schemas import users as UserSchema

db_session:Session = get_db()

def get_users(keyword:str=None,last:int=0,limit:int=50):
    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
    if keyword:
        stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
    stmt = stmt.offset(last).limit(limit)
    users =  db_session.execute(stmt).all()

    return users

def get_user_infor_by_id(user_id: int):

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