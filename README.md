# JobScraper

JobScraper is a small pipeline to clean job-export CSVs (Stepstone, Glassdoor, Xing), filter out undesired roles, and detect positions that require German so you get ready-to-apply lists.

## Components

- `job_cleaner.py`: the single generic cleaner. It iterates over the enabled site configs in `constants.py`, detects the relevant columns using site-specific keywords, normalizes dates, and writes cleaned outputs.
- `german_filter.py`: fetches job pages from cleaned CSVs and applies compiled regex patterns from `constants.py` to detect German-language requirements; it produces apply-ready recent CSVs with rows that do NOT require German.
- `main.py`: orchestrates the pipeline. It runs the shared cleaner for each enabled source, then applies `german_filter.py` only for the sites whose `*_USE_GERMAN_FILTER` flag is enabled in `constants.py`, and moves the final recent files into `output/`.

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

All settings live in `constants.py`, with user-tunable switches moved to `settings.py`:

- Input filenames per source (`INPUT_FILE`, `XING_INPUT_FILE`, etc.)
- Final output folder: `OUTPUT_DIR`
- Site-specific column keywords such as `STEPSTONE_DATE_KEYWORDS`, `GLASSDOOR_URL_KEYWORDS`, and `XING_TITLE_COLUMN_KEYWORDS`
- Per-site German-filter toggles such as `STEPSTONE_USE_GERMAN_FILTER`, `GLASSDOOR_USE_GERMAN_FILTER`, and `XING_USE_GERMAN_FILTER`
- `LAST_DAYS` controls the "recent" window
- `POSITION_EXCLUSION_TERMS` lists senior/irrelevant roles to drop
- `GERMAN_REQUIRED_PATTERNS` contains regexes used by `german_filter.py` to detect German-language requirements
- `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING` toggles control which cleaners `main.py` runs
- `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING`, `GLASSDOOR_USE_GERMAN_FILTER`, `STEPSTONE_USE_GERMAN_FILTER`, `XING_USE_GERMAN_FILTER`, and `LAST_DAYS` are defined in `settings.py`

## How to run

Run the full pipeline (will respect `PROCESS_*` flags):

```bash
python main.py
```

Run the generic cleaner directly if you want to clean all enabled sites:

```bash
python job_cleaner.py
```

## Outputs

Each cleaner writes a temporary recent CSV in the project root. The final apply-ready files are written to `output/`, for example:

- `stepstone_cleaned_recent.csv` -> `output/stepstone_recent_<LAST_DAYS>days_YYYYMMDD.csv`
- `stepstone_apply_recent.csv` -> `output/stepstone_recent_<LAST_DAYS>days_YYYYMMDD.csv`
- `glassdoor_cleaned_recent.csv` -> `output/glassdoor_recent_<LAST_DAYS>days_YYYYMMDD.csv`
- `xing_cleaned_recent.csv` -> `output/xing_recent_<LAST_DAYS>days_YYYYMMDD.csv`

The temporary root files are cleaned up by `main.py` after each site finishes.

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

Run the pipeline and inspect the recent apply-ready CSVs for the last `LAST_DAYS`:

```bash
python main.py
ls output/*recent*
```

## License / Contact

This is a personal utility. If you want enhancements (more sites, better language detection, or different output formats), open an issue or edit `constants.py` and the cleaners accordingly.
