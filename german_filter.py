import os
import re
import time
from datetime import datetime
import pandas as pd
import requests
from html.parser import HTMLParser
from constants import (
    GERMAN_FILTER_FULL_INPUT_CSV,
    GERMAN_FILTER_FULL_OUTPUT_CSV,
    GERMAN_FILTER_REQUEST_DELAY,
    GERMAN_FILTER_RECENT_INPUT_CSV,
    GERMAN_FILTER_RECENT_OUTPUT_CSV,
    GERMAN_REQUIRED_PATTERNS,
)

REQUEST_DELAY = GERMAN_FILTER_REQUEST_DELAY

GERMAN_REGEX = re.compile(
    "|".join(GERMAN_REQUIRED_PATTERNS),
    flags=re.IGNORECASE,
)


def log(message: str):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] {message}", flush=True)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip_tags = {"script", "style", "noscript", "nav", "header", "footer"}
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self._chunks.append(stripped)

    def get_text(self):
        return " ".join(self._chunks)


def fetch_job_text(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    try:
        log(f"Fetching: {url}")
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        parser = TextExtractor()
        parser.feed(r.text)
        return parser.get_text()
    except Exception as e:
        log(f"Fetch failed: {e}")
        return f"[FETCH ERROR: {e}]"


def ensure_output_dir(path: str):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def process_input_file(input_csv: str, output_csv: str, label: str):
    log(f"Processing {label}: {input_csv} -> {output_csv}")

    if not os.path.exists(input_csv):
        log(f"Input file not found: {input_csv}")
        return

    log(f"Reading input CSV: {input_csv}")

    df = pd.read_csv(input_csv)
    log(f"Loaded {len(df)} jobs")

    if df.empty:
        log("Input CSV has no rows. Writing empty output and exiting this dataset.")
        ensure_output_dir(output_csv)
        df.to_csv(output_csv, index=False)
        log(f"Saved 0/0 jobs to {output_csv}")
        return

    keep = []
    for row_num, (_, row) in enumerate(df.iterrows(), start=1):
        print(
            f"[{row_num}/{len(df)}] {str(row['position'])[:60]}...", end=" ", flush=True
        )
        text = fetch_job_text(row["job_url"])
        m = GERMAN_REGEX.search(text)
        if m:
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            print(f"❌ skipped — «{text[start:end].strip()[:80]}»")
        else:
            print("✅ kept")
            keep.append(row)
        time.sleep(REQUEST_DELAY)

    out = pd.DataFrame(keep, columns=df.columns).reset_index(drop=True)
    log(f"Writing output CSV: {output_csv}")
    ensure_output_dir(output_csv)
    out.to_csv(output_csv, index=False)
    log(f"Saved {len(out)}/{len(df)} jobs to {output_csv}")


def main():
    log("Starting german_filter.py")
    process_input_file(
        GERMAN_FILTER_FULL_INPUT_CSV,
        GERMAN_FILTER_FULL_OUTPUT_CSV,
        label="full",
    )
    process_input_file(
        GERMAN_FILTER_RECENT_INPUT_CSV,
        GERMAN_FILTER_RECENT_OUTPUT_CSV,
        label="recent",
    )


if __name__ == "__main__":
    main()
