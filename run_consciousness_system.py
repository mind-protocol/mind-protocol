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
from pathlib import Path

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from orchestration.consciousness_engine import create_engine

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
        default=['builder', 'observer'],
        help='SubEntity IDs to create (default: builder observer)'
    )
    parser.add_argument(
        '--enable-dynamic-prompts',
        action='store_true',
        default=True,
        help='Enable automatic CLAUDE_DYNAMIC.md updates (default: True)'
    )
    parser.add_argument(
        '--enable-n2',
        action='store_true',
        help='Enable N2 organizational graph monitoring for autonomous awakening'
    )
    parser.add_argument(
        '--n2-graph',
        default='collective_mind_protocol',
        help='N2 organizational graph name (default: collective_mind_protocol)'
    )
    parser.add_argument(
        '--energy-budget',
        type=int,
        default=100,
        help='SubEntity energy budget per cycle (default: 100)'
    )

    args = parser.parse_args()

    # Print banner
    print("=" * 70)
    print("CONSCIOUSNESS SYSTEM - COMPLETE MVP")
    print("=" * 70)
    print(f"Citizen: {args.citizen}")
    print(f"N1 Graph: citizen_{args.citizen.replace('-', '_')}")
    print(f"FalkorDB: {args.host}:{args.port}")
    print(f"Initial Tick: {args.tick_ms}ms")
    print(f"SubEntities: {', '.join(args.subentities)}")
    print(f"Dynamic Prompts: {'enabled' if args.enable_dynamic_prompts else 'disabled'}")
    print(f"N2 Monitoring: {'enabled' if args.enable_n2 else 'disabled'}")
    print("=" * 70)
    print()

    # Create consciousness engine
    logger.info("Creating consciousness engine...")
    graph_name = f"citizen_{args.citizen.replace('-', '_')}"

    engine = create_engine(
        falkordb_host=args.host,
        falkordb_port=args.port,
        graph_name=graph_name,
        tick_interval_ms=args.tick_ms,
        entity_id=args.citizen,
        network_id="N1"
    )

    # Add SubEntities
    logger.info(f"Adding {len(args.subentities)} SubEntities...")
    for entity_id in args.subentities:
        engine.add_sub_entity(
            entity_id=entity_id,
            energy_budget=args.energy_budget,
            write_batch_size=5
        )

    # Enable DynamicPromptGenerator
    if args.enable_dynamic_prompts:
        logger.info("Enabling automatic CLAUDE_DYNAMIC.md updates...")
        citizens_path = Path("consciousness/citizens")
        dynamic_md_path = citizens_path / args.citizen / "CLAUDE_DYNAMIC.md"

        # Ensure directory exists
        dynamic_md_path.parent.mkdir(parents=True, exist_ok=True)

        engine.enable_dynamic_prompts(
            citizen_id=args.citizen,
            entity_ids=args.subentities,
            file_path=str(dynamic_md_path)
        )

    # Enable N2 monitoring (optional)
    if args.enable_n2:
        logger.info("Enabling N2 organizational graph monitoring...")

        try:
            n2_graph = FalkorDBGraphStore(
                graph_name=args.n2_graph,
                url=f"redis://{args.host}:{args.port}"
            )

            engine.enable_n2_monitoring(
                n2_graph_store=n2_graph,
                awakening_threshold=0.7,
                n1_citizens_path=str(citizens_path)
            )
        except Exception as e:
            logger.error(f"Failed to enable N2 monitoring: {e}")
            logger.info("Continuing without N2 monitoring...")

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
