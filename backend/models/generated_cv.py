from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.types import FLOAT

from config import Base, MAX_PATH_LENGTH


class GeneratedCV(Base):
    __tablename__ = 'generated_cv'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey('cv_templates.id'), nullable=False, index=True)
    job_description = Column(Text, nullable=False)
    selected_projects = Column(JSON, nullable=True)
    selected_experiences = Column(JSON, nullable=True)
    selected_summary_label = Column(String(100), nullable=True)
    file_path = Column(String(MAX_PATH_LENGTH), nullable=False)
    generation_time_seconds = Column(FLOAT, nullable=True)
    created_at = Column(DateTime, default=func.now())

    template = relationship("CVTemplate", backref="generated_cvs")