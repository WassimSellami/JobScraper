import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from ...schemas import UserProfile
from .service import CombinedJobsService, JobsFilterError, JobsReadError

router = APIRouter()
logger = logging.getLogger(__name__)
service = CombinedJobsService()


@router.post("/all")
def post_all(profile: UserProfile) -> list[dict[str, Any]]:
    logger.info(
        "POST /all started | terms=%d source=database boards=linkedin,indeed",
        len(profile.search_terms),
    )

    try:
        return service.get_all(profile)
    except JobsReadError as exc:
        raise HTTPException(
            status_code=500, detail="Jobs database read failed"
        ) from exc
    except JobsFilterError as exc:
        raise HTTPException(
            status_code=500, detail="Jobs filtering failed"
        ) from exc
