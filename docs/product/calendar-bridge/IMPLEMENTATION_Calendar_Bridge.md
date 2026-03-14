# Calendar Bridge — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Calendar_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Calendar_Bridge.md
PATTERNS:        ./PATTERNS_Calendar_Bridge.md
ALGORITHM:       ./ALGORITHM_Calendar_Bridge.md
VALIDATION:      ./VALIDATION_Calendar_Bridge.md
THIS:            IMPLEMENTATION_Calendar_Bridge.md (you are here)
HEALTH:          ./HEALTH_Calendar_Bridge.md
SYNC:            ./SYNC_Calendar_Bridge.md

IMPL:            mind-mcp/runtime/integrations/calendar/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/runtime/integrations/calendar/
├── __init__.py                                    # Exports: CalendarBridge, CalendarEvent, sync_calendar
├── calendar_event_model_and_normalization.py       # CalendarEvent dataclass + EventAttendee
├── calendar_sync_loop_and_diff.py                 # Main sync loop, diff logic, graph injection
├── provider_base_and_factory.py                   # CalendarProvider ABC + provider_factory()
├── providers/
│   ├── __init__.py
│   ├── google_calendar_api_provider.py            # Google Calendar API v3 integration
│   ├── outlook_graph_calendar_provider.py         # Microsoft Graph calendar (shared token with email)
│   └── caldav_standard_calendar_provider.py       # CalDAV RFC 4791 client
└── tests/
    ├── test_calendar_event_normalization.py        # Unit tests for all three normalizers
    ├── test_calendar_sync_diff_and_apply.py        # Sync loop, diff, graph injection tests
    └── test_caldav_ical_parsing.py                 # CalDAV-specific iCalendar parsing edge cases
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines (est.) | Status |
|------|---------|----------------------|-------|--------|
| `calendar_event_model_and_normalization.py` | Unified event model + attendee model | `CalendarEvent`, `EventAttendee` | ~80 | OK |
| `calendar_sync_loop_and_diff.py` | Sync orchestration: fetch, normalize, diff, apply | `sync_calendar()`, `diff_events()`, `apply_to_graph()` | ~200 | OK |
| `provider_base_and_factory.py` | Abstract provider + factory for instantiation | `CalendarProvider` (ABC), `provider_factory()` | ~60 | OK |
| `google_calendar_api_provider.py` | Google Calendar API v3: fetch, normalize, CRUD | `GoogleCalendarProvider`, `normalize_google()` | ~180 | OK |
| `outlook_graph_calendar_provider.py` | MS Graph calendar: fetch, normalize, shared token | `OutlookCalendarProvider`, `normalize_outlook()` | ~150 | OK |
| `caldav_standard_calendar_provider.py` | CalDAV: REPORT, iCalendar parsing, normalize | `CalDAVProvider`, `normalize_caldav()`, `parse_ical_response()` | ~200 | OK |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Provider Strategy + Pipeline

**Why this pattern:** Three providers share the same sync/diff/apply pipeline but differ in how they fetch and normalize data. The Strategy pattern isolates provider-specific logic behind a common interface. The Pipeline pattern (fetch -> normalize -> diff -> apply) keeps the sync loop clean and testable at each stage.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Strategy | `CalendarProvider` ABC | Each provider implements `fetch_events()` and `normalize()` |
| Pipeline | `sync_calendar()` | Sequential stages with clear data boundaries |
| Factory | `provider_factory()` | Instantiate correct provider from config string |
| Lock | `acquire_sync_lock()` | Prevent concurrent sync per citizen+provider |

### Anti-Patterns to Avoid

- **Provider-specific branching in sync loop**: If `sync_calendar()` ever contains `if provider == "google"`, the abstraction has failed. All provider differences must be behind the `CalendarProvider` interface.
- **God normalizer**: Don't create one `normalize()` function with three code paths. Each provider has its own normalizer file.
- **Eager recurrence expansion**: Don't expand recurring events beyond the sync window. The expansion is bounded by window, not by event count.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Provider | API-specific fetch/normalize logic | Sync loop, diff, graph | `CalendarProvider.fetch_events()`, `CalendarProvider.normalize()` |
| Sync loop | Fetch, diff, apply orchestration | Provider specifics, graph internals | `sync_calendar(citizen_id, provider)` |
| Graph injection | Moment node CRUD, attendee linking | Event fetching, normalization | `apply_to_graph(diff, citizen_id)` |

---

## SCHEMA

### CalendarEvent

