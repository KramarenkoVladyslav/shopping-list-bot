from typing import Dict, List
from fastapi import WebSocket

class WebSocketManager:
    """ Manages WebSocket connections for real-time updates in rooms. """

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}  # room_id -> list of WebSocket connections

    async def connect(self, room_id: int, websocket: WebSocket):
        """ Accepts a new WebSocket connection and adds it to the room. """
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        """ Removes a WebSocket connection when a user disconnects. """
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]  # Remove room if no active connections

    async def send_message(self, room_id: int, message: str):
        """ Sends a well-formatted message to all connected clients in a room. """
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id]:
                await connection.send_text(message)

# Global instance of the WebSocketManager
websocket_manager = WebSocketManager()
