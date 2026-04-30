"""Shared cleaner for all supported job sources."""

# pyright: reportMissingImports=false, reportGeneralTypeIssues=false

import os
import re

import pandas as pd

from constants import LAST_DAYS, POSITION_EXCLUSION_TERMS, SITE_PIPELINE_CONFIGS

ENCODING_REPLACEMENTS = {
    'â€"': "–",
    "â€™": "'",
    "Ã¼": "ü",
    "Ã¶": "ö",
    "Ã¤": "ä",
    "Ã–": "Ö",
    "Ã„": "Ä",
    "Ãœ": "Ü",
    "ÃŸ": "ß",
    "â‚¬": "€",
}


def fix_encoding(text):
    if not isinstance(text, str):
        return text

    for old, new in ENCODING_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def normalize_date_text(site_name: str, text):
    if not isinstance(text, str):
        return text

    normalized = text.strip()
    if site_name in {"stepstone", "xing"}:
        normalized = re.sub(r"^posted\s+", "", normalized, flags=re.IGNORECASE)

    return re.sub(r"\s+", " ", normalized)


def date_age_in_days(site_name: str, text):
    if not isinstance(text, str):
        return float("inf")

    value_text = normalize_date_text(site_name, text).lower()

    if site_name == "xing":
        if value_text in {"just now", "today"}:
            return 0
        if value_text == "yesterday":
            return 1

        match = re.fullmatch(
            r"(\d+)\s+(hour|hours|day|days|week|weeks|month|months|year|years)\s+ago",
            value_text,
        )
        if not match:
            return float("inf")

        value = int(match.group(1))
        unit = match.group(2)

        if unit in {"hour", "hours"}:
            return value / 24
        if unit in {"day", "days"}:
            return value
        if unit in {"week", "weeks"}:
            return value * 7
        if unit in {"month", "months"}:
            return value * 30
        if unit in {"year", "years"}:
            return value * 365

        return float("inf")

    if site_name == "glassdoor":
        match = re.fullmatch(r"(\d+)(std|t)", value_text)
        if not match:
            return float("inf")

        value = int(match.group(1))
        unit = match.group(2)
        if unit == "std":
            return value / 24
        if unit == "t":
            return value
        return float("inf")

    match = re.match(
        r"vor\s+(\d+)\s+(stunde|stunden|tag|tagen|woche|wochen)", value_text
    )
    if not match:
        return float("inf")

    value = int(match.group(1))
    unit = match.group(2)

    if unit in {"stunde", "stunden"}:
        return value / 24
    if unit in {"tag", "tagen"}:
        return value
    if unit in {"woche", "wochen"}:
        return value * 7

    return float("inf")


def column_contains_keywords(series: pd.Series, keywords):
    return any(
        series.astype(str).str.contains(keyword, case=False, na=False, regex=True).any()
        for keyword in keywords
    )


def find_column(
    df: pd.DataFrame,
    *,
    column_name_keywords=None,
    content_keywords=None,
    excluded_columns=None,
    exclude_url=False,
):
    excluded_columns = set(excluded_columns or [])
    best_column = None
    best_score = -1

    for column in df.columns:
        if column in excluded_columns:
            continue

        column_name = column.lower()
        if column_name_keywords and not any(
            keyword.lower() in column_name for keyword in column_name_keywords
        ):
            continue

        series = df[column].astype(str)
        if exclude_url and series.str.contains(r"https?://", na=False).any():
            continue

        if content_keywords:
            matches = sum(
                series.str.contains(keyword, case=False, na=False, regex=True).sum()
                for keyword in content_keywords
            )
            if matches == 0:
                continue
            if matches > best_score:
                best_column = column
                best_score = matches
            continue

        return column

    if best_column is not None:
        return best_column

    raise ValueError(
        "Could not auto-detect a column for "
        f"name keywords={column_name_keywords} content keywords={content_keywords}"
    )


def drop_position_exclusions(df: pd.DataFrame):
    return df[
        ~df["position"]
        .astype(str)
        .str.contains(
            r"\b(?:" + "|".join(POSITION_EXCLUSION_TERMS) + r")\b",
            case=False,
            na=False,
        )
    ].reset_index(drop=True)


