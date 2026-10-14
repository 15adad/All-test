from fastapi import APIRouter, Query, WebSocket
from httpx2.websockets import WebSocketDisconnect
import logging

from ws_manager import ConnectionManager

router = APIRouter()
logger = logging.getLogger()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, user_id: int = Query(...)):
    await ConnectionManager.connect(ws, user_id)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        logger.info("websocket disconnect")
    finally:
        ConnectionManager.disconnect(ws)
