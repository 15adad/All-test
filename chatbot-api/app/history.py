# 根据 session_id 获取该会话的所有消息列表。
from app.models import ChatHistory


def get_history(session_id):
    return ChatMessage(session_id=session_id,)