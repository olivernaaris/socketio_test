"use client";

import { useEffect, useState } from "react";
import io from "socket.io-client";
import ChatBox from "../components/ChatBox";

// Our static token - in a real app, you'd want to store this securely
const STATIC_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

export default function ChatPage() {
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const newSocket = io("http://localhost:8000", {
      auth: {
        token: STATIC_TOKEN
      },
      transports: ['websocket'],
      upgrade: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 5000,
    });

    // Add more detailed connection logging
    newSocket.on("connect", () => {
      console.log("Connected to Socket.IO");
      console.log("Transport:", newSocket.io.engine.transport.name);
      setConnected(true);
    });

    newSocket.on("connect_error", (error) => {
      console.error("Connection error:", error);
      console.error("Error details:", {
        type: error.type,
        message: error.message,
        description: error.description
      });
      setConnected(false);
    });

    newSocket.io.on("error", (error) => {
      console.error("Transport error:", error);
    });

    newSocket.io.on("reconnect_attempt", (attempt) => {
      console.log("Reconnection attempt:", attempt);
    });

    // Chat message handler
    newSocket.on("chat_message", (msg: string) => {
      setMessages((prevMessages) => [...prevMessages, msg]);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const sendMessage = (message: string) => {
    if (socket && connected) {
      socket.emit("chat_message", message);
    }
  };

  if (!connected) {
    return <p>Connecting to chat...</p>;
  }

  return (
    <div className="flex flex-col h-screen">
      <div className="bg-gray-200 p-4">
        <p className="text-lg font-semibold">Chat</p>
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className="mb-2 p-2 bg-white rounded shadow">
            {msg}
          </div>
        ))}
      </div>
      <ChatBox onSendMessage={sendMessage} />
    </div>
  );
} 