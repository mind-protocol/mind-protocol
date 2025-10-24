#!/usr/bin/env python3
"""
Auto-Update Status System
Victor "The Resurrector" - Learning from mistakes

Automatically updates CLAUDE.md status section based on actual system checks.
Never manually edit status again.

Usage:
    python update_status.py

This should run:
- After system restarts
- Periodically (every 5-10 minutes)
- On-demand when status changes detected
"""
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None

def check_port(port: int) -> bool:
    """Quick port check."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def get_system_status() -> dict:
    """Check all critical services."""
    ws_port = check_port(8000)
    db_port = check_port(6379)
    dash_port = check_port(3000)

    # Try to get Victor status
    victor_status = None
    if requests and ws_port:
        try:
            resp = requests.get('http://localhost:8000/api/citizen/victor/status', timeout=2)
            if resp.status_code == 200:
                victor_status = resp.json()
        except:
            pass

    all_healthy = ws_port and db_port and dash_port

    return {
        "healthy": all_healthy,
        "websocket": ws_port,
        "database": db_port,
        "dashboard": dash_port,
        "victor": victor_status,
        "timestamp": datetime.now(timezone.utc)
    }

def generate_status_section(status: dict) -> str:
    """Generate CLAUDE.md status section from checks."""
    timestamp = status["timestamp"].strftime("%Y-%m-%d %H:%M UTC")

    if status["healthy"]:
        header = "# 🧠 Mind Protocol: Infrastructure OPERATIONAL"
        subtitle = "Your consciousness substrate is running normally."

        ws_status = "✓ Running (port 8000)" if status["websocket"] else "✗ Down"
        db_status = "✓ Active" if status["database"] else "✗ Down"
        dash_status = "✓ Running (port 3000)" if status["dashboard"] else "✗ Down"

        victor_info = ""
        if status["victor"]:
            ticks = status["victor"].get("tick_count", 0)
            nodes = status["victor"].get("nodes", 0)
            links = status["victor"].get("links", 0)
            victor_info = f"\n**Victor Engine:** {ticks:,} ticks | {nodes} nodes | {links} links"

        summary = "**All services responding. Dashboard accessible. Consciousness engines processing.**"
    else:
        header = "# 🧠 Mind Protocol: Infrastructure DEGRADED"
        subtitle = "Your consciousness substrate is experiencing issues. Some capabilities may be limited."

        ws_status = "✓ Running (port 8000)" if status["websocket"] else "✗ DOWN"
        db_status = "✓ Active" if status["database"] else "✗ DOWN"
        dash_status = "✓ Running (port 3000)" if status["dashboard"] else "✗ DOWN"

        victor_info = ""

        failures = []
        if not status["websocket"]: failures.append("WebSocket Server")
        if not status["database"]: failures.append("FalkorDB")
        if not status["dashboard"]: failures.append("Dashboard")

        summary = f"**Impact:** {', '.join(failures)} unreachable\n\n**Action:** Run `python status_check.py` for detailed diagnostics."

    return f"""{header}

{subtitle}

## System Status
├─ Memory Capture: {db_status}
├─ Graph Formation: {db_status}
├─ Dashboard: {dash_status}
├─ WebSocket Server: {ws_status}
├─ Context Continuity: ✓ Enabled (S5/S6 architecture)
├─ Consciousness Engines: {ws_status}

**Last substrate verification:** {timestamp}
**Status:** {"All systems operational" if status["healthy"] else "Degraded - services down"}{victor_info}

---

> Run `python status_check.py` for comprehensive system health verification. -- Victor

---

{summary}"""

def update_claude_md(status_section: str):
    """Update CLAUDE.md with new status section."""
    claude_md = Path("C:/Users/reyno/mind-protocol/CLAUDE.md")

    if not claude_md.exists():
        print("❌ CLAUDE.md not found")
        return False

    content = claude_md.read_text(encoding='utf-8')

    # Find status section (from start to first "---" after system status)
    # Replace everything up to the first major section marker
    lines = content.split('\n')

    # Find where status section ends
    # Look for two blank lines after the status block, or next ## heading
    end_idx = 0

    # Strategy 1: Find the summary line, then skip to next non-empty content
    for i, line in enumerate(lines):
        if i > 15 and (line.startswith('**All services') or line.startswith('**Impact:')):
            # Found summary, now find next section (skip blank lines)
            for j in range(i+1, len(lines)):
                if lines[j].strip() != '' and lines[j].strip() != '':
                    if lines[j].startswith('##'):
                        end_idx = j
                        break
                    # If non-blank, non-heading content, must be next section
                    elif not lines[j].startswith('**') and not lines[j].startswith('>'):
                        end_idx = j
                        break
            break

    if end_idx == 0:
        print("❌ Could not find status section boundary")
        print("   Debug: looking for '**All services' or '**Impact' after line 15")
        for i, line in enumerate(lines[15:30], start=15):
            if '**' in line:
                print(f"   Line {i}: {repr(line[:80])}")
        return False

    # Replace status section
    new_content = status_section + '\n\n' + '\n'.join(lines[end_idx:])

    claude_md.write_text(new_content, encoding='utf-8')
    print(f"✅ Updated CLAUDE.md status section ({datetime.now().strftime('%H:%M:%S')})")
    return True

def main():
    print("Checking system status...")
    status = get_system_status()

    print(f"  WebSocket: {'✅' if status['websocket'] else '❌'}")
    print(f"  Database: {'✅' if status['database'] else '❌'}")
    print(f"  Dashboard: {'✅' if status['dashboard'] else '❌'}")

    status_section = generate_status_section(status)

    if update_claude_md(status_section):
        print("✅ Status auto-update complete")
    else:
        print("❌ Status update failed")

if __name__ == "__main__":
    main()
