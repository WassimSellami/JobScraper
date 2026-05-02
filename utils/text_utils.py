"""Text encoding and normalization utilities."""

ENCODING_REPLACEMENTS = {
    'â€"': "–",
    "â€™": "'",
    "Ã¼": "ü",
    "Ã¶": "ö",
    "Ã¤": "ä",
    "Ã–": "Ö",
    "Ã„": "Ä",
    "Ãœ": "Ü",
    "ÃŸ": "ß",
    "â‚¬": "€",
}


def fix_encoding(text):
    if not isinstance(text, str):
        return text
    for old, new in ENCODING_REPLACEMENTS.items():
        text = text.replace(old, new)
    return text
