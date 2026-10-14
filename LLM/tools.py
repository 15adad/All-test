from datetime import datetime, UTC

from langchain_core.tools import tool


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