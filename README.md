# JobScraper

Python backend for scraping and serving LinkedIn job listings.

**Live:** [jobscraper-frontend-5fxf.onrender.com](https://jobscraper-frontend-5fxf.onrender.com/)

**Frontend:** [github.com/WassimSellami/jobscraper-frontend](https://github.com/WassimSellami/jobscraper-frontend)

## Features

- Scrapes LinkedIn job listings via jobspy
- FastAPI backend serving job data to the frontend
- Filters jobs by search terms, level, location, and age
- German language detection to flag roles requiring German

## Setup

```bash
pip install -r requirements.txt
python main.py
```

The API runs at `http://localhost:8000`.
