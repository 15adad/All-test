import asyncio
from langchain_ollama import OllamaLLM
from rich import print as rprint

llm = OllamaLLM(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

messages = [
    "介绍一下太阳系的行星",
    "介绍一下人工智能",
    "介绍一下深度学习"
]

# 定义一个异步流式任务
async def stream_one(idx, msg):
    rprint(f"\n[bold cyan]=== 问题 {idx}: {msg} ===[/bold cyan]")
    # 使用 astream 异步流式
    async for chunk in llm.astream(msg):
        rprint(chunk, end="")
    print("\n" + "-" * 40)

# 并发执行多个流式任务
async def main():
    tasks = [stream_one(i, msg) for i, msg in enumerate(messages, start=1)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())