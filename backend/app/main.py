import os
import logging

from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from routers import files, chat, code
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('fastapi')

app = FastAPI(
    debug=True
)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(files.router)
app.include_router(chat.router)
app.include_router(code.router)

@app.get("/")
async def root():
    logger.info('Get app root.')
    return {'msg": "Get root, nothing to see here..'}


if __name__ == "__main__":
    if os.environ.get('APP_ENV') == "development":
        uvicorn.run("main:app", host="0.0.0.0", port=3500,
                    workers=4, reload=True)
