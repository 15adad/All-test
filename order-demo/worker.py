"""Worker 业务逻辑：驱动订单状态机 + 缓存 + 推送。"""
import asyncio
import logging
from redis_service import RedisService
from redis_client import get_redis_client
from mq import get_connection, start_consumer
from config import settings
logger = logging.getLogger(__name__)

FLOW = [
    (OrderStatus.PAID, 1),
    (OrderStatus.SHIPPED, 2),
    (OrderStatus.DONE, 3),
]


# 1.建立MQ连接 2.声明队列 3.进入消费循环等待生产者的消息 4.收到消息调用业务函数处理 5.确认ack告诉MQ处理结果
async def process_order_event(body: dict) -> None:
    await start_consumer(body)
    order_no = body.get("order_no")
    user_id = body.get("user_id")
    if not order_no or user_id is None:
        logger.warning("消息格式错误: %s", body)
        return
    # 数据库查询订单是否存在
    order = get_order(order_no)
    if order is None:
        logger.warning("订单不存在: %s", order_no)
        return
    # 拿到封装好的redis业务封装的client
    redis = RedisService(await get_redis_client())


    for new_status, step in FLOW:
        # 幂等：跳过已走过的步骤
        if step <= order["step"]:
            continue

        await asyncio.sleep(2)  # 模拟耗时业务
        update_order(order_no, new_status, step)

        # 1. 刷缓存
        await redis.set_json(
            f"order:{order_no}",
            {"order_no": order_no, "status": new_status, "step": step},
            ttl=settings.ORDER_CACHE_TTL,
        )

        # 2. 通过 Redis Pub/Sub 通知 API 进程，让 WebSocket 推送
        await redis.publish(
            f"ws:user:{user_id}",
            {
                "type": "order_update",
                "order_no": order_no,
                "status": new_status,
                "step": step,
            },
        )
        logger.info("[worker] %s → %s (step=%s)", order_no, new_status, step)
