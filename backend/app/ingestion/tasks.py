from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
from app.db.models import upsert_ohlcv
from app.core.config import settings
from .fetchers import PolygonFetcher

celery = Celery("equity_engine", broker=settings.REDIS_URL,
                backend=settings.REDIS_URL)

celery.conf.beat_schedule = {
    "fetch-eod-daily": {
        "task": "ingestion.tasks.fetch_eod_batch",
        "schedule": crontab(hour=18, minute=30),   # after US market close
    },
}

@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_eod_batch(self, symbols: list[str] | None = None):
    symbols = symbols or settings.WATCHLIST
    fetcher = PolygonFetcher()
    today = datetime.utcnow().strftime("%Y-%m-%d")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
    for sym in symbols:
        try:
            # Need an event loop here in practice for async, but keeping your logic!
            import asyncio
            df = asyncio.run(fetcher.get_aggs(sym, yesterday, today))
            upsert_ohlcv(df, symbol=sym, timeframe="1D", source="polygon")
        except Exception as exc:
            raise self.retry(exc=exc)