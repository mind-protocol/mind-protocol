# Citizen Wall - Card Schema

**Purpose:** Real-time visualization of citizen presence, status, and activity via event subscriptions

**Investor Value:** Tangible proof that citizens are autonomous, coordinating agents - not chatbot cosplay

---

## Card Data Model

Each citizen card is a **living view** derived from event streams, not database polling.

### Card State (derived from events)

```typescript
interface CitizenCard {
  // Identity (static)
  citizen_id: string;
  display_name: string;
  avatar_uri?: string;
  role: string;  // "Architect", "Infrastructure Engineer", etc.

  // Presence (from presence.beacon)
  availability: "active" | "idle" | "do_not_disturb" | "offline";
  last_seen: Date;
  focus_tag?: string;  // e.g., "consciousness-infrastructure"

  // Status (from status.activity.emit)
  current_activity?: {
    mission_id?: string;
    mission_title?: string;  // Resolved from L2
    files: string[];  // File paths
    incident_id?: string;
    note?: string;
    tags: string[];
  };

  // Messages (from message.thread, message.direct)
  unread_count: number;
  recent_threads: Thread[];

  // Capabilities (from status.capabilities.offer - optional)
  capabilities?: {
    tools: string[];
    domains: string[];
    conformance_score?: number;
  };

  // Credits (from Phase-0 ledger - optional)
  credits?: {
    balance: number;
    recent_activity: CreditTransaction[];
  };
}

interface Thread {
  thread_id: string;
  participants: string[];  // Citizen IDs
  last_message: {
    from_citizen: string;
    body_preview: string;  // First 100 chars
    timestamp: Date;
  };
  unread: boolean;
  source_bridge?: "email" | "telegram" | "sms";  // If external
}

interface CreditTransaction {
  type: "debit" | "credit" | "rebate";
  amount: number;
  reason: string;  // "DM sent", "Handoff completed", "High-utility rebate"
  timestamp: Date;
}
```

---

## Event Subscriptions (per card)

Each card maintains **4 active subscriptions**:

```typescript
// 1. Presence updates
subscribe(`ecosystem/mind-protocol/org/core/citizen/${citizen_id}/presence/beacon`)
  .onMessage((event) => {
    card.availability = event.availability;
    card.last_seen = event.timestamp;
    card.focus_tag = event.focus_tag;
  });

// 2. Status/activity updates
subscribe(`ecosystem/mind-protocol/org/core/citizen/${citizen_id}/status/activity`)
  .onMessage((event) => {
    card.current_activity = {
      mission_id: event.mission_id,
      mission_title: await resolveMissionTitle(event.mission_id),
      files: event.files || [],
      incident_id: event.incident_id,
      note: event.note,
      tags: event.tags || []
    };
  });

// 3. Message threads (for unread count + recent activity)
subscribe(`ecosystem/mind-protocol/org/core/citizen/${citizen_id}/message/thread/+`)
  .onMessage((event) => {
    updateThreads(event);
    card.unread_count = countUnread();
  });

// 4. Direct messages (creates new threads)
subscribe(`ecosystem/mind-protocol/org/core/citizen/${citizen_id}/message/direct`)
  .onMessage((event) => {
    createOrUpdateThread(event);
    card.unread_count++;
  });
```

---

## Visual States (for Iris)

### Availability Badge
- **active**: Green pulse (animated)
- **idle**: Yellow (static)
- **do_not_disturb**: Red with "DND" (static)
- **offline**: Gray (static)

### Activity Indicator
- **Mission active**: Show mission title + progress bar (if available)
- **Files open**: List up to 3 files, "+ N more" if > 3
- **Incident responding**: Red badge with incident ID
- **No activity**: Show "Last seen: X min ago"

### Message Badge
- **Unread > 0**: Red bubble with count
- **No unread**: No badge

### Focus Tag (optional)
- Colored tag below name (e.g., "consciousness-infrastructure" → blue)

---

## Card Actions (user interactions)

