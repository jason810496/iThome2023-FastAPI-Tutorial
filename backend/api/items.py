from fastapi import APIRouter, HTTPException

from typing import List , Dict
from schemas import items as ItemSchema
from database.fake_db import get_db

fake_db = get_db()
router = APIRouter(
    tags=["items"],
    prefix="/api"
)


@router.get("/items" , response_model=List[ItemSchema.ItemRead])
def get_items(qry: str = None):
    return fake_db['items']

@router.get("/items/{item_id}" , response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id : int , qry : str = None ):

    for item in fake_db["users"]:
        if item["id"] == item_id:
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/items" , response_model=ItemSchema.ItemCreate)
def create_items(newItem: ItemSchema.ItemCreate ):

    for item in fake_db["items"]:
        if item["id"] == newItem.id:
            raise HTTPException(status_code=409, detail="Item already exists")
        
    fake_db["items"].routerend(newItem)
    return newItem

@router.delete("/items/{item_id}")
def delete_items(item_id: int):
        
    for item in fake_db["items"]:
        if item["id"] == item_id:
            fake_db["items"].remove(item)
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")