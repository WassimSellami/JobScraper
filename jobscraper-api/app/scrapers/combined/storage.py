from __future__ import annotations

import re
from pathlib import Path
from threading import Lock

import pandas as pd


class SharedJobsCsvStore:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)
        self._lock = Lock()

    def read(self, site: str | None = None) -> pd.DataFrame:
        if not self.csv_path.exists():
            return pd.DataFrame()

        df = pd.read_csv(self.csv_path)
        if site and not df.empty and "site" in df.columns:
            site_value = str(site).strip().casefold()
            df = df[
                df["site"].fillna("").astype(str).str.strip().str.casefold()
                == site_value
            ].copy()

        return df.reset_index(drop=True)

    def upsert(self, new_rows: pd.DataFrame) -> pd.DataFrame:
        if new_rows is None or new_rows.empty:
            return self.read()

        with self._lock:
            current_rows = self.read()
            combined = pd.concat([current_rows, new_rows], ignore_index=True, sort=False)
            combined = self._normalize_whitespace(combined)

            if "job_url" in combined.columns:
                combined["job_url"] = combined["job_url"].fillna("").astype(str).str.strip()
                combined = combined[combined["job_url"] != ""].copy()
                combined = combined.drop_duplicates(subset=["job_url"], keep="first")

            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            combined.to_csv(self.csv_path, index=False)
            return combined

    @staticmethod
    def _normalize_whitespace(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty or "description" not in df.columns:
            return df

        cleaned = df.copy()
        description_series = cleaned["description"].fillna("").astype(str)
        description_series = description_series.map(
            lambda value: re.sub(r"\s+", " ", value).strip()
        )
        cleaned["description"] = description_series
        return cleaned
