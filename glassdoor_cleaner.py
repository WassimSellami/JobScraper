import pandas as pd
import re

from constants import (
    GLASSDOOR_INPUT_FILE,
    GLASSDOOR_RECENT_OUTPUT_FILE,
    POSITION_EXCLUSION_TERMS,
    LAST_DAYS,
)


def fix_encoding(text):
    if not isinstance(text, str):
        return text
    replacements = {
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
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def date_age_in_days(text):
    if not isinstance(text, str):
        return float("inf")

    m = re.fullmatch(r"(\d+)(Std|T)", text.strip())
    if not m:
        return float("inf")

    value = int(m.group(1))
    unit = m.group(2)

    if unit == "Std":
        return value / 24
    if unit == "T":
        return value

    return float("inf")


df = pd.read_csv(GLASSDOOR_INPUT_FILE)

# Auto-detect columns by content patterns
title_col = next(
    c
    for c in df.columns
    if df[c].astype(str).str.contains(r"m/w/d|all gender", na=False).any()
    and not df[c].astype(str).str.contains(r"https?://", na=False).any()
)
url_col = next(
    c
    for c in df.columns
    if df[c].astype(str).str.contains("/job-listing/", na=False).any()
    and not df[c].astype(str).str.contains("partner/jobListing", na=False).any()
)
date_col = next(
    c
    for c in df.columns
    if df[c].astype(str).str.match(r"^\d+(Std|T)$", na=False).any()
)

result = df[[title_col, url_col, date_col]].copy()
result.columns = ["position", "job_url", "date"]

result["position"] = result["position"].apply(fix_encoding)

# Keep only rows with a /job-listing/ URL and all columns non-null
result = result[result["job_url"].str.contains("/job-listing/", na=False)]
result = result.dropna(subset=["position", "job_url", "date"]).reset_index(drop=True)
result = result[
    ~result["position"]
    .astype(str)
    .str.contains(
        r"\b(" + "|".join(POSITION_EXCLUSION_TERMS) + r")\b",
        case=False,
        na=False,
    )
].reset_index(drop=True)

result["_date_age_days"] = result["date"].apply(date_age_in_days)
result = result.sort_values("_date_age_days", kind="stable").reset_index(drop=True)

result_last_x_days = result[result["_date_age_days"] <= LAST_DAYS].drop(
    columns=["_date_age_days"]
)[["date", "position", "job_url"]]

result_last_x_days.to_csv(GLASSDOOR_RECENT_OUTPUT_FILE, index=False)
print(f"Saved {len(result_last_x_days)} jobs to {GLASSDOOR_RECENT_OUTPUT_FILE}")
