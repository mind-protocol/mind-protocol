"""Economy runtime wiring."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Optional

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

from .collector import EconomyCollector
from .manager import EconomyManager
from .membrane_store import MembraneStore
from .oracle import PriceOracle
from .policy_loader import BudgetPolicyManager
from .settings import EconomySettings
from .ubc import UBCDistributor

logger = logging.getLogger(__name__)


class EconomyRuntime:
    """Coordinates economy subsystems."""

    def __init__(self, settings: EconomySettings, broadcaster: ConsciousnessStateBroadcaster) -> None:
        self._settings = settings
        self._broadcaster = broadcaster
        self._store = MembraneStore(settings.redis_url, spend_alpha=settings.spend_alpha)
        self._oracle = PriceOracle(settings)
        self._policies = BudgetPolicyManager(graph=settings.l2_graph)
        self._manager = EconomyManager(settings, self._store, self._policies, broadcaster)
        self._collector = EconomyCollector(settings, self._store, self._oracle, broadcaster)
        self._ubc = UBCDistributor(settings, self._store, broadcaster)
        self._started = False

    async def start(self) -> None:
        if self._started:
            return
        await self._manager.start()
        await self._ubc.start()
        self._collector.start()
        self._started = True

    async def stop(self) -> None:
        if not self._started:
            return
        self._collector.stop()
        await self._ubc.stop()
        await self._manager.stop()
        await self._oracle.close()
        await self._store.close()
        self._started = False

    async def get_lane_snapshot(self, lane: str, *, org_id: Optional[str] = None) -> Dict[str, float]:
        """
        Retrieve the latest economy snapshot for a specific lane.
        """
        org = org_id or self._settings.org_id
        return await self._store.get_lane_snapshot(org, lane)

    async def get_lane_multiplier(
        self,
        *,
        org_id: str,
        lane: str,
        citizen_id: Optional[str] = None,
    ) -> Optional[Dict[str, float]]:
        """
        Compute the gating multipliers for a lane, including wallet balance hints.
        """
        snapshot = await self._store.get_lane_snapshot(org_id, lane)
        throttle = snapshot.get("throttle", 1.0)
        soft_cap = snapshot.get("soft_cap", 0.0)

        # If we have no data at all, skip emitting multipliers
        if throttle == 0.0 and soft_cap == 0.0 and snapshot.get("spent_rolling", 0.0) == 0.0:
            return None

        result: Dict[str, float] = {
            "lane": lane,
            "throttle": throttle or 1.0,
            "f_lane": snapshot.get("f_lane", 1.0),
            "h_roi": snapshot.get("h_roi", 1.0),
            "g_wallet": snapshot.get("g_wallet", 1.0),
            "budget_remaining": snapshot.get("budget_remaining", 0.0),
            "soft_cap": soft_cap,
        }

        wallet_node: Optional[str] = self._settings.lane_wallets.get(lane)
        if not wallet_node and citizen_id:
            wallet_node = f"node:citizen:{citizen_id}"

        if wallet_node:
            balance = await self._store.get_wallet_balance(org_id, wallet_node)
            result["wallet_balance"] = balance

            next_eta = await self._store.get_wallet_next_ubc(org_id, wallet_node)
            if next_eta:
                result["ubc_next_eta"] = next_eta

        return result


_runtime: Optional[EconomyRuntime] = None


def initialize_economy_runtime(broadcaster: ConsciousnessStateBroadcaster) -> EconomyRuntime:
    global _runtime
    if _runtime is None:
        settings = EconomySettings()
        _runtime = EconomyRuntime(settings, broadcaster)
    return _runtime


def get_runtime() -> Optional[EconomyRuntime]:
    """Return the active economy runtime if one has been initialised."""
    return _runtime
