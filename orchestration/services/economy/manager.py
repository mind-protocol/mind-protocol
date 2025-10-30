"""Budget policy evaluation loop."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Dict, Optional

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

from .membrane_store import MembraneStore
from .policy_loader import BudgetPolicyManager, PolicyExpressionError
from .settings import EconomySettings

logger = logging.getLogger(__name__)


class EconomyManager:
    """Periodically evaluates budget policies and emits telemetry."""

    def __init__(
        self,
        settings: EconomySettings,
        store: MembraneStore,
        policies: BudgetPolicyManager,
        broadcaster: ConsciousnessStateBroadcaster,
    ) -> None:
        self._settings = settings
        self._store = store
        self._policies = policies
        self._broadcaster = broadcaster
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is None:
            await self._policies.ensure_loaded()
            self._running = True
            self._task = asyncio.create_task(self._run_loop(), name="economy-manager")

    async def stop(self) -> None:
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:  # pragma: no cover - cooperative cancellation
                pass
            self._task = None

    async def _run_loop(self) -> None:
        interval = max(1, self._settings.throttle_interval_seconds)
        refresh_interval = max(interval, self._settings.policy_refresh_seconds)
        last_refresh = 0.0

        while self._running:
            now = time.time()
            if now - last_refresh >= refresh_interval:
                try:
                    await self._policies.refresh()
                except Exception as exc:  # pragma: no cover - defensive
                    logger.warning("Failed to refresh budget policies: %s", exc)
                else:
                    last_refresh = now

            for policy in self._policies.policies:
                await self._evaluate_policy(policy)

            await asyncio.sleep(interval)

    async def _evaluate_policy(self, policy) -> None:
        metrics = await self._store.get_lane_snapshot(self._settings.org_id, policy.lane)

        budget_remaining = metrics.get("budget_remaining", 0.0)
        soft_cap = metrics.get("soft_cap", policy.extras.get("soft_cap", 0.0))
        if soft_cap <= 0:
            soft_cap = max(policy.extras.get("soft_cap", 1.0), 1.0)

        roi_ema = metrics.get("roi_ema", 1.0)

        context: Dict[str, float] = {
            "budget_remaining": budget_remaining,
            "soft_cap": soft_cap,
            "roi_ema": roi_ema,
            "spent_rolling": metrics.get("spent_rolling", 0.0),
        }
        for key, value in policy.extras.items():
            if isinstance(value, (int, float)):
                context[key] = float(value)

        try:
            f_lane = max(0.0, min(1.0, policy.evaluate(context)))
        except PolicyExpressionError as exc:
            logger.warning("Failed to evaluate policy %s: %s", policy.lane, exc)
            f_lane = self._store.compute_f_lane(budget_remaining, soft_cap)
        h_roi = self._store.compute_h_roi(roi_ema, self._settings.roi_alpha)

        wallet_node = policy.extras.get("wallet_node") or self._settings.lane_wallets.get(policy.lane)
        g_wallet = 1.0
        wallet_balance: Optional[float] = None
        if wallet_node:
            wallet_balance = await self._store.get_wallet_balance(self._settings.org_id, wallet_node)
            if wallet_balance < policy.min_floor_mind:
                g_wallet = self._settings.wallet_floor_multiplier

        throttle = f_lane * h_roi * g_wallet

        await self._store.set_throttle(
            self._settings.org_id,
            policy.lane,
            throttle,
            f_lane=f_lane,
            h_roi=h_roi,
            g_wallet=g_wallet,
        )

        telemetry = {
            "lane": policy.lane,
            "org_id": self._settings.org_id,
            "throttle": throttle,
            "f_lane": f_lane,
            "h_roi": h_roi,
            "g_wallet": g_wallet,
            "policy_formula": policy.formula_raw,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "budget_remaining": budget_remaining,
            "soft_cap": soft_cap,
            "roi_ema": roi_ema,
            "spent_rolling": metrics.get("spent_rolling", 0.0),
        }
        if wallet_balance is not None:
            telemetry["wallet_balance"] = wallet_balance

        await self._broadcaster.broadcast_event("telemetry.economy.spend", telemetry)
