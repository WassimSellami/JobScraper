import logging
from typing import List

import pandas as pd

from ...constants import (
    RESULTS_WANTED_DEFAULT,
    SCRAPE_DISTANCE_MILES,
    SCRAPE_HOURS_OLD,
    SCRAPE_LOCATION,
)
from ...user_profiles import UserProfile

logger = logging.getLogger(__name__)


def normalize_search_terms(search_terms: List[str]) -> list[str]:
    normalized = []
    for term in search_terms:
        term_text = str(term).strip()
        if term_text and term_text not in normalized:
            normalized.append(term_text)
    return normalized


def scrape_linkedin_terms(search_terms: List[str]) -> pd.DataFrame:
    try:
        from jobspy import scrape_jobs
    except Exception:
        logger.exception("Failed to import jobspy.scrape_jobs")
        raise

    normalized_terms = normalize_search_terms(search_terms) or [None]
    frames: list[pd.DataFrame] = []

    for term in normalized_terms:
        logger.info("Scraping term: %r", term)
        try:
            df = scrape_jobs(
                site_name="linkedin",
                search_term=term,
                location=SCRAPE_LOCATION,
                distance=SCRAPE_DISTANCE_MILES,
                hours_old=SCRAPE_HOURS_OLD,
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
