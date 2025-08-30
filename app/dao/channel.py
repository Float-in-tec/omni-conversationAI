import sqlalchemy
from .base import Base

class DAOChannel(Base):
    __tablename__ = "channels"

    id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True, autoincrement=True)
    company_id = sqlalchemy.Column(sqlalchemy.BigInteger, sqlalchemy.ForeignKey("companies.id"), nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String(255), nullable=False)
    type = sqlalchemy.Column(sqlalchemy.String(50), nullable=False)
    created_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=sqlalchemy.func.current_timestamp())
