from html.parser import HTMLParser
import requests


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks = []
        self._skip_tags = {"script", "style", "noscript", "nav", "header", "footer"}
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in self._skip_tags and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self._chunks.append(stripped)

    def get_text(self):
        return " ".join(self._chunks)


def fetch_job_text(url: str, timeout: int = 15) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        parser = TextExtractor()
        parser.feed(r.text)
        return parser.get_text()
    except Exception as e:
        return f"[FETCH ERROR: {e}]"
