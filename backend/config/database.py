import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database path
SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL')

# Make SQLite engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session Local (every session request/creation uses this)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis for SQLAlchemy models to inherit
Base = declarative_base()

# Creates all tables registered in Base.metadata
Base.metadata.create_all(bind=engine)
