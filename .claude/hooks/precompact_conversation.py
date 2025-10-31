#!/usr/bin/env python3
from __future__ import annotations
"""
Claude Code PreCompact hook - Preserves conversation before compact
Triggered when compact is about to happen (manual or auto)

This hook ensures pre-compact conversation is preserved by:
1. Finalizing the current context (mark as closed)
2. Creating new context directory for post-compact conversation
3. Updating tracking so future messages go to new context
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

from membrane_bus import publish_to_membrane

def detect_entity_info() -> tuple[str, str]:
    """
    Detect subentity type and ID from current working directory.
    Handles:
    - consciousness/citizens/{citizen}/ → ('citizen', citizen_name)
    - consciousness/organization/ → ('organization', 'mind_protocol')
    - consciousness/ecology/ → ('ecology', 'ecosystem')

    Returns (entity_type, entity_id)
    """
    cwd = Path.cwd()
    parts = cwd.parts

    # Check for citizens
    if 'citizens' in parts:
        try:
            citizens_idx = parts.index('citizens')
            if citizens_idx + 1 < len(parts):
                return ('citizen', parts[citizens_idx + 1])
        except (ValueError, IndexError):
            pass

    # Check for organization
    if 'organization' in parts:
        return ('organization', 'mind_protocol')

    # Check for ecology/ecosystem
    if 'ecology' in parts or 'ecosystem' in parts:
        return ('ecology', 'ecosystem')

    return ('unknown', 'unknown')

def find_entity_dir() -> Path:
    """
    Find the subentity directory (citizen/organization/ecology) from current working directory.
    """
    cwd = Path.cwd()
    parts = cwd.parts

    # For citizens: navigate to citizens/{citizen}/
    if 'citizens' in parts:
        try:
            citizens_idx = parts.index('citizens')
            entity_root = Path(*parts[:citizens_idx + 2])  # includes citizens/{citizen}
            return entity_root
        except (ValueError, IndexError):
            pass

    # For organization: navigate to organization/
    if 'organization' in parts:
        try:
            collective_idx = parts.index('organization')
            entity_root = Path(*parts[:collective_idx + 1])  # includes organization
            return entity_root
        except (ValueError, IndexError):
            pass

    # For ecology: navigate to ecology/
    if 'ecology' in parts or 'ecosystem' in parts:
        try:
            idx = parts.index('ecology') if 'ecology' in parts else parts.index('ecosystem')
            entity_root = Path(*parts[:idx + 1])
            return entity_root
        except (ValueError, IndexError):
            pass

    # Fallback: assume CWD is the subentity directory
    return cwd

def finalize_current_context() -> tuple[Path | None, str | None]:
    """
    Finalize the current context by marking it as closed.
    This prevents future messages from being added to this context.
    """
    entity_root = find_entity_dir()
    contexts_dir = entity_root / 'contexts'

    if not contexts_dir.exists():
        return  # No contexts yet

    # Find most recent context
    contexts = sorted([d for d in contexts_dir.iterdir() if d.is_dir()], reverse=True)

    if not contexts:
        return None, None

    latest_context = contexts[0]
    metadata_file = latest_context / 'metadata.json'
    context_id = latest_context.name

    if not metadata_file.exists():
        return latest_context, context_id

    try:
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)

        # Mark as closed (compact happened)
        metadata['closed_at'] = datetime.now(timezone.utc).isoformat()
        metadata['closed_reason'] = 'compact'

        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    except Exception as e:
        print(f"⚠ Error finalizing context: {e}", file=sys.stderr)
        return latest_context, context_id

    return latest_context, context_id
def create_new_context() -> tuple[Path, str]:
    """
    Create new context directory for post-compact conversation.
    Returns (context_dir, context_id)
    """
    entity_type, entity_id = detect_entity_info()
    entity_root = find_entity_dir()
    contexts_dir = entity_root / 'contexts'
    contexts_dir.mkdir(parents=True, exist_ok=True)

    # Create new context with timestamp
    context_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_context = contexts_dir / context_id
    new_context.mkdir(exist_ok=True)

    # Create initial metadata
    metadata = {
        'context_id': context_id,
        'entity_type': entity_type,
        'entity_id': entity_id,
        'created_at': datetime.now(timezone.utc).isoformat(),
        'created_by': 'precompact_hook',
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'message_count': 0,
        'has_tool_calls': False
    }

    metadata_file = new_context / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    return new_context, context_id

def main():
    try:
        # Read hook input
        data = json.load(sys.stdin)

        # Debug logging (non-fatal if fails)
        try:
            debug_file = Path('/home/mind-protocol/mindprotocol/.claude/hooks/precompact_hook_debug.log')
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_file, 'a') as f:
                f.write(f"\n\n=== PreCompact Hook Fired at {datetime.now()} ===\n")
                f.write(f"Trigger: {data.get('trigger', 'unknown')}\n")
                f.write(f"Session ID: {data.get('session_id', 'unknown')}\n")
        except Exception as e:
            print(f"⚠ Debug log write failed: {e}", file=sys.stderr)

        # Detect subentity
        entity_type, entity_id = detect_entity_info()
        if entity_type == 'unknown':
            print("⚠ Could not detect subentity from CWD", file=sys.stderr)
            return

        # Step 1: Finalize current context
        closed_context_path, closed_context_id = finalize_current_context()

        # Step 2: Create new context for post-compact conversation
        new_context, context_id = create_new_context()

        print(f"✓ PreCompact: Finalized old context, created {entity_id}/contexts/{context_id}/", file=sys.stderr)

        project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", Path.cwd()))
        closed_metadata = (closed_context_path / 'metadata.json') if closed_context_path else None
        try:
            new_metadata_rel = (new_context / 'metadata.json').relative_to(project_root)
        except ValueError:
            new_metadata_rel = new_context / 'metadata.json'
        closed_metadata_rel = None
        if closed_metadata and closed_metadata.exists():
            try:
                closed_metadata_rel = closed_metadata.relative_to(project_root)
            except ValueError:
                closed_metadata_rel = closed_metadata

        publish_to_membrane(
            channel="session.compaction",
            origin="ui",
            payload={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "closed_context_id": closed_context_id,
                "new_context_id": context_id,
                "closed_metadata_file": str(closed_metadata_rel) if closed_metadata_rel else None,
                "new_metadata_file": str(new_metadata_rel),
            },
            ttl_frames=900,
            dedupe_key=f"{entity_id}:compaction:{context_id}",
        )

        with open(debug_file, 'a') as f:
            f.write(f"Created new context: {context_id}\n")
            f.write(f"Success\n")

    except Exception as e:
        print(f"✗ Error in PreCompact hook: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Don't exit with error - don't block compact
        sys.exit(0)

if __name__ == '__main__':
    main()
