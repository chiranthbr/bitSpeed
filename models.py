from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from database import Base
import enum

class LinkPrecedence(str, enum.Enum):
    primary = "primary"
    secondary = "secondary"

class Contact(Base):
    __tablename__ = "Contact"

    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    linkedId = Column(Integer, nullable=True)
    linkPrecedence = Column(Enum(LinkPrecedence), default="primary")
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)