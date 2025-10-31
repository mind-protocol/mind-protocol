#!/usr/bin/env python3
"""
Claude Code Stop hook - Captures conversation to contexts/ with full JSON structure
Triggered after each assistant response completes
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
    Handles:
    - .../consciousness/citizens/{citizen}/ → returns path to citizen root
    - .../consciousness/organization/ → returns path to organization root
    - .../consciousness/ecology/ → returns path to ecology root
    """
    cwd = Path.cwd()
    parts = cwd.parts

    # For citizens: navigate to citizens/{citizen}/
    if 'citizens' in parts:
        try:
            citizens_idx = parts.index('citizens')
            # Reconstruct path up to citizen directory
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

def get_or_create_context_dir() -> tuple[Path, str]:
    """
    Get current context directory or create new one.
    Uses most recent context if it exists, is less than 1 hour old, AND is not closed.
    Otherwise creates new context.
    Returns (context_dir, context_id)
    """
    citizen_root = find_entity_dir()
    contexts_dir = citizen_root / 'contexts'
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

                # Check if context is closed (by PreCompact hook)
                if 'closed_at' in metadata:
                    # Context was closed - create new one
                    pass  # Fall through to create new context
                else:
                    last_updated = datetime.fromisoformat(metadata.get('last_updated', '2000-01-01'))
                    age_hours = (datetime.now(timezone.utc) - last_updated).total_seconds() / 3600

                    # Reuse context if less than 1 hour old and not closed
                    if age_hours < 1:
                        return latest_context, context_id
            except Exception:
                pass  # If error reading metadata, create new context

    # Create new context
    context_id = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    new_context = contexts_dir / context_id
    new_context.mkdir(exist_ok=True)

    return new_context, context_id

def extract_tool_calls(content_blocks) -> tuple[list, list]:
    """Extract tool calls and results from content blocks"""
    tool_calls = []
    tool_results = []

    for block in content_blocks:
        if not isinstance(block, dict):
            continue

        if block.get('type') == 'tool_use':
            tool_calls.append({
                'id': block.get('id'),
                'tool': block.get('name'),
                'input': block.get('input', {}),
            })
        elif block.get('type') == 'tool_result':
            tool_results.append({
                'id': block.get('tool_use_id'),
                'output': block.get('content'),
                'is_error': block.get('is_error', False)
            })

    return tool_calls, tool_results

def format_message(message: dict) -> dict:
    """Format a message for JSON storage"""
    role = message.get('role', 'unknown')
    content = message.get('content', [])

    # Handle content as string or array
    if isinstance(content, str):
        # Simple string content (common for user messages)
        text_content = content
        tool_calls, tool_results = [], []
    else:
        # Array of content blocks
        content_blocks = content if isinstance(content, list) else []

        # Extract text content
        text_content = ''
        for block in content_blocks:
            if isinstance(block, dict) and block.get('type') == 'text':
                text_content += block.get('text', '')
            elif isinstance(block, str):
                text_content += block

        # Extract tool calls and results
        tool_calls, tool_results = extract_tool_calls(content_blocks)

    # Use preserved timestamp if available, otherwise use current time
    timestamp = message.get('_timestamp')
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    formatted = {
        'role': role,
        'timestamp': timestamp,
        'content': text_content
    }

    if tool_calls:
        formatted['tool_calls'] = tool_calls
    if tool_results:
        formatted['tool_results'] = tool_results

    return formatted

def read_transcript(transcript_path: str) -> list:
    """Read and parse JSONL transcript file"""
    messages = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # Extract the message from the entry
                    # Structure: {message: {role, content}, type, uuid, timestamp, ...}
                    if 'message' in entry:
                        msg = entry['message']
                        msg['_timestamp'] = entry.get('timestamp')  # Preserve original timestamp
                        messages.append(msg)
    except Exception as e:
        print(f"⚠ Error reading transcript: {e}", file=sys.stderr)

    return messages

