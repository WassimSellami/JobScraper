from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    search_terms: list[str] = Field(default_factory=lambda: ["software engineer"])
    job_levels: list[str] = Field(
        default_factory=lambda: [
            "entry level",
            "mid-senior level",
            "not applicable",
        ]
    )
    excluded_companies: list[str] = Field(default_factory=list)
    excluded_positions: list[str] = Field(default_factory=list)
    allow_deutsch: bool = False
    last_hours: int = Field(default=24, ge=0)


class UserProfileRecord(UserProfile):
    profile_id: str
