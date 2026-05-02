"""Utility modules for JobScraper."""

from .text_utils import fix_encoding
from .date_utils import normalize_date_text, date_age_in_days
from .column_utils import find_column
from .text_extraction import fetch_job_text, TextExtractor
from .german_detector import (
    has_german_requirement,
    process_input_file as process_german_filter,
    GERMAN_REGEX,
)

__all__ = [
    "fix_encoding",
    "normalize_date_text",
    "date_age_in_days",
    "find_column",
    "fetch_job_text",
    "TextExtractor",
    "has_german_requirement",
    "process_german_filter",
    "GERMAN_REGEX",
]
