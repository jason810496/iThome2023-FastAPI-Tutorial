from datetime import date

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    birthday: date