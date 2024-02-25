import json
from typing import Dict

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from openai import OpenAI


router = APIRouter(
    prefix='/chat'
)


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    def add_connection(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket

    def remove_connection(self, user_id: str):
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_message(self, user_id: str, message: str):
        if user_id in self.connections:
            await self.connections[user_id].send_text(message)

manager = WebSocketManager()


@router.websocket("/ws/{user_id}")
async def chat_endpoint(user_id: str, websocket: WebSocket):
    print('Opening websocket connection')
    await websocket.accept()
    manager.add_connection(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await get_openai_response(data)
            print('Sending response back to client:', response)
            #await websocket.send_json({'message': response})
            await manager.send_message(user_id, response)
    except WebSocketDisconnect:
        print('Websocket disconnected:', user_id)
        manager.remove_connection(user_id)
    #finally:
    #    print('Closing websocket connection!')
    #    await websocket.close()


async def get_openai_response(message: str) -> str:
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    
    res = [x.message.content.strip() for x in result.choices]
    return res[0]

