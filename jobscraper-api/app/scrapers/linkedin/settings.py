from pydantic import BaseModel
from typing import List


class LinkedInScraperSettings(BaseModel):
    SEARCH_TERMS: List[str] = [
        "software engineer",
        "software developer",
        "software entwickler",
        "software entwicklung",
        "full stack developer",
        "web developer",
        "web entwickler",
        "backend developer",
        "frontend developer",
    ]

    LINKEDIN_JOB_LEVEL_ALLOWED_VALUES: List[str] = [
        "entry level",
        "mid-senior level",
        "not applicable",
    ]

    LOCATION: str = "Munich, Germany"
    DISTANCE_MILES: int = 31
    HOURS_OLD: int = 24
    RESULTS_WANTED: int = 50
    ALLOW_DEUTSCH: bool = True
