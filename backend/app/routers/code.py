import logging
from io import StringIO
import re
import sys

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from openai import OpenAI

from websocket_manager import WSManager

logger = logging.getLogger('fastapi')

SYSTEM_MESSAGE = "You are python programming assistant. You are given python code, and a question or enhancement request related to it. If you aren't given any python code, you will need to generate it. In both cases include (RESPONSE): and (CODE): tags, everything after the (CODE): must be valid code. You MUST respond in format: (RESPONSE): <your response> (CODE): <code>"
#SYSTEM_MESSAGE = "You are python programming assistant. You are given python code, and a question or enhancement request related to it. You must include modified code after (CODE): tag, everything after the (CODE): tag must be valid python code. You MUST respond in format: <your response> (CODE): <code>"
SYSTEM_MESSAGE = "You are python programming assistant. You are given python code, and a question or improvement request related to it. Include your modified code in JSON code field, code field must be valid python code. You MUST respond with JSON in format: {response: <your response>, code: <your code>}"
MESSAGE_TYPES = {
    'execute_code': "Explain what this code does.",
    'enhance': "How would you improve this code? Try to always find something to improve. Don't improve anything that already exists in code. Improvements can be anything, for example: latest PEP style, logging, error handling, usability, run speed, readability, memory optimization, bug fixes, etc..",
    'add_logging': "Please add logging to this code using python built-in logging library. Don't modify already existing logging statements. Add new ones if there is missing, or convert print statements to logger.",
    'find_bugs': "Find possible bugs in this code. Respond with modified code.",
    'gen_message': "Customer class that has usual customer attributes.",
    'error_message': "This code produces error: ",
}


router = APIRouter(
    prefix='/code'
)


class CodeRequest(BaseModel):
    code: str
    message_type: str


def execute_code(code: str):
    try:
        # Redirect stdout and stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Execute the code
        exec(code)

        # Capture the output and error messages
        output_message = sys.stdout.getvalue()
        error_message = sys.stderr.getvalue()

        # Restore the original stdout and stderr
        sys.stdout = original_stdout
        sys.stderr = original_stderr

        print('Output:', output_message)
        print('Error:', error_message)

        return {'status': 'success', 'code': output_message}
    except Exception as e:
        return {'status': 'error', 'code': str(e)}


@router.post("/")
async def execute_code_endpoint(code_request: CodeRequest):
    print("Code request: ", code_request)
    if code_request.message_type == 'execute_code':
        code_res = execute_code(code_request.code)
        print("CODE RES: ", code_res)
        #return code_res

    message = MESSAGE_TYPES.get(code_request.message_type)
    res = _get_openai_response(code_request.code, message)
    #print('res: ', res[0].encode('utf-8').decode('utf-8'))
    if not res:
        return {'message': res, 'status': 'error'}
    #for row in res:
    #    print('res row:', row)
    result = res[0].strip()
    print('openai response: ', result)
    response_message, response_code = parse_open_ai_response(result)

    status = 'success'
    if code_request.message_type == 'execute_code':
        response_code = code_res['code']
        status = code_res['status']
    
    response = {"message": response_message, "status": status, "code": response_code}
    print('final response:', response)
    return response


def parse_open_ai_response(openai_response):
    response_pattern = r"\(RESPONSE\):(.*?)(\(CODE\)|$)"
    code_pattern = r"\(CODE\):(.*)"
    parts = openai_response.split('(CODE):')
    print(parts)
    import json
    json_resp = json.loads(openai_response)
    print(json_resp)
    message = json_resp.get('response', 'No response found')
    code = json_resp.get('code', 'No code found')
    #code_matches = re.search(code_pattern, openai_response, re.DOTALL)
    #response_matches = re.search(response_pattern, openai_response, re.DOTALL)
    #message = response_matches.group(1) if response_matches and response_matches.group(1) else ""
    #code = code_matches.group(1).strip() if code_matches and code_matches.group(1) else ""
    #print('groups:', matches.groups())
    return message, code


def _get_openai_response(code: str, message: str):
    client = OpenAI()
    result = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "assistant", "content": code},
            {"role": "user", "content": message}
        ],
        response_format={ "type": "json_object" },
        #stream=True
    )
    for row in result.choices:
        print('choice row:', row)
    res = [x.message.content for x in result.choices]
    print('res after choices:', res)
    return res


manager = WSManager()

#@router.websocket("/ws/{user_id}")
#async def code_chat(user_id: str, websocket: WebSocket):
#    print('Opening websocket connection')
#    await websocket.accept()
#    manager.add_connection(user_id, websocket)
#    #message_id = 1
#    try:
#        while True:
#            message_json = await websocket.receive_json()
#            message_text = message_json.get('code')
#            message_filename = message_json.get('message')
#            #message_id = message_json.get('id')
#            #manager.add_message(user_id, {'type': 'user', 'id': message_id, 'text': message_text})
#            #message_id += 1
#
#            full_text = ""
#            async for partial_response in get_openai_response_from_file_stream(message_filename, message_text):
#                if partial_response is not None:
#                    full_text += partial_response
#                    await websocket.send_json({'text': partial_response, 'type': 'bot'})
#
#    except WebSocketDisconnect:
#        print('Websocket disconnected:', user_id)
#        manager.remove_connection(user_id)
#    except Exception as e:
#        print('Exception:', e)
#        manager.remove_connection(user_id)


async def get_openai_response_from_file_stream(code: str, message: str):
    #print(embeddings_result)

    client = OpenAI()
    for partial_result in client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": message}] + [{"role": "assistant", "content": code}],
        stream=True
    ):
        partial_msg = partial_result.choices[0].delta.content
        yield partial_msg

