from uuid import uuid4

from .database import get_pool
from .schemas import UserProfile


class UserProfileStore:
    def list_profile_ids(self) -> list[str]:
        with get_pool().connection() as connection:
            rows = connection.execute(
                "SELECT profile_id FROM user_profiles ORDER BY profile_id"
            ).fetchall()
        return [row["profile_id"] for row in rows]

    def list_profiles(self) -> list[tuple[str, UserProfile]]:
        with get_pool().connection() as connection:
            rows = connection.execute(
                """
                SELECT profile_id, search_terms, job_levels, excluded_companies,
                       excluded_positions, allow_deutsch, last_hours
                FROM user_profiles
                ORDER BY profile_id
                """
            ).fetchall()
        return [(row["profile_id"], self._profile_from_row(row)) for row in rows]

    def get_profile(self, profile_id: str) -> UserProfile | None:
        with get_pool().connection() as connection:
            row = connection.execute(
                """
                SELECT search_terms, job_levels, excluded_companies,
                       excluded_positions, allow_deutsch, last_hours
                FROM user_profiles
                WHERE profile_id = %s
                """,
                (self._normalize_profile_id(profile_id),),
            ).fetchone()
        return self._profile_from_row(row) if row else None

    def save_profile(self, profile_id: str, profile: UserProfile) -> UserProfile:
        values = self._profile_values(profile)
        with get_pool().connection() as connection:
            connection.execute(
                """
                INSERT INTO user_profiles (
                    profile_id, search_terms, job_levels, excluded_companies,
                    excluded_positions, allow_deutsch, last_hours
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (profile_id) DO UPDATE SET
                    search_terms = EXCLUDED.search_terms,
                    job_levels = EXCLUDED.job_levels,
                    excluded_companies = EXCLUDED.excluded_companies,
                    excluded_positions = EXCLUDED.excluded_positions,
                    allow_deutsch = EXCLUDED.allow_deutsch,
                    last_hours = EXCLUDED.last_hours,
                    updated_at = NOW()
                """,
                (self._normalize_profile_id(profile_id), *values),
            )
        return profile

    def create_profile(self, profile: UserProfile) -> str:
        profile_id = uuid4().hex
        values = self._profile_values(profile)
        with get_pool().connection() as connection:
            connection.execute(
                """
                INSERT INTO user_profiles (
                    profile_id, search_terms, job_levels, excluded_companies,
                    excluded_positions, allow_deutsch, last_hours
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (profile_id, *values),
            )
        return profile_id

    def delete_profile(self, profile_id: str) -> bool:
        with get_pool().connection() as connection:
            result = connection.execute(
                "DELETE FROM user_profiles WHERE profile_id = %s",
                (self._normalize_profile_id(profile_id),),
            )
        return result.rowcount > 0

    @staticmethod
    def _normalize_profile_id(profile_id: str) -> str:
        normalized_profile_id = str(profile_id).strip()
        if not normalized_profile_id:
            raise ValueError("profile_id must not be empty")
        return normalized_profile_id

    @staticmethod
    def _profile_values(
        profile: UserProfile,
    ) -> tuple[list[str], list[str], list[str], list[str], bool, int]:
        return (
            profile.search_terms,
            profile.job_levels,
            profile.excluded_companies,
            profile.excluded_positions,
            profile.allow_deutsch,
            profile.last_hours,
        )

    @staticmethod
    def _profile_from_row(row: dict) -> UserProfile:
        return UserProfile.model_validate(
            {
                "search_terms": row["search_terms"],
                "job_levels": row["job_levels"],
                "excluded_companies": row["excluded_companies"],
                "excluded_positions": row["excluded_positions"],
                "allow_deutsch": row["allow_deutsch"],
                "last_hours": row["last_hours"],
            }
        )
