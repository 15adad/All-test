import asyncio
import random
from typing import List

from fastapi import FastAPI, Request, Depends
from starlette.responses import StreamingResponse

from pydantic import BaseModel, Field
from sse_starlette.sse import ServerSentEvent, EventSourceResponse

app = FastAPI()

# 2. 阈值配置
# ============================================================
THRESHOLDS = {
    "cpu": 90.0,
    "memory": 85.0,
    "disk": 80.0,
}

UNITS = {
    "cpu": "%",
    "memory": "%",
    "disk": "%",
}


class PydanticModel(BaseModel):
    metrics: str = Field("cpu,memory,disk", description="各个指标")
    interval: float = Field(2, ge=0.5, le=10.0, description="采样间隔")


async def monitor(request: Request, metrics: List[str], interval: float):
    values = {"cpu": 30.0, "memory": 50.0, "disk": 60.0}
    # 各个指标浮动+-0.3
    count: int = 1
    while True:
        # 从values列表里随机选一个指标
        random_key = random.choice(metrics)
        # 做上下浮动0.3逻辑
        temp_data = values[random_key] * random.uniform(-0.3, 0.3)
        new_value = values[random_key] + temp_data
        new_value = max(0.0, min(100.0, new_value))
        if await request.is_disconnected():
            print("客户端断开")
            return
        if new_value > THRESHOLDS[random_key]:
            yield ServerSentEvent(
                data=f"{random_key}:{values[random_key]}超过阈值{THRESHOLDS[random_key]}了",
                event="alert"
            )
        yield ServerSentEvent(
            data=f"{random_key} : {new_value}",
            event="metric"
        )
        values[random_key] = new_value
        await asyncio.sleep(interval)
        if count % 5 == 0:
            yield ServerSentEvent(
                comment="alive"
            )
        count += 1


"""路由"""
@app.get("/monitor/stream")
async def monitor_stream(request: Request, q: PydanticModel = Depends()):
    monitor_list  = [e.strip() for e in q.metrics.split(",")]
    return EventSourceResponse(
        monitor(request,monitor_list,q.interval),
        media_type = "text/event-stream",
        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("demo9:app", host="127.0.0.1", port=8000)
