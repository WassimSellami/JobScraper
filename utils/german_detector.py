"""German language requirement detection for job postings."""

import os
import re
import pandas as pd
from constants import GERMAN_REQUIRED_PATTERNS

GERMAN_REGEX = re.compile(
    "|".join(GERMAN_REQUIRED_PATTERNS),
    flags=re.IGNORECASE,
)


def has_german_requirement(text: str) -> bool:
    """Check if text contains a German language requirement.

    Args:
        text: The text to check (e.g., job description).

    Returns:
        True if German requirement is detected, False otherwise.
    """
    if not text or not isinstance(text, str):
        return False
    return GERMAN_REGEX.search(text) is not None


def _ensure_output_dir(path: str):
    """Create parent directories for output file if needed."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def process_input_file(
    input_csv: str,
    output_csv: str,
    get_job_text_func,
    label: str,
    log_func=None,
):
    """Filter a CSV file based on German language requirement detection.

    Args:
        input_csv: Path to input CSV file (must have 'job_url' column).
        output_csv: Path to write filtered output CSV.
        get_job_text_func: Callable that takes a URL and returns job text.
        label: Human-readable label for logging.
        log_func: Optional logging function (default prints to stdout).
    """
    if log_func is None:
        log_func = print

    log_func(f"Processing {label}: {input_csv} -> {output_csv}")

    if not os.path.exists(input_csv):
        log_func(f"Input file not found: {input_csv}")
        return

    log_func(f"Reading input CSV: {input_csv}")
    df = pd.read_csv(input_csv)
    log_func(f"Loaded {len(df)} jobs")

    if df.empty:
        log_func("Input CSV has no rows. Writing empty output and exiting.")
        _ensure_output_dir(output_csv)
        df.to_csv(output_csv, index=False)
        log_func(f"Saved 0/0 jobs to {output_csv}")
        return

    keep = []
    for row_num, (_, row) in enumerate(df.iterrows(), start=1):
        prefix = f"[{row_num}/{len(df)}]"
        text = get_job_text_func(row["job_url"])
        match = GERMAN_REGEX.search(text)
        if match:
            matched_text = match.group(0).strip().replace("\n", " ")
            log_func(f"{prefix} ❌ skipped (match: {matched_text})")
        else:
            log_func(f"{prefix} ✅ kept")
            keep.append(row)

    out = pd.DataFrame(keep, columns=df.columns).reset_index(drop=True)
    log_func(f"Writing output CSV: {output_csv}")
    _ensure_output_dir(output_csv)
    out.to_csv(output_csv, index=False)
    log_func(f"Saved {len(out)}/{len(df)} jobs to {output_csv}")
