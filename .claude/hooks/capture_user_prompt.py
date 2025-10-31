#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook - Captures user prompts to contexts/
Triggered when user submits a message, before Claude processes it
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
            entity_root = Path(*parts[:citizens_idx + 2])
            return entity_root
        except (ValueError, IndexError):
            pass

    # For organization: navigate to organization/
    if 'organization' in parts:
        try:
            collective_idx = parts.index('organization')
            entity_root = Path(*parts[:collective_idx + 1])
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

def get_or_create_context_dir() -> tuple[Path, str]:
    """
    Get current context directory or create new one.
    Uses most recent context if it exists and is less than 1 hour old,
    otherwise creates new context.
    Returns (context_dir, context_id)
    """
    entity_root = find_entity_dir()
    contexts_dir = entity_root / 'contexts'
    contexts_dir.mkdir(parents=True, exist_ok=True)

    # Find most recent context
    contexts = sorted([d for d in contexts_dir.iterdir() if d.is_dir()], reverse=True)

    if contexts:
        latest_context = contexts[0]
        context_id = latest_context.name
        metadata_file = latest_context / 'metadata.json'

        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                last_updated = datetime.fromisoformat(metadata.get('last_updated', '2000-01-01'))
                age_hours = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600

                # Reuse context if less than 1 hour old
                if age_hours < 1:
                    return latest_context, context_id
            except Exception:
                pass  # If error reading metadata, create new context

    # Create new context
    context_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_context = contexts_dir / context_id
    new_context.mkdir(exist_ok=True)

    return new_context, context_id

def main():
    try:
        # Read hook input
        data = json.load(sys.stdin)

        # Detect subentity (citizen/organization/ecology)
        entity_type, entity_id = detect_entity_info()
        if entity_type == 'unknown':
            print("⚠ Could not detect subentity from CWD", file=sys.stderr)
            return

        # Get or create context directory
        context_dir, context_id = get_or_create_context_dir()

        # Load existing conversation or create new
        conversation_file = context_dir / f'{context_id}.json'
        if conversation_file.exists():
            with open(conversation_file, 'r', encoding='utf-8') as f:
                conversation_data = json.load(f)
        else:
            conversation_data = {
                'context_id': context_id,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'messages': []
            }

        # Extract user prompt from hook data
        user_prompt = data.get('prompt', '')

        # Create user message entry
        user_message = {
            'role': 'user',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': user_prompt
        }

        # Append user message
        conversation_data['messages'].append(user_message)
        conversation_data['last_updated'] = datetime.now(timezone.utc).isoformat()
        conversation_data['message_count'] = len(conversation_data['messages'])

        # Validate JSON before writing
        try:
            json.dumps(conversation_data)
        except (TypeError, ValueError) as e:
            print(f"✗ JSON validation failed for conversation data: {e}", file=sys.stderr)
            return

        # Write conversation file atomically
        temp_file = conversation_file.with_suffix('.json.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            temp_file.replace(conversation_file)
        except Exception as e:
            print(f"✗ Failed to write conversation file: {e}", file=sys.stderr)
            if temp_file.exists():
                temp_file.unlink()
            return

        # Update metadata
        metadata = {
            'context_id': context_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'created_at': conversation_data['created_at'],
            'last_updated': conversation_data['last_updated'],
            'message_count': conversation_data['message_count'],
            'has_tool_calls': any('tool_calls' in m for m in conversation_data['messages'])
        }

        # Validate metadata JSON
        try:
            json.dumps(metadata)
        except (TypeError, ValueError) as e:
            print(f"✗ JSON validation failed for metadata: {e}", file=sys.stderr)
            return

        # Write metadata file atomically
        metadata_file = context_dir / 'metadata.json'
        temp_metadata = metadata_file.with_suffix('.json.tmp')
        try:
            with open(temp_metadata, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            temp_metadata.replace(metadata_file)
        except Exception as e:
            print(f"✗ Failed to write metadata file: {e}", file=sys.stderr)
            if temp_metadata.exists():
                temp_metadata.unlink()
            return

        # Publish to membrane bus
        project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", Path.cwd()))
        try:
            context_rel = (conversation_file.relative_to(project_root))
        except ValueError:
            context_rel = conversation_file
        publish_to_membrane(
            channel="ui.action.user_prompt",
            origin="ui",
            payload={
                "session_id": context_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "content": user_prompt,
                "message_index": conversation_data['message_count'],
                "context_file": str(context_rel),
            },
            ttl_frames=600,
            dedupe_key=f"{entity_id}:{context_id}:prompt:{conversation_data['message_count']}",
        )

        print(f"✓ Captured user prompt to {entity_id}/contexts/{context_id}/", file=sys.stderr)

    except Exception as e:
        print(f"✗ Error capturing user prompt: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Don't exit with error - don't block Claude Code
        sys.exit(0)

if __name__ == '__main__':
    main()
