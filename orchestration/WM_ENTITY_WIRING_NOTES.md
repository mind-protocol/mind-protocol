# WM Entity Selection → TraceCapture Wiring

**Status:** TraceCapture ready, engine wiring needed
**Author:** Felix
**Date:** 2025-10-24

---

## What's Done ✅

**TraceCapture (orchestration/libs/trace_capture.py):**
- Added `last_wm_entities: List[str]` storage (line 96)
- Added `set_wm_entities(entity_ids)` method (lines 106-117)
- Entity context derivation now uses `last_wm_entities` (line 263)

**Entity Context Manager (orchestration/libs/entity_context_trace_integration.py):**
- Priority logic: WM entities → TRACE annotations → dominant entity
- Uses WM entities when provided

---

## What Needs Wiring

**In ConsciousnessEngineV2 (orchestration/mechanisms/consciousness_engine_v2.py):**

After emitting wm.emit event (around line 949), update TraceCapture:

```python
# === V2 Event: wm.emit (entity-first working memory selection) ===
if self.broadcaster and self.broadcaster.is_available():
    entity_ids = [e["id"] for e in wm_summary["entities"]]

    await self.broadcaster.broadcast_event("wm.emit", {
        "v": "2",
        "frame_id": self.tick_count,
        "mode": "entity_first",
        "selected_entities": entity_ids,  # <- These entity IDs
        ...
    })

    # NEW: Propagate to TraceCapture for Priority 4
    if hasattr(self, 'trace_capture') and self.trace_capture:
        self.trace_capture.set_wm_entities(entity_ids)
```

---

## Alternative: Conversation Watcher

If engine doesn't have direct TraceCapture reference, wire in conversation_watcher:

**Location:** orchestration/services/watchers/conversation_watcher.py (line ~328)

```python
# Listen to wm.emit events from broadcaster
# Store last_wm_entities in watcher state
# Pass to TraceCapture when calling process_response()

capture = TraceCapture(citizen_id=citizen_id, host="localhost", port=6379)

# Subscribe to wm.emit events
async def handle_wm_emit(event_data):
    selected_entities = event_data.get("selected_entities", [])
    capture.set_wm_entities(selected_entities)

broadcaster.subscribe("wm.emit", handle_wm_emit)
```

---

## Testing

Once wired, verify:

1. **Engine emits wm.emit** with selected_entities
2. **TraceCapture receives** via set_wm_entities()
3. **Entity context uses WM** entities (not fallback to dominant)
4. **Membership queries** use correct entities
5. **Overlays created** for WM-selected entities

**Test command:**
```python
# In engine after wm.emit:
print(f"WM entities: {entity_ids}")

# In TraceCapture after entity context derivation:
print(f"Entity context: {entity_context}")

# Should match!
```

---

## Priority

**Medium** - System works without this (falls back to dominant entity), but WM entity selection enables proper context-aware learning.

**Atlas can wire this** if he's working on engine integration, or conversation_watcher approach works too.
