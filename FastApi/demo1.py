import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

async def text_generator(text: str):
    """异步生成器：逐字产出"""
    for char in text:
        await asyncio.sleep(0.1)  # 模拟 LLM 生成延迟
        # SSE 协议要求格式：data: <内容>\n\n
        yield f"data: {json.dumps({'token': char})}\n\n"
    # 发送结束标志
    yield f"data: {json.dumps({'type': 'end'})}\n\n"

@app.get("/chat/stream")
async def chat_stream(question: str):
    # 这里可以调用真实的 LLM API，此处用模拟文本代替
    full_text = f"你好！你问的是：{question}。我是 AI 助手，正在流式回复..."
    return StreamingResponse(
        text_generator(full_text),
        media_type="text/event-stream"  # 必须设置！
    )