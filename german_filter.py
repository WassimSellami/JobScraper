import time
from datetime import datetime
from constants import GERMAN_FILTER_REQUEST_DELAY, SITE_PIPELINE_CONFIGS
from utils.text_extraction import fetch_job_text
from utils.german_detector import process_input_file as filter_german_requirement

REQUEST_DELAY = GERMAN_FILTER_REQUEST_DELAY


def log(message: str):
    """Print timestamped log message."""
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)


def _fetch_job_text_with_delay(url: str) -> str:
    """Fetch job text and apply request delay to avoid rate limiting."""
    text = fetch_job_text(url)
    time.sleep(REQUEST_DELAY)
    return text


def process_input_file(input_csv: str, output_csv: str, label: str):
    """Wrapper for backward compatibility with main.py.

    Filters a CSV file based on German language requirements,
    fetching live job pages and applying request delays.
    """
    filter_german_requirement(
        input_csv,
        output_csv,
        _fetch_job_text_with_delay,
        label=label,
        log_func=log,
    )


def main():
    """Orchestrate German filter for all enabled sites."""
    log("Starting german_filter.py")
    for site_name, config in SITE_PIPELINE_CONFIGS.items():
        if not config["enabled"] or not config.get("use_german_filter", False):
            continue

        filter_german_requirement(
            config["recent_temp_output_file"],
            config["german_filter_temp_output_file"],
            _fetch_job_text_with_delay,
            label=f"{site_name} recent",
            log_func=log,
        )


if __name__ == "__main__":
    main()
