import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.dialects.sqlite import JSON

from backend.config.database import Base


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, nullable=False)
    achievements = Column(JSON, nullable=False)
    duration = Column(String(255), nullable=False)
    role = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))