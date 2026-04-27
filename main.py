import os
import subprocess
import sys
from datetime import datetime

from constants import (
    FULL_OUTPUT_FILE,
    GERMAN_FILTER_FULL_OUTPUT_CSV,
    GERMAN_FILTER_RECENT_OUTPUT_CSV,
    LAST_DAYS,
    RECENT_OUTPUT_FILE,
)


def run_script(script_name: str):
    print(f"Running {script_name}...")
    subprocess.run([sys.executable, script_name], check=True)


def add_suffix_to_filename(path: str, suffix: str) -> str:
    base, ext = os.path.splitext(path)
    return f"{base}_{suffix}{ext}"


def rename_output_files(run_date: str):
    full_target = add_suffix_to_filename(
        GERMAN_FILTER_FULL_OUTPUT_CSV,
        run_date,
    )
    recent_target = add_suffix_to_filename(
        GERMAN_FILTER_RECENT_OUTPUT_CSV,
        f"{LAST_DAYS}days_{run_date}",
    )

    if os.path.exists(GERMAN_FILTER_FULL_OUTPUT_CSV):
        os.replace(GERMAN_FILTER_FULL_OUTPUT_CSV, full_target)
        print(f"Renamed {GERMAN_FILTER_FULL_OUTPUT_CSV} -> {full_target}")
    else:
        print(f"Warning: missing output {GERMAN_FILTER_FULL_OUTPUT_CSV}")

    if os.path.exists(GERMAN_FILTER_RECENT_OUTPUT_CSV):
        os.replace(GERMAN_FILTER_RECENT_OUTPUT_CSV, recent_target)
        print(f"Renamed {GERMAN_FILTER_RECENT_OUTPUT_CSV} -> {recent_target}")
    else:
        print(f"Warning: missing output {GERMAN_FILTER_RECENT_OUTPUT_CSV}")


def cleanup_intermediate_files():
    for file_path in [FULL_OUTPUT_FILE, RECENT_OUTPUT_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted intermediate file: {file_path}")


def main():
    run_date = datetime.now().strftime("%Y%m%d")

    run_script("cleaner.py")
    run_script("german_filter.py")

    rename_output_files(run_date)
    cleanup_intermediate_files()

    print("Pipeline completed.")


if __name__ == "__main__":
    main()
