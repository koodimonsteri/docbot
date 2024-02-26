import json
from typing import Dict

from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from openai import OpenAI

from database.database import search_embeddings

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
            message_json = await websocket.receive_json()
            message_text = message_json.get('text')
            message_filename = message_json.get('file_name')
            
            if not message_filename:
                response = await get_openai_response(message_text)
                print('Sending response back to client:', response)
            else:
                # Embeddings to chat in here
                response = await get_openai_response_from_file(message_filename, message_text)
                
            await manager.send_message(user_id, response)
    except WebSocketDisconnect:
        print('Websocket disconnected:', user_id)
        manager.remove_connection(user_id)


async def get_openai_response(message: str) -> str:
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    
    res = [x.message.content.strip() for x in result.choices]
    return res[0]


async def get_openai_response_from_file(file_name: str, message: str) -> str:
    embeddings_result = search_embeddings(file_name, message)
    print(embeddings_result)
    
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}] + [{"role": "assistant", "content": response} for response in embeddings_result]
    )

    res = [x.message.content.strip() for x in result.choices]
    print(res)
    return res[0]