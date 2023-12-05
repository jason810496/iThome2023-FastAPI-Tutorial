import os
from functools import lru_cache

class BaseSettings():
    app_name:str = "iThome2023 FastAPI Tutorial"
    author:str = "Jason Liu"

    app_mode: str = os.getenv("APP_MODE").upper()
    port:int = int(os.getenv("PORT"))
    reload:bool = os.getenv("RELOAD") 

    access_token_secret:str = os.getenv("ACCESS_TOKEN_SECRET")
    access_token_expire_minutes:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    refresh_token_secret:str = os.getenv("REFRESH_TOKEN_SECRET")
    refresh_token_expire_minutes:int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

    sentry_dsn:str = os.getenv("SENTRY_DSN")

class Settings(BaseSettings):
    db_type:str = os.getenv("DB_TYPE").upper()
    database_url: str = os.getenv("DATABASE_URL")
    redis_url:str = os.getenv("REDIS_URL")
    

class PrimaryReplicaSetting(BaseSettings):
    primary_database_url: str = os.getenv("PRIMARY_DATABASE_URL")
    replica_database_url: str = os.getenv("REPLICA_DATABASE_URL")
    redis_url:str = os.getenv("REDIS_URL") 
    


@lru_cache()
def get_settings():

    if os.getenv("APP_MODE") is 'primary-replica':
        return PrimaryReplicaSetting()

    setting_cls_dict = {
        "DEV":Settings,
        "TEST":Settings,
        "PROD":Settings,
    }

    return setting_cls_dict[os.getenv("APP_MODE").upper()]()
