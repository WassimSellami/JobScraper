import os
import subprocess
import sys
from datetime import datetime

from constants import (
    FULL_OUTPUT_FILE,
    GERMAN_FILTER_RECENT_OUTPUT_CSV,
    GLASSDOOR_RECENT_OUTPUT_FILE,
    LAST_DAYS,
    PROCESS_XING,
    RECENT_OUTPUT_FILE,
    PROCESS_GLASSDOOR,
    PROCESS_STEPSTONE,
    XING_FULL_OUTPUT_FILE,
    XING_GERMAN_FILTER_RECENT_OUTPUT_CSV,
    XING_RECENT_OUTPUT_FILE,
)
from german_filter import process_input_file


def run_script(script_name: str):
    print(f"Running {script_name}...")
    subprocess.run([sys.executable, script_name], check=True)


def main():
    run_date = datetime.now().strftime("%Y%m%d")

    stepstone_input = os.path.join("input", "stepstone.csv")
    glassdoor_input = os.path.join("input", "glassdoor.csv")
    xing_input = os.path.join("input", "xing.csv")

    if PROCESS_STEPSTONE and os.path.exists(stepstone_input):
        run_script("stepstone_cleaner.py")
        process_input_file(
            RECENT_OUTPUT_FILE, GERMAN_FILTER_RECENT_OUTPUT_CSV, "stepstone recent"
        )
        final = f"stepstone_recent_{LAST_DAYS}days_{run_date}.csv"
        os.replace(GERMAN_FILTER_RECENT_OUTPUT_CSV, final)
        print(f"Output: {final}")
        for f in [FULL_OUTPUT_FILE, RECENT_OUTPUT_FILE]:
            if os.path.exists(f):
                os.remove(f)

    if PROCESS_GLASSDOOR and os.path.exists(glassdoor_input):
        run_script("glassdoor_cleaner.py")
        final = f"glassdoor_recent_{LAST_DAYS}days_{run_date}.csv"
        os.replace(GLASSDOOR_RECENT_OUTPUT_FILE, final)
        print(f"Output: {final}")

    if PROCESS_XING and os.path.exists(xing_input):
        run_script("xing_cleaner.py")
        process_input_file(
            XING_RECENT_OUTPUT_FILE, XING_GERMAN_FILTER_RECENT_OUTPUT_CSV, "xing recent"
        )
        final = f"xing_recent_{LAST_DAYS}days_{run_date}.csv"
        os.replace(XING_GERMAN_FILTER_RECENT_OUTPUT_CSV, final)
        print(f"Output: {final}")
        for f in [XING_FULL_OUTPUT_FILE, XING_RECENT_OUTPUT_FILE]:
            if os.path.exists(f):
                os.remove(f)

    print("Pipeline completed.")


if __name__ == "__main__":
    main()
