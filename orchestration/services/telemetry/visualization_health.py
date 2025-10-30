"""
Visualization Pipeline Health Monitoring

For Victor "The Resurrector" to integrate into guardian.py

Monitors 4 critical components:
1. WebSocket server (port 8765)
2. Frontend (port 3000)
3. Snapshot API endpoint
4. Event stream flow

Recovery procedures for each failure mode.

@victor - Guardian integration module
@iris - Health monitoring architecture
Created: 2025-10-21
"""

import asyncio
import aiohttp
import websockets
import socket
import subprocess
import json
from typing import Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# ============================================================================
# Component Health Checks
# ============================================================================

async def check_websocket_server(host: str = "localhost", port: int = 8765, timeout: float = 2.0) -> Tuple[bool, str]:
    """
    Check if WebSocket server is accepting connections
    Returns: (healthy, message)
    """
    try:
        uri = f"ws://{host}:{port}"
        async with websockets.connect(uri, ping_timeout=timeout) as ws:
            # Try to receive one event
            try:
                event_json = await asyncio.wait_for(ws.recv(), timeout=timeout)
                event = json.loads(event_json)
                if 'kind' in event and 'frame_id' in event:
                    return True, f"WebSocket healthy (received {event['kind']})"
                else:
                    return False, "WebSocket returned invalid event format"
            except asyncio.TimeoutError:
                return True, "WebSocket connected (no events yet)"
    except ConnectionRefusedError:
        return False, f"WebSocket server not running on port {port}"
    except Exception as e:
        return False, f"WebSocket error: {e}"

async def check_frontend(host: str = "localhost", port: int = 3000, timeout: float = 3.0) -> Tuple[bool, str]:
    """
    Check if Next.js frontend is serving pages
    Returns: (healthy, message)
    """
    try:
        url = f"http://{host}:{port}/consciousness"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    # Verify it's actually the consciousness page
                    if 'consciousness' in html.lower() or 'canvas' in html.lower():
                        return True, f"Frontend healthy (HTTP {resp.status})"
                    else:
                        return False, "Frontend returned unexpected content"
                else:
                    return False, f"Frontend returned HTTP {resp.status}"
    except aiohttp.ClientConnectorError:
        return False, f"Frontend not responding on port {port}"
    except asyncio.TimeoutError:
        return False, "Frontend timeout"
    except Exception as e:
        return False, f"Frontend error: {e}"

async def check_snapshot_api(host: str = "localhost", port: int = 3000, timeout: float = 5.0) -> Tuple[bool, str]:
    """
    Check if snapshot API endpoint returns valid data
    Returns: (healthy, message)
    """
    try:
        url = f"http://{host}:{port}/api/viz/snapshot"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Validate structure
                    if 'nodes' in data and 'links' in data and 'subentities' in data:
                        node_count = len(data['nodes'])
                        link_count = len(data['links'])
                        entity_count = len(data['subentities'])
                        return True, f"Snapshot API healthy ({node_count} nodes, {link_count} links, {entity_count} subentities)"
                    else:
                        return False, "Snapshot API returned invalid structure"
                elif resp.status == 404:
                    return False, "Snapshot API endpoint not implemented yet"
                else:
                    return False, f"Snapshot API returned HTTP {resp.status}"
    except aiohttp.ClientConnectorError:
        return False, "Snapshot API not reachable"
    except asyncio.TimeoutError:
        return False, "Snapshot API timeout"
    except Exception as e:
        return False, f"Snapshot API error: {e}"

def check_port_listening(port: int) -> bool:
    """Check if a port is being listened to"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# ============================================================================
# Recovery Procedures
# ============================================================================

def recover_websocket_server() -> bool:
    """
    Attempt to recover WebSocket server
    Returns: True if recovery attempted
    """
    print(f"[VizHealth] Attempting to recover WebSocket server...")

    # Check if websocket_server.py exists
    server_path = Path(__file__).parent / "websocket_server.py"
    if not server_path.exists():
        print(f"[VizHealth] websocket_server.py not found at {server_path}")
        return False

    # Guardian should handle process management
    # This is just a notification
    print(f"[VizHealth] WebSocket server needs restart (guardian will handle)")
    return True

def recover_frontend() -> bool:
    """
    Attempt to recover Next.js frontend
    Returns: True if recovery attempted
    """
    print(f"[VizHealth] Attempting to recover Next.js frontend...")

    # Guardian should handle process management
    print(f"[VizHealth] Frontend needs restart (guardian will handle)")
    return True

# ============================================================================
# Complete Health Check
# ============================================================================

async def check_visualization_health() -> Dict[str, any]:
    """
    Run complete health check of visualization pipeline
    Returns: {
        'healthy': bool,
        'components': {
            'websocket': {'status': bool, 'message': str},
            'frontend': {'status': bool, 'message': str},
            'snapshot_api': {'status': bool, 'message': str}
        },
        'timestamp': str
    }
    """
    results = {}

    # Check all components concurrently
    ws_health, ws_msg = await check_websocket_server()
    frontend_health, frontend_msg = await check_frontend()
    snapshot_health, snapshot_msg = await check_snapshot_api()

    results = {
        'healthy': ws_health and frontend_health and snapshot_health,
        'components': {
            'websocket': {'status': ws_health, 'message': ws_msg},
            'frontend': {'status': frontend_health, 'message': frontend_msg},
            'snapshot_api': {'status': snapshot_health, 'message': snapshot_msg}
        },
        'timestamp': datetime.now().isoformat()
    }

    return results

# ============================================================================
# Guardian Integration
# ============================================================================

async def visualization_health_check_for_guardian() -> Tuple[bool, str]:
    """
    Simplified health check for guardian.py integration
    Returns: (all_healthy, summary_message)

    Usage in guardian.py:
        from orchestration.visualization_health import visualization_health_check_for_guardian

        async def check_visualization():
            healthy, message = await visualization_health_check_for_guardian()
            if not healthy:
                logging.warning(f"[Guardian] Visualization unhealthy: {message}")
                # Trigger recovery...
            return healthy
    """
    results = await check_visualization_health()

    if results['healthy']:
        return True, "All visualization components healthy"
    else:
        unhealthy = [
            name for name, data in results['components'].items()
            if not data['status']
        ]
        return False, f"Unhealthy: {', '.join(unhealthy)}"

# ============================================================================
# CLI for Manual Testing
# ============================================================================

async def main():
    """Run health check from command line"""
    print("\n" + "="*60)
    print("Visualization Pipeline Health Check")
    print("="*60 + "\n")

    results = await check_visualization_health()

    # Print results
    for component, data in results['components'].items():
        symbol = "✓" if data['status'] else "✗"
        status_str = "HEALTHY" if data['status'] else "UNHEALTHY"
        print(f"{symbol} {component.upper()}: {status_str}")
        print(f"  → {data['message']}")

    print("\n" + "="*60)
    if results['healthy']:
        print("✓ ALL COMPONENTS HEALTHY")
    else:
        print("✗ SOME COMPONENTS UNHEALTHY")
    print("="*60 + "\n")

    return results['healthy']

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
