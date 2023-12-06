## [[Day30]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day30) FastAPI 系列：山重水複疑無路，柳暗花明又一村


## 來不及在 iThome 鐵人賽關版前寫完的文章

都會放放在 [Github Repo](https://github.com/jason810496/iThome2023-FastAPI-Tutorial) 上，有興趣的可以自行閱讀 ! <br>
- [[Day31]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day31) : Event Driven 初探(1) 以 Redis 作為 Message Queue
- [[Day32]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day32) : Event Driven 初探(2) 以 Celery + Redis 作為可監控式 Message Broker
- [[Day33]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day32) 以 Redis 實作 Rate Limit Middleware

## 回顧

在 30 天的鐵人賽，我們完成了以下的內容 <br>
### 基礎功能
- FastAPI 基本用法 : 以 FastAPI 來實作基本 RESTful API
- Databse Injections : 以 SQLAlchemy 作為 ORM 來操作資料庫
- 以 Pytest 撰寫 Unit Test 和 Benchmark
- 以 Docker + Docker Compose 來部署專案

### 架構實作
- OAuth2 + JWT 實作 : 以 OAuth2 + JWT 來實作登入機制
- 以 Redis 作為 Server Side Cache : 實作 Key-Value Cache 和 Pagenation Cache 
- 實作 Primary Replica 架構 : 以 Read-Write Splitting 和 Read-Only Replica 來提升 Query 效能
- 實作 Event Driven 架構 : 以 Celery + Redis 作為 Message Broker 來實作非同步任務
- 實作 Rate Limit Middleware : 以 Redis 作為 Rate Limit 的資料儲存

<br>

**在 Day01 ~ Day09 : 介紹 FastAPI 的基本用法** <br>
- [[Day01]  FastAPI 推坑與框架的朋友們](https://ithelp.ithome.com.tw/articles/10320028)
- [[Day02] FastAPI 啟動： 環境安裝](https://ithelp.ithome.com.tw/articles/10320376)
- [[Day03] FastAPI 設定與 Uvicorn 包裝](https://ithelp.ithome.com.tw/articles/10320570)
- [[Day04] FastAPI 基礎架構](https://ithelp.ithome.com.tw/articles/10322582)
- [[Day05] FastAPI : Schema & Pydantic](https://ithelp.ithome.com.tw/articles/10322585)
- [[Dat06] FastAPI : Response model](https://ithelp.ithome.com.tw/articles/10324121)
- [[Day07] 再談 Python Typing 與 Schema 常見錯誤](https://ithelp.ithome.com.tw/articles/10324964)
- [[Day08] 為 Swagger (OpenAPI) 加上更多資訊](https://ithelp.ithome.com.tw/articles/10325684)
- [[Day09]  架構優化：依據項目切分 Router](https://ithelp.ithome.com.tw/articles/10326343)

**在 Day10 ~ Day16 : 在 FastAPI 中使用 SQLAlchemy 和 Depends injection** <br>
- [[Day10] 連接 Database](https://ithelp.ithome.com.tw/articles/10326759)
- [[Day11] SQLAlchemy Model](https://ithelp.ithome.com.tw/articles/10328525)
- [[Day12] 使用 SQLalchemy](https://ithelp.ithome.com.tw/articles/10329028)
- [[Day13] 架構優化： Depends 萬用刀 & 常見錯誤](https://ithelp.ithome.com.tw/articles/10329960)
- [[Day14] 架構優化：將 CRUD 與 API endpoint 分離](https://ithelp.ithome.com.tw/articles/10331002)
- [[Day15] 架構優化：非同步存取 DB](https://ithelp.ithome.com.tw/articles/10331531)
- [[Day16] 架構優化：非同步存取 DB （2）](https://ithelp.ithome.com.tw/articles/10332377)

**在 Day17 ~ Day20 : 實作 OAuth2 + JWT 登入機制** <br>
- [[Day17] OAuth2 實例： 密碼驗證](https://ithelp.ithome.com.tw/articles/10333002)
- [[Day18] OAuth2 實例： OAuth2 Schema & JWT](https://ithelp.ithome.com.tw/articles/10333835)
- [[Day19] OAuth2 實例：Authorize Dependency 、 權限管理](https://ithelp.ithome.com.tw/articles/10333926)
- [[Day20] OAuth2 實例：實作總結](https://ithelp.ithome.com.tw/articles/10335041)

**在 Day21 ~ Day23 : 以 Pytest 來撰寫 Unit Test 和 Docker Compose 來部署專案** <br>
- [[Day21] Pytest 入門與安裝](https://ithelp.ithome.com.tw/articles/10335690)
- [[Day22] 測試： Pytest `paramaterize` 與功能驗證](https://ithelp.ithome.com.tw/articles/10336272)
- [[Day23] 部署： 透過 Docker Compose 部署 FastAPI + PostgreSQL + MySQL](https://ithelp.ithome.com.tw/articles/10336829)

**在 Day24 ~ Day26 : 以 Redis 實作 Server Side Cache** <br>
- [[Day24] 架構優化 : Redis Cache , `redis-py` 架構初探](https://ithelp.ithome.com.tw/articles/10337357)
- [[Day25] 架構優化 : Redis 實作 Server Cache](https://ithelp.ithome.com.tw/articles/10337853)
- [[Day26] 架構優化 : Redis Pagenation Cache 實作](https://ithelp.ithome.com.tw/articles/10338413)

**在 Day27 ~ Day29 : 實作 Primary Replica 架構** <br>
- [[Day27]  FastAPI : Primary Replica 架構實作](https://ithelp.ithome.com.tw/articles/10338649)
- [[Day28] FastAPI : Primary Replica 架構實作 (2)](https://ithelp.ithome.com.tw/articles/10339203)
- [[Day29] FastAPI : Refactoring & CROS 設定](https://ithelp.ithome.com.tw/articles/10339634)
- [[Day30] FastAPI 系列：山重水複疑無路，柳暗花明又一村](https://ithelp.ithome.com.tw/articles/10340054)

**在 Day31 ~ Day33 : Event Drive 與 Rate Limit 實作** <br>
> 來不及在 iThome 鐵人賽關版前寫完的文章 <br>
> 都會放放在 [Github Repo](https://github.com/jason810496/iThome2023-FastAPI-Tutorial) 上，有興趣的可以自行閱讀 ! <br>
- [[Day31]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day31) : Event Driven 初探(1) 以 Redis 作為 Message Queue
- [[Day32]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day32) : Event Driven 初探(2) 以 Celery + Redis 作為可監控式 Message Broker
- [[Day33]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day33) 以 Redis 實作 Rate Limit Middleware


## 總結 

原本是 10/16 就會結束的鐵人賽 <br>
其實到今天 ( 12/06 ) 才正式寫完 TAT <br>

<br>

在開賽前，我其實只有囤不到 10 篇的文章 <br>
接下來都是盡可能一天生一篇 <br>
> 但是每篇包含 code 大概都落在 3000~5000 字 <br>
> 還有在新功能實作時，多少會遇到一些 bugs <br>
> 後期的文章都只能拿以前的文章先貼上去 <br>

<br>

還有在最後 5 篇文章時，想不太到也寫什麼 ( 之前規劃的內容都寫完了 ) <br>
也花了快一兩週來看其他文章、學新技術、找主題 <br>

<br>

在實作也遇到蠻多出乎意料的問題 <br>
- 在處理 async genrator 時：發現需要透過 `asynccontextmanager` 才能正確的 yield 出 `AsyncSession`
- 以 Redis 實作 Pagenaion Cache 時：發現後端再處理資料合併時效率太低，用其他寫法才達到預期的效果
- 實作 Primary Replica 架構時：發現以 `random.choice` 來選擇 Replica 會倒致效率低落，改用以 bitwise 實現 `round-robin` 才達到預期的效果

<br>

像是在處理 Pagenaion Cache 和 Primary Replica 架構問題時 <br>
都分別花 3 天到 1 週才通靈出關鍵點 <br>


<br>

在這兩個月的時間 <br>
除了正式完成 iThome 鐵人賽 <br>
也在 10 月打 [**NCPC 決賽**](https://ncpc.ntnu.edu.tw/)、[**ICPC 桃園站**](https://icpc.global/regionals/finder/Taipei) 和 [**ITSA 決賽**](https://www.itsa.org.tw/itsacontest/2023/register/index.php) <br>
11 月 在 [**MOPCON 講議程**](https://mopcon.org/2023/schedule/)、參加 [**臺北程式節黑客松**](https://codefest.taipei/) 和 **聽 Coldplay演唱會** <br>
是個非常充實的兩個月！<br>


## About Me

我是劉哲佑 <br>
目前就讀成大資工大二 <br>
目前往 Fullstack 偏 Backend + DevOps 的方向發展 ! <br>


[![Facebook](https://img.shields.io/static/v1?style=for-the-badge&message=Facebook&color=1877F2&logo=Facebook&logoColor=FFFFFF&label=)](https://www.facebook.com/JasonBigCow)
[![LinkedIn](https://img.shields.io/static/v1?style=for-the-badge&message=LinkedIn&color=0A66C2&logo=LinkedIn&logoColor=FFFFFF&label=)](https://www.linkedin.com/in/zhe-you-liu/)
[![Gmail](https://img.shields.io/static/v1?style=for-the-badge&message=Gmail&color=EA4335&logo=Gmail&logoColor=FFFFFF&label=)](mailto:f74116720@gs.ncku.edu.tw)