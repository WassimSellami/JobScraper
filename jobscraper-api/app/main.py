import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .scrapers.linkedin import router as linkedin_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(linkedin_router.router, prefix="/api/scrape")


@app.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}
