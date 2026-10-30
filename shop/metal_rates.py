"""Server-side INR quotes; never expose the provider credential to browsers."""
import math
import threading
import ssl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import requests
from django.conf import settings
from django.core.cache import cache

_lock = threading.Lock()
METALS = {"XAU": ("gold_24k", "gold_22k"), "XAG": ("silver",), "XPT": ("platinum",)}

class SystemTrustAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = ssl.create_default_context()
        return super().init_poolmanager(*args, **kwargs)


def _fetch(symbol):
    with requests.Session() as session:
        session.mount("https://", SystemTrustAdapter())
        response = session.get("https://www.goldapi.io/api/" + symbol + "/INR",
        headers={"x-access-token": settings.GOLD_API_KEY}, timeout=(4, 8))
    response.raise_for_status()
    data = response.json()
    if data.get("currency") != "INR" or data.get("metal") != symbol:
        raise ValueError("Unexpected quote")
    timestamp = float(data["timestamp"])
    if not math.isfinite(timestamp) or timestamp <= 0 or timestamp > datetime.now(timezone.utc).timestamp() + 300:
        raise ValueError("Invalid quote time")
    stamp = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    values = ([data["price_gram_24k"], data["price_gram_22k"]] if symbol == "XAU"
              else [float(data["price"]) / 31.1034768])
    quotes = {}
    for key, value in zip(METALS[symbol], values):
        value = float(value)
        if not math.isfinite(value) or value <= 0:
            raise ValueError("Invalid quote")
        quotes[key] = {"value": round(value, 2), "quoted_at": stamp, "failed": False}
    return quotes

def get_rates():
    with _lock:
        cached = cache.get("metal_rates_snapshot_v1")
        if cached is not None:
            return cached
        quotes = cache.get("metal_rates_last_v1", {})
        quotes = {key: dict(value, failed=True) for key, value in quotes.items()}
        with ThreadPoolExecutor(max_workers=3) as pool:
            jobs = {symbol: pool.submit(_fetch, symbol) for symbol in METALS}
            for symbol, job in jobs.items():
                try:
                    quotes.update(job.result())
                except (requests.RequestException, ValueError, KeyError, TypeError, OverflowError):
                    pass
        now = datetime.now(timezone.utc)
        result = {"source": "GoldAPI", "currency": "INR", "unit": "gram", "quotes": {}, "refresh_seconds": 60}
        for keys in METALS.values():
            for key in keys:
                quote = quotes.get(key)
                if quote:
                    age = (now - datetime.fromisoformat(quote["quoted_at"])).total_seconds()
                    result["quotes"][key] = dict(quote, stale=quote["failed"] or age > 900)
                else:
                    result["quotes"][key] = {"value": None, "quoted_at": None, "stale": True}
        cache.set("metal_rates_last_v1", quotes, 86400)
        cache.set("metal_rates_snapshot_v1", result, 60)
        return result
