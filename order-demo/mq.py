import json
import logging

import aio_pika

from app.config import settings

logger = logging.getLogger(__name__)

_connection: aio_pika.abc.AbstractRobustConnection | None = None


async def get_connection() -> aio_pika.abc.AbstractRobustConnection:
    global _connection
    if _connection is None:
        _connection = await aio_pika.connect(settings.RABBITMQ_URL)
    return _connection

async def publish_order_event(order_no: str, user_id: int) -> bool:
    """下单成功后发消息；失败只记日志，绝不抛（旁路原则）"""
    try:
        connection = await get_connection()
        channel = await connection.channel()
        try:
            await channel.declare_queue(settings.ORDER_QUEUE, durable=True, auto_delete=False, exclusive=False)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps({"order_no": order_no, "user_id": user_id}),
                    delivery_mode=2,
                    content_type="application/json"
                ),
                routing_key=settings.ORDER_QUEUE
            )
        finally:
            await channel.close()
            logger.info("事件已发布")
            return True
    except Exception:
        logger.warning("发布事件失败")
        return False

async def start_consumer(on_message) -> None:
    """
    启动消费者：从队列取消息，调用 on_message。
    在 main.py 的 lifespan 里用 asyncio.create_task 启动。
    """
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)   # 一次处理一条，公平分发
    queue = await channel.declare_queue(settings.ORDER_QUEUE, durable=True)

    logger.info("MQ 消费者已启动，等待消息...")

    async with queue.iterator() as it:
        async for message in it:
            async with message.process():   # 正常退出自动 ack，异常自动 nack
                body = json.loads(message.body)
                await on_message(body)
