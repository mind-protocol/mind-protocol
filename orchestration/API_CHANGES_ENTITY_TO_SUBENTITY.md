# API Changes: Entity → SubEntity Terminology

**Date:** 2025-10-26
**Agent:** Agent 4 (Python Adapters & Scripts Taxonomy Update)
**Status:** Complete

## Overview

Updated REST API endpoints and internal terminology from "Entity" to "SubEntity" to align with TAXONOMY_RECONCILIATION.md §3.

---

## Changed Endpoints

### Membership Endpoint

**Before:**
```
GET /api/entity/{entity_id}/members
```

**After:**
```
GET /api/subentity/{subentity_id}/members
```

**Function Name:**
- `get_entity_members()` → `get_subentity_members()`

---

## Changed Request Parameters

| Old Parameter | New Parameter | Endpoint |
|--------------|---------------|----------|
| `entity_id` | `subentity_id` | `/api/subentity/{subentity_id}/members` |

---

## Changed Response Fields

### `/api/subentity/{subentity_id}/members` Response

**Before:**
```json
{
  "entity_id": "E.architect",
  "count": 42,
  "members": [...]
}
```

**After:**
```json
{
  "subentity_id": "E.architect",
  "count": 42,
  "members": [...]
}
```

---

## Changed Event Types

### WebSocket Events (Telemetry)

| Old Event Type | New Event Type | Description |
|---------------|----------------|-------------|
| `entity.flip` | `subentity.flip` | SubEntity activation flip event |
| `entity_activity` | `subentity_activity` | SubEntity exploration updates |

---

## TypeScript Updates Required (Agent 6)

**Agent 6 must update the following files:**

### 1. Event Type Definitions
**File:** `app/consciousness/types/events.ts`

```typescript
// OLD
export type EventType =
  | 'entity.flip'
  | 'entity_activity'
  | ...

// NEW
export type EventType =
  | 'subentity.flip'
  | 'subentity_activity'
  | ...
```

### 2. WebSocket Types
**File:** `app/consciousness/hooks/websocket-types.ts`

```typescript
// OLD
interface EntityFlipEvent {
  type: 'entity.flip';
  entity_id: string;
  ...
}

// NEW
interface SubEntityFlipEvent {
  type: 'subentity.flip';
  subentity_id: string;
  ...
}
```

### 3. API Fetch Hooks
Update any API hooks that call entity endpoints

### 4. Component Props
Update any component props that use `entityId`

---

## Search Patterns for Agent 6

```bash
# Find all entity_id references in TypeScript
grep -r "entity_id" app/consciousness --include="*.ts" --include="*.tsx"

# Find all entity.flip event types
grep -r "entity\.flip\|entity_activity" app/consciousness --include="*.ts" --include="*.tsx"

# Find all /api/entity/ endpoint calls
grep -r "/api/entity/" app/consciousness --include="*.ts" --include="*.tsx"
```

---

## Files Modified

### Python (Agent 4 - Complete)
- `orchestration/adapters/api/control_api.py` - API endpoint definitions

### TypeScript (Agent 6 - TODO)
- `app/consciousness/types/events.ts` - Event type definitions
- `app/consciousness/hooks/websocket-types.ts` - WebSocket event interfaces
- Any components using entity_id props

---

**End of API Changes Document**
