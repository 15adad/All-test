from typing import Tuple


def calculate(a: float, b: float, operation: str) -> Tuple[float, str]:
    """
    执行计算，返回 (结果, 消息)
    """
    ops = {
        "add": lambda x, y: (x + y, f"{x} + {y} = {x + y}"),
        "subtract": lambda x, y: (x - y, f"{x} - {y} = {x - y}"),
        "multiply": lambda x, y: (x * y, f"{x} × {y} = {x * y}"),
        "divide": lambda x, y: (x / y, f"{x} ÷ {y} = {x / y}") if y != 0 else (float('inf'), "错误：除数不能为 0"),
    }

    if operation not in ops:
        raise ValueError(f"不支持的运算: {operation}")

    result, message = ops[operation](a, b)
    return result, message