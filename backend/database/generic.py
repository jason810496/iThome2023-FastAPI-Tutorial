from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine , async_sessionmaker
from sqlalchemy.orm import DeclarativeBase 
from sqlalchemy.schema import CreateTable

from setting.config import get_settings
from models.user import User
from models.item import Item

settings = get_settings()

# Create engine
engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_pre_ping=True
)

# Create session
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, autocommit=False)

class Base(DeclarativeBase):
    pass

@asynccontextmanager
async def get_db():
    async with SessionLocal() as db:
        async with db.begin():
            yield db

async def init_db():
    async with SessionLocal() as db:
        async with db.begin():
            await db.execute(CreateTable(User.__table__,if_not_exists=True))
            await db.execute(CreateTable(Item.__table__,if_not_exists=True))

async def close_db():
    async with engine.begin() as conn:
        await conn.close()


# decorator dependency for getting db session

def db_session_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        async with get_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    # print("out db_context_decorator")
    return wrapper

def crud_class_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))
    # print("out db_class_decorator")
    return cls
