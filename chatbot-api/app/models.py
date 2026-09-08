# 定义模型
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """用户发送消息请求体"""
    # 消息最短最长应当有限制
    message: str = Field(..., min_length=1, max_length=3000, description="用户发送的信息")
    session_id: Optional[str] = Field(None, description="用于区分不同用户ID")


class ChatMessage(BaseModel):
    """单条消息"""
    role: str
    content: str


class ChatHistory(BaseModel):
    """历史消息"""
    session_id: str
    messages: List[ChatMessage]
