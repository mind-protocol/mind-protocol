# MEMBER_OF Edge-Based Membership Persistence - Integration Specification

**Status:** Ready for Implementation (Atlas)
**Priority:** P1 (Unblocks Dashboard Entity Visualization)
**Created:** 2025-10-25
**Author:** Ada (Architect) with implementation guidance from Nicolas

---

## Executive Summary

Complete migration from cache-only entity activation tracking to edge-based canonical truth with denormalized cache. Implements proper graph database pattern: relationship data lives on edges, nodes cache for performance.

**What This Delivers:**
- ✅ Canonical truth on `MEMBER_OF` edges (weight, activation stats)
- ✅ API endpoint for entity membership queries (`/entity/:id/members`)
- ✅ Event-driven cache invalidation (real-time dashboard updates)
- ✅ P1 dashboard blocker removed (entity visualization complete)

**Integration Points:**
1. Database schema setup (constraints + indexes)
2. Persistence layer (FalkorDB adapter batch upserts)
3. API layer (new endpoint in control_api.py)
4. Cache layer (rebuild from edges via write-through)
5. Observability layer (3 new event types)

---

## Architecture Pattern: Truth on Edges, Cache on Nodes

### Canonical Truth (MEMBER_OF Edge Properties)

```cypher
(:Node)-[r:MEMBER_OF {
  weight: float,                  // membership strength (log-domain)
  activation_ema: float,          // running average of activation
  activation_count: int,          // total times this node activated this entity
  last_activated_ts: int,         // milliseconds timestamp
  created_at: int,                // edge creation time
  updated_at: int                 // last modification time
}]->(:Subentity)
```

**Lifecycle:**
- **Created:** Entity bootstrap (initial memberships materialized)
- **Updated:** Entity weight learning (adjusts weights from co-activation)
- **Read:** Entity activation (every tick for energy computation)
- **Pruned:** Sparsification (memberships below learned floor deleted)
- **Deleted:** Entity dissolution (all edges removed)

### Denormalized Cache (Node Property)

```python
node.entity_activations: Dict[str, Dict[str, float]] = {
    "E.architect": {
        "activation_ema": 0.63,
        "last_ts": 1730074800000,
        "weight": 1.42
    },
    "E.runtime": {
        "activation_ema": 0.27,
        "last_ts": 1730074798000,
        "weight": 0.88
    }
    # ... top-K entities by activation_ema
}
```

**Rebuild Policy:**
- **Write-through:** After batch flush that updates MEMBER_OF for a node
- **Periodic sweep:** Background task for drift correction (hourly or on high change volume)
- **Always derived from edges** - can be rebuilt at any time

---

## Integration 1: Database Schema Setup

### File: `orchestration/scripts/setup_membership_schema.py` (NEW)

One-time migration script to create constraints and indexes.

```python
"""
Setup MEMBER_OF edge schema - constraints and indexes.
Run once during deployment or migration.
"""

import redis
from orchestration.libs.utils.falkordb_adapter import get_falkordb_client

CONSTRAINTS_AND_INDEXES = [
    # Node & SubEntity constraints
    """
    CREATE CONSTRAINT node_id IF NOT EXISTS
    FOR (n:Node) REQUIRE n.id IS UNIQUE
    """,
    """
    CREATE CONSTRAINT subentity_id IF NOT EXISTS
    FOR (e:SubEntity) REQUIRE e.id IS UNIQUE
    """,

    # MEMBER_OF edge indexes for query performance
    """
    CREATE INDEX member_of_weight IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.weight)
    """,
    """
    CREATE INDEX member_of_last_ts IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.last_activated_ts)
    """,
    """
    CREATE INDEX member_of_activation IF NOT EXISTS
    FOR ()-[r:MEMBER_OF]-() ON (r.activation_ema)
    """
]

def setup_membership_schema(graph_id: str = "citizen_felix"):
    """
    Create constraints and indexes for MEMBER_OF edge schema.

    Args:
        graph_id: FalkorDB graph ID (default: citizen_felix)
    """
    client = get_falkordb_client()

    for query in CONSTRAINTS_AND_INDEXES:
        try:
            result = client.execute_command("GRAPH.QUERY", graph_id, query)
            print(f"✓ Executed: {query.strip()[:60]}...")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"⊘ Already exists: {query.strip()[:60]}...")
            else:
                print(f"✗ Error: {e}")
                raise

    print(f"\n✅ Schema setup complete for graph: {graph_id}")

if __name__ == "__main__":
    setup_membership_schema()
```

