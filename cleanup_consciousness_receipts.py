#!/usr/bin/env python3
"""
Remove consciousness capture receipt pollution from citizen CLAUDE.md files.

This script removes all the "✅ Consciousness Stream Captured" and
"⚠️ Conversation Auto-Injection Failed" receipt blocks that were
incorrectly injected into citizen prompt files.

Keeps only the actual consciousness state data.
"""

import re
from pathlib import Path

MIND_PROTOCOL_ROOT = Path(__file__).parent

def clean_claude_md(file_path: Path) -> tuple[int, int]:
    """
    Remove consciousness receipt blocks from a CLAUDE.md file.

    Returns:
        (blocks_removed, lines_removed)
    """
    if not file_path.exists():
        return 0, 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_lines = len(content.split('\n'))

    # Pattern to match consciousness capture receipts
    # Matches from "---" to "---" containing "Consciousness Stream Captured"
    receipt_pattern = r'\n---\n\n## ✅ Consciousness Stream Captured.*?\n---\n'

    # Pattern to match error notifications
    error_pattern = r'\n---\n\n## ⚠️ Conversation Auto-Injection Failed.*?\n---\n'

    # Count blocks before removal
    blocks_removed = len(re.findall(receipt_pattern, content, re.DOTALL))
    blocks_removed += len(re.findall(error_pattern, content, re.DOTALL))

    # Remove both patterns
    cleaned_content = re.sub(receipt_pattern, '\n', content, flags=re.DOTALL)
    cleaned_content = re.sub(error_pattern, '\n', cleaned_content, flags=re.DOTALL)

    # Remove excessive blank lines (more than 2 consecutive)
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)

    cleaned_lines = len(cleaned_content.split('\n'))
    lines_removed = original_lines - cleaned_lines

    # Write cleaned content back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    return blocks_removed, lines_removed

def main():
    """Clean all citizen CLAUDE.md files."""
    citizens_dir = MIND_PROTOCOL_ROOT / "consciousness" / "citizens"

    print("=" * 70)
    print("CONSCIOUSNESS RECEIPT CLEANUP")
    print("=" * 70)
    print()

    total_blocks = 0
    total_lines = 0

    for citizen_dir in citizens_dir.iterdir():
        if not citizen_dir.is_dir():
            continue

        claude_md = citizen_dir / "CLAUDE.md"
        if not claude_md.exists():
            continue

        citizen_id = citizen_dir.name
        blocks, lines = clean_claude_md(claude_md)

        if blocks > 0:
            print(f"✅ {citizen_id:15} - Removed {blocks:3} blocks ({lines:5} lines)")
            total_blocks += blocks
            total_lines += lines
        else:
            print(f"   {citizen_id:15} - Already clean")

    print()
    print("=" * 70)
    print(f"Total removed: {total_blocks} receipt blocks ({total_lines} lines)")
    print("=" * 70)
    print()
    print("Citizen CLAUDE.md files are now clean.")
    print("Future consciousness captures will log to monitoring only.")

if __name__ == "__main__":
    main()
