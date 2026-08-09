from __future__ import annotations

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import DATABASE_URL

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        if not DATABASE_URL or "YOUR_NEON" in DATABASE_URL:
            raise RuntimeError(
                "DATABASE_URL is not configured. Add the PostgreSQL connection "
                "string to jobscraper-api/.env."
            )

        _pool = ConnectionPool(
            conninfo=DATABASE_URL,
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
                profile_name TEXT,
                search_terms TEXT[] NOT NULL DEFAULT ARRAY['software engineer']::TEXT[],
                job_levels TEXT[] NOT NULL DEFAULT ARRAY[
                    'internship', 'entry level', 'mid-senior level', 'not applicable'
                ]::TEXT[],
                excluded_companies TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
                excluded_positions TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
                allow_deutsch BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            """
            ALTER TABLE user_profiles
            ADD COLUMN IF NOT EXISTS last_hours INTEGER NOT NULL DEFAULT 1
            """
        )
        connection.execute(
            """
            ALTER TABLE user_profiles
            ADD COLUMN IF NOT EXISTS profile_name TEXT
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS user_profiles_profile_name_unique
            ON user_profiles (LOWER(profile_name))
            WHERE profile_name IS NOT NULL
            """
        )
        connection.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'user_profiles_last_hours_nonnegative'
                      AND conrelid = 'user_profiles'::regclass
                ) THEN
                    ALTER TABLE user_profiles
                    ADD CONSTRAINT user_profiles_last_hours_nonnegative
                    CHECK (last_hours >= 0);
                END IF;
            END
            $$
            """
        )


def close_database() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None
