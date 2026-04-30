"""Date normalization and age calculation utilities."""

import re

_RELATIVE_PATTERNS = {
    "xing": [
        (r"just now|today", lambda _v, _u: 0),
        (r"yesterday", lambda _v, _u: 1),
        (
            r"(\d+)\s+(hour|hours|day|days|week|weeks|month|months|year|years)\s+ago",
            lambda v, u: {
                "hour": v / 24,
                "hours": v / 24,
                "day": v,
                "days": v,
                "week": v * 7,
                "weeks": v * 7,
                "month": v * 30,
                "months": v * 30,
                "year": v * 365,
                "years": v * 365,
            }.get(u, float("inf")),
        ),
    ],
    "glassdoor": [
        (
            r"(\d+)(std|t)",
            lambda v, u: v / 24 if u == "std" else v,
        ),
    ],
    "stepstone": [
        (
            r"vor\s+(\d+)\s+(stunde|stunden|tag|tagen|woche|wochen)",
            lambda v, u: {
                "stunde": v / 24,
                "stunden": v / 24,
                "tag": v,
                "tagen": v,
                "woche": v * 7,
                "wochen": v * 7,
            }.get(u, float("inf")),
        ),
    ],
}


def normalize_date_text(site_name: str, text):
    if not isinstance(text, str):
        return text
    normalized = text.strip()
    if site_name in {"stepstone", "xing"}:
        normalized = re.sub(r"^posted\s+", "", normalized, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", normalized)


def date_age_in_days(site_name: str, text) -> float:
    if not isinstance(text, str):
        return float("inf")

    value_text = normalize_date_text(site_name, text).lower()
    patterns = _RELATIVE_PATTERNS.get(
        site_name, _RELATIVE_PATTERNS.get("stepstone", [])
    )

    for pattern, calculator in patterns:
        match = re.fullmatch(pattern, value_text)
        if match:
            groups = match.groups()
            v = int(groups[0]) if groups and groups[0].isdigit() else 0
            u = groups[1] if len(groups) > 1 else ""
            return calculator(v, u)

    return float("inf")
