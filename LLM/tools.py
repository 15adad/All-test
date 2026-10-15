import random
from datetime import datetime, UTC
from langchain_core.tools import tool

from LLM.rag import _load_vectorstore

_vectorstore = None


@tool
def calculator(expression: str) -> str:
    """计算数学表达式。

    当用户需要做数学计算时使用。支持 + - * / ** 和括号。

    Args:
        expression: 数学表达式，例如 "2 + 3 * 4" 或 "(10 + 5) / 3"

    Returns:
        计算结果
    """
    try:
        # 只允许安全的字符，防止注入
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "表达式包含不支持的字符"
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


@tool
def get_current_time() -> str:
    """获取当前日期和时间。

    当用户询问"现在几点"、"今天几号"、"当前时间"时使用。

    Returns:
        当前日期时间字符串
    """
    now = datetime.now()
    return f"当前的时间是：{now.strftime("%Y-%m-%d %H:%M:%S，星期" + "一二三四五六日"[now.weekday()])} ，当前的时区是：{datetime.now(UTC)}"


@tool
def random_number(min: int, max: int) -> str:
    """生成指定范围内的随机整数。

        当用户需要随机数、抽签、掷骰子时使用。

        Args:
            min_value: 最小值（包含）
            max_value: 最大值（包含）

        Returns:
            随机整数
        """
    if min > max:
        return f"最小值不能大于最大值"
    return f"随机整数为：{random.randint(min, max)}"


@tool
def word_count(text: str) -> str:
    """统计一段文本的字符数和词数。

    当用户想知道文本长度时使用。

    Args:
        text: 要统计的文本

    Returns:
        字符数和词数
    """
    char_count = len(text)
    # 按**任意空白**分割（空格、制表符`\t`、换行`\n`），**自动忽略连续空白，首尾空白直接丢掉**
    word_count = len(text.split())
    return f"字符数：{char_count}，词数：{word_count}"


@tool
def search_notes(query: str) -> str:
    """搜索用户的个人笔记。笔记内容包括 Python 编程和机器学习知识。

    当用户询问笔记里的知识点、概念、定义、用法时使用这个工具。

    Args:
        query: 要搜索的问题，例如 "什么是装饰器" 或 "过拟合怎么解决"

    Returns:
        检索到的相关笔记片段
    """
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = _load_vectorstore()

    docs = _vectorstore.similarity_search(query, k=3)
    if not docs:
        return "笔记中没有找到相关内容"

    #
    #
    results = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "未知来源")
        results.append(f"[片段{i}来源{source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(results)
