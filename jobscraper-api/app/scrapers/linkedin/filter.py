import pandas as pd

from app.constants import (
    POSITION_EXCLUSION_TERMS,
    COMPANY_EXCLUSION_TERMS,
    LINKEDIN_AFTER_FILTER_COLUMNS,
)
from app.scrapers.linkedin import settings
from app.utils.german_detector import has_german_requirement


def run_filter(df: pd.DataFrame, settings) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=LINKEDIN_AFTER_FILTER_COLUMNS)

    if "id" in df.columns:
        id_series = df["id"].fillna("").astype(str).str.strip()
        has_real_id = id_series != ""
        deduped_with_id = df.loc[has_real_id].drop_duplicates(
            subset=["id"], keep="first"
        )
        rows_without_id = df.loc[~has_real_id]
        df = pd.concat([deduped_with_id, rows_without_id], ignore_index=True)

    def has_exclusion_term(title: str) -> bool:
        title_lower = str(title).lower()
        for keyword in POSITION_EXCLUSION_TERMS:
            if keyword.lower() in title_lower:
                return True
        return False

    def has_company_exclusion_term(company: str) -> bool:
        company_lower = str(company).lower()
        for keyword in COMPANY_EXCLUSION_TERMS:
            if keyword.lower() in company_lower:
                return True
        return False

    df_filtered = df[~df["title"].apply(has_exclusion_term)].copy()
    df_filtered = df_filtered[
        ~df_filtered["company"].apply(has_company_exclusion_term)
    ].copy()

    allowed_job_levels = {
        value.lower() for value in settings.LINKEDIN_JOB_LEVEL_ALLOWED_VALUES
    } | {"not applicable"}
    df_filtered = df_filtered[
        df_filtered["job_level"].fillna("").str.lower().isin(allowed_job_levels)
    ].copy()

    df_filtered = df_filtered[df_filtered["job_type"] == "fulltime"].copy()

    if not settings.ALLOW_DEUTSCH:
        keep_rows = []
        for idx, row in df_filtered.iterrows():
            description = row.get("description", "")
            if pd.isna(description):
                description = ""
            if has_german_requirement(description):
                continue
            keep_rows.append(idx)
        df_filtered = df_filtered.loc[keep_rows].copy()

    df_output = df_filtered[LINKEDIN_AFTER_FILTER_COLUMNS].reset_index(drop=True)
    job_level_order = {"entry level": 0, "mid-senior level": 1}
    df_output["_job_level_order"] = (
        df_output["job_level"].fillna("").str.lower().map(job_level_order).fillna(99)
    )
    df_output = df_output.sort_values(
        by=["_job_level_order", "date_posted"],
        ascending=[True, False],
        na_position="first",
        ignore_index=True,
    ).drop(columns=["_job_level_order"])

    return df_output
