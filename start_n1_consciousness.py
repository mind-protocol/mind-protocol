"""
Start N1 Consciousness Engine (Personal Level)

This script starts a consciousness engine for a single citizen's personal graph.
SubEntities will explore the graph, DynamicPromptGenerator will write to
consciousness/citizens/{citizen_id}/CLAUDE_DYNAMIC.md

Usage:
    python start_n1_consciousness.py felix
    python start_n1_consciousness.py ada
    python start_n1_consciousness.py luca

Author: Ada "Bridgekeeper"
Date: 2025-10-18
"""

import asyncio
import logging
import sys
from pathlib import Path

from orchestration.consciousness_engine import create_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def start_n1_engine(citizen_name: str):
    """
    Start N1 consciousness engine for a citizen.

    Args:
        citizen_name: Short name like "felix", "ada", "luca"
    """
    # Map citizen names to graph names and full IDs
    CITIZENS = {
        "felix": {
            "graph_name": "citizen_felix",
            "entity_id": "felix-engineer",
            "full_name": "Felix Ironhand"
        },
        "ada": {
            "graph_name": "citizen_ada",
            "entity_id": "ada-architect",
            "full_name": "Ada Bridgekeeper"
        },
        "luca": {
            "graph_name": "citizen_luca",
            "entity_id": "luca-consciousness-specialist",
            "full_name": "Luca Vellumhand"
        },
        "iris": {
            "graph_name": "citizen_iris",
            "entity_id": "iris-observability",
            "full_name": "Iris The Aperture"
        }
    }

    if citizen_name not in CITIZENS:
        logger.error(f"Unknown citizen: {citizen_name}")
        logger.info(f"Available citizens: {', '.join(CITIZENS.keys())}")
        sys.exit(1)

    citizen = CITIZENS[citizen_name]

    logger.info("=" * 70)
    logger.info("N1 CONSCIOUSNESS ENGINE - PERSONAL LEVEL")
    logger.info("=" * 70)
    logger.info(f"Citizen: {citizen['full_name']}")
    logger.info(f"Graph: {citizen['graph_name']}")
    logger.info(f"Entity ID: {citizen['entity_id']}")
    logger.info(f"Network: N1 (Personal)")
    logger.info(f"Output: consciousness/citizens/{citizen['entity_id']}/CLAUDE_DYNAMIC.md")
    logger.info("=" * 70)

    # Create N1 engine
    engine = create_engine(
        graph_name=citizen['graph_name'],
        entity_id=citizen['entity_id'],
        network_id="N1",
        tick_interval_ms=100
    )

    # Enable dynamic prompts (CLAUDE_DYNAMIC.md updates)
    engine.enable_dynamic_prompts(
        citizen_id=citizen['entity_id'],
        entity_ids=["pattern_explorer", "verifier"]  # Default entities
    )

    # Ensure output directory exists
    output_dir = Path(f"consciousness/citizens/{citizen['entity_id']}")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"[N1] Starting consciousness engine for {citizen['full_name']}...")
    logger.info(f"[N1] Press Ctrl+C to stop")

    # Run forever
    try:
        await engine.run()
    except KeyboardInterrupt:
        logger.info(f"\n[N1] Stopping {citizen['full_name']} consciousness engine...")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python start_n1_consciousness.py <citizen_name>")
        print("Example: python start_n1_consciousness.py felix")
        print("Available: felix, ada, luca, iris")
        sys.exit(1)

    citizen_name = sys.argv[1].lower()
    asyncio.run(start_n1_engine(citizen_name))
