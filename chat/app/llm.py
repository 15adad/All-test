import asyncio

RESPONSES = {
    "你好": "你好！很高兴见到你，有什么我可以帮你的吗？",
    "天气": "今天天气不错，阳光明媚。不过我没有联网获取实时天气的能力。",
    "名字": "我叫小助手，是你的 AI 对话伙伴。",
    "默认": "我理解你的问题，但作为演示版机器人，我的知识有限。"
}


async def stream_llm_response(prompt: str):
    reply = RESPONSES["默认"]
    for kw, resp in RESPONSES.items():
        if kw in prompt:
            reply = resp
            break

    await asyncio.sleep(0.5)
    for char in reply:
        await asyncio.sleep(0.05)
        yield char