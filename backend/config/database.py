import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

MAX_NAME_LENGTH = 255
MAX_PATH_LENGTH = 500

# Database path
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Make SQLite engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session Local (every session request/creation uses this)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis for SQLAlchemy models to inherit
Base = declarative_base()

def init_db():
    # Creates all tables registered in Base.metadata
    Base.metadata.create_all(bind=engine)
