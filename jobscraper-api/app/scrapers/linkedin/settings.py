from pydantic import BaseModel
from typing import List


class LinkedInScraperSettings(BaseModel):
    SEARCH_TERMS: List[str] = []

    LINKEDIN_JOB_LEVEL_ALLOWED_VALUES: List[str] = [
        "entry level",
        "mid-senior level",
        "not applicable",
    ]

    POSITION_EXCLUSION_TERMS: List[str] = []
    COMPANY_EXCLUSION_TERMS: List[str] = []

    LOCATION: str = "Munich, Germany"
    DISTANCE_MILES: int = 31
    HOURS_OLD: int = 24
    RESULTS_WANTED: int = 10
    ALLOW_DEUTSCH: bool = False
