import sqlalchemy
from .base import Base

class DAOConversation(Base):
    __tablename__ = "conversations"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    company_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("companies.id"), nullable=False)
    channel_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("channels.id"), nullable=False)
    contact_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("contacts.id"), nullable=False)
    owner_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("users.id"))
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.current_timestamp())
