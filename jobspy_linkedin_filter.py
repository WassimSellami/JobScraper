import os
import pandas as pd
from datetime import datetime
from constants import (
    POSITION_EXCLUSION_TERMS,
    COMPANY_EXCLUSION_TERMS,
    LINKEDIN_JOB_LEVEL_ALLOWED_VALUES,
    LINKEDIN_FILTERED_FILE,
    LINKEDIN_INPUT_FILE,
    LINKEDIN_AFTER_FILTER_COLUMNS,
)
from utils import has_german_requirement, GERMAN_REGEX


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

    if "id" in df.columns:
        id_series = df["id"].fillna("").astype(str).str.strip()
        has_real_id = id_series != ""

        deduped_with_id = df.loc[has_real_id].drop_duplicates(
            subset=["id"], keep="first"
        )
        rows_without_id = df.loc[~has_real_id]

        before_dedup = len(df)
        df = pd.concat([deduped_with_id, rows_without_id], ignore_index=True)
        removed_duplicates = before_dedup - len(df)
        log(
            f"After id deduplication: {len(df)} jobs (removed {removed_duplicates} duplicates; kept empty ids)"
        )
    else:
        log("WARNING: No 'id' column found; skipping deduplication")

    # Apply filters
    log("Applying filters...")

    # Filter 1: Remove rows whose title contains an exclusion term
    df_filtered = df[~df["title"].apply(has_exclusion_term)].copy()
    log(f"After title exclusion filter: {len(df_filtered)} jobs")

    # Filter 1.5: Remove rows whose company contains an exclusion term
    df_filtered = df_filtered[
        ~df_filtered["company"].apply(has_company_exclusion_term)
    ].copy()
    log(f"After company exclusion filter: {len(df_filtered)} jobs")

    # Filter 2: Keep only allowed job levels from constants
    allowed_job_levels = {value.lower() for value in LINKEDIN_JOB_LEVEL_ALLOWED_VALUES}
    df_filtered = df_filtered[
        df_filtered["job_level"].fillna("").str.lower().isin(allowed_job_levels)
    ].copy()
    log(f"After job_level inclusion filter: {len(df_filtered)} jobs")

    # Filter 3: Keep full-time, part-time, and internship roles.
    df_filtered = df_filtered[
        df_filtered["job_type"].fillna("").str.lower().isin(
            {"fulltime", "parttime", "internship"}
        )
    ].copy()
    log(f"After job_type filter (fulltime, parttime, or internship): {len(df_filtered)} jobs")

    # Filter 4: Remove jobs with German language requirement
    log("Checking German language requirements...")
    keep_rows = []
    for row_number, (idx, row) in enumerate(df_filtered.iterrows(), start=1):
        description = row.get("description", "")
        if pd.isna(description):
            description = ""
        if has_german_requirement(description):
            match = GERMAN_REGEX.search(description)
            matched_text = (
                match.group(0).strip().replace("\n", " ") if match else "(no match)"
            )
            log(f"  ❌ Skipping row {row_number} ({matched_text})")
        else:
            log(f"  ✅ Keeping row {row_number}")
            keep_rows.append(idx)

    df_filtered = df_filtered.loc[keep_rows].copy()
    log(f"After German filter: {len(df_filtered)} jobs")

    df_output = df_filtered[LINKEDIN_AFTER_FILTER_COLUMNS].reset_index(drop=True)
    job_level_order = {
        "internship": 0,
        "entry level": 1,
        "mid-senior level": 2,
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
    input_csv = LINKEDIN_INPUT_FILE
    output_csv = LINKEDIN_FILTERED_FILE

    filter_linkedin_jobs(input_csv, output_csv)
