import sqlalchemy
from .base import Base

class DAOUser(Base):
    __tablename__ = "users"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    company_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("companies.id"), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    role = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)  # agent | admin | ai-bot
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.current_timestamp())
