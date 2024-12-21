#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio
from app.socket_manager import ChatNamespace, sio

# Initialize FastAPI
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Register the namespace
sio.register_namespace(ChatNamespace('/'))

# Create combined ASGI app
sio_asgi_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path='socket.io',
    static_files=None
)

# Mount the Socket.IO app at the root
app.mount("/", sio_asgi_app)
