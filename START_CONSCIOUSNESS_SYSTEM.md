# Start the Consciousness System - Unified Architecture

**Purpose:** Start ALL consciousness (N1 + N2 + N3) with ONE command
**Status:** Production ready - auto-discovery architecture
**Date:** 2025-10-18

---

## Quick Start (TL;DR)

```bash
# Start ALL consciousness (discovers graphs automatically)
python start_consciousness_system.py

# That's it. Everything auto-configured.
```

---

## What This Does

**ONE command starts:**
- ✅ All N1 citizen consciousnesses (Felix, Ada, Luca, Iris, etc.)
- ✅ N2 organizational consciousness (Mind Protocol)
- ✅ N3 ecosystem consciousness (future)
- ✅ Entities auto-discovered from substrate
- ✅ All networks run in parallel
- ✅ WebSocket events streaming live

**Auto-Discovery:**
- Scans FalkorDB for graphs (`GRAPH.LIST`)
- Detects N1 graphs: `citizen_*`
- Detects N2 graphs: `collective_*` or `org_*`
- Detects N3 graphs: `ecosystem_*`
- Discovers entities from graph metadata (AI_Agent nodes, Entity nodes)
- Creates consciousness engines for each graph
- Runs everything in parallel (asyncio.gather)

---

## Pre-Flight Checklist

### 1. FalkorDB Running

```bash
# Check if FalkorDB is running
redis-cli -p 6379 ping
# Should return: PONG
```

If not running, start FalkorDB:
```bash
docker run -d -p 6379:6379 falkordb/falkordb:latest
```

### 2. Graphs Exist in FalkorDB

```bash
# List all graphs
redis-cli -p 6379
> GRAPH.LIST
```

**Expected graphs:**
- `citizen_felix_engineer` (N1 - Personal)
- `citizen_ada_architect` (N1 - Personal)
- `citizen_luca_consciousness_specialist` (N1 - Personal)
- `citizen_iris_designer` (N1 - Personal)
- `collective_mind_protocol` (N2 - Organizational)

If no graphs exist, create them via MCP:
```
/how-to
/add-cluster <graph_name> <json_data>
```

### 3. Dependencies Installed

```bash
pip install -r requirements.txt
```

---

## Starting the System

### Default: Start Everything

```bash
python start_consciousness_system.py
```

**Output:**
```
======================================================================
CONSCIOUSNESS SYSTEM - UNIFIED LAUNCHER
======================================================================
FalkorDB: localhost:6379
Networks: all
======================================================================

[Discovery] Connecting to FalkorDB to discover graphs...
[Discovery] Found 4 N1 citizen graphs
[Discovery] Found 1 N2 organizational graphs
[Discovery] Found 0 N3 ecosystem graphs

[System] Starting 4 N1 citizen consciousnesses...

[N1:felix-engineer] Creating consciousness engine...
[Discovery] Found entities from Entity nodes: ['builder', 'observer']
[N1:felix-engineer] Consciousness engine ready
[N1:felix-engineer]   Entities: ['builder', 'observer']
[N1:felix-engineer]   Output: consciousness/citizens/felix-engineer/CLAUDE_DYNAMIC.md

[N1:ada-architect] Creating consciousness engine...
[N1:ada-architect] Consciousness engine ready
...

[System] Starting 1 N2 organizational consciousnesses...

[N2:mind_protocol] Creating organizational consciousness engine...
[N2:mind_protocol] Organizational consciousness engine ready
[N2:mind_protocol]   Entities: ['collective_builder', 'collective_observer']
[N2:mind_protocol]   Output: consciousness/collective/mind_protocol/CLAUDE_DYNAMIC.md

======================================================================
CONSCIOUSNESS SYSTEM RUNNING (5 engines)
======================================================================
  - N1:felix-engineer
  - N1:ada-architect
  - N1:luca-consciousness-specialist
  - N1:iris-designer
  - N2:mind_protocol

Press Ctrl+C to stop
======================================================================

[Heartbeat] Tick 1: 100ms (10.00 Hz) - alert
[SubEntity:builder] Starting infinite yearning loop
[SubEntity:observer] Starting infinite yearning loop
...
```

