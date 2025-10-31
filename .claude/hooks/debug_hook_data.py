#!/usr/bin/env python3
"""
Debug hook - Print the exact JSON structure received from Claude Code hooks
"""
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    data = json.load(sys.stdin)

    # Write to debug file
    debug_file = Path('.claude/hooks/hook_debug_output.json')

    with open(debug_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'hook_data': data
        }, f, indent=2, ensure_ascii=False)

    print(f"✓ Debug data written to {debug_file}", file=sys.stderr)

except Exception as e:
    print(f"✗ Error in debug hook: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
