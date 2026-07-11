import logging

from fastapi import APIRouter, HTTPException, status

from .user_profiles import (
    UserProfile,
    UserProfileRecord,
    UserProfileStore,
)

router = APIRouter()
logger = logging.getLogger(__name__)
store = UserProfileStore()


def _to_record(profile_id: str, profile: UserProfile) -> UserProfileRecord:
    return UserProfileRecord(profile_id=profile_id, **profile.model_dump())


@router.get("", response_model=list[UserProfileRecord])
def list_profiles():
    return [
        _to_record(profile_id, profile)
        for profile_id, profile in store.list_profiles()
    ]


@router.get("/{profile_id}", response_model=UserProfileRecord)
def get_profile(profile_id: str):
    profile = store.get_profile(profile_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return _to_record(profile_id, profile)


@router.post("", response_model=UserProfileRecord, status_code=status.HTTP_201_CREATED)
def create_profile(payload: UserProfile):
    profile_id = store.create_profile(payload)
    logger.info("Created profile %s", profile_id)
    return _to_record(profile_id, payload)


@router.put("/{profile_id}", response_model=UserProfileRecord)
def update_profile(profile_id: str, payload: UserProfile):
    existing_profile = store.get_profile(profile_id)
    if existing_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    saved_profile = store.save_profile(profile_id, payload)
    logger.info("Updated profile %s", profile_id)
    return _to_record(profile_id, saved_profile)


@router.delete("/{profile_id}")
def delete_profile(profile_id: str):
    deleted = store.delete_profile(profile_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    logger.info("Deleted profile %s", profile_id)
    return {"status": "deleted", "profile_id": profile_id}
