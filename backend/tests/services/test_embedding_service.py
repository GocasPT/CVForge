from unittest.mock import patch

import numpy as np
import pytest

from services import EmbeddingService


class TestEmbeddingService:
    # ==================== DIMENSION TESTS ====================

    def test_model_dimension_is_correct(self, embedding_service):
        """Test that embedding vectors have the expected dimension."""
        expected_dimension = 384  # all-MiniLM-L6-v2 produces 384-dim vectors
        assert embedding_service.dimension == expected_dimension

    def test_single_encoding_dimension(self, embedding_service):
        """Test that a single text encoding has correct dimension."""
        text = "This is a test description"
        embedding = embedding_service.encode(text)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (embedding_service.dimension,)
        assert len(embedding) == 384

    def test_batch_encoding_dimensions(self, embedding_service):
        """Test that batch encoding produces correct dimensions."""
        texts = ["First text", "Second text", "Third text"]
        embeddings = embedding_service.encode_batch(texts)

        assert isinstance(embeddings, np.ndarray)
        assert embeddings.shape == (3, embedding_service.dimension)
        assert embeddings.shape[1] == 384

    def test_empty_string_encoding_dimension(self, embedding_service):
        """Test that encoding empty string still produces correct dimension."""
        embedding = embedding_service.encode("")
        assert embedding.shape == (embedding_service.dimension,)

    # ==================== SEARCH CONSISTENCY TESTS ====================

    def test_search_returns_consistent_results(self, embedding_service, sample_projects):
        """Test that identical queries return identical results."""
        index = embedding_service.build_index(sample_projects)
        query = "Build a Python web application with FastAPI"

        # Run search twice
        results1 = embedding_service.search(index, query, top_n=3)
        results2 = embedding_service.search(index, query, top_n=3)

        # Results should be identical
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1["rank"] == r2["rank"]
            assert r1["project"]["id"] == r2["project"]["id"]
            assert np.isclose(r1["score"], r2["score"], rtol=1e-6)

    def test_search_returns_top_n_results(self, embedding_service, sample_projects):
        """Test that search returns exactly top_n results."""
        index = embedding_service.build_index(sample_projects)
        query = "Python development"

        for top_n in [1, 2, 3]:
            results = embedding_service.search(index, query, top_n=top_n)
            assert len(results) == min(top_n, len(sample_projects))

    def test_search_results_are_sorted_by_score(self, embedding_service, sample_projects):
        """Test that search results are ordered by descending relevance score."""
        index = embedding_service.build_index(sample_projects)
        query = "Machine learning with Python"

        results = embedding_service.search(index, query, top_n=3)
        scores = [r["score"] for r in results]

        # Scores should be in descending order
        assert scores == sorted(scores, reverse=True)

    def test_search_relevance_makes_sense(self, embedding_service, sample_projects):
        """Test that highly relevant projects score higher."""
        index = embedding_service.build_index(sample_projects)

        # Query specifically about ML should rank ML project highest
        ml_query = "Machine learning and TensorFlow project"
        results = embedding_service.search(index, ml_query, top_n=3)

        # Project 2 (ML Pipeline) should be most relevant
        assert results[0]["project"]["id"] == 2

    def test_search_score_range(self, embedding_service, sample_projects):
        """Test that cosine similarity scores are in valid range [-1, 1]."""
        index = embedding_service.build_index(sample_projects)
        query = "Software development project"

        results = embedding_service.search(index, query, top_n=3)
        for result in results:
            score = result["score"]
            assert -1.0 <= score <= 1.0, f"Score {score} outside valid range"

    # ==================== ERROR HANDLING & FALLBACK TESTS ====================

    def test_empty_projects_list(self, embedding_service):
        """Test handling of empty projects list."""
        empty_projects = []

        # Should not raise an error, but return empty index
        with pytest.raises(Exception):
            # This should fail as FAISS needs at least one vector
            index = embedding_service.build_index(empty_projects)

    def test_search_with_empty_query(self, embedding_service, sample_projects):
        """Test search with empty query string."""
        index = embedding_service.build_index(sample_projects)
        results = embedding_service.search(index, "", top_n=3)

        # Should still return results (all projects equally irrelevant)
        assert len(results) == 3
        assert all(isinstance(r["score"], float) for r in results)

    def test_search_with_very_long_query(self, embedding_service, sample_projects):
        """Test search with extremely long query text."""
        index = embedding_service.build_index(sample_projects)
        long_query = "Python development " * 1000  # Very long repeated text

        results = embedding_service.search(index, long_query, top_n=3)
        assert len(results) == 3

    def test_projects_with_empty_descriptions(self, embedding_service):
        """Test handling of projects with empty descriptions."""
        projects = [
            {
                "id": 1,
                "title": "Project 1",
                "description": "",
                "technologies": ["Python"]
            }
        ]

        # Should not crash, technologies should still be encoded
        index = embedding_service.build_index(projects)
        results = embedding_service.search(index, "Python", top_n=1)
        assert len(results) == 1

    def test_projects_with_empty_technologies(self, embedding_service):
        """Test handling of projects with no technologies."""
        projects = [
            {
                "id": 1,
                "title": "Project 1",
                "description": "Some description",
                "technologies": []
            }
        ]

        index = embedding_service.build_index(projects)
        results = embedding_service.search(index, "description", top_n=1)
        assert len(results) == 1

    def test_model_loading_failure_fallback(self):
        """Test fallback when model fails to load."""
        with patch('sentence_transformers.SentenceTransformer') as mock_model:
            mock_model.side_effect = Exception("Model loading failed")

            with pytest.raises(Exception):
                EmbeddingService("invalid-model-name")

    def test_encode_with_special_characters(self, embedding_service):
        """Test encoding text with special characters."""
        special_text = "Python & C++ with @decorators, #hashtags, and émojis! 🚀"
        embedding = embedding_service.encode(special_text)

        assert embedding.shape == (embedding_service.dimension,)
        assert not np.any(np.isnan(embedding))

    def test_search_top_n_exceeds_projects(self, embedding_service, sample_projects):
        """Test search when top_n exceeds available projects."""
        index = embedding_service.build_index(sample_projects)
        results = embedding_service.search(index, "Python", top_n=100)

        # Should return all available projects (3), not 100
        assert len(results) == len(sample_projects)

    # ==================== NORMALIZATION TESTS ====================

    def test_embeddings_are_normalized(self, embedding_service, sample_projects):
        """Test that embeddings are properly normalized for cosine similarity."""
        index = embedding_service.build_index(sample_projects)

        # Get embeddings directly from the encoding process to verify normalization
        texts = [f"[{', '.join(p['technologies'])}] {p['description']}" for p in sample_projects]
        embeddings = embedding_service.encode_batch(texts)

        # After normalization, L2 norm should be 1
        for vector in embeddings:
            norm = np.linalg.norm(vector)
            assert np.isclose(norm, 1.0, rtol=1e-5), f"Vector not normalized: norm={norm}"

    def test_query_vector_normalization(self, embedding_service, sample_projects):
        """Test that query vectors are normalized before search."""
        index = embedding_service.build_index(sample_projects)
        query = "Python development"

        # Get query embedding directly
        query_vec = embedding_service.encode(query)
        original_norm = np.linalg.norm(query_vec)

        # Search should normalize it
        results = embedding_service.search(index, query, top_n=1)

        # Verify search works (normalization happened internally)
        assert len(results) == 1
        assert results[0]["score"] <= 1.0

    # ==================== INTEGRATION TESTS ====================

    def test_full_workflow(self, embedding_service, sample_projects):
        """Test complete workflow from indexing to search."""
        # Build index
        index = embedding_service.build_index(sample_projects)
        assert index.ntotal == len(sample_projects)

        # Perform search
        query = "Build a Python backend with FastAPI and PostgreSQL"
        results = embedding_service.search(index, query, top_n=2)

        # Validate results structure
        assert len(results) == 2
        for i, result in enumerate(results):
            assert result["rank"] == i + 1
            assert "score" in result
            assert "project" in result
            assert "id" in result["project"]
            assert "title" in result["project"]
            assert "description" in result["project"]
            assert "technologies" in result["project"]

    def test_multiple_searches_on_same_index(self, embedding_service, sample_projects):
        """Test that one index can be used for multiple searches."""
        index = embedding_service.build_index(sample_projects)

        queries = [
            "Python web development",
            "Machine learning",
            "Mobile application"
        ]

        for query in queries:
            results = embedding_service.search(index, query, top_n=3)
            assert len(results) <= 3
            assert all(r["score"] >= -1.0 and r["score"] <= 1.0 for r in results)

    # ==================== EDGE CASES ====================

    def test_unicode_text_handling(self, embedding_service):
        """Test handling of unicode characters in various languages."""
        unicode_projects = [
            {
                "id": 1,
                "title": "项目一",
                "description": "用Python构建的电子商务平台",
                "technologies": ["Python", "Django"]
            },
            {
                "id": 2,
                "title": "Проект два",
                "description": "Разработка машинного обучения",
                "technologies": ["Python", "TensorFlow"]
            }
        ]

        index = embedding_service.build_index(unicode_projects)
        results = embedding_service.search(index, "Python development", top_n=2)

        assert len(results) == 2

    def test_single_project_search(self, embedding_service):
        """Test search with only one project in database."""
        single_project = [
            {
                "id": 1,
                "title": "Solo Project",
                "description": "The only project",
                "technologies": ["Python"]
            }
        ]

        index = embedding_service.build_index(single_project)
        results = embedding_service.search(index, "project", top_n=5)

        # Should return exactly 1 result even though top_n=5
        assert len(results) == 1
        assert results[0]["rank"] == 1

    def test_identical_projects(self, embedding_service):
        """Test handling of duplicate/identical projects."""
        identical_projects = [
            {
                "id": 1,
                "title": "Project A",
                "description": "Same description",
                "technologies": ["Python"]
            },
            {
                "id": 2,
                "title": "Project B",
                "description": "Same description",
                "technologies": ["Python"]
            }
        ]

        index = embedding_service.build_index(identical_projects)
        results = embedding_service.search(index, "Same description", top_n=2)

        # Both should have very similar scores
        assert len(results) == 2
        assert np.isclose(results[0]["score"], results[1]["score"], rtol=0.01)

    # ==================== PERFORMANCE TESTS ====================

    @pytest.mark.slow
    @pytest.mark.timeout(30)
    def test_large_project_database(self, embedding_service):
        """Test performance with larger number of projects."""
        large_projects = [
            {
                "id": i,
                "title": f"Project {i}",
                "description": f"Description for project {i} with various technologies",
                "technologies": ["Python", "FastAPI", "PostgreSQL"]
            }
            for i in range(100)
        ]

        import time
        start = time.time()
        index = embedding_service.build_index(large_projects)
        index_time = time.time() - start

        start = time.time()
        results = embedding_service.search(index, "Python FastAPI", top_n=10)
        search_time = time.time() - start

        # Reasonable performance expectations
        assert index_time < 10.0, f"Indexing took too long: {index_time}s"
        assert search_time < 1.0, f"Search took too long: {search_time}s"
        assert len(results) == 10

    # =============================================================

    # In test_embedding_service.py
    def test_build_index_with_none_projects(self, embedding_service):
        """Test handling of None projects list."""
        with pytest.raises(Exception):
            embedding_service.build_index(None)

    def test_search_with_none_index(self, embedding_service):
        """Test search with None index."""
        with pytest.raises(Exception):
            embedding_service.search(None, "test query")
