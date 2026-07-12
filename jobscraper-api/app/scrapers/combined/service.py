import json
import logging
from typing import Any

import pandas as pd

from ...constants import JOB_BOARD_INDEED, JOB_BOARD_LINKEDIN
from ...schemas import UserProfile
from .filter import filter_indeed, filter_linkedin
from .storage import JobsPostgresStore

logger = logging.getLogger(__name__)


class JobsReadError(RuntimeError):
    pass


class JobsFilterError(RuntimeError):
    pass


class CombinedJobsService:
    def __init__(self, jobs_store: JobsPostgresStore | None = None) -> None:
        self.jobs_store = jobs_store or JobsPostgresStore()

    def get_all(self, profile: UserProfile) -> list[dict[str, Any]]:
        try:
            linkedin_df = self.jobs_store.read(
                site=JOB_BOARD_LINKEDIN,
                last_hours=profile.last_hours,
            )
            indeed_df = self.jobs_store.read(
                site=JOB_BOARD_INDEED,
                last_hours=profile.last_hours,
            )
            logger.info(
                "Jobs database returned %d LinkedIn rows and %d Indeed rows",
                len(linkedin_df),
                len(indeed_df),
            )
        except Exception as exc:
            logger.exception("Jobs database read failed")
            raise JobsReadError from exc

        try:
            filtered_linkedin = filter_linkedin(linkedin_df, profile)
            filtered_indeed = filter_indeed(indeed_df, profile)
            records = self._dataframe_to_records(filtered_linkedin)
            records.extend(self._dataframe_to_records(filtered_indeed))
            logger.info(
                "Filters returned %d LinkedIn rows and %d Indeed rows",
                len(filtered_linkedin),
                len(filtered_indeed),
            )
            return records
        except Exception as exc:
            logger.exception("Jobs filtering failed")
            raise JobsFilterError from exc

    @staticmethod
    def _dataframe_to_records(df: pd.DataFrame) -> list[dict[str, Any]]:
        return json.loads(df.to_json(orient="records", date_format="iso"))
