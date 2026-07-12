from __future__ import annotations

import asyncio
import logging
from typing import Optional

from ...constants import PROFILE_SCRAPE_INTERVAL_SECONDS
from ...user_profiles import UserProfileStore
from ...utils.search_terms import normalize_search_terms
from .scraper import scrape_linkedin_terms
from .storage import JobsPostgresStore

logger = logging.getLogger(__name__)


class ProfileScrapeScheduler:
    def __init__(
        self,
        profile_store: Optional[UserProfileStore] = None,
        jobs_store: Optional[JobsPostgresStore] = None,
        interval_seconds: int = PROFILE_SCRAPE_INTERVAL_SECONDS,
    ):
        self.profile_store = profile_store or UserProfileStore()
        self.jobs_store = jobs_store or JobsPostgresStore()
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Started profile scrape scheduler | interval=%ss", self.interval_seconds)

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is None:
            return

        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None
            logger.info("Stopped profile scrape scheduler")

    async def run_once(self) -> int:
        terms = await asyncio.to_thread(self._collect_unique_terms)
        if not terms:
            logger.warning("No search terms found in stored profiles; skipping scrape")
            return 0

        logger.info("Running scheduled scrape for %d unique terms", len(terms))
        scraped = await asyncio.to_thread(scrape_linkedin_terms, terms)
        if scraped is None or scraped.empty:
            logger.warning("Scheduled scrape produced no rows")
            return 0

        updated_count = await asyncio.to_thread(self.jobs_store.upsert, scraped)
        logger.info("Upserted %d jobs", updated_count)
        return updated_count

    async def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                await self.run_once()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Scheduled scrape failed")

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval_seconds)
            except asyncio.TimeoutError:
                continue

    def _collect_unique_terms(self) -> list[str]:
        search_terms = [
            term
            for _, profile in self.profile_store.list_profiles()
            for term in profile.search_terms
        ]
        return normalize_search_terms(search_terms)
