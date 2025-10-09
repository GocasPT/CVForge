from sqlalchemy import Column, Integer, String, DateTime, Text, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql.sqltypes import Date

from backend.config import Base, MAX_NAME_LENGTH


class Experience(Base):
    __tablename__ = "experiences"

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

    def as_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "company": self.company,
            "location": self.location,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "description": self.description,
            "technologies": self.technologies,
            "achievements": self.achievements,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
