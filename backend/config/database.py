from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

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
    } if DATABASE_URL.startswith("sqlite") else {},
    future=True,
)

# Session Local (every session request/creation uses this)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)

def get_db():
    return SessionLocal