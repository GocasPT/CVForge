from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, func
from config import Base, MAX_NAME_LENGTH, MAX_PATH_LENGTH

class CVTemplate(Base):
    __tablename__ = 'cv_templates'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(MAX_NAME_LENGTH), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(MAX_PATH_LENGTH), nullable=False)
    preview_image = Column(String(MAX_PATH_LENGTH), nullable=True)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=func.now())
