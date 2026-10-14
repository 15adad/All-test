from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str
    password: str = Field(max_length=50, description="密码")

class RegisterResponse(BaseModel):
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    created_at: datetime = Field(datetime.now(), description="创建时间")
