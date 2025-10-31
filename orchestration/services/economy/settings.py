"""
Configuration helpers for economy services.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict


def _parse_json_env(name: str, default: Dict[str, str]) -> Dict[str, str]:
    raw = os.getenv(name)
    if not raw:
        return dict(default)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"{name} must be valid JSON (got {raw!r})") from None

    if not isinstance(value, dict):
        raise ValueError(f"{name} must decode to an object mapping, got {type(value).__name__}")

    return {str(k): str(v) for k, v in value.items()}


@dataclass(frozen=True)
class EconomySettings:
    """Runtime settings for economy services."""

    org_id: str = field(default_factory=lambda: os.getenv("ECONOMY_ORG_ID", "mind-protocol_org"))
    l2_graph: str = field(default_factory=lambda: os.getenv("ECONOMY_L2_GRAPH", "mind-protocol_org"))
    redis_url: str = field(default_factory=lambda: os.getenv("ECONOMY_REDIS_URL", "redis://localhost:6379/0"))
    throttle_interval_seconds: int = field(default_factory=lambda: int(os.getenv("ECONOMY_THROTTLE_INTERVAL", "60")))
    policy_refresh_seconds: int = field(default_factory=lambda: int(os.getenv("ECONOMY_POLICY_REFRESH", "300")))
    spend_alpha: float = field(default_factory=lambda: float(os.getenv("ECONOMY_SPEND_ALPHA", "0.2")))
    roi_alpha: float = field(default_factory=lambda: float(os.getenv("ECONOMY_ROI_ALPHA", "0.5")))
    wallet_floor_multiplier: float = field(default_factory=lambda: float(os.getenv("ECONOMY_WALLET_FLOOR_MULT", "0.4")))
    lane_wallets: Dict[str, str] = field(default_factory=lambda: _parse_json_env("ECONOMY_LANE_WALLETS", {}))

    mind_mint: str = field(default_factory=lambda: os.getenv("MIND_MINT_ADDRESS", ""))
    helius_api_key: str = field(default_factory=lambda: os.getenv("HELIUS_API_KEY", ""))
    helius_base_url: str = field(default_factory=lambda: os.getenv("HELIUS_BASE_URL", "https://api.helius.xyz"))
    mind_usd_fallback: float = field(default_factory=lambda: float(os.getenv("MIND_USD_FALLBACK", "1.0")))
    price_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("ECONOMY_PRICE_TTL", "300")))

    ubc_daily: float = field(default_factory=lambda: float(os.getenv("UBC_DAILY", "100.0")))
    ubc_treasury_wallet: str = field(default_factory=lambda: os.getenv("UBC_TREASURY_WALLET", ""))
    ubc_citizen_wallets: Dict[str, str] = field(
        default_factory=lambda: _parse_json_env("UBC_CITIZEN_WALLETS", {})
    )
    ubc_start_offset_seconds: int = field(default_factory=lambda: int(os.getenv("UBC_CRON_OFFSET_SECONDS", "0")))

    @property
    def has_price_oracle(self) -> bool:
        return bool(self.mind_mint and self.helius_api_key)
