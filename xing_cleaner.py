import pandas as pd
import re

from constants import (
    LAST_DAYS,
    POSITION_EXCLUSION_TERMS,
    XING_FULL_OUTPUT_FILE,
    XING_INPUT_FILE,
    XING_RECENT_OUTPUT_FILE,
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
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def normalize_date_text(text):
    if not isinstance(text, str):
        return text

    text = text.strip()
    text = re.sub(r"^posted\s+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text


def date_age_in_days(text):
    if not isinstance(text, str):
        return float("inf")

    value_text = normalize_date_text(text).lower()

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


df = pd.read_csv(XING_INPUT_FILE)

url_col = next(
    c
    for c in df.columns
    if (
        df[c]
        .astype(str)
        .str.contains(r"(?:www\.)?xing\.com/jobs/|/jobs/", case=False, na=False)
        .any()
    )
)

title_col = next(
    c
    for c in df.columns
    if "headline" in c.lower()
    and not df[c].astype(str).str.contains(r"https?://", na=False).any()
)

date_col = next(
    c
    for c in df.columns
    if df[c]
    .astype(str)
    .str.strip()
    .str.contains(
        r"^(?:\d+\s+(?:hour|hours|day|days|week|weeks|month|months|year|years)\s+ago|yesterday|just now|today)$",
        case=False,
        regex=True,
        na=False,
    )
    .any()
)

result = df[[title_col, url_col, date_col]].copy()
result.columns = ["position", "job_url", "date"]

result["position"] = result["position"].apply(fix_encoding)
result["date"] = result["date"].apply(normalize_date_text)

result = result[
    result["job_url"].str.contains(
        r"(?:www\.)?xing\.com/jobs/|/jobs/", case=False, na=False
    )
]
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
result = result.sort_values(["_date_age_days", "position"], kind="stable").reset_index(
    drop=True
)

result_last_x_days = result[result["_date_age_days"] <= LAST_DAYS].drop(
    columns=["_date_age_days"]
)

result = result.drop(columns=["_date_age_days"])

result = result[["date", "position", "job_url"]]
result_last_x_days = result_last_x_days[["date", "position", "job_url"]]

result.to_csv(XING_FULL_OUTPUT_FILE, index=False)
result_last_x_days.to_csv(XING_RECENT_OUTPUT_FILE, index=False)
print(f"Saved {len(result)} jobs to {XING_FULL_OUTPUT_FILE}")
print(f"Saved {len(result_last_x_days)} jobs to {XING_RECENT_OUTPUT_FILE}")
