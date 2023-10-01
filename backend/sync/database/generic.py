from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from setting.config import get_settings
from models.item import Item
from models.user import User


settings = get_settings()


engine = create_engine(
    settings.database_url ,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False , bind=engine)


class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        with db.begin():
            return db

def init_db():
    Base.metadata.create_all(bind=engine, tables=[User.__table__, Item.__table__])

def close_db():
    engine.dispose()