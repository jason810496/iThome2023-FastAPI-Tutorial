# [Day20] OAuth2 實例：實作總結

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day20 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day20)** <br>


## 回顧

我們在
- [Day17](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day17) 完成 hash password 的實作
- [Day18](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day18) 完成 OAuth2 login 和 <br>
    Bearer token Schema 的實作  <br>
    與 JWT token 的實作
- [Day19](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day19) 完成 Authorize Dependency 和 權限管理 的實作  

<br>

今天我們會完成整體 OAuth2 Authentication 的實作 <br>
把各個部分串起來 <br>
並修好細節 ! <br>


## Hash Password 修正

### 單一 Password 更新 Router
在 `PUT /user/{user_id}` 與 `PUT /user/{user_id}/password` 的時候 <br>
這兩個 API 都會更新密碼 <br>
應該改為 `PUT /user/{user_id}/password` 這個 API 才會更新密碼比較合適 <br>

`schemas/user.py`
```python

# ...   

class UserUpdate(UserBase):
    #password: Optional[str] = Field(min_length=6) # <------ 移除 
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0,lt=100)
    birthday: Optional[date] = Field()

# ...

```

<br>

`api/user.py`
```python

@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
    # ...

    # newUser.password = get_password_hash(newUser.password) # <------ 移除

    await UserCrud.update_user(newUser,user_id)
    return newUser
```

<br>

`crud/user.py`
```python
# ...
    async def update_user(self,newUser: UserSchema.UserUpdate,user_id:int, db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            # password=newUser.password, # <------ 新增
            name=newUser.name,
            age=newUser.age,
            birthday=newUser.birthday,
            avatar=newUser.avatar
        )
```

<br>

### Hash Password 注入點

在 `create_user` 、 `update_user_password` 這兩個 API 中 <br>
將明碼密碼改成 hash 過的密碼都是寫在 `api/user.py` 中 <br>
應該把這部分的邏輯寫在 `crud/user.py` 中 <br>

<br>

`api/users.py`
```python

# ... 
async def create_user(newUser: UserSchema.UserCreate ):

    # ...

    # newUser.password = get_password_hash(newUser.password) # <------ 移除
    user = await UserCrud.create_user(newUser)
    return vars(user)


async def update_user_password(newUser:UserSchema.UserUpdatePassword,user_id:int=Depends(check_user_id)):

    # newUser.password = get_password_hash(newUser.password) # <------ 移除
    await UserCrud.update_user_password(newUser,user_id)
    return 
```

<br>

`crud/user.py`
```python

    async def create_user(self,newUser: UserSchema.UserCreate, db_session:AsyncSession=None ):
        user = UserModel(
            name=newUser.name,
            password=get_password_hash(newUser.password), # <------ 新增
            # ...
        )
        # ...
        return user

    # ...

    async def update_user_password(self,newUser: UserSchema.UserUpdatePassword,user_id:int, db_session:AsyncSession=None):
        stmt = update(UserModel).where(UserModel.id == user_id).values(
            password=get_password_hash(newUser.password), # <------ 新增
        )
        # ...
```

<br>

## 驗證權限

我們在 [Day19](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day19) 只有為 `update_user` 這個 API 加上了權限驗證 <br>

<br>

接下來加上 `CurrentUser` Schema 確保傳遞正確 <br>
並為所有需要驗證權限的 API 加上 `get_current_user` dependency <br>
- `PUT /user/{user_id}`
- `PUT /user/{user_id}/password`
- `DELETE /user/{user_id}`

<br>

`schemas/user.py`
```python

class CurrentUser(BaseModel):
    id: int
    name: str
    email: str
```

<br>

`api/user.py`
```python

# ...
async def update_user_password(
    newUser:UserSchema.UserUpdatePassword,
    user_id:int=Depends(check_user_id),
    current_user:UserSchema.CurrentUser=Depends(get_current_user) # <------ 新增
):
    # ...
    if current_user.id != user_id: # <------ 新增
        raise Exception403
    # ...

# ...
async def delete_users(
    user_id:int = Depends(check_user_id),
    user:UserSchema.CurrentUser = Depends(get_current_user) # <------ 新增
):

    # ...
    if user.id != user_id:
        raise Exception403
    # ...
```

## Item 相關功能

### Item Schema

我們為 `GET /items/{item_id}` 加上 `ItemInfor` Schema <br>
再新增 `UpdateItem` Schema <br>

<br>

`schemas/item.py`
```python
# ...

class ItemInfor(ItemRead):
    brand: str
    description: Optional[str] = None

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None
    brand: Optional[str] = None
    description: Optional[str] = None

# ...

```

<br>

### Item CRUD

我們從 CRUD 開始的範例都以 User 為主 <br>
所以 Item 的 CRUD 只需要照著 User 的 CRUD 做一些修改就可以了 <br>

<br>

先 import 相關的 Schema 、 Model <br>
和 SQLAlchemy 的操作、`AsyncSession` <br>
與 `crud_class_decorator` <br>
`crud/item.py`
```python
@crud_class_decorator
class ItemCrudManager:

    async def get_item(self, item_id: int):
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self.db_session.execute(stmt)
        return result.scalars().first()

    async def get_items(self, skip: int = 0, limit: int = 100):
        stmt = select(ItemModel).offset(skip).limit(limit)
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def create_item(self, newItem: ItemSchema.ItemCreate):
        item = ItemModel(
            name=newItem.name,
            price=newItem.price,
            brand=newItem.brand,
            description=newItem.description
        )
        self.db_session.add(item)
        await self.db_session.commit()
        await self.db_session.refresh(item)
        return item

    async def update_item(self, newItem: ItemSchema.ItemUpdate, item_id: int):
        stmt = update(ItemModel).where(ItemModel.id == item_id).values(
            name=newItem.name,
            price=newItem.price,
            brand=newItem.brand,
            description=newItem.description
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        return

    async def delete_item(self, item_id: int):
        stmt = delete(ItemModel).where(ItemModel.id == item_id)
        await self.db_session.execute(stmt)
        await self.db_session.commit()
        return

```

### Item 權限管理

接下來要為 Item 加上權限管理 <br>
避免 Item 被不屬於自己的 User 修改、刪除 <br>

<br>

所以一樣可以透過我們的 `get_current_user` 來取得當前的 User <br>
和 `check_item_id` 來確認 Item 是否存在 <br>
來檢查 `item.user_id` 是否等於 `current_user.id` <br>

<br>

`api/item.py`
```python
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
```

透過 `Depends` 來取得 `item` 和 `user` <br>
只需要額外加上一行判斷就可以完成權限管理！ <br>

<br>

當我們以 `user1` 的身份來修改 `test` 的 Item 時 <br>

![403](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day20/403.png)

就會回傳 `403 Permissison Denied` <br>

<br>

## 總結

延續著 User 與 Item 的 CRUD <br>
我們完成了整個 OAuth2 Authentication 的實作 <br>
並且加上了權限管理 <br>

![swagger](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day20/swagger.png)

快看到需要驗證權限的 API 都有 `lock` 的圖示了！ <br>

