from typing import List

from pydantic import BaseModel


class CombinedScraperSettings(BaseModel):
    SEARCH_TERMS: List[str] = ["software engineer"]
    sites: List[str] = ["linkedin", "indeed"]
    POSITION_EXCLUSION_TERMS: List[str] = []
    COMPANY_EXCLUSION_TERMS: List[str] = []

    LOCATION: str = "Munich, Germany"
    DISTANCE_MILES: int = 31
    HOURS_OLD: int = 24
    RESULTS_WANTED: int = 10
    ALLOW_DEUTSCH: bool = False
    LINKEDIN_JOB_LEVEL_ALLOWED_VALUES: List[str] = [
        "entry level",
        "mid-senior level",
        "not applicable",
    ]
