from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete

from database.generic import get_db
from models.item import Item as ItemModel 
from schemas import items as ItemSchema

db_session:Session = get_db()

def get_items(keyword:str=None,last:int=0,limit:int=50):
    stmt = select(ItemModel.name,ItemModel.id,ItemModel.email,ItemModel.avatar)
    if keyword:
        stmt = stmt.where(ItemModel.name.like(f"%{keyword}%"))
    stmt = stmt.offset(last).limit(limit)
    items =  db_session.execute(stmt).all()

    return items

def get_item_by_id(item_id: int):

    stmt = select(ItemModel.name,ItemModel.price).where(ItemModel.id == item_id)
    item = db_session.execute(stmt).first()
    if item:
        return item
        
    return None

def get_item_id_by_id(item_id: int):
    stmt = select(ItemModel.id).where(ItemModel.id == item_id)
    item = db_session.execute(stmt).first()
    if item:
        return item
        
    return None

def create_item(newItem: ItemSchema.ItemCreate,user_id:int ):
    item = ItemModel(
        name=newItem.name,
        price=newItem.price,
        description=newItem.description,
        user_id=user_id
    )

    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item

def delete_item(item_id:int):
    stmt = delete(ItemModel).where(ItemModel.id == item_id)
    db_session.execute(stmt)
    db_session.commit()

    return True