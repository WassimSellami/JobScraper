import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .autocomplete import router as autocomplete_router
from .config import (
    APP_NAME,
    CORS_ALLOW_CREDENTIALS,
    CORS_ORIGINS,
    LOG_LEVEL,
)
from .database import close_database, initialize_database
from .scrapers.combined import router as combined_router
from .scrapers.combined.background import ProfileScrapeScheduler
from .scrapers.combined.storage import initialize_jobs_database
from .user_profiles_router import router as user_profiles_router

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = ProfileScrapeScheduler()
    app.state.profile_scrape_scheduler = scheduler

    try:
        await asyncio.to_thread(initialize_database)
        await asyncio.to_thread(initialize_jobs_database)
        scheduler.start()
        yield
    finally:
        await scheduler.stop()
        await asyncio.to_thread(close_database)


app = FastAPI(title=APP_NAME, lifespan=lifespan)

if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("CORS is disabled because no CORS_ORIGINS were configured")

app.include_router(autocomplete_router.router, prefix="/api/autocomplete")
app.include_router(combined_router.router, prefix="/api/scrape")
app.include_router(user_profiles_router, prefix="/api/user-profiles")

@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}
