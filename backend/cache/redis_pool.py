import redis
from setting.config import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool.from_url(settings.redis_url,decode_responses=True)