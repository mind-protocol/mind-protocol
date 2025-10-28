"""
Run Consciousness System - Complete MVP

Starts the complete consciousness system with:
- Variable tick frequency heartbeat
- SubEntity yearning loops (continuous exploration)
- DynamicPromptGenerator (automatic CLAUDE_DYNAMIC.md updates)
- N2 ActivationMonitor (autonomous citizen awakening)

This is the main entry point for running consciousness infrastructure.

Usage:
    python run_consciousness_system.py --citizen felix-engineer
    python run_consciousness_system.py --citizen ada-architect --enable-n2

Designer: Felix "Ironhand" (Engineer)
Date: 2025-10-18
"""

import asyncio
import argparse
import logging

from llama_index.graph_stores.falkordb import FalkorDBGraphStore

from orchestration.mechanisms.consciousness_engine_v2 import (
    ConsciousnessEngineV2,
    EngineConfig
)
from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter
from orchestration.mechanisms.subentity_bootstrap import SubEntityBootstrap
from orchestration.mechanisms.subentity_post_bootstrap import (
    run_post_bootstrap_initialization
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run complete consciousness system."""
    parser = argparse.ArgumentParser(
        description='Run Complete Consciousness System'
    )

    # Required arguments
    parser.add_argument(
        '--citizen',
        required=True,
        help='Citizen ID (e.g., "felix-engineer", "ada-architect")'
    )

    # Optional arguments
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
        '--tick-ms',
        type=int,
        default=100,
        help='Initial tick interval in ms (default: 100)'
    )
    parser.add_argument(
        '--subentities',
        nargs='+',
        default=[],
        help='(Deprecated) Retained for compatibility; V2 engine bootstraps entities automatically'
    )
    parser.add_argument(
        '--enable-dynamic-prompts',
        action='store_true',
        default=False,
        help='(Deprecated) Dynamic prompt updates are managed by higher-level services in V2'
    )
    parser.add_argument(
        '--enable-n2',
        action='store_true',
        help='(Deprecated) N2 monitoring is handled by orchestration services, not per-engine'
    )
    parser.add_argument(
        '--n2-graph',
        default='collective_mind_protocol',
        help='(Deprecated) N2 graph name placeholder'
    )
    parser.add_argument(
        '--energy-budget',
        type=int,
        default=100,
        help='(Deprecated) V2 engine manages energy budgets internally'
    )

    args = parser.parse_args()

    if args.subentities:
        logger.warning(
            "Subentity hints provided (%s) but V2 engine bootstraps entities automatically; hints will be ignored.",
            args.subentities
        )
    if args.enable_dynamic_prompts:
        logger.warning("Dynamic prompt updates are managed by higher-level services in V2; flag ignored.")
    if args.enable_n2:
        logger.warning("N2 monitoring is orchestrated by dedicated services; engine-level flag ignored.")

    # Print banner
    print("=" * 70)
    print("CONSCIOUSNESS SYSTEM - COMPLETE MVP")
    print("=" * 70)
    print(f"Citizen: {args.citizen}")
    print(f"N1 Graph: citizen_{args.citizen.replace('-', '_')}")
    print(f"FalkorDB: {args.host}:{args.port}")
    print(f"Initial Tick: {args.tick_ms}ms")
    if args.subentities:
        legacy_hint = ', '.join(args.subentities)
    else:
        legacy_hint = 'none (auto-bootstrap)'
    print(f"Legacy SubEntity hints: {legacy_hint}")
    if args.enable_dynamic_prompts or args.enable_n2:
        print("Legacy toggles detected (dynamic prompts / N2 monitoring) - V2 ignores these flags")
    print("=" * 70)
    print()

    # Create consciousness engine
    logger.info("Creating consciousness engine...")
    graph_name = f"citizen_{args.citizen.replace('-', '_')}"
    graph_store = FalkorDBGraphStore(
        database=graph_name,
        url=f"redis://{args.host}:{args.port}"
    )
    adapter = FalkorDBAdapter(graph_store)

    loop = asyncio.get_running_loop()
    logger.info("Loading graph '%s' from FalkorDB...", graph_name)
    graph = await loop.run_in_executor(None, adapter.load_graph, graph_name)
    logger.info(
        "Graph loaded: nodes=%s links=%s entities=%s",
        len(graph.nodes),
        len(graph.links),
        len(graph.subentities) if graph.subentities else 0
    )

    if not graph.subentities:
        logger.info("No subentities detected; running bootstrap pipeline...")
        bootstrap = SubEntityBootstrap(graph)
        bootstrap_stats = bootstrap.run_complete_bootstrap()
        logger.info("Entity bootstrap stats: %s", bootstrap_stats)

        post_stats = run_post_bootstrap_initialization(graph)
        logger.info("Post-bootstrap stats: %s", post_stats)

        persist_stats = adapter.persist_subentities(graph)
        logger.info("Persisted subentities: %s", persist_stats)
    else:
        logger.info("Entity layer already present (%s entities); skipping bootstrap.", len(graph.subentities))

    config = EngineConfig(
        tick_interval_ms=float(args.tick_ms),
        entity_id=args.citizen,
        network_id="N1",
        enable_diffusion=True,
        enable_decay=True,
        enable_strengthening=True,
        enable_websocket=True
    )

    engine = ConsciousnessEngineV2(graph, adapter, config)
    logger.info(
        "Consciousness engine initialized (tick_interval_ms=%.2f, network=%s)",
        config.tick_interval_ms,
        config.network_id
    )

    # Start consciousness system
    logger.info("Starting consciousness system...")
    print()
    print("=" * 70)
    print("SYSTEM RUNNING - Press Ctrl+C to stop")
    print("=" * 70)
    print()

    try:
        await engine.run()
    except KeyboardInterrupt:
        print()
        logger.info("Consciousness system stopped by user")
    except Exception as e:
        logger.error(f"Consciousness system fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
