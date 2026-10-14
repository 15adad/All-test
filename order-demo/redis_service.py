import json
import logging
import redis.asyncio
from redis import RedisError

from app.config import settings

"""业务封装缓存+限流"""
logger = logging.getLogger(__name__)


class RedisService:
    # lua脚本用于限流，保证原子性，防止并发问题
    _RATE_LIMIT_LUA = """
        local current = redis.call('INCR', KEYS[1])
        if current == 1 then
            redis.call('EXPIRE', KEYS[1], ARGV[1])
        end
        return current
        """

    def __init__(self, client: redis.Redis | None = None):
        self.client = client

    # 自动加前缀
    def _key(self, key: str):
        return f"{settings.REDIS_PREFIX}_{key}"

    # 封装get方法
    async def get_json(self, key: str):
        if self.client is None:
            logger.warning("redis client is None")
            return None
        try:
            # 此处调用的是redis的get方法
            result = await self.client.get(self._key(key))
            return json.loads(result) if result else None
        except RedisError:
            logger.warning("redis client not initialized")
            return None

    async def set_json(self, key: str, value: str, ttl: int = 60):
        if self.client is None:
            logger.warning("redis client is None")
            return None
        try:
            await self.client.set(self._key(key), json.dumps(value), ex=ttl)
        except RedisError:
            logger.warning("%s is not exist", key)

    async def publish(self, channel: str, message: dict) -> None:
        """发布到 Redis 频道（用于跨进程通知 WebSocket）"""
        if self.client is None:
            return
        try:
            await self.client.publish(
                self._key(channel),
                json.dumps(message, ensure_ascii=False),
            )
        except RedisError:
            logger.warning("Redis publish 失败: %s", channel)

    async def limit_rate(self, key: str, limit: int, window: int = 60) -> bool:
        """原子限流：返回 True 放行，False 拒绝"""
        if self.client is None:
            return True
        try:
            count = await self.client.eval(self._RATE_LIMIT_LUA,1,self._key(f"rl_{key}"),window)
            return int(count)<=limit
        except RedisError:
            logger.warning("Redis 限流失败，放行: %s", key)
            return True