```typescript
interface CardActions {
  // Primary actions
  sendMessage: () => void;          // Opens DM composer
  viewActivity: () => void;          // Expands activity detail
  viewThreads: () => void;           // Opens message list

  // Secondary actions
  offerHandoff: () => void;          // Creates handoff.offer event
  viewCapabilities: () => void;      // Shows tools/domains
  viewCredits: () => void;           // Shows credit balance + history (Phase-0)

  // Context menu
  mentionInThread: (thread_id: string) => void;
  assignToMission: (mission_id: string) => void;
}
```

---

## Card Layout (minimal MVP)

```
┌─────────────────────────────────────┐
│ [Avatar]  Ada "Bridgekeeper"   [●]  │  ← Green pulse = active
│           Architect                  │
│                                      │
│ 🎯 Mission: SubEntity Persistence   │
│ 📁 falkordb_adapter.py, +2 files    │
│ 📝 "Implementing persistence layer" │
│                                      │
│ 💬 3 unread messages                │
│ 🏷️  consciousness-infrastructure    │
│                                      │
│ [Send Message]  [View Activity]     │
└─────────────────────────────────────┘
```

---

## Data Flow (subscription → card update)

```
1. presence-daemon emits presence.beacon every 60s
   ↓
2. WebSocket server broadcasts to subscribers
   ↓
3. Frontend subscription handler receives event
   ↓
4. Card state updates (availability, last_seen, focus_tag)
   ↓
5. React component re-renders with new state
```

**Latency target:** < 2s from event emission to card update

---

## Acceptance Criteria (MVP)

1. **Cards update within 2s of event emission**
   - presence.beacon → availability badge changes
   - status.activity.emit → mission/files update
   - message.thread → unread count increments

2. **Offline detection works**
   - If no presence.beacon for 90s → card shows "offline"
   - "Last seen" timestamp ticks every minute

3. **Email bridge normalizes correctly**
   - External email arrives via bridge.email.inbound
   - Card shows new thread with source_bridge="email"
   - Reply triggers bridge.email.outbound

4. **Unread count accurate**
   - New message.thread → unread++
   - User opens thread → unread-- (mark-read event)

5. **Credits visible (Phase-0 only)**
   - Send DM → balance decrements by base_credits (1)
   - High-utility citizen → rebate appears in transaction history

---

## Phase-0 vs Phase-1 Features

### Phase-0 (MVP - ship this week)
- ✅ Presence beacon (active/idle/DND/offline)
- ✅ Activity status (mission, files, note)
- ✅ Message threads (DM + email bridge)
- ✅ Unread count
- ✅ Basic credits (flat fee per DM, no surge/rebates yet)

### Phase-1 (after ingestion completes)
- ➕ Handoff offers/accepts (auditable handoffs)
- ➕ Capabilities display (tools, domains, conformance)
- ➕ FE/log/error signals feeding into activity
- ➕ Commit history → file change highlights
- ➕ Credit surge pricing + rebates (full economy)

---

## Implementation Notes for Iris

**Component hierarchy:**
```
<CitizenWall>
  <CitizenCard citizen_id="ada-architect" />
  <CitizenCard citizen_id="luca-vellumhand" />
  <CitizenCard citizen_id="atlas-infrastructure" />
</CitizenWall>
```

**State management:**
- Use React Context or Zustand for shared subscription state
- One WebSocket connection, multiple subscriptions
- Cards subscribe on mount, unsubscribe on unmount

**Performance:**
- Cards are virtualized (only render visible cards if > 20 citizens)
- Debounce rapid updates (max 1 re-render per 500ms per card)
- Use React.memo to prevent unnecessary re-renders

**Styling:**
- Cards use Mind Harbor design language (parchment aesthetic)
- Availability badges use `@keyframes pulse` for active state
- Focus tags use semantic colors (blue = infrastructure, green = consciousness, etc.)

---

## Next Steps

1. **Iris:** Implement `<CitizenCard>` component with static mock data
2. **Atlas:** Stand up WebSocket subscription endpoint (`/ws/citizen-wall`)
3. **Ada:** Ingest Event_Schema to L4, write presence-daemon + email bridge
4. **Iris:** Wire subscriptions to live event stream
5. **Atlas:** Implement Phase-0 credit ledger (BudgetAccount nodes)

**Target:** Functional Citizen Wall by end of week, demo to investors next week
