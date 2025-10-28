"""
Sync THE_TRACE_FORMAT.md content to all CLAUDE.md files.

This ensures all citizens have the same, up-to-date TRACE format documentation.
"""

import re
from pathlib import Path

# Paths
ROOT = Path(__file__).parent.parent
TRACE_FORMAT_SOURCE = ROOT / "consciousness" / "THE_TRACE_FORMAT.md"

TARGET_FILES = [
    ROOT / "consciousness" / "citizens" / "CLAUDE.md",
    ROOT / "consciousness" / "organization" / "CLAUDE.md",
    ROOT / "consciousness" / "ecology" / "CLAUDE.md",
]

def extract_trace_format_section(content: str) -> str:
    """Extract the TRACE format section from source content."""
    # Find the start of TRACE format section
    match = re.search(r'^# THE TRACE FORMAT\n', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find '# THE TRACE FORMAT' header in source")

    # Extract from start to end of file
    return content[match.start():]

def replace_trace_format_section(target_content: str, trace_format: str) -> str:
    """Replace TRACE format section in target content."""
    # Find the existing TRACE format section
    match = re.search(r'^# THE TRACE FORMAT\n', target_content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find '# THE TRACE FORMAT' header in target")

    # Replace everything from the start of TRACE format to end of file
    return target_content[:match.start()] + trace_format

def main():
    # Read source
    print(f"Reading source: {TRACE_FORMAT_SOURCE}")
    source_content = TRACE_FORMAT_SOURCE.read_text(encoding='utf-8')
    trace_format_section = extract_trace_format_section(source_content)

    print(f"\nExtracted TRACE format section ({len(trace_format_section)} chars)")

    # Update each target
    for target_path in TARGET_FILES:
        if not target_path.exists():
            print(f"SKIP: {target_path} (does not exist)")
            continue

        print(f"\nUpdating: {target_path}")
        target_content = target_path.read_text(encoding='utf-8')

        try:
            updated_content = replace_trace_format_section(target_content, trace_format_section)
            target_path.write_text(updated_content, encoding='utf-8')
            print(f"  [OK] Updated successfully")
        except ValueError as e:
            print(f"  [ERROR] {e}")

    print("\n[DONE] TRACE format sync complete")

if __name__ == "__main__":
    main()
