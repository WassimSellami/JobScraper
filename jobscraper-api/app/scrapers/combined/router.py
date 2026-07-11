import json
import logging

import pandas as pd
from fastapi import APIRouter, HTTPException

from .filter import filter_linkedin
from .storage import SharedJobsCsvStore
from ...constants import JOB_BOARD_LINKEDIN, SHARED_JOBS_CSV
from ...user_profiles import UserProfile

router = APIRouter()
logger = logging.getLogger(__name__)
csv_store = SharedJobsCsvStore(SHARED_JOBS_CSV)


def _dataframe_to_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


@router.post("/all")
def post_all(profile: UserProfile):
    logger.info(
        "POST /all started | terms=%d source=shared_csv board=%s",
        len(profile.search_terms),
        JOB_BOARD_LINKEDIN,
    )

    try:
        raw_df = csv_store.read(site=JOB_BOARD_LINKEDIN)
        logger.info("Shared CSV returned %d LinkedIn rows", len(raw_df))
    except Exception:
        logger.exception("Shared CSV read failed")
        raise HTTPException(status_code=500, detail="Shared CSV read failed")

    try:
        filtered = filter_linkedin(raw_df, profile)
        logger.info("LinkedIn filter returned %d rows", len(filtered))
    except Exception:
        logger.exception("LinkedIn filtering failed")
        raise HTTPException(status_code=500, detail="LinkedIn filtering failed")

    return _dataframe_to_records(filtered)
