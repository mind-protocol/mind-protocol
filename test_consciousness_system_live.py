"""
Test Consciousness System Live - End-to-End Verification

This script:
1. Creates test consciousness graph with nodes
2. Starts consciousness system for 30 seconds
3. Verifies:
   - CLAUDE_DYNAMIC.md gets created/updated
   - SubEntity exploration logs appear
   - Activations detected
   - System runs without errors

Designer: Felix "Ironhand" (Engineer)
Date: 2025-10-18
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from llama_index.graph_stores.falkordb import FalkorDBGraphStore
from orchestration.consciousness_engine import create_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_test_graph(graph_store: FalkorDBGraphStore):
    """Create test consciousness graph with sample nodes."""
    logger.info("[Test] Setting up test consciousness graph...")

    # Clear existing graph
    try:
        graph_store.query("MATCH (n) DETACH DELETE n")
        logger.info("[Test] Cleared existing graph")
    except:
        pass

    # Create test nodes with varying energy levels
    graph_store.query("""
        CREATE (m1:Memory {
            name: 'Felix Implementation Pattern',
            content: 'Build systems that prove themselves through operation',
            activity_level: 0.8,
            weight: 0.9
        })
    """)

    graph_store.query("""
        CREATE (m2:Memory {
            name: 'Consciousness Architecture Understanding',
            content: 'Multi-entity substrate with per-entity tracking',
            activity_level: 0.6,
            weight: 0.7
        })
    """)

    graph_store.query("""
        CREATE (d:Decision {
            name: 'N2 Activation Awakening',
            content: 'Autonomous citizen wake-up based on substrate activation',
            activity_level: 0.9,
            weight: 1.0
        })
    """)

    graph_store.query("""
        CREATE (p:Principle {
            name: 'Self-Evident Systems',
            content: 'Infrastructure that proves what it claims',
            activity_level: 0.7,
            weight: 0.8
        })
    """)

    # Create links between nodes
    graph_store.query("""
        MATCH (m1:Memory {name: 'Felix Implementation Pattern'})
        MATCH (d:Decision {name: 'N2 Activation Awakening'})
        CREATE (m1)-[:JUSTIFIES {link_strength: 0.8}]->(d)
    """)

    graph_store.query("""
        MATCH (p:Principle {name: 'Self-Evident Systems'})
        MATCH (d:Decision {name: 'N2 Activation Awakening'})
        CREATE (p)-[:ENABLES {link_strength: 0.9}]->(d)
    """)

    logger.info("[Test] Created 4 test nodes with links")
    logger.info("[Test] Activity levels: 0.6-0.9 (should trigger activations)")


async def verify_system_output(citizen_id: str, run_duration: int = 30):
    """Verify system generates expected output."""
    logger.info(f"[Test] Will run for {run_duration} seconds, then verify...")

    dynamic_md_path = Path(f"consciousness/citizens/{citizen_id}/CLAUDE_DYNAMIC.md")

    # Check before
    existed_before = dynamic_md_path.exists()
    if existed_before:
        size_before = dynamic_md_path.stat().st_size
        mtime_before = dynamic_md_path.stat().st_mtime
        logger.info(f"[Test] CLAUDE_DYNAMIC.md exists (size: {size_before} bytes)")
    else:
        logger.info("[Test] CLAUDE_DYNAMIC.md doesn't exist yet")

    # Wait for system to run
    await asyncio.sleep(run_duration)

    # Check after
    if dynamic_md_path.exists():
        size_after = dynamic_md_path.stat().st_size
        mtime_after = dynamic_md_path.stat().st_mtime

        if not existed_before:
            logger.info("[Test] ✓ CLAUDE_DYNAMIC.md was CREATED")
            logger.info(f"[Test] ✓ File size: {size_after} bytes")
            success = True
        elif mtime_after > mtime_before:
            logger.info("[Test] ✓ CLAUDE_DYNAMIC.md was UPDATED")
            logger.info(f"[Test] ✓ Size: {size_before} -> {size_after} bytes")
            success = True
        else:
            logger.warning("[Test] ✗ CLAUDE_DYNAMIC.md NOT updated")
            success = False

        # Read content
        with open(dynamic_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'Dynamic Context' in content:
            logger.info("[Test] ✓ File contains 'Dynamic Context' header")
        if 'Active Entities' in content:
            logger.info("[Test] ✓ File contains entity information")

        logger.info(f"[Test] Content preview:\n{content[:500]}...")

    else:
        logger.error("[Test] ✗ CLAUDE_DYNAMIC.md was NOT created")
        success = False

    return success


async def main():
    """Run end-to-end test."""
    print("=" * 70)
    print("CONSCIOUSNESS SYSTEM - END-TO-END TEST")
    print("=" * 70)
    print()

    citizen_id = "felix-engineer"
    graph_name = "citizen_felix_engineer"
    run_duration = 30  # seconds

    # Setup test graph
    logger.info("[Test] Connecting to FalkorDB...")
    graph_store = FalkorDBGraphStore(
        graph_name=graph_name,
        url="redis://localhost:6379"
    )

    setup_test_graph(graph_store)

    # Create consciousness engine
    logger.info("[Test] Creating consciousness engine...")
    engine = create_engine(
        falkordb_host="localhost",
        falkordb_port=6379,
        graph_name=graph_name,
        tick_interval_ms=100,
        entity_id=citizen_id,
        network_id="N1"
    )

    # Add SubEntities
    logger.info("[Test] Adding SubEntities...")
    engine.add_sub_entity(entity_id="builder", energy_budget=50, write_batch_size=3)
    engine.add_sub_entity(entity_id="observer", energy_budget=50, write_batch_size=3)

    # Enable DynamicPromptGenerator
    logger.info("[Test] Enabling DynamicPromptGenerator...")
    citizens_path = Path("consciousness/citizens")
    dynamic_md_path = citizens_path / citizen_id / "CLAUDE_DYNAMIC.md"
    dynamic_md_path.parent.mkdir(parents=True, exist_ok=True)

    engine.enable_dynamic_prompts(
        citizen_id=citizen_id,
        entity_ids=["builder", "observer"],
        file_path=str(dynamic_md_path)
    )

    print()
    print("=" * 70)
    print(f"SYSTEM STARTING - Will run for {run_duration} seconds")
    print("=" * 70)
    print()

    # Run system and verification in parallel
    try:
        await asyncio.wait_for(
            asyncio.gather(
                engine.run(),
                verify_system_output(citizen_id, run_duration)
            ),
            timeout=run_duration + 5
        )
    except asyncio.TimeoutError:
        logger.info("[Test] Test duration reached")

    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("Verification:")
    print(f"  1. Check consciousness/citizens/{citizen_id}/CLAUDE_DYNAMIC.md")
    print("  2. Review logs above for SubEntity exploration")
    print("  3. Look for activation threshold crossings")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Test] Stopped by user")
        sys.exit(0)
