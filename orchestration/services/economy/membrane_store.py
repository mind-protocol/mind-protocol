"""Redis-backed membrane economy store."""

from __future__ import annotations
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from redis.asyncio import Redis  # type: ignore


def _to_float(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class MembraneStore:
    """Tracks rolling spend, ROI, wallet balances, and lane throttles."""

    def __init__(
        self,
        redis_url: str,
        *,
        spend_alpha: float = 0.2,
        ledger_maxlen: int = 2048,
    ) -> None:
        self._redis = Redis.from_url(redis_url, decode_responses=True)
        self._spend_alpha = max(0.0, min(1.0, spend_alpha))
        self._ledger_maxlen = max(128, ledger_maxlen)

    # ------------------------------------------------------------------ lifecycle

    async def close(self) -> None:
        await self._redis.close()

    # ------------------------------------------------------------------ key helpers

    @staticmethod
    def _lane_budget_key(org_id: str, lane: str) -> str:
        return f"{org_id}:budget:lane:{lane}"

    @staticmethod
    def _lane_roi_key(org_id: str, lane: str) -> str:
        return f"{org_id}:roi_ema:lane:{lane}"

    @staticmethod
    def _lane_spent_key(org_id: str, lane: str) -> str:
        return f"{org_id}:spent:lane:{lane}"

    @staticmethod
    def _econ_ledger_key(org_id: str) -> str:
        return f"{org_id}:ledger:econ"

    @staticmethod
    def _ubc_ledger_key(org_id: str) -> str:
        return f"{org_id}:ledger:ubc"

    @staticmethod
    def _wallet_balance_key(org_id: str, wallet_node: str) -> str:
        return f"{org_id}:balance:{wallet_node}"

    @staticmethod
    def _wallet_spent_stream(org_id: str, wallet_node: str) -> str:
        return f"{org_id}:spent:node:{wallet_node}"

    @staticmethod
    def _wallet_spent_window_key(org_id: str, wallet_node: str) -> str:
        return f"{org_id}:spent:node:{wallet_node}:60s"

    @staticmethod
    def _wallet_next_ubc_key(org_id: str, wallet_node: str) -> str:
        return f"{org_id}:ubc:next_eta:{wallet_node}"

    # ------------------------------------------------------------------ lane metrics

    async def set_lane_budget(self, org_id: str, lane: str, *, soft_cap: float, budget_remaining: Optional[float] = None) -> None:
        key = self._lane_budget_key(org_id, lane)
        mapping: Dict[str, str] = {
            "soft_cap": str(max(soft_cap, 0.0)),
            "updated_at": str(time.time()),
        }
        if budget_remaining is not None:
            mapping["budget_remaining"] = str(budget_remaining)
        await self._redis.hset(key, mapping=mapping)

    async def adjust_budget(self, org_id: str, lane: str, delta: float) -> float:
        key = self._lane_budget_key(org_id, lane)
        new_value = await self._redis.hincrbyfloat(key, "budget_remaining", delta)
        await self._redis.hset(key, mapping={"updated_at": str(time.time())})
        return float(new_value)

    async def get_lane_snapshot(self, org_id: str, lane: str) -> Dict[str, float]:
        budget_key = self._lane_budget_key(org_id, lane)
        roi_key = self._lane_roi_key(org_id, lane)

        budget_data, roi_data = await self._redis.hmget(
            budget_key,
            "soft_cap",
            "budget_remaining",
            "spent_rolling",
            "throttle",
            "last_f_lane",
            "last_h_roi",
            "last_g_wallet",
        ), await self._redis.hgetall(roi_key)

        soft_cap = _to_float(budget_data[0], 0.0)
        budget_remaining = _to_float(budget_data[1], 0.0)
        spent_rolling = _to_float(budget_data[2], 0.0)
        throttle = _to_float(budget_data[3], 0.0)
        last_f_lane = _to_float(budget_data[4], 1.0)
        last_h_roi = _to_float(budget_data[5], 1.0)
        last_g_wallet = _to_float(budget_data[6], 1.0)

        roi_ema = _to_float(roi_data.get("ema"), 1.0)

        spent_window = await self._redis.get(self._lane_spent_key(org_id, lane))

        return {
            "soft_cap": soft_cap,
            "budget_remaining": budget_remaining,
            "spent_rolling": spent_rolling,
            "roi_ema": roi_ema,
            "throttle": throttle,
            "f_lane": last_f_lane,
            "h_roi": last_h_roi,
            "g_wallet": last_g_wallet,
            "spent_60s": _to_float(spent_window, 0.0),
        }

    async def record_charge(
        self,
        org_id: str,
        lane: str,
        amount_mind: float,
        *,
        roi_sample: Optional[float] = None,
        citizen_id: Optional[str] = None,
        wallet_node: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, float]:
        """Update spend metrics for a lane and append ledger entry."""

        if amount_mind <= 0:
            return await self.get_lane_snapshot(org_id, lane)

        budget_key = self._lane_budget_key(org_id, lane)
        roi_key = self._lane_roi_key(org_id, lane)
        spent_key = self._lane_spent_key(org_id, lane)

        # Fetch previous values
        pipe = self._redis.pipeline()
        pipe.hget(budget_key, "spent_rolling")
        pipe.hget(roi_key, "ema")
        spent_prev_raw, roi_prev_raw = await pipe.execute()

        spent_prev = float(spent_prev_raw) if spent_prev_raw is not None else 0.0
        roi_prev = float(roi_prev_raw) if roi_prev_raw is not None else 1.0

        alpha = self._spend_alpha
        spent_new = (1 - alpha) * spent_prev + alpha * abs(amount_mind)
        roi_new = roi_prev
        if roi_sample is not None:
            roi_new = (1 - alpha) * roi_prev + alpha * max(roi_sample, 0.0)

        timestamp = time.time()
        iso_ts = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

        # Update Redis state
        pipe = self._redis.pipeline()
        pipe.hincrbyfloat(budget_key, "budget_remaining", -abs(amount_mind))
        pipe.hset(
            budget_key,
            mapping={
                "spent_rolling": str(spent_new),
                "updated_at": str(timestamp),
            },
        )
        pipe.hset(
            roi_key,
            mapping={
                "ema": str(roi_new),
                "updated": str(timestamp),
            },
        )
        pipe.set(spent_key, str(spent_new), ex=60)
        await pipe.execute()

        # Append ledger entry
        ledger_entry = {
            "lane": lane,
            "amount_mind": f"{amount_mind:.6f}",
            "roi_sample": f"{roi_sample:.6f}" if roi_sample is not None else "",
            "citizen_id": citizen_id or "",
            "timestamp": iso_ts,
        }
        if metadata:
            for key, value in metadata.items():
                ledger_entry[f"meta_{key}"] = str(value)

        await self._redis.xadd(
            self._econ_ledger_key(org_id),
            ledger_entry,
            maxlen=self._ledger_maxlen,
            approximate=True,
        )

        # Wallet balance + rolling spend for citizen
        if wallet_node:
            await self.adjust_wallet_balance(org_id, wallet_node, -abs(amount_mind))
            await self._record_wallet_spend(org_id, wallet_node, abs(amount_mind), timestamp)

        budget_remaining_str = await self._redis.hget(budget_key, "budget_remaining")

        return {
            "spent_rolling": spent_new,
            "budget_remaining": _to_float(budget_remaining_str, 0.0),
            "roi_ema": roi_new,
        }

    async def set_throttle(
        self,
        org_id: str,
        lane: str,
        throttle_value: float,
        *,
        f_lane: float,
        h_roi: float,
        g_wallet: float,
    ) -> None:
        key = self._lane_budget_key(org_id, lane)
        await self._redis.hset(
            key,
            mapping={
                "throttle": str(throttle_value),
                "last_f_lane": str(f_lane),
                "last_h_roi": str(h_roi),
                "last_g_wallet": str(g_wallet),
                "throttle_updated_at": str(time.time()),
            },
        )

    async def get_lane_throttle(self, org_id: str, lane: str) -> float:
        value = await self._redis.hget(self._lane_budget_key(org_id, lane), "throttle")
        return _to_float(value, 1.0)

    # ------------------------------------------------------------------ wallet helpers

    async def get_wallet_balance(self, org_id: str, wallet_node: str) -> float:
        value = await self._redis.get(self._wallet_balance_key(org_id, wallet_node))
        return _to_float(value, 0.0)

    async def adjust_wallet_balance(self, org_id: str, wallet_node: str, delta: float) -> float:
        key = self._wallet_balance_key(org_id, wallet_node)
        value = await self._redis.incrbyfloat(key, delta)
        return float(value)

    async def set_wallet_balance(self, org_id: str, wallet_node: str, balance: float) -> None:
        key = self._wallet_balance_key(org_id, wallet_node)
        await self._redis.set(key, str(balance))

    async def set_wallet_next_ubc(self, org_id: str, wallet_node: str, eta_iso: str) -> None:
        await self._redis.set(self._wallet_next_ubc_key(org_id, wallet_node), eta_iso)

    async def get_wallet_next_ubc(self, org_id: str, wallet_node: str) -> Optional[str]:
        return await self._redis.get(self._wallet_next_ubc_key(org_id, wallet_node))

    async def record_ubc_ledger(self, org_id: str, entry: Dict[str, Any]) -> None:
        payload = {key: str(value) for key, value in entry.items()}
        await self._redis.xadd(
            self._ubc_ledger_key(org_id),
            payload,
            maxlen=self._ledger_maxlen,
            approximate=True,
        )

    async def _record_wallet_spend(self, org_id: str, wallet_node: str, amount: float, timestamp: float) -> None:
        stream_key = self._wallet_spent_stream(org_id, wallet_node)
        member = f"{timestamp}:{amount:.6f}"
        window_key = self._wallet_spent_window_key(org_id, wallet_node)

        pipe = self._redis.pipeline()
        pipe.zadd(stream_key, {member: timestamp})
        cutoff = timestamp - 60.0
        pipe.zremrangebyscore(stream_key, 0, cutoff)
        await pipe.execute()

        # Sum residual entries for 60-second window
        remaining = await self._redis.zrange(stream_key, 0, -1)
        total = 0.0
        for entry in remaining:
            try:
                _, amt = entry.split(":", 1)
                total += float(amt)
            except ValueError:
                continue
        await self._redis.set(window_key, str(total), ex=120)

    # ------------------------------------------------------------------ helpers for orchestrator

    @staticmethod
    def compute_f_lane(budget_remaining: float, soft_cap: float) -> float:
        if soft_cap <= 0:
            return 1.0
        ratio = budget_remaining / soft_cap
        return max(0.0, min(1.0, ratio))

    @staticmethod
    def compute_h_roi(roi_ema: float, alpha: float) -> float:
        weighted = alpha * roi_ema + (1 - alpha)
        return max(0.5, min(1.5, weighted))
