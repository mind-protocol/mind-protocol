"""
Clean up CLAUDE.md files polluted with processing statistics blocks.

The conversation_watcher was appending processing stats to CLAUDE.md files,
which should only contain citizen identity information.

This script removes all "Consciousness Stream Captured" blocks.

Author: Felix (cleaning up the mess)
Date: 2025-10-19
"""

import re
from pathlib import Path

# Find all CLAUDE.md files in consciousness/citizens/
mind_protocol_root = Path(__file__).parent
citizens_dir = mind_protocol_root / "consciousness" / "citizens"

# Pattern to match the pollution blocks
# Matches from "---" through "## ✅ Consciousness Stream Captured" to the closing "---"
pollution_pattern = re.compile(
    r'\n---\n\n## ✅ Consciousness Stream Captured \([^)]+\)\n\n'
    r'\*\*TRACE Format Processing:\*\*\n'
    r'(?:- [^\n]+\n)+'
    r'\n'
    r'\*\*Dual Learning Mode:\*\*\n'
    r'(?:- [^\n]+\n)+'
    r'\n'
    r'\[✅ Graph updated - learning continues\]\n'
    r'\n---\n',
    re.MULTILINE
)

def clean_claude_file(file_path: Path) -> int:
    """
    Remove all pollution blocks from a CLAUDE.md file.

    Returns: Number of blocks removed
    """
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count matches before removing
        matches = pollution_pattern.findall(content)
        count = len(matches)

        if count == 0:
            print(f"[OK] {file_path.parent.name}/CLAUDE.md - Already clean")
            return 0

        # Remove all pollution blocks
        cleaned = pollution_pattern.sub('', content)

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned)

        print(f"[OK] {file_path.parent.name}/CLAUDE.md - Removed {count} pollution blocks")
        return count

    except Exception as e:
        print(f"[ERROR] {file_path.parent.name}/CLAUDE.md - Error: {e}")
        return 0

def main():
    print("\n=== CLAUDE.md Pollution Cleanup ===\n")
    print("Scanning for polluted CLAUDE.md files...\n")

    if not citizens_dir.exists():
        print(f"Error: Citizens directory not found: {citizens_dir}")
        return

    # Find all CLAUDE.md files
    claude_files = list(citizens_dir.glob("*/CLAUDE.md"))

    if not claude_files:
        print("No CLAUDE.md files found")
        return

    print(f"Found {len(claude_files)} CLAUDE.md files\n")

    # Clean each file
    total_removed = 0
    for claude_file in sorted(claude_files):
        removed = clean_claude_file(claude_file)
        total_removed += removed

    print(f"\n=== Cleanup Complete ===")
    print(f"Total pollution blocks removed: {total_removed}")
    print()

if __name__ == '__main__':
    main()
