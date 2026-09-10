# 定义模型
from typing import List, Optional

from pydantic import BaseModel, Field


# 定义消息请求体 POST
class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=300, description="信息")
    session_id: Optional[str] = Field(None, description="会话ID")

# 单条消息
class Message(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str

# 对话历史记录
class History(BaseModel):
    session_id: str
    messages: List[Message]
