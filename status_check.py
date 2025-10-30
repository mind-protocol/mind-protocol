#!/usr/bin/env python3
"""
Comprehensive Mind Protocol Status Check
Victor "The Resurrector" - Guardian Infrastructure

Single command to verify all system components.
"""
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import json

try:
    import requests
except ImportError:
    print("⚠️  requests not installed, HTTP checks will be skipped")
    requests = None

def check_port(port: int, service_name: str) -> dict:
    """Check if port is bound."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('localhost', port))
        bound = result == 0
        sock.close()
        return {"service": service_name, "port": port, "status": "✅ BOUND" if bound else "❌ NOT BOUND", "bound": bound}
    except Exception as e:
        return {"service": service_name, "port": port, "status": f"❌ ERROR: {e}", "bound": False}

def check_api_endpoint(url: str, name: str) -> dict:
    """Check HTTP endpoint."""
    if not requests:
        return {"endpoint": name, "url": url, "status": "⚠️  SKIPPED", "responding": False}

    try:
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            return {"endpoint": name, "url": url, "status": "✅ RESPONDING", "data": data, "responding": True}
        else:
            return {"endpoint": name, "url": url, "status": f"❌ HTTP {resp.status_code}", "responding": False}
    except Exception as e:
        return {"endpoint": name, "url": url, "status": f"❌ ERROR: {e}", "responding": False}

def check_git_status() -> dict:
    """Check git repository status."""
    try:
        # Check last commit
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h %s - %ar"],
            capture_output=True,
            text=True,
            cwd="/home/mind-protocol/mindprotocol"
        )
        last_commit = result.stdout.strip() if result.returncode == 0 else "ERROR"

        # Check for uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd="/home/mind-protocol/mindprotocol"
        )
        has_changes = bool(result.stdout.strip())

        return {
            "last_commit": last_commit,
            "uncommitted_changes": has_changes,
            "status": "✅ CLEAN" if not has_changes else "⚠️  UNCOMMITTED CHANGES"
        }
    except Exception as e:
        return {"status": f"❌ ERROR: {e}"}

def main():
    print("=" * 70)
    print("MIND PROTOCOL - COMPREHENSIVE STATUS CHECK")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)
    print()

    # Port checks
    print("🔌 PORT STATUS:")
    ports = [
        (8000, "WebSocket Server"),
        (6379, "FalkorDB/Redis"),
        (3000, "Next.js Dashboard"),
    ]

    port_results = []
    for port, name in ports:
        result = check_port(port, name)
        port_results.append(result)
        print(f"  {result['status']:20s} {name:20s} (port {port})")
    print()

    # API endpoints
    print("🌐 API ENDPOINTS:")
    endpoints = [
        ("http://localhost:8000/api/citizen/victor/status", "Victor Status"),
        ("http://localhost:8000/api/consciousness/status", "System Status"),
    ]

    api_results = []
    for url, name in endpoints:
        result = check_api_endpoint(url, name)
        api_results.append(result)
        print(f"  {result['status']:20s} {name}")

        # Show key data if available
        if result.get('responding') and 'data' in result:
            data = result['data']
            if 'tick_count' in data:
                print(f"    → Ticks: {data['tick_count']:,}")
            if 'nodes' in data:
                print(f"    → Graph: {data['nodes']} nodes, {data.get('links', 0)} links")
            if 'consciousness_state' in data:
                print(f"    → State: {data['consciousness_state']}")
    print()

    # Git status
    print("📦 GIT REPOSITORY:")
    git_result = check_git_status()
    print(f"  {git_result['status']}")
    if 'last_commit' in git_result:
        print(f"    → {git_result['last_commit']}")
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY:")

    all_ports_bound = all(r['bound'] for r in port_results)
    all_apis_responding = all(r['responding'] for r in api_results if requests)

    if all_ports_bound and (all_apis_responding or not requests):
        print("✅ ALL SYSTEMS OPERATIONAL")
        sys.exit(0)
    else:
        print("❌ ISSUES DETECTED")
        if not all_ports_bound:
            print("  - Some ports not bound")
        if requests and not all_apis_responding:
            print("  - Some APIs not responding")
        sys.exit(1)

if __name__ == "__main__":
    main()