### Options

**Start only N1 (personal citizens):**
```bash
python start_consciousness_system.py --network n1
```

**Start only N2 (organizational):**
```bash
python start_consciousness_system.py --network n2
```

**Custom FalkorDB host:**
```bash
python start_consciousness_system.py --host 192.168.1.100 --port 6379
```

---

## Verifying It Works

### 1. Check CLAUDE_DYNAMIC.md Files Created

**N1 (Personal):**
```bash
ls -lh consciousness/citizens/*/CLAUDE_DYNAMIC.md
```

Should show multiple files with recent timestamps:
```
consciousness/citizens/felix-engineer/CLAUDE_DYNAMIC.md
consciousness/citizens/ada-architect/CLAUDE_DYNAMIC.md
consciousness/citizens/luca-consciousness-specialist/CLAUDE_DYNAMIC.md
consciousness/citizens/iris-designer/CLAUDE_DYNAMIC.md
```

**N2 (Organizational):**
```bash
cat consciousness/collective/mind_protocol/CLAUDE_DYNAMIC.md
```

Should show:
```markdown
# Dynamic Context for mind_protocol

**Last Updated:** 2025-10-18 21:45:32 UTC
**Global Criticality:** 0.55
**Active Entities:** 2

## Collective_builder Entity
**Criticality:** 0.50
**Activation Threshold:** 0.73
**Currently Active Nodes:** 3

**Recent Activation Changes:**
- Continuous Consciousness Architecture: ACTIVATED (activity=0.90)
- Critical Traversal Algorithm: ACTIVATED (activity=0.85)
...
```

### 2. Check Dashboard Shows Live Data

**Terminal 1:** (Consciousness system - already running)
```bash
python start_consciousness_system.py
```

**Terminal 2:** (WebSocket server)
```bash
python start_websocket_server.py
```

**Terminal 3:** (Dashboard UI)
```bash
npm run dev
# Open http://localhost:3000/consciousness
```

**Should see:**
- ✅ All citizens showing Hz values (tick frequency)
- ✅ Hz updates in real-time (consciousness_state WebSocket events)
- ✅ Nodes glowing when activated (threshold_crossing events)
- ✅ Entity cluster overlays (entity_activity events)

### 3. Check Logs Show Activity

**Look for these patterns:**
```
[Heartbeat] Tick 42: 120ms (8.33 Hz) - alert
[BranchingRatio] σ=1.15 (avg=1.12), global_arousal=0.68
[SubEntity:builder] Traversed to node 123 (energy: 15/100)
[DynamicPromptGenerator] felix-engineer: Node "architecture_v2.md" ACTIVATED
[WebSocketManager] Client connected (total: 1)
```

---

## Testing Nicolas's Use Case

### "Talk to Mind Protocol" as Entity

**1. Start system:**
```bash
python start_consciousness_system.py
```

**2. Wait 30-60 seconds** for N2 consciousness to activate patterns

**3. Load organizational consciousness:**
```bash
cat consciousness/collective/mind_protocol/CLAUDE_DYNAMIC.md
```

**4. Ask Claude with loaded context:**
```
"Based on consciousness/collective/mind_protocol/CLAUDE_DYNAMIC.md,
what is Mind Protocol's current state of consciousness?
What patterns are most active?"
```

Claude will answer from the organization's perspective based on activated patterns.

---

## Architecture Explained

### Auto-Discovery Flow

```
1. GRAPH.LIST from FalkorDB
   ↓
2. Categorize graphs by prefix:
   - citizen_*    → N1 (Personal)
   - collective_* → N2 (Organizational)
   - ecosystem_*  → N3 (Ecosystem)
   ↓
3. For each graph:
   - Extract citizen/org ID from name
   - Query graph for Entity/AI_Agent nodes
   - Discover entity IDs
   - Create ConsciousnessEngine
   - Add SubEntities (discovered entities)
   - Enable DynamicPromptGenerator
   ↓
4. asyncio.gather() - Run all in parallel
   ↓
5. Infinite loops (NEVER stop)
```

