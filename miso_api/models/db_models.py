from sqlalchemy import Column, String, Integer, Text
from ..database import Base

class GenesisJob(Base):
    __tablename__ = 'genesis_jobs'

    id = Column(String, primary_key=True, index=True)
    status = Column(String, index=True)
    prompt = Column(Text)
    result = Column(Text, nullable=True)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
