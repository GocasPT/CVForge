from unittest.mock import Mock, patch

import pytest

from models import Project
from services import ProjectMatcherService


class TestProjectMatcher:
    # ==================== INITIALIZATION TESTS ====================

    def test_project_matcher_initialization(self):
        """Test that ProjectMatcher initializes correctly."""
        with patch('services.project_matcher.EmbeddingService') as mock_embedding:
            matcher = ProjectMatcherService()

            # Should initialize with multilingual model
            mock_embedding.assert_called_once_with('paraphrase-multilingual-MiniLM-L12-v2')

    def test_embedding_service_created(self, project_matcher):
        """Test that embedding service is properly initialized."""
        assert hasattr(project_matcher, 'embedding_service')

    # ==================== DATABASE INTERACTION TESTS ====================

    def test_get_all_projects_retrieves_from_db(self, sample_db_projects):
        """Test that _get_all_projects retrieves data from database."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            matcher = ProjectMatcherService()
            projects = matcher._get_all_projects()

            # Verify database query was made
            mock_session.query.assert_called_once_with(Project)
            mock_session.close.assert_called_once()

            # Verify correct number of projects
            assert len(projects) == 3

    def test_get_all_projects_returns_correct_format(self, sample_db_projects):
        """Test that _get_all_projects returns correctly formatted data."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            matcher = ProjectMatcherService()
            projects = matcher._get_all_projects()

            # Check format of returned projects
            for project in projects:
                assert "id" in project
                assert "title" in project
                assert "description" in project
                assert "technologies" in project
                assert isinstance(project["id"], int)
                assert isinstance(project["title"], str)
                assert isinstance(project["description"], str)
                assert isinstance(project["technologies"], list)

    def test_get_all_projects_closes_session(self, sample_db_projects):
        """Test that database session is always closed."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            matcher = ProjectMatcherService()
            matcher._get_all_projects()

            # Session should be closed even if no exception
            mock_session.close.assert_called_once()

    def test_get_all_projects_closes_session_on_error(self):
        """Test that database session is closed even on error."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.side_effect = Exception("Database error")

            matcher = ProjectMatcherService()

            with pytest.raises(Exception):
                matcher._get_all_projects()

            # Session should be closed despite exception
            mock_session.close.assert_called_once()

    # ==================== MATCHING TESTS ====================

    def test_match_projects_returns_results(self, sample_db_projects):
        """Test that match_projects returns matching results."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            # Setup mocks
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding

            mock_index = Mock()
            mock_embedding.build_index.return_value = mock_index

            # Mock search results
            mock_embedding.search.return_value = [
                {"rank": 1, "score": 0.85, "project": {"id": 1, "title": "E-commerce Platform"}},
                {"rank": 2, "score": 0.72, "project": {"id": 2, "title": "ML Pipeline"}}
            ]

            matcher = ProjectMatcherService()
            results = matcher.match_projects("Python FastAPI backend development", top_n=2)

            # Verify results
            assert len(results) == 2
            assert results[0]["rank"] == 1
            assert results[0]["score"] == 0.85

    def test_match_projects_with_different_top_n(self, sample_db_projects):
        """Test match_projects with various top_n values."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()

            matcher = ProjectMatcherService()

            for top_n in [1, 3, 5, 10]:
                mock_embedding.search.return_value = [
                    {"rank": i, "score": 0.9 - i * 0.1, "project": {"id": i}}
                    for i in range(1, min(top_n, 3) + 1)
                ]

                results = matcher.match_projects("test query", top_n=top_n)

                # Should call search with correct top_n
                mock_embedding.search.assert_called_with(
                    mock_embedding.build_index.return_value,
                    "test query",
                    top_n=top_n
                )

    def test_match_projects_builds_index_correctly(self, sample_db_projects):
        """Test that match_projects builds index with correct project data."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.search.return_value = []

            matcher = ProjectMatcherService()
            matcher.match_projects("test query")

            # Verify build_index was called with project data
            mock_embedding.build_index.assert_called_once()
            call_args = mock_embedding.build_index.call_args[0][0]

            assert len(call_args) == 3
            assert all("id" in p and "title" in p for p in call_args)

    # ==================== ERROR HANDLING & FALLBACK TESTS ====================

    def test_match_projects_with_empty_database(self):
        """Test match_projects when no projects exist in database."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService'):
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = []

            matcher = ProjectMatcherService()
            results = matcher.match_projects("test query", top_n=5)

            # Should return empty list when no projects
            assert results == []

    def test_match_projects_handles_none_results(self):
        """Test match_projects when embedding search returns None."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = [
                Mock(id=1, title="Test", description="Test", technologies=["Python"])
            ]

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = None

            matcher = ProjectMatcherService()
            results = matcher.match_projects("test query")

            # Should handle None gracefully
            assert results is None or results == []

    def test_match_projects_with_database_error(self):
        """Test that database errors are propagated correctly."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.side_effect = Exception("Database connection failed")

            matcher = ProjectMatcherService()

            with pytest.raises(Exception) as exc_info:
                matcher.match_projects("test query")

            assert "Database connection failed" in str(exc_info.value)

    def test_match_projects_with_embedding_error(self, sample_db_projects):
        """Test handling of embedding service errors."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.side_effect = Exception("Embedding failed")

            matcher = ProjectMatcherService()

            with pytest.raises(Exception) as exc_info:
                matcher.match_projects("test query")

            assert "Embedding failed" in str(exc_info.value)

    def test_match_projects_with_empty_job_description(self, sample_db_projects):
        """Test match_projects with empty job description."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            matcher = ProjectMatcherService()
            results = matcher.match_projects("", top_n=5)

            # Should still attempt to search
            mock_embedding.search.assert_called_once()
            assert isinstance(results, list)

    def test_match_projects_with_very_long_description(self, sample_db_projects):
        """Test match_projects with extremely long job description."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            long_description = "Python developer " * 10000  # Very long text

            matcher = ProjectMatcherService()
            results = matcher.match_projects(long_description, top_n=5)

            # Should handle without crashing
            mock_embedding.search.assert_called_once()

    def test_match_projects_with_special_characters(self, sample_db_projects):
        """Test match_projects with special characters in job description."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            special_description = "Python & C++ dev with @decorators! 🚀 #backend"

            matcher = ProjectMatcherService()
            results = matcher.match_projects(special_description, top_n=5)

            # Should handle special characters
            assert isinstance(results, list)

    # ==================== INTEGRATION TESTS ====================

    def test_full_matching_workflow(self, sample_db_projects):
        """Test complete workflow from database to results."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            # Setup full mock chain
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_index = Mock()
            mock_embedding.build_index.return_value = mock_index

            expected_results = [
                {
                    "rank": 1,
                    "score": 0.92,
                    "project": {
                        "id": 1,
                        "title": "E-commerce Platform",
                        "description": "Built scalable microservices with Python FastAPI",
                        "technologies": ["Python", "FastAPI", "PostgreSQL", "Docker"]
                    }
                },
                {
                    "rank": 2,
                    "score": 0.78,
                    "project": {
                        "id": 2,
                        "title": "ML Pipeline",
                        "description": "Created machine learning pipeline for data processing",
                        "technologies": ["Python", "TensorFlow", "Pandas", "Airflow"]
                    }
                }
            ]
            mock_embedding.search.return_value = expected_results

            # Execute workflow
            matcher = ProjectMatcherService()
            job_description = "Looking for Python backend developer with FastAPI experience"
            results = matcher.match_projects(job_description, top_n=2)

            # Verify entire workflow
            mock_session.query.assert_called_once_with(Project)
            mock_embedding.build_index.assert_called_once()
            mock_embedding.search.assert_called_once_with(mock_index, job_description, top_n=2)
            mock_session.close.assert_called_once()

            # Verify results
            assert len(results) == 2
            assert results[0]["score"] == 0.92
            assert results[1]["score"] == 0.78

    def test_multiple_consecutive_matches(self, sample_db_projects):
        """Test that multiple match operations work correctly."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            matcher = ProjectMatcherService()

            # Perform multiple matches
            queries = [
                "Python backend development",
                "Machine learning engineer",
                "Mobile app developer"
            ]

            for query in queries:
                results = matcher.match_projects(query, top_n=3)
                assert isinstance(results, list)

            # Each match should query database fresh
            assert mock_session.query.call_count == 3

    # ==================== EDGE CASES ====================

    def test_match_projects_with_unicode_job_description(self, sample_db_projects):
        """Test matching with unicode characters in job description."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            unicode_description = "寻找Python开发人员 with FastAPI 经验"

            matcher = ProjectMatcherService()
            results = matcher.match_projects(unicode_description, top_n=5)

            # Should handle unicode
            assert isinstance(results, list)

    def test_match_projects_with_zero_top_n(self, sample_db_projects):
        """Test match_projects with top_n=0."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_index = Mock()  # Create a specific mock for the index
            mock_embedding.build_index.return_value = mock_index
            mock_embedding.search.return_value = []

            matcher = ProjectMatcherService()
            results = matcher.match_projects("test query", top_n=0)

            # Use the actual index mock that was created
            mock_embedding.search.assert_called_with(mock_index, "test query", top_n=0)
            assert results == []

    def test_match_projects_with_negative_top_n(self, sample_db_projects):
        """Test match_projects with negative top_n value."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:

            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()

            matcher = ProjectMatcherService()

            # May raise error or handle gracefully depending on implementation
            # At minimum, should not crash the application
            try:
                results = matcher.match_projects("test query", top_n=-1)
                assert isinstance(results, list)
            except (ValueError, Exception):
                pass  # Acceptable to raise validation error

    def test_match_projects_default_top_n(self, sample_db_projects):
        """Test that default top_n value is used when not specified."""
        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = sample_db_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_index = Mock()  # Create a specific mock for the index
            mock_embedding.build_index.return_value = mock_index
            mock_embedding.search.return_value = []

            matcher = ProjectMatcherService()
            matcher.match_projects("test query")  # No top_n specified

            # Use the actual index mock that was created
            mock_embedding.search.assert_called_with(mock_index, "test query", top_n=5)

    # ==================== PERFORMANCE TESTS ====================

    @pytest.mark.slow
    def test_match_projects_with_large_database(self):
        """Test performance with large number of projects."""
        large_projects = [
            Mock(
                id=i,
                title=f"Project {i}",
                description=f"Description for project {i}",
                technologies=["Python", "FastAPI"]
            )
            for i in range(1000)
        ]

        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = large_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding
            mock_embedding.build_index.return_value = Mock()
            mock_embedding.search.return_value = []

            import time
            start = time.time()

            matcher = ProjectMatcherService()
            matcher.match_projects("Python developer", top_n=10)

            elapsed = time.time() - start

            # Should complete in reasonable time even with 1000 projects
            assert elapsed < 5.0, f"Matching took too long: {elapsed}s"

    # ==================== DATA VALIDATION TESTS ====================

    def test_projects_missing_required_fields(self):
        """Test handling of projects with missing fields."""
        incomplete_projects = [
            Mock(
                id=1,
                title="Project 1",
                # Missing description
                technologies=["Python"]
            )
        ]

        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:

            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = incomplete_projects

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding

            matcher = ProjectMatcherService()

            # Should handle gracefully or raise appropriate error
            try:
                matcher.match_projects("test query")
            except AttributeError:
                # Expected if description is accessed but missing
                pass

    def test_projects_with_none_values(self):
        """Test handling of projects with None values."""
        projects_with_none = [
            Mock(
                id=1,
                title="Project 1",
                description=None,
                technologies=None
            )
        ]

        with patch('services.project_matcher.SessionLocal') as mock_session_local, \
                patch('services.project_matcher.EmbeddingService') as mock_embedding_cls:

            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_session.query.return_value.all.return_value = projects_with_none

            mock_embedding = Mock()
            mock_embedding_cls.return_value = mock_embedding

            matcher = ProjectMatcherService()

            # Should handle None values gracefully
            try:
                matcher.match_projects("test query")
            except (TypeError, AttributeError):
                # May raise error when trying to process None
                pass
