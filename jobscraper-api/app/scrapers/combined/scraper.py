import logging
from typing import List

import pandas as pd

from ...constants import RESULTS_WANTED_DEFAULT
from ...user_profiles import UserProfile

logger = logging.getLogger(__name__)


def normalize_sites(sites: List[str]) -> list[str]:
    normalized = []
    for site in sites:
        site_name = str(site).strip().lower()
        if site_name and site_name not in normalized:
            normalized.append(site_name)
    return normalized


def scrape_all_sites(profile: UserProfile) -> pd.DataFrame:
    try:
        from jobspy import scrape_jobs
    except Exception:
        logger.exception("Failed to import jobspy.scrape_jobs")
        raise

    requested_sites = normalize_sites(profile.sites) or ["linkedin", "indeed"]
    site_name = requested_sites if len(requested_sites) > 1 else requested_sites[0]

    search_terms = [t for t in profile.search_terms if t] or [None]
    frames: list[pd.DataFrame] = []

    for term in search_terms:
        logger.info("Scraping term: %r", term)
        try:
            df = scrape_jobs(
                site_name=site_name,
                search_term=term,
                location=profile.location,
                distance=profile.distance_miles,
                hours_old=profile.hours_old,
                results_wanted=RESULTS_WANTED_DEFAULT,
                linkedin_fetch_description=True,
                country_indeed="germany",
                verbose=0,
            )
            if df is not None and not df.empty:
                df["_search_term"] = term  # optional: track which term produced the row
                frames.append(df)
        except Exception:
            logger.exception("Failed scraping term %r", term)

    if not frames:
        return pd.DataFrame()

    combined = pd.concat(frames, ignore_index=True)
    # Deduplicate by job_url if available, keeping first occurrence
    if "job_url" in combined.columns:
        combined = combined.drop_duplicates(subset=["job_url"], keep="first")

    return combined


def split_by_site(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    if "site" in df.columns:
        site_series = df["site"].fillna("").astype(str).str.lower()
        linkedin_df = df.loc[site_series == "linkedin"].copy()
        indeed_df = df.loc[site_series == "indeed"].copy()
        return linkedin_df, indeed_df

    job_level_series = (
        df["job_level"]
        if "job_level" in df.columns
        else pd.Series(index=df.index, dtype=object)
    )
    linkedin_mask = job_level_series.notna()
    return df.loc[linkedin_mask].copy(), df.loc[~linkedin_mask].copy()
