from __future__ import annotations
from typing import Any, Callable
import asyncio, time
from ..utils.config import settings

try:
    import redis.asyncio as aioredis
except Exception:
    aioredis = None  # type: ignore

class Cache:
    def __init__(self):
        self._redis = None
        self._local = {}

    async def init(self):
        if aioredis and settings.REDIS_URL:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get_or_set(self, key: str, ttl: int, loader: Callable[[], Any]):
        if self._redis:
            val = await self._redis.get(key)
            if val:
                return val
            val = await loader()
            await self._redis.setex(key, ttl, val)
            return val
        else:
            if key in self._local:
                v, exp = self._local[key]
                if time.time() < exp:
                    return v
            v = await loader() if asyncio.iscoroutinefunction(loader) else loader()
            self._local[key] = (v, time.time() + ttl)
            return v

cache = Cache()