def main():
    try:
        # Read hook input
        data = json.load(sys.stdin)

        # Debug: log what we received (non-fatal if fails)
        try:
            debug_file = Path('/home/mind-protocol/mindprotocol/.claude/hooks/stop_hook_debug.log')
            debug_file.parent.mkdir(parents=True, exist_ok=True)
            with open(debug_file, 'a') as f:
                f.write(f"\n\n=== Stop Hook Fired at {datetime.now()} ===\n")
                f.write(f"Hook data keys: {list(data.keys())}\n")
                f.write(f"Full data: {json.dumps(data, indent=2)}\n")
        except Exception as e:
            # Debug logging failure shouldn't crash the hook
            print(f"⚠ Debug log write failed: {e}", file=sys.stderr)

        # Stop hook provides transcript_path, not conversation directly
        transcript_path = data.get('transcript_path', '')
        if not transcript_path:
            print("⚠ No transcript_path in hook data", file=sys.stderr)
            return

        # Detect subentity (citizen/organization/ecology)
        entity_type, entity_id = detect_entity_info()
        if entity_type == 'unknown':
            print("⚠ Could not detect subentity from CWD", file=sys.stderr)
            return

        # Get or create context directory
        context_dir, context_id = get_or_create_context_dir()

        # Load existing conversation or create new
        # File is named with timestamp: {context_id}.json
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

        # Read messages from transcript JSONL file
        messages = read_transcript(transcript_path)

        # Format all messages (preserving history)
        formatted_messages = []
        for msg in messages:
            formatted_messages.append(format_message(msg))

        # Update conversation data
        conversation_data['messages'] = formatted_messages
        conversation_data['last_updated'] = datetime.now(timezone.utc).isoformat()
        conversation_data['message_count'] = len(formatted_messages)

        # Validate JSON before writing (catch serialization errors early)
        try:
            json.dumps(conversation_data)
        except (TypeError, ValueError) as e:
            print(f"✗ JSON validation failed for conversation data: {e}", file=sys.stderr)
            return

        # Write conversation.json atomically (write to temp, then rename)
        temp_file = conversation_file.with_suffix('.json.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(conversation_data, f, indent=2, ensure_ascii=False)
            # Atomic rename (POSIX and Windows guarantee atomicity)
            temp_file.replace(conversation_file)
        except Exception as e:
            print(f"✗ Failed to write conversation file: {e}", file=sys.stderr)
            if temp_file.exists():
                temp_file.unlink()  # Clean up temp file
            return

        # Prepare metadata
        metadata = {
            'context_id': context_id,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'created_at': conversation_data['created_at'],
            'last_updated': conversation_data['last_updated'],
            'message_count': conversation_data['message_count'],
            'has_tool_calls': any('tool_calls' in m for m in formatted_messages)
        }

        # Validate metadata JSON
        try:
            json.dumps(metadata)
        except (TypeError, ValueError) as e:
            print(f"✗ JSON validation failed for metadata: {e}", file=sys.stderr)
            return

        # Write metadata.json atomically
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

        project_root = Path(os.getenv("CLAUDE_PROJECT_DIR", Path.cwd()))
        try:
            conversation_rel = conversation_file.relative_to(project_root)
            metadata_rel = metadata_file.relative_to(project_root)
        except ValueError:
            conversation_rel = conversation_file
            metadata_rel = metadata_file

        latest_message = formatted_messages[-1] if formatted_messages else {}

        publish_to_membrane(
            channel="provider.claude.output",
            origin="provider_claude",
            payload={
                "session_id": context_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "message_count": conversation_data["message_count"],
                "context_file": str(conversation_rel),
                "metadata_file": str(metadata_rel),
                "latest_message": latest_message,
            },
            ttl_frames=900,
            dedupe_key=f"{entity_id}:{context_id}:stop:{conversation_data['message_count']}",
        )

        print(f"✓ Captured to {entity_id}/contexts/{context_id}/", file=sys.stderr)

    except Exception as e:
        print(f"✗ Error capturing conversation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        # Don't exit with error - don't block Claude Code
        sys.exit(0)

if __name__ == '__main__':
    main()