**When to Run:** Once during initial deployment, or as part of migration pipeline

**Success Criteria:** All constraints created without error, indexes built

---

## Integration 2: Edge Persistence Layer

### File: `orchestration/libs/utils/falkordb_adapter.py` (EXTEND EXISTING)

Add batch upsert function for MEMBER_OF edges.

```python
def flush_membership_edges(client, graph_id: str, memberships: List[Dict[str, Any]]) -> int:
    """
    Batch upsert MEMBER_OF edges with activation stats.

    Args:
        client: Redis client connected to FalkorDB
        graph_id: Target graph (e.g., "citizen_felix")
        memberships: List of membership updates, each containing:
            {
                "node_id": str,
                "entity_id": str,
                "weight_new": float,        // updated weight
                "weight_init": float,       // initial weight if creating
                "activation_ema": float,
                "activation_count_inc": int,
                "last_activated_ts": int    // milliseconds
            }

    Returns:
        Number of edges upserted

    Example:
        >>> memberships = [
        ...     {"node_id": "n1", "entity_id": "E.architect",
        ...      "weight_new": 1.42, "weight_init": 0.4,
        ...      "activation_ema": 0.63, "activation_count_inc": 1,
        ...      "last_activated_ts": 1730074800000},
        ...     {"node_id": "n2", "entity_id": "E.architect",
        ...      "weight_new": 0.88, "weight_init": 0.3,
        ...      "activation_ema": 0.27, "activation_count_inc": 0}
        ... ]
        >>> flush_membership_edges(client, "citizen_felix", memberships)
        2
    """
    if not memberships:
        return 0

    # Batched upsert query
    query = """
    UNWIND $memberships AS m
    MERGE (n:Node {id: m.node_id})
    MERGE (e:SubEntity {id: m.entity_id})
    MERGE (n)-[r:MEMBER_OF]->(e)
    ON CREATE SET
      r.weight = m.weight_init,
      r.activation_ema = coalesce(m.activation_ema, 0.0),
      r.activation_count = coalesce(m.activation_count_inc, 0),
      r.last_activated_ts = coalesce(m.last_activated_ts, timestamp()),
      r.created_at = timestamp(),
      r.updated_at = timestamp()
    ON MATCH SET
      r.weight = m.weight_new,
      r.activation_ema = m.activation_ema,
      r.activation_count = coalesce(r.activation_count, 0) + coalesce(m.activation_count_inc, 0),
      r.last_activated_ts = coalesce(m.last_activated_ts, r.last_activated_ts),
      r.updated_at = timestamp()
    """

    params = {"memberships": memberships}

    try:
        result = client.execute_command("GRAPH.QUERY", graph_id, query,
                                       "--params", json.dumps(params))
        return len(memberships)
    except Exception as e:
        logger.error(f"Failed to flush {len(memberships)} membership edges: {e}")
        raise


def rebuild_node_entity_activations_cache(client, graph_id: str, node_id: str, k: int = 10) -> Dict:
    """
    Rebuild node.entity_activations from MEMBER_OF edges (top-K by activation_ema).

    Args:
        client: Redis client
        graph_id: Target graph
        node_id: Node to rebuild cache for
        k: Number of top entities to cache (default: 10)

    Returns:
        Rebuilt cache dict {entity_id: {activation_ema, last_ts, weight}}
    """
    # Query top-K MEMBER_OF edges by activation_ema
    query = """
    MATCH (n:Node {id: $node_id})-[r:MEMBER_OF]->(e:SubEntity)
    WITH e.id AS eid, r.activation_ema AS a, r.last_activated_ts AS ts, r.weight AS w
    ORDER BY a DESC NULLS LAST
    LIMIT $k
    RETURN collect([eid, {activation_ema: a, last_ts: ts, weight: w}]) AS pairs
    """

    params = {"node_id": node_id, "k": k}
    result = client.execute_command("GRAPH.QUERY", graph_id, query,
                                   "--params", json.dumps(params))

    # Parse result into dict
    if result and len(result) > 1 and result[1]:
        pairs = result[1][0][0]  # First row, first column
        cache = {eid: stats for eid, stats in pairs}
    else:
        cache = {}

    # Write cache back to node
    update_query = """
    MATCH (n:Node {id: $node_id})
    SET n.entity_activations = $cache,
        n.entity_activations_updated_at = timestamp()
    """
    client.execute_command("GRAPH.QUERY", graph_id, update_query,
                         "--params", json.dumps({"node_id": node_id, "cache": json.dumps(cache)}))

    return cache
```