def write_outputs(site_name: str, result: pd.DataFrame, recent_result: pd.DataFrame):
    config = SITE_PIPELINE_CONFIGS[site_name]

    recent_output_file = config["recent_temp_output_file"]
    recent_result.to_csv(recent_output_file, index=False)
    print(f"Saved {len(recent_result)} jobs to {recent_output_file}")


def clean_site(site_name: str):
    config = SITE_PIPELINE_CONFIGS[site_name]
    input_file = config["input_file"]

    if not os.path.exists(input_file):
        print(f"Skipping {site_name}: input file not found: {input_file}")
        return

    print(f"Cleaning {site_name}: {input_file}")
    df = pd.read_csv(input_file)

    for exact_value in config.get("drop_exact_value_rows", []):
        has_exact_value = (
            df.astype(str)
            .apply(
                lambda col: col.str.strip().str.fullmatch(
                    exact_value, case=False, na=False
                )
            )
            .any(axis="columns")
        )
        df = df[~has_exact_value].copy()

    selected_columns = []

    title_col = find_column(
        df,
        column_name_keywords=config.get("title_column_name_keywords"),
        content_keywords=config.get("title_content_keywords"),
        exclude_url=config.get("title_exclude_url", False),
    )
    selected_columns.append(title_col)

    url_col = find_column(
        df,
        content_keywords=config.get("url_content_keywords"),
        excluded_columns=selected_columns,
    )
    selected_columns.append(url_col)

    extra_columns = []
    for extra_column in config.get("extra_columns", []):
        column = find_column(
            df,
            content_keywords=extra_column.get("content_keywords"),
            excluded_columns=selected_columns,
        )
        selected_columns.append(column)
        extra_columns.append((column, extra_column["name"]))

    date_col = find_column(
        df,
        content_keywords=config.get("date_content_keywords"),
        excluded_columns=selected_columns,
    )
    selected_columns.append(date_col)

    result: pd.DataFrame = df[selected_columns].copy()

    output_columns = ["position", "job_url"]
    output_columns.extend(name for _, name in extra_columns)
    output_columns.append("date")
    result.columns = output_columns

    result["position"] = result["position"].apply(fix_encoding)
    result["date"] = result["date"].apply(
        lambda value: normalize_date_text(site_name, value)
    )
    result = result.dropna(subset=output_columns).reset_index(drop=True)
    result = result[
        result["job_url"].str.contains(
            "|".join(config.get("url_content_keywords", [])),
            case=False,
            na=False,
            regex=True,
        )
    ].reset_index(drop=True)
    result = drop_position_exclusions(result)

    if site_name == "stepstone":
        result = result[
            result["match"].astype(str).str.strip() != "Passt weniger"
        ].reset_index(drop=True)
        result["match"] = result["match"].replace(
            {"Passt hervorragend": "per", "Passt gut": "gut"}
        )
        result["match"] = pd.Categorical(
            result["match"], categories=["per", "gut"], ordered=True
        )

    result["_date_age_days"] = result["date"].apply(
        lambda value: date_age_in_days(site_name, value)
    )

    if site_name == "stepstone":
        result = result.sort_values(
            ["match", "_date_age_days"], kind="stable"
        ).reset_index(drop=True)
    elif site_name == "xing":
        result = result.sort_values(
            ["_date_age_days", "position"], kind="stable"
        ).reset_index(drop=True)
    else:
        result = result.sort_values("_date_age_days", kind="stable").reset_index(
            drop=True
        )

    recent_result = result[result["_date_age_days"] <= LAST_DAYS].drop(
        columns=["_date_age_days"]
    )
    result = result.drop(columns=["_date_age_days"])

    if site_name == "stepstone":
        recent_result = recent_result[["match", "date", "position", "job_url"]]
    else:
        recent_result = recent_result[["date", "position", "job_url"]]

    write_outputs(site_name, result, recent_result)


def main():
    for site_name, config in SITE_PIPELINE_CONFIGS.items():
        if config["enabled"]:
            clean_site(site_name)


if __name__ == "__main__":
    main()
