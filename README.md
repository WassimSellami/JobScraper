# JobScraper

JobScraper is a small pipeline to clean job-export CSVs (Stepstone, Glassdoor, Xing), filter out undesired roles, and detect positions that require German so you get ready-to-apply lists.

## Components

- `stepstone_cleaner.py`: cleans Stepstone CSVs. Auto-detects title/url/date columns, removes excluded senior roles, and emits a full cleaned file and a recent cleaned file (last `LAST_DAYS`).
- `glassdoor_cleaner.py`: cleans Glassdoor CSVs following the same pattern (full/recent outputs).
- `xing_cleaner.py`: cleans Xing CSVs; it auto-detects columns and normalizes English relative-date strings like `3 hours ago`, `2 days ago`, `Yesterday`, and `Just now`, producing full/recent outputs.
- `german_filter.py`: fetches job pages from cleaned CSVs and applies compiled regex patterns from `constants.py` to detect German-language requirements; it produces apply-ready CSVs (full and recent) with rows that do NOT require German.
- `main.py`: orchestrates the pipeline. It runs the enabled cleaners (controlled by `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING` in `constants.py`), then runs `german_filter.py` on the recent outputs and renames results with the execution date.

## Requirements

- Python 3.10+
- Dependencies:
  - `pandas`
  - `requests`

Install:

```bash
pip install pandas requests
```

## Configuration

All settings live in `constants.py`:

- Input/output filenames per source (`INPUT_FILE`, `XING_INPUT_FILE`, etc.)
- `LAST_DAYS` controls the "recent" window
- `POSITION_EXCLUSION_TERMS` lists senior/irrelevant roles to drop
- `GERMAN_REQUIRED_PATTERNS` contains regexes used by `german_filter.py` to detect German-language requirements
- `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING` toggles control which cleaners `main.py` runs

## How to run

Run the full pipeline (will respect `PROCESS_*` flags):

```bash
python main.py
```

If you only want a specific cleaner, run its module directly (example):

```bash
python xing_cleaner.py
python glassdoor_cleaner.py
python stepstone_cleaner.py
```

## Outputs

Each cleaner writes two cleaned CSVs (full and recent). After `german_filter.py` runs you'll get apply-ready files, for example:

- `stepstone_cleaned_full.csv`
- `stepstone_cleaned_recent.csv`
- `stepstone_apply_full_YYYYMMDD.csv`
- `stepstone_apply_recent_<LAST_DAYS>days_YYYYMMDD.csv`

And likewise for `glassdoor` and `xing` (filenames configured in `constants.py`).

## Git / housekeeping

- The repo `.gitignore` includes a Python baseline and ignores `*.csv`, `*.pyc`, and `__pycache__/` directories. If CSVs were already committed, untrack them with:

```bash
git rm --cached input/*.csv
git rm --cached *.csv
git commit -m "Stop tracking CSV outputs"
```

## Notes & behavior

- `german_filter.py` performs live HTTP fetches of job URLs; adjust `GERMAN_FILTER_REQUEST_DELAY` in `constants.py` to slow down requests.
- Regex patterns in `constants.py` are intentionally broad and include many German phrasing variants (e.g., `fließend`, `C1`, `Deutsch- und Englischkenntnisse`, `sprichst fließend Deutsch`). Add more patterns there as needed.

## Example

Run the pipeline and inspect the recent apply-ready CSV for the last `LAST_DAYS`:

```bash
python main.py
ls *apply_recent*
```

## License / Contact

This is a personal utility. If you want enhancements (more sites, better language detection, or different output formats), open an issue or edit `constants.py` and the cleaners accordingly.
