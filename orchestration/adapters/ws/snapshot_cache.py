"""
SnapshotCache - Retained Graph State for WebSocket Replay

ARCHITECTURAL PRINCIPLE: Decouple engine initialization from client connection timing

This module retains the last-known state of each citizen's graph so that new
WebSocket clients can receive a snapshot regardless of when they connect relative
to engine initialization.

Problem Solved:
- Engines broadcast at 01:42 during initialization
- Frontend connects at 01:47 (5 minutes later)
- Without cache: Frontend receives 0 nodes (broadcasts already happened)
- With cache: Frontend receives full snapshot from retained state

Author: Felix (Core Consciousness Engineer)
Created: 2025-10-31 (Dashboard Graph Zero Nodes Fix)
Architecture: Snapshot Cache + Replay-on-Connect pattern
"""

import logging
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class SnapshotCache:
    """
    Retained snapshot state for all citizens, replayed on new client connections.

    Thread-safe for single-process use (WebSocket server is single-process).
    For multi-process, use Redis or shared memory (future enhancement).

    Example Usage:
        >>> cache = SnapshotCache()
        >>> cache.upsert_node("atlas", {"id": "n1", "name": "Test", "type": "Concept"})
        >>> cache.upsert_link("atlas", {"source": "n1", "target": "n2", "type": "RELATES_TO"})
        >>> snapshot = cache.build_snapshot("atlas")
        >>> print(len(snapshot["nodes"]))  # 1
    """

    def __init__(self, max_nodes: int = 100_000, max_links: int = 200_000):
        """
        Initialize snapshot cache with size limits.

        Args:
            max_nodes: Maximum nodes to retain per citizen (防止内存爆炸)
            max_links: Maximum links to retain per citizen
        """
        # citizen_id -> {node_id: node_data}
        self.nodes: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # citizen_id -> {link_key: link_data}
        self.links: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # citizen_id -> {subentity_id: subentity_data}
        self.subentities: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # citizen_id -> last update timestamp
        self.ts: Dict[str, float] = {}

        self.max_nodes = max_nodes
        self.max_links = max_links

        logger.info(
            f"[SnapshotCache] Initialized (max_nodes={max_nodes}, max_links={max_links})"
        )

    def upsert_node(self, citizen_id: str, node: Dict[str, Any]) -> None:
        """
        Upsert node into retained snapshot.

        Args:
            citizen_id: Citizen identifier
            node: Node data dict with at least {"id": str}
        """
        node_id = node.get("id")
        if not node_id:
            logger.warning("[SnapshotCache] Skipping node with no id")
            return

        # Check size limit (LRU eviction would be better, but YAGNI for now)
        if len(self.nodes[citizen_id]) >= self.max_nodes:
            logger.warning(
                f"[SnapshotCache] Node limit reached for {citizen_id} "
                f"({self.max_nodes}), skipping upsert"
            )
            return

        self.nodes[citizen_id][node_id] = node
        self.ts[citizen_id] = time.time()

    def upsert_link(self, citizen_id: str, link: Dict[str, Any]) -> None:
        """
        Upsert link into retained snapshot.

        Args:
            citizen_id: Citizen identifier
            link: Link data dict with {"source": str, "target": str, "type": str}
        """
        source = link.get("source")
        target = link.get("target")
        link_type = link.get("type", "")

        if not source or not target:
            logger.warning("[SnapshotCache] Skipping link with no source/target")
            return

        # Unique key: source->target:type
        link_key = f"{source}->{target}:{link_type}"

        # Check size limit
        if len(self.links[citizen_id]) >= self.max_links:
            logger.warning(
                f"[SnapshotCache] Link limit reached for {citizen_id} "
                f"({self.max_links}), skipping upsert"
            )
            return

        self.links[citizen_id][link_key] = link
        self.ts[citizen_id] = time.time()

    def upsert_subentity(self, citizen_id: str, subentity: Dict[str, Any]) -> None:
        """
        Upsert subentity into retained snapshot.

        Args:
            citizen_id: Citizen identifier
            subentity: SubEntity data dict with at least {"id": str}
        """
        se_id = subentity.get("id")
        if not se_id:
            logger.warning("[SnapshotCache] Skipping subentity with no id")
            return

        self.subentities[citizen_id][se_id] = subentity
        self.ts[citizen_id] = time.time()

    def remove_node(self, citizen_id: str, node_id: str) -> None:
        """Remove node from snapshot (for delete events)."""
        self.nodes[citizen_id].pop(node_id, None)
        self.ts[citizen_id] = time.time()

    def remove_link(self, citizen_id: str, source: str, target: str, link_type: str = "") -> None:
        """Remove link from snapshot (for delete events)."""
        link_key = f"{source}->{target}:{link_type}"
        self.links[citizen_id].pop(link_key, None)
        self.ts[citizen_id] = time.time()

    def build_snapshot(self, citizen_id: str) -> Dict[str, Any]:
        """
        Build complete snapshot for a citizen.

        Args:
            citizen_id: Citizen identifier

        Returns:
            {
                "citizen_id": str,
                "nodes": List[dict],
                "links": List[dict],
                "subentities": List[dict],
                "ts": float
            }
        """
        return {
            "citizen_id": citizen_id,
            "nodes": list(self.nodes[citizen_id].values()),
            "links": list(self.links[citizen_id].values()),
            "subentities": list(self.subentities[citizen_id].values()),
            "ts": self.ts.get(citizen_id, time.time())
        }

    def get_all_citizen_ids(self) -> List[str]:
        """Get list of all citizens with cached data."""
        return list(self.nodes.keys())

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            {
                "citizens": int,
                "total_nodes": int,
                "total_links": int,
                "total_subentities": int,
                "per_citizen": Dict[str, Dict[str, int]]
            }
        """
        per_citizen = {}
        for cid in self.nodes.keys():
            per_citizen[cid] = {
                "nodes": len(self.nodes[cid]),
                "links": len(self.links[cid]),
                "subentities": len(self.subentities[cid]),
                "last_update": self.ts.get(cid, 0)
            }

        return {
            "citizens": len(self.nodes),
            "total_nodes": sum(len(nodes) for nodes in self.nodes.values()),
            "total_links": sum(len(links) for links in self.links.values()),
            "total_subentities": sum(len(ses) for ses in self.subentities.values()),
            "per_citizen": per_citizen
        }


# Global singleton instance
_snapshot_cache: Optional[SnapshotCache] = None


def get_snapshot_cache() -> SnapshotCache:
    """Get or create global snapshot cache singleton."""
    global _snapshot_cache
    if _snapshot_cache is None:
        _snapshot_cache = SnapshotCache()
    return _snapshot_cache
