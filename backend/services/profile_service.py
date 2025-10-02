import json
import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

class ProfileData(BaseModel):
    personal: Dict[str, Any]
    professional: Optional[Dict[str, Any]] = None
    skills: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class ProfileService:
    def __init__(self, profile_path: str = "config/profile.json"):
        self.profile_path = Path(profile_path)

    def load_profile(self) -> Optional[ProfileData]:
        if not self.profile_path.exists():
            logger.warning("Profile not found at %s" % self.profile_path)
            return None

        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return ProfileData(**data)

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in profile file: %s" % e)
            return None

        except ValidationError as e:
            logger.error("Profile validation failed: %s" % e)
            return None

        except PermissionError as e:
            logger.error("Permission denied reading profile: %s" % e)
            return None

        except Exception as e:
            logger.exception("Unexpected error loading profile: %s" % e)
            return None

    def save_profile(self, profile: ProfileData) -> bool:
        try:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first
            with tempfile.NamedTemporaryFile(
                    mode='w',
                    delete=False,
                    dir=self.profile_path.parent,
                    encoding='utf-8'
            ) as tmp_file:
                json.dump(profile.model_dump(), tmp_file,
                          ensure_ascii=False, indent=4)
                tmp_path = tmp_file.name

            # Atomic rename
            shutil.move(tmp_path, self.profile_path)
            return True

        except Exception as e:
            logger.error("Error saving profile: %s" % e)
            return False

    def profile_exists(self) -> bool:
        return self.profile_path.exists()

    def validate_profile(self) -> tuple[bool, Optional[str]]:
        if not self.profile_exists():
            return False, "Profile file not found"

        try:
            profile = self.load_profile()
            if profile is None:
                return False, "Could not load profile"

            # Basic validation checks
            if not profile.personal.get('full_name'):
                return False, "Missing full_name in personal section"

            if not profile.personal.get('email'):
                return False, "Missing email in personal section"

            return True, None

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_profile_summary(self) -> Dict[str, Any]:
        if not self.profile_exists():
            return {
                "exists": False,
                "path": str(self.profile_path),
                "error": "Profile file not found"
            }

        profile = self.load_profile()
        if profile is None:
            return {
                "exists": True,
                "path": str(self.profile_path),
                "error": "Could not load profile data"
            }

        return {
            "exists": True,
            "path": str(self.profile_path),
            "full_name": profile.personal.get('full_name', 'Unknown'),
            "email": profile.personal.get('email', 'Unknown'),
            "skills_categories": len(profile.skills) if profile.skills else 0
        }