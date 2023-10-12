## [[Day25]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day25) 架構優化: Redis Cache , `redis-py` 架構初探

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day25 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day25)** <br>

## 前言

在 [昨天](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day25) 我們完成 Redis 的基本操作包括：
- 建立 Redis 連線
    - 使用 `Redis` 類別來建立連線
    - 以 `ConnectionPool` 來管理連線 
- 存取資料
    - 以 `redis-py` 提供的 `set` 、 `save`
    - 使用 `redis-om` 的 Object Mapping 來做 CRUD

<br>

有這些基本的認識後  <br>
今天可以嘗試使用 `redis-om` 來實作 Server Cache  <br>
並比較 `fastapi-cache` 和 `redis-py` 來實作 Cache 的差異 <br>

<br>

## Server Cache 架構

這次想實作的 Server Cache 是在 CRUD 層面的 Cache <br>
而不是在 Response  Level 的 Cache <br>

<br>

所以在遇到 `Read` 操作時，我們會先去 Cache 中尋找資料 <br>
如果 Cache 中有資料，則直接回傳 <br>
並把 `user_id` 當作 `key` 來存取 <br>

<br>

而 `Create` , `Update` , `Delete` 操作時 <br>
我們會依據 **選定的 Key** 來更新或刪除 key-value pair <br>

## 如果使用 `fastapi-cache` 實作

