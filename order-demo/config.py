from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://192:6379/0" # 虚拟机里查看ip，后续填
    REDIS_PREFIX = "demo"
    RABBITMQ_URL = "amqp://oc:oc123@:5672/" # 虚拟机里查看ip，后续填
    ORDER_QUEUE = "order_events"
    ORDER_CACHE_TTL = 300

settings = Settings()


