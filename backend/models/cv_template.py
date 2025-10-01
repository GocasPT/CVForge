import datetime

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime

from backend.config.database import Base


class CVTemplate(Base):
    __tablename__ = 'cv_templates'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=False)
    preview_image = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
