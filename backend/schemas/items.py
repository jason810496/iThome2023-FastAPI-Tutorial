from typing import Optional
from pydantic import BaseModel

class ItemBase(BaseModel):
    id: int

class ItemCreate(ItemBase):
    name: str
    price: float
    brand: str
    description: Optional[str] = None

class ItemRead(ItemBase):
    name: str
    price: float