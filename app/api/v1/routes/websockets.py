from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websockets.manager import websocket_manager

router = APIRouter()


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    """Handles WebSocket connections for real-time updates in a room."""
    await websocket_manager.connect(websocket, room_id)

    try:
        while True:
            await websocket.receive_text()  # Keep connection open
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, room_id)
