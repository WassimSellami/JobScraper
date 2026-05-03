import json
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import LINKEDIN_RESULTS_FILE
from .settings import LinkedInScraperSettings
from .scraper import run_scraper
from .filter import run_filter

router = APIRouter()
logger = logging.getLogger(__name__)


def _dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.post("/linkedin")
def post_linkedin(settings: LinkedInScraperSettings):
    logger.info(
        "POST /linkedin started | terms=%d location=%s hours_old=%s results_wanted=%s",
        len(settings.SEARCH_TERMS),
        settings.LOCATION,
        settings.HOURS_OLD,
        settings.RESULTS_WANTED,
    )
    try:
        df = run_scraper(settings)
        logger.info("Scraper returned %d rows", len(df))
        cleaned = run_filter(df, settings)
        logger.info("Filter returned %d rows", len(cleaned))
        cleaned.to_csv(LINKEDIN_RESULTS_FILE, index=False)
        logger.info("Saved latest LinkedIn results to %s", LINKEDIN_RESULTS_FILE)
        return _dataframe_to_records(cleaned)
    except Exception as e:
        logger.exception("POST /linkedin failed with unhandled exception")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@router.get("/linkedin/export")
def get_linkedin_export():
    logger.info("GET /linkedin/export called")
    if not LINKEDIN_RESULTS_FILE.exists() or LINKEDIN_RESULTS_FILE.stat().st_size == 0:
        logger.warning("Export requested but no results are available")
        raise HTTPException(status_code=404, detail="No results available")

    logger.info("Exporting results from %s", LINKEDIN_RESULTS_FILE)
    return FileResponse(
        path=LINKEDIN_RESULTS_FILE,
        media_type="text/csv",
        filename="linkedin_results.csv",
    )
