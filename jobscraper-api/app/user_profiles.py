from __future__ import annotations

import os
from uuid import uuid4

from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel, Field

load_dotenv()


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
    excluded_positions: list[str] = Field(default_factory=list)
    allow_deutsch: bool = False


class UserProfileRecord(UserProfile):
    profile_id: str


_pool: ConnectionPool | None = None


def _database_url() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url or "YOUR_NEON" in database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured. Add the Neon PostgreSQL connection "
            "string to jobscraper-api/.env."
        )
    return database_url


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_database_url(),
            min_size=0,
            max_size=10,
            kwargs={"row_factory": dict_row},
            check=ConnectionPool.check_connection,
            max_idle=120,
            max_lifetime=1800,
            open=False,
        )
        _pool.open(wait=True)
    return _pool


def initialize_database() -> None:
    with get_pool().connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
                profile_id TEXT PRIMARY KEY,
                search_terms TEXT[] NOT NULL DEFAULT ARRAY['software engineer']::TEXT[],
                job_levels TEXT[] NOT NULL DEFAULT ARRAY[
                    'entry level', 'mid-senior level', 'not applicable'
                ]::TEXT[],
                excluded_companies TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
                excluded_positions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
                allow_deutsch BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )


def close_database() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


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
                       excluded_positions, allow_deutsch
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
                       excluded_positions, allow_deutsch
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
                    excluded_positions, allow_deutsch
                ) VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (profile_id) DO UPDATE SET
                    search_terms = EXCLUDED.search_terms,
                    job_levels = EXCLUDED.job_levels,
                    excluded_companies = EXCLUDED.excluded_companies,
                    excluded_positions = EXCLUDED.excluded_positions,
                    allow_deutsch = EXCLUDED.allow_deutsch,
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
                    excluded_positions, allow_deutsch
                ) VALUES (%s, %s, %s, %s, %s, %s)
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
    def _profile_values(profile: UserProfile) -> tuple[list[str], list[str], list[str], list[str], bool]:
        return (
            profile.search_terms,
            profile.job_levels,
            profile.excluded_companies,
            profile.excluded_positions,
            profile.allow_deutsch,
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
            }
        )
