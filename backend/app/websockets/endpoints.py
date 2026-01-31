from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.connection_manager import manager

router = APIRouter()

@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Wait for any message from React (or just keep connection open)
            data = await websocket.receive_text()
            # Echo back or handle logic
    except WebSocketDisconnect:
        manager.disconnect(websocket)