import io
import json
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from .settings import LinkedInScraperSettings
from .scraper import run_scraper
from .filter import run_filter

router = APIRouter()
logger = logging.getLogger(__name__)

_last_results: pd.DataFrame | None = None


def _dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.post("/linkedin")
def post_linkedin(settings: LinkedInScraperSettings):
    global _last_results
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
        _last_results = cleaned
        return _dataframe_to_records(cleaned)
    except Exception as e:
        logger.exception("POST /linkedin failed with unhandled exception")
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {e}")


@router.get("/linkedin/export")
def get_linkedin_export():
    logger.info("GET /linkedin/export called")
    if _last_results is None or _last_results.empty:
        logger.warning("Export requested but no results are available")
        raise HTTPException(status_code=404, detail="No results available")

    stream = io.StringIO()
    _last_results.to_csv(stream, index=False)
    stream.seek(0)
    headers = {"Content-Disposition": "attachment; filename=linkedin_results.csv"}
    logger.info("Exporting %d rows", len(_last_results))
    return StreamingResponse(stream, media_type="text/csv", headers=headers)
