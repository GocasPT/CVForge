import pytest
import tempfile
from pathlib import Path
from typing import Generator
from backend.config.database import Base, SessionLocal, engine

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def clean_database():
    # Setup: Create fresh database
    Base.metadata.create_all(bind=engine)

    yield

    # Teardown: Clean up (optional, depending on isolation needs)
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

# Add the missing fixtures
@pytest.fixture
def temp_profile_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def profile_service(temp_profile_dir):
    from backend.services.profile_service import ProfileService
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