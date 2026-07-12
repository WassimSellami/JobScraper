import re

from app.constants import GERMAN_REQUIRED_PATTERNS

GERMAN_REGEX = re.compile("|".join(GERMAN_REQUIRED_PATTERNS), flags=re.IGNORECASE)


def has_german_requirement(text: str) -> bool:
    if not text or not isinstance(text, str):
        return False
    return GERMAN_REGEX.search(text) is not None