```yaml
CalendarEvent:
  required:
    - external_id: str            # Provider-specific unique ID
    - provider: str               # "google" | "outlook" | "caldav"
    - title: str                  # Event summary
    - start_time: datetime        # UTC, timezone-aware
    - end_time: datetime          # UTC, timezone-aware
    - status: str                 # "confirmed" | "tentative" | "cancelled"
  optional:
    - description: str            # Event body/notes
    - all_day: bool               # Default false
    - timezone: str               # IANA timezone, default "UTC"
    - location: str               # Physical location
    - video_call_url: str         # Normalized video call link
    - attendees: list[EventAttendee]
    - organizer: EventAttendee
    - recurrence_id: str          # For instances of recurring events
    - recurrence_rule: str        # RRULE for master event
    - last_modified: datetime
  constraints:
    - end_time >= start_time
    - provider in {"google", "outlook", "caldav"}
    - status in {"confirmed", "tentative", "cancelled"}
```

### SyncState

```yaml
SyncState:
  required:
    - citizen_id: str
    - provider: str
  optional:
    - last_sync_time: datetime
    - sync_token: str             # Provider-specific (Google syncToken, Outlook deltaLink)
    - consecutive_failures: int   # Default 0
    - last_error: str
    - known_event_ids: set[str]   # For CalDAV deletion detection
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `sync_calendar()` | `calendar_sync_loop_and_diff.py` | Scheduler (every 5 minutes) |
| `provider_factory()` | `provider_base_and_factory.py` | Sync loop initialization |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Calendar Sync Flow: Fetch-Normalize-Diff-Apply Pipeline

This flow covers the entire sync cycle from provider API to graph. It transforms raw API responses into moment nodes. This is the only flow in the module -- everything else is a sub-step.

```yaml
flow:
  name: calendar_sync_loop
  purpose: "Sync calendar events from external provider to citizen's L1 graph"
  scope: "Input: provider API. Output: moment nodes + attendee links in graph."
  steps:
    - id: acquire_lock
      description: "Prevent concurrent sync for same citizen+provider"
      file: calendar_sync_loop_and_diff.py
      function: acquire_sync_lock()
      input: "(citizen_id, provider)"
      output: bool
      trigger: "Scheduler fires sync_calendar()"
      side_effects: "Lock key set with TTL"
    - id: fetch_events
      description: "Call provider API to get events in sync window"
      file: "providers/{provider}.py"
      function: "CalendarProvider.fetch_events()"
      input: "(SyncState, TimeWindow)"
      output: "FetchResult (raw events, deleted IDs, sync token)"
      trigger: "Lock acquired"
      side_effects: "HTTP request to external API"
    - id: normalize
      description: "Map raw provider response to unified CalendarEvent model"
      file: "providers/{provider}.py"
      function: "normalize_*()"
      input: "raw API response"
      output: "list[CalendarEvent]"
      trigger: "FetchResult returned"
      side_effects: "None"
    - id: diff
      description: "Compare fetched events against graph state"
      file: calendar_sync_loop_and_diff.py
      function: diff_events()
      input: "(list[CalendarEvent], dict[str, MomentNode], list[str])"
      output: "EventDiff (create, update, delete)"
      trigger: "Normalization complete"
      side_effects: "Graph read query"
    - id: apply
      description: "Write creates/updates/deletes to graph"
      file: calendar_sync_loop_and_diff.py
      function: apply_to_graph()
      input: "(EventDiff, citizen_id)"
      output: "ApplyResult (counts)"
      trigger: "Diff computed"
      side_effects: "Graph write operations, attendee link creation"
    - id: update_state
      description: "Persist sync token and timestamp"
      file: calendar_sync_loop_and_diff.py
      function: update_sync_state()
      input: "(SyncState, FetchResult)"
      output: "SyncState (updated)"
      trigger: "Apply complete"
      side_effects: "State persistence"
  docking_points:
    guidance:
      include_when: "Boundary between external API and internal state; boundary between sync and graph"
      omit_when: "Internal transformations within a single step"
      selection_notes: "Two key docks: API response entry (after fetch) and graph write exit (after apply)"
    available:
      - id: dock_api_response
        type: api
        direction: input
        file: "providers/{provider}.py"
        function: "CalendarProvider.fetch_events()"
        trigger: "HTTP response received"
        payload: "FetchResult"
        async_hook: optional
        needs: "add interceptor for health monitoring"
        notes: "This is where provider failures are first visible"
      - id: dock_normalized_events
        type: event
        direction: output
        file: "providers/{provider}.py"
        function: "normalize_*()"
        trigger: "Normalization complete"
        payload: "list[CalendarEvent]"
        async_hook: not_applicable
        needs: none
        notes: "Good for integrity checks -- are all required fields populated?"
      - id: dock_graph_write
        type: graph_ops
        direction: output
        file: calendar_sync_loop_and_diff.py
        function: apply_to_graph()
        trigger: "Diff applied"
        payload: "ApplyResult (created, updated, deleted counts)"
        async_hook: optional
        needs: "add async hook for event_count_sanity checker"
        notes: "Final boundary -- after this, data is in the graph"
      - id: dock_sync_state
        type: db
        direction: output
        file: calendar_sync_loop_and_diff.py
        function: update_sync_state()
        trigger: "Sync complete"
        payload: "SyncState"
        async_hook: not_applicable
        needs: none
        notes: "sync_freshness checker reads this"
    health_recommended:
      - dock_id: dock_api_response
        reason: "Detects provider failures before they propagate"
      - dock_id: dock_graph_write
        reason: "Verifies events actually reach the graph"
      - dock_id: dock_sync_state
        reason: "sync_freshness checker depends on last_sync_time"
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
calendar/
    └── imports → runtime/integrations/auth/     (OAuth tokens)
    └── imports → runtime/graph/                 (graph operations)
    └── imports → runtime/integrations/email/    (shared MS Graph token store)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `google-api-python-client` | Google Calendar API v3 | `google_calendar_api_provider.py` |
