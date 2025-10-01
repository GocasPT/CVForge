import datetime

from sqlalchemy import Column, Integer, Text, String, DateTime
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.types import FLOAT

from backend.config.database import Base
from backend.models.cv_template import CVTemplate


class GeneratedCV(Base):
    __tablename__ = 'generated_cv'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, key=CVTemplate.id, nullable = False)
    job_description = Column(Text, nullable=False)
    selected_projects = Column(JSON, nullable=True)
    selected_experiences = Column(JSON, nullable=True)
    selected_summary_label = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=False)
    generation_time_seconds = Column(FLOAT, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))