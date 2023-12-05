from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select , update , delete

from database.injection import crud_class_decorator
from models.item import Item as ItemModel 
from schemas import items as ItemSchema




@crud_class_decorator
class ItemCrudManager:

    async def get_items(self,
                        keyword:str=None,
                        last:int=0,
                        limit:int=50,
                        db_session:AsyncSession=None) -> List[ItemSchema.ItemRead]:
        stmt = select(ItemModel.name,ItemModel.id,ItemModel.name,ItemModel.price)
        if keyword:
            stmt = stmt.where(ItemModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)

        result = await db_session.execute(stmt)
        items = result.all()

        return items

    async def get_item_by_id(self,item_id: int,db_session:AsyncSession) -> ItemSchema.ItemInfor:
        stmt = select(ItemModel.id,ItemModel.name,ItemModel.price,ItemModel.brand,ItemModel.description).where(ItemModel.id == item_id)
        item = (await db_session.execute(stmt)).first()
        if item:
            return item
        return None

    async def create_item(self,newItem: ItemSchema.ItemCreate,user_id:int ,db_session:AsyncSession=None) -> ItemSchema.ItemCreate:
        item = ItemModel(
            name=newItem.name,
            brand=newItem.brand,
            price=newItem.price,
            description=newItem.description,
            user_id=user_id
        )

        db_session.add(item)
        await db_session.commit()
        return item
    
    async def update_item_by_id(self,item_id:int,updateItem: ItemSchema.ItemUpdate,db_session:AsyncSession=None) :
        stmt = update(ItemModel).where(ItemModel.id == item_id).values(**updateItem.model_dump())
        await db_session.execute(stmt)
        await db_session.commit()
        return updateItem

    async def delete_item_by_id(self,item_id:int,db_session:AsyncSession=None):
        stmt = delete(ItemModel).where(ItemModel.id == item_id)
        await db_session.execute(stmt)
        await db_session.commit()

        return True

    async def get_item_in_db_by_id(self,item_id:int,db_session:AsyncSession=None):
        stmt = select(ItemModel.id,ItemModel.user_id).where(ItemModel.id == item_id)
        result = await db_session.execute(stmt)
        item = result.first()
        if item:
            return item
        return None