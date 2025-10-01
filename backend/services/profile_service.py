import json

from pathlib import Path
from typing import Optional, Dict, Any

from pydantic import BaseModel, ValidationError


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
            return None

        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return ProfileData(**data)

        except (json.JSONDecodeError, ValidationError, FileNotFoundError, PermissionError, OSError) as e:
            print(f"Error loading profile: {e}")
            return None

    def save_profile(self, profile: ProfileData) -> bool:
        try:
            self.profile_path.parent.mkdir(parents=True, exist_ok=True)

            profile_dict = profile.model_dump()

            with open(self.profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_dict, f, ensure_ascii=False, indent=4)

            return True

        except (json.JSONDecodeError, ValidationError, FileNotFoundError, PermissionError, OSError, Exception) as e:
            print(f"Error saving profile: {e}")
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