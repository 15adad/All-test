import asyncio
import random

from fastapi import FastAPI,Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from starlette.responses import HTMLResponse
from tenacity import retry

app=FastAPI()

async def log(request:Request):

    yield ServerSentEvent(
        comment="already",
        retry=3000
    )



    yield ServerSentEvent(
        data="代码拉取中",
        event="info"
    )
    await asyncio.sleep(1.5)
    yield ServerSentEvent(
        data="代码拉取完成 (commit: a1b2c3d)",
        event="success"
    )

    if await request.is_disconnected():
        print("已断连")
        return

    yield ServerSentEvent(
        data="安装依赖",
        event="info"
    )
    await asyncio.sleep(2)
    yield ServerSentEvent(
        data="依赖安装完成 (123 packages)",
        event="success"
    )
    if random.random()>0.9:
        yield ServerSentEvent(
            data="运行测试",
            event="info"
        )
        await asyncio.sleep(1.5)
        yield ServerSentEvent(
            data="全部测试通过 (42 passed)",
            event="success"
        )
    else:
        await asyncio.sleep(1.5)
        yield ServerSentEvent(
            data="失败",
            event="fail"
        )

@app.get("/build/logs")
async def routine(request:Request):

    return EventSourceResponse(
        log(request),
        headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no"
        }
    )
@app.get("/")
async def home():
    # 注意：确保你的电脑上，在 'demo5.py' 同级目录下有一个 index.html 文件
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)