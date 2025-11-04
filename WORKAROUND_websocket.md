# WebSocket Server Crash-Loop Workaround

**Issue:** WebSocket server crashes during initialization, preventing dashboard from receiving graph data.

**Confirmed by:** Felix (04:49), Victor (04:43), Iris (04:52)

## Root Causes (from SYNC.md)

1. **SafeMode tripwire** - Server shuts down immediately due to telemetry emission failure
2. **SubEntity loading failure** - `Loaded 0 subentities from FalkorDB` despite thousands existing (label case mismatch?)
3. **WebSocket connection bug** - `control_api.py:2808` WebSocket not accepted properly

## Current Status

- ✅ FalkorDB: Running with rich data (Iris: 689 nodes, Felix: 10 nodes, others: 1000s)
- ✅ Dashboard: Running and rendering correctly
- ❌ WebSocket Server: Crash-looping, not binding to port 8000
- ❌ Graph visualization: No data flowing to dashboard

## Temporary Workaround: Static Snapshot View

Since the WebSocket connection is broken, we can create a **static snapshot viewer** that reads directly from FalkorDB without needing the WebSocket server.

### Option 1: REST API Fallback

Create a simple HTTP endpoint that serves graph snapshots:

```python
# Add to dashboard API route: app/api/consciousness/snapshot/route.ts

import { FalkorDB } from 'falkordb';

export async function GET(request: Request) {
  const db = new FalkorDB({ host: 'localhost', port: 6379 });
  const graph = db.selectGraph('mind-protocol_iris');

  const nodes = await graph.query('MATCH (n) RETURN n LIMIT 100');
  const links = await graph.query('MATCH ()-[r]->() RETURN r LIMIT 100');

  return Response.json({ nodes, links });
}
```

### Option 2: Direct FalkorDB Query (Python Script)

Extract graph snapshot and save as JSON for dashboard to load:

```bash
python3 -c "
from falkordb import FalkorDB
import json

db = FalkorDB(host='localhost', port=6379)
g = db.select_graph('mind-protocol_iris')

# Query nodes
nodes_result = g.query('MATCH (n) RETURN n LIMIT 100')
nodes = [{'id': n.properties.get('node_id', n.id), 'type': n.properties.get('node_type', 'Unknown')} for n in nodes_result.result_set]

# Query links
links_result = g.query('MATCH (s)-[r]->(t) RETURN s.node_id, type(r), t.node_id LIMIT 100')
links = [{'source': row[0], 'type': row[1], 'target': row[2]} for row in links_result.result_set]

print(json.dumps({'nodes': nodes, 'links': links}, indent=2))
" > graph_snapshot.json
```

Then modify dashboard to load from static file as fallback.

## Long-term Fix Required

**For Atlas/Felix to implement:**

1. Fix SubEntity loading query in `falkordb_adapter.py` (case mismatch: 'SubEntity' vs 'Subentity'?)
2. Disable or fix SafeMode tripwire in `safe_mode.py` (too sensitive)
3. Fix WebSocket connection handling in `control_api.py:2808`

## User Impact

**Right now:** Dashboard loads but shows "0 nodes" because WebSocket connection fails.

**Workaround:** Static snapshot would let you see the graph structure, but no real-time updates.

**Ideal:** Fix WebSocket server so real-time visualization works as designed.
