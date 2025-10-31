"""
SafeBroadcaster - Reliability Layer for Consciousness Event Streaming

ARCHITECTURAL PRINCIPLE: Make event emission reliable, observable, and self-reporting

This module wraps ConsciousnessStateBroadcaster with:
- Readiness gating (no cold-start drops)
- Spill buffer for failed emissions (no silent loss)
- Health self-reporting to membrane bus

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-30 (WebSocket-Only Architecture - Reliability Layer)
Architecture: Option B (auto-send snapshots) + SafeBroadcaster pattern
"""

import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional

from orchestration.libs.websocket_broadcast import ConsciousnessStateBroadcaster
from orchestration.libs.schema_registry import get_schema_registry

logger = logging.getLogger(__name__)


class SafeBroadcaster:
    """
    Reliable broadcaster with spill buffer and health self-reporting.

    RELIABILITY GUARANTEES:
    - No cold-start drops: Events spill to buffer until WebSocket ready
    - No silent failures: Health events report rejection reasons
    - Flush on recovery: Spill buffer drains when WebSocket becomes available

    Example Usage:
        >>> safe = SafeBroadcaster(citizen_id="atlas")
        >>> await safe.safe_emit("graph.delta.node.upsert", {...})
        # If WebSocket unavailable: event spills to buffer + health.compliance emitted
        # If WebSocket available: event broadcasts immediately
        # On recovery: spill buffer drains automatically
    """

    def __init__(
        self,
        citizen_id: str,
        *,
        websocket_manager: Optional[Any] = None,
        max_spill_size: int = 1000,
        health_bus_inject: Optional[Any] = None
    ):
        """
        Initialize SafeBroadcaster with spill buffer and health reporting.

        Args:
            citizen_id: Citizen identifier for provenance
            websocket_manager: WebSocket manager (optional, auto-imports if None)
            max_spill_size: Maximum events in spill buffer before dropping old
            health_bus_inject: Health bus inject function (optional)
        """
        self.citizen_id = citizen_id
        self.max_spill_size = max_spill_size
        self.health_bus_inject = health_bus_inject

        # Core broadcaster (wraps existing ConsciousnessStateBroadcaster)
        self.broadcaster = ConsciousnessStateBroadcaster(
            websocket_manager=websocket_manager,
            default_citizen_id=citizen_id
        )

        # Spill buffer: events that failed to emit (FIFO queue)
        self.spill_buffer: deque = deque(maxlen=max_spill_size)

        # Health telemetry: track rejection reasons
        self.rejection_counts: Dict[str, int] = {}
        self.total_emitted = 0
        self.total_spilled = 0
        self.total_rejected = 0

        # Flush state
        self.is_flushing = False
        self.last_flush_attempt = None

        # Schema validation (runtime mp-lint integration)
        self.schema_registry = get_schema_registry()
        self.schema_validation_enabled = True  # Can be disabled for testing

        logger.info(
            f"[SafeBroadcaster] Initialized for {citizen_id} "
            f"(spill_max={max_spill_size}, health_reporting={'on' if health_bus_inject else 'off'}, "
            f"schema_validation={'on' if self.schema_validation_enabled else 'off'})"
        )

    async def safe_emit(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Emit event with reliability guarantees and schema validation.

        VALIDATION FLOW:
        1. Validate event against L4 schema registry (R-001, R-002)
        2. If invalid: reject (don't spill), report violation, return False
        3. If valid: check WebSocket availability
        4. If WebSocket unavailable: spill to buffer (only valid events spilled)
        5. If WebSocket available: emit immediately

        Args:
            event_type: Event type (e.g., "graph.delta.node.upsert")
            data: Event data dict

        Returns:
            True if emitted immediately, False if rejected or spilled

        Example:
            >>> await safe.safe_emit("presence.beacon", {
            ...     "citizen_id": "ada",
            ...     "availability": "active"
            ... })
        """
        # Update snapshot cache for graph deltas
        if event_type == "graph.delta.node.upsert":
            try:
                from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache
                cache = get_snapshot_cache()
                citizen_id = data.get("citizen_id", self.citizen_id)
                node_data_for_cache = {
                    "id": data.get("node_id"),
                    "type": data.get("node_type"),
                    "name": data.get("properties", {}).get("role_or_topic"), # Best effort for name
                    "properties": data.get("properties", {})
                }
                if node_data_for_cache["id"]:
                    cache.upsert_node(citizen_id, node_data_for_cache)
            except Exception as e:
                logger.error(f"[SafeBroadcaster] Failed to cache node upsert: {e}")

        elif event_type == "graph.delta.link.upsert":
            try:
                from orchestration.adapters.ws.snapshot_cache import get_snapshot_cache
                cache = get_snapshot_cache()
                citizen_id = data.get("citizen_id", self.citizen_id)
                link_data_for_cache = data.copy()
                if link_data_for_cache.get("source") and link_data_for_cache.get("target"):
                    cache.upsert_link(citizen_id, link_data_for_cache)
            except Exception as e:
                logger.error(f"[SafeBroadcaster] Failed to cache link upsert: {e}")

        # STEP 1: Schema validation (mp-lint R-001, R-002)
        if self.schema_validation_enabled:
            validation = self.schema_registry.validate_event_basic(event_type)

            if not validation.valid:
                # REJECT: Invalid event, don't spill to buffer
                self.total_rejected += 1
                self.rejection_counts[validation.rule_code] = \
                    self.rejection_counts.get(validation.rule_code, 0) + 1

                logger.debug(
                    f"[SafeBroadcaster] Event rejected: {event_type} "
                    f"({validation.rule_code}: {validation.error})"
                )

                # Report violation to health bus
                await self._report_health_compliance()

                return False  # Event rejected, not emitted or spilled

        # STEP 2: Check if WebSocket available (readiness gating)
        if not self.broadcaster.is_available():
            # WebSocket not ready: spill to buffer (only valid events reach here)
            self._spill_event(event_type, data, reason="ws_not_ready")

            # Emit health.compliance snapshot (self-reporting)
            await self._report_health_compliance()

            return False

        # STEP 3: WebSocket ready - try to emit
        try:
            await self.broadcaster.broadcast_event(event_type, data)
            self.total_emitted += 1

            # If spill buffer has events, try flushing (opportunistic recovery)
            if len(self.spill_buffer) > 0 and not self.is_flushing:
                asyncio.create_task(self._flush_spill_buffer())

            return True

        except Exception as exc:
            # Emission failed: spill to buffer (only valid events reach here)
            logger.warning(f"[SafeBroadcaster] Emission failed, spilling: {exc}")
            self._spill_event(event_type, data, reason=f"emit_failed:{exc.__class__.__name__}")

            # Emit health.compliance snapshot
            await self._report_health_compliance()

            return False

    def _spill_event(self, event_type: str, data: Dict[str, Any], reason: str):
        """
        Spill event to buffer (called when emission fails).

        Args:
            event_type: Event type
            data: Event data
            reason: Rejection reason (for health telemetry)
        """
        # Add to spill buffer (FIFO, auto-drops oldest if full)
        spill_entry = {
            "event_type": event_type,
            "data": data,
            "spilled_at": datetime.now().isoformat(),
            "reason": reason
        }
        self.spill_buffer.append(spill_entry)

        # Update telemetry
        self.total_spilled += 1
        self.rejection_counts[reason] = self.rejection_counts.get(reason, 0) + 1

        # Log at DEBUG level (spill is normal during cold-start)
        logger.debug(
            f"[SafeBroadcaster] Spilled event {event_type} (reason={reason}, "
            f"buffer_size={len(self.spill_buffer)})"
        )

    async def _flush_spill_buffer(self):
        """
        Drain spill buffer when WebSocket becomes available (opportunistic recovery).

        Called automatically after successful emission if buffer has events.
        """
        if self.is_flushing:
            return  # Already flushing

        self.is_flushing = True
        self.last_flush_attempt = datetime.now()

        try:
            flushed_count = 0
            failed_count = 0

            # Drain buffer (FIFO order)
            while len(self.spill_buffer) > 0:
                # Check if still available (avoid tight loop if WebSocket dies)
                if not self.broadcaster.is_available():
                    logger.warning(
                        f"[SafeBroadcaster] Flush aborted: WebSocket unavailable "
                        f"(flushed={flushed_count}, remaining={len(self.spill_buffer)})"
                    )
                    break

                # Pop oldest event
                spill_entry = self.spill_buffer.popleft()

                # Try to emit
                try:
                    await self.broadcaster.broadcast_event(
                        spill_entry["event_type"],
                        spill_entry["data"]
                    )
                    flushed_count += 1
                    self.total_emitted += 1

                except Exception as exc:
                    # Re-spill (append to end of buffer)
                    logger.warning(f"[SafeBroadcaster] Flush emission failed: {exc}")
                    self.spill_buffer.append(spill_entry)
                    failed_count += 1

                    # Abort flush if errors accumulating
                    if failed_count >= 3:
                        logger.warning(
                            f"[SafeBroadcaster] Flush aborted: too many errors "
                            f"(flushed={flushed_count}, failed={failed_count})"
                        )
                        break

            if flushed_count > 0:
                logger.info(
                    f"[SafeBroadcaster] Flushed {flushed_count} events from spill buffer "
                    f"(remaining={len(self.spill_buffer)})"
                )

        finally:
            self.is_flushing = False

    async def _report_health_compliance(self):
        """
        Emit health.compliance.snapshot to membrane bus (self-reporting).

        Reports top rejection reasons to make broadcast issues visible.
        """
        if not self.health_bus_inject:
            return  # Health reporting not configured

        # Build top rejects list (sorted by count, descending)
        top_rejects = sorted(
            self.rejection_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5 reasons

        # Emit health.compliance.snapshot
        try:
            await self.health_bus_inject({
                "type": "health.compliance.snapshot",
                "id": f"compliance_{self.citizen_id}_{int(datetime.now().timestamp() * 1000)}",
                "spec": {"name": "health.v1", "rev": "1.0.0"},
                "provenance": {
                    "scope": "personal",
                    "citizen_id": self.citizen_id,
                    "component": "SafeBroadcaster"
                },
                "payload": {
                    "top_rejects": top_rejects,
                    "spill_buffer_size": len(self.spill_buffer),
                    "total_emitted": self.total_emitted,
                    "total_spilled": self.total_spilled,
                    "timestamp": datetime.now().isoformat()
                }
            })
        except Exception as exc:
            # Don't fail on health reporting (defensive)
            logger.debug(f"[SafeBroadcaster] Health reporting failed: {exc}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get SafeBroadcaster statistics.

        Returns:
            {
                "total_emitted": int,
                "total_spilled": int,
                "total_rejected": int,
                "spill_buffer_size": int,
                "rejection_counts": Dict[str, int],
                "is_flushing": bool,
                "last_flush_attempt": Optional[str],
                "broadcaster_available": bool,
                "schema_validation_enabled": bool,
                "schema_registry_loaded": bool
            }
        """
        return {
            "total_emitted": self.total_emitted,
            "total_spilled": self.total_spilled,
            "total_rejected": self.total_rejected,
            "spill_buffer_size": len(self.spill_buffer),
            "rejection_counts": dict(self.rejection_counts),
            "is_flushing": self.is_flushing,
            "last_flush_attempt": self.last_flush_attempt.isoformat() if self.last_flush_attempt else None,
            "broadcaster_available": self.broadcaster.is_available(),
            "schema_validation_enabled": self.schema_validation_enabled,
            "schema_registry_loaded": self.schema_registry.loaded if hasattr(self, 'schema_registry') else False
        }

    def is_available(self) -> bool:
        """
        Check if broadcaster is available (delegates to wrapped broadcaster).

        Returns:
            True if WebSocket manager is available, False otherwise
        """
        return self.broadcaster.is_available()

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast event (backward-compatible alias for safe_emit).

        This method provides API compatibility with ConsciousnessStateBroadcaster
        for drop-in replacement without changing call sites.

        Args:
            event_type: Event type (e.g., "graph.delta.node.upsert")
            data: Event data dict

        Example:
            >>> await safe.broadcast_event("graph.delta.node.upsert", {...})
        """
        await self.safe_emit(event_type, data)

    async def broadcast_consciousness_state(
        self,
        network_id: str,
        global_energy: float,
        branching_ratio: float,
        raw_sigma: float,
        tick_interval_ms: float,
        tick_frequency_hz: float,
        consciousness_state: str,
        time_since_last_event: float,
        timestamp: Any
    ):
        """
        Broadcast consciousness state (delegates to wrapped broadcaster).

        This method provides API compatibility with ConsciousnessStateBroadcaster.
        """
        if hasattr(self.broadcaster, 'broadcast_consciousness_state'):
            await self.broadcaster.broadcast_consciousness_state(
                network_id=network_id,
                global_energy=global_energy,
                branching_ratio=branching_ratio,
                raw_sigma=raw_sigma,
                tick_interval_ms=tick_interval_ms,
                tick_frequency_hz=tick_frequency_hz,
                consciousness_state=consciousness_state,
                time_since_last_event=time_since_last_event,
                timestamp=timestamp
            )

    def stride_exec(self, stride_data: Dict[str, Any]):
        """
        Broadcast stride execution event (delegates to wrapped broadcaster).

        This method provides API compatibility with ConsciousnessStateBroadcaster.
        """
        if hasattr(self.broadcaster, 'stride_exec'):
            self.broadcaster.stride_exec(stride_data)

    async def broadcast_energy_state(
        self,
        network_id: str,
        node_energy_distribution: Dict[str, float]
    ):
        """
        Broadcast energy state (delegates to wrapped broadcaster).

        This method provides API compatibility with ConsciousnessStateBroadcaster.
        """
        if hasattr(self.broadcaster, 'broadcast_energy_state'):
            await self.broadcaster.broadcast_energy_state(
                network_id=network_id,
                node_energy_distribution=node_energy_distribution
            )

    def get_counter_stats(self) -> Dict[str, Any]:
        """
        Get counter stats (delegates to wrapped broadcaster).

        This method provides API compatibility with ConsciousnessStateBroadcaster.
        """
        if hasattr(self.broadcaster, 'get_counter_stats'):
            return self.broadcaster.get_counter_stats()
        return {}


# ------------------------------------------------------------------ Factory Functions

def create_safe_broadcaster(
    citizen_id: str,
    *,
    websocket_manager: Optional[Any] = None,
    max_spill_size: int = 1000,
    health_bus_inject: Optional[Any] = None
) -> SafeBroadcaster:
    """
    Factory function for creating SafeBroadcaster instances.

    Args:
        citizen_id: Citizen identifier for provenance
        websocket_manager: WebSocket manager (optional)
        max_spill_size: Maximum events in spill buffer
        health_bus_inject: Health bus inject function (optional)

    Returns:
        SafeBroadcaster instance

    Example:
        >>> safe = create_safe_broadcaster("atlas")
        >>> await safe.safe_emit("graph.delta.node.upsert", {...})
    """
    return SafeBroadcaster(
        citizen_id=citizen_id,
        websocket_manager=websocket_manager,
        max_spill_size=max_spill_size,
        health_bus_inject=health_bus_inject
    )
