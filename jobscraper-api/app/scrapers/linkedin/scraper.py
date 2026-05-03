import pandas as pd
import logging
from typing import List

from app.constants import LINKEDIN_OUTPUT_COLUMNS
from .settings import LinkedInScraperSettings

logger = logging.getLogger(__name__)


def run_scraper(settings: LinkedInScraperSettings) -> pd.DataFrame:
    try:
        from jobspy import scrape_jobs
    except Exception:
        logger.exception("Failed to import jobspy.scrape_jobs")
        raise

    all_results: List[pd.DataFrame] = []

    for term in settings.SEARCH_TERMS:
        try:
            logger.info("Scraping term='%s'", term)
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=term,
                location=settings.LOCATION,
                distance=settings.DISTANCE_MILES,
                hours_old=settings.HOURS_OLD,
                results_wanted=settings.RESULTS_WANTED,
                linkedin_fetch_description=True,
                verbose=0,
            )
            logger.info("Term='%s' returned %d rows", term, len(jobs))
            if not jobs.empty:
                all_results.append(jobs)
        except Exception:
            logger.exception("Scrape failed for term='%s'", term)
            continue

    if not all_results:
        logger.warning("No results returned for all terms")
        return pd.DataFrame(columns=LINKEDIN_OUTPUT_COLUMNS)

    combined = pd.concat(all_results, ignore_index=True)
    available_cols = [c for c in LINKEDIN_OUTPUT_COLUMNS if c in combined.columns]
    output = combined[available_cols].copy()
    logger.info("Combined output rows=%d cols=%d", len(output), len(output.columns))
    return output
