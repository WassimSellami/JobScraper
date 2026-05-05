import logging
from typing import List

import pandas as pd

from .settings import CombinedScraperSettings

logger = logging.getLogger(__name__)


def normalize_sites(sites: List[str]) -> list[str]:
    normalized = []
    for site in sites:
        site_name = str(site).strip().lower()
        if site_name and site_name not in normalized:
            normalized.append(site_name)
    return normalized


def scrape_all_sites(settings: CombinedScraperSettings) -> pd.DataFrame:
    try:
        from jobspy import scrape_jobs
    except Exception:
        logger.exception("Failed to import jobspy.scrape_jobs")
        raise

    requested_sites = normalize_sites(settings.sites) or ["linkedin", "indeed"]
    site_name = requested_sites if len(requested_sites) > 1 else requested_sites[0]

    raw_df = scrape_jobs(
        site_name=site_name,
        search_term=" OR ".join(term for term in settings.SEARCH_TERMS if term) or None,
        location=settings.LOCATION,
        distance=settings.DISTANCE_MILES,
        hours_old=settings.HOURS_OLD,
        results_wanted=settings.RESULTS_WANTED,
        linkedin_fetch_description=True,
        country_indeed="germany",
        verbose=0,
    )
    return raw_df


def split_by_site(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    if "site" in df.columns:
        site_series = df["site"].fillna("").astype(str).str.lower()
        linkedin_df = df.loc[site_series == "linkedin"].copy()
        indeed_df = df.loc[site_series == "indeed"].copy()
        return linkedin_df, indeed_df

    # Fallback for older payloads: LinkedIn rows usually expose job_level.
    job_level_series = (
        df["job_level"]
        if "job_level" in df.columns
        else pd.Series(index=df.index, dtype=object)
    )
    linkedin_mask = job_level_series.notna()
    linkedin_df = df.loc[linkedin_mask].copy()
    indeed_df = df.loc[~linkedin_mask].copy()
    return linkedin_df, indeed_df
