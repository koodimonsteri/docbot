from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import mapped_column, declarative_base
from sqlalchemy import Column, BigInteger, DateTime, func, TEXT, Integer, String, ForeignKey

Base = declarative_base()


class Embedding(Base):
    __tablename__ = 'Embeddings'

    id = Column(BigInteger, primary_key=True)
    embedding = mapped_column(Vector())
    text = Column(TEXT)
    file_name = Column(TEXT)
    time_created = Column(DateTime(timezone=True), server_default=func.now())


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    order_index = Column(Integer, nullable=False)
    chat_id = Column(Integer, ForeignKey('chat_histories.id'), nullable=False)
    message_text = Column(TEXT, nullable=False)
    message_type = Column(TEXT, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())



class ChatHistory(Base):
    __tablename__ = 'chat_histories'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

