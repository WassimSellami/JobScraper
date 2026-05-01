import os
import re
import pandas as pd
from datetime import datetime
from constants import (
    GERMAN_REQUIRED_PATTERNS,
    POSITION_EXCLUSION_TERMS,
    COMPANY_EXCLUSION_TERMS,
    LINKEDIN_JOB_LEVEL_ALLOWED_VALUES,
)

GERMAN_REGEX = re.compile(
    "|".join(GERMAN_REQUIRED_PATTERNS),
    flags=re.IGNORECASE,
)


def log(message: str):
    """Print timestamped log message."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)


def has_exclusion_term(title: str) -> bool:
    """Check if title contains any exclusion term from constants."""
    title_lower = str(title).lower()

    # Check for exclusion terms from POSITION_EXCLUSION_TERMS
    for keyword in POSITION_EXCLUSION_TERMS:
        if keyword.lower() in title_lower:
            return True

    return False


def has_company_exclusion_term(company: str) -> bool:
    """Check if company contains any exclusion term from constants."""
    company_lower = str(company).lower()

    # Check for exclusion terms from COMPANY_EXCLUSION_TERMS
    for keyword in COMPANY_EXCLUSION_TERMS:
        if keyword.lower() in company_lower:
            return True

    return False


def has_german_requirement(description: str) -> bool:
    """Check if description contains German language requirement."""
    if not description or pd.isna(description):
        return False

    description_text = str(description)
    match = GERMAN_REGEX.search(description_text)
    return match is not None


def filter_linkedin_jobs(input_file: str, output_file: str):
    """Filter LinkedIn jobs based on criteria."""
    log(f"Starting LinkedIn job filter")
    log(f"Input file: {input_file}")

    if not os.path.exists(input_file):
        log(f"ERROR: Input file not found: {input_file}")
        return

    log("Reading input CSV...")
    df = pd.read_csv(input_file)
    log(f"Loaded {len(df)} jobs")

    if df.empty:
        log("WARNING: Input CSV is empty")
        return

    # Apply filters
    log("Applying filters...")

    # Filter 1: Remove rows whose title contains an exclusion term
    df_filtered = df[~df["title"].apply(has_exclusion_term)].copy()
    log(f"After title exclusion filter: {len(df_filtered)} jobs")

    # Filter 1.5: Remove rows whose company contains an exclusion term
    df_filtered = df_filtered[~df_filtered["company"].apply(has_company_exclusion_term)].copy()
    log(f"After company exclusion filter: {len(df_filtered)} jobs")

    # Filter 2: Keep only allowed job levels from constants
    allowed_job_levels = {value.lower() for value in LINKEDIN_JOB_LEVEL_ALLOWED_VALUES}
    df_filtered = df_filtered[
        df_filtered["job_level"].fillna("").str.lower().isin(allowed_job_levels)
    ].copy()
    log(f"After job_level inclusion filter: {len(df_filtered)} jobs")

    # Filter 3: job_type equals "fulltime"
    df_filtered = df_filtered[df_filtered["job_type"] == "fulltime"].copy()
    log(f"After job_type filter (fulltime): {len(df_filtered)} jobs")

    # Filter 4: Remove jobs with German language requirement
    log("Checking German language requirements...")
    keep_rows = []
    for row_number, (idx, row) in enumerate(df_filtered.iterrows(), start=1):
        if has_german_requirement(row["description"]):
            log(f"  ❌ Skipping row {row_number}: German language required")
        else:
            log(f"  ✅ Keeping row {row_number}")
            keep_rows.append(idx)

    df_filtered = df_filtered.loc[keep_rows].copy()
    log(f"After German filter: {len(df_filtered)} jobs")

    columns_to_keep = [
        "job_level",
        "title",
        "date_posted",
        "company",
        "company_industry",
        "job_url",
    ]

    df_output = df_filtered[columns_to_keep].reset_index(drop=True)
    job_level_order = {
        "entry level": 0,
        "mid-senior level": 1,
    }
    df_output["_job_level_order"] = (
        df_output["job_level"].fillna("").str.lower().map(job_level_order).fillna(99)
    )
    df_output = df_output.sort_values(
        by=["_job_level_order", "date_posted"],
        ascending=[True, False],
        na_position="first",
        ignore_index=True,
    ).drop(columns=["_job_level_order"])

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    log(f"Writing output CSV: {output_file}")
    df_output.to_csv(output_file, index=False)
    log(f"Successfully saved {len(df_output)} filtered jobs to {output_file}")


if __name__ == "__main__":
    input_csv = "job_spy_linkedin_raw.csv"
    output_csv = "output/job_spy_linkedin_filtered.csv"

    filter_linkedin_jobs(input_csv, output_csv)
