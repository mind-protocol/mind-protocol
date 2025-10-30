#!/usr/bin/env python3
"""
Batch update imports to new orchestration structure.

Usage: python scripts/fix_imports.py

Author: Ada (Architect)
Created: 2025-10-22
"""

import re
from pathlib import Path
from typing import List, Tuple

# Define replacements (pattern, replacement)
REPLACEMENTS: List[Tuple[str, str]] = [
    # Storage adapters
    (r'from orchestration\.retrieval import', 'from orchestration.adapters.storage.retrieval import'),
    (r'from orchestration\.insertion import', 'from orchestration.adapters.storage.insertion import'),
    (r'from orchestration\.extraction import', 'from orchestration.adapters.storage.extraction import'),
    (r'from orchestration\.engine_registry import', 'from orchestration.adapters.storage.engine_registry import'),

    # Search adapters
    (r'from orchestration\.embedding_service import', 'from orchestration.adapters.search.embedding_service import'),
    (r'from orchestration\.semantic_search import', 'from orchestration.adapters.search.semantic_search import'),

    # WebSocket adapters
    (r'from orchestration\.traversal_event_emitter import', 'from orchestration.adapters.ws.traversal_event_emitter import'),
    (r'from orchestration\.control_api import', 'from orchestration.adapters.api.control_api import'),
    (r'from orchestration\.websocket_server import', 'from orchestration.adapters.ws.websocket_server import'),

    # Libs
    (r'from orchestration\.custom_claude_llm import', 'from orchestration.libs.custom_claude_llm import'),
    (r'from orchestration\.dynamic_prompt_generator import', 'from orchestration.libs.dynamic_prompt_generator import'),
    (r'from orchestration\.trace_parser import', 'from orchestration.libs.trace_parser import'),
    (r'from orchestration\.trace_capture import', 'from orchestration.libs.trace_capture import'),
    (r'from orchestration\.utils\.falkordb_adapter import', 'from orchestration.libs.utils.falkordb_adapter import'),

    # Mechanisms
    (r'from orchestration\.consciousness_engine_v2 import', 'from orchestration.mechanisms.consciousness_engine_v2 import'),

    # Observability (moved from orchestration/orchestration/ to libs/)
    (r'from orchestration\.orchestration\.metrics import', 'from orchestration.libs.metrics import'),
    (r'from orchestration\.orchestration\.websocket_broadcast import', 'from orchestration.libs.websocket_broadcast import'),
]


def fix_file(file_path: Path) -> Tuple[int, List[str]]:
    """
    Fix imports in a single file.

    Returns:
        (replacements_made, list_of_changes)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        print(f"  ❌ Error reading {file_path.name}: {e}")
        return 0, []

    original_content = content
    replacements_made = 0
    changes = []

    for pattern, replacement in REPLACEMENTS:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            change_msg = f"{pattern} → {replacement} ({count}x)"
            changes.append(change_msg)
            replacements_made += count
            content = new_content

    if content != original_content:
        try:
            file_path.write_text(content, encoding='utf-8')
        except Exception as e:
            print(f"  ❌ Error writing {file_path.name}: {e}")
            return 0, []

    return replacements_made, changes


def main():
    """Fix all Python files in orchestration/."""
    orchestration_dir = Path(__file__).parent.parent
    print(f"Scanning: {orchestration_dir}")
    print("-" * 80)

    total_replacements = 0
    files_modified = 0

    # Find all Python files
    py_files = sorted(orchestration_dir.rglob("*.py"))

    for py_file in py_files:
        # Skip __pycache__ and this script
        if "__pycache__" in str(py_file) or py_file.name == "fix_imports.py":
            continue

        replacements, changes = fix_file(py_file)

        if replacements > 0:
            files_modified += 1
            total_replacements += replacements
            relative_path = py_file.relative_to(orchestration_dir)
            print(f"\n✓ {relative_path} ({replacements} changes)")
            for change in changes:
                print(f"  - {change}")

    print("\n" + "=" * 80)
    print(f"✓ Fixed {total_replacements} imports across {files_modified} files")
    print("=" * 80)

    if files_modified == 0:
        print("\n✓ No files needed updating - imports already correct!")


if __name__ == "__main__":
    main()
