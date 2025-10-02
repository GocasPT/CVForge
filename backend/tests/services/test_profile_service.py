import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch
from services import ProfileService, ProfileData

class TestProfileData:
    def test_profile_data_creation_valid(self):
        data = {
            "personal": {"full_name": "John Doe", "email": "john@example.com"},
            "professional": {"title": "Developer"},
            "skills": {"languages": ["Python"]},
            "preferences": {"theme": "dark"},
            "metadata": {"version": "1.0"}
        }

        profile = ProfileData(**data)
        assert profile.personal["full_name"] == "John Doe"
        assert profile.professional["title"] == "Developer"
        assert profile.skills["languages"] == ["Python"]

    def test_profile_data_creation_minimal(self):
        data = {
            "personal": {"full_name": "John Doe", "email": "john@example.com"}
        }

        profile = ProfileData(**data)
        assert profile.personal["full_name"] == "John Doe"
        assert profile.professional is None
        assert profile.skills is None

    def test_profile_data_validation_missing_personal(self):
        with pytest.raises(ValueError):
            ProfileData(personal=None)

class TestProfileService:
    def test_profile_exists_false_when_missing(self, profile_service):
        assert not profile_service.profile_exists()

    def test_profile_exists_true_when_present(self, profile_service, sample_profile_data):
        profile = ProfileData(**sample_profile_data)
        profile_service.save_profile(profile)
        assert profile_service.profile_exists()

    def test_load_profile_none_when_missing(self, profile_service):
        assert profile_service.load_profile() is None

    def test_load_profile_success(self, profile_service, sample_profile_data):
        # Save profile first
        profile = ProfileData(**sample_profile_data)
        profile_service.save_profile(profile)

        # Load and verify
        loaded_profile = profile_service.load_profile()
        assert loaded_profile is not None
        assert loaded_profile.personal["full_name"] == "Test User"
        assert loaded_profile.personal["email"] == "test@example.com"

    def test_save_and_load_roundtrip(self, profile_service, sample_profile_data):
        original_profile = ProfileData(**sample_profile_data)

        # Save and load
        assert profile_service.save_profile(original_profile)
        loaded_profile = profile_service.load_profile()

        # Compare the data
        assert loaded_profile.model_dump() == original_profile.model_dump()

    def test_save_profile_creates_directory(self, temp_profile_dir):
        nested_path = temp_profile_dir / "nested" / "deep" / "profile.json"
        service = ProfileService(profile_path=str(nested_path))

        profile_data = ProfileData(
            personal={"full_name": "Test", "email": "test@example.com"}
        )

        assert service.save_profile(profile_data)
        assert nested_path.exists()

    def test_validate_profile_success(self, profile_service, sample_profile_data):
        profile = ProfileData(**sample_profile_data)
        profile_service.save_profile(profile)

        is_valid, error = profile_service.validate_profile()
        assert is_valid
        assert error is None

    def test_validate_profile_missing_file(self, profile_service):
        is_valid, error = profile_service.validate_profile()
        assert not is_valid
        assert "not found" in error.lower()

    def test_validate_profile_missing_full_name(self, profile_service):
        invalid_data = {
            "personal": {
                "email": "test@example.com"
                # missing full_name
            }
        }

        profile = ProfileData(**invalid_data)
        profile_service.save_profile(profile)

        is_valid, error = profile_service.validate_profile()
        assert not is_valid
        assert "full_name" in error.lower()

    def test_validate_profile_missing_email(self, profile_service):
        invalid_data = {
            "personal": {
                "full_name": "Test User"
                # missing email
            }
        }

        profile = ProfileData(**invalid_data)
        profile_service.save_profile(profile)

        is_valid, error = profile_service.validate_profile()
        assert not is_valid
        assert "email" in error.lower()

    def test_get_profile_summary_when_missing(self, profile_service):
        summary = profile_service.get_profile_summary()

        assert summary["exists"] is False
        assert "error" in summary
        assert str(profile_service.profile_path) in summary["path"]

    def test_get_profile_summary_success(self, profile_service, sample_profile_data):
        profile = ProfileData(**sample_profile_data)
        profile_service.save_profile(profile)

        summary = profile_service.get_profile_summary()

        assert summary["exists"] is True
        assert summary["full_name"] == "Test User"
        assert summary["email"] == "test@example.com"
        assert summary["skills_categories"] == 2  # programming and tools

    def test_get_profile_summary_no_skills(self, profile_service):
        minimal_data = {
            "personal": {
                "full_name": "Test User",
                "email": "test@example.com"
            }
        }

        profile = ProfileData(**minimal_data)
        profile_service.save_profile(profile)

        summary = profile_service.get_profile_summary()
        assert summary["skills_categories"] == 0

