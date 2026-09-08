from pydantic import BaseModel, Field
from typing import Optional

class CalculationRequest(BaseModel):
    """计算请求模型"""
    a: float = Field(..., description="第一个数字")
    b: float = Field(..., description="第二个数字")
    operation: str = Field(..., description="运算类型: add, subtract, multiply, divide")

class CalculationResponse(BaseModel):
    """计算响应模型"""
    a: float
    b: float
    operation: str
    result: float
    message: Optional[str] = None