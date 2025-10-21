#!/usr/bin/env python3
"""
Verify TRACE parser test results

Checks:
1. Guardian log for TraceParser output
2. Graph API for test nodes
3. Detailed error messages if parsing failed
"""

import subprocess
import json
import time
from datetime import datetime

print("=" * 70)
print("TRACE PARSER VERIFICATION TEST")
print("=" * 70)
print(f"Timestamp: {datetime.now().isoformat()}")
print()

# Wait for conversation_watcher to process (should be fast with file watching)
print("Waiting 5 seconds for conversation_watcher to process...")
time.sleep(5)

# Check 1: Guardian log for latest TraceParser activity
print("\n[1/3] Checking guardian.log for TraceParser activity...")
print("-" * 70)

try:
    result = subprocess.run(
        ['tail', '-100', 'guardian.log'],
        capture_output=True,
        text=True,
        cwd='C:/Users/reyno/mind-protocol'
    )

    lines = result.stdout.split('\n')

    # Find most recent TraceParser lines for felix
    parser_lines = [l for l in lines if 'TraceParser' in l and 'felix' in l.lower()]

    if parser_lines:
        print("Latest TraceParser activity:")
        for line in parser_lines[-10:]:  # Last 10 relevant lines
            print(f"  {line}")
    else:
        print("⚠️  No TraceParser activity found for felix in last 100 lines")

    # Look for processing stats
    stats_lines = [l for l in lines if 'TRACE processing stats' in l or 'nodes created' in l.lower() or 'formations' in l.lower()]
    if stats_lines:
        print("\nProcessing stats:")
        for line in stats_lines[-5:]:
            print(f"  {line}")

    # Look for errors/warnings
    error_lines = [l for l in lines[-50:] if 'ERROR' in l or 'WARNING' in l]
    if error_lines:
        print("\nRecent errors/warnings:")
        for line in error_lines[-10:]:
            print(f"  {line}")

except Exception as e:
    print(f"❌ Error reading guardian.log: {e}")

# Check 2: Query graph API for test nodes
print("\n[2/3] Checking graph API for test nodes...")
print("-" * 70)

try:
    result = subprocess.run(
        ['curl', '-s', 'http://localhost:8000/api/graph/citizen/citizen_felix'],
        capture_output=True,
        text=True
    )

    graph_data = json.loads(result.stdout)

    # Look for test nodes created today
    test_nodes = [
        n for n in graph_data.get('nodes', [])
        if n.get('node_id') and 'test_' in n.get('node_id', '') and '2025_10_19' in n.get('node_id', '')
    ]

    if test_nodes:
        print(f"✅ Found {len(test_nodes)} test node(s):")
        for node in test_nodes:
            print(f"  - {node.get('node_id')}")
            print(f"    Text: {node.get('text', 'N/A')[:100]}")
            print(f"    Confidence: {node.get('confidence', 'N/A')}")
    else:
        print("❌ No test nodes found in graph")
        print(f"   Total nodes: {graph_data.get('metadata', {}).get('node_count', 'unknown')}")

        # Show some recent nodes for comparison
        print("\n   Sample of existing nodes:")
        for node in graph_data.get('nodes', [])[:5]:
            print(f"     - ID: {node.get('id')}, node_id: {node.get('node_id', 'null')}")

except json.JSONDecodeError as e:
    print(f"❌ Error parsing graph response: {e}")
    print(f"   Response: {result.stdout[:200]}")
except Exception as e:
    print(f"❌ Error querying graph: {e}")

# Check 3: Check conversation_watcher specific logs
print("\n[3/3] Checking conversation_watcher activity...")
print("-" * 70)

try:
    # Check if conversation_watcher detected the response
    result = subprocess.run(
        ['grep', '-A', '5', 'felix', '.heartbeats/conversation_watcher.log'],
        capture_output=True,
        text=True,
        cwd='C:/Users/reyno/mind-protocol'
    )

    if result.stdout:
        lines = result.stdout.split('\n')
        print(f"Latest conversation_watcher.log entries ({len(lines)} lines)")
        # Show last 20 lines
        for line in lines[-20:]:
            if line.strip():
                print(f"  {line}")
    else:
        print("⚠️  No felix entries in conversation_watcher.log")

except Exception as e:
    print(f"⚠️  Could not read conversation_watcher.log: {e}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
