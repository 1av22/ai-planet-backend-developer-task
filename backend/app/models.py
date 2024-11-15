from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Files(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_url = Column(String, unique=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("Users", back_populates="files")


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)

    files = relationship("Files", back_populates="owner")
    documents = relationship("Documents", back_populates="owner")


class Documents(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    document_name = Column(String, index=True)
    document_type = Column(String)
    upload_date = Column(DateTime, default=datetime.utcnow)
    s3_url = Column(String)

    owner = relationship("Users", back_populates="documents")
    document_metadata = relationship(
        "DocumentMetadata", back_populates="document")


class DocumentMetadata(Base):
    __tablename__ = 'document_metadata'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    metadata_key = Column(String)
    metadata_value = Column(String)

    document = relationship("Documents", back_populates="document_metadata")
