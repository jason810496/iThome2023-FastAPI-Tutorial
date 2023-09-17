from datetime import date

from pydantic import BaseModel

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    age: int
    email: str
    birthday: date

class UserRead(UserBase):
    email: str