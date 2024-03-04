from typing import Dict
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    def add_connection(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket

    def remove_connection(self, user_id: str):
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_message(self, user_id: str, message: Dict):
        if user_id in self.connections:
            await self.connections[user_id].send_json(message)

WSManager = WebSocketManager