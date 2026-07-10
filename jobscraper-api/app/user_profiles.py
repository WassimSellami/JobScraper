from __future__ import annotations

import json
from uuid import uuid4
from pathlib import Path
from threading import Lock
from typing import Any

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    search_terms: list[str] = Field(default_factory=lambda: ["software engineer"])
    job_levels: list[str] = Field(
        default_factory=lambda: [
            "entry level",
            "mid-senior level",
            "not applicable",
        ]
    )
    excluded_companies: list[str] = Field(default_factory=list)
    sites: list[str] = Field(default_factory=lambda: ["linkedin", "indeed"])
    excluded_positions: list[str] = Field(default_factory=list)
    location: str = "Munich, Germany"
    distance_miles: int = 31
    hours_old: int = 24
    allow_deutsch: bool = False


class UserProfileRecord(UserProfile):
    profile_id: str


class UserProfileStore:
    def __init__(self, storage_path: Path | str | None = None):
        self.storage_path = Path(storage_path or self.default_storage_path())
        self._lock = Lock()

    @staticmethod
    def default_storage_path() -> Path:
        return Path(__file__).resolve().parent / "data" / "user_profiles.json"

    def list_profile_ids(self) -> list[str]:
        return sorted(self._read_all().keys())

    def get_profile(self, profile_id: str) -> UserProfile | None:
        raw_profiles = self._read_all()
        raw_profile = raw_profiles.get(self._normalize_profile_id(profile_id))
        if raw_profile is None:
            return None

        return UserProfile.model_validate(raw_profile)

    def save_profile(self, profile_id: str, profile: UserProfile) -> UserProfile:
        normalized_profile_id = self._normalize_profile_id(profile_id)
        with self._lock:
            raw_profiles = self._read_all()
            raw_profiles[normalized_profile_id] = profile.model_dump(mode="json")
            self._write_all(raw_profiles)
        return profile

    def create_profile(self, profile: UserProfile) -> str:
        with self._lock:
            raw_profiles = self._read_all()
            profile_id = self._generate_profile_id(raw_profiles)
            raw_profiles[profile_id] = profile.model_dump(mode="json")
            self._write_all(raw_profiles)
        return profile_id

    def delete_profile(self, profile_id: str) -> bool:
        normalized_profile_id = self._normalize_profile_id(profile_id)
        with self._lock:
            raw_profiles = self._read_all()
            if normalized_profile_id not in raw_profiles:
                return False

            del raw_profiles[normalized_profile_id]
            self._write_all(raw_profiles)
        return True

    def _read_all(self) -> dict[str, Any]:
        if not self.storage_path.exists():
            return {}

        try:
            with self.storage_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except json.JSONDecodeError:
            return {}

        if not isinstance(payload, dict):
            return {}

        return payload

    def _write_all(self, profiles: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.storage_path.open("w", encoding="utf-8") as file_handle:
            json.dump(profiles, file_handle, indent=2, sort_keys=True)
            file_handle.write("\n")

    @staticmethod
    def _normalize_profile_id(profile_id: str) -> str:
        normalized_profile_id = str(profile_id).strip()
        if not normalized_profile_id:
            raise ValueError("profile_id must not be empty")
        return normalized_profile_id

    @staticmethod
    def _generate_profile_id(existing_profiles: dict[str, Any]) -> str:
        profile_id = uuid4().hex
        while profile_id in existing_profiles:
            profile_id = uuid4().hex
        return profile_id
