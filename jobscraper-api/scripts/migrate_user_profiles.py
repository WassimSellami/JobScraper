"""Import profiles from the legacy JSON file into PostgreSQL once."""

import json
from pathlib import Path

from app.user_profiles import (
    UserProfile,
    UserProfileStore,
    close_database,
    initialize_database,
)


def main() -> None:
    source = Path(__file__).resolve().parents[1] / "app" / "data" / "user_profiles.json"
    profiles = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(profiles, dict):
        raise ValueError("Expected user_profiles.json to contain an object")

    initialize_database()
    store = UserProfileStore()
    for profile_id, payload in profiles.items():
        store.save_profile(profile_id, UserProfile.model_validate(payload))

    close_database()
    print(f"Migrated {len(profiles)} user profile(s).")


if __name__ == "__main__":
    main()
