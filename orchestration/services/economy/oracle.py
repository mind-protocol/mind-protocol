"""Price oracle backed by Helius price endpoint."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx

from .settings import EconomySettings

logger = logging.getLogger(__name__)


class PriceOracle:
    """Fetches USD/MIND rates with caching."""

    def __init__(self, settings: EconomySettings) -> None:
        self._settings = settings
        self._cache_value: Optional[float] = None
        self._cache_expires_at: float = 0.0
        self._client: Optional[httpx.AsyncClient] = None
        self._lock = asyncio.Lock()

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_usd_per_mind(self) -> float:
        """Return USD price for one MIND token."""
        async with self._lock:
            now = time.time()
            if self._cache_value is not None and now < self._cache_expires_at:
                return self._cache_value

            price = await self._fetch_price()
            if price is None:
                price = self._settings.mind_usd_fallback

            self._cache_value = price
            self._cache_expires_at = now + self._settings.price_ttl_seconds
            return price

    async def _fetch_price(self) -> Optional[float]:
        if not self._settings.has_price_oracle:
            logger.debug("Price oracle disabled (missing mint or API key)")
            return None

        client = await self._ensure_client()
        url = f"{self._settings.helius_base_url.rstrip('/')}/v0/price"
        params = {"ids": self._settings.mind_mint, "api-key": self._settings.helius_api_key}

        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Helius price fetch failed: %s", exc)
            return None

        data: Dict[str, Any] = response.json()
        prices = data.get("prices")
        if not isinstance(prices, dict):
            logger.warning("Unexpected price payload: %s", data)
            return None

        entry = prices.get(self._settings.mind_mint)
        if not isinstance(entry, dict):
            logger.warning("Price entry missing for mint %s", self._settings.mind_mint)
            return None

        price = entry.get("price")
        if price is None:
            logger.warning("Price payload missing 'price' field: %s", entry)
            return None

        try:
            return float(price)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            logger.warning("Invalid price value %s", price)
            return None