**Integration Point:** Call `flush_membership_edges()` from consciousness_engine_v2.py after entity_weight_learning updates

**Integration Point:** Call `rebuild_node_entity_activations_cache()` after flushing edges (write-through cache)

---

## Integration 3: API Endpoint for Entity Members

### File: `orchestration/adapters/api/control_api.py` (ADD ROUTE)

Add endpoint to existing router for querying entity membership.

```python
# Add to existing imports
from typing import Literal

# Add to router (around line 700, after other entity endpoints)

@router.get("/entity/{entity_id}/members")
async def get_entity_members(
    entity_id: str,
    limit: int = Query(100, ge=1, le=1000),
    sort: Literal["weight", "activation", "recent"] = "weight",
    order: Literal["desc", "asc"] = "desc"
):
    """
    Query members of an entity with their membership stats.

    Args:
        entity_id: Entity to query (e.g., "E.architect")
        limit: Max members to return (1-1000, default 100)
        sort: Sort by "weight" (structure), "activation" (recent activity), or "recent" (time)
        order: "desc" or "asc"

    Returns:
        {
            "entity_id": str,
            "count": int,
            "members": [
                {
                    "node_id": str,
                    "name": str,
                    "weight": float,
                    "activation_ema": float,
                    "activation_count": int,
                    "last_activated_ts": int
                },
                ...
            ]
        }

    Example:
        GET /api/entity/E.architect/members?sort=activation&order=desc&limit=20
    """
    # Map sort param to property (whitelist to prevent injection)
    sort_map = {
        "weight": "r.weight",
        "activation": "r.activation_ema",
        "recent": "r.last_activated_ts"
    }
    sort_by = sort_map.get(sort, "r.weight")

    query = f"""
    MATCH (n:Node)-[r:MEMBER_OF]->(e:SubEntity {{id: $entity_id}})
    RETURN n.id AS node_id,
           coalesce(n.name, n.id) AS name,
           r.weight AS weight,
           r.activation_ema AS activation_ema,
           r.activation_count AS activation_count,
           r.last_activated_ts AS last_activated_ts
    ORDER BY {sort_by} {order.upper()}
    LIMIT $limit
    """

    params = {"entity_id": entity_id, "limit": limit}

    try:
        r = get_redis_client()
        # Determine graph from entity_id prefix or use default
        graph_id = "citizen_felix"  # TODO: extract from entity_id or query param

        result = r.execute_command("GRAPH.QUERY", graph_id, query,
                                  "--params", json.dumps(params))

        members = []
        if result and len(result) > 1:
            header = result[0]
            rows = result[1]

            for row in rows:
                member = {}
                for i, col_name in enumerate(header):
                    col_str = col_name.decode('utf-8') if isinstance(col_name, bytes) else col_name
                    value = row[i]
                    member[col_str] = value.decode('utf-8') if isinstance(value, bytes) else value
                members.append(member)

        return {
            "entity_id": entity_id,
            "count": len(members),
            "members": members
        }

    except Exception as e:
        logger.error(f"Failed to query entity members: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Integration Point:** Existing control_api.py router, add after other entity endpoints

**P1 Dashboard Unblock:** Frontend can now query and display entity membership with sorting

---

## Integration 4: Observability Events

### File: `orchestration/mechanisms/subentity_weight_learning_observe.py` (NEW)

Event emitters for membership changes.

```python
"""
Observability events for subentity weight learning and membership changes.
Emits real-time events via WebSocket broadcaster for dashboard visualization.
"""

from typing import List, Dict, Any, Optional
from time import time
import logging

logger = logging.getLogger(__name__)


