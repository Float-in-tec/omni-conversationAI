import sqlalchemy
from .base import Base

class DAOMessage(Base):
    __tablename__ = "messages"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    conversation_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("conversations.id"), nullable=False)
    sender = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)  # contact | agent | ai
    content = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.current_timestamp())
