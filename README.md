# JobScraper

This tool helps you clean a Stepstone jobs CSV and keep only roles that are more suitable for your profile. It removes unwanted listings and gives you ready-to-apply output files.

## What it does

1. `cleaner.py`
- Reads raw input CSV (`stepstone.csv`)
- Auto-detects title/url/match/date columns
- Filters out unwanted senior roles
- Produces two intermediate files:
  - full cleaned file
  - recent cleaned file (last `LAST_DAYS`)

2. `german_filter.py`
- Reads the two cleaned files
- Opens each job URL
- Uses regex patterns to detect German language requirements
- Skips matching jobs and keeps the rest
- Produces two apply-ready files:
  - `stepstone_apply_full.csv`
  - `stepstone_apply_recent.csv`

3. `main.py`
- Runs `cleaner.py`
- Runs `german_filter.py`
- Renames final outputs with execution date (and recent days)
- Deletes intermediate cleaned files

## Requirements

- Python 3.10+
- Packages:
  - `pandas`
  - `requests`

Install dependencies:

```bash
pip install pandas requests
```

## How to run

Run the full pipeline:

```bash
python main.py
```

## Final outputs

After `main.py`, you will get files like:

- `stepstone_apply_full_YYYYMMDD.csv`
- `stepstone_apply_recent_<LAST_DAYS>days_YYYYMMDD.csv`

Example:

- `stepstone_apply_full_20260427.csv`
- `stepstone_apply_recent_2days_20260427.csv`

## Configuration

All tunable settings are in `constants.py`, including:

- Input/output file names
- `LAST_DAYS` for recent filtering
- Position exclusion terms
- German-language regex patterns
- Request delay for URL checks

## Notes

- `german_filter.py` logs each checked row as:
  - `[i/n] ✅ kept`
  - `[i/n] ❌ skipped (match: ...)`
- Request speed is controlled by `GERMAN_FILTER_REQUEST_DELAY`.
