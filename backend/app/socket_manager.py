import socketio
from app.config import settings
import json

# Create Socket.IO server with Redis manager
mgr = socketio.AsyncRedisManager('redis://localhost:6379/0')
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    client_manager=mgr,
    logger=True,
    engineio_logger=False,
    transports=['websocket'],
    engineio_opts={
        'cors_allowed_origins': '*',
        'pingTimeout': 5000,
        'pingInterval': 2500,
        'version': 4
    }
)

class ChatNamespace(socketio.AsyncNamespace):
    async def on_connect(self, sid, environ, auth):
        """Verify the token during WebSocket connection"""
        print(f"Connection attempt - SID: {sid}")
        print(f"Environment: {environ}")
        print(f"Auth data: {auth}")

        # 1. Try Socket.IO native auth
        token = None
        if auth:
            print(f"Socket.IO auth received: {auth}")
            if isinstance(auth, dict):
                token = auth.get('token')
            elif isinstance(auth, str):
                try:
                    auth_dict = json.loads(auth)
                    token = auth_dict.get('token')
                except json.JSONDecodeError:
                    print("Failed to parse auth string")

        # 2. If no token from Socket.IO auth, try headers
        if not token and 'HTTP_TOKEN' in environ:
            print("Using token from headers")
            token = environ['HTTP_TOKEN']

        print(f"Final token: {token}")

        if not token or token != settings.STATIC_TOKEN:
            print("Authentication failed - token mismatch")
            raise ConnectionRefusedError('Authentication failed')

        print(f"Client connected successfully with sid: {sid}")
        return True

    def on_disconnect(self, sid):
        print(f"Client disconnected: {sid}")

    async def on_chat_message(self, sid, data):
        print(f"Message from {sid}: {data}")
        await self.emit("chat_message", data)