try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create a simple async Redis client wrapper with fallback
class AsyncRedisClient:
    def __init__(self, url):
        self.cache = {}  # In-memory fallback
        if REDIS_AVAILABLE:
            try:
                self.client = redis.from_url(url, decode_responses=True)
                self.connected = True
            except Exception:
                self.client = None
                self.connected = False
        else:
            self.client = None
            self.connected = False
    
    async def ping(self):
        if self.connected:
            return self.client.ping()
        return True
    
    async def setnx(self, key, value):
        if self.connected:
            return self.client.setnx(key, value)
        else:
            if key not in self.cache:
                self.cache[key] = value
                return True
            return False
    
    async def expire(self, key, seconds):
        if self.connected:
            return self.client.expire(key, seconds)
        return True
    
    async def close(self):
        if self.connected and self.client:
            self.client.close()

redis_client = AsyncRedisClient(REDIS_URL)