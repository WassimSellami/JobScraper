import json
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException

from .filter import filter_linkedin
from .storage import JobsPostgresStore
from ...constants import JOB_BOARD_LINKEDIN
from ...user_profiles import UserProfile

router = APIRouter()
logger = logging.getLogger(__name__)
jobs_store = JobsPostgresStore()


def _dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.post("/all")
def post_all(profile: UserProfile):
    logger.info(
        "POST /all started | terms=%d source=database board=%s",
        len(profile.search_terms),
        JOB_BOARD_LINKEDIN,
    )

    try:
        raw_df = jobs_store.read(
            site=JOB_BOARD_LINKEDIN, last_hours=profile.last_hours
        )
        logger.info("Jobs database returned %d LinkedIn rows", len(raw_df))
    except Exception:
        logger.exception("Jobs database read failed")
        raise HTTPException(status_code=500, detail="Jobs database read failed")

    try:
        filtered = filter_linkedin(raw_df, profile)
        logger.info("LinkedIn filter returned %d rows", len(filtered))
    except Exception:
        logger.exception("LinkedIn filtering failed")
        raise HTTPException(status_code=500, detail="LinkedIn filtering failed")

    return _dataframe_to_records(filtered)
