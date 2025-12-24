"""Redis cache utility for Score API."""
import json
import redis
from typing import Optional, Any
from functools import wraps
import structlog

logger = structlog.get_logger()

# Redis connection (will be initialized on startup)
redis_client: Optional[redis.Redis] = None

def init_redis(host: str = "redis", port: int = 6379, db: int = 0):
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,
            socket_connect_timeout=5
        )
        # Test connection
        redis_client.ping()
        logger.info("Redis connected successfully", host=host, port=port)
    except Exception as e:
        logger.warning("Redis connection failed, cache disabled", error=str(e))
        redis_client = None

def get_cache(key: str) -> Optional[Any]:
    """Get value from cache."""
    if not redis_client:
        return None
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        logger.warning("Cache get error", key=key, error=str(e))
        return None

def set_cache(key: str, value: Any, expire: int = 3600):
    """Set value in cache with expiration (default 1 hour)."""
    if not redis_client:
        return False
    try:
        redis_client.setex(
            key,
            expire,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        logger.warning("Cache set error", key=key, error=str(e))
        return False

def delete_cache(key: str):
    """Delete key from cache."""
    if not redis_client:
        return False
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.warning("Cache delete error", key=key, error=str(e))
        return False

def cache_result(key_prefix: str, expire: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = get_cache(cache_key)
            if cached is not None:
                logger.debug("Cache hit", key=cache_key)
                return cached
            
            # Execute function and cache result
            logger.debug("Cache miss", key=cache_key)
            result = await func(*args, **kwargs)
            set_cache(cache_key, result, expire)
            return result
        return wrapper
    return decorator

