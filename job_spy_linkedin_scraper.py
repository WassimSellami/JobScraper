import csv
import os
import pandas as pd
from jobspy import scrape_jobs
from settings_jobspy import (
    DISTANCE_MILES,
    HOURS_OLD,
    LOCATION,
    RESULTS_WANTED,
    SEARCH_TERMS,
)
from constants import LINKEDIN_INPUT_FILE, LINKEDIN_OUTPUT_COLUMNS


def search_jobs(search_term: str) -> pd.DataFrame:
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            location=LOCATION,
            distance=DISTANCE_MILES,
            hours_old=HOURS_OLD,
            results_wanted=RESULTS_WANTED,
            linkedin_fetch_description=True,
            verbose=1,
        )
        print(f"[{search_term}] Found {len(jobs)} results")
        return jobs
    except Exception as e:
        print(f"[{search_term}] Error: {e}")
        return pd.DataFrame()


def scrape_linkedin_jobs_to_csv(output_file: str):
    all_results = []

    for term in SEARCH_TERMS:
        df = search_jobs(term)
        if not df.empty:
            all_results.append(df)

    if not all_results:
        print("No jobs found.")
        return

    combined = pd.concat(all_results, ignore_index=True)

    available_cols = [c for c in LINKEDIN_OUTPUT_COLUMNS if c in combined.columns]
    output = combined[available_cols].copy()

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    output.to_csv(
        output_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False
    )
    print(f"Saved to '{output_file}'")


def main():
    scrape_linkedin_jobs_to_csv(LINKEDIN_INPUT_FILE)


if __name__ == "__main__":
    main()
