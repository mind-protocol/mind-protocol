#!/usr/bin/env python3
"""
Diff Normalizer - Generates structured diffs from file changes

Takes file change events and produces structured diffs with hunks
for code review pipeline.

Diff Format:
  {
    "files": [{
      "path": "...",
      "sha_before": "...",
      "sha_after": "...",
      "hunks": [{"start": 120, "end": 138, "add": "+ ...", "del": "- ..."}]
    }]
  }

Author: Atlas "Infrastructure Engineer"
Created: 2025-10-31
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md § 5.1, § 6.1
"""

import difflib
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Hunk:
    """Represents a continuous change hunk in a file."""
    start_line: int
    end_line: int
    additions: List[str] = field(default_factory=list)
    deletions: List[str] = field(default_factory=list)


@dataclass
class FileDiff:
    """Represents a complete file diff with all hunks."""
    path: str
    event_type: str  # "created", "modified", "deleted"
    sha_before: Optional[str] = None
    sha_after: Optional[str] = None
    hunks: List[Hunk] = field(default_factory=list)


def compute_file_hash(content: bytes) -> str:
    """Compute SHA256 hash of file content (first 16 chars)."""
    return hashlib.sha256(content).hexdigest()[:16]


def generate_diff(
    file_path: Path,
    event_type: str,
    old_content: Optional[bytes] = None,
    new_content: Optional[bytes] = None
) -> FileDiff:
    """
    Generate structured diff for a file change.

    Args:
        file_path: Path to the file
        event_type: "created", "modified", or "deleted"
        old_content: Previous file content (for modified/deleted)
        new_content: New file content (for created/modified)

    Returns:
        FileDiff with hunks showing changes
    """
    rel_path = str(file_path)

    # Compute hashes
    sha_before = compute_file_hash(old_content) if old_content else None
    sha_after = compute_file_hash(new_content) if new_content else None

    # Handle different event types
    if event_type == "created":
        return _generate_creation_diff(rel_path, sha_after, new_content)
    elif event_type == "deleted":
        return _generate_deletion_diff(rel_path, sha_before, old_content)
    elif event_type == "modified":
        return _generate_modification_diff(rel_path, sha_before, sha_after, old_content, new_content)
    else:
        # Unknown event type - return empty diff
        return FileDiff(
            path=rel_path,
            event_type=event_type,
            sha_before=sha_before,
            sha_after=sha_after,
            hunks=[]
        )


def _generate_creation_diff(path: str, sha_after: str, content: bytes) -> FileDiff:
    """Generate diff for newly created file (all additions)."""
    try:
        text = content.decode('utf-8')
        lines = text.splitlines()

        # Create single hunk with all additions
        hunk = Hunk(
            start_line=1,
            end_line=len(lines),
            additions=[f"+ {line}" for line in lines[:20]],  # First 20 lines
            deletions=[]
        )

        # Add truncation marker if file is longer
        if len(lines) > 20:
            hunk.additions.append(f"... ({len(lines) - 20} more lines)")

        return FileDiff(
            path=path,
            event_type="created",
            sha_before=None,
            sha_after=sha_after,
            hunks=[hunk]
        )
    except UnicodeDecodeError:
        # Binary file - no hunks
        return FileDiff(
            path=path,
            event_type="created",
            sha_before=None,
            sha_after=sha_after,
            hunks=[]
        )


def _generate_deletion_diff(path: str, sha_before: str, content: bytes) -> FileDiff:
    """Generate diff for deleted file (all deletions)."""
    try:
        text = content.decode('utf-8')
        lines = text.splitlines()

        # Create single hunk with all deletions
        hunk = Hunk(
            start_line=1,
            end_line=len(lines),
            additions=[],
            deletions=[f"- {line}" for line in lines[:20]]  # First 20 lines
        )

        # Add truncation marker if file is longer
        if len(lines) > 20:
            hunk.deletions.append(f"... ({len(lines) - 20} more lines)")

        return FileDiff(
            path=path,
            event_type="deleted",
            sha_before=sha_before,
            sha_after=None,
            hunks=[hunk]
        )
    except UnicodeDecodeError:
        # Binary file - no hunks
        return FileDiff(
            path=path,
            event_type="deleted",
            sha_before=sha_before,
            sha_after=None,
            hunks=[]
        )


def _generate_modification_diff(
    path: str,
    sha_before: str,
    sha_after: str,
    old_content: bytes,
    new_content: bytes
) -> FileDiff:
    """Generate diff for modified file with hunks."""
    try:
        old_text = (old_content or b'').decode('utf-8')
        new_text = (new_content or b'').decode('utf-8')

        old_lines = old_text.splitlines()
        new_lines = new_text.splitlines()

        # Generate unified diff
        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=3  # Context lines
        ))

        # Parse hunks from unified diff
        hunks = _parse_unified_diff(diff_lines)

        return FileDiff(
            path=path,
            event_type="modified",
            sha_before=sha_before,
            sha_after=sha_after,
            hunks=hunks
        )
    except UnicodeDecodeError:
        # Binary file - no hunks
        return FileDiff(
            path=path,
            event_type="modified",
            sha_before=sha_before,
            sha_after=sha_after,
            hunks=[]
        )


