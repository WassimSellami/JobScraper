import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .autocomplete import router as autocomplete_router
from .config import APP_NAME, CORS_ALLOW_CREDENTIALS, CORS_ORIGINS, LOG_LEVEL
from .scrapers.combined import router as combined_router
from .user_profiles_router import router as user_profiles_router

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title=APP_NAME)

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
