"""Shared cleaner for all supported job sources."""

# pyright: reportMissingImports=false, reportGeneralTypeIssues=false

import os

import pandas as pd

from constants import LAST_DAYS, POSITION_EXCLUSION_TERMS, SITE_PIPELINE_CONFIGS
from utils import fix_encoding, normalize_date_text, date_age_in_days, find_column

# ── helpers ───────────────────────────────────────────────────────────────────


def _drop_exact_value_rows(df: pd.DataFrame, exact_values: list) -> pd.DataFrame:
    for value in exact_values:
        mask = (
            df.astype(str)
            .apply(
                lambda col: col.str.strip().str.fullmatch(value, case=False, na=False)
            )
            .any(axis="columns")
        )
        df = df[~mask].copy()
    return df


def _select_columns(df: pd.DataFrame, config: dict) -> tuple[pd.DataFrame, list]:
    """Returns a renamed DataFrame and list of extra column names."""
    selected, extra_cols = [], []

    title_col = find_column(
        df,
        column_name_keywords=config.get("title_column_name_keywords"),
        content_keywords=config.get("title_content_keywords"),
        exclude_url=config.get("title_exclude_url", False),
    )
    selected.append(title_col)

    url_col = find_column(
        df,
        content_keywords=config.get("url_content_keywords"),
        excluded_columns=selected,
    )
    selected.append(url_col)

    for extra in config.get("extra_columns", []):
        col = find_column(
            df,
            content_keywords=extra.get("content_keywords"),
            excluded_columns=selected,
        )
        selected.append(col)
        extra_cols.append(extra["name"])

    date_col = find_column(
        df,
        content_keywords=config.get("date_content_keywords"),
        excluded_columns=selected,
    )
    selected.append(date_col)

    result = df[selected].copy()
    result.columns = ["position", "job_url", *extra_cols, "date"]
    return result, extra_cols


def _apply_filters(df: pd.DataFrame, site_name: str, config: dict) -> pd.DataFrame:
    df["position"] = df["position"].apply(fix_encoding)
    df["date"] = df["date"].apply(lambda v: normalize_date_text(site_name, v))

    output_cols = list(df.columns)
    df = df.dropna(subset=output_cols).reset_index(drop=True)

    df = df[
        df["job_url"].str.contains(
            "|".join(config.get("url_content_keywords", [])),
            case=False,
            na=False,
            regex=True,
        )
    ].reset_index(drop=True)

    df = df[
        ~df["position"]
        .astype(str)
        .str.contains(
            r"\b(?:" + "|".join(POSITION_EXCLUSION_TERMS) + r")\b",
            case=False,
            na=False,
        )
    ].reset_index(drop=True)

    # Site-specific column transforms (config-driven via constants)
    for col_cfg in config.get("categorical_columns", []):
        col = col_cfg["name"]
        df = df[
            df[col].astype(str).str.strip() != col_cfg.get("exclude_value", "")
        ].reset_index(drop=True)
        df[col] = df[col].replace(col_cfg.get("replacements", {}))
        df[col] = pd.Categorical(
            df[col], categories=col_cfg["categories"], ordered=True
        )

    return df


def _sort_and_split(
    df: pd.DataFrame, site_name: str, config: dict
) -> tuple[pd.DataFrame, pd.DataFrame]:
    df["_date_age_days"] = df["date"].apply(lambda v: date_age_in_days(site_name, v))

    sort_cols = config.get("sort_columns", ["_date_age_days"])
    df = df.sort_values(sort_cols, kind="stable").reset_index(drop=True)

    recent = df[df["_date_age_days"] <= LAST_DAYS].copy()
    df = df.drop(columns=["_date_age_days"])
    recent = recent.drop(columns=["_date_age_days"])

    col_order = config.get("output_column_order")
    if col_order:
        recent = recent[col_order]

    return df, recent


def _write_outputs(site_name: str, recent: pd.DataFrame, config: dict):
    path = config["recent_temp_output_file"]
    recent.to_csv(path, index=False)
    print(f"Saved {len(recent)} jobs to {path}")


# ── main pipeline ─────────────────────────────────────────────────────────────


def clean_site(site_name: str):
    config = SITE_PIPELINE_CONFIGS[site_name]
    input_file = config["input_file"]

    if not os.path.exists(input_file):
        print(f"Skipping {site_name}: input file not found: {input_file}")
        return

    print(f"Cleaning {site_name}: {input_file}")
    df = pd.read_csv(input_file)
    df = _drop_exact_value_rows(df, config.get("drop_exact_value_rows", []))
    df, _extra_cols = _select_columns(df, config)
    df = _apply_filters(df, site_name, config)
    _full, recent = _sort_and_split(df, site_name, config)
    _write_outputs(site_name, recent, config)


def main():
    for site_name, config in SITE_PIPELINE_CONFIGS.items():
        if config["enabled"]:
            clean_site(site_name)


if __name__ == "__main__":
    main()
