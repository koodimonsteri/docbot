import logging
import os

from openai import OpenAI
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from database.model import Embedding
import settings

logger = logging.getLogger(__name__)


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


def search_embeddings(text: str):
    logger.info('Searching embeddings for text: %s', text)

    client = OpenAI()
    #texts = [x.replace("\n", " ") for x in texts]
    embeddings = client.embeddings.create(input = [text], model=settings.EMBEDDING_MODEL).data[0].embedding
    #print('embeddings: ', embeddings)
    session = get_session()
    try:
        result = session.scalars(select(Embedding).order_by(Embedding.embedding.cosine_distance(embeddings)).limit(3))
        print(result)
        return result
    except Exception as error:
        print("Error..", error)
    finally:
        session.close()


