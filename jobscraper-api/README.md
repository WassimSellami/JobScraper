JobScraper FastAPI backend.

Run locally:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run:

```bash
uvicorn app.main:app --reload
```

Endpoints:

- POST /api/scrape/linkedin — run scraper and filter, returns JSON list of jobs
- GET /api/scrape/linkedin/export — download last results as CSV
