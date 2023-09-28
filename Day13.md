# [Day13] 架構優化： Depends 萬用刀 & 常見錯誤


> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day13 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day13)** <br>

## 回顧 & 介紹

我們從 [Day10](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10) 到 [Day12](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day12) 完成：
- 連結 DB connection ，並可以透過 `argumnets` 來切換 DB
- 定義 `User` 與 `Item` 的 DB Model
- 透過 SQLalchemy ORM 來實現 `User` 與 `Item` 的 CRUD

今天我們要來談 FastAPI 中的 Dependency Injection (DI) <br>
`Depends` 來幫助我們將常用的 function 或 class 注入到 router 中 <br>
減少重複的程式碼 <br>

<br>

> 在 FastAPI 中，只要是 **callable** 的都可以被 `Depends` 來注入 <br>
> 如： class 和 function <br>

## Dependency Injection


觀察昨天寫的 user CRUD ， 會發現我們在每個 router 中都需要 `db_session` <br>
```python
# ...
def get_users(qry: str = None):
    db_session:Session = get_db()

    # ...

# ....

def get_user_by_id(user_id: int):
    db_session:Session = get_db()

    # ...

```
<br>

所以我們可以將 `db_session` 抽出來，直接定義在 `users.py` 最上方 <br>
> 這是所有 `.py` 都可以用的方式 <br>
> 還沒有使用到 FastAPI 中暑的 `Depends` 語法 <br>

```python 
# ...

router = APIRouter(
    tags=["users"],
    prefix="/api"
)

db_session:Session = get_db() # 將 `get_db` 從每個 router 抽出來

```


## Depends

### Repeatable code
在 FastAPI 中，需要從 `fastapi` import `Depends` <br>
`api/user.py`
```python
from fastapi import Depends
```
<br>

再次觀察剛剛 CRUD 的 code ， 會發現**檢查 user 是否存在**的 code 出現很多次 <br>
```python
    # ... 
    stmt = select(UserModel.id).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # ...
```
所以可以將檢查是否有該 user 的 function 抽出來 <br>
作為 Depends 注入到 router 中 <br>

<br>

新增 `api/depends.py` <br>

```python
from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import select 

from models.user import User as UserModel
from database.generic import get_db



def check_user_id(user_id:int):
    db_session:Session = get_db()

    stmt = select(UserModel.id).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id
```


在 `api/user.py` 中引入 `check_user_id` <br>
並且將 `get_user_by_id` 的 `user_id` 改為 `user_id:int = Depends(check_user_id)` <br>
```python

from fastapi import Depends

from api.depends import check_user_id

# ...

@router.delete("/users/{user_id}",status_code=status.HTTP_204_NO_CONTENT )
def delete_users(user_id:int = Depends(check_user_id) ):
    
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return 
```

<br>

![delete depends](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day13/delete-depends.png)
可以看到 path parameter 仍然要求要是 `int` <br>
並當我們輸入不存在的 user id 時，會 raise `HTTPException` 404 error code <br>

<br>

需要**特別注意** 的是，如果 `Depends` 的包含 path parameter <br>
不能將 `Depends` 放在 function 參數的最前面 <br>

`api/users.py` update_user 錯誤範例 ：
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
def update_user(user_id:int=Depends(check_user_id), newUser: UserSchema.UserUpdate ):
    # ...
```

![update depends error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day13/update-depends-error.png)

因為這違反 python 的語法 <br>
**「有預設值的參數」必須放在「沒有預設值的參數」後面** <br>
所以要將 `Depends` 放在 `user_id` 後面 <br>

<br>

`api/users.py` update_user 正確範例 ：
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
def update_user(newUser: UserSchema.UserUpdate,user_id:int=Depends(check_user_id) ):
    
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        name=newUser.name,
        # ....
    )

    # ...
```

### Common query params

除了可以使用 `Depends` 來注入 重複的 function 外 <br>
也可以透過 `Depends` 來注入常用的 query params <br>
如 get_users 和 get_items 的 API 常需要做 **pagination** (分頁) <br>
我們可以把 pagination 的所有 query params 抽出來 <br>
當成 `Depends` 注入到 router 中 <br>

<br>

而在 FastAPI 中有兩種注入方式：
- **透過 class**
- **透過 function**

<br>

**透過 class** :
<br>

透過 class 注入重複的 pagination query params <br>
先定義 `keyword` , `last` , `limit` 三個 query params 和預設值 <br>

`api/depends.py`
```python

class paginationParms:
    def __init__(self,keyword:Optional[str]=None,last:int=0,limit:int=50):
        self.keyword = keyword
        self.last = last
        self.limit = limit
```

<br>

接著就可以透過 `Annotated` 搭配 `Depends` 來注入 <br>
`api/users.py`
```python

from api.depends import paginationParms
# ...

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(page_parms:Annotated[paginationParms,Depends(pagination_parms)]):
    # ...
```

<br>

**透過 function**

<br>

在最一開頭有提到，只要是 **callable** 的都可以被 `Depends` 來注入 <br>
所以這邊以 function 來實現 <br>

`api/depends.py`
```python

def pagination_parms(keyword:Optional[str]=None,last:int=0,limit:int=50):
    return {
        "keyword":keyword,
        "last":last,
        "limit":limit
    }
```

<br>

並注意，這邊 `Depends` 中的 function 不需要加上 `()` <br>
`api/users.py`
```python

from api.depends import pagination_parms

# ...

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(page_parms=Depends(pagination_parms)):
    # ...
```

<br>

在 Swagger UI 中可以看到，這兩種方式都可以正常運作 <br>
都有看到 `keyword` , `last` , `limit` 三個 query params <br>

![pagination depends](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day13/pagination-depends.png)

## `Depends` 的其他常見用法

如我們的 API 需要帶入我們自訂的 Header 來做驗證 <br>
可以在 `router` 中加入 `dependencies=[Depends(xxx)]` <br>

`api/depeneds.py`
```python
from fastapi.params import Header
# ...

def test_verify_token(verify_header: str = Header()):
    if verify_header != "secret-token":
        raise HTTPException(status_code=403, detail="Forbidden")
    return verify_header
```

`api/users.py`
```python

from api.depends import test_verify_token

# ...

router = APIRouter(
    tags=["users"],
    prefix="/api",
    dependencies=[Depends(test_verify_token)]
)
```

<br>

![header depends](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day13/header-depends.png)

<br>

如果要驗證多個 Header 可以在 `dependencies=[]`的 list 中加入多個 `Depends` <br>
```python
router = APIRouter(
    tags=["users"],
    prefix="/api",
    dependencies=[
        Depends(test_verify_token),
        Depends(test_verify_token2)
    ]
)
```

## 總結

- `Depends` 只要是 **callable** 的都可以被注入 <br>
    如： class 和 function <br>
- `Depends` 可以將常用的 function 或 class 注入到 **router handler** 中 <br>
    來減少重複的程式碼 <br>
- `Depends` 可以注入 **path parameter** <br>
    但不能放在 function 參數的最前面 <br>
-  可以將多個重複的 query params 抽出來 <br>
    並透過 `Depends` 注入到 router 中 <br>

## Reference
- [FastAPI : Depends](https://fastapi.tiangolo.com/tutorial/dependencies/) 
- [FastAPI : Class as dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/) 
- [FastAPI : Global Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/global-dependencies/)




