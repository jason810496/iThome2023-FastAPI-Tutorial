from fastapi import HTTPException
from fastapi.params import Header
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select 

from models.user import User as UserModel
from crud.users import UserCrudManager
from crud.items import ItemCrudManager

UserCrud = UserCrudManager()
ItemCrud = ItemCrudManager()

async def check_user_id(user_id:int):
    user = await UserCrud.get_user_id_by_id(user_id=user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

async def check_item_id(item_id:int):
    item = await ItemCrud.get_item_in_db_by_id(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

def pagination_parms(keyword:Optional[str]=None,last:int=0,limit:int=50):
    return {
        "keyword":keyword,
        "last":last,
        "limit":limit
    }

class paginationParms:
    def __init__(self,keyword:Optional[str]=None,last:int=0,limit:int=50):
        self.keyword = keyword
        self.last = last
        self.limit = limit

def test_verify_token(verify_header: str = Header()):
    if verify_header != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return verify_header


