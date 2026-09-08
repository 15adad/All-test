import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def text_generator(text: str):
    for char in text:
        await asyncio.sleep(0.1)  # 模拟推理延迟
        # 注意：必须加 \n\n，否则浏览器不会分帧触发事件
        yield f"data: {json.dumps({'token': char})}\n\n"
    # 结束标记
    yield f"data: {json.dumps({'type': 'end'})}\n\n"

@app.get("/chat")
async def chat_stream(msg: str = "你好"):
    full_text = f"你说了：{msg}。我是最小化 AI，正在流式回复..."
    return StreamingResponse(
        text_generator(full_text),
        media_type="text/event-stream"  # 强制要求，开启 SSE 模式
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)