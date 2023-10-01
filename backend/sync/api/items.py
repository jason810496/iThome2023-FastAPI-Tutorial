from fastapi import APIRouter, HTTPException , Depends

from typing import List 
from schemas import items as ItemSchema
from sync.api.depends import check_item_id , pagination_parms
from sync.crud import items as ItemCrud


router = APIRouter(
    tags=["items"],
    prefix="/sync/api"
)


@router.get("/items" , response_model=List[ItemSchema.ItemRead])
def get_items(page_parms:dict= Depends(pagination_parms)):
    items = ItemCrud.get_items(**page_parms)
    return items

@router.get("/items/{item_id}" , response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id : int):
    item = ItemCrud.get_item_by_id(item_id)
    if item:
        return item
        
    raise HTTPException(status_code=404, detail="Item not found")

@router.post("/items" , response_model=ItemSchema.ItemCreate)
def create_items(newItem: ItemSchema.ItemCreate ):

    item = ItemCrud.create_item(newItem)
    return item


@router.delete("/items/{item_id}")
def delete_items(item_id:int = Depends(check_item_id)):
        
    ItemCrud.delete_item(item_id)
    return