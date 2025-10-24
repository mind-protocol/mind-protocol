"""
Diagnostic script to trace entity loading through the actual engine initialization path.

Author: Felix
Date: 2025-10-24
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose():
    """Test entity loading through actual initialization path."""

    from llama_index.graph_stores.falkordb import FalkorDBGraphStore
    from orchestration.libs.utils.falkordb_adapter import FalkorDBAdapter

    citizen_id = "felix"
    graph_name = f"citizen_{citizen_id}"

    logger.info(f"=== DIAGNOSING ENTITY LOADING FOR {graph_name} ===")

    # Step 1: Create adapter (same as websocket_server.py)
    logger.info("\nStep 1: Creating FalkorDB adapter...")
    graph_store = FalkorDBGraphStore(
        database=graph_name,
        url="redis://localhost:6379"
    )
    adapter = FalkorDBAdapter(graph_store)
    logger.info(f"✅ Adapter created")

    # Step 2: Load graph (this should use our fixed load_graph())
    logger.info("\nStep 2: Loading graph from FalkorDB...")
    try:
        graph = adapter.load_graph(graph_name)
        logger.info(f"✅ Graph loaded")
    except Exception as e:
        logger.error(f"❌ Graph loading failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Step 3: Check what was loaded
    logger.info("\nStep 3: Checking loaded data...")
    logger.info(f"  Nodes: {len(graph.nodes)}")
    logger.info(f"  Links: {len(graph.links)}")
    logger.info(f"  Subentities: {len(graph.subentities) if graph.subentities else 0}")

    if graph.subentities:
        logger.info(f"\n✅ SUCCESS - Loaded {len(graph.subentities)} entities:")
        for entity_id, entity in graph.subentities.items():
            logger.info(f"    - {entity_id}")
    else:
        logger.error("\n❌ FAILURE - No entities loaded into graph.subentities!")
        logger.error("  This means either:")
        logger.error("  1. Query returned no results")
        logger.error("  2. Deserialization failed for all entities")
        logger.error("  3. graph.add_entity() didn't populate graph.subentities")

    # Step 4: Check bootstrap condition
    logger.info("\nStep 4: Checking bootstrap condition...")
    current_entity_count = len(graph.subentities) if graph.subentities else 0
    expected_entity_count = 8

    if not graph.subentities or current_entity_count < expected_entity_count:
        logger.warning(f"⚠️  Bootstrap condition would trigger:")
        logger.warning(f"    Current: {current_entity_count}, Expected: {expected_entity_count}")
        logger.warning(f"    This would CLEAR entities and recreate them!")
    else:
        logger.info(f"✅ Bootstrap condition would NOT trigger")
        logger.info(f"    Current: {current_entity_count}, Expected: {expected_entity_count}")

if __name__ == '__main__':
    diagnose()
