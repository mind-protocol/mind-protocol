"""
Dashboard State Aggregator - 1Hz State Emission Service

ARCHITECTURAL PRINCIPLE: Reduce WebSocket noise by aggregating state updates

This service collects consciousness state from all engines and emits
aggregated updates at 1Hz (once per second) instead of per-tick (10Hz per engine).

Benefits:
- Reduces WebSocket bandwidth (60x reduction: 6 engines * 10Hz → 1Hz)
- Dashboard receives clean, aggregated state snapshots
- Uses SafeBroadcaster for reliable emission

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-30 (WebSocket-Only Architecture - State Aggregation)
Architecture: dashboard.state.emit@1.0 pattern
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DashboardStateAggregator:
    """
    Aggregates consciousness state from all engines and emits at 1Hz.

    Example Usage:
        >>> aggregator = DashboardStateAggregator(
        ...     safe_broadcaster=safe_broadcaster,
        ...     get_engines_fn=lambda: engine_registry.get_all_engines()
        ... )
        >>> await aggregator.start()
        # Emits dashboard.state.emit@1.0 every second
    """

    def __init__(
        self,
        safe_broadcaster: Any,
        get_engines_fn: Callable[[], Dict[str, Any]],
        emission_hz: float = 1.0
    ):
        """
        Initialize Dashboard State Aggregator.

        Args:
            safe_broadcaster: SafeBroadcaster instance for reliable emission
            get_engines_fn: Function that returns dict of {citizen_id: engine}
            emission_hz: Emission frequency in Hz (default: 1.0 = once per second)
        """
        self.broadcaster = safe_broadcaster
        self.get_engines = get_engines_fn
        self.emission_hz = emission_hz
        self.emission_interval = 1.0 / emission_hz

        self.running = False
        self._task = None

        # Telemetry
        self.total_emissions = 0
        self.total_errors = 0
        self.last_emission_time = None

        logger.info(
            f"[DashboardStateAggregator] Initialized "
            f"(emission_hz={emission_hz}, interval={self.emission_interval}s)"
        )

    async def start(self):
        """
        Start the aggregator emission loop.

        Runs in background, emitting state every interval.
        """
        if self.running:
            logger.warning("[DashboardStateAggregator] Already running")
            return

        self.running = True
        self._task = asyncio.create_task(self._emission_loop())
        logger.info(f"[DashboardStateAggregator] Started (emitting every {self.emission_interval}s)")

    async def stop(self):
        """
        Stop the aggregator emission loop.
        """
        if not self.running:
            return

        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("[DashboardStateAggregator] Stopped")

    async def _emission_loop(self):
        """
        Main emission loop - runs every interval.
        """
        logger.info("[DashboardStateAggregator] Emission loop started")

        while self.running:
            try:
                # Collect state from all engines
                state = self._collect_state()

                # Emit via SafeBroadcaster
                await self.broadcaster.safe_emit("dashboard.state.emit@1.0", state)

                # Update telemetry
                self.total_emissions += 1
                self.last_emission_time = datetime.now()

                # Log periodically (every 10 emissions = 10 seconds)
                if self.total_emissions % 10 == 0:
                    logger.debug(
                        f"[DashboardStateAggregator] Emitted {self.total_emissions} states "
                        f"({len(state.get('citizens', []))} citizens)"
                    )

            except Exception as exc:
                self.total_errors += 1
                logger.error(f"[DashboardStateAggregator] Emission failed: {exc}")

            # Wait for next interval
            await asyncio.sleep(self.emission_interval)

    def _collect_state(self) -> Dict[str, Any]:
        """
        Collect aggregated state from all consciousness engines.

        Returns:
            {
                "timestamp": ISO timestamp,
                "citizens": [
                    {
                        "citizen_id": str,
                        "node_count": int,
                        "link_count": int,
                        "subentity_count": int,
                        "global_energy": float,
                        "consciousness_state": str,
                        "tick_frequency_hz": float
                    },
                    ...
                ],
                "totals": {
                    "total_nodes": int,
                    "total_links": int,
                    "total_subentities": int,
                    "avg_energy": float
                }
            }
        """
        try:
            engines = self.get_engines()
        except Exception as exc:
            logger.warning(f"[DashboardStateAggregator] Failed to get engines: {exc}")
            engines = {}

        citizens = []
        total_nodes = 0
        total_links = 0
        total_subentities = 0
        total_energy = 0.0
        valid_engines = 0

        for citizen_id, engine in engines.items():
            try:
                # Extract engine state
                node_count = len(getattr(engine.graph, 'nodes', {}))
                link_count = len(getattr(engine.graph, 'links', {}))
                subentity_count = len(getattr(engine, 'sub_entities', {}))

                # Get global energy (safely)
                try:
                    global_energy = engine.graph.compute_global_energy() if hasattr(engine.graph, 'compute_global_energy') else 0.0
                except Exception:
                    global_energy = 0.0

                # Get consciousness state (safely)
                try:
                    consciousness_state = getattr(engine.coherence_state, 'state_name', 'unknown') if hasattr(engine, 'coherence_state') else 'unknown'
                except Exception:
                    consciousness_state = 'unknown'

                # Get tick frequency (safely)
                try:
                    tick_frequency_hz = 1000.0 / engine.config.base_tick_interval_ms if hasattr(engine, 'config') else 10.0
                except Exception:
                    tick_frequency_hz = 10.0

                citizens.append({
                    "citizen_id": citizen_id,
                    "node_count": node_count,
                    "link_count": link_count,
                    "subentity_count": subentity_count,
                    "global_energy": round(global_energy, 3),
                    "consciousness_state": consciousness_state,
                    "tick_frequency_hz": round(tick_frequency_hz, 2)
                })

                # Accumulate totals
                total_nodes += node_count
                total_links += link_count
                total_subentities += subentity_count
                total_energy += global_energy
                valid_engines += 1

            except Exception as exc:
                logger.warning(f"[DashboardStateAggregator] Failed to collect state for {citizen_id}: {exc}")
                continue

        # Calculate averages
        avg_energy = (total_energy / valid_engines) if valid_engines > 0 else 0.0

        return {
            "timestamp": datetime.now().isoformat(),
            "citizens": citizens,
            "totals": {
                "total_nodes": total_nodes,
                "total_links": total_links,
                "total_subentities": total_subentities,
                "avg_energy": round(avg_energy, 3),
                "engine_count": valid_engines
            }
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get aggregator statistics.

        Returns:
            {
                "running": bool,
                "emission_hz": float,
                "total_emissions": int,
                "total_errors": int,
                "last_emission_time": Optional[str]
            }
        """
        return {
            "running": self.running,
            "emission_hz": self.emission_hz,
            "total_emissions": self.total_emissions,
            "total_errors": self.total_errors,
            "last_emission_time": self.last_emission_time.isoformat() if self.last_emission_time else None
        }


# ------------------------------------------------------------------ Factory Function

def create_dashboard_aggregator(
    safe_broadcaster: Any,
    get_engines_fn: Callable[[], Dict[str, Any]],
    emission_hz: float = 1.0
) -> DashboardStateAggregator:
    """
    Factory function for creating DashboardStateAggregator instances.

    Args:
        safe_broadcaster: SafeBroadcaster instance
        get_engines_fn: Function returning {citizen_id: engine} dict
        emission_hz: Emission frequency in Hz (default 1.0)

    Returns:
        DashboardStateAggregator instance

    Example:
        >>> aggregator = create_dashboard_aggregator(
        ...     safe_broadcaster=safe,
        ...     get_engines_fn=lambda: engine_registry.get_all_engines()
        ... )
        >>> await aggregator.start()
    """
    return DashboardStateAggregator(
        safe_broadcaster=safe_broadcaster,
        get_engines_fn=get_engines_fn,
        emission_hz=emission_hz
    )
