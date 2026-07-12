def normalize_search_terms(search_terms: list[str]) -> list[str]:
    normalized_terms: list[str] = []
    seen: set[str] = set()

    for term in search_terms:
        normalized = str(term).strip()
        term_key = normalized.casefold()
        if not normalized or term_key in seen:
            continue

        seen.add(term_key)
        normalized_terms.append(normalized)

    return normalized_terms
