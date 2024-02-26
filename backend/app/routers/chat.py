import json
from typing import Dict, List

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
        self.chat_histories: Dict[str, List[Dict]] = {}

    def add_connection(self, user_id: str, websocket: WebSocket):
        self.connections[user_id] = websocket
        self.chat_histories[user_id] = []

    def remove_connection(self, user_id: str):
        if user_id in self.connections:
            del self.connections[user_id]
        if user_id in self.chat_histories:
            del self.chat_histories[user_id]

    def add_message(self, user_id, message: Dict):
        print('Add message to chat history:', message)
        if user_id in self.chat_histories:
            self.chat_histories[user_id].append(message)
        else:
            self.chat_histories[user_id] = [message]

    async def send_message(self, user_id: str, message: Dict):
        if user_id in self.connections:
            await self.connections[user_id].send_json(message)
        if user_id in self.chat_histories:
            self.chat_histories.append


manager = WebSocketManager()

@router.websocket("/ws/{user_id}")
async def chat_endpoint(user_id: str, websocket: WebSocket):
    print('Opening websocket connection')
    await websocket.accept()
    manager.add_connection(user_id, websocket)
    message_id = 1
    try:
        while True:
            message_json = await websocket.receive_json()
            message_text = message_json.get('text')
            message_filename = message_json.get('file_name')
            message_id = message_json.get('id')
            manager.add_message(user_id, {'type': 'user', 'id': message_id, 'text': message_text})
            message_id += 1

            if not message_filename:
                full_text = ""
                async for partial_response in get_openai_response_stream(message_text):
                    if partial_response is not None:
                        full_text += partial_response
                        await websocket.send_json({'text': partial_response, 'id': message_id, 'type': 'bot'})
                manager.add_message(user_id, {'type': 'bot', 'id': message_id, 'text': full_text})
                message_id += 1
            else:
                full_text = ""
                async for partial_response in get_openai_response_from_file_stream(message_filename, message_text):
                    if partial_response is not None:
                        full_text += partial_response
                        await websocket.send_json({'text': partial_response, 'id': message_id, 'type': 'bot'})

                manager.add_message(user_id, {'type': 'bot', 'id': message_id, 'text': full_text})
                message_id += 1

    except WebSocketDisconnect:
        print('Websocket disconnected:', user_id)
        manager.remove_connection(user_id)
    except Exception as e:
        print('Exception:', e)
        manager.remove_connection(user_id)


async def get_openai_response(message: str) -> str:
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}]
    )
    
    res = [x.message.content.strip() for x in result.choices]
    return res[0]


async def get_openai_response_stream(message: str):
    client = OpenAI()
    for partial_result in client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}],
        stream=True
    ):
        partial_msg = partial_result.choices[0].delta.content
        yield partial_msg


async def get_openai_response_from_file(file_name: str, message: str) -> str:
    embeddings_result = search_embeddings(file_name, message)
    print(embeddings_result)
    
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}] + [{"role": "assistant", "content": response} for response in embeddings_result]
    )

    res = [x.message.content.strip() for x in result.choices]
    return res[0]


async def get_openai_response_from_file_stream(file_name: str, message: str):
    embeddings_result = search_embeddings(file_name, message)
    print(embeddings_result)

    client = OpenAI()
    for partial_result in client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}] + [{"role": "assistant", "content": response} for response in embeddings_result],
        stream=True
    ):
        partial_msg = partial_result.choices[0].delta.content
        yield partial_msg
