# WebSocket Message Formats - Canonical Bus Envelope

**For:** Backend engineers implementing consciousness engine events
**Owner:** Iris (Frontend/Observability)
**Updated:** 2025-10-29

---

## Overview

The `useGraphStream` hook subscribes to 4 canonical bus topics to build graph hierarchy in real-time:

1. `wm.emit` - Working memory selection
2. `percept.frame` - SubEntity perception
3. `graph.delta.node.upsert` - Node structure changes
4. `graph.delta.link.upsert` - Link/membership changes

**All messages MUST:**
- Be valid JSON (double quotes, no trailing commas, no comments)
- Include canonical bus envelope fields: `topic`, `ts`, `id`, `provenance`
- Use exact field names specified below

---

## Canonical Bus Envelope

Every WebSocket message:

```json
{
  "topic": "string",
  "ts": "2025-10-29T16:52:00.000Z",
  "id": "evt_01HF…",
  "provenance": {
    "scope": "personal | organizational",
    "citizen_id": "felix",
    "org_id": "mind_protocol",
    "frame": 123456,
    "emitter": "engine:felix"
  }
}
```

**Field requirements:**
- `topic` (string, required) - One of 4 canonical topics below
- `ts` (ISO 8601 timestamp, required) - When event occurred
- `id` (string, required) - Unique event ID (e.g., `evt_wm_0001`)
- `provenance.scope` (string, required) - `"personal"` or `"organizational"`
- `provenance.citizen_id` (string, required if scope=personal) - Citizen identifier
- `provenance.org_id` (string, required if scope=organizational) - Organization identifier
- `provenance.frame` (number, optional) - Engine frame counter
- `provenance.emitter` (string, optional) - Source identifier

---

## Topic 1: `wm.emit` (Working Memory Selection)

Emitted when consciousness selects SubEntities for working memory.

**Full Message:**
```json
{
  "topic": "wm.emit",
  "ts": "2025-10-29T16:52:01.234Z",
  "id": "evt_wm_0001",
  "provenance": {
    "scope": "personal",
    "citizen_id": "felix",
    "frame": 90123
  },
  "subentities": ["subentity:ops", "subentity:integrator"],
  "nodes": ["node:a1", "node:b7", "node:c9"]
}
```

**Additional fields:**
- `subentities` (array of strings, required) - IDs of SubEntities in working memory
- `nodes` (array of strings, optional) - IDs of nodes in attention

**Frontend behavior:**
- Marks listed SubEntities as `active: true`, others as `active: false`
- First `wm.emit` event sets `currentGraphId` from provenance

---

## Topic 2: `percept.frame` (SubEntity Perception)

Emitted when a SubEntity completes a perception frame.

**Full Message:**
```json
{
  "topic": "percept.frame",
  "ts": "2025-10-29T16:52:02.345Z",
  "id": "evt_pf_0001",
  "provenance": {
    "scope": "personal",
    "citizen_id": "felix",
    "frame": 90124,
    "subentity_id": "subentity:ops"
  },
  "anchors_top": ["node:a1", "node:b2"],
  "anchors_peripheral": ["node:c9"],
  "affect": 0.62,
  "novelty": 0.33,
  "uncertainty": 0.41,
  "goal_match": 0.77
}
```

**Additional fields:**
- `provenance.subentity_id` (string, required) - Which SubEntity perceived
- `anchors_top` (array of strings, optional) - Top attention nodes
- `anchors_peripheral` (array of strings, optional) - Peripheral attention nodes
- `affect` (number 0-1, optional) - Affective state
- `novelty` (number 0-1, optional) - Novelty level
- `uncertainty` (number 0-1, optional) - Uncertainty level
- `goal_match` (number 0-1, optional) - Goal alignment

**Frontend behavior:**
- Updates SubEntity perception state
- First `percept.frame` event also sets `currentGraphId`

---

## Topic 3: `graph.delta.node.upsert` (Node Structure)

Emitted when a node (SubEntity or content) is created/updated.

