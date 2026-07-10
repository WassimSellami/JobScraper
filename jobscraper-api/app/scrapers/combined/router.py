import json
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException

from .filter import filter_indeed, filter_linkedin
from .scraper import normalize_sites, scrape_all_sites, split_by_site
from ...user_profiles import UserProfile

router = APIRouter()
logger = logging.getLogger(__name__)


def _dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.post("/all")
def post_all(profile: UserProfile):
    logger.info(
        "POST /all started | terms=%d location=%s hours_old=%s sites=%s",
        len(profile.search_terms),
        profile.location,
        profile.hours_old,
        profile.sites,
    )

    requested_sites = normalize_sites(profile.sites) or ["linkedin", "indeed"]

    try:
        raw_df = scrape_all_sites(profile)
        logger.info("Combined scraper returned %d rows", len(raw_df))
    except Exception:
        logger.exception("Combined scrape failed")
        raise HTTPException(status_code=500, detail="Combined scrape failed")

    linkedin_df, indeed_df = split_by_site(raw_df)
    results = []

    if "linkedin" not in requested_sites:
        linkedin_df = pd.DataFrame()
    if "indeed" not in requested_sites:
        indeed_df = pd.DataFrame()

    try:
        logger.info("LinkedIn subset rows=%d", len(linkedin_df))
        ln_clean = filter_linkedin(linkedin_df, profile)
        logger.info("LinkedIn filter returned %d rows", len(ln_clean))
        results.append(ln_clean)
    except Exception:
        logger.exception("LinkedIn filtering failed")

    try:
        logger.info("Indeed subset rows=%d", len(indeed_df))
        id_clean = filter_indeed(indeed_df, profile)
        logger.info("Indeed filter returned %d rows", len(id_clean))
        results.append(id_clean)
    except Exception:
        logger.exception("Indeed filtering failed")

    if not results:
        logger.warning("No results returned from any pipeline")
        combined = pd.DataFrame()
    else:
        combined = pd.concat(results, ignore_index=True, sort=False)

    # Ensure `job_level` exists so combined output always has the column
    if "job_level" not in combined.columns:
        combined["job_level"] = pd.NA
    else:
        combined["job_level"] = (
            combined["job_level"]
            .astype(object)
            .where(combined["job_level"].notna(), None)
        )

    return _dataframe_to_records(combined)
