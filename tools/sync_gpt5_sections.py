"""
Sync GPT-5 Pro's Perspective Sections

Copies "GPT-5 Pro's Perspective" sections from conversations/ files
to corresponding discussions/active/ files.

Usage:
    python tools/sync_gpt5_sections.py

Author: Iris "The Aperture"
Created: 2025-10-19
"""

import re
from pathlib import Path
from typing import Optional


def extract_section(content: str, section_heading: str) -> Optional[str]:
    """
    Extract a markdown section by heading

    Args:
        content: Full markdown content
        section_heading: Heading to find (e.g., "### GPT-5 Pro's Perspective")

    Returns:
        Section content (including heading) or None if not found
    """
    # Escape special regex characters in heading
    escaped_heading = re.escape(section_heading)

    # Pattern: heading line + everything until next heading of same or higher level
    # Supports ### headings, finds everything until next ##, ###, or end of file
    pattern = rf'({escaped_heading}.*?)(?=\n##[^#]|\n###[^#]|\Z)'

    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1).rstrip()

    return None


def replace_section(content: str, section_heading: str, new_section: str) -> str:
    """
    Replace a markdown section with new content

    Args:
        content: Full markdown content
        section_heading: Heading to replace
        new_section: New section content (including heading)

    Returns:
        Updated content
    """
    # Escape special regex characters in heading
    escaped_heading = re.escape(section_heading)

    # Pattern: heading line + everything until next heading of same or higher level
    pattern = rf'{escaped_heading}.*?(?=\n##[^#]|\n###[^#]|\Z)'

    # Replace with new section, preserving surrounding content
    updated = re.sub(pattern, new_section, content, flags=re.DOTALL)

    return updated


def sync_file_pair(source_path: Path, target_path: Path, section_heading: str) -> bool:
    """
    Sync specific section from source to target file

    Args:
        source_path: Path to conversations/ file
        target_path: Path to discussions/active/ file
        section_heading: Section to sync

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read source file
        if not source_path.exists():
            print(f"  [!] Source not found: {source_path.name}")
            return False

        source_content = source_path.read_text(encoding='utf-8')

        # Extract section from source
        section_content = extract_section(source_content, section_heading)

        if not section_content:
            print(f"  [!] Section '{section_heading}' not found in source")
            return False

        # Read target file
        if not target_path.exists():
            print(f"  [!] Target not found: {target_path.name}")
            return False

        target_content = target_path.read_text(encoding='utf-8')

        # Check if target has the section
        if section_heading not in target_content:
            print(f"  [!] Section '{section_heading}' not found in target")
            return False

        # Replace section in target
        updated_content = replace_section(target_content, section_heading, section_content)

        # Write updated target
        target_path.write_text(updated_content, encoding='utf-8')

        return True

    except Exception as e:
        print(f"  [!] Error processing {source_path.name}: {e}")
        return False


def main():
    """Sync GPT-5 Pro's Perspective sections from conversations to discussions"""

    repo_root = Path(__file__).parent.parent
    conversations_dir = repo_root / "docs" / "specs" / "consciousness_engine_architecture" / "conversations"
    discussions_dir = repo_root / "docs" / "specs" / "consciousness_engine_architecture" / "discussions" / "active"

    # Files to sync (numbered 001-010)
    file_numbers = [
        "001_diffusion_numerical_stability",
        "002_link_creation_mechanism",
        "003_entity_emergence_threshold",
        "004_workspace_goal_circular_dependency",
        "005_link_weight_runaway_growth",
        "006_criticality_tuning_oscillation",
        "007_memory_consolidation",
        "008_tick_speed_temporal_aliasing",
        "009_fixed_workspace_capacity",
        "010_entity_competition_model",
    ]

    section_heading = "### GPT-5 Pro's Perspective"

    print("[*] Syncing GPT-5 Pro's Perspective sections...")
    print(f"[*] Source: {conversations_dir}")
    print(f"[*] Target: {discussions_dir}")
    print()

    successful = 0
    failed = 0

    for file_name in file_numbers:
        source_file = conversations_dir / f"{file_name}.md"
        target_file = discussions_dir / f"{file_name}.md"

        print(f"Processing: {file_name}.md...", end=" ")

        if sync_file_pair(source_file, target_file, section_heading):
            print("OK")
            successful += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"[+] Successfully synced: {successful} files")

    if failed > 0:
        print(f"[!] Failed: {failed} files")


if __name__ == "__main__":
    main()
