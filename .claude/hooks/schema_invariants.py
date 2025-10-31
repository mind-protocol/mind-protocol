#!/usr/bin/env python3
"""
Schema Invariant Lints for Mind Protocol

Validates architectural constraints after Write/Edit operations:
1. No energy fields on Mode nodes
2. Affiliation mass bounds per SubEntity [0.8, 1.2]
3. Entity deprecation (use SubEntity/Mode explicitly)

Author: Atlas (Infrastructure Engineer)
Created: 2025-10-26
Spec: TIER1_REDLINES_2025-10-26.md (Amendments 1-3)
"""

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class Violation:
    """Schema invariant violation"""
    type: str
    severity: str  # "ERROR" | "WARNING"
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None


def lint_entity_deprecation(file_path: str, content: str) -> List[Violation]:
    """
    Amendment 3: Check for deprecated 'Entity' usage.

    Use SubEntity or Mode explicitly to prevent terminology confusion.
    """
    violations = []

    # Skip non-text files
    if not any(file_path.endswith(ext) for ext in ['.md', '.py', '.ts', '.tsx', '.json', '.yaml', '.yml']):
        return violations

    # Patterns that should trigger warning
    forbidden_patterns = [
        (r'\bEntity\b(?! Ecosystem)', "Deprecated 'Entity' - use 'SubEntity' or 'Mode'"),
        (r'entity_layer', "Deprecated 'entity_layer' module name"),
    ]

    # Allowed patterns (don't flag these)
    allowed_patterns = [
        r'SubEntity',                 # Correct term
        r'entity_id',                 # Established field name
        r'# Previously.*Entity',      # Historical comment
        r'entity_differentiation',    # Spec filename (established)
        r'entity_metrics',            # Established module
        r'entity_creation',           # Established module
        r'entity_lifecycle',          # Established module
        r'entity_activations',        # Established field
        r'EntityMetrics',             # Class name
        r'EntityCreation',            # Class name
        r'EntityLifecycle',           # Class name
        r'EntityBootstrap',           # Class name
        r'MEMBER_OF.*entity',         # Edge context
    ]

    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Skip if matches allowed pattern
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in allowed_patterns):
            continue

        # Check forbidden patterns
        for pattern, msg in forbidden_patterns:
            if re.search(pattern, line):
                violations.append(
                    Violation(
                        type="TERMINOLOGY",
                        severity="WARNING",
                        file=Path(file_path),
                        line=i,
                        message=f"{msg} (TAXONOMY_RECONCILIATION.md §3)"
                    )
                )

    return violations


def lint_mode_energy_fields(file_path: str, content: str) -> List[Violation]:
    """
    Amendment 1: Verify no Mode nodes have energy fields.

    Modes are derived activations - energy on Mode violates single-energy substrate.
    """
    violations = []

    # Only check Python/TypeScript files where Mode creation happens
    if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.tsx']):
        return violations

    # Check for Mode creation with energy fields
    mode_creation_patterns = [
        (r'Mode\s*\(.*energy\s*=', "Mode creation with 'energy' field"),
        (r'Mode\s*\{.*energy\s*:', "Mode creation with 'energy' field"),
        (r':Mode.*energy\s*:', "Mode node with 'energy' property"),
    ]

    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#') or line.strip().startswith('//'):
            continue

        for pattern, msg in mode_creation_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                violations.append(
                    Violation(
                        type="SCHEMA_INVARIANT",
                        severity="ERROR",
                        file=Path(file_path),
                        line=i,
                        message=f"{msg} - violates single-energy substrate (TIER1_REDLINES §1)"
                    )
                )

    return violations


def lint_affiliation_budget_violations(file_path: str, content: str) -> List[Violation]:
    """
    Amendment 2: Check for affiliation weight assignments that might violate bounds.

    This is a static lint - runtime validation happens in mode creation.
    Just flag suspicious patterns for review.
    """
    violations = []

    # Only check Python files where affiliation logic lives
    if not file_path.endswith('.py'):
        return violations

    # Look for affiliation weight assignments >1.2 or <0
    suspicious_patterns = [
        (r'weight\s*=\s*([1-9]\.\d+|[2-9]\.)', "Affiliation weight >1.0 (verify total stays within [0.8, 1.2])"),
        (r'weight\s*=\s*-', "Negative affiliation weight"),
    ]

    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue

        # Check if line is in AFFILIATES_WITH context
        if 'AFFILIATES_WITH' not in line and 'affiliation' not in line.lower():
            continue

        for pattern, msg in suspicious_patterns:
            if re.search(pattern, line):
                violations.append(
                    Violation(
                        type="SCHEMA_INVARIANT",
                        severity="WARNING",
                        file=Path(file_path),
                        line=i,
                        message=f"{msg} (TIER1_REDLINES §2)"
                    )
                )

    return violations


def main():
    """
    PreToolUse hook: Validate schema invariants before Write/Edit.

    Returns JSON with permissionDecision to deny if violations found.
    """
    try:
        # Read hook input from stdin
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        # Invalid input - fail silently
        sys.exit(0)

    hook_event = input_data.get("hook_event_name", "")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Only run for Write/Edit/NotebookEdit
    if hook_event != "PreToolUse" or tool_name not in ["Write", "Edit", "NotebookEdit"]:
        sys.exit(0)

    # Get file path and content
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Get proposed content based on tool type
    if tool_name == "Write":
        # Write has full content
        content = tool_input.get("content", "")
    elif tool_name == "Edit":
        # Edit: Read current file and apply proposed change
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                current_content = f.read()

            old_string = tool_input.get("old_string", "")
            new_string = tool_input.get("new_string", "")

            # Apply the proposed edit
            if old_string and old_string in current_content:
                content = current_content.replace(old_string, new_string, 1)
            else:
                # Can't apply edit - skip validation
                sys.exit(0)
        except Exception:
            # Can't read file - skip validation
            sys.exit(0)
    elif tool_name == "NotebookEdit":
        # NotebookEdit has new_source
        content = tool_input.get("new_source", "")
    else:
        sys.exit(0)

    if not content:
        sys.exit(0)

    # Run lints
    violations = []
    violations.extend(lint_entity_deprecation(file_path, content))
    violations.extend(lint_mode_energy_fields(file_path, content))
    violations.extend(lint_affiliation_budget_violations(file_path, content))

    if not violations:
        # No violations - allow
        sys.exit(0)

    # Format violations
    errors = [v for v in violations if v.severity == "ERROR"]
    warnings = [v for v in violations if v.severity == "WARNING"]

    if errors:
        # Deny write with error feedback
        feedback = "❌ **Schema Invariant Violations:**\n\n"
        for v in errors:
            location = f"{v.file.name}:{v.line}" if v.file else "unknown"
            feedback += f"- **{location}**: {v.message}\n"

        feedback += f"\n{len(errors)} error(s) found. Please fix before writing."

        # Write to stderr for conversation capture
        print(feedback, file=sys.stderr)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": feedback
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    if warnings:
        # Allow write but show warnings
        feedback = "⚠️  **Schema Invariant Warnings:**\n\n"
        for v in warnings:
            location = f"{v.file.name}:{v.line}" if v.file else "unknown"
            feedback += f"- **{location}**: {v.message}\n"

        feedback += f"\n{len(warnings)} warning(s) found. Review recommended."

        # Write to stderr for conversation capture
        print(feedback, file=sys.stderr)

        # For PreToolUse warnings, we use "deny"for self-correction
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": feedback
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
