"""
Learning Heartbeat - Monitor weight learning activity

Writes learning statistics to .heartbeats/learning_YYYYMMDD_HHMMSS.json
so we can verify the sophisticated weight learning is actually running.

Author: Felix "Ironhand"
Date: 2025-10-21
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class LearningHeartbeat:
    """
    Track weight learning activity and write heartbeats.

    Monitors:
    - Total nodes processed
    - Total weight updates applied
    - Average log_weight delta
    - EMA statistics
    - Processing times
    """

    def __init__(self, heartbeat_dir: str = ".heartbeats"):
        """
        Initialize heartbeat writer.

        Args:
            heartbeat_dir: Directory to write heartbeat files
        """
        self.heartbeat_dir = Path(heartbeat_dir)
        self.heartbeat_dir.mkdir(exist_ok=True)

        # Cumulative statistics
        self.total_traces_processed = 0
        self.total_nodes_processed = 0
        self.total_updates_applied = 0
        self.total_log_weight_delta = 0.0
        self.total_processing_time_ms = 0.0

        # Per-trace statistics (reset each write)
        self.current_trace_stats = {
            'nodes_processed': 0,
            'updates_applied': 0,
            'log_weight_delta': 0.0,
            'processing_time_ms': 0.0
        }

        # Individual weight updates (for detailed telemetry)
        self.weight_updates = []

    def record_weight_update(
        self,
        node_id: str,
        channel: str,
        delta_log_weight: float,
        z_score: float,
        learning_rate: float,
        local_overlays: list = None
    ):
        """
        Record individual weight update with entity attribution (Priority 4).

        Args:
            node_id: Node being updated
            channel: Learning channel (e.g., "trace", "wm")
            delta_log_weight: Global weight change
            z_score: Z-score used for learning
            learning_rate: Adaptive learning rate
            local_overlays: Entity-specific overlay updates (Priority 4)
        """
        update_record = {
            'node_id': node_id,
            'channel': channel,
            'delta_log_weight': round(delta_log_weight, 4),
            'z_score': round(z_score, 3),
            'learning_rate': round(learning_rate, 3),
            'timestamp': datetime.now().isoformat()
        }

        # Add entity attribution if available (Priority 4)
        if local_overlays:
            update_record['local_overlays'] = [
                {
                    'entity': overlay['entity'],
                    'delta': round(overlay['delta'], 4),
                    'overlay_after': round(overlay['overlay_after'], 4),
                    'membership_weight': round(overlay['membership_weight'], 3)
                }
                for overlay in local_overlays
            ]

        self.weight_updates.append(update_record)

    def record_trace_processing(
        self,
        nodes_processed: int,
        updates_applied: int,
        log_weight_delta: float,
        processing_time_ms: float
    ):
        """
        Record statistics for a single TRACE processing.

        Args:
            nodes_processed: Number of nodes loaded for cohort
            updates_applied: Number of weight updates applied
            log_weight_delta: Total log_weight change across all updates
            processing_time_ms: Processing time in milliseconds
        """
        # Update cumulative stats
        self.total_traces_processed += 1
        self.total_nodes_processed += nodes_processed
        self.total_updates_applied += updates_applied
        self.total_log_weight_delta += log_weight_delta
        self.total_processing_time_ms += processing_time_ms

        # Update current trace stats
        self.current_trace_stats['nodes_processed'] = nodes_processed
        self.current_trace_stats['updates_applied'] = updates_applied
        self.current_trace_stats['log_weight_delta'] = log_weight_delta
        self.current_trace_stats['processing_time_ms'] = processing_time_ms

    def write_heartbeat(self):
        """
        Write heartbeat file with current statistics.

        Creates a timestamped JSON file in .heartbeats/
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        heartbeat_file = self.heartbeat_dir / f"learning_{timestamp}.json"

        heartbeat_data = {
            'timestamp': datetime.now().isoformat(),
            'cumulative': {
                'total_traces_processed': self.total_traces_processed,
                'total_nodes_processed': self.total_nodes_processed,
                'total_updates_applied': self.total_updates_applied,
                'total_log_weight_delta': round(self.total_log_weight_delta, 3),
                'total_processing_time_ms': round(self.total_processing_time_ms, 2),
                'avg_updates_per_trace': (
                    round(self.total_updates_applied / self.total_traces_processed, 2)
                    if self.total_traces_processed > 0 else 0
                ),
                'avg_log_weight_delta_per_update': (
                    round(self.total_log_weight_delta / self.total_updates_applied, 4)
                    if self.total_updates_applied > 0 else 0
                )
            },
            'current_trace': self.current_trace_stats,
            'weight_updates': self.weight_updates,  # NEW: Detailed updates with entity attribution
            'health': {
                'learning_active': self.total_updates_applied > 0,
                'traces_processed': self.total_traces_processed,
                'status': self._compute_status()
            }
        }

        # Reset weight_updates after writing
        self.weight_updates = []

        try:
            with open(heartbeat_file, 'w') as f:
                json.dump(heartbeat_data, f, indent=2)

            logger.debug(f"[LearningHeartbeat] Wrote heartbeat to {heartbeat_file}")

        except Exception as e:
            logger.error(f"[LearningHeartbeat] Failed to write heartbeat: {e}")

    def _compute_status(self) -> str:
        """
        Compute overall health status.

        Returns:
            "healthy" | "degraded" | "inactive"
        """
        if self.total_traces_processed == 0:
            return "inactive"

        # Healthy if we're getting updates on most traces
        update_rate = self.total_updates_applied / self.total_traces_processed

        if update_rate >= 1.0:
            return "healthy"
        elif update_rate >= 0.1:
            return "degraded"
        else:
            return "inactive"

    def get_summary(self) -> Dict[str, Any]:
        """
        Get current statistics summary.

        Returns:
            Dict with cumulative and current trace stats
        """
        return {
            'total_traces_processed': self.total_traces_processed,
            'total_updates_applied': self.total_updates_applied,
            'avg_updates_per_trace': (
                round(self.total_updates_applied / self.total_traces_processed, 2)
                if self.total_traces_processed > 0 else 0
            ),
            'status': self._compute_status()
        }