class TestProfileServiceEdgeCases:
    def test_load_profile_invalid_json(self, temp_profile_dir):
        profile_path = temp_profile_dir / "profile.json"
        service = ProfileService(profile_path=str(profile_path))

        # Write invalid JSON
        with open(profile_path, 'w') as f:
            f.write('{"invalid": json}')

        profile = service.load_profile()
        assert profile is None

    def test_load_profile_file_not_found(self, profile_service):
        # Ensure file doesn't exist
        if profile_service.profile_path.exists():
            profile_service.profile_path.unlink()

        profile = profile_service.load_profile()
        assert profile is None

    @patch('tempfile.NamedTemporaryFile', side_effect=PermissionError("No permission"))
    def test_save_profile_permission_error(self, mock_tempfile, profile_service):
        profile_data = ProfileData(
            personal={"full_name": "Test", "email": "test@example.com"}
        )

        result = profile_service.save_profile(profile_data)
        assert not result

    @patch('builtins.open', side_effect=PermissionError("No permission"))
    def test_load_profile_permission_error(self, mock_file, profile_service):
        # Create the file first so exists() returns True
        profile_service.profile_path.touch()

        profile = profile_service.load_profile()
        assert profile is None

    def test_save_profile_validation_error(self, profile_service):
        # This should not happen in normal usage since we're passing a ProfileData object
        # But we can test the error handling by mocking model_dump to raise an exception
        with patch.object(ProfileData, 'model_dump', side_effect=Exception("Validation error")):
            profile_data = ProfileData(
                personal={"full_name": "Test", "email": "test@example.com"}
            )

            result = profile_service.save_profile(profile_data)
            assert not result

class TestProfileServiceIntegration:
    def test_complete_profile_lifecycle(self, temp_profile_dir):
        profile_path = temp_profile_dir / "test_profile.json"
        service = ProfileService(profile_path=str(profile_path))

        # Step 1: Verify no profile exists initially
        assert not service.profile_exists()
        assert service.load_profile() is None

        # Step 2: Create and save a profile
        profile_data = {
            "personal": {
                "full_name": "Integration Test User",
                "email": "integration@example.com",
                "location": "Test City"
            },
            "skills": {
                "languages": ["Python", "TypeScript"],
                "databases": ["PostgreSQL", "Redis"]
            }
        }

        profile = ProfileData(**profile_data)
        assert service.save_profile(profile)

        # Step 3: Verify profile exists and can be loaded
        assert service.profile_exists()

        loaded_profile = service.load_profile()
        assert loaded_profile is not None
        assert loaded_profile.personal["full_name"] == "Integration Test User"

        # Step 4: Validate profile
        is_valid, error = service.validate_profile()
        assert is_valid
        assert error is None

        # Step 5: Get summary
        summary = service.get_profile_summary()
        assert summary["exists"] is True
        assert summary["full_name"] == "Integration Test User"
        assert summary["skills_categories"] == 2

        # Step 6: Verify file was actually created on disk
        assert profile_path.exists()
        with open(profile_path, 'r') as f:
            disk_data = json.load(f)
            assert disk_data["personal"]["full_name"] == "Integration Test User"