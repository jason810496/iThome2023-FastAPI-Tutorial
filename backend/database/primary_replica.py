from random import choice

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine , async_sessionmaker
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.schema import CreateTable

from setting.config import get_primary_replica_settings
from models.user import User
from models.item import Item


settings = get_primary_replica_settings()

primary_engine = create_async_engine(
    settings.primary_database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=8, max_overflow=0,
    
)

replica_engine = create_async_engine(
    settings.replica_database_url,
    echo=True,
    pool_pre_ping=True,
    pool_size=8, max_overflow=0
)


primarySession = async_sessionmaker(primary_engine, expire_on_commit=False, autocommit=False)
replicaSession = async_sessionmaker(replica_engine, expire_on_commit=False, autocommit=False)
# readSessions = [primarySession,replicaSession]
# indexies = [0,1]

# idx = 0
flag = True

GET = "get"

class Base(DeclarativeBase):
    pass

@asynccontextmanager
async def get_primary_db():
    async with primarySession() as db:
        async with db.begin():
            yield db

@asynccontextmanager
async def get_read_db():

    flag = not flag  # toggle flag

    if flag:
        async with primarySession() as db:
            async with db.begin():
                yield db

    else:
        async with replicaSession() as db:
            async with db.begin():
                yield db

async def init_db():
    async with primarySession() as db:
        async with db.begin():
            await db.execute(CreateTable(User.__table__,if_not_exists=True))
            await db.execute(CreateTable(Item.__table__,if_not_exists=True))

async def close_db():
    async with primarySession.begin() as conn:
        await conn.close()

    async with replicaSession.begin() as conn:
        await conn.close()


# decorator dependency for getting db session

def db_session_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):

        # if GET in func.__name__: # original 
        if func.__name__[0] == 'g': # get
            async with get_read_db() as db_session:
                kwargs["db_session"] = db_session
                result = await func(*args, **kwargs)
                return result

        async with get_primary_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    return wrapper

def crud_class_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))
    # print("out db_class_decorator")
    return cls
