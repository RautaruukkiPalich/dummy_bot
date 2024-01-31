from config import REDIS_HOST, REDIS_PORT
import redis.asyncio as redis


r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
)