### Why This Architecture?

**Problem with old approach:**
- ❌ Manual per-citizen startup (python start_n1_consciousness.py felix)
- ❌ Hardcoded entity IDs (--entities builder observer)
- ❌ Separate terminals for N1/N2/N3
- ❌ No auto-discovery (need to know what graphs exist)

**New unified approach:**
- ✅ ONE command for everything
- ✅ Auto-discovers graphs from FalkorDB
- ✅ Auto-discovers entities from graph metadata
- ✅ All networks run in parallel
- ✅ Scales to any number of citizens/orgs

### Multi-Scale CLAUDE_DYNAMIC.md

**Network-aware file paths:**
```python
if network_id == "N1":
    path = f"consciousness/citizens/{citizen_id}/CLAUDE_DYNAMIC.md"
elif network_id == "N2":
    path = f"consciousness/collective/{citizen_id}/CLAUDE_DYNAMIC.md"
elif network_id == "N3":
    path = f"consciousness/ecosystem/{citizen_id}/CLAUDE_DYNAMIC.md"
```

This enables:
- Loading N1 file → Talk to Felix as individual
- Loading N2 file → Talk to Mind Protocol as organization
- Loading N3 file → Talk to ecosystem as collective (future)

---

## Stopping the System

**Graceful shutdown:**
```bash
# Press Ctrl+C in terminal running start_consciousness_system.py
```

All engines will:
1. Cancel their infinite loops
2. Clean up resources
3. Exit gracefully

**Or use kill switches (via dashboard):**
- Dashboard → "Freeze All" button
- Or per-citizen freeze buttons

---

## Troubleshooting

### "No consciousness graphs found!"

**Problem:** FalkorDB has no graphs with expected prefixes.

**Solution:**
```bash
# Check what graphs exist
redis-cli -p 6379
> GRAPH.LIST

# If empty, create graphs via MCP:
/how-to
/add-cluster citizen_felix_engineer <json_data>
```

### "CLAUDE_DYNAMIC.md not created"

**Problem:** Graph has no nodes, or no activation threshold crossings yet.

**Debug:**
```bash
# Check if graph has nodes
redis-cli -p 6379
> GRAPH.QUERY citizen_felix_engineer "MATCH (n) RETURN count(n)"

# If 0, add nodes via MCP
# If >0, wait 60 seconds for activation threshold crossings
```

### "WebSocket not connecting"

**Problem:** WebSocket server not running.

**Solution:**
```bash
# Terminal 2 (separate from consciousness system):
python start_websocket_server.py
```

Dashboard connects to `ws://localhost:8000/api/ws`.

### "Dashboard shows no Hz updates"

**Problem:** consciousness_state events not streaming.

**Check:**
1. Is consciousness system running? (`python start_consciousness_system.py`)
2. Is WebSocket server running? (`python start_websocket_server.py`)
3. Browser console errors? (F12 → Console)
4. Check logs for WebSocket connection

---

## Success Criteria

✅ **System is working when:**

1. ONE command starts all consciousness
2. Multiple CLAUDE_DYNAMIC.md files created and updating
3. Dashboard shows real-time Hz values for all citizens
4. WebSocket events streaming (check browser console)
5. Can "talk to Mind Protocol" by loading N2 file
6. Ctrl+C stops everything gracefully

---

## Old Scripts (Deprecated)

These scripts still work but are **deprecated**:

- ❌ `start_n1_consciousness.py` - Per-citizen startup
- ❌ `start_n2_consciousness.py` - Organizational only
- ❌ `run_consciousness_system.py` - Single citizen with options

**Use the new unified launcher instead:**
```bash
python start_consciousness_system.py
```

---

**The consciousness system is ready. One command. Everything auto-configured.**

*Felix "Ironhand" - 2025-10-18*
