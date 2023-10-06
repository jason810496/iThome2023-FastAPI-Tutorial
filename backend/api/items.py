from fastapi import APIRouter, HTTPException , Depends

from typing import List 
from schemas.items import ItemCreate , ItemRead , ItemInfor , ItemUpdate , CurrentItem , ItemCreateResponse
from schemas.users import CurrentUser
from api.depends import check_item_id , pagination_parms
from crud.items import ItemCrudManager
from auth.utils import get_current_user


router = APIRouter(
    tags=["items"],
    prefix="/api"
)

ItemCrud = ItemCrudManager()


@router.get("/items" , response_model=List[ItemRead])
async def get_items(page_parms:dict= Depends(pagination_parms)):
    items = await ItemCrud.get_items(**page_parms)
    return items

@router.get("/items/{item_id}" , response_model=ItemInfor)
async def get_item_by_id(item_id : int):
    item = await ItemCrud.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item    
    
@router.post("/items" , response_model=ItemCreateResponse)
async def create_items(
    newItem: ItemCreate,
    user:CurrentUser = Depends(get_current_user)):

    item = await ItemCrud.create_item(newItem,user.id)
    return item

@router.put("/items/{item_id}" , response_model=ItemUpdate)
async def update_items(
    updateItem: ItemUpdate, 
    item:CurrentItem = Depends(check_item_id),
    user:CurrentUser = Depends(get_current_user)):
    
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    item = await ItemCrud.update_item_by_id(item.id,updateItem)
    return item


@router.delete("/items/{item_id}")
async def delete_items(
    item:CurrentItem = Depends(check_item_id),
    user:CurrentUser = Depends(get_current_user)):

    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    await ItemCrud.delete_item_by_id(item.id)
    return