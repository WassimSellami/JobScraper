import csv
import pandas as pd
from jobspy import scrape_jobs

SEARCH_TERMS = [
    "software engineer",
    "software developer",
    "software entwickler",
    "software entwicklung",
    "full stack developer",
    "backend developer",
    "frontend developer",
]

LOCATION = "Munich, Germany"
DISTANCE_MILES = 31
HOURS_OLD = 48

OUTPUT_COLUMNS = [
    "title",
    "description",
    "job_level",
    "company_industry",
    "date_posted",
    "job_url",
    "company",
    "location",
    "job_type",
]

OUTPUT_FILE = "job_spy_linkedin_raw.csv"


def search_jobs(search_term: str) -> pd.DataFrame:
    try:
        jobs = scrape_jobs(
            site_name=["linkedin"],
            search_term=search_term,
            location=LOCATION,
            distance=DISTANCE_MILES,
            hours_old=HOURS_OLD,
            results_wanted=100,
            linkedin_fetch_description=True,
            verbose=1,
        )
        print(f"[{search_term}] Found {len(jobs)} results")
        return jobs
    except Exception as e:
        print(f"[{search_term}] Error: {e}")
        return pd.DataFrame()


def main():
    all_results = []

    for term in SEARCH_TERMS:
        df = search_jobs(term)
        if not df.empty:
            all_results.append(df)

    if not all_results:
        print("No jobs found.")
        return

    combined = pd.concat(all_results, ignore_index=True)
    before = len(combined)
    combined.drop_duplicates(subset=["job_url"], inplace=True)
    print(
        f"\nTotal unique jobs: {len(combined)} (removed {before - len(combined)} duplicates)"
    )

    available_cols = [c for c in OUTPUT_COLUMNS if c in combined.columns]
    output = combined[available_cols].copy()

    output.to_csv(
        OUTPUT_FILE, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False
    )
    print(f"Saved to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
