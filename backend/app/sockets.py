from typing import Dict

from fastapi import Depends
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.auth import get_current_user
from app.models import TokenData

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user: TokenData):
        await websocket.accept()
        self.active_connections[user.username] = websocket

    def disconnect(self, username: str):
        del self.active_connections[username]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, user: TokenData = Depends(get_current_user)):
    await manager.connect(websocket, user)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"User #{user.username} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user.username)
        await manager.broadcast(f"User #{user.username} left the chat") 