from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column, declarative_base
from sqlalchemy import Column, BigInteger, DateTime, func, TEXT

Base = declarative_base()


class Embedding(Base):
    __tablename__ = 'Embeddings'

    id = Column(BigInteger, primary_key=True)
    embedding = mapped_column(Vector())
    text = Column(TEXT)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
