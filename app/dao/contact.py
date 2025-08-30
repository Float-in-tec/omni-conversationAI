import sqlalchemy
from .base import Base

class DAOContact(Base):
    __tablename__ = "contacts"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    company_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("companies.id"), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(255))
    phone = sqlalchemy.Column(sqlalchemy.String(50))
    email = sqlalchemy.Column(sqlalchemy.String(255))
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.current_timestamp())
