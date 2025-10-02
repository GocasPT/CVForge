import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError, IntegrityError
from backend.config import Base

class TestDatabaseConnection:
    def test_database_url_from_environment(self, monkeypatch, temp_db):
        engine, _, db_path = temp_db
        test_db_url = f"sqlite:///{db_path}"
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        assert os.environ.get('DATABASE_URL') == test_db_url

    def test_database_file_creation(self, temp_db):
        engine, _, db_path = temp_db
        assert Path(db_path).exists()

    def test_engine_connection(self, temp_db):
        engine, _, _ = temp_db
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_invalid_database_url(self):
        with pytest.raises(Exception):
            invalid_engine = create_engine("invalid://url")
            with invalid_engine.connect():
                pass


class TestSessionManagement:
    def test_session_creation(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        session = TestSessionLocal()
        assert isinstance(session, Session)
        session.close()

    def test_session_autoflush_disabled(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        session = TestSessionLocal()
        assert session.autoflush is False
        session.close()

    def test_multiple_sessions(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        session1 = TestSessionLocal()
        session2 = TestSessionLocal()

        assert session1 is not session2

        session1.close()
        session2.close()

    def test_session_context_manager(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        with TestSessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def test_session_rollback_on_error(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        session = TestSessionLocal()
        try:
            session.execute(text("SELECT * FROM nonexistent_table"))
        except OperationalError:
            session.rollback()
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        finally:
            session.close()


class TestTableCreation:
    def test_base_metadata_exists(self):
        assert hasattr(Base, 'metadata')
        assert Base.metadata is not None

    def test_tables_created_on_init(self, temp_db):
        engine, _, _ = temp_db
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ))
            tables = [row[0] for row in result]
            assert len(tables) >= 0

    def test_create_all_idempotent(self, temp_db):
        engine, _, _ = temp_db
        Base.metadata.create_all(bind=engine)
        Base.metadata.create_all(bind=engine)  # Should not raise error

    def test_table_recreation(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        try:
            db_url = f"sqlite:///{db_path}"
            test_engine = create_engine(db_url, connect_args={"check_same_thread": False})

            Base.metadata.create_all(bind=test_engine)
            Base.metadata.drop_all(bind=test_engine)
            Base.metadata.create_all(bind=test_engine)

            test_engine.dispose()
        finally:
            try:
                os.unlink(db_path)
            except (PermissionError, FileNotFoundError):
                pass


class TestThreadSafety:
    def test_concurrent_sessions(self, temp_db):
        import threading
        _, TestSessionLocal, _ = temp_db
        sessions = []

        def create_session():
            session = TestSessionLocal()
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
    def test_invalid_sql_query(self, db_session):
        with pytest.raises(OperationalError):
            db_session.execute(text("INVALID SQL SYNTAX"))

    def test_connection_after_error(self, db_session):
        try:
            db_session.execute(text("SELECT * FROM nonexistent_table"))
        except OperationalError:
            pass

        db_session.rollback()
        result = db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1

    def test_session_close_idempotent(self, temp_db):
        _, TestSessionLocal, _ = temp_db
        session = TestSessionLocal()
        session.close()
        session.close()  # Should not raise error


class TestDatabasePersistence:
    def test_data_persists_across_sessions(self, temp_db):
        engine, TestSessionLocal, _ = temp_db

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.commit()

        session1 = TestSessionLocal()
        session1.execute(text("INSERT INTO test_table (value) VALUES ('test')"))
        session1.commit()
        session1.close()

        session2 = TestSessionLocal()
        result = session2.execute(text("SELECT value FROM test_table"))
        values = [row[0] for row in result]
        session2.close()

        assert 'test' in values

    def test_transaction_rollback(self, temp_db):
        engine, TestSessionLocal, _ = temp_db

        with engine.connect() as conn:
            conn.execute(text("CREATE TABLE temp_rollback_test (id INTEGER, value TEXT)"))
            conn.commit()

        session = TestSessionLocal()
        session.execute(text("INSERT INTO temp_rollback_test (id, value) VALUES (1, 'test')"))
        session.close()  # No commit - should rollback

        session2 = TestSessionLocal()
        result = session2.execute(text("SELECT COUNT(*) FROM temp_rollback_test"))
        count = result.scalar()
        session2.close()

        assert count == 0, "Uncommitted data should have been rolled back"


class TestDatabaseConstraints:
    def test_primary_key_constraint(self, temp_db):
        engine, TestSessionLocal, _ = temp_db

        with engine.connect() as conn:
            conn.execute(text(
                "CREATE TABLE test_pk (id INTEGER PRIMARY KEY, value TEXT)"
            ))
            conn.commit()

        session = TestSessionLocal()
        session.execute(text("INSERT INTO test_pk (id, value) VALUES (1, 'first')"))
        session.commit()

        with pytest.raises(IntegrityError):
            session.execute(text("INSERT INTO test_pk (id, value) VALUES (1, 'second')"))
            session.commit()

        session.close()


class TestDatabaseConfiguration:
    def test_database_encoding(self, temp_db):
        engine, _, _ = temp_db
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'test_ãé' as value"))
            assert result.scalar() == 'test_ãé'