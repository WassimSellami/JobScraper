import os

from dotenv import load_dotenv

load_dotenv()


def _parse_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


def _parse_csv_env(name: str, default: str) -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


APP_NAME = os.getenv("APP_NAME", "jobscraper-api")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
if LOG_LEVEL not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
    raise ValueError("LOG_LEVEL must be CRITICAL, ERROR, WARNING, INFO, or DEBUG")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

CORS_ORIGINS = _parse_csv_env(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:4200,http://127.0.0.1:4200",
)

CORS_ALLOW_CREDENTIALS = _parse_bool_env("CORS_ALLOW_CREDENTIALS", True)