async def emit_weights_updated(
    broadcaster,
    level: str,
    citizen_id: str,
    frame_id: int,
    run_id: str,
    entity_id: str,
    entity_name: str,
    changes: List[Dict[str, Any]],
    stats: Dict[str, Any],
    mission_id: Optional[str] = None,
    stimulus_id: Optional[str] = None
):
    """
    Emit subentity.weights.updated event when membership weights change.

    Args:
        broadcaster: WebSocket broadcaster instance
        level: Graph level ("N1" | "N2" | "N3")
        citizen_id: Citizen identifier
        frame_id: Engine frame number
        run_id: Process run identifier
        entity_id: Entity that changed (e.g., "E.architect")
        entity_name: Human-readable entity name
        changes: List of membership changes, each:
            {
                "node_id": str,
                "weight_prev": float,
                "weight_new": float,
                "delta": float,
                "activation_ema": float,
                "activation_count_inc": int,
                "last_activated_ts": int
            }
        stats: Entity-level stats:
            {
                "cohesion_before": float,
                "cohesion_after": float,
                "stability_z": float,
                "formation_quality_q": float,
                "num_pruned": int,
                "budget_method": str,
                "ema_alpha": float
            }
        mission_id: Optional mission context
        stimulus_id: Optional stimulus context

    Example:
        >>> await emit_weights_updated(
        ...     broadcaster, "N1", "felix", 2341, "2025-10-25T07:11Z@felix",
        ...     "E.runtime", "Runtime Engineering",
        ...     changes=[{
        ...         "node_id": "N.diffusion_note",
        ...         "weight_prev": 0.62, "weight_new": 0.69, "delta": 0.07,
        ...         "activation_ema": 0.41, "activation_count_inc": 1,
        ...         "last_activated_ts": 1730074798123
        ...     }],
        ...     stats={"cohesion_after": 0.75, "stability_z": 1.8, "num_pruned": 0}
        ... )
    """
    if not broadcaster:
        logger.debug("No broadcaster available, skipping weights.updated event")
        return

    event = {
        "topic": "subentity.weights.updated",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "frame_id": frame_id,
        "run_id": run_id,
        "mission_id": mission_id,
        "stimulus_id": stimulus_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:frame{frame_id}",
        "payload": {
            "entity": {
                "id": entity_id,
                "name": entity_name,
                "cohesion_before": stats.get("cohesion_before"),
                "cohesion_after": stats.get("cohesion_after"),
                "stability_z": stats.get("stability_z"),
                "formation_quality_q": stats.get("formation_quality_q"),
            },
            "stats": {
                "num_updated": len(changes),
                "num_pruned": stats.get("num_pruned", 0),
                "budget_method": stats.get("budget_method"),
                "ema_alpha": stats.get("ema_alpha"),
            },
            "memberships": changes
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted weights.updated for {entity_id}: {len(changes)} changes")


async def emit_membership_pruned(
    broadcaster,
    level: str,
    citizen_id: str,
    frame_id: int,
    run_id: str,
    entity_id: str,
    node_id: str,
    weight_prev: float,
    activation_ema_prev: float,
    reason: str = "below_learned_floor"
):
    """
    Emit subentity.membership.pruned event when MEMBER_OF edge deleted.

    Args:
        broadcaster: WebSocket broadcaster
        level: Graph level
        citizen_id: Citizen identifier
        frame_id: Engine frame
        run_id: Process run ID
        entity_id: Entity losing member
        node_id: Node being pruned
        weight_prev: Previous weight before pruning
        activation_ema_prev: Previous activation EMA
        reason: Why pruned ("below_learned_floor" | "stale_membership" | "entity_dissolved")
    """
    if not broadcaster:
        return

    event = {
        "topic": "subentity.membership.pruned",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "frame_id": frame_id,
        "run_id": run_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:{node_id}:frame{frame_id}",
        "payload": {
            "entity_id": entity_id,
            "node_id": node_id,
            "weight_prev": weight_prev,
            "activation_ema_prev": activation_ema_prev,
            "reason": reason
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted membership.pruned: {node_id} from {entity_id}")


async def emit_lifecycle_event(
    broadcaster,
    level: str,
    citizen_id: str,
    run_id: str,
    entity_id: str,
    prev_status: str,
    new_status: str,
    evidence: Dict[str, float]
):
    """
    Emit subentity.lifecycle event for entity promotion/dissolution.

    Args:
        broadcaster: WebSocket broadcaster
        level: Graph level
        citizen_id: Citizen identifier
        run_id: Process run ID
        entity_id: Entity changing status
        prev_status: Previous status ("candidate" | "provisional" | "mature")
        new_status: New status
        evidence: Evidence for transition:
            {
                "formation_quality_q": float,
                "stability_z": float,
                "membership_drift_q": float
            }
    """
    if not broadcaster:
        return

    event = {
        "topic": "subentity.lifecycle",
        "v": "1",
        "ts_ms": int(time() * 1000),
        "level": level,
        "citizen_id": citizen_id,
        "run_id": run_id,
        "dedupe_key": f"{citizen_id}:{level}:{entity_id}:{new_status}:{time()}",
        "payload": {
            "entity_id": entity_id,
            "prev_status": prev_status,
            "new_status": new_status,
            "evidence": evidence
        }
    }

    await broadcaster.broadcast_event(event["topic"], event)
    logger.info(f"Emitted lifecycle: {entity_id} {prev_status} → {new_status}")
```

**Integration Point:** Import and call from entity_weight_learning mechanism after weight updates

**Telemetry Counters:** Increment on each emit:
- `events.subentity.weights.updated.total` and `.last_60s`
- `events.subentity.membership.pruned.total` and `.last_60s`
- `events.subentity.lifecycle.total` and `.last_60s`

---

## Integration 5: Frontend TypeScript Types

### File: `app/consciousness/types/events.ts` (ADD TYPES)

```typescript
export type SubentityWeightsUpdatedV1 = {
  topic: "subentity.weights.updated";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  mission_id?: string;
  stimulus_id?: string;
  dedupe_key: string;
  payload: {
    entity: {
      id: string;
      name?: string;
      cohesion_before?: number;
      cohesion_after?: number;
      stability_z?: number;
      formation_quality_q?: number;
    };
    stats: {
      num_updated: number;
      num_pruned: number;
      budget_method?: "sainte-lague" | "hamilton" | string;
      ema_alpha?: number;
    };
    memberships: Array<{
      node_id: string;
      weight_prev?: number;
      weight_new?: number;
      delta?: number;
      activation_ema?: number;
      activation_count_inc?: number;
      last_activated_ts?: number;
    }>;
  };
};

export type SubentityMembershipPrunedV1 = {
  topic: "subentity.membership.pruned";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  frame_id?: number;
  run_id: string;
  dedupe_key: string;
  payload: {
    entity_id: string;
    node_id: string;
    weight_prev: number;
    activation_ema_prev: number;
    reason: "below_learned_floor" | "stale_membership" | "entity_dissolved";
  };
};

export type SubentityLifecycleV1 = {
  topic: "subentity.lifecycle";
  v: "1";
  ts_ms: number;
  level: "N1" | "N2" | "N3";
  citizen_id: string;
  run_id: string;
  dedupe_key: string;
  payload: {
    entity_id: string;
    prev_status: "candidate" | "provisional" | "mature";
    new_status: "candidate" | "provisional" | "mature" | "dissolved";
    evidence: {
      formation_quality_q?: number;
      stability_z?: number;
      membership_drift_q?: number;
    };
  };
};

// Add to existing event union type
export type ConsciousnessEvent =
  | NodeFlipV1
  | LinkFlowSummaryV1
  | SubentityWeightsUpdatedV1
  | SubentityMembershipPrunedV1
  | SubentityLifecycleV1;
```

**Integration Point:** Dashboard components subscribe to these events for real-time membership visualization

---

## Integration 6: Backfill Migration (One-Time)

### File: `orchestration/scripts/migrate_entity_activations_to_edges.py` (NEW)

Migrate existing `node.entity_activations` JSON cache to MEMBER_OF edge properties.

```python
"""
One-time migration: node.entity_activations JSON → MEMBER_OF edge properties.
Converts denormalized cache to canonical edge truth.
"""

import redis
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def migrate_entity_activations_to_edges(graph_id: str = "citizen_felix"):
    """
    Migrate node.entity_activations cache to MEMBER_OF edge properties.

    For each node with entity_activations:
    1. Parse JSON cache
    2. Create/update MEMBER_OF edges with activation stats
    3. Mark migration complete

    Args:
        graph_id: Target graph to migrate
    """
    client = redis.Redis(host='localhost', port=6379, decode_responses=False)

    # Query all nodes with entity_activations cache
    query = """
    MATCH (n:Node)
    WHERE n.entity_activations IS NOT NULL
    RETURN n.id AS node_id, n.entity_activations AS cache
    LIMIT 1000
    """

    result = client.execute_command("GRAPH.QUERY", graph_id, query)

    if not result or len(result) < 2:
        logger.info("No nodes with entity_activations found")
        return 0

    header = result[0]
    rows = result[1]

    migrated = 0

    for row in rows:
        node_id = row[0].decode('utf-8') if isinstance(row[0], bytes) else row[0]
        cache_str = row[1].decode('utf-8') if isinstance(row[1], bytes) else row[1]

        try:
            cache = json.loads(cache_str) if isinstance(cache_str, str) else cache_str
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse cache for {node_id}: {e}")
            continue

        # Materialize each cached entity activation as MEMBER_OF edge
        for entity_id, stats in cache.items():
            migrate_query = """
            MATCH (n:Node {id: $node_id})
            MERGE (e:SubEntity {id: $entity_id})
            MERGE (n)-[r:MEMBER_OF]->(e)
            SET r.activation_ema = coalesce($activation_ema, r.activation_ema, 0.0),
                r.last_activated_ts = coalesce($last_ts, r.last_activated_ts),
                r.weight = coalesce($weight, r.weight, 0.0),
                r.updated_at = timestamp(),
                r.migrated_from_cache = true
            """

            params = {
                "node_id": node_id,
                "entity_id": entity_id,
                "activation_ema": stats.get("activation_ema"),
                "last_ts": stats.get("last_ts"),
                "weight": stats.get("weight")
            }

            try:
                client.execute_command("GRAPH.QUERY", graph_id, migrate_query,
                                     "--params", json.dumps(params))
                migrated += 1
            except Exception as e:
                logger.error(f"Failed to migrate {node_id} → {entity_id}: {e}")

    logger.info(f"✅ Migrated {migrated} entity activations to MEMBER_OF edges")

    # After migration, rebuild caches from edges to ensure consistency
    logger.info("Rebuilding caches from canonical edge truth...")
    rebuild_all_caches(client, graph_id)

    return migrated


def rebuild_all_caches(client, graph_id: str, k: int = 10):
    """Rebuild all node.entity_activations caches from MEMBER_OF edges."""
    # Batch rebuild query
    query = f"""
    CALL {{
      MATCH (n:Node)-[r:MEMBER_OF]->(e:SubEntity)
      WITH n, e.id AS eid, r.activation_ema AS a, r.last_activated_ts AS ts, r.weight AS w
      ORDER BY a DESC NULLS LAST
      WITH n, collect([eid, {{activation_ema:a, last_ts:ts, weight:w}}])[0..{k}] AS pairs
      WITH n, apoc.map.fromPairs(pairs) AS m
      SET n.entity_activations = m,
          n.entity_activations_updated_at = timestamp()
    }} IN TRANSACTIONS OF 1000 ROWS
    """

    try:
        client.execute_command("GRAPH.QUERY", graph_id, query)
        logger.info("✅ Rebuilt all caches from edges")
    except Exception as e:
        logger.error(f"Cache rebuild failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    migrate_entity_activations_to_edges()
```

**When to Run:** Once after edge persistence code is deployed, before removing old cache-only logic

---

## Integration 7: Sparsification (Membership Pruning)

### File: `orchestration/mechanisms/entity_weight_learning.py` (FUTURE - ADD LOGIC)

Periodic pruning of weak memberships to prevent "entity creep".

```python
async def prune_weak_memberships(
    client,
    graph_id: str,
    entity_id: str,
    weight_floor: float,
    broadcaster = None
):
    """
    Delete MEMBER_OF edges below learned weight floor.

    Args:
        client: Redis client
        graph_id: Target graph
        entity_id: Entity to prune
        weight_floor: Learned floor (cohort-based, no fixed constant)
        broadcaster: Optional broadcaster for events

    Returns:
        Number of edges pruned
    """
    # Query weak memberships
    query = """
    MATCH (n:Node)-[r:MEMBER_OF]->(e:SubEntity {id: $entity_id})
    WHERE r.weight < $weight_floor
    WITH n, r, e
    DELETE r
    RETURN n.id AS node_id, r.weight AS weight_prev, r.activation_ema AS activation_prev
    """

    params = {"entity_id": entity_id, "weight_floor": weight_floor}
    result = client.execute_command("GRAPH.QUERY", graph_id, query,
                                   "--params", json.dumps(params))

    # Emit pruning events
    if result and len(result) > 1 and broadcaster:
        rows = result[1]
        for row in rows:
            node_id = row[0]
            weight_prev = row[1]
            activation_prev = row[2]

            await emit_membership_pruned(
                broadcaster, "N1", "felix", 0, "run_id",
                entity_id, node_id, weight_prev, activation_prev,
                reason="below_learned_floor"
            )

    pruned_count = len(result[1]) if result and len(result) > 1 else 0
    logger.info(f"Pruned {pruned_count} weak memberships from {entity_id}")

    return pruned_count
```

**Integration Point:** Call periodically from entity_weight_learning mechanism after weight updates

**Learned Floor:** Derived from cohort statistics, not fixed constant (aligns with zero-constant principle)

---

## Success Criteria

### P1 Dashboard Unblock
- ✅ API endpoint `/entity/:id/members` returns sorted member list
- ✅ Frontend can query and display entity membership
- ✅ Membership stats (weight, activation, recent) visible in UI

### Data Integrity
- ✅ MEMBER_OF edges are canonical truth for membership
- ✅ node.entity_activations cache can be rebuilt from edges at any time
- ✅ Cache staleness bounded (write-through or periodic sweep)

### Observability
- ✅ `subentity.weights.updated` events emitted when weights change
- ✅ `subentity.membership.pruned` events emitted when edges deleted
- ✅ Dashboard shows real-time membership changes via WebSocket

### Performance
- ✅ Batch upserts handle 100+ membership updates per frame
- ✅ API queries return <100ms for typical entity (10-100 members)
- ✅ Cache rebuilds complete <50ms per node (top-K query)

---

## Testing Checklist

1. **Schema Setup**
   - Run setup_membership_schema.py
   - Verify constraints created without error
   - Verify indexes built successfully

2. **Edge Persistence**
   - Create test memberships via flush_membership_edges()
   - Query MEMBER_OF edges, verify properties present
   - Update weights, verify ON MATCH logic works

3. **API Endpoint**
   - Hit `/entity/:id/members?sort=weight&order=desc`
   - Verify sorted member list returned
   - Test all sort modes (weight, activation, recent)

4. **Cache Rebuild**
   - Update MEMBER_OF edges for a node
   - Call rebuild_node_entity_activations_cache()
   - Verify node.entity_activations matches top-K edges

5. **Events**
   - Emit weights.updated event with test data
   - Subscribe to WebSocket, verify event received
   - Verify dedupe_key prevents duplicates

6. **Backfill**
   - Run migrate_entity_activations_to_edges.py on test graph
   - Verify edges created from cache
   - Verify cache rebuilt from edges matches original

---

## Handoff to Atlas

**Owner:** Atlas (Infrastructure Engineer)

**Implementation Order:**
1. Schema setup script (run once, low risk)
2. Persistence layer (falkordb_adapter.py extensions)
3. API endpoint (control_api.py new route)
4. Observability events (new file, integrate with broadcaster)
5. Backfill migration (run once after #1-4 deployed)

**Dependencies:**
- Existing FalkorDB adapter infrastructure
- Existing WebSocket broadcaster (control_api.py)
- Existing consciousness_engine_v2.py frame loop

**Questions for Atlas:**
- Preferred migration strategy (backfill all at once vs gradual)?
- Cache rebuild cadence (write-through only or periodic sweep)?
- FalkorDB version/APOC availability (affects cache rebuild query)?

**Verification Support:**
- Ada available for architecture questions
- Felix available for consciousness integration questions
- Dashboard team (Iris) ready to test API endpoint

---

**Status:** Ready for Atlas implementation, P1 priority for dashboard unblock
