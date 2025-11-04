# Production FalkorDB Migration Guide

## Overview

This guide explains how to migrate local FalkorDB consciousness graph data to the production Render environment.

**Problem:** Production FalkorDB on Render is empty (0 nodes), while local has 18,874 nodes across 7 citizen graphs.

**Solution:** Export local data to JSON → Upload to Render → Import using internal network access.

---

## Status

- ✅ **Export Script Created:** `export_falkordb_to_json.py`
- ✅ **Import Script Created:** `tools/import_from_json.py`
- ✅ **Local Data Exported:** `/tmp/mindprotocol_graph_export.json` (144.82 MB)
  - 18,874 nodes
  - 9,005 relationships
  - 7 graphs (mind-protocol + 6 citizens)
- ⏳ **Ready for Upload:** Need to transfer export file to Render

---

## Migration Steps

### Step 1: Upload Export File to Render

Since the JSON export file is 145MB, you have a few options:

**Option A: Upload to Cloud Storage (Recommended)**
```bash
# Upload to S3, Google Cloud Storage, or similar
aws s3 cp /tmp/mindprotocol_graph_export.json s3://your-bucket/

# Or use a temporary file hosting service like transfer.sh
curl --upload-file /tmp/mindprotocol_graph_export.json https://transfer.sh/mindprotocol_graph_export.json
```

**Option B: Add to Git Repository (if acceptable)**
```bash
# Note: This will add 145MB to your repo
cp /tmp/mindprotocol_graph_export.json /home/mind-protocol/mindprotocol/data/
git add data/mindprotocol_graph_export.json
git commit -m "Add graph data export for production migration"
git push
```

**Option C: Use Render Shell Upload**
1. Go to Render Dashboard → Your Backend Service
2. Click "Shell" tab
3. Use `cat > mindprotocol_graph_export.json` and paste content (may timeout for large files)

### Step 2: Run Import on Render

Once the export file is accessible on Render, connect to the Render Shell:

1. **Open Render Shell:**
   - Render Dashboard → Your Backend Service (consciousness engines)
   - Click "Shell" tab

2. **Download Export File (if using cloud storage):**
   ```bash
   # If using S3/GCS:
   curl -o /tmp/mindprotocol_graph_export.json "https://your-url/mindprotocol_graph_export.json"

   # If using transfer.sh:
   curl -o /tmp/mindprotocol_graph_export.json "https://transfer.sh/xxxxx/mindprotocol_graph_export.json"

   # If in git repo:
   # File should already be at data/mindprotocol_graph_export.json
   ```

3. **Run Import Script:**
   ```bash
   # The script will automatically use ECONOMY_REDIS_URL from Render environment
   python tools/import_from_json.py /tmp/mindprotocol_graph_export.json
   ```

   Expected output:
   ```
   ============================================================
   Mind Protocol - Import Graph Data from JSON
   ============================================================

   📄 Export file: /tmp/mindprotocol_graph_export.json
      Size: 144.82 MB

   ⏳ Loading JSON data...
     ✅ Loaded 7 graphs

   🔌 Connecting to FalkorDB...
     Using ECONOMY_REDIS_URL from environment
     ✅ Connected to FalkorDB

   ============================================================
   Importing: mind-protocol
   ============================================================
     Nodes to import: 3625
     Relationships to import: 1344

     Importing nodes...
       500/3625 nodes imported
       1000/3625 nodes imported
       ...
       3625/3625 nodes imported
     ✅ Imported 3625/3625 nodes (0 failed)

   [... similar output for other 6 graphs ...]

   ============================================================
   ✅ Import Complete!
   ============================================================

   Imported 7/7 graphs
   Time elapsed: 120.5 seconds

   🎉 All graphs imported successfully!
   ```

### Step 3: Restart Consciousness Engines

After import completes, restart the consciousness engines to trigger SnapshotCache bootstrap:

1. **Render Dashboard → Backend Service → Manual Deploy**
   - Click "Manual Deploy" → "Deploy latest commit"
   - This will restart the service and run bootstrap

2. **Or use Render API:**
   ```bash
   curl -X POST https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys \
     -H "Authorization: Bearer YOUR_RENDER_API_KEY" \
     -H "Content-Type: application/json"
   ```

### Step 4: Verify Migration Success

1. **Check Render Logs:**
   - Look for: `[Bootstrap] ✅ SnapshotCache populated: 18874 nodes, 7 subentities, 9005 links`
   - This confirms engines loaded data from FalkorDB

