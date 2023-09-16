# [Day02]  FastAPI 啟動： 環境安裝

![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day02/banner.png)


這次需要安裝的套件有
- `fastapi`
- `uvicorn`

## 環境安裝

如果要在 local 直接安裝套件，雖然可以直接使用 pip3 安裝
( 但非常**不建議**這樣做！ )
```bash
pip3 install fastapi
```

這邊想要提供一個**更好的**環境管理方式 <br>
使用 poetry 來管理環境 <br>
或是使用 venv 在虛擬環境中安裝

可以避免在開發時，全域環境中的套件版本相依性的 error ! <br>

## poetry

[`poetry`](https://python-poetry.org/) 是一個 python 的 dependency manager <br>
( 可以在[官方安裝教學](https://python-poetry.org/docs/#installation)中找到安裝方式 ) <br>
poetry 也會順邊幫我們創建一個虛擬環境 <br>

### 安裝 fastapi 和 uvicorn

1. 快速安裝
如果已經在專案目錄中 ，可以使用以下指令安裝 `fastapi` 和 `uvicorn`
```bash
poetry init -n
poetry add fastapi
poetry add uvicorn
```

2. 互動式安裝
不加上 `-n` 參數，會進入互動式安裝
```bash
poetry init
```
應該會跳出以下畫面 <br>
接者在 `package name` 輸入 `fastapi` 和 `uvicorn` <br>

![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day02/poetry-interative.png)

### 啟用虛擬環境

如果要進入 poetry 的虛擬環境 <br>
需使用 `poetry shell` 指令 
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day02/active.png)

或是使用 `poetry run` 指令 <br>
以虛擬環境執行 python 檔案 ( 但不會進入虛擬環境 ) 

```bash
poetry run python3 main.py
```

## venv

如果不想使用 poetry ，可以使用 python 內建的 venv <br>

### 創建虛擬環境

```bash
python3 -m venv venv
```

會在當前目錄下創建一個 `venv` 資料夾 <br>
一般會將 `venv` 加入 `.gitignore` 中 <br>

### 啟用虛擬環境

如果要離開虛擬環境，可以使用 `deactivate` 指令 <br>
```bash
source venv/bin/activate
```

![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day02/venv.png)


### 安裝 fastapi 和 uvicorn

```bash
pip3 install fastapi
pip3 install uvicorn
```

## 什麼是 Uvicorn ?

[`uvicorn`](https://www.uvicorn.org/) 是一個 ASGI server <br> 
( ASGI 是一個 python 的 async server gateway interface ) <br>
FastAPI 也是使用 uvicorn 來啟動 server <br>

安裝完 `uvicorn` 之後，可以使用以下指令來啟動 server
```bash
uvicorn <path_to_your_app>:<app_object_name> --host <host> --port <port>
```

如果有一下的檔案結構
```
.
└── main.py
```
而 `main.py` 中有一個 `my_app` instance
```python
from fastapi import FastAPI

my_app = FastAPI()

@my_app.get("/")
def root():
    return {"message": "Hello World"}
```
並且要跑在 `0.0.0.0` 的 `8000` port 上 <br>
可以使用以下指令來啟動 server
```bash
uvicorn main:my_app --host 0.0.0.0 --port 8000
# 如果已經有在虛擬環境中

poetry run uvicorn main:my_app --host 0.0.0.0 --port 8000
# 如果有使用 poetry 但沒有進入虛擬環境
```

## Summary

這次的環境安裝，可以使用 `poetry` 或是 `venv` <br>

- `poetry`
    - 使用 `poetry shell` 進入虛擬環境
    - 一搬會將 `poetry.lock` 加入 `.gitignore` 中
- `venv`
    - 使用 `source venv/bin/activate` 進入虛擬環境
    - 一搬會將整個 `venv` 目錄加入 `.gitignore` 中

##### Reference

[Install Poetry](https://python-poetry.org/docs/#installation) <br>
[Poetry tutorial](https://python-poetry.org/docs/basic-usage/) <br>
[Python venv](https://docs.python.org/3/library/venv.html) <br>
[Python venv tutorial](https://docs.python.org/3/tutorial/venv.html) <br>


