"""LinkedIn-only pipeline: scrape, filter, and clean temporary raw CSV."""

import os

from constants import LINKEDIN_FILTERED_FILE, LINKEDIN_INPUT_FILE
from job_spy_linkedin_scraper import scrape_linkedin_jobs_to_csv
from jobspy_linkedin_filter import filter_linkedin_jobs


def cleanup_temp_file(path: str):
    if path and os.path.exists(path):
        os.remove(path)


def main():
    print("Starting LinkedIn pipeline...")

    try:
        scrape_linkedin_jobs_to_csv(LINKEDIN_INPUT_FILE)
        filter_linkedin_jobs(LINKEDIN_INPUT_FILE, LINKEDIN_FILTERED_FILE)
    finally:
        cleanup_temp_file(LINKEDIN_INPUT_FILE)

    print(f"LinkedIn pipeline completed. Final output: {LINKEDIN_FILTERED_FILE}")


if __name__ == "__main__":
    main()
