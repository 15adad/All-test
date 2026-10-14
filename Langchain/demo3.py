from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
import asyncio
llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
    temperature=0.7,
)

message_history = [
    SystemMessage(content="你是一个专业的问答机器人,回答简洁明了"),
]

print("Start")
while True:
    user_input = input("请输入: ")
    if user_input == "exit":
        break
    message_history.append(HumanMessage(content=user_input))
    ai_reply = ""
    # 调用模型流式输出
    for chunk in llm.stream(message_history):
        print(chunk.content, end="", flush=True)
        ai_reply += chunk.content
    print("\n")
    message_history.append(AIMessage(content=ai_reply))

