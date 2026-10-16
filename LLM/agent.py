from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver

from LLM.tools import search_notes, calculator, get_current_time, random_number, word_count

llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
)

tools = [
    search_notes,  # RAG 检索笔记
    calculator,  # 数学计算
    get_current_time,  # 查时间
    random_number,  # 随机数
    word_count,  # 字数统计

]

middleware = [

]
agent = create_agent(
    model=llm,
    tools=tools,
    checkpointer=InMemorySaver(),
    system_prompt=
    """你是一个个人学习助手。你可以使用工具来帮助用户。
工具使用原则：
1. 用户问笔记里的知识（Python、机器学习等）→ 用 search_notes
2. 用户要算数学 → 用 calculator（不要自己算）
3. 用户问时间 → 用 get_current_time
4. 用户要随机数 → 用 random_number
5. 用户要统计字数 → 用 word_count
6. 多个工具可以组合使用

回答原则：
- 基于工具返回的结果回答，不要编造
- 如果笔记里没有，明确说"笔记里没有相关内容"
- 回答简洁、清楚、友好
"""
)
if __name__ == "__main__":
    import logging

    while True:
        try:
            user_input = input("\nYou:").strip()
        except (KeyboardInterrupt, EOFError):
            break
        # 一次输出一段话，交互差
        # result = agent.invoke(
        #     {"messages": [{"role": "user", "content": user_input}]},
        #     config={"configurable": {"thread_id": "user_one"}},
        # )
        # answer = result["messages"][-1]["content"]
        # logging.info(answer)
        for chunk in agent.stream(
                {"messages": [{"role": "user","content": user_input}]},
                config={"configurable": {"thread_id": "user_one"}},
                stream_model="messages"
        ):
            # chunk 是一个元组 (message_chunk, metadata)
            message_chunk, metadata = chunk
            if message_chunk.content:
                print(message_chunk.content, end="", flush=True) # logging没有end和flush
        print()
