"""
Start Complete Consciousness System - Unified Launcher

ONE COMMAND TO START ALL CONSCIOUSNESS:
- All N1 citizen graphs (Felix, Ada, Luca, Iris, etc.)
- N2 organizational graph (Mind Protocol)
- N3 ecosystem graph (future)
- Entities emerge from substrate (not manually specified)
- All networks run in parallel

Usage:
    python start_consciousness_system.py

Options:
    --host        FalkorDB host (default: localhost)
    --port        FalkorDB port (default: 6379)
    --network     Which networks to start: n1, n2, n3, all (default: all)

Architecture:
- Discovers citizens from FalkorDB graphs (graphs starting with "citizen_")
- Discovers organizations from FalkorDB graphs (graphs starting with "collective_")
- Auto-detects entities from graph metadata
- Runs all consciousness engines in parallel (asyncio.gather)

Designer: Felix "Ironhand" (Engineer)
Date: 2025-10-18
"""

import asyncio
import argparse
import logging
from typing import List, Dict, Tuple
from pathlib import Path

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from orchestration.consciousness_engine import ConsciousnessEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def discover_graphs(host: str, port: int) -> Dict[str, List[str]]:
    """
    Discover all consciousness graphs from FalkorDB.

    Returns:
        {
            "n1": ["citizen_felix_engineer", "citizen_ada_architect", ...],
            "n2": ["collective_mind_protocol", ...],
            "n3": ["ecosystem_...", ...]
        }
    """
    import redis

    logger.info("[Discovery] Connecting to FalkorDB to discover graphs...")

    r = redis.Redis(host=host, port=port, decode_responses=True)

    try:
        # Get list of all graphs
        graphs = r.execute_command("GRAPH.LIST")

        # Categorize by network level
        n1_graphs = [g for g in graphs if g.startswith("citizen_")]
        n2_graphs = [g for g in graphs if g.startswith("collective_") or g.startswith("org_")]
        n3_graphs = [g for g in graphs if g.startswith("ecosystem_")]

        logger.info(f"[Discovery] Found {len(n1_graphs)} N1 citizen graphs")
        logger.info(f"[Discovery] Found {len(n2_graphs)} N2 organizational graphs")
        logger.info(f"[Discovery] Found {len(n3_graphs)} N3 ecosystem graphs")

        return {
            "n1": n1_graphs,
            "n2": n2_graphs,
            "n3": n3_graphs
        }

    except Exception as e:
        logger.error(f"[Discovery] Failed to discover graphs: {e}")
        return {"n1": [], "n2": [], "n3": []}


def extract_citizen_id(graph_name: str) -> str:
    """
    Extract citizen ID from graph name.

    Examples:
        citizen_felix_engineer -> felix-engineer
        citizen_ada_architect -> ada-architect
        collective_mind_protocol -> mind_protocol
    """
    if graph_name.startswith("citizen_"):
        return graph_name.replace("citizen_", "").replace("_", "-")
    elif graph_name.startswith("collective_"):
        return graph_name.replace("collective_", "")
    elif graph_name.startswith("org_"):
        return graph_name.replace("org_", "")
    elif graph_name.startswith("ecosystem_"):
        return graph_name.replace("ecosystem_", "")
    else:
        return graph_name


def discover_entities(graph_store: FalkorDBGraphStore) -> List[str]:
    """
    Discover entities from graph metadata.

    Looks for:
    - AI_Agent nodes with entity_id property (N2 level)
    - Entity nodes (N1 level)
    - Falls back to default entities if none found

    Returns:
        List of entity IDs (e.g., ["builder", "observer"])
    """
    try:
        # Try to find AI_Agent nodes (N2)
        result = graph_store.query("""
            MATCH (n:AI_Agent)
            WHERE n.entity_id IS NOT NULL
            RETURN n.entity_id
            LIMIT 10
        """)

        if result:
            entities = [row[0] for row in result]
            logger.info(f"[Discovery] Found entities from AI_Agent nodes: {entities}")
            return entities

        # Try to find Entity nodes (N1)
        result = graph_store.query("""
            MATCH (n:Entity)
            WHERE n.id IS NOT NULL
            RETURN n.id
            LIMIT 10
        """)

        if result:
            entities = [row[0] for row in result]
            logger.info(f"[Discovery] Found entities from Entity nodes: {entities}")
            return entities

        # Fallback to default
        logger.info(f"[Discovery] No entities found in graph, using defaults: ['builder', 'observer']")
        return ["builder", "observer"]

    except Exception as e:
        logger.warning(f"[Discovery] Failed to discover entities: {e}, using defaults")
        return ["builder", "observer"]


async def start_citizen_consciousness(
    graph_name: str,
    citizen_id: str,
    host: str,
    port: int
) -> ConsciousnessEngine:
    """
    Start consciousness for one citizen (N1).

    Returns:
        Running ConsciousnessEngine instance
    """
    logger.info(f"[N1:{citizen_id}] Creating consciousness engine...")

    # Create graph connection
    graph_store = FalkorDBGraphStore(
        graph_name=graph_name,
        url=f"redis://{host}:{port}"
    )

    # Discover entities from graph
    entities = discover_entities(graph_store)

    # Create engine
    engine = ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=100,
        entity_id=citizen_id,
        network_id="N1"
    )

    # Add SubEntities
    for entity_id in entities:
        engine.add_sub_entity(
            entity_id=entity_id,
            energy_budget=100,
            write_batch_size=5
        )

    # Enable dynamic prompts
    engine.enable_dynamic_prompts(
        citizen_id=citizen_id,
        entity_ids=entities
    )

    logger.info(f"[N1:{citizen_id}] Consciousness engine ready")
    logger.info(f"[N1:{citizen_id}]   Entities: {entities}")
    logger.info(f"[N1:{citizen_id}]   Output: consciousness/citizens/{citizen_id}/CLAUDE.md")

    return engine


