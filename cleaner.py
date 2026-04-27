import pandas as pd
import re


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

    match = re.match(
        r"vor\s+(\d+)\s+(stunde|stunden|tag|tagen|woche|wochen)", text.strip().lower()
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


df = pd.read_csv("stepstone.csv")

# Keep only rows where no column contains the exact value 'Deutsch'
has_deutsch = (
    df.astype(str)
    .apply(lambda col: col.str.strip().str.fullmatch(r"Deutsch", case=False, na=False))
    .any(axis=1)
)
df = df[~has_deutsch].copy()

# Auto-detect the 4 columns by their content patterns
title_col = next(
    c
    for c in df.columns
    if df[c]
    .astype(str)
    .str.contains(r"Softwareentwickler|Developer|Engineer|Entwickler", na=False)
    .sum()
    > 3
    and not df[c].astype(str).str.contains(r"https?://", na=False).any()
)
url_col = next(
    c
    for c in df.columns
    if df[c].astype(str).str.contains("stellenangebote", na=False).any()
)
passt_col = next(
    c for c in df.columns if df[c].astype(str).str.contains("Passt", na=False).any()
)
date_col = next(
    c for c in df.columns if df[c].astype(str).str.contains(r"vor \d+", na=False).any()
)

result = df[[title_col, url_col, passt_col, date_col]].copy()
result.columns = ["position", "job_url", "match", "date"]

result["position"] = result["position"].apply(fix_encoding)

# Keep only rows with a stellenangebote URL AND all 4 columns non-null
result = result[result["job_url"].str.contains("stellenangebote", na=False)]
result = result.dropna(subset=["position", "job_url", "match", "date"]).reset_index(
    drop=True
)
result = result[
    ~result["position"]
    .astype(str)
    .str.contains(
        r"\b(Senior|Lead|Professor|Projektleiter|Manager|ERP|Defence|Architect)\b",
        case=False,
        na=False,
    )
].reset_index(drop=True)
result = result[result["match"].astype(str).str.strip() != "Passt weniger"].reset_index(
    drop=True
)
result["match"] = result["match"].replace(
    {
        "Passt hervorragend": "per",
        "Passt gut": "gut",
    }
)
result["match"] = pd.Categorical(
    result["match"],
    categories=["per", "gut"],
    ordered=True,
)
result["_date_age_days"] = result["date"].apply(date_age_in_days)
result = (
    result.sort_values(["match", "_date_age_days"], kind="stable")
    .drop(columns=["_date_age_days"])
    .reset_index(drop=True)
)

result = result[["match", "date", "position", "job_url"]]

result.to_csv("stepstone_cleaned_columns.csv", index=False)
print(f"Saved {len(result)} jobs to stepstone_cleaned_columns.csv")
