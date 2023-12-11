import os
from functools import lru_cache

class BaseSettings():
    def __init__(self) -> None:
        self.app_name:str = "iThome2023 FastAPI Tutorial"
        self.author:str = "Jason Liu"

        self.app_mode: str = os.getenv("APP_MODE").upper()
        self.port:int = int(os.getenv("PORT"))
        self.reload:bool = os.getenv("RELOAD") 

        self.access_token_secret:str = os.getenv("ACCESS_TOKEN_SECRET")
        self.access_token_expire_minutes:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

        self.refresh_token_secret:str = os.getenv("REFRESH_TOKEN_SECRET")
        self.refresh_token_expire_minutes:int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))

        self.sentry_dsn:str = os.getenv("SENTRY_DSN")

class Settings(BaseSettings):
    def __init__(self) -> None:
        self.db_type:str = os.getenv("DB_TYPE").upper()
        self.database_url: str = os.getenv("DATABASE_URL")
        self.redis_url:str = os.getenv("REDIS_URL")
    

class PrimaryReplicaSetting(BaseSettings):
    def __init__(self) -> None:
        self.primary_database_url: str = os.getenv("PRIMARY_DATABASE_URL")
        self.replica_database_url: str = os.getenv("REPLICA_DATABASE_URL")
        self.redis_url:str = os.getenv("REDIS_URL") 

class MessageQueueSettings():
    def __init__(self) -> None:
        self.upload_path:str = os.getenv("UPLOAD_PATH")
        self.tmp_path:str = os.getenv("TMP_PATH")
        self.redis_url:str = os.getenv("REDIS_URL")
        self.queue_name:str = os.getenv("QUEUE_NAME")
    


@lru_cache()
def get_settings():

    if os.getenv("APP_MODE") == 'primary-replica':
        return PrimaryReplicaSetting()
    
    if os.getenv("APP_MODE") == 'MESSAGE-QUEUE':
        return MessageQueueSettings()

    setting_cls_dict = {
        "DEV":Settings,
        "TEST":Settings,
        "PROD":Settings,
    }

    return setting_cls_dict[os.getenv("APP_MODE").upper()]()
