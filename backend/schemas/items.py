from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    id: int

class ItemCreate(BaseModel):
    name: str
    price: float
    brand: str
    description: Optional[str] = None

class ItemCreateResponse(ItemBase):
    name: str
    price: float
    brand: str
    description: Optional[str] = None

class ItemRead(ItemBase):
    name: str
    price: float

class ItemInfor(ItemRead):
    brand: str
    description: Optional[str] = None

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    description: Optional[str] = None

class CurrentItem(ItemBase):
    id: int
    user_id: int