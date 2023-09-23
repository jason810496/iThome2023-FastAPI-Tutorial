from datetime import datetime
from typing import Annotated , Optional

from sqlalchemy.orm import DeclarativeBase , mapped_column
from sqlalchemy import String , Integer , DateTime

class Base(DeclarativeBase):
    pass

class BaseType:
    int_primary_key = Annotated[int, mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)]
    str_30 = Annotated[str, mapped_column(String(30))]
    str_50 = Annotated[str, mapped_column(String(50))]
    optional_str_50 = Annotated[Optional[str], mapped_column(String(50), nullable=True)]
    optional_str_100 = Annotated[Optional[str], mapped_column(String(100), nullable=True)]
    update_time = Annotated[datetime, mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)]
