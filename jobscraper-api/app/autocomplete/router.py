import json
import logging
import unicodedata
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Query

router = APIRouter()
logger = logging.getLogger(__name__)

_CITIES_FILE = Path(__file__).resolve().parents[1] / "german-cities.json"
_DEFAULT_LIMIT = 5
_MAX_LIMIT = 20


@lru_cache(maxsize=1)
def _load_cities() -> tuple[dict, ...]:
    with _CITIES_FILE.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    cities: list[dict] = []
    seen: set[str] = set()

    for item in raw:
        city = (item.get("name") or "").strip()
        if not city:
            continue

        key = _normalize(city)
        if key in seen:
            continue

        seen.add(key)

        aliases: list[str] = [city]
        for alt in item.get("alts", []):
            alt_text = (alt or "").strip()
            if alt_text:
                aliases.append(alt_text)

        searchable = [_normalize(v) for v in aliases if v]
        cities.append({"city": city, "aliases": aliases, "searchable": searchable})

    logger.info("Loaded %d unique cities for autocomplete", len(cities))
    return tuple(cities)


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).casefold()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.split())


def _rank_match(query: str, candidate: str) -> tuple[int, int, int] | None:
    if candidate == query:
        return (0, 0, len(candidate))

    if candidate.startswith(query):
        return (1, 0, len(candidate))

    words = candidate.split()
    if any(word.startswith(query) for word in words):
        return (2, 0, len(candidate))

    idx = candidate.find(query)
    if idx != -1:
        return (3, idx, len(candidate))

    return None


@router.get("/cities")
def get_city_autocomplete(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=_DEFAULT_LIMIT, ge=1, le=_MAX_LIMIT),
):
    query = _normalize(q)
    matches: list[tuple[tuple[int, int, int], str]] = []

    for city_data in _load_cities():
        best_score: tuple[int, int, int] | None = None
        for searchable in city_data["searchable"]:
            score = _rank_match(query, searchable)
            if score is None:
                continue
            if best_score is None or score < best_score:
                best_score = score

        if best_score is not None:
            matches.append((best_score, city_data["city"]))

    matches.sort(key=lambda item: (item[0], item[1]))

    return [{"city": city_name, "label": city_name} for _, city_name in matches[:limit]]
