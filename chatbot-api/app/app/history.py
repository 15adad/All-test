# 根据 session_id 获取该会话的所有消息列表。
from typing import Dict, List
from app.models import Message, MessageRequest

# 内存存储把每一条消息存起来
chat_sessions: Dict[str, List[Message]] = {}

"""
get_history(session_id)：根据 session_id 获取该会话的所有消息列表。

add_message(session_id, role, content)：向指定会话添加一条消息。

clear_history(session_id)：清空指定会话的所有消息。"""


def get_history(session_id):
    return chat_sessions.get(session_id,[])


def add_message(session_id:str, role, content):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append(Message(role=role, content=content))
    return chat_sessions[session_id]


def delete_history(session_id):
    if session_id in chat_sessions:
        chat_sessions[session_id] = []