| `msal` or `httpx` | Microsoft Graph API requests | `outlook_graph_calendar_provider.py` |
| `caldav` (python-caldav) | CalDAV protocol client | `caldav_standard_calendar_provider.py` |
| `icalendar` | iCalendar (RFC 5545) parsing | `caldav_standard_calendar_provider.py` |
| `python-dateutil` | Recurrence rule expansion (rrulestr) | `caldav_standard_calendar_provider.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| SyncState | Key-value store (per citizen per provider) | Per citizen+provider | Created on first sync, updated every cycle |
| Sync lock | Distributed lock (Redis or in-memory) | Per citizen+provider | Acquired at cycle start, released at end (TTL: 5 min) |
| OAuth tokens | Shared auth module token store | Per citizen+provider | Managed by auth module, refreshed on 401 |

### State Transitions

```
NO_STATE ──first_sync──> SYNCING ──success──> SYNCED ──interval──> SYNCING
                              |                                       |
                              └──failure──> FAILED ──retry──> SYNCING
                                              |
                                              └──3x_failure──> ALERT_SENT
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Read citizen's calendar configuration (which providers, which calendars)
2. For each configured provider:
   a. Verify OAuth token exists and is valid (via auth module)
   b. Load SyncState from store (or create default)
   c. Register sync_calendar() with scheduler at configured interval
```

### Main Loop (per provider, per citizen)

```
1. Scheduler fires sync_calendar(citizen_id, provider)
2. Acquire lock (skip if held)
3. Fetch events from provider API
4. Normalize to CalendarEvent model
5. Diff against graph state
6. Apply creates/updates/deletes to graph
7. Update SyncState
8. Release lock
```

### Shutdown

```
1. Cancel all scheduled sync tasks
2. Release all held locks
3. Persist any in-flight SyncState
```

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `CALENDAR_SYNC_INTERVAL` | env / config.yaml | `300` (seconds) | How often to poll each provider |
| `CALENDAR_SYNC_WINDOW_DAYS` | env / config.yaml | `30` | How far ahead to sync events |
| `CALENDAR_MAX_CONSECUTIVE_FAILURES` | env / config.yaml | `3` | Failures before alerting citizen |
| `CALENDAR_PROVIDERS` | citizen config | `[]` | List of configured providers per citizen |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| (not yet implemented) | — | `# DOCS: docs/product/calendar-bridge/` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM sync_calendar | `calendar_sync_loop_and_diff.py:sync_calendar()` |
| ALGORITHM fetch_events | `providers/*.py:CalendarProvider.fetch_events()` |
| ALGORITHM normalize_* | `providers/*.py:normalize_*()` |
| ALGORITHM diff_events | `calendar_sync_loop_and_diff.py:diff_events()` |
| ALGORITHM apply_to_graph | `calendar_sync_loop_and_diff.py:apply_to_graph()` |
| BEHAVIOR B1 | `calendar_sync_loop_and_diff.py:sync_calendar()` |
| BEHAVIOR B7 | `outlook_graph_calendar_provider.py` (shared token) |
| VALIDATION V1 | `test_calendar_sync_diff_and_apply.py` |
| VALIDATION V2 | `test_calendar_event_normalization.py` |

---

## MARKERS

<!-- @mind:todo Create all implementation files in mind-mcp repo during S7 -->
<!-- @mind:todo Verify python-caldav library supports REPORT with time-range filter -->
<!-- @mind:proposition Consider shared ProviderBase class across calendar and email bridges -->
