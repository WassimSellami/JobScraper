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
 - POST /api/scrape/all — read LinkedIn jobs from the shared CSV, apply the user profile filters, and return JSON
 - The endpoint is LinkedIn-only for now and uses `app/data/shared_jobs.csv` as its source
This repo is ready to run as a DigitalOcean App Platform web service.

Required environment variables:

- `CORS_ORIGINS` should contain the comma-separated frontend origins you want to allow in production.
- `LOG_LEVEL` can be set to `INFO`, `WARNING`, or `DEBUG`.
- `WEB_CONCURRENCY` optionally controls the number of Gunicorn workers.
- `WEB_TIMEOUT` optionally controls the request timeout for long-running scrape jobs.

The app starts with Gunicorn through the `Procfile`, so no extra start command is needed on DigitalOcean.
