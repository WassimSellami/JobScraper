JobScraper FastAPI backend.

Run locally:

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and replace `DATABASE_URL` with the connection
   string from the Neon dashboard. Keep `sslmode=require` in the URL.

3. Run:

```bash
uvicorn app.main:app --reload
```

To import the existing JSON profiles once, run from `jobscraper-api`:

```bash
python -m scripts.migrate_user_profiles
```

Endpoints:
 - POST /api/scrape/all — read LinkedIn and Indeed jobs from PostgreSQL, apply the user profile filters, and return JSON
 - The scheduled scraper writes directly to PostgreSQL and deduplicates jobs by URL.
This repo is ready to run as a DigitalOcean App Platform web service.

Required environment variables:

- `DATABASE_URL` is the Neon PostgreSQL connection string. The `user_profiles`
  and `jobs` tables are created automatically when the API starts.
- `CORS_ORIGINS` should contain the comma-separated frontend origins you want to allow in production.
- `LOG_LEVEL` can be set to `INFO`, `WARNING`, or `DEBUG`.
- `WEB_CONCURRENCY` optionally controls the number of Gunicorn workers. Keep it
  at `1` while the in-process scheduled scraper is enabled, otherwise every
  worker will run its own scheduler.
- `WEB_TIMEOUT` optionally controls the request timeout for long-running scrape jobs.

The app starts with Gunicorn through the `Procfile`, so no extra start command is needed on DigitalOcean.