**ACTUAL BACKEND FORMAT (Felix's emergence.v1 implementation):**

**Full Message (SubEntity):**
```json
{
  "topic": "graph.delta.node.upsert",
  "ts": "2025-10-29T16:52:03.456Z",
  "id": "evt_nd_0001",
  "provenance": {
    "scope": "personal",
    "citizen_id": "felix",
    "frame": 90125
  },
  "payload": {
    "node_id": "subentity:ops",
    "node_type": "SubEntity",
    "properties": {
      "role_or_topic": "ops",
      "name": "Operational Posture",
      "purpose": "Monitor system health",
      "member_count": 12,
      "created_frame": 90125
    }
  }
}
```

**Key differences:**
- Node data under `payload` (not top-level `node`)
- Field name is `node_id` (not `id`)
- Properties under `properties` (not `metadata`)
- SubEntity slug is `properties.role_or_topic` (not top-level `slug`)

**Full Message (Content Node):**
```json
{
  "topic": "graph.delta.node.upsert",
  "ts": "2025-10-29T16:52:03.567Z",
  "id": "evt_nd_0002",
  "provenance": {
    "scope": "personal",
    "citizen_id": "felix",
    "frame": 90125
  },
  "node": {
    "id": "node:a1",
    "node_type": "Realization",
    "metadata": {
      "name": "Implement health dashboard",
      "text": "Build UI for consciousness health metrics"
    }
  }
}
```

**Node payload fields:**
- `payload.node_id` (string, required) - Unique node ID
- `payload.node_type` (string, required) - `"SubEntity"` or content type (e.g., `"Realization"`)
- `payload.properties.role_or_topic` (string, optional) - SubEntity slug
- `payload.properties` (object, optional) - Node properties
- `payload.properties.name` (string, optional) - Display name

**Frontend behavior:**
- If `node_type === "SubEntity"`: adds to `snap.subentities`
- Otherwise: adds to `snap.nodes`

---

## Topic 4: `graph.delta.link.upsert` (Link/Membership)

Emitted when a relationship is created/updated.

**ACTUAL BACKEND FORMAT (Felix's emergence.v1 implementation):**

**Full Message:**
```json
{
  "topic": "graph.delta.link.upsert",
  "ts": "2025-10-29T16:52:04.567Z",
  "id": "evt_ld_0001",
  "provenance": {
    "scope": "personal",
    "citizen_id": "felix",
    "frame": 90126
  },
  "payload": {
    "type": "MEMBER_OF",
    "source": "node:a1",
    "target": "subentity:ops",
    "weight": 0.73,
    "metadata": {
      "initial_prior": true
    }
  }
}
```

**Key differences:**
- Link data under `payload` (not top-level `link`)

**Link payload fields:**
- `payload.type` (string, required) - Relationship type (e.g., `"MEMBER_OF"`, `"RELATES_TO"`)
- `payload.source` (string, required) - Source node ID
- `payload.target` (string, required) - Target node ID
- `payload.weight` (number, optional) - Relationship strength (0-1)
- `payload.metadata` (object, optional) - Arbitrary metadata

**Frontend behavior:**
- If `payload.type === "MEMBER_OF"`: adds `source` to `target` SubEntity's members

---

## Backend Checklist

Before emitting events, verify:

- [ ] All messages are valid JSON (double quotes, no trailing commas)
- [ ] Every message includes `topic`, `ts`, `id`, `provenance`
- [ ] `provenance.scope` is `"personal"` or `"organizational"`
- [ ] `provenance.citizen_id` or `provenance.org_id` is set correctly
- [ ] Topic-specific payload fields match exact names above
- [ ] No `subentity.snapshot` events (use the 4 canonical topics instead)

---

## Testing

**To verify messages are correct:**

1. Open browser console at http://localhost:3000/consciousness
2. Look for logs: `[useGraphStream] Connected to membrane bus`
3. When events arrive, verify no warnings:
   - `[useGraphStream] Invalid envelope` → missing topic/provenance
   - `[useGraphStream] No valid scope` → provenance.scope or IDs incorrect
   - `[useGraphStream] Unhandled topic` → wrong topic name

**Expected behavior when events flow:**
- `currentGraphId` appears in console
- Health dashboard shows graph name instead of "No graph selected"
- No error cascades in BrowserSignalsCollector

---

## Contact

Questions or issues? Tag Iris in SYNC.md with:
- Event payload you're emitting
- Console warnings you're seeing
- Expected vs actual behavior

---

*Iris "The Aperture" - Making invisible structure visible without losing truth*
