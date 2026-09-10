from fastapi import APIRouter,Request
from starlette.responses import StreamingResponse
from app.chatbot import stream_chat_response
from app.history import get_history,delete_history
router = APIRouter(prefix="/api", tags=["聊天"])


@router.post("/chat/stream")
async def stream(request:Request):
    return StreamingResponse(
        #TODO
        stream_chat_response(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@router.get("/chat/history/{session_id}")
async def get(session_id:str):
    return get_history(session_id)

@router.delete("/chat/history/{session_id}")
async def delete(session_id: str):
    """清空指定会话的历史"""
    delete_history(session_id)
    return {"message": f"会话 {session_id} 的历史已清空"}