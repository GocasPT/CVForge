from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Text, JSON, DateTime, func
from sqlalchemy.sql.sqltypes import Date
from models import Base
from config import MAX_NAME_LENGTH

class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    position: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    company: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(MAX_NAME_LENGTH), nullable=True)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technologies: Mapped[list] = mapped_column(JSON, nullable=False)
    achievements: Mapped[list] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())