import os
from functools import lru_cache

from dotenv import load_dotenv

class Settings():
    app_name:str = "iThome2023 FastAPI Tutorial"
    author:str = "Jason Liu"

    app_mode: str = os.getenv("APP_MODE")
    port:int = int(os.getenv("PORT"))
    reload:bool = os.getenv("RELOAD")
    
    db_type:str = os.getenv("DB_TYPE").upper()
    database_url: str = os.getenv(f"{db_type}_DATABASE_URL")


@lru_cache()
def get_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return Settings()
