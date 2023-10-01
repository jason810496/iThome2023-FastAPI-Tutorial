from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine , async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from setting.config import get_settings

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


async def get_db():
    async with SessionLocal() as db:
        async with db.begin():
            yield db

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    async with engine.begin() as conn:
        await conn.close()
    