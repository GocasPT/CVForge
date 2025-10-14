import os
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from backend.services import ProfileService, ProfileData
from pathlib import Path

router = APIRouter()
PROFILE_PATH = Path(os.environ.get("PROFILE_PATH"))
profile_service = ProfileService(PROFILE_PATH)

@router.get("")
def get_profile():
    profile = profile_service.load_profile()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile.model_dump()

@router.post("")
def update_profile(data: dict):
    profile_data = ProfileData(**data)
    success = profile_service.save_profile(profile_data)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to save profile")
    return {
        "status": "updated",
        "profile": profile_data.model_dump()
    }


def deep_update(target: Any, updates: Dict[str, Any]) -> None:
    for key, value in updates.items():
        if not hasattr(target, key):
            continue

        current_value = getattr(target, key)

        if isinstance(value, dict) and hasattr(current_value, '__dict__'):
            deep_update(current_value, value)

        elif isinstance(value, dict) and isinstance(current_value, dict):
            current_value.update(value)

        else:
            if current_value != value:
                setattr(target, key, value)

@router.patch("")
def parcial_update_profile(data: dict):
    profile = profile_service.load_profile()
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    deep_update(profile, data)

    success = profile_service.save_profile(profile)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to save profile")

    return {
        "status": "updated",
        "profile": profile.model_dump()
    }


@router.get("/validate")
def validate_profile():
    valid, err = profile_service.validate_profile()
    if not valid:
        return {
            "valid": False,
            "message": err
        }

    return {
        "valid": True
    }

@router.get("/summary")
def summary_profile():
    return profile_service.get_profile_summary()