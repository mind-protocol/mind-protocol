"""Economy collector listening to bus events."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster

from .membrane_store import MembraneStore
from .oracle import PriceOracle
from .settings import EconomySettings

logger = logging.getLogger(__name__)


@dataclass
class PendingRequest:
    request_id: str
    capability: str
    lane: str
    citizen_id: str
    est_units: float
    est_roi: float
    created_at: datetime


class EconomyCollector:
    """Consumes tool events and emits economy telemetry."""

    def __init__(
        self,
        settings: EconomySettings,
        store: MembraneStore,
        oracle: PriceOracle,
        broadcaster: ConsciousnessStateBroadcaster,
    ) -> None:
        self._settings = settings
        self._store = store
        self._oracle = oracle
        self._broadcaster = broadcaster
        self._requests: Dict[str, PendingRequest] = {}
        self._lock = asyncio.Lock()
        self._listener_registered = False

    def start(self) -> None:
        if not self._listener_registered:
            ConsciousnessStateBroadcaster.register_listener(self._listener)
            self._listener_registered = True
            logger.info("Economy collector listening for tool events")

    def stop(self) -> None:
        if self._listener_registered:
            ConsciousnessStateBroadcaster.unregister_listener(self._listener)
            self._listener_registered = False

    def _listener(self, citizen_id: str, event_type: str, payload: Dict[str, Any]) -> Optional[asyncio.Future]:
        if event_type not in {"tool.request", "tool.result.usage"}:
            return None
        return self._handle_event(citizen_id, event_type, payload)

    async def _handle_event(self, citizen_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        if event_type == "tool.request":
            await self._handle_tool_request(citizen_id, payload)
        elif event_type == "tool.result.usage":
            await self._handle_tool_usage(citizen_id, payload)

    async def _handle_tool_request(self, citizen_id: str, payload: Dict[str, Any]) -> None:
        request_id = str(payload.get("request_id"))
        if not request_id:
            return

        lane = str(payload.get("lane") or payload.get("args", {}).get("lane") or "general")
        capability = str(payload.get("capability") or "unknown")
        est_units = float(payload.get("args", {}).get("estimated_units", 0.0) or 0.0)
        est_roi = float(payload.get("args", {}).get("estimated_roi", 1.0) or 1.0)
        usd_est = float(payload.get("args", {}).get("estimated_usd_per_unit", 0.0) or 0.0)

        usd_per_mind = await self._oracle.get_usd_per_mind()
        mind_per_unit_est = usd_est / usd_per_mind if usd_per_mind else 0.0
        mind_estimate = mind_per_unit_est * est_units

        pending = PendingRequest(
            request_id=request_id,
            capability=capability,
            lane=lane,
            citizen_id=citizen_id,
            est_units=est_units,
            est_roi=est_roi,
            created_at=datetime.now(timezone.utc),
        )

        async with self._lock:
            self._requests[request_id] = pending

        # Emit charge request telemetry (estimates only)
        payload = {
            "request_id": request_id,
            "capability": capability,
            "lane": lane,
            "estimated_units": est_units,
            "estimated_usd_per_unit": usd_est,
            "estimated_mind_per_unit": mind_per_unit_est,
            "estimated_mind_total": mind_estimate,
            "citizen_id": citizen_id,
            "org_id": self._settings.org_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._broadcaster.broadcast_event("economy.charge.request", payload)

    async def _handle_tool_usage(self, citizen_id: str, payload: Dict[str, Any]) -> None:
        request_id = str(payload.get("request_id"))
        if not request_id:
            return

        async with self._lock:
            pending = self._requests.pop(request_id, None)

        lane = str(payload.get("lane") or (pending.lane if pending else "general"))
        capability = str(payload.get("capability") or (pending.capability if pending else "unknown"))

        usage = payload.get("usage") or {}
        units = float(usage.get("units") or usage.get("total_units") or 0.0)
        if units <= 0:
            logger.debug("tool.result.usage missing units for %s", request_id)
            return

        usd_cost = float(usage.get("usd_cost") or usage.get("estimated_usd") or 0.0)
        usd_per_unit = float(payload.get("usd_per_unit") or (usd_cost / units if usd_cost else 0.0))

        usd_per_mind = await self._oracle.get_usd_per_mind()
        mind_per_unit = usd_per_unit / usd_per_mind if usd_per_mind else 0.0
        mind_spent = mind_per_unit * units

        roi_sample = float(payload.get("roi") or (pending.est_roi if pending else 1.0))

        wallet_node = f"node:citizen:{citizen_id}"

        metrics = await self._store.record_charge(
            self._settings.org_id,
            lane,
            mind_spent,
            roi_sample=roi_sample,
            citizen_id=citizen_id,
            wallet_node=wallet_node,
        )

        # Broadcast observed rate
        rate_event = {
            "request_id": request_id,
            "capability": capability,
            "lane": lane,
            "units": units,
            "usd_per_unit": usd_per_unit,
            "mind_per_unit": mind_per_unit,
            "proof": {
                "source": "helius" if self._settings.has_price_oracle else "fallback",
                "mint": self._settings.mind_mint,
            },
            "citizen_id": citizen_id,
            "org_id": self._settings.org_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._broadcaster.broadcast_event("economy.rate.observed", rate_event)

        charge_event = {
            "request_id": request_id,
            "capability": capability,
            "lane": lane,
            "actual_units": units,
            "mind_per_unit": mind_per_unit,
            "mind_spent": mind_spent,
            "citizen_id": citizen_id,
            "org_id": self._settings.org_id,
            "budget_remaining": metrics.get("budget_remaining", 0.0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._broadcaster.broadcast_event("economy.charge.settle", charge_event)
