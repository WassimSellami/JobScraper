import logging

from fastapi import APIRouter, HTTPException, status

from .schemas import ProfileRenameRequest, UserProfile, UserProfileRecord
from .user_profile_repository import UserProfileStore

router = APIRouter()
logger = logging.getLogger(__name__)
store = UserProfileStore()


def _to_record(profile_id: str, profile: UserProfile) -> UserProfileRecord:
    return UserProfileRecord(profile_id=profile_id, **profile.model_dump())


def _bad_profile_id(exc: ValueError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


def _database_error(action: str, exc: Exception) -> HTTPException:
    logger.exception("Failed to %s user profile", action, exc_info=exc)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="User profile database operation failed",
    )


@router.get("", response_model=list[UserProfileRecord])
def list_profiles() -> list[UserProfileRecord]:
    try:
        profiles = store.list_profiles()
    except Exception as exc:
        raise _database_error("list", exc) from exc
    return [_to_record(profile_id, profile) for profile_id, profile in profiles]


@router.get("/{profile_id}", response_model=UserProfileRecord)
def get_profile(profile_id: str) -> UserProfileRecord:
    try:
        profile = store.get_profile(profile_id)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("get", exc) from exc
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return _to_record(profile_id, profile)


@router.post("", response_model=UserProfileRecord, status_code=status.HTTP_201_CREATED)
def create_profile(payload: UserProfile) -> UserProfileRecord:
    try:
        profile_id = store.create_profile(payload)
    except Exception as exc:
        raise _database_error("create", exc) from exc
    logger.info("Created profile %s", profile_id)
    return _to_record(profile_id, payload)


@router.put("/{profile_id}", response_model=UserProfileRecord)
def update_profile(profile_id: str, payload: UserProfile) -> UserProfileRecord:
    try:
        existing_profile = store.get_profile(profile_id)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("get", exc) from exc
    if existing_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    if payload.profile_name is None:
        payload.profile_name = existing_profile.profile_name

    try:
        saved_profile = store.save_profile(profile_id, payload)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("update", exc) from exc
    logger.info("Updated profile %s", profile_id)
    return _to_record(profile_id, saved_profile)


@router.patch("/{profile_id}/name", response_model=UserProfileRecord)
def rename_profile(
    profile_id: str, payload: ProfileRenameRequest
) -> UserProfileRecord:
    try:
        profile = store.get_profile(profile_id)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("get", exc) from exc
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    try:
        renamed_profile_name = store.rename_profile(profile_id, payload.profile_name)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("rename", exc) from exc
    if renamed_profile_name is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    profile.profile_name = renamed_profile_name
    logger.info("Renamed profile %s", profile_id)
    return _to_record(profile_id, profile)


@router.delete("/{profile_id}")
def delete_profile(profile_id: str) -> dict[str, str]:
    try:
        deleted = store.delete_profile(profile_id)
    except ValueError as exc:
        raise _bad_profile_id(exc) from exc
    except Exception as exc:
        raise _database_error("delete", exc) from exc
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    logger.info("Deleted profile %s", profile_id)
    return {"status": "deleted", "profile_id": profile_id}
