import pandas as pd

from app.constants import (
    INDEED_AFTER_FILTER_COLUMNS,
    JOB_BOARD_INDEED,
    JOB_BOARD_LINKEDIN,
    LINKEDIN_AFTER_FILTER_COLUMNS,
)
from app.utils.german_detector import has_german_requirement

from .settings import CombinedScraperSettings


def _dedupe_by_id_if_present(df: pd.DataFrame) -> pd.DataFrame:
    if "id" not in df.columns:
        return df

    id_series = df["id"].fillna("").astype(str).str.strip()
    has_real_id = id_series != ""
    deduped_with_id = df.loc[has_real_id].drop_duplicates(subset=["id"], keep="first")
    rows_without_id = df.loc[~has_real_id]
    return pd.concat([deduped_with_id, rows_without_id], ignore_index=True)


def _apply_common_exclusions(
    df: pd.DataFrame, settings: CombinedScraperSettings
) -> pd.DataFrame:
    def has_exclusion_term(title: str) -> bool:
        title_lower = str(title).lower()
        for keyword in settings.POSITION_EXCLUSION_TERMS:
            if keyword.lower() in title_lower:
                return True
        return False

    def has_company_exclusion_term(company: str) -> bool:
        company_lower = str(company).lower()
        for keyword in settings.COMPANY_EXCLUSION_TERMS:
            if keyword.lower() in company_lower:
                return True
        return False

    df_filtered = df[~df["title"].apply(has_exclusion_term)].copy()
    df_filtered = df_filtered[
        ~df_filtered["company"].apply(has_company_exclusion_term)
    ].copy()
    return df_filtered


def _apply_german_filter(
    df: pd.DataFrame, settings: CombinedScraperSettings
) -> pd.DataFrame:
    if settings.ALLOW_DEUTSCH:
        return df

    keep_rows = []
    for idx, row in df.iterrows():
        description = row.get("description", "")
        if pd.isna(description):
            description = ""
        if has_german_requirement(description):
            continue
        keep_rows.append(idx)

    return df.loc[keep_rows].copy()


def filter_linkedin(
    df: pd.DataFrame, settings: CombinedScraperSettings
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=LINKEDIN_AFTER_FILTER_COLUMNS)

    df = _dedupe_by_id_if_present(df)
    df = _apply_common_exclusions(df, settings)

    allowed_job_levels = {
        value.lower() for value in settings.LINKEDIN_JOB_LEVEL_ALLOWED_VALUES
    } | {"not applicable"}
    df = df[df["job_level"].fillna("").str.lower().isin(allowed_job_levels)].copy()
    df = df[df["job_type"] == "fulltime"].copy()

    df["job_board"] = JOB_BOARD_LINKEDIN
    df = _apply_german_filter(df, settings)

    df_output = df[LINKEDIN_AFTER_FILTER_COLUMNS].reset_index(drop=True)
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


def filter_indeed(df: pd.DataFrame, settings: CombinedScraperSettings) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=INDEED_AFTER_FILTER_COLUMNS)

    df = _dedupe_by_id_if_present(df)
    df = _apply_common_exclusions(df, settings)

    # Indeed does not use LinkedIn-specific job_level filtering.
    df = df[df["job_type"] == "fulltime"].copy()

    df = _apply_german_filter(df, settings)
    df["job_board"] = JOB_BOARD_INDEED

    df_output = df[INDEED_AFTER_FILTER_COLUMNS].reset_index(drop=True)
    if "date_posted" in df_output.columns:
        df_output = df_output.sort_values(
            by=["date_posted"], ascending=False, ignore_index=True
        )

    return df_output
