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
    run_mode:str = os.getenv("RUN_MODE").upper()
    database_url: str = os.getenv(f"{run_mode}_{db_type}_DATABASE_URL")
    redis_url:str = os.getenv("REDIS_URL") 

    access_token_secret:str = os.getenv("ACCESS_TOKEN_SECRET")
    access_token_expire_minutes:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    refresh_token_secret:str = os.getenv("REFRESH_TOKEN_SECRET")
    refresh_token_expire_minutes:int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))


class PrimaryReplicaSetting():
    primary_database_url: str = os.getenv("ASYNC_PRIMARY_DATABASE_URL")
    replica_database_url: str = os.getenv("ASYNC_REPLICA_DATABASE_URL")
    redis_url:str = os.getenv("REDIS_URL") 

    access_token_secret:str = os.getenv("ACCESS_TOKEN_SECRET")
    access_token_expire_minutes:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    refresh_token_secret:str = os.getenv("REFRESH_TOKEN_SECRET")
    refresh_token_expire_minutes:int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
    


@lru_cache()
def get_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return Settings()


@lru_cache()
def get_primary_replica_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return PrimaryReplicaSetting()