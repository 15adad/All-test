import asyncio
import json
import random

from sse_starlette.sse import ServerSentEvent
from app.history import add_message

RESPONSES = {
    "你好": "你好！很高兴见到你。有什么我可以帮你的吗？",
    "天气": "今天天气不错，阳光明媚。不过我暂时没有联网获取实时天气的能力。",
    "名字": "我叫小助手，是你的 AI 对话伙伴。",
    "默认": "我理解你的问题，但作为演示版机器人，我的知识有限。"
}

""" 1. 用 await asyncio.sleep(random.uniform(0.5, 1.5)) 模拟 AI 推理延迟
    2. 遍历 RESPONSES，匹配关键词
    3. 返回匹配的回复字符串"""
# 异步回复生成函数
async def async_generate_response(user_message: str) -> str:
    await asyncio.sleep(random.uniform(1, 2))
    for keyword, response in RESPONSES.items():
        if keyword in user_message:
            return response
    return RESPONSES["默认"]


async def stream_chat_response(request, user_message, session_id):
    # 1. 先存用户消息
    add_message(session_id, "user", user_message)

    # 2. 获取完整回复（一次性）
    full_response = await async_generate_response(user_message)

    # 3. 逐字流式输出
    for idx, char in enumerate(full_response):
        if await request.is_disconnected():
            print("已断开")
            return

        await asyncio.sleep(0.05)  # 每个字的间隔

        yield ServerSentEvent(
            data=char,  # 单个字符
            event="token",  # 注意是单数
            id=str(idx)
        )

    # 4. 全部输出完后，把 AI 回复存入历史
    add_message(session_id, "assistant", full_response)

    # 5. 发送结束信号
    yield ServerSentEvent(
        data=json.dumps({"session_id": session_id}),
        event="done"
    )

