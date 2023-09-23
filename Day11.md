# [Day11] SQLAlchemy Model

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day11 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day11)** <br>

## 回顧

在 [Day10](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10) 中，我們已經完成了 SQLAlchemy 的基本設定 <br>
能夠以 argument 的方式選擇要使用的資料庫，並且透過通用的 SQLAlchemy 來連接資料庫 <br>
接下來我們要來建立關鍵的  **Model** <br>

## Model

**Model** 是 SQLAlchemy 中定義 **table** 的方式 <br>
可以透過定義 Model 來建立實際在 databases 中的 table ！ <br>
> 確切來說，是以一個 `object` 來對應一個 `table` <br>
> 也就是 ORM (Object Relational Mapping) 的概念 <br>

<br>

在 SQLAlchemy 2.x 是以 `DeclarativeBase`  來建立 Model [ORM  Declarative Mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping)<br>
( 在 SQLAlchemy 1.x 則是以 `declarative_base` 來建立 Model [SQLAlchemy 1.x ORM Tutorial - Declarative](https://docs.sqlalchemy.org/en/14/orm/tutorial.html#declare-a-mapping) ) <br>
> 因為 SQLAlchemy 2.x 是大改版，在 1.x 的 ORM 與 2.x 的 ORM 有些許不同 <br>
> 如 `Column` 改為 `mapped_column` <br>
> 詳細資訊可以看 [What’s New in SQLAlchemy 2.0?](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing) 來將 1.x 的 ORM 轉換為 2.x <br>


### 建立 Model

```bash
mkdir models
touch models/{base,users,item}.py
```
<br>

在 SQLAlchemy 2 中，我們的 Model 都需要繼承 `DeclarativeBase` <br>
所以先定義一個專門被繼承的通用 `Base` class <br>
和提供通用 `type` 的 `BaseType` <br>
[SQLalchemy: mapping multiple type configurations to python types](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapping-multiple-type-configurations-to-python-types)
`models/base.py`

```python
# ...
class Base(DeclarativeBase):
    pass

class BaseType:
    int_primary_key = Annotated[int, mapped_column(Integer, primary_key=True, unique=True, autoincrement=True)]
    str_30 = Annotated[str, mapped_column(String(30))]
    str_50 = Annotated[str, mapped_column(String(50))]
    optional_str_50 = Annotated[Optional[str], mapped_column(String(50), nullable=True)]
    optional_str_100 = Annotated[Optional[str], mapped_column(String(100), nullable=True)]
    update_time = Annotated[datetime, mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)]
```

<br>

接著我們要建立 `User` 和 `Item` 的  Model <br>
依據之前 **Schema** 來建立 Database 中的 Table <br>
`models/users.py`
```python
class User(Base):
    __tablename__ = "User"
    id:Mapped[BaseType.int_primary_key]
    password:Mapped[BaseType.str_50]
    name:Mapped[BaseType.str_30]
    age:Mapped[int]
    avatar:Mapped[BaseType.optional_str_100]
    birthday:Mapped[date] = mapped_column(Date)
    email:Mapped[BaseType.str_50]
    create_time:Mapped[BaseType.update_time]

    items:Mapped[list["Item"]] \
        = relationship("Item", 
            back_populates="user", 
            cascade="all, delete-orphan", 
            lazy="select", 
            order_by="Item.name"
        )
```
而因為 `User` 與 `Item` 是**一對多**的關係 <br>
所以我們需要在 `User` 中使用 `relationship` 定義 `items` 來表示這個關係 <br>
> 並加上 `back_populates` 來表示 `Item` 中的 `user` <br>
> 而 `cascade="all, delete-orphan"` 則是表示當 `User` 被刪除時，這個 user 的所有 items 也會被刪除 <br>
> `lazy="select"` 則是表示當我們有使用到 `user.items` 時，才會去資料庫中取得 `items` <br>
> 詳細資訊可以看 [SQLAlchemy: relationship](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#relationship-patterns) <br>

<br>

再定義 `User` 的 constructor <br>
而 **`password` 應該要被 hash 過後才存入資料庫** <br>
這邊只是做 demo ， 在後幾天的 **`OAuth2 實例：密碼驗證`** 才會演示如何安全的做 password hashing <br>

`models/users.py`
```python
    def __init__(self, password:str, name:str, age:int, avatar:Optional[str], birthday:date, email:str) -> None:
        # password should be hashed before store in database , here is just for demo
        self.password = hashlib.md5(password.encode()+b'secret').hexdigest()
        self.name = name
        self.age = age
        self.avatar = avatar
        self.birthday = birthday
        self.email = email
```

<br>

最後加上 `__repr__` 來定義 `User` 的轉為 `str` 時的格式 <br>
會比較好 debug 與測試<br>
`models/users.py`
```python
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, age={self.age}, email={self.email})>"
```

### 建立 Item Model

接著我們來建立 `Item` 的 Model <br>

`models/item.py`
```python
class Item(Base):
    __tablename__ = "Item"
    id:Mapped[BaseType.int_primary_key]
    name:Mapped[BaseType.str_50]
    price:Mapped[float]
    brand:Mapped[BaseType.str_30]
    description:Mapped[BaseType.optional_str_100]
    create_time:Mapped[BaseType.update_time]
    last_login:Mapped[BaseType.update_time]

    user_id:Mapped[int] = mapped_column(ForeignKey("User.id", ondelete="cascade"))
    user:Mapped["User"] = relationship("User", back_populates="items")
```
要注意的是，因為 `Item` 與 `User` 是**多對一**的關係 <br>
所以我們需要在 `Item` 中使用 `ForeignKey` 來定義 `user_id` <br>
> 並加上 `ondelete="cascade"` 來表示當 `User` 被刪除時，這個 user 的所有 items 也會被刪除 <br>

<br>

而 `Item` 的 `__init__` 與 `__repr__` 基本上與 `User` 一樣 <br>
可以直接參照  [FastAPI Tutorial : Day11 branch `/models/item.py`](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10/backend/models/item.py) <br>


## create database

而我們可以透過 `Base.metadata.create_all` 來建立資料庫中的 table <br>
在 `database/generic.py` 中新增 `create_all` <br>
```python
# ....

def init_db():
    Base.metadata.create_all(bind=engine, tables=[User.__table__, Item.__table__])
```

<br>

而在 `main.py` 中，我們可以透過 `startup` event 來初始化資料庫 <br>
```python
from database.generic import init_db

# ....

@app.on_event("startup")
def startup():
    init_db()
```


## Create tables

接著直接跑起 FastAPI 來看看資料庫中是否有建立 table <br>
先以預設的 PostgreSQL 來看看 <br>
```bash
poetry run python3 run.py
```

![postgresql create](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/postgresql-create.png)

可以看到 FastAPI 的 log 中有顯示 `CREATE TABLE` <br>
並且是依據我們 Model 的定義來建立出 table 的<br>

<br>

接著我們再來看看 MySQL <br>
```bash
poetry run python3 run.py --db mysql
```

![mysql create](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/mysql-create.png)


## 測試基本 CRUD

### 新增測試 Router 

我們在加上一個 `/test/create` 和 `/test/read` 來測試我們的資料庫是否正常運作 <br>

在 `routers/infor.py` 中新增 `test/create` <br>
```python
from database.generic import get_db
from models.user import User
from models.item import Item

# ...

@router.get("/test/create")
def test():
    db_session = get_db()
    result = {
        "user": None,
        "item": None,
    }
    try :
        test_user = User("123456", "test0", 0, None, "2000-01-01", "123@email.com")
        db_session.add(test_user)
        db_session.commit()
        result["user"] = test_user

        test_item = Item("item0",99.9, "brand0", "test0", test_user.id)
        db_session.add(test_item)
        db_session.commit()
        result["user"] = test_user
        result["item"] = test_item

    except Exception as e:
        print(e)

    return result
```

`get_db` 會自動建立一個 `SessionLocal` 來連接資料庫 <br>
而 `db_session.add` 則是將 `test_user` 和 `test_item` 加入 `SessionLocal` <br>
又因為我們在 `database/generic.py` 中有設定 `autocommit=False` <br>
所以 `db_session.commit()` 才會將 `test_user` 和 `test_item` 寫入資料庫 <br>

<br>


在 `routers/infor.py` 中新增 `test/read` <br>
```python
@router.get("/test/read")
def test():
    db_session = get_db()
    result = {
        "user": None,
        "item": None,
        "user.items": None,
    }
    try :

        test_user = User("123456", "test0", 0, None, "2000-01-01", "123@email.com")
        db_session.add(test_user)
        db_session.commit()
        result["user"] = test_user

        test_item = Item("item0",99.9, "brand0", "test0", test_user.id)
        db_session.add(test_item)
        db_session.commit()
        result["item"] = test_item

    except Exception as e:
        print(e)

    return result
```

### 以 Swagger 測試

接著我們可以透過 Swagger 打剛剛建立的 test API <br>
來測試我們的資料庫是否正常運作 <br>

Create : 
![test create](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/test-create.png)
在看 Log 時，可以看到被 ORM 轉換的 `INSERT INTO`  SQL 語法 <br>
![test create log](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/test-create-log.png)

Read :
![test read](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/test-read.png)
在看 Log 時，可以看到被 ORM 轉換的 `SELECT`  SQL 語法 <br>
![test read log](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day11/test-read-log.png)
可以注意的是，當我們在使用到 `user.items` 時，才會去資料庫中取得 `items` <br>
而如果將 `lazy="select"` 改為 `lazy="joined"` 時，則會在一開始就將 `items` 一起取得 <br>
在沒有使用到 `user.items` 的情況，則會增加一個 `SELECT` 的成本 <br>

## 當前目錄架構
在設定完 SQLAlchemy ORM 和成功連接資料庫後 <br>
目前的目錄架構如下 <br>
```bash
.
├── api
│   ├── infor.py
│   ├── items.py
│   └── users.py
├── database
│   ├── fake_db.py
│   └── generic.py
├── main.py
├── models
│   ├── base.py
│   ├── item.py
│   └── user.py
├── run.py
├── schemas
│   ├── items.py
│   └── users.py
└── setting
    ├── .env.dev
    ├── .env.prod
    ├── .env.test
    └── config.py

5 directories, 16 files
```


## 總結

- 透過 `DeclarativeBase` 來建立 Model
- 透過 `relationship` 來定義關係
- 透過 `Base.metadata.create_all` 來建立資料庫中的 table
- 透過 `SessionLocal` 來連接資料庫

明天才會比較詳細講 SQLAlchemy ORM 的 CRUD <br>
但因為 SQLAlchemy 2.x 本身就可以再講一篇鐵人賽了 QQ <br>
所以今天只主要以常見用法來做說明！ <br>


#### reference: 

[What’s New in SQLAlchemy 2.0?](https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#whatsnew-20-orm-declarative-typing)
[SQLAlchemy: relationship - one to many](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many)
[SQLAlchemy: relationship configuration](https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params)
[SQLAlchemy: declarative-mapping](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-declarative-mapping)
[SQLalchemy: mapping multiple type configurations to python types](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html#mapping-multiple-type-configurations-to-python-types)