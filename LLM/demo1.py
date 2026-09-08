import asyncio
import sys


# ---------- 模拟大模型流式生成的异步生成器 ----------
async def stream_llm_response(text: str, delay: float = 0.1):
    """
    模拟大模型逐 token（字符）生成响应。
    :param text: 要输出的完整文本
    :param delay: 每个 token 之间的延迟（秒），模拟生成时间
    """
    for token in text:
        await asyncio.sleep(delay)
        yield token


# ---------- 主程序：消费异步生成器 ----------
async def main():
    # 准备一段示例文本（可以是任意长文本）
    sample_text = (
        "你好，我是 DeepSeek 助手。\n"
        "我正在通过异步生成器逐字输出这条消息，"
        "模拟大模型流式生成的效果。\n"
        "你可以看到每个字符逐个出现，就像真实的 AI 对话一样。"
    )

    print("🤖 大模型开始流式输出：\n")

    # 使用 async for 逐 token 消费
    async for token in stream_llm_response(sample_text,0.08):
        sys.stdout.write(token)
        sys.stdout.flush()

# 启动事件循环
if __name__ == "__main__":
    asyncio.run(main())