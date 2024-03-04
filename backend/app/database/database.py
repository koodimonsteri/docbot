from io import BytesIO
import logging
import os

from fastapi import UploadFile
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from pypdf import PdfReader
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database.model import Embedding
import settings

logger = logging.getLogger('fastapi')


def get_engine():
    db_name = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    pwd = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    return create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db_name}")


def get_session(engine=None):
    engine = engine or get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def pdf_exists_in_database(file_name: str):
    session = get_session()
    temp = session.query(Embedding).filter(Embedding.file_name == file_name).all()
    return bool(temp)


def get_all_pdf_filenames():
    session = get_session()
    temp = session.query(Embedding).all()
    files = [x.file_name for x in temp]
    return set(files)


def ingest_pdf_bytes(file_name: str, pdf_bytes: bytes):
    print('Extracting text.')
    reader = PdfReader(BytesIO(pdf_bytes))
    doc_str = ''
    for page in reader.pages:
        text = page.extract_text()
        doc_str += text
        
    print('Splitting text.')
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap = 100
    )
    splits = splitter.split_text(doc_str)
    print(splits)

    logger.info('Creating embeddings')
    client = OpenAI()
    embeddings = client.embeddings.create(input = splits, model=settings.EMBEDDING_MODEL).data

    session = get_session()
    try:
        for text, embedding in zip(splits, embeddings):
            logger.info('Add new embeddings to database')
            session.add(Embedding(
                embedding=embedding.embedding,
                text=text,
                file_name=file_name
            ))
        session.commit()
    except (Exception) as error:
        print("Error while writing to DB", error)
        session.rollback()
    finally:
        session.close()


def ingest_embeddings(text: str):
    #texts = [
    #    "I like to eat broccoli and bananas.",
    #    "I ate a banana and spinach smoothie for breakfast.",
    #    "Chinchillas and kittens are cute.",
    #    "My sister adopted a kitten yesterday.",
    #    "Look at this cute hamster munching on a piece of broccoli.",
    #]

    client = OpenAI()

    texts = [text]
    logger.info('Creating embeddings')
    embeddings = client.embeddings.create(input = texts, model=settings.EMBEDDING_MODEL).data

    session = get_session()
    try:
        for text, embedding in zip(texts, embeddings):
            logger.info('Add new embeddings to database')
            session.add(Embedding(
                embedding=embedding.embedding,
                text=text
            ))

        session.commit()
    except (Exception) as error:
        print("Error while writing to DB", error)
        session.rollback()
    finally:
        session.close()


def search_embeddings(file_name: str, text: str):
    logger.info('Searching embeddings for text: %s', text)

    client = OpenAI()
    embeddings = client.embeddings.create(input = [text], model=settings.EMBEDDING_MODEL).data[0].embedding
    
    session = get_session()
    try:
        result = session.scalars(
            select(Embedding)
            .filter(Embedding.file_name == file_name)
            .order_by(Embedding.embedding.cosine_distance(embeddings))
            .limit(3)
        )
        results = [x.text for x in result]
        return results
    except Exception as error:
        print("Error..", error)
    finally:
        session.close()



