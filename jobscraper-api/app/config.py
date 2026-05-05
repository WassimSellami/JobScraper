import os


def _parse_csv_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


APP_NAME = os.getenv("APP_NAME", "jobscraper-api")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

CORS_ORIGINS = _parse_csv_env(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200",
)

CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
