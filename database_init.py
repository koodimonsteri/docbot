import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.database.model import Base
from dotenv import load_dotenv


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


def init_db():
    engine = get_engine()
    session = get_session(engine)
    session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
    session.commit()
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    print('Initializing db!')
    from dotenv import load_dotenv
    load_dotenv('./local_db_secrets.env')
    init_db()
