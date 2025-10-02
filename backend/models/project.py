from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.dialects.sqlite import JSON
from config import Base, MAX_NAME_LENGTH

class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(MAX_NAME_LENGTH), nullable=False)
    description = Column(Text, nullable=False)
    technologies = Column(JSON, nullable=False)
    achievements = Column(JSON, nullable=False)
    duration = Column(String(MAX_NAME_LENGTH), nullable=False)
    role = Column(String(MAX_NAME_LENGTH), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