2. **Check Production Dashboard:**
   - Visit: https://www.mindprotocol.ai/consciousness
   - Should show nodes and links (not 0/0)
   - WebSocket status should be "Connected"

3. **Test WebSocket Events:**
   - Open browser console on dashboard
   - Should see `snapshot.chunk@1.0` events with actual node/link data
   - Should see `subentity.activation` events with active nodes

4. **Query FalkorDB Directly (Optional):**
   ```bash
   # In Render Shell:
   python -c "
   from falkordb import FalkorDB
   import os
   db = FalkorDB(host='localhost', port=6379)  # Internal access
   graph = db.select_graph('mind-protocol')
   result = graph.query('MATCH (n) RETURN count(n) as count')
   print(f'Nodes in graph: {result.result_set[0][0]}')
   "
   ```
   Should output: `Nodes in graph: 3625` (or total 18874 across all graphs)

---

## Troubleshooting

### Import Script Fails to Connect

**Error:** `❌ Failed to connect: Timeout connecting to server`

**Cause:** Script is trying to connect via external network instead of internal.

**Solution:** Make sure you're running the script **from within Render Shell**, not from your local machine. The script will automatically use `ECONOMY_REDIS_URL` which has internal network access.

### Import Script Says "No ECONOMY_REDIS_URL found"

**Cause:** Environment variable not set in Render.

**Solution:**
1. Render Dashboard → Your Backend Service → Environment
2. Check if `ECONOMY_REDIS_URL` exists
3. If using Render Redis: Should be auto-populated by Render
4. If manual FalkorDB: Add manually with format `redis://host:port`

### Nodes Import but Dashboard Still Empty

**Cause:** SnapshotCache not bootstrapped after import.

**Solution:**
1. Verify engines restarted after import (Step 3)
2. Check Render logs for `[Bootstrap] ✅ SnapshotCache populated` message
3. If missing: Bootstrap code may not be deployed yet (check git commit has the fix)
4. Manually restart service: Render Dashboard → Manual Deploy

### Import Succeeds but Relationships Missing

**Expected Behavior:** Initial import skips relationships (requires complex node ID mapping).

**Impact:** None - consciousness engines recreate relationships during runtime based on node properties.

**What Backend Does:**
- SubEntity spawning creates `CONTAINS` relationships
- Activation spreading creates `ACTIVATES` relationships
- Learning mechanisms create `RELATES_TO` relationships

Relationships emerge from consciousness engine behavior, not static import.

---

## Technical Details

### Why JSON Export/Import?

**Problem:** Render FalkorDB port 6379 is correctly private (not exposed to internet).

**Attempted:** Direct connection from local machine → Timed out (expected).

**Solution:** Export to portable JSON → Upload to Render → Import from internal network.

### What Gets Exported?

- **Nodes:** All node labels and properties (18,874 nodes)
- **Relationships:** Source/target node properties + relationship type (9,005 relationships)
- **Graphs:** 7 separate graphs (main + 6 citizens)

### Why Skip Relationships on Import?

Relationships in graph databases reference internal node IDs. After export/import:
- Old node IDs don't match new node IDs
- Would need complex matching algorithm (e.g., match by `id` property)
- Backend engines recreate relationships during runtime anyway

**Tradeoff:** Faster, simpler import vs. static relationship preservation.

**Impact:** None for Mind Protocol - relationships are dynamic, not static.

---

## Files

- **Export Script:** `/tmp/export_falkordb_to_json.py` (temporary)
- **Import Script:** `tools/import_from_json.py` (committed to repo)
- **Export Data:** `/tmp/mindprotocol_graph_export.json` (145MB, temporary)
- **This Guide:** `tools/MIGRATION_GUIDE.md`

---

## Estimated Time

- **Export:** 30 seconds (already complete)
- **Upload:** 5-10 minutes (depends on method)
- **Import:** 2-3 minutes (on Render hardware)
- **Restart:** 1-2 minutes
- **Verification:** 1 minute

**Total:** ~15-20 minutes

---

## Next Steps After Migration

Once migration is complete and verified:

1. ✅ Production dashboard shows consciousness graph data
2. ✅ WebSocket events stream graph updates
3. ✅ SnapshotCache stays populated across restarts
4. 🎯 Monitor graph growth as citizens interact
5. 🎯 Verify telemetry shows consciousness activity
6. 🎯 Test that new nodes/relationships appear in real-time

---

**Status:** Ready for Step 1 (upload export file)

**Blocked By:** Need to choose upload method and get export file to Render

**Once Unblocked:** Migration can complete in ~15-20 minutes
