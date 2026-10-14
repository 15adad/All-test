from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 创建本地模型实例
llm = OllamaLLM(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",  # Ollama 默认地址
    temperature=0.7,
)

# 2. 定义提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的翻译官，请将用户输入的文本从中文翻译成英文。"),
    ("human", "{text}"),
])



# 3. 用 LCEL 串联成链
chain = prompt | llm | StrOutputParser()

print("翻译结果：", end="", flush=True)
for chunk in chain.stream({"text": "你好，今天天气不错。简单来说，temperature 是你控制模型“脑洞大小”的旋钮。"}):
    print(chunk, end="", flush=True)
print()  # 最后换行