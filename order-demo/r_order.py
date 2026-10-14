from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config import settings
from redis_service import RedisService
from redis_client import get_redis_client
from mq import publish_order_event
router = APIRouter()


class CreateOrderRequest(BaseModel):
    user_id: int


async def get_redis_service() -> RedisService:
    return RedisService(await get_redis_client())


@router.post("/orders")
async def create_order(
        req: CreateOrderRequest,
        redis: RedisService = Depends(get_redis_service),
):
    # 限流
    is_limit = await redis.limit_rate(f"order:{req.user_id}", 5, settings.ORDER_CACHE_TTL)
    if is_limit == False:
        raise HTTPException(
            status_code=429,
            detail="下单太频繁，请稍后再试",
            headers={"Retry-After": "60"},
        )
    # 2. 写库（同步，很快） TODO待实现
    order = create_order(req.user_id)
    # 3. 发 MQ（异步，不阻塞返回）
    await publish_order_event(order["order_no"], req.user_id)
    # 4. 秒返回
    return {"order_no": order["order_no"], "status": "PENDING"}
@router.get("/orders/{order_no}")
async def get_order_detail(
    order_no: str,
    redis: RedisService = Depends(get_redis_service),
):
    # 1. 从缓存中读取订单详情
    cache = await redis.get(f"order:{order_no}")
    if cache is None:
        # 读数据库
    return {**cache}

