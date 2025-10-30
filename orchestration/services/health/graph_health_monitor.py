"""
Graph Health Monitor - Consciousness Substrate Diagnostics

Provides real-time health monitoring for consciousness graphs via WebSocket events.

10 Core Metrics:
1. Subentity-to-Node Density (E/N)
2. Membership Overlap (M/N)
3. Subentity Size & Dominance
4. Orphan Ratio
5. Subentity Coherence
6. Highway Health (RELATES_TO)
7. WM Health
8. Context Reconstruction
9. Learning Flux
10. Sector Connectivity

Author: Felix (Consciousness Engineer)
Date: 2025-10-29
Spec: docs/specs/v2/ops_and_viz/GRAPH_HEALTH_DIAGNOSTICS.md
"""

import asyncio
import logging
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
from falkordb import FalkorDB

from tools.logger import setup_logger
from orchestration.services.health.schema_map import SchemaMap

logger = setup_logger(__name__)


class HealthStatus(str, Enum):
    """Health status based on percentile bands"""
    GREEN = "GREEN"   # q20 <= current <= q80
    AMBER = "AMBER"   # q10 <= current < q20 or q80 < current <= q90
    RED = "RED"       # current < q10 or current > q90


class TrendDirection(str, Enum):
    """Trend direction over time"""
    RISING = "rising"
    STABLE = "stable"
    FALLING = "falling"


@dataclass
class DensityMetric:
    """Subentity-to-Node Density (E/N)"""
    entities: int
    nodes: int
    density: float                      # E/N ratio
    percentile: float
    trend: TrendDirection
    status: HealthStatus


@dataclass
class OverlapMetric:
    """Membership Overlap (M/N)"""
    total_memberships: int              # M
    total_nodes: int                    # N
    overlap_ratio: float                # M/N
    percentile: float
    trend: TrendDirection
    status: HealthStatus


@dataclass
class EntitySizeMetric:
    """Subentity Size & Dominance"""
    median_size: int
    mean_size: float
    gini_coefficient: float             # 0 = perfect equality, 1 = one entity has all
    size_distribution: Dict[str, int]   # q25, q50, q75, q90
    top_entities: List[Dict[str, Any]]  # Top 5 by size
    status: HealthStatus


@dataclass
class OrphanMetric:
    """Orphan Ratio"""
    total_nodes: int
    orphan_count: int
    orphan_ratio: float                 # 0-1
    new_orphans_last_24h: int
    percentile: float
    trend: TrendDirection
    status: HealthStatus
    sample_orphans: List[Dict[str, Any]]  # For targeted inspection


@dataclass
class CoherenceMetric:
    """Subentity Coherence"""
    entity_coherence: List[Dict[str, Any]]  # Per-entity coherence scores
    overall_median_coherence: float
    flagged_entities: List[str]         # Low coherence + large size


@dataclass
class HighwayMetric:
    """Highway Health (RELATES_TO)"""
    total_highways: int
    total_crossings: int                # Sum of all h.count
    mean_crossings_per_highway: float
    highways: List[Dict[str, Any]]      # All highways
    backbone_highways: List[Dict[str, Any]]  # Top 20 by crossings
    status: HealthStatus


@dataclass
class WMHealthMetric:
    """WM Health"""
    window_frames: int
    mean_selected: float                # Mean entities active per frame
    median_selected: float
    p90_selected: float
    mean_vitality: float                # E/Θ
    flip_rate: float                    # Flips per frame
    stability_score: float              # Low flip rate + stable count = high
    status: HealthStatus


@dataclass
class ReconstructionMetric:
    """Context Reconstruction Health"""
    window_reconstructions: int
    mean_latency_ms: float
    p50_latency_ms: float
    p90_latency_ms: float
    mean_similarity: float
    p50_similarity: float
    p10_similarity: float               # Worst 10%
    status: HealthStatus


@dataclass
class LearningFluxMetric:
    """Learning Flux"""
    window_hours: int
    weight_updates: int                 # Total weight changes
    prunes: int                         # Total membership removals
    update_rate: float                  # Updates per hour
    prune_rate: float                   # Prunes per hour
    percentile_update: float
    percentile_prune: float
    trend: TrendDirection
    status: HealthStatus


