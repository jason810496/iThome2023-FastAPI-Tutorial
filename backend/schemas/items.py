from pydantic import BaseModel

class ItemBase(BaseModel):
    id: int

class ItemCreate(ItemBase):
    name: str
    price: float
    brand: str

class ItemRead(ItemBase):
    name: str
    price: float