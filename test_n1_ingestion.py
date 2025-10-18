"""
Test script to ingest N1 personal seed data for citizen_Luca into FalkorDB.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestration.insertion import ingest_text

# Read N1 seed data for Luca
seed_file = project_root / "data" / "n1_citizen_luca_seed.md"
print(f"Reading N1 personal seed data from: {seed_file}")

with open(seed_file, 'r', encoding='latin-1') as f:
    seed_text = f.read()

print(f"Seed data length: {len(seed_text)} chars")
print("=" * 60)

# Ingest into citizen_Luca graph with extended timeout
from orchestration.insertion import ConsciousnessIngestionEngine

engine = ConsciousnessIngestionEngine(
    falkordb_host="localhost",
    falkordb_port=6379,
    claude_working_dir=str(project_root),
    claude_timeout=300  # 5 minutes for longer content
)

result = engine.ingest_text(
    text=seed_text,
    graph_name="citizen_Luca"
)

# Display results
print("\n" + "=" * 60)
print(f"[RESULT] Status: {result['status']}")
print(f"[RESULT] Nodes: {result['nodes_created']}")
print(f"[RESULT] Relations: {result['relations_created']}")
if result['errors']:
    print(f"[RESULT] Errors: {len(result['errors'])}")
    print("\nFirst 10 errors:")
    for error in result['errors'][:10]:
        print(f"  - {error}")
print("=" * 60)