> [`fastapi-cache` Github](https://github.com/long2ice/fastapi-cache)

因為該套件主要是針對 Response Level 的 Cache <br>
是透過 decorator 來 Cache 我們要 Response 前的結果 <br>

<br>

用法大略如下：
    
```python
from fastapi_cache.decorator import cache

@app.get("/users/{user_id}")
@cache(expire=60) # <----- 60 秒後過期
async def read_user(user_id: int):
    return {"user_id": user_id}
```


<br>

但是 `fastapi-cache` 無法做到遇到: <br>
 「 `Create` , `Update` , `Delete` 操作時，要依需相對應的 Key 來更新刪除 Key-value Pair  」的操作 <br>

## 如果使用 `redis-om` 實作

如果由 `redis-om` 來實作的話 <br>
我們也需要先定義 `UserCacheModel` <br>


```python
class UserCache( JsonModel ):
    id: Optional[int] = Field(index=True)
    name:Optional[str] = Field(index=True)
    password:Optional[str] = Field(index=False)
    name: Optional[str] = Field(index=True)
    avatar: Optional[str] = Field(index=False)
    age: Optional[int] = Field(index=False,default=0)
    email: Optional[EmailStr] = Field(index=True)
    birthday: Optional[date] = Field(index=False)

    class Meta:
        database = redis
```

<br>


為了盡量不改動到 CRUD 的 Code <br>
我們可以使用 **decorator** 來實作 <br>
又因為讓 cache decorator 保留彈性，我們可以傳入 `key` 來當作 **目前應該要依據哪個欄位搜尋**  <br>
`cls` 則是 CRUD 回傳的 Schema <br>

<br>
因為我們的 decorator 有傳入參數，所以我們需要實作兩層的 decorator <br>

`database/redis_cache.py` <br>
```python
def generic_cache_get(key:str,cls):
    def inner(func):
        async def wrapper(*args, **kwargs):
            # TODO
            return wrapper
    return inner
```

再將內層 get 、 set 邏輯實作完 <br>
`database/redis_cache.py` <br>
```python
    try:
        redis_result = UserCache.find( ModelField(name=key,type=type(value_key)) == value_key ).first()
    except:
        redis_result = None

    if redis_result:
        return cls(**redis_result.dict())
    else:
        result = await func(*args, **kwargs)
        UserCache(**result.dict()).save()
        return result
```


### 使用 `redis-om` 內建 Model 實作的坑

會發現在使用上，每 `Model.save()` 一次後 <br>
在 `redis` 中就會多一個 `key` <br>

![redis new](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/redis-new.png)

假設我們要以 `user_id` 當 Key 的 Cache 資料只有 `id` , `name` , `email` , `avatar` 四個欄位 <br>
另一個以同樣以 `user_id` 最為 Key 的 Cache 資料只有 `id` , `password` 兩個欄位 <br>
還需要我們額外處理 <br>

<br>

又因為 `redis-om` 的 Model 是透過 `pydantic` 來實作 <br>
像是 email 綁定 `EmailStr` 、 birthday 綁定 `date` 會導致一些 Validation 的問題 <br>

![email str error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/email-str-error.png)

因為 `redis-om` 綁定 `pydantic` 的關係 <br>
沒有辦法使用的這麼彈性 <br>

### 觀察 `redis-om` 結果

觀察 `redis-om` 的結果可以發現 <br>
是將 **modulename + classname + pk** 當作 **key** <br>
如下所示：

![redis hash model](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/redis-hash-model.png)
( `HashModel` 生成的 Key 格式 )

![redis json model](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/redis-json-model.png)
( `JsonModel` 生成的 Key 格式 )

## 以 `redis-py` 和自定義 Model 實作

既然使用 `redis-om` 會有額外的問題 <br>
也須要額外處理 <br>

<br>

那不如我們就直接使用 `redis-py` 來實作 <br>
同樣也是使用 decorator 來實作 <br>

## cache decorator 設計

Cache 主要分成 3 個操作
- get
- update
- delete

並使用 Redis 內建的 `Hash` Type 來實作 <br>
- `redis_connection.hgetall( key_name )` : 回傳 `key_name` 下所有的 key-value pair ( dict )
- `redis_connection.hset( key_name , mapping )` : 將 `mapping` 中的 key-value pair 寫入 `key_name` 中 ( 可以當作新增或更新 ) 
<br>

又考慮到**複用性** ，我們將 `perfix` 和 `key` 作為參數傳入 <br>
讓能夠以 **prefix + kargs[key]** 作為 Key <br>
> 所以要被 Wrap 起來的 function 必須要有 `**kwargs` 來傳參數 <br>

`database/redis_cache.py` <br>
```python
def generic_cache_get(prefix:str,key:str,cls:object):
    '''
    prefix: namspace for redis key ( such as `user` 、`item` 、`article` )
    key: **parameter name** in caller function ( such as `user_id` 、`email` 、`item_id` )
    cls: **response schema** in caller function ( such as `UserSchema.UserRead` 、`UserSchema.UserId` 、`ItemSchema.ItemRead` )
    '''

    rc = redis.Redis(connection_pool=redis_pool)

    def inner(func):
        async def wrapper(*args, **kwargs):
            # TODO ...
        return wrapper
    return inner
```

<br>

如果有 `cache_key` 還需要檢查**目前 Cache 的結果是否有所有 Schema 包含的 Field** <br>
如果有缺少 Field 話 <br>
也需要先去 DB 中取得資料後再更新！ <br>

<br>

`database/redis_cache.py` <br>
```python
    #...
    # 在呼叫被包裝的 function 時，要以 func(key=value) 的方式傳入參數
    value_key = kwargs.get(key) 
    if not value_key:
        return await func(*args, **kwargs)
    
    # 組合成給 redis 的 key
    cache_key = f"{prefix}:{value_key}"

    # 檢查是否有 cache
    try:
        redis_result:dict = rc.hgetall(cache_key)

        # 即使有結果 還需要檢查是否有所有的 Field
        if check_has_all_keys(redis_result,cls): # cache hit !
            return cls(**redis_result) 
    except:
        pass

    sql_result = await func(*args, **kwargs) 
    if not sql_result:
        return None
    
    rc.hset(cache_key, mapping=sql_query_row_to_dict(sql_result))
    return sql_result
    
```

我們這邊直接用 exception 來判斷是否有 cache hit <br>
而不用 `redis_connect.exists` 來檢查來加速 <br>

## 使用 cache decorator

在 CRUD 中，我們只需要加上 `@generic_cache_get` 來使用 <br>
`crud/users.py` <br>
```python
# ...
    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserRead)
        async def get_user_infor_by_id(self,user_id:int ,db_session:AsyncSession) -> UserSchema.UserInfor:
            # ...

    @generic_cache_get(prefix="user",key="user_id",cls=UserSchema.UserId)
    async def get_user_id_by_id(self,user_id:int ,db_session:AsyncSession=None) -> UserSchema.UserId:
        # ...
    

    @generic_cache_get(prefix="user",key="email",cls=UserSchema.UserInDB)
    async def get_user_in_db(self,email:str , db_session:AsyncSession=None) -> UserSchema.UserInDB :
        # ...
# ...
```

要注意的是 <br>
當我們在 call 這些 CRUD function 時，要以 `func(key=value)` 的方式傳入參數 <br>

<br>

`api/users.py` <br>
```python
# ...

    # ...
    async def get_user_infor_by_id(user_id: int):
        # 這邊要以 `user_id=user_id` 的方式傳入
        user = await UserCrud.get_user_infor_by_id(user_id=user_id)
```

`api/auth.py` <br>
```python
async def login(form_data: login_form_schema):    # ...

    # 要以 `email=form_data.username` 的方式傳入
    user_in_db:UserInDB = await UserCrud.get_user_in_db(email=form_data.username)
```

## Update 與 Delete 的 Cache 操作

對於 Update 和 Delete Cache 的操作也與 Get 類似 <br>
也是先從 DB 中取得資料後以 `hset` 更新 <br>

<br>

Delete 則是直接依據 `key` 來刪除 <br>

> 這邊就不佔篇幅 <br>
> 可以直接看 [Day25 branch: database/redis_cache.py]() <br>

## Benchmark 比較結果

這邊都以 100 個 user 和隨機的合法 user_id 來測試 <br>

- 以 **5000** 個 Query 來測試 <br>
> 原本的
> ![benchmark 5000 orig](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/benchmark-5000-orig.png)


> 加上 Redis Cache 後
> ![benchmark 5000 cache](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/benchmark-5000-cache.png)

<br>

可以看到大約快了 **12 秒** ！

<br>

- 以 **50000** 個 Query 來測試 <br>
> 原本的
> ![benchmark 50000 orig](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/benchmark-50000-orig.png)


> 加上 Redis Cache 後
> ![benchmark 50000 cache](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day25/benchmark-50000-cache.png)

<br>

可以看到大約快了 **150 秒** ！

## 總結

今天我們使用 `redis-py` 來實作 Server Cache <br>
也看到以 `redis-om` 來實作的坑 <br>
最後以 Redis 內建的 `Hash` Type 來實作 <br>
包裝成可複用的 **decorator** <br>

<br>

使用 Redis 作為 Server Cache 也有看到不錯的效果 <br>
明天會接著把 **pagenation** ( `get_user_list` CRUD ) 也加入 Cache <br>

## Reference

[redis python hash operation](https://www.cnblogs.com/bigberg/p/8287948.html)

