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
- GET /api/autocomplete/cities?q=<fragment>&limit=5 — German city autocomplete (returns up to 5 items with city and label)

## DigitalOcean deployment

This repo is ready to run as a DigitalOcean App Platform web service.

Required environment variables:

- `CORS_ORIGINS` should contain the comma-separated frontend origins you want to allow in production.
- `LOG_LEVEL` can be set to `INFO`, `WARNING`, or `DEBUG`.
- `WEB_CONCURRENCY` optionally controls the number of Gunicorn workers.
- `WEB_TIMEOUT` optionally controls the request timeout for long-running scrape jobs.
- `RESULTS_DIR` optionally overrides where the latest LinkedIn export CSV is stored.

The app starts with Gunicorn through the `Procfile`, so no extra start command is needed on DigitalOcean.