@dataclass
class SectorConnectivityMetric:
    """Sector Connectivity"""
    sectors: List[str]
    connectivity_matrix: List[List[int]]  # sectors × sectors adjacency
    modularity_score: Optional[float]     # Optional if GDS available
    cross_sector_highways: int
    status: HealthStatus


@dataclass
class GraphHealthSnapshot:
    """Complete health snapshot event"""
    type: str = 'graph.health.snapshot'
    graph_id: str = ''
    timestamp: int = 0
    history_window_days: int = 30

    # Summary
    overall_status: HealthStatus = HealthStatus.GREEN
    flagged_metrics: List[str] = None

    # 10 Core Metrics
    density: Optional[DensityMetric] = None
    overlap: Optional[OverlapMetric] = None
    entity_size: Optional[EntitySizeMetric] = None
    orphans: Optional[OrphanMetric] = None
    coherence: Optional[CoherenceMetric] = None
    highways: Optional[HighwayMetric] = None
    wm_health: Optional[WMHealthMetric] = None
    reconstruction: Optional[ReconstructionMetric] = None
    learning_flux: Optional[LearningFluxMetric] = None
    sector_connectivity: Optional[SectorConnectivityMetric] = None

    # Trends
    trends: Dict[str, TrendDirection] = None

    def __post_init__(self):
        if self.flagged_metrics is None:
            self.flagged_metrics = []
        if self.trends is None:
            self.trends = {}


class HealthHistoryStore:
    """Stores health metrics history for trend analysis"""

    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.history: Dict[str, deque] = {}  # graph_id -> deque of snapshots

    async def save_snapshot(self, graph_id: str, snapshot: GraphHealthSnapshot):
        """Save health snapshot with timestamp"""
        if graph_id not in self.history:
            self.history[graph_id] = deque(maxlen=1000)  # ~30 days at 60s intervals

        self.history[graph_id].append({
            'timestamp': snapshot.timestamp,
            'density': snapshot.density.density if snapshot.density else None,
            'overlap_ratio': snapshot.overlap.overlap_ratio if snapshot.overlap else None,
            'orphan_ratio': snapshot.orphans.orphan_ratio if snapshot.orphans else None,
            'median_entity_size': snapshot.entity_size.median_size if snapshot.entity_size else None,
            'mean_coherence': snapshot.coherence.overall_median_coherence if snapshot.coherence else None,
            'overall_status': snapshot.overall_status.value
        })

        # Cleanup old entries
        cutoff = time.time() - (self.retention_days * 24 * 3600)
        while self.history[graph_id] and self.history[graph_id][0]['timestamp'] < cutoff:
            self.history[graph_id].popleft()

    def get_history(self, graph_id: str, window_days: int = 30) -> List[Dict[str, Any]]:
        """Get historical samples for graph"""
        if graph_id not in self.history:
            return []

        cutoff = time.time() - (window_days * 24 * 3600)
        return [
            sample for sample in self.history[graph_id]
            if sample['timestamp'] >= cutoff
        ]

    def compute_percentiles(self, graph_id: str, metric: str) -> Dict[str, float]:
        """Compute q10/q20/q80/q90 percentiles for metric"""
        history = self.get_history(graph_id)
        values = [s[metric] for s in history if s.get(metric) is not None]

        if len(values) < 10:  # Not enough data
            return {'q10': 0.0, 'q20': 0.0, 'q80': 1.0, 'q90': 1.0}

        percentiles = np.percentile(values, [10, 20, 80, 90])
        return {
            'q10': float(percentiles[0]),
            'q20': float(percentiles[1]),
            'q80': float(percentiles[2]),
            'q90': float(percentiles[3])
        }


