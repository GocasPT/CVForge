from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.config import settings

MAX_NAME_LENGTH = 255
MAX_PATH_LENGTH = 500

# Database path
DATABASE_URL = settings.database_url
if not DATABASE_URL:
    raise ValueError(
        "`DATABASE_URL` environment variable is not set. Please set it to a valid database connection string."
    )

# Make SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

# Session Local (every session request/creation uses this)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis for SQLAlchemy models to inherit
Base = declarative_base()


def init_db():
    Base.metadata.create_all(bind=engine)


def delete_db():
    Base.metadata.drop_all(bind=engine)


def reset_db():
    delete_db()
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()