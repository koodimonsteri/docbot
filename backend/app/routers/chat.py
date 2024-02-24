from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse

from openai import OpenAI


router = APIRouter(
    prefix='/chat'
)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/chat/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@router.get('/')
async def get_chat():
    return HTMLResponse(html)


@router.websocket("/ws")
async def chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = await get_openai_response(data)
            await websocket.send_text(response)
    finally:
        await websocket.close()


async def get_openai_response(message: str) -> str:
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        #response_format={ "type": "json_object" },
        messages=[{"role": "user", "content": message}]
    )
    
    res = [x.message.content.strip() for x in result.choices]
    return res

