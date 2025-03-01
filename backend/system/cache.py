import redis.asyncio as redis
from fastapi import Request
class Cache:
    def __init__(self, redis_url: str = "redis://localhost:6379", pool_size: int = 5):
        self.pool = redis.ConnectionPool.from_url(redis_url, max_connections=pool_size)
        self.client:redis.Redis = redis.Redis(connection_pool=self.pool, decode_responses=True)  # Decode to string

    async def close(self):
        """Close Redis connection."""
        print("closing")
        await self.client.close()

def get_cache(request:Request) ->redis.Redis:
    return request.app.state.cache