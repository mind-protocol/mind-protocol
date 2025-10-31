#!/usr/bin/env python3
"""Debug script to understand why assistant messages aren't being captured."""

import json
from pathlib import Path

# Find most recent transcript
transcript_dir = Path('/mnt/c/Users/reyno/.claude/projects')
ada_project = list(transcript_dir.glob('C--Users-reyno-mind-protocol-consciousness-citizens-ada'))

if ada_project:
    transcripts = list(ada_project[0].glob('*.jsonl'))
    if transcripts:
        latest = max(transcripts, key=lambda p: p.stat().st_mtime)
        print(f"Reading transcript: {latest.name}\n")

        # Read last 50 lines
        with open(latest, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-50:]

        user_count = 0
        assistant_count = 0

        print("=== Last 50 transcript entries ===\n")

        for i, line in enumerate(recent_lines):
            try:
                entry = json.loads(line)
                if 'message' in entry:
                    msg = entry['message']
                    role = msg.get('role', 'unknown')
                    content_blocks = msg.get('content', [])

                    # Count text blocks
                    text_blocks = [b for b in content_blocks if isinstance(b, dict) and b.get('type') == 'text']

                    if role == 'user':
                        user_count += 1
                        print(f"[{i}] USER - {len(content_blocks)} blocks ({len(text_blocks)} text)")
                    elif role == 'assistant':
                        assistant_count += 1
                        print(f"[{i}] ASSISTANT - {len(content_blocks)} blocks ({len(text_blocks)} text)")

                        # Show first text block if exists
                        if text_blocks:
                            text_preview = text_blocks[0].get('text', '')[:100]
                            print(f"     Text preview: {text_preview}...")
                        else:
                            print(f"     No text blocks! Block types: {[b.get('type') for b in content_blocks if isinstance(b, dict)]}")
            except Exception as e:
                print(f"[{i}] ERROR parsing: {e}")

        print(f"\n=== Summary ===")
        print(f"User messages: {user_count}")
        print(f"Assistant messages: {assistant_count}")