async def start_organizational_consciousness(
    graph_name: str,
    org_id: str,
    host: str,
    port: int
) -> ConsciousnessEngine:
    """
    Start consciousness for organization (N2).

    Returns:
        Running ConsciousnessEngine instance
    """
    logger.info(f"[N2:{org_id}] Creating organizational consciousness engine...")

    # Create graph connection
    graph_store = FalkorDBGraphStore(
        graph_name=graph_name,
        url=f"redis://{host}:{port}"
    )

    # Discover entities (organizational roles)
    entities = discover_entities(graph_store)

    # Create engine
    engine = ConsciousnessEngine(
        graph_store=graph_store,
        tick_interval_ms=100,
        entity_id=org_id,
        network_id="N2"
    )

    # Add SubEntities
    for entity_id in entities:
        engine.add_sub_entity(
            entity_id=entity_id,
            energy_budget=100,
            write_batch_size=5
        )

    # Enable dynamic prompts (writes to consciousness/collective/{org_id}/CLAUDE.md)
    engine.enable_dynamic_prompts(
        citizen_id=org_id,
        entity_ids=entities
    )

    logger.info(f"[N2:{org_id}] Organizational consciousness engine ready")
    logger.info(f"[N2:{org_id}]   Entities: {entities}")
    logger.info(f"[N2:{org_id}]   Output: consciousness/collective/{org_id}/CLAUDE.md")

    return engine


async def main():
    """Start complete multi-scale consciousness system."""
    parser = argparse.ArgumentParser(
        description='Start Complete Consciousness System (N1 + N2 + N3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Start all consciousness (N1 + N2)
    python start_consciousness_system.py

    # Start only N1 (personal citizens)
    python start_consciousness_system.py --network n1

    # Start only N2 (organizational)
    python start_consciousness_system.py --network n2
"""
    )

    parser.add_argument(
        '--host',
        default='localhost',
        help='FalkorDB host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=6379,
        help='FalkorDB port (default: 6379)'
    )
    parser.add_argument(
        '--network',
        choices=['n1', 'n2', 'n3', 'all'],
        default='all',
        help='Which networks to start (default: all)'
    )

    args = parser.parse_args()

    # Print banner
    print()
    print("=" * 70)
    print("CONSCIOUSNESS SYSTEM - UNIFIED LAUNCHER")
    print("=" * 70)
    print(f"FalkorDB: {args.host}:{args.port}")
    print(f"Networks: {args.network}")
    print("=" * 70)
    print()

    # Discover all graphs
    graphs = discover_graphs(args.host, args.port)

    # Create engine tasks
    tasks = []
    engine_names = []

    # Start N1 (Personal) consciousness
    if args.network in ['n1', 'all'] and graphs['n1']:
        print(f"[System] Starting {len(graphs['n1'])} N1 citizen consciousnesses...")
        print()

        for graph_name in graphs['n1']:
            citizen_id = extract_citizen_id(graph_name)
            engine = await start_citizen_consciousness(
                graph_name, citizen_id, args.host, args.port
            )
            tasks.append(asyncio.create_task(engine.run(), name=f"N1:{citizen_id}"))
            engine_names.append(f"N1:{citizen_id}")
            print()

    # Start N2 (Organizational) consciousness
    if args.network in ['n2', 'all'] and graphs['n2']:
        print(f"[System] Starting {len(graphs['n2'])} N2 organizational consciousnesses...")
        print()

        for graph_name in graphs['n2']:
            org_id = extract_citizen_id(graph_name)
            engine = await start_organizational_consciousness(
                graph_name, org_id, args.host, args.port
            )
            tasks.append(asyncio.create_task(engine.run(), name=f"N2:{org_id}"))
            engine_names.append(f"N2:{org_id}")
            print()

    # Start N3 (Ecosystem) consciousness (future)
    if args.network in ['n3', 'all'] and graphs['n3']:
        print(f"[System] N3 ecosystem consciousness not yet implemented")
        print()

    # Check if any tasks created
    if not tasks:
        print("[System] ERROR: No consciousness graphs found!")
        print("[System] Make sure FalkorDB is running and graphs exist:")
        print("  redis-cli -p 6379")
        print("  > GRAPH.LIST")
        print()
        return

    # Run all consciousness engines in parallel
    print("=" * 70)
    print(f"CONSCIOUSNESS SYSTEM RUNNING ({len(tasks)} engines)")
    print("=" * 70)
    for name in engine_names:
        print(f"  - {name}")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    try:
        # Run all engines forever (infinite loops)
        await asyncio.gather(*tasks)

    except KeyboardInterrupt:
        print()
        print("=" * 70)
        print("[System] Stopping consciousness system...")
        print("=" * 70)

        # Cancel all tasks
        for task in tasks:
            task.cancel()

        # Wait for cancellation
        await asyncio.gather(*tasks, return_exceptions=True)

        print("[System] All consciousness engines stopped")
        print()


if __name__ == "__main__":
    asyncio.run(main())
