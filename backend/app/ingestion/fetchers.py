import httpx
import yfinance as yf
import pandas as pd
from app.core.config import settings

class PolygonFetcher:
    BASE = "https://api.polygon.io/v2"
    async def get_aggs(self, symbol: str, from_: str, to: str,
                       timespan: str = "day") -> pd.DataFrame:
        url = f"{self.BASE}/aggs/ticker/{symbol}/range/1/{timespan}/{from_}/{to}"
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params={"apiKey": settings.POLYGON_KEY,
                                              "adjusted": True, "limit": 50000})
        r.raise_for_status()
        results = r.json().get("results", [])
        df = pd.DataFrame(results)
        df["time"] = pd.to_datetime(df["t"], unit="ms", utc=True)
        return df.rename(columns={"o":"open","h":"high","l":"low",
                                   "c":"close","v":"volume","vw":"vwap"})

class YahooFetcher:
    def get_daily(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, auto_adjust=True)
        df.index = pd.to_datetime(df.index, utc=True)
        df.index.name = "time"
        return df[["Open","High","Low","Close","Volume"]].rename(
            columns=str.lower)