import re

import pandas as pd

from app.constants import (
    INDEED_AFTER_FILTER_COLUMNS,
    JOB_BOARD_INDEED,
    JOB_BOARD_LINKEDIN,
    LINKEDIN_AFTER_FILTER_COLUMNS,
)
from app.schemas import UserProfile
from app.utils.german_detector import GERMAN_REGEX


def _contains_any(series: pd.Series, terms: list[str]) -> pd.Series:
    if not terms:
        return pd.Series(False, index=series.index)

    pattern = "|".join(re.escape(str(term)) for term in terms)
    return series.astype(str).str.contains(pattern, case=False, regex=True, na=False)


def _apply_common_exclusions(
    df: pd.DataFrame, profile: UserProfile
) -> pd.DataFrame:
    df_filtered = df.copy()
    if "title" in df_filtered.columns:
        excluded_titles = _contains_any(
            df_filtered["title"], profile.excluded_positions
        )
        df_filtered = df_filtered[~excluded_titles].copy()
    if "company" in df_filtered.columns:
        excluded_companies = _contains_any(
            df_filtered["company"], profile.excluded_companies
        )
        df_filtered = df_filtered[~excluded_companies].copy()
    return df_filtered


def _apply_search_term_filter(df: pd.DataFrame, profile: UserProfile) -> pd.DataFrame:
    search_terms = [
        str(term).strip()
        for term in profile.search_terms
        if str(term).strip()
    ]
    if not search_terms:
        return df

    searchable_columns = [
        column_name
        for column_name in ["_search_terms", "_search_term"]
        if column_name in df.columns
    ]
    if not searchable_columns:
        return df

    combined_text = df[searchable_columns].fillna("").astype(str).agg(" ".join, axis=1)
    search_pattern = "|".join(re.escape(term) for term in search_terms)
    if not search_pattern:
        return df

    return df[combined_text.str.contains(search_pattern, case=False, regex=True, na=False)].copy()


def _apply_german_filter(
    df: pd.DataFrame, profile: UserProfile
) -> pd.DataFrame:
    if profile.allow_deutsch:
        return df

    if "description" not in df.columns:
        return df

    has_german_requirement = (
        df["description"]
        .fillna("")
        .astype(str)
        .str.contains(GERMAN_REGEX, na=False)
    )
    return df[~has_german_requirement].copy()


def filter_linkedin(
    df: pd.DataFrame, profile: UserProfile
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=LINKEDIN_AFTER_FILTER_COLUMNS)

    df = _apply_search_term_filter(df, profile)
    df = _apply_common_exclusions(df, profile)

    allowed_job_levels = {
        str(value).strip().casefold()
        for value in profile.job_levels
        if str(value).strip()
    }
    allowed_job_levels.add("not applicable")
    if "job_level" in df.columns:
        normalized_job_levels = (
            df["job_level"].fillna("").astype(str).str.strip().str.casefold()
        )
        df = df[normalized_job_levels.isin(allowed_job_levels)].copy()

    if "job_type" in df.columns:
        df = df[df["job_type"].fillna("").astype(str).str.lower() == "fulltime"].copy()

    df["job_board"] = JOB_BOARD_LINKEDIN
    df = _apply_german_filter(df, profile)

    missing_columns = [column_name for column_name in LINKEDIN_AFTER_FILTER_COLUMNS if column_name not in df.columns]
    for column_name in missing_columns:
        df[column_name] = pd.NA

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


def filter_indeed(df: pd.DataFrame, profile: UserProfile) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=INDEED_AFTER_FILTER_COLUMNS)

    df = _apply_common_exclusions(df, profile)

    # Indeed does not use LinkedIn-specific job_level filtering.
    df = df[df["job_type"] == "fulltime"].copy()

    df = _apply_german_filter(df, profile)
    df["job_board"] = JOB_BOARD_INDEED

    df_output = df[INDEED_AFTER_FILTER_COLUMNS].reset_index(drop=True)
    if "date_posted" in df_output.columns:
        df_output = df_output.sort_values(
            by=["date_posted"], ascending=False, ignore_index=True
        )

    return df_output
