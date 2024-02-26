import logging
from pathlib import Path

from database.database import search_embeddings, ingest_embeddings, ingest_pdf_bytes, pdf_exists_in_database, get_all_pdf_filenames
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends

logger = logging.getLogger('fastapi')

router = APIRouter(
    prefix='/files'
)


#@router.get('/')
#def get_embeddings(mystr: str):
#    res = search_embeddings(mystr)
#    return {'results': res}


#@router.post('/')
#def post_embedding(mystr: str):
#    print(mystr)
#    res = ingest_embeddings(mystr)
#    print(res)
#    return mystr


def is_pdf(file_path: Path) -> bool:
    return file_path.suffix.lower() == ".pdf"


async def validate_pdf(file: UploadFile = File(...)):
    if not is_pdf(Path(file.filename)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF files are allowed",
        )
    return file


@router.get('')
def get_files():
    return {'files': get_all_pdf_filenames()}


@router.post('')
def upload(file: UploadFile = Depends(validate_pdf)):
    try:
        print('Uploading file', file.filename)
        if pdf_exists_in_database(file.filename):
            return {"message": "File exists already in database!"}
        contents = file.file.read()
        ingest_pdf_bytes(file.filename, contents)

    except Exception as e:
        logger.exception(e)
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}
