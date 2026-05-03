import os
import tempfile
from pathlib import Path


def _parse_csv_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


APP_NAME = os.getenv("APP_NAME", "jobscraper-api")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

CORS_ORIGINS = _parse_csv_env(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)

CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}

RESULTS_DIR = Path(
    os.getenv("RESULTS_DIR", str(Path(tempfile.gettempdir()) / "jobscraper-api"))
)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LINKEDIN_RESULTS_FILE = RESULTS_DIR / "linkedin_results.csv"
