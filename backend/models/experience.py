import datetime

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql.sqltypes import Date

from backend.config.database import Base


class Experience(Base):
    __tablename__ = 'experiences'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, nullable=False)
    achievements = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))