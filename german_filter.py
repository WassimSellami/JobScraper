import os
import re
import time
from datetime import datetime
import pandas as pd
import requests
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
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
        prefix = f"[{row_num}/{len(df)}]"
        text = fetch_job_text(row["job_url"])
        m = GERMAN_REGEX.search(text)
        if m:
            matched_text = m.group(0).strip().replace("\n", " ")
            print(f"{prefix} ❌ skipped (match: {matched_text})")
        else:
            print(f"{prefix} ✅ kept")
            keep.append(row)
        time.sleep(REQUEST_DELAY)

    out = pd.DataFrame(keep, columns=df.columns).reset_index(drop=True)
    log(f"Writing output CSV: {output_csv}")
    ensure_output_dir(output_csv)
    out.to_csv(output_csv, index=False)
    log(f"Saved {len(out)}/{len(df)} jobs to {output_csv}")


def process_input_file_playwright(input_csv: str, output_csv: str, label: str):
    """Like process_input_file but uses a real Chromium browser to bypass Cloudflare/403."""
    log(f"Processing {label} (playwright): {input_csv} -> {output_csv}")

    if not os.path.exists(input_csv):
        log(f"Input file not found: {input_csv}")
        return

    df = pd.read_csv(input_csv)
    log(f"Loaded {len(df)} jobs")

    if df.empty:
        log("Input CSV has no rows. Writing empty output.")
        ensure_output_dir(output_csv)
        df.to_csv(output_csv, index=False)
        log(f"Saved 0/0 jobs to {output_csv}")
        return

    keep = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            locale="de-DE",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        for row_num, (_, row) in enumerate(df.iterrows(), start=1):
            prefix = f"[{row_num}/{len(df)}]"
            url = row["job_url"]
            try:
                page.goto(url, timeout=30000, wait_until="domcontentloaded")
                # Wait briefly for any JS-rendered content
                page.wait_for_timeout(2000)
                text = page.inner_text("body")
            except Exception as e:
                log(f"Playwright fetch failed for {url}: {e}")
                text = f"[FETCH ERROR: {e}]"

            m = GERMAN_REGEX.search(text)
            if m:
                matched_text = m.group(0).strip().replace("\n", " ")
                print(f"{prefix} ❌ skipped (match: {matched_text})")
            else:
                print(f"{prefix} ✅ kept")
                keep.append(row)
            time.sleep(REQUEST_DELAY)

        browser.close()

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