class GraphHealthMonitor:
    """
    Periodic health monitoring service that computes 10 metrics
    and emits WebSocket events.
    """

    def __init__(
        self,
        websocket_server,
        falkordb_host: str = "localhost",
        falkordb_port: int = 6379,
        interval_seconds: int = 60,
        history_window_days: int = 30,
        schema_config_path: Optional[Path] = None
    ):
        self.ws = websocket_server
        self.interval = interval_seconds
        self.history_window_days = history_window_days

        # FalkorDB connection
        self.db = FalkorDB(host=falkordb_host, port=falkordb_port)

        # Schema adapter for weighted membership computation
        if schema_config_path is None:
            schema_config_path = Path(__file__).parent / "schema.yaml"
        self.schema_map = SchemaMap(schema_config_path)

        # History storage
        self.history_store = HealthHistoryStore(retention_days=history_window_days)

        # Track previous status for alert detection
        self.previous_status: Dict[str, HealthStatus] = {}

        logger.info(f"GraphHealthMonitor initialized (interval={interval_seconds}s, history={history_window_days}d, schema_view={self.schema_map.config.view})")

    async def monitor_loop(self):
        """Main monitoring loop - runs continuously"""
        logger.info("Starting graph health monitoring loop")

        while True:
            try:
                for graph_id in await self.get_active_graphs():
                    snapshot = await self.compute_health_snapshot(graph_id)

                    # Emit periodic snapshot
                    await self.emit_snapshot(snapshot)

                    # Check for status changes → emit alert
                    if self.status_changed(graph_id, snapshot.overall_status):
                        alert = await self.generate_alert(graph_id, snapshot)
                        await self.emit_alert(alert)

                    # Store for historical trends
                    await self.history_store.save_snapshot(graph_id, snapshot)

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}", exc_info=True)

            await asyncio.sleep(self.interval)

    async def get_active_graphs(self) -> List[str]:
        """Get list of active consciousness graphs to monitor"""
        # Query FalkorDB for all graphs
        all_graphs = self.db.list_graphs()

        # Filter for consciousness graphs (starts with 'consciousness-')
        consciousness_graphs = [
            g for g in all_graphs
            if g and g.startswith('consciousness-')
        ]

        return consciousness_graphs

    async def compute_health_snapshot(self, graph_id: str) -> GraphHealthSnapshot:
        """Compute complete health snapshot for graph"""
        logger.info(f"Computing health snapshot for {graph_id}")

        snapshot = GraphHealthSnapshot(
            graph_id=graph_id,
            timestamp=int(time.time() * 1000),  # milliseconds
            history_window_days=self.history_window_days
        )

        graph = self.db.select_graph(graph_id)

        # Compute all metrics
        snapshot.density = await self.compute_density(graph, graph_id)
        snapshot.overlap = await self.compute_overlap(graph, graph_id)
        snapshot.entity_size = await self.compute_entity_size(graph)
        snapshot.orphans = await self.compute_orphans(graph, graph_id)
        # snapshot.coherence = await self.compute_coherence(graph)  # Requires embeddings
        snapshot.highways = await self.compute_highways(graph)
        # snapshot.wm_health = await self.compute_wm_health(graph_id)  # From telemetry
        # snapshot.reconstruction = await self.compute_reconstruction(graph_id)  # From telemetry
        # snapshot.learning_flux = await self.compute_learning_flux(graph_id)  # From telemetry
        # snapshot.sector_connectivity = await self.compute_sector_connectivity(graph)  # If sectors tagged

        # Compute overall status
        snapshot.overall_status = self.compute_overall_status(snapshot)
        snapshot.flagged_metrics = self.get_flagged_metrics(snapshot)

        # Compute trends
        snapshot.trends = await self.compute_trends(graph_id)

        return snapshot

    def judge_health(
        self,
        current_value: float,
        percentiles: Dict[str, float],
        inverted: bool = False
    ) -> HealthStatus:
        """
        Judge health by percentile bands.

        Args:
            current_value: Current metric value
            percentiles: Dict with q10, q20, q80, q90
            inverted: If True, higher values = worse (e.g., orphan_ratio)

        Returns:
            GREEN: q20 <= current <= q80 (normal band)
            AMBER: q10 <= current < q20 or q80 < current <= q90 (watch)
            RED: current < q10 or current > q90 (intervention needed)
        """
        q10, q20, q80, q90 = percentiles['q10'], percentiles['q20'], percentiles['q80'], percentiles['q90']

        if inverted:
            # For metrics where higher = worse (orphans, latency, etc.)
            if current_value <= q20:
                return HealthStatus.GREEN
            elif current_value <= q80:
                return HealthStatus.AMBER
            else:
                return HealthStatus.RED
        else:
            # For metrics where lower = worse or middle = good
            if q20 <= current_value <= q80:
                return HealthStatus.GREEN
            elif q10 <= current_value <= q90:
                return HealthStatus.AMBER
            else:
                return HealthStatus.RED

    async def compute_density(self, graph, graph_id: str) -> DensityMetric:
        """
        Compute Subentity-to-Node Density (E/N).

        Uses weighted membership: counts nodes with w_s(n) >= threshold
        """
        # Count SubEntities
        query_entities = "MATCH (e:SubEntity) RETURN count(e) AS total"
        result = graph.query(query_entities)
        entities = result.result_set[0][0] if result.result_set else 0

        # Count content nodes (exclude SubEntities)
        query_nodes = """
        MATCH (n)
        WHERE NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
        RETURN count(n) AS total
        """
        result = graph.query(query_nodes)
        nodes = result.result_set[0][0] if result.result_set else 0

        # Compute density
        density = float(entities) / nodes if nodes > 0 else 0.0

        # Get historical percentiles
        percentiles = self.history_store.compute_percentiles(graph_id, 'density')

        # Compute percentile position of current value
        history = self.history_store.get_history(graph_id)
        values = [s['density'] for s in history if s.get('density') is not None]
        if values:
            percentile = float(np.searchsorted(sorted(values), density) / len(values) * 100)
        else:
            percentile = 50.0

        # Judge health
        status = self.judge_health(density, percentiles, inverted=False)

        return DensityMetric(
            entities=entities,
            nodes=nodes,
            density=density,
            percentile=percentile,
            trend=TrendDirection.STABLE,  # TODO: Compute from history
            status=status
        )

    async def compute_overlap(self, graph, graph_id: str) -> OverlapMetric:
        """
        Compute Membership Overlap using weighted Jaccard.

        Measures how much SubEntities share nodes (weighted by membership strength).
        """
        # Get all SubEntities
        query = "MATCH (s:SubEntity) RETURN id(s) AS se_id, s.id AS se_name"
        result = graph.query(query)
        subentities = [(record[0], record[1] or record[0]) for record in result.result_set]

        if len(subentities) < 2:
            return OverlapMetric(0, 0, 0.0, 0.0, TrendDirection.STABLE, HealthStatus.GREEN)

        # Compute weighted membership for each SubEntity
        # This is expensive - we'll sample pairs
        overlaps = []
        for i in range(min(10, len(subentities))):
            for j in range(i + 1, min(10, len(subentities))):
                se1_name, se2_name = subentities[i][1], subentities[j][1]
                try:
                    overlap = self.schema_map.compute_overlap_weighted(graph, se1_name, se2_name)
                    overlaps.append(overlap)
                except Exception as e:
                    logger.warning(f"Failed to compute overlap for {se1_name}, {se2_name}: {e}")
                    continue

        # Average overlap as metric
        overlap_ratio = float(np.mean(overlaps)) if overlaps else 0.0

        # Count total memberships (nodes with w_s(n) >= threshold)
        total_memberships = 0
        for se_id, se_name in subentities[:20]:  # Sample first 20
            try:
                members = self.schema_map.get_members(graph, se_name)
                total_memberships += len(members)
            except Exception:
                continue

        # Count content nodes
        query_nodes = """
        MATCH (n)
        WHERE NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
        RETURN count(n) AS total
        """
        result = graph.query(query_nodes)
        total_nodes = result.result_set[0][0] if result.result_set else 0

        # Get historical percentiles
        percentiles = self.history_store.compute_percentiles(graph_id, 'overlap_ratio')

        # Compute percentile position
        history = self.history_store.get_history(graph_id)
        values = [s['overlap_ratio'] for s in history if s.get('overlap_ratio') is not None]
        if values:
            percentile = float(np.searchsorted(sorted(values), overlap_ratio) / len(values) * 100)
        else:
            percentile = 50.0

        # Judge health (middle range is good)
        status = self.judge_health(overlap_ratio, percentiles, inverted=False)

        return OverlapMetric(
            total_memberships=total_memberships,
            total_nodes=total_nodes,
            overlap_ratio=overlap_ratio,
            percentile=percentile,
            trend=TrendDirection.STABLE,  # TODO: Compute from history
            status=status
        )

    async def compute_entity_size(self, graph) -> EntitySizeMetric:
        """
        Compute Subentity Size & Dominance using weighted membership.

        Size = sum of w_s(n) for all nodes (or binary count with threshold)
        """
        # Get all SubEntities
        query = "MATCH (s:SubEntity) RETURN id(s) AS se_id, s.id AS se_name, coalesce(s.name, s.id) AS display_name"
        result = graph.query(query)
        subentities = [(record[0], record[1] or record[0], record[2]) for record in result.result_set]

        if not subentities:
            return EntitySizeMetric(0, 0.0, 0.0, {}, [], HealthStatus.GREEN)

        # Compute weighted size for each SubEntity
        sizes_data = []
        for se_id, se_name, display_name in subentities:
            try:
                # Use binary size (count of nodes with w_s(n) >= threshold)
                size = self.schema_map.get_binary_size(graph, se_name)
                sizes_data.append((se_name, display_name, size))
            except Exception as e:
                logger.warning(f"Failed to compute size for {se_name}: {e}")
                continue

        if not sizes_data:
            return EntitySizeMetric(0, 0.0, 0.0, {}, [], HealthStatus.GREEN)

        sizes = [s[2] for s in sizes_data]
        median_size = int(np.median(sizes))
        mean_size = float(np.mean(sizes))

        # Compute Gini coefficient (inequality measure)
        sorted_sizes = sorted(sizes)
        n = len(sorted_sizes)
        if sum(sorted_sizes) > 0:
            gini = (2 * sum((i + 1) * size for i, size in enumerate(sorted_sizes))) / (n * sum(sorted_sizes)) - (n + 1) / n
        else:
            gini = 0.0

        # Percentiles
        percentiles = np.percentile(sizes, [25, 50, 75, 90])
        size_distribution = {
            'q25': int(percentiles[0]),
            'q50': int(percentiles[1]),
            'q75': int(percentiles[2]),
            'q90': int(percentiles[3])
        }

        # Top 5 entities by size
        sizes_data_sorted = sorted(sizes_data, key=lambda x: x[2], reverse=True)
        top_entities = [
            {
                'id': se_name,
                'name': display_name,
                'size': size,
                'percentile': float(np.searchsorted(sorted_sizes, size) / len(sorted_sizes) * 100)
            }
            for se_name, display_name, size in sizes_data_sorted[:5]
        ]

        # Status based on Gini coefficient
        # Low Gini (<0.3) = good equality
        # High Gini (>0.6) = concerning concentration
        if gini < 0.4:
            status = HealthStatus.GREEN
        elif gini < 0.6:
            status = HealthStatus.AMBER
        else:
            status = HealthStatus.RED

        return EntitySizeMetric(
            median_size=median_size,
            mean_size=mean_size,
            gini_coefficient=float(gini),
            size_distribution=size_distribution,
            top_entities=top_entities,
            status=status
        )

    async def compute_orphans(self, graph, graph_id: str) -> OrphanMetric:
        """
        Compute Orphan Ratio using weighted membership.

        Orphans = nodes with max_s w_s(n) < threshold
        """
        # Count content nodes
        query_nodes = """
        MATCH (n)
        WHERE NOT 'SubEntity' IN labels(n) AND NOT 'Subentity' IN labels(n)
        RETURN count(n) AS total
        """
        result = graph.query(query_nodes)
        total_nodes = result.result_set[0][0] if result.result_set else 0

        if total_nodes == 0:
            return OrphanMetric(0, 0, 0.0, 0, 0.0, TrendDirection.STABLE, HealthStatus.GREEN, [])

        # Find orphans using schema_map
        try:
            orphans = self.schema_map.find_orphans(graph)
            orphan_count = len(orphans)
            orphan_ratio = float(orphan_count) / total_nodes if total_nodes > 0 else 0.0

            # Sample orphans for display (up to 10)
            sample_orphans = [
                {
                    'id': orphan['id'],
                    'name': orphan['id'],  # ID as fallback
                    'type': orphan['labels'][0] if orphan['labels'] else 'Unknown',
                    'max_weight': orphan['max_weight']
                }
                for orphan in orphans[:10]
            ]
        except Exception as e:
            logger.error(f"Failed to compute orphans: {e}")
            return OrphanMetric(total_nodes, 0, 0.0, 0, 0.0, TrendDirection.STABLE, HealthStatus.GREEN, [])

        # Get historical percentiles
        percentiles = self.history_store.compute_percentiles(graph_id, 'orphan_ratio')

        # Compute percentile position
        history = self.history_store.get_history(graph_id)
        values = [s['orphan_ratio'] for s in history if s.get('orphan_ratio') is not None]
        if values:
            percentile = float(np.searchsorted(sorted(values), orphan_ratio) / len(values) * 100)
        else:
            percentile = 50.0

        # Judge health (orphan_ratio is inverted - higher is worse)
        status = self.judge_health(orphan_ratio, percentiles, inverted=True)

        return OrphanMetric(
            total_nodes=total_nodes,
            orphan_count=orphan_count,
            orphan_ratio=orphan_ratio,
            new_orphans_last_24h=0,  # TODO: Track from history
            percentile=percentile,
            trend=TrendDirection.STABLE,  # TODO: Compute from history
            status=status,
            sample_orphans=sample_orphans
        )

    async def compute_highways(self, graph) -> HighwayMetric:
        """
        Compute Highway Health using COACTIVATES_WITH relationships.

        In current schema, highways are SubEntity-SubEntity coactivation edges.
        """
        # Use schema_map to get the appropriate query
        query = self.schema_map.get_highway_query()

        result = graph.query(query)

        if not result.result_set:
            return HighwayMetric(0, 0, 0.0, [], [], HealthStatus.GREEN)

        highways = [
            {
                'source_id': row[0],
                'target_id': row[1],
                'weight': row[2] if len(row) > 2 else 1
            }
            for row in result.result_set
        ]

        total_highways = len(highways)
        total_crossings = sum(h['weight'] for h in highways)
        mean_crossings = float(total_crossings) / total_highways if total_highways > 0 else 0.0

        # Get top 20 backbone highways by weight
        backbone_highways = sorted(highways, key=lambda h: h['weight'], reverse=True)[:20]

        # Status based on highway count
        # Low count = concerning (isolated SubEntities)
        if total_highways >= 15:
            status = HealthStatus.GREEN
        elif total_highways >= 5:
            status = HealthStatus.AMBER
        else:
            status = HealthStatus.RED

        return HighwayMetric(
            total_highways=total_highways,
            total_crossings=int(total_crossings),
            mean_crossings_per_highway=mean_crossings,
            highways=highways,
            backbone_highways=backbone_highways,
            status=status
        )

    async def compute_trends(self, graph_id: str) -> Dict[str, TrendDirection]:
        """Compute trend direction for each metric"""
        # TODO: Implement EMA slope analysis over last 30 days
        return {
            'density': TrendDirection.STABLE,
            'overlap': TrendDirection.STABLE,
            'orphan_ratio': TrendDirection.STABLE
        }

    def compute_overall_status(self, snapshot: GraphHealthSnapshot) -> HealthStatus:
        """Compute overall health status from all metrics"""
        statuses = []

        if snapshot.density:
            statuses.append(snapshot.density.status)
        if snapshot.overlap:
            statuses.append(snapshot.overlap.status)
        if snapshot.entity_size:
            statuses.append(snapshot.entity_size.status)
        if snapshot.orphans:
            statuses.append(snapshot.orphans.status)
        if snapshot.highways:
            statuses.append(snapshot.highways.status)

        if not statuses:
            return HealthStatus.GREEN

        # Worst status wins
        if HealthStatus.RED in statuses:
            return HealthStatus.RED
        elif HealthStatus.AMBER in statuses:
            return HealthStatus.AMBER
        else:
            return HealthStatus.GREEN

    def get_flagged_metrics(self, snapshot: GraphHealthSnapshot) -> List[str]:
        """Get list of metrics in AMBER or RED status"""
        flagged = []

        if snapshot.density and snapshot.density.status != HealthStatus.GREEN:
            flagged.append('density')
        if snapshot.overlap and snapshot.overlap.status != HealthStatus.GREEN:
            flagged.append('overlap')
        if snapshot.entity_size and snapshot.entity_size.status != HealthStatus.GREEN:
            flagged.append('entity_size')
        if snapshot.orphans and snapshot.orphans.status != HealthStatus.GREEN:
            flagged.append('orphans')
        if snapshot.highways and snapshot.highways.status != HealthStatus.GREEN:
            flagged.append('highways')

        return flagged

    def status_changed(self, graph_id: str, new_status: HealthStatus) -> bool:
        """Check if overall status changed"""
        old_status = self.previous_status.get(graph_id)
        self.previous_status[graph_id] = new_status
        return old_status is not None and old_status != new_status

    async def generate_alert(self, graph_id: str, snapshot: GraphHealthSnapshot) -> Dict[str, Any]:
        """Generate health alert event"""
        old_status = self.previous_status.get(graph_id, HealthStatus.GREEN)

        flagged_metrics = []
        for metric_name in snapshot.flagged_metrics:
            metric = getattr(snapshot, metric_name, None)
            if metric and hasattr(metric, 'status'):
                flagged_metrics.append({
                    'metric': metric_name,
                    'status': metric.status.value,
                    'current_value': getattr(metric, metric_name.replace('_', ''), 0.0),
                    'percentile': getattr(metric, 'percentile', 0.0),
                    'threshold': 'q90' if metric.status == HealthStatus.RED else 'q80'
                })

        procedures = await self.recommend_procedures(snapshot)

        return {
            'type': 'graph.health.alert',
            'graph_id': graph_id,
            'timestamp': snapshot.timestamp,
            'severity': snapshot.overall_status.value,
            'previous_severity': old_status.value,
            'flagged_metrics': flagged_metrics,
            'procedures': procedures
        }

    async def recommend_procedures(self, snapshot: GraphHealthSnapshot) -> List[Dict[str, Any]]:
        """Recommend procedures based on health issues"""
        procedures = []

        if snapshot.orphans and snapshot.orphans.status == HealthStatus.RED:
            procedures.append({
                'metric': 'orphans',
                'severity': 'HIGH',
                'procedure': 'backfill_orphans',
                'description': f"{snapshot.orphans.orphan_ratio*100:.1f}% orphan ratio detected. Run one-time backfill using centroid/medoid matching with learned priors.",
                'parameters': {
                    'learned_threshold': 0.55,
                    'weight_init': 0.42
                }
            })

        if snapshot.overlap and snapshot.overlap.status == HealthStatus.AMBER:
            procedures.append({
                'metric': 'overlap',
                'severity': 'MEDIUM',
                'procedure': 'sparsify_memberships',
                'description': f"Overlap ratio {snapshot.overlap.overlap_ratio:.2f} is elevated. Prune weak memberships below learned floor.",
                'parameters': {
                    'learned_floor': 0.15
                }
            })

        return procedures

    async def emit_snapshot(self, snapshot: GraphHealthSnapshot):
        """Emit health snapshot event to WebSocket"""
        # Convert to dict for JSON serialization
        event_data = {
            'type': snapshot.type,
            'graph_id': snapshot.graph_id,
            'timestamp': snapshot.timestamp,
            'history_window_days': snapshot.history_window_days,
            'overall_status': snapshot.overall_status.value,
            'flagged_metrics': snapshot.flagged_metrics,
            'density': asdict(snapshot.density) if snapshot.density else None,
            'overlap': asdict(snapshot.overlap) if snapshot.overlap else None,
            'entity_size': asdict(snapshot.entity_size) if snapshot.entity_size else None,
            'orphans': asdict(snapshot.orphans) if snapshot.orphans else None,
            'highways': asdict(snapshot.highways) if snapshot.highways else None,
            'trends': snapshot.trends
        }

        # Emit via WebSocket
        await self.ws.broadcast(event_data)
        logger.info(f"Emitted health snapshot for {snapshot.graph_id}: {snapshot.overall_status.value}")

    async def emit_alert(self, alert: Dict[str, Any]):
        """Emit health alert event to WebSocket"""
        await self.ws.broadcast(alert)
        logger.warning(f"Emitted health alert for {alert['graph_id']}: {alert['severity']}")
