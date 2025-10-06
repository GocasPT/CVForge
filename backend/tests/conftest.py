import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pytest
from sqlalchemy.orm import sessionmaker

from services import EmbeddingService, ProjectMatcherService, ProfileService


# ==================== PYTEST CONFIGURATION ====================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ==================== TEMPORARY DIRECTORY FIXTURES ====================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_db_path(temp_dir):
    """Create a temporary database path."""
    db_path = temp_dir / "test_cvforge.db"
    yield str(db_path)


# ==============================================================

@pytest.fixture
def temp_profile_dir(temp_dir):
    """Create a temporary directory for profile tests."""
    profile_dir = temp_dir / "profile"
    profile_dir.mkdir()
    yield profile_dir


@pytest.fixture
def profile_service(temp_profile_dir):
    """Create a ProfileService instance with temporary path."""
    profile_path = temp_profile_dir / "profile.json"
    return ProfileService(profile_path=str(profile_path))


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {
        "personal": {
            "full_name": "Test User",
            "email": "test@example.com",
            "location": "Test City"
        },
        "skills": {
            "programming": ["Python", "JavaScript"],
            "tools": ["Docker", "Git"]
        }
    }


@pytest.fixture
def temp_db(temp_db_path):
    """Create a temporary database with schema."""

    # Ensure the database URL is set to our temporary path
    import os
    original_db_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = f"sqlite:///{temp_db_path}"

    # Re-import to get the new engine with updated DATABASE_URL
    import importlib
    from config import database
    importlib.reload(database)

    # Use the reloaded module
    engine = database.engine
    Base = database.Base
    SessionLocal = database.SessionLocal

    # Create all tables - this should create the database file
    Base.metadata.create_all(bind=engine)

    # Create a test session local
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    yield engine, TestSessionLocal, temp_db_path

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    # Restore original DATABASE_URL
    if original_db_url:
        os.environ['DATABASE_URL'] = original_db_url
    elif 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']


@pytest.fixture
def db_session(temp_db):
    """Create a database session for testing."""
    engine, TestSessionLocal, _ = temp_db
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


# ==============================================================

# ==================== PROJECT DATA FIXTURES ====================

@pytest.fixture
def sample_project_dict():
    """Single sample project as dictionary."""
    return {
        "id": 1,
        "title": "E-commerce Platform",
        "description": "Built scalable microservices architecture with Python FastAPI and PostgreSQL",
        "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        "role": "Backend Developer",
        "duration": "6 months"
    }


@pytest.fixture
def sample_projects_list():
    """Multiple sample projects for testing."""
    return [
        {
            "id": 1,
            "title": "E-commerce Platform",
            "description": "Built scalable microservices architecture with Python FastAPI and PostgreSQL",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"]
        },
        {
            "id": 2,
            "title": "Machine Learning Pipeline",
            "description": "Developed end-to-end ML pipeline for sentiment analysis using TensorFlow and Airflow",
            "technologies": ["Python", "TensorFlow", "Pandas", "Apache Airflow", "Scikit-learn"]
        },
        {
            "id": 3,
            "title": "Mobile Banking App",
            "description": "Created secure mobile banking application with biometric authentication",
            "technologies": ["React Native", "Node.js", "MongoDB", "AWS", "Firebase"]
        },
        {
            "id": 4,
            "title": "Data Analytics Dashboard",
            "description": "Built real-time analytics dashboard for business intelligence",
            "technologies": ["React", "D3.js", "Python", "Flask", "Elasticsearch"]
        },
        {
            "id": 5,
            "title": "DevOps Automation Suite",
            "description": "Automated CI/CD pipelines and infrastructure management",
            "technologies": ["Kubernetes", "Terraform", "Jenkins", "Docker", "AWS"]
        }
    ]


@pytest.fixture
def sample_job_descriptions():
    """Sample job descriptions for testing matching."""
    return {
        "backend": "We are looking for a Backend Engineer with strong Python and FastAPI experience. "
                   "Must have experience with PostgreSQL, Docker, and building scalable microservices.",

        "ml_engineer": "Seeking Machine Learning Engineer proficient in TensorFlow and PyTorch. "
                       "Experience with MLOps, data pipelines, and model deployment required.",

        "fullstack": "Full-stack developer needed with React and Node.js experience. "
                     "Should be comfortable with both frontend and backend development.",

        "devops": "DevOps Engineer position requiring Kubernetes, Docker, and AWS expertise. "
                  "Infrastructure as Code and CI/CD pipeline experience essential.",

        "mobile": "Mobile App Developer with React Native experience. "
                  "Knowledge of mobile security and authentication flows preferred."
    }


