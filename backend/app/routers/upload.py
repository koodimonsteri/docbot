import logging

from database.database import search_embeddings, ingest_embeddings, ingest_pdf_bytes
from fastapi import APIRouter, UploadFile, File

logger = logging.getLogger('fastapi')

upload_router = APIRouter(
    prefix='/upload'
)


@upload_router.get('/')
def get_embeddings(mystr: str):
    res = search_embeddings(mystr)
    return {'results': res}


@upload_router.post('/')
def post_embedding(mystr: str):
    print(mystr)
    res = ingest_embeddings(mystr)
    print(res)
    return mystr


@upload_router.post('/file')
def upload(file: UploadFile = File(...)):
    try:
        print('Uploading file', file.filename)
        contents = file.file.read()
        ingest_pdf_bytes(contents)

    except Exception as e:
        logger.exception(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}