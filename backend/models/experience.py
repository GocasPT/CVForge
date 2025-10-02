from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql.sqltypes import Date
from config import Base, MAX_NAME_LENGTH

class Experience(Base):
    __tablename__ = 'experiences'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    position = Column(String(MAX_NAME_LENGTH), nullable=False)
    company = Column(String(MAX_NAME_LENGTH), nullable=False)
    location = Column(String(MAX_NAME_LENGTH), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, nullable=False)
    achievements = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
