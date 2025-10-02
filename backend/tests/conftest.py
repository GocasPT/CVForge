import os
import tempfile
from pathlib import Path
from typing import Generator, Tuple

import pytest
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

from config import init_db
from services import ProfileService


@pytest.fixture
def temp_db() -> Generator[Tuple[Engine, sessionmaker, str], None, None]:
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name

    db_url = f"sqlite:///{db_path}"
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Create all tables
    init_db()

    try:
        yield test_engine, TestSessionLocal, db_path
    finally:
        # Cleanup
        test_engine.dispose()
        try:
            os.unlink(db_path)
        except (PermissionError, FileNotFoundError):
            pass

@pytest.fixture
def db_session(temp_db) -> Generator[Session, None, None]:
    engine, TestSessionLocal, _ = temp_db
    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def clean_database(temp_db):
    engine, TestSessionLocal, _ = temp_db
    yield engine, TestSessionLocal

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def temp_profile_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def profile_service(temp_profile_dir):
    profile_path = temp_profile_dir / "profile.json"
    return ProfileService(profile_path=str(profile_path))

@pytest.fixture
def sample_profile_data() -> dict:
    return {
        "personal": {
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+351 912 345 678",
            "location": "Test City, Portugal"
        },
        "professional": {
            "current_role": "Test Developer",
            "experience_years": 3
        },
        "skills": {
            "programming_languages": ["Python", "JavaScript"],
            "frameworks": ["FastAPI", "Vue.js"]
        },
        "preferences": {
            "default_summary": "backend",
            "max_projects_per_cv": 5
        }
    }