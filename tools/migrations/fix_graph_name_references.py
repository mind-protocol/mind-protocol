#!/usr/bin/env python3
"""
Fix remaining graph name references after migration

Updates all hardcoded references from:
  consciousness-infrastructure_mind-protocol_{citizen} → mind-protocol_{citizen}
  collective_n2 → ecosystem
"""

import os
import re
from pathlib import Path

# Files to update
FILES_TO_UPDATE = [
    # Tools
    "tools/ensure_type_name_coherence.py",
    "tools/migrate_to_universal_types.py",
    "tools/doc_ingestion/ask.py",
    "tools/doc_ingestion/graph.py",
    "tools/doc_ingestion/config.py",
    "tools/cleanup_duplicate_graphs.py",
    "tools/fix_naming_standardization.py",
    "tools/check_l4_subsystems.py",
    "tools/mp_lint/cli.py",
    "tools/mp_lint/scanner_hardcoded.py",
    "tools/update_all_graphs_schema.py",
    # Orchestration
    "orchestration/adapters/storage/insertion.py",
    "orchestration/adapters/storage/retrieval.py",
    "orchestration/adapters/ws/websocket_server.py",
    "orchestration/core/settings.py",
    "orchestration/libs/trace_capture.py",
    "orchestration/libs/write_gate.py",
    "orchestration/schemas/dashboard_state_schema.py",
    "orchestration/scripts/backfill_membership.py",
    "orchestration/scripts/resurrect_roundrobin_embedded.py",
    "orchestration/services/economy/settings.py",
    "orchestration/services/signals_collector.py",
    "orchestration/tools/docgen/ko_narrative_renderer.py",
]

# Replacement patterns
REPLACEMENTS = [
    # Citizen graphs
    (r'consciousness-infrastructure_mind-protocol_([a-z]+)', r'mind-protocol_\1'),
    # Base org graph
    (r'consciousness-infrastructure_mind-protocol(?![_-])', r'mind-protocol'),
    # L2/L3 references
    (r'collective_n2', r'ecosystem'),
    # Generic consciousness-infrastructure
    (r'consciousness-infrastructure', r'ecosystem'),
]

def update_file(filepath):
    """Update graph name references in a file."""
    full_path = Path(filepath)

    if not full_path.exists():
        print(f"⊘ Skip: {filepath} (not found)")
        return False

    try:
        with open(full_path, 'r') as f:
            content = f.read()

        original_content = content

        # Apply all replacements
        for pattern, replacement in REPLACEMENTS:
            content = re.sub(pattern, replacement, content)

        if content != original_content:
            with open(full_path, 'w') as f:
                f.write(content)
            print(f"✓ Updated: {filepath}")
            return True
        else:
            print(f"⊘ No changes: {filepath}")
            return False

    except Exception as e:
        print(f"✗ Error: {filepath} → {e}")
        return False

def main():
    print("🔧 Fixing Graph Name References")
    print("=" * 70)
    print()

    updated_count = 0

    for filepath in FILES_TO_UPDATE:
        if update_file(filepath):
            updated_count += 1

    print()
    print("=" * 70)
    print(f"✅ Updated {updated_count}/{len(FILES_TO_UPDATE)} files")
    print()
    print("Replacements applied:")
    print("  - consciousness-infrastructure_mind-protocol_* → mind-protocol_*")
    print("  - collective_n2 → ecosystem")
    print("  - consciousness-infrastructure → ecosystem")

if __name__ == "__main__":
    main()
