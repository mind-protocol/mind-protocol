"""
Test script to ingest N2 collective seed data into FalkorDB.

This script tests the full Write Flux with the actual N2 collective graph seed.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration.insertion import ingest_text

# Read N2 seed data
seed_file = project_root / "data" / "n2_collective_graph_seed.md"
print(f"Reading seed data from: {seed_file}")

with open(seed_file, 'r', encoding='latin-1') as f:
    seed_text = f.read()

print(f"Seed data length: {len(seed_text)} chars")
print("=" * 60)

# Ingest into collective_n2 graph
result = ingest_text(
    text=seed_text,
    graph_name="collective_n2",
    claude_working_dir=str(project_root)
)

# Display results
print("\n" + "=" * 60)
print(f"[RESULT] Status: {result['status']}")
print(f"[RESULT] Nodes: {result['nodes_created']}")
print(f"[RESULT] Relations: {result['relations_created']}")
if result['errors']:
    print(f"[RESULT] Errors: {len(result['errors'])}")
    print("\nFirst 5 errors:")
    for error in result['errors'][:5]:
        print(f"  - {error}")
print("=" * 60)
