import json
import logging
import asyncio
from fastapi import WebSocket
from redis.asyncio import Redis

from config import settings
from redis_client import get_redis_client
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        # {
        #   用户1: {ws1, ws2, ...},
        #   用户2: {ws3}
        #               }
        # set集合用于去重还能处理None值
        self.connections = dict[int, set[WebSocket]] = {}
    async def connect(self, user_id: int, ws: WebSocket):
        """连接用户"""
        await ws.accept()
        self.connections.setdefault(user_id, set()).add(ws)
        logger.info("用户 %s 上线，共 %s 条连接", user_id, len(self.connections[user_id]))
    def disconnect(self, user_id: int, ws: WebSocket):
        """断开用户"""
        conn = self.connections.pop(user_id)
        if conn is None:
            return
        conn.discard(ws)
        if len(conn) == 0:
            del self.connections[user_id]
    async def send_message(self, user_id: int, message: dict):
        conn = self.connections[user_id]
        if not conn:
            return
        for ws in list(conn):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, ws)

    async def subscribe_redis(self) -> None:
        client = await get_redis_client()
        pubsub = client.pubsub()
        pattern = f"{settings.REDIS_PREFIX}:ws:user:*"
        await pubsub.psubscribe(pattern)
        logger.info("开始订阅 Redis 频道: %s", pattern)

        async for msg in pubsub.listen():
            if msg["type"] != "pmessage":
                continue
            try:
                user_id = int(msg["channel"].split(":")[-1])
                payload = json.loads(msg["data"])
                await self.broadcast_to_user(user_id, payload)
            except Exception as e:
                logger.warning("转发 WS 消息失败: %s", e)