# ==================== MOCK DATABASE FIXTURES ====================

@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy database session."""
    session = Mock()
    session.query = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_project_orm():
    """Create a mock Project ORM object."""

    def _create_project(**kwargs):
        project = Mock()
        project.id = kwargs.get('id', 1)
        project.title = kwargs.get('title', 'Test Project')
        project.description = kwargs.get('description', 'Test description')
        project.technologies = kwargs.get('technologies', ['Python'])
        project.role = kwargs.get('role', 'Developer')
        project.duration = kwargs.get('duration', '3 months')
        return project

    return _create_project


# ==================== EMBEDDING SERVICE FIXTURES ====================

@pytest.fixture
def embedding_service():
    """Create a fresh EmbeddingService instance for each test."""
    return EmbeddingService(model_name="sentence-transformers/all-MiniLM-L6-v2")


@pytest.fixture
def sample_projects():
    """Sample project data for testing."""
    return [
        {
            "id": 1,
            "title": "E-commerce Platform",
            "description": "Built a scalable e-commerce platform with microservices architecture",
            "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"]
        },
        {
            "id": 2,
            "title": "Machine Learning Pipeline",
            "description": "Developed end-to-end ML pipeline for sentiment analysis",
            "technologies": ["Python", "TensorFlow", "Scikit-learn", "Apache Airflow"]
        },
        {
            "id": 3,
            "title": "Mobile Banking App",
            "description": "Created secure mobile banking application with biometric authentication",
            "technologies": ["React Native", "Node.js", "MongoDB", "AWS"]
        }
    ]


@pytest.fixture
def mock_embedding_model():
    """Mock sentence-transformers model."""
    model = Mock()
    model.get_sentence_embedding_dimension.return_value = 384

    def mock_encode(text):
        # Return deterministic embeddings based on text length
        np.random.seed(len(text) if isinstance(text, str) else 42)
        return np.random.randn(384).astype(np.float32)

    def mock_encode_batch(texts):
        embeddings = np.array([mock_encode(text) for text in texts])
        return embeddings

    model.encode = Mock(side_effect=mock_encode)
    model.encode_batch = Mock(side_effect=mock_encode_batch)

    return model


@pytest.fixture
def mock_faiss_index():
    """Mock FAISS index."""
    index = Mock()
    index.ntotal = 5  # Simulate 5 indexed items
    index.d = 384  # Dimension

    def mock_search(query_vec, k):
        # Return mock scores and indices
        n_results = min(k, index.ntotal)
        scores = np.array([[0.9 - i * 0.1 for i in range(n_results)]])
        indices = np.array([[i for i in range(n_results)]])
        return scores, indices

    index.search = Mock(side_effect=mock_search)
    index.add = Mock()

    return index


# ==============================================================================

@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = Mock()
    return session


@pytest.fixture
def sample_db_projects():
    """Create sample Project ORM objects."""
    projects = [
        Mock(
            id=1,
            title="E-commerce Platform",
            description="Built scalable microservices with Python FastAPI",
            technologies=["Python", "FastAPI", "PostgreSQL", "Docker"]
        ),
        Mock(
            id=2,
            title="ML Pipeline",
            description="Created machine learning pipeline for data processing",
            technologies=["Python", "TensorFlow", "Pandas", "Airflow"]
        ),
        Mock(
            id=3,
            title="Mobile App",
            description="Developed React Native mobile application",
            technologies=["React Native", "Node.js", "MongoDB"]
        )
    ]
    return projects


@pytest.fixture
def project_matcher():
    """Create ProjectMatcher instance with mocked dependencies."""
    with patch('services.project_matcher.SessionLocal') as mock_session_local, \
            patch('services.project_matcher.EmbeddingService') as mock_embedding_service:
        matcher = ProjectMatcherService()
        matcher.mock_session = mock_session_local
        matcher.mock_embedding = mock_embedding_service
        return matcher


# ==================== EMBEDDING SERVICE WITH REAL BEHAVIOR ====================

@pytest.fixture
def deterministic_embedding_service():
    """
    Create an embedding service with deterministic behavior for testing.
    Uses actual sentence-transformers but with fixed random seed.
    """
    with patch('embedding_service.SentenceTransformer') as mock_st:
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384

        def deterministic_encode(text):
            # Create deterministic embeddings based on text hash
            np.random.seed(hash(text) % 2 ** 32)
            embedding = np.random.randn(384).astype(np.float32)
            return embedding

        def deterministic_encode_batch(texts):
            return np.array([deterministic_encode(t) for t in texts])

        mock_model.encode = deterministic_encode
        mock_model.encode_batch = deterministic_encode_batch
        mock_st.return_value = mock_model

        from backend.services import EmbeddingService
        return EmbeddingService("test-model")


# ==================== HELPER FUNCTIONS ====================

@pytest.fixture
def create_mock_search_results():
    """Factory fixture for creating mock search results."""

    def _create_results(n_results=3, base_score=0.9, projects=None):
        if projects is None:
            projects = [
                {"id": i, "title": f"Project {i}", "description": f"Description {i}"}
                for i in range(1, n_results + 1)
            ]

        results = []
        for i, project in enumerate(projects[:n_results]):
            results.append({
                "rank": i + 1,
                "score": base_score - i * 0.1,
                "project": project
            })
        return results

    return _create_results


@pytest.fixture
def assert_embeddings_normalized():
    """Helper to assert that embeddings are normalized."""

    def _assert_normalized(embeddings, tolerance=1e-5):
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)

        norms = np.linalg.norm(embeddings, axis=1)
        assert np.allclose(norms, 1.0, rtol=tolerance), \
            f"Embeddings not normalized: norms={norms}"

    return _assert_normalized


@pytest.fixture
def assert_valid_search_results():
    """Helper to validate search result structure."""

    def _assert_valid(results):
        assert isinstance(results, list), "Results must be a list"

        for i, result in enumerate(results):
            assert "rank" in result, f"Result {i} missing 'rank'"
            assert "score" in result, f"Result {i} missing 'score'"
            assert "project" in result, f"Result {i} missing 'project'"

            assert result["rank"] == i + 1, f"Rank should be {i + 1}, got {result['rank']}"
            assert isinstance(result["score"], (int, float)), "Score must be numeric"
            assert -1.0 <= result["score"] <= 1.0, f"Score {result['score']} out of range"

            project = result["project"]
            assert "id" in project, "Project missing 'id'"
            assert "title" in project, "Project missing 'title'"
            assert "description" in project, "Project missing 'description'"

    return _assert_valid


# ==================== PARAMETRIZED TEST DATA ====================

@pytest.fixture
def edge_case_texts():
    """Various edge case text inputs for testing."""
    return {
        "empty": "",
        "whitespace": "   ",
        "single_char": "a",
        "very_long": "test " * 10000,
        "unicode": "Test with émojis 🚀 and Chinese 中文 and Arabic العربية",
        "special_chars": "!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`",
        "newlines": "Line 1\nLine 2\nLine 3\n\n\nLine 4",
        "tabs": "Col1\tCol2\tCol3",
        "mixed": "Normal text with 中文 and émojis 🎉 and\nnewlines\tand\ttabs!",
        "html": "<html><body><p>HTML content</p></body></html>",
        "code": "def function():\n    return 'test'",
        "numbers": "1234567890",
        "repeated": "test" * 100
    }


# ==================== PERFORMANCE MONITORING ====================

@pytest.fixture
def performance_timer():
    """Context manager for timing test execution."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, *args):
            self.end_time = time.time()
            self.elapsed = self.end_time - self.start_time

        def assert_faster_than(self, max_seconds, message=None):
            assert self.elapsed < max_seconds, \
                message or f"Operation took {self.elapsed:.3f}s, expected < {max_seconds}s"

    return Timer


# ==================== CLEANUP ====================

@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Automatically cleanup after each test."""
    yield
    # Any cleanup code here runs after each test
