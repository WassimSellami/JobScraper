# JobScraper

JobScraper is a small pipeline to clean job-export CSVs (Stepstone, Glassdoor, Xing), filter out undesired roles, and detect positions that require German so you get ready-to-apply lists.

## Components

**Core modules:**
- `cleaner.py`: the orchestration-only cleaner. Iterates over enabled site configs in `constants.py`, delegates to focused helpers, and writes cleaned outputs.
- `text_utils.py`: handles encoding fixes for garbled Unicode characters.
- `date_utils.py`: normalizes date text and converts relative dates to days-ago using config-driven pattern dispatch (no if/site_name branches).
- `column_utils.py`: auto-detects CSV columns using content and name keywords.
- `german_filter.py`: fetches job pages from cleaned CSVs and applies compiled regex patterns from `constants.py` to detect German-language requirements; it produces apply-ready recent CSVs with rows that do NOT require German.
- `main.py`: orchestrates the full pipeline. Runs the shared cleaner for each enabled source, then applies `german_filter.py` only for sites whose `*_USE_GERMAN_FILTER` flag is enabled in `constants.py`, and moves final recent files into `output/`.
- `main_linkedin.py`: orchestrates the LinkedIn jobspy pipeline.

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

All settings live in `constants.py`, with user-tunable switches split by pipeline:

- Input filenames per source (`STEPSTONE_INPUT_FILE`, `XING_INPUT_FILE`, etc.)
- Final output folder: `OUTPUT_DIR`
- Site-specific column keywords such as `STEPSTONE_DATE_KEYWORDS`, `GLASSDOOR_URL_KEYWORDS`, and `XING_TITLE_COLUMN_KEYWORDS`
- Per-site German-filter toggles such as `STEPSTONE_USE_GERMAN_FILTER`, `GLASSDOOR_USE_GERMAN_FILTER`, and `XING_USE_GERMAN_FILTER`
- `LAST_DAYS` controls the "recent" window
- `POSITION_EXCLUSION_TERMS` lists senior/irrelevant roles to drop
- `GERMAN_REQUIRED_PATTERNS` contains regexes used by `german_filter.py` to detect German-language requirements
- `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING` toggles control which cleaners `main.py` runs
- `settings_general.py` holds the general scraper toggles and shared timing window
- `settings_jobspy.py` holds the LinkedIn jobspy search and filter parameters

**Per-site configuration in `SITE_PIPELINE_CONFIGS` dictionary:**
- `sort_columns` — which columns to sort by (e.g., stepstone sorts by `["match", "_date_age_days"]`)
- `output_column_order` — final column arrangement in output CSV
- `categorical_columns` — site-specific categorical transformations (e.g., stepstone's match levels: "per", "gut")
- All existing config keys for column detection, URL filtering, date parsing, etc.

Settings from `settings_general.py`: `PROCESS_STEPSTONE`, `PROCESS_GLASSDOOR`, `PROCESS_XING`, `GLASSDOOR_USE_GERMAN_FILTER`, `STEPSTONE_USE_GERMAN_FILTER`, `XING_USE_GERMAN_FILTER`, and `LAST_DAYS`

Settings from `settings_jobspy.py`: `SEARCH_TERMS`, `LINKEDIN_JOB_LEVEL_ALLOWED_VALUES`, `LOCATION`, `DISTANCE_MILES`, `HOURS_OLD`, and `RESULTS_WANTED`

## How to run

Run the full pipeline (will respect `PROCESS_*` flags):

```bash
python main.py
```

Run the generic cleaner directly if you want to clean all enabled sites:

```bash
python cleaner.py
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

## Architecture

The pipeline is designed for **config-driven, site-specific behavior**:

- **No if/site_name branches** — all site differences are config entries in `SITE_PIPELINE_CONFIGS`
- **Focused modules** — each utility has a single responsibility:
  - `text_utils.fix_encoding()` — encoding fixes only
  - `date_utils.date_age_in_days()` — uses dispatch table for pattern matching (xing, glassdoor, stepstone)
  - `column_utils.find_column()` — intelligent column detection
  - `cleaner.py` — pure orchestration, no site-specific logic
- **Dispatch-table date parsing** — adding a new site means adding one pattern entry to `_RELATIVE_PATTERNS` in `date_utils.py`, not editing long if/elif chains
- **Easy testing** — each helper is independently testable with no global state

## Notes & behavior

- `german_filter.py` performs live HTTP fetches of job URLs; adjust `GERMAN_FILTER_REQUEST_DELAY` in `constants.py` to slow down requests.
- Regex patterns in `constants.py` are intentionally broad and include many German phrasing variants (e.g., `fließend`, `C1`, `Deutsch- und Englischkenntnisse`, `sprichst fließend Deutsch`). Add more patterns there as needed.
- To add a new job source: create a config entry in `SITE_PIPELINE_CONFIGS`, add date patterns to `date_utils.py` if needed, and set column keywords in `constants.py`.

## Example

Run the pipeline and inspect the recent apply-ready CSVs for the last `LAST_DAYS`:

```bash
python main.py
ls output/*recent*
```

## License / Contact

This is a personal utility. If you want enhancements (more sites, better language detection, or different output formats), simply:
- Add a config entry to `SITE_PIPELINE_CONFIGS` in `constants.py`
- Add date patterns to `_RELATIVE_PATTERNS` in `date_utils.py` if the site uses a new date format
- Tune the keyword filters in `constants.py` for your target role

The refactored architecture makes these additions straightforward without touching the core `cleaner.py`.
