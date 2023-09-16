from fastapi import FastAPI

from setting.config import get_settings

app = FastAPI()

@app.get("/")
def hello_world():
    return "Hello World"

@app.get("/infor")
def get_infor():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode ,
        "port": settings.port,
        "database_url": settings.database_url,
        "reload": settings.reload
    }

@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    return {"user_id": user_id, "query": qry }