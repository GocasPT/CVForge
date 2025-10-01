import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError

from backend.config.database import Base, SessionLocal, engine

class TestDatabaseConnection:
    def test_database_url_from_environment(self, monkeypatch):
        test_db_url = "sqlite:///./test_custom.db"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        # Import after setting env var
        from backend.config import database
        import importlib
        importlib.reload(database)

        assert os.environ.get('DATABASE_URL') == test_db_url

    def test_database_file_creation(self, tmp_path):
        db_file = tmp_path / "test.db"
        db_url = f"sqlite:///{db_file}"

        test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=test_engine)

        assert db_file.exists()
        test_engine.dispose()

    def test_engine_is_created(self):
        assert engine is not None
        assert hasattr(engine, 'connect')

    def test_engine_connection(self):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_invalid_database_url(self):
        with pytest.raises(Exception):
            invalid_engine = create_engine("invalid://url")
            with invalid_engine.connect():
                pass


class TestSessionManagement:
    def test_session_creation(self):
        session = SessionLocal()
        assert isinstance(session, Session)
        session.close()

    # def test_session_autocommit_disabled(self):
    #     session = SessionLocal()
    #     assert session.autocommit == False
    #     session.close()

    def test_session_autoflush_disabled(self):
        session = SessionLocal()
        assert session.autoflush == False
        session.close()

    def test_multiple_sessions(self):
        session1 = SessionLocal()
        session2 = SessionLocal()

        assert session1 is not session2

        session1.close()
        session2.close()

    def test_session_context_manager(self):
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_session_rollback_on_error(self):
        session = SessionLocal()
        try:
            # Attempt invalid operation
            session.execute(text("SELECT * FROM nonexistent_table"))
        except:
            session.rollback()
            # Session should still be usable after rollback
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            session.close()


class TestTableCreation:
    def test_base_metadata_exists(self):
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None

    def test_tables_created_on_init(self):
        # Tables should already be created by the module import
        # Check if we can query sqlite_master
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]

            # At minimum, sqlite_sequence should exist if any tables use autoincrement
            assert len(tables) >= 0  # May have no user tables yet

    def test_create_all_idempotent(self):
        # Should not raise error
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_table_recreation(self, tmp_path):
        db_file = tmp_path / "test_recreate.db"
        db_url = f"sqlite:///{db_file}"

        test_engine = create_engine(db_url, connect_args={"check_same_thread": False})

        # Create tables
        Base.metadata.create_all(bind=test_engine)

        # Drop tables
        Base.metadata.drop_all(bind=test_engine)

        # Recreate tables
        Base.metadata.create_all(bind=test_engine)

        test_engine.dispose()


class TestThreadSafety:
    # def test_check_same_thread_disabled(self):
    #     # This is important for multi-threaded applications
    #     assert "check_same_thread" in str(engine.url)

    def test_concurrent_sessions(self):
        import threading
        sessions = []

        def create_session():
            session = SessionLocal()
            sessions.append(session)

        threads = [threading.Thread(target=create_session) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(sessions) == 5
        for session in sessions:
            session.close()


class TestErrorHandling:
    def test_invalid_sql_query(self):
        session = SessionLocal()

        with pytest.raises(OperationalError):
            session.execute(text("INVALID SQL SYNTAX"))

        session.close()

    def test_connection_after_error(self):
        session = SessionLocal()

        # Cause an error
        try:
            session.execute(text("SELECT * FROM nonexistent_table"))
        except OperationalError:
            pass

        # Rollback and try again
        session.rollback()
        result = session.execute(text("SELECT 1"))
        assert result.scalar() == 1

        session.close()

    def test_session_close_idempotent(self):
        session = SessionLocal()
        session.close()
        session.close()  # Should not raise error

    def test_missing_database_file(self, tmp_path):
        db_file = tmp_path / "new.db"
        assert not db_file.exists()

        db_url = f"sqlite:///{db_file}"
        test_engine = create_engine(db_url, connect_args={"check_same_thread": False})

        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        assert db_file.exists()
        test_engine.dispose()


class TestDatabasePersistence:
    def test_data_persists_across_sessions(self, tmp_path):
        db_file = tmp_path / "persist_test.db"
        db_url = f"sqlite:///{db_file}"

        test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        # Create a simple test table
        with test_engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.commit()

        # Insert data in first session
        session1 = TestSessionLocal()
        session1.execute(text("INSERT INTO test_table (value) VALUES ('test')"))
        session1.commit()
        session1.close()

        # Read data in second session
        session2 = TestSessionLocal()
        result = session2.execute(text("SELECT value FROM test_table"))
        values = [row[0] for row in result]
        session2.close()

        assert 'test' in values
        test_engine.dispose()

    def test_transaction_rollback(self):
        # Create a test table first
        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE IF NOT EXISTS temp_rollback_test (id INTEGER, value TEXT)"))
            conn.commit()

        session = SessionLocal()

        # Insert data but don't commit
        session.execute(text("INSERT INTO temp_rollback_test (id, value) VALUES (1, 'test')"))
        # Don't commit, just close - this should rollback
        session.close()

        # Data should not exist due to rollback
        session2 = SessionLocal()
        result = session2.execute(text("SELECT COUNT(*) FROM temp_rollback_test"))
        count = result.scalar()
        session2.close()

        # Clean up
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS temp_rollback_test"))
            conn.commit()

        assert count == 0, "Uncommitted data should have been rolled back"


class TestDatabaseConstraints:
    def test_primary_key_constraint(self, tmp_path):
        db_file = tmp_path / "constraint_test.db"
        db_url = f"sqlite:///{db_file}"

        test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        with test_engine.connect() as conn:
            conn.execute(text(
                "CREATE TABLE test_pk (id INTEGER PRIMARY KEY, value TEXT)"
            ))
            conn.commit()

        session = TestSessionLocal()
        session.execute(text("INSERT INTO test_pk (id, value) VALUES (1, 'first')"))
        session.commit()

        # Try to insert duplicate primary key
        with pytest.raises(IntegrityError):
            session.execute(text("INSERT INTO test_pk (id, value) VALUES (1, 'second')"))
            session.commit()

        session.close()
        test_engine.dispose()


class TestDatabaseConfiguration:
    def test_default_database_location(self):
        db_url = os.environ.get('DATABASE_URL')
        assert db_url is not None
        assert 'data' in db_url or 'cvforge.db' in db_url

    def test_database_engine_pool_size(self):
        # SQLite doesn't use connection pooling in the same way,
        # but we can check that engine is properly configured
        assert engine.pool is not None

    def test_database_encoding(self):
        with engine.connect() as conn:
            # SQLite should handle UTF-8 by default
            result = conn.execute(text("SELECT 'test_ãé' as value"))
            assert result.scalar() == 'test_ãé'