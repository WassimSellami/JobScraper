from __future__ import annotations

import json
import re

import pandas as pd
from psycopg.types.json import Jsonb

from ...database import get_pool


def initialize_jobs_database() -> None:
    with get_pool().connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                external_id TEXT,
                job_url TEXT NOT NULL UNIQUE,
                site TEXT,
                job_url_direct TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                date_posted TEXT,
                job_type TEXT,
                description TEXT,
                job_level TEXT,
                company_industry TEXT,
                search_term TEXT,
                search_terms TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
                payload JSONB NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS jobs_site_idx ON jobs (LOWER(site))"
        )
        connection.execute(
            """
            ALTER TABLE jobs
            ADD COLUMN IF NOT EXISTS search_terms TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[]
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS jobs_site_created_at_idx
            ON jobs (LOWER(site), created_at DESC)
            """
        )


class JobsPostgresStore:
    def read(
        self, site: str | None = None, last_hours: int | None = None
    ) -> pd.DataFrame:
        query = "SELECT payload, search_terms FROM jobs"
        conditions: list[str] = []
        parameters: list = []
        if site:
            conditions.append("LOWER(site) = LOWER(%s)")
            parameters.append(str(site).strip())
        if last_hours is not None:
            if last_hours < 0:
                raise ValueError("last_hours must be greater than or equal to 0")
            if last_hours == 0:
                conditions.append("FALSE")
            else:
                conditions.append("created_at >= NOW() - (%s * INTERVAL '1 hour')")
                parameters.append(last_hours)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY created_at DESC"

        with get_pool().connection() as connection:
            rows = connection.execute(query, tuple(parameters)).fetchall()

        records = []
        for row in rows:
            record = dict(row["payload"])
            stored_terms = row["search_terms"] or []
            if stored_terms:
                record["_search_terms"] = stored_terms
            records.append(record)
        return pd.DataFrame(records)

    def upsert(self, new_rows: pd.DataFrame) -> int:
        if new_rows is None or new_rows.empty:
            return 0

        cleaned = self._normalize_whitespace(new_rows)
        if "job_url" not in cleaned.columns:
            raise ValueError("Scraped jobs must contain a job_url column")

        cleaned = cleaned.copy()
        cleaned["job_url"] = cleaned["job_url"].fillna("").astype(str).str.strip()
        cleaned = cleaned[cleaned["job_url"] != ""].copy()
        cleaned = cleaned.drop_duplicates(subset=["job_url"], keep="first")

        records = json.loads(cleaned.to_json(orient="records", date_format="iso"))
        values = [self._record_values(record) for record in records]
        if values:
            with get_pool().connection() as connection:
                connection.cursor().executemany(
                    """
                    INSERT INTO jobs (
                        external_id, job_url, site, job_url_direct, title, company,
                        location, date_posted, job_type, description, job_level,
                        company_industry, search_term, search_terms, payload
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_url) DO UPDATE SET
                        external_id = EXCLUDED.external_id,
                        site = EXCLUDED.site,
                        job_url_direct = EXCLUDED.job_url_direct,
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        location = EXCLUDED.location,
                        date_posted = EXCLUDED.date_posted,
                        job_type = EXCLUDED.job_type,
                        description = EXCLUDED.description,
                        job_level = EXCLUDED.job_level,
                        company_industry = EXCLUDED.company_industry,
                        search_term = EXCLUDED.search_term,
                        search_terms = EXCLUDED.search_terms,
                        payload = EXCLUDED.payload,
                        updated_at = NOW()
                    """,
                    values,
                )

        return len(values)

    @staticmethod
    def _record_values(record: dict) -> tuple:
        return (
            record.get("id"),
            record["job_url"],
            record.get("site"),
            record.get("job_url_direct"),
            record.get("title"),
            record.get("company"),
            record.get("location"),
            record.get("date_posted"),
            record.get("job_type"),
            record.get("description"),
            record.get("job_level"),
            record.get("company_industry"),
            record.get("_search_term"),
            record.get("_search_terms", []),
            Jsonb(record),
        )

    @staticmethod
    def _normalize_whitespace(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty or "description" not in df.columns:
            return df

        cleaned = df.copy()
        cleaned["description"] = (
            cleaned["description"]
            .fillna("")
            .astype(str)
            .map(lambda value: re.sub(r"\s+", " ", value).strip())
        )
        return cleaned
