import os
from datetime import datetime

from constants import OUTPUT_DIR, LAST_DAYS, SITE_PIPELINE_CONFIGS
from german_filter import process_input_file
from cleaner import clean_site


def ensure_parent_dir(path: str):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def build_final_output_path(site_name: str, run_date: str) -> str:
    template = SITE_PIPELINE_CONFIGS[site_name]["final_output_template"]
    file_name = template.format(days=LAST_DAYS, date=run_date)
    return os.path.join(OUTPUT_DIR, file_name)


def cleanup_files(*paths: str):
    for path in paths:
        if path and os.path.exists(path):
            os.remove(path)


def main():
    run_date = datetime.now().strftime("%Y%m%d")

    for site_name, config in SITE_PIPELINE_CONFIGS.items():
        if not config["enabled"] or not os.path.exists(config["input_file"]):
            continue

        clean_site(site_name)

        recent_output = config["recent_temp_output_file"]
        final_output = build_final_output_path(site_name, run_date)
        ensure_parent_dir(final_output)

        if config["use_german_filter"]:
            german_filter_output = config["german_filter_temp_output_file"]
            process_input_file(
                recent_output, german_filter_output, f"{site_name} recent"
            )
            os.replace(german_filter_output, final_output)
            cleanup_files(recent_output)
        else:
            os.replace(recent_output, final_output)

        print(f"Output: {final_output}")

    print("Pipeline completed.")


if __name__ == "__main__":
    main()
