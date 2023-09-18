from datetime import date

from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    id: int

class UserCreate(UserBase):
    password:str
    name: str
    avatar: Optional[str] = None
    age: int
    email: str
    birthday: date

class UserRead(UserBase):
    name: str
    email: str
    avatar: Optional[str] = None


# Prevent return plain text password
class UserCreateResponse(UserBase):
    name: str
    email: str