# iThome 2023

FastAPI RestfulAPI 前後端分離的支柱

-  [Day01](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day01)  FastAPI 推坑與框架的朋友們
    - FastAPI 優點
    - django / flask / FastAPI 大比拼
    - FastAPI 之於 其他 python 後端框架架，就像 typescript 之於 javascript(指的是語法層面)
    - 在各個 function 傳遞之間都會定義好 schema ， 更容易 Debus ( Schema 設定好)
- [Day02](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day02)  FastAPI 起步： 環境安裝
    - venv 
    - poetry 
    - uvicorn
- [Day03](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day03) FastAPI 設定與 Uvicorn 包裝
    - CROS
    - `app.py` 包裝
- [Day04](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day04) FastAPI 基礎架構
    - app instance
    - router
    - swagger docs 
    - typing
- [Day05](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day05) Schema & Pydanic
    - Pydanic
    - FastAPI 中的 Schema
- [Day06] Response model
- [Day07] 再談 Python Typing 與 Schema 常見錯誤
    - HTTPException
    - 可能為 None -> Optional
    - 可以是多個 type -> Union
- [Day08] 為 Swagger API endpoint 加上更多資訊
    - Response description
    - Summary
    - Example
    - Field
    - deprecated
    - Status code
- [Day09] Dpendency 萬用刀 & 常見錯誤
    - common query params
    - common header
    - 要是 callable
    - 只能在 router 的地方使用 Depends
    - 如果在其他 utils.py 或 model.py 使用會報錯
- [Day10] 依據項目切分 Router
- [Day11] 連接 DB
- [Day12] Model
- [Day13] 使用 SQLalchemy
- [Day14] Schema 與 Model 差別
- [Day15] 架構優化：將 CRUD 與 api endpoint 分離
- [Day16] 架構優化：非同步存取 DB
- [Day17] 架構優化：透過 Depends 注入非同步 DB Session 到 CRUD
- [Day18] OAuth2 實例：OAuth2 Login / Refresh JWT 機制
    - 分為三個 router : 
        - /auth
        - /user
        - /me ( protected router)
            - birthday
            - country
            - avatar
            - money
            - address
- [Day19] OAuth2 實例：內建 OAuth2_schema
- [Day20] OAuth2 實例：密碼驗證
- [Day21] OAuth2 實例： JWT 驗證
- [Day22] OAuth2 實例：需要 Authorize 的 router
    - 將 OAuth2_schema 設為 Depends
- [Day23] OAuth2 實例：User api & CRUD
- [Day24] OAuth2 實例：Me api & CRUD
- [Day25] 測試：pytest 入門與安裝
- [Day26] 測試：pytest CRUD 與驗證
- [Day27] 部署：使用 docker-compose 部署

- [DayXX] 延伸功能：使用 redis 作為 server cache (設定)
- [DayXX] 延伸功能：在 CRUD 查詢加上 cache
- [DayXX] 延伸功能：使用 decorator 重構 redis 架構
- [DayXX] 延伸功能：專案細節調整與部署

- [Day30] 總結：


    