def _parse_unified_diff(diff_lines: List[str]) -> List[Hunk]:
    """
    Parse unified diff output into structured hunks.

    Unified diff format:
        @@ -start,count +start,count @@
        -deleted line
        +added line
         context line
    """
    hunks = []
    current_hunk = None

    # Regex to match hunk headers: @@ -120,5 +120,7 @@
    hunk_header_re = re.compile(r'^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@')

    for line in diff_lines:
        # Check for hunk header
        match = hunk_header_re.match(line)
        if match:
            # Save previous hunk
            if current_hunk:
                hunks.append(current_hunk)

            # Start new hunk
            old_start = int(match.group(1))
            new_start = int(match.group(3))

            current_hunk = Hunk(
                start_line=new_start,
                end_line=new_start,  # Will be updated as we parse
                additions=[],
                deletions=[]
            )
            continue

        # Skip diff metadata lines
        if line.startswith('---') or line.startswith('+++'):
            continue

        # Parse hunk content
        if current_hunk:
            if line.startswith('-'):
                current_hunk.deletions.append(line)
            elif line.startswith('+'):
                current_hunk.additions.append(line)
                current_hunk.end_line += 1
            elif line.startswith(' '):
                # Context line - advance end line
                current_hunk.end_line += 1

    # Save last hunk
    if current_hunk:
        hunks.append(current_hunk)

    return hunks


def normalize_diff_batch(
    root_path: Path,
    file_changes: List[Dict],
    store_old_content: bool = False
) -> List[FileDiff]:
    """
    Normalize a batch of file changes into structured diffs.

    Args:
        root_path: Repository root path
        file_changes: List of file change dicts from FileWatcher
            [{"path": "...", "event_type": "...", "sha_after": "..."}]
        store_old_content: Whether to read old file content from disk
            (requires git history or backup mechanism)

    Returns:
        List of FileDiff objects with hunks
    """
    diffs = []

    for change in file_changes:
        file_path = root_path / change["path"]
        event_type = change["event_type"]

        # Determine old and new content
        old_content = None
        new_content = None

        if event_type == "created":
            # New file - read current content
            if file_path.exists():
                new_content = file_path.read_bytes()

        elif event_type == "deleted":
            # Deleted file - old content not available unless backed up
            # For now, skip hunks for deleted files without backup
            old_content = None

        elif event_type == "modified":
            # Modified file - read current content
            if file_path.exists():
                new_content = file_path.read_bytes()

            # Old content requires git history or backup
            # For real-time watching, we can't easily get old content
            # Solution: Use git diff or maintain shadow copies
            # For now: emit modified event without hunks (just hashes)
            if store_old_content:
                # TODO: Implement git-based old content retrieval
                old_content = _get_old_content_from_git(file_path)

        # Generate diff
        diff = generate_diff(file_path, event_type, old_content, new_content)
        diffs.append(diff)

    return diffs


def _get_old_content_from_git(file_path: Path) -> Optional[bytes]:
    """
    Get old file content from git (HEAD version).

    This is a placeholder for git integration.
    Real implementation would use: git show HEAD:path
    """
    # TODO: Implement git-based content retrieval
    # For MVP: return None (diffs will be hash-only)
    return None


def serialize_diff(diff: FileDiff) -> Dict:
    """
    Serialize FileDiff to JSON-compatible dict.

    Output format matches spec § 6.1:
    {
      "path": "...",
      "sha_before": "...",
      "sha_after": "...",
      "hunks": [{"start": 120, "end": 138, "add": "...", "del": "..."}]
    }
    """
    return {
        "path": diff.path,
        "sha_before": diff.sha_before,
        "sha_after": diff.sha_after,
        "hunks": [
            {
                "start": hunk.start_line,
                "end": hunk.end_line,
                "add": "\n".join(hunk.additions) if hunk.additions else "",
                "del": "\n".join(hunk.deletions) if hunk.deletions else ""
            }
            for hunk in diff.hunks
        ]
    }


# Test function
if __name__ == "__main__":
    import tempfile

    # Test: Create a temporary file and modify it
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def hello():\n    print('Hello')\n")
        temp_path = Path(f.name)

    try:
        # Test creation diff
        content = temp_path.read_bytes()
        diff = generate_diff(temp_path, "created", None, content)
        print("Creation diff:")
        print(f"  Path: {diff.path}")
        print(f"  SHA: {diff.sha_after}")
        print(f"  Hunks: {len(diff.hunks)}")
        if diff.hunks:
            print(f"  First hunk: {diff.hunks[0].start_line}-{diff.hunks[0].end_line}")
            print(f"  Additions: {len(diff.hunks[0].additions)}")

        # Test modification diff
        old_content = content
        temp_path.write_text("def hello():\n    print('Hello, World!')\n")
        new_content = temp_path.read_bytes()

        diff = generate_diff(temp_path, "modified", old_content, new_content)
        print("\nModification diff:")
        print(f"  Path: {diff.path}")
        print(f"  SHA before: {diff.sha_before}")
        print(f"  SHA after: {diff.sha_after}")
        print(f"  Hunks: {len(diff.hunks)}")
        if diff.hunks:
            for i, hunk in enumerate(diff.hunks):
                print(f"  Hunk {i+1}: {hunk.start_line}-{hunk.end_line}")
                print(f"    Additions: {hunk.additions}")
                print(f"    Deletions: {hunk.deletions}")

    finally:
        temp_path.unlink()
