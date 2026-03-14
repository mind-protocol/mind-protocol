# Calendar Bridge — Algorithm: Multi-Provider Calendar Sync Pipeline

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
THIS:            ALGORITHM_Calendar_Bridge.md (you are here)
VALIDATION:      ./VALIDATION_Calendar_Bridge.md
HEALTH:          ./HEALTH_Calendar_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Calendar_Bridge.md
SYNC:            ./SYNC_Calendar_Bridge.md

IMPL:            mind-mcp/runtime/integrations/calendar/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The calendar bridge runs a periodic sync loop per configured provider. Each cycle fetches events from the provider API, normalizes them into CalendarEvent objects, diffs against the graph's current state, and applies creates/updates/deletes as moment node operations. The same loop handles all three providers (Google, Outlook, CalDAV) through a provider abstraction that maps provider-specific responses to the unified event model.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| MIND knows your schedule | B1, B4, B5 | The sync loop is the mechanism that makes schedule awareness real |
| Three providers, uniform model | B2, B6, B7 | Provider abstraction + normalization produce uniform CalendarEvents |
| Calendar feeds downstream | B3 | Graph injection enables meeting prep and Brief Matinal |

---

## DATA STRUCTURES

### CalendarEvent (normalized)

```
CalendarEvent:
    external_id: str               # Provider-specific unique ID
    provider: str                  # "google" | "outlook" | "caldav"
    title: str                     # Event summary/subject
    description: str | None        # Event body/notes
    start_time: datetime           # UTC, timezone-aware
    end_time: datetime             # UTC, timezone-aware
    all_day: bool                  # True for date-only events
    timezone: str                  # IANA timezone (e.g., "Europe/Paris")
    location: str | None           # Physical location or room name
    video_call_url: str | None     # Normalized video call link (Meet, Teams, Zoom)
    attendees: list[EventAttendee] # Normalized attendee list
    organizer: EventAttendee | None
    status: str                    # "confirmed" | "tentative" | "cancelled"
    recurrence_id: str | None      # For expanded instances of recurring events
    recurrence_rule: str | None    # RRULE string for the master event
    last_modified: datetime        # When the event was last changed at source
    raw_provider_data: dict | None # Original response for debugging (not injected into graph)
```

### EventAttendee

```
EventAttendee:
    name: str | None               # Display name
    email: str                     # Email address (primary key for matching)
    rsvp: str                      # "accepted" | "declined" | "tentative" | "needs_action" | "unknown"
    is_organizer: bool
```

### SyncState

```
SyncState:
    citizen_id: str
    provider: str
    last_sync_time: datetime       # When we last synced
    sync_token: str | None         # Provider-specific incremental sync token
    consecutive_failures: int      # For alerting logic
    last_error: str | None
```

---

## ALGORITHM: sync_calendar_loop

### Step 1: Acquire Lock

Prevent concurrent sync for the same citizen+provider. If a previous cycle is still running, skip this cycle.

```
FUNCTION acquire_sync_lock(citizen_id: str, provider: str) -> bool:
    lock_key = f"calendar_sync:{citizen_id}:{provider}"
    acquired = try_acquire_lock(lock_key, ttl=300)  # 5-minute TTL
    IF NOT acquired:
        log.warning(f"Sync already running for {citizen_id}:{provider}, skipping")
    RETURN acquired
```

### Step 2: Fetch Events from Provider

Each provider implements the same interface but talks to a different API.

```
FUNCTION fetch_events(provider: CalendarProvider, state: SyncState, window: TimeWindow) -> FetchResult:

    IF provider.type == "google":
        # Google Calendar API v3 — events.list with syncToken or timeMin/timeMax
        IF state.sync_token:
            response = google_api.events.list(calendarId="primary", syncToken=state.sync_token)
        ELSE:
            response = google_api.events.list(
                calendarId="primary",
                timeMin=window.start.isoformat(),
                timeMax=window.end.isoformat(),
                singleEvents=True,        # Expands recurring events
                orderBy="startTime",
            )
        RETURN FetchResult(
            events=response.items,
            deleted_ids=[e.id for e in response.items if e.status == "cancelled"],
            next_sync_token=response.nextSyncToken,
        )

    ELIF provider.type == "outlook":
        # Microsoft Graph API — /me/calendarView with deltaLink
        IF state.sync_token:
            response = graph_api.get(state.sync_token)  # deltaLink is a full URL
        ELSE:
            response = graph_api.get("/me/calendarView", params={
                "startDateTime": window.start.isoformat(),
                "endDateTime": window.end.isoformat(),
            })
        RETURN FetchResult(
            events=response.value,
            deleted_ids=[e.id for e in response.value if "@removed" in e],
            next_sync_token=response.delta_link,
        )

    ELIF provider.type == "caldav":
        # CalDAV — REPORT with time-range filter on VEVENT
        calendar_url = provider.calendar_url
        response = caldav_report(
            url=calendar_url,
            method="REPORT",
            body=build_calendar_query(window.start, window.end),
            headers={"Depth": "1"},
        )
        vevents = parse_ical_response(response.text)
        RETURN FetchResult(
            events=vevents,
            deleted_ids=detect_deletions(state.known_event_ids, vevents),
            next_sync_token=None,  # CalDAV uses ctag/etag, not sync tokens
        )
```

### Step 3: Normalize to CalendarEvent

Each provider response is mapped to the unified CalendarEvent model.

```
FUNCTION normalize_google(raw: dict) -> CalendarEvent:
    RETURN CalendarEvent(
        external_id=raw["id"],
        provider="google",
        title=raw.get("summary", "(No title)"),
        description=raw.get("description"),
        start_time=parse_google_datetime(raw["start"]),
        end_time=parse_google_datetime(raw["end"]),
        all_day="date" in raw["start"],
        timezone=raw["start"].get("timeZone", "UTC"),
        location=raw.get("location"),
        video_call_url=extract_google_video_url(raw),
        attendees=[normalize_google_attendee(a) for a in raw.get("attendees", [])],
        organizer=normalize_google_attendee(raw.get("organizer")),
        status=raw.get("status", "confirmed"),
        recurrence_id=raw.get("recurringEventId"),
        recurrence_rule=raw.get("recurrence", [None])[0],
        last_modified=parse_rfc3339(raw["updated"]),
    )

FUNCTION normalize_outlook(raw: dict) -> CalendarEvent:
    RETURN CalendarEvent(
        external_id=raw["id"],
        provider="outlook",
        title=raw.get("subject", "(No title)"),
        description=raw.get("body", {}).get("content"),
        start_time=parse_outlook_datetime(raw["start"]),
        end_time=parse_outlook_datetime(raw["end"]),
        all_day=raw.get("isAllDay", False),
        timezone=raw["start"].get("timeZone", "UTC"),
        location=raw.get("location", {}).get("displayName"),
        video_call_url=extract_outlook_video_url(raw),
        attendees=[normalize_outlook_attendee(a) for a in raw.get("attendees", [])],
        organizer=normalize_outlook_attendee(raw.get("organizer")),
        status=map_outlook_status(raw.get("showAs")),
        recurrence_id=raw.get("seriesMasterId"),
        recurrence_rule=raw.get("recurrence"),
        last_modified=parse_rfc3339(raw["lastModifiedDateTime"]),
    )

FUNCTION normalize_caldav(vevent: VEvent) -> CalendarEvent:
    RETURN CalendarEvent(
        external_id=vevent.uid,
        provider="caldav",
        title=vevent.summary or "(No title)",
        description=vevent.description,
        start_time=vevent.dtstart.to_utc(),
        end_time=vevent.dtend.to_utc() if vevent.dtend else vevent.dtstart + vevent.duration,
        all_day=isinstance(vevent.dtstart, date) and not isinstance(vevent.dtstart, datetime),
        timezone=str(vevent.dtstart.tzinfo) if vevent.dtstart.tzinfo else "UTC",
        location=vevent.location,
        video_call_url=extract_url_from_description(vevent.description),
        attendees=[normalize_caldav_attendee(a) for a in vevent.attendees],
        organizer=normalize_caldav_attendee(vevent.organizer),
        status=vevent.status.lower() if vevent.status else "confirmed",
        recurrence_id=str(vevent.recurrence_id) if vevent.recurrence_id else None,
        recurrence_rule=str(vevent.rrule) if vevent.rrule else None,
        last_modified=vevent.last_modified.to_utc() if vevent.last_modified else now(),
    )
```

### Step 4: Diff Against Graph State

Compare fetched events with what's already in the graph to determine creates, updates, and deletes.

```
FUNCTION diff_events(
    fetched: list[CalendarEvent],
    graph_events: dict[str, MomentNode],  # external_id -> existing node
    deleted_ids: list[str],
) -> EventDiff:

    to_create = []
    to_update = []
    to_delete = []

    FOR event IN fetched:
        existing = graph_events.get(event.external_id)
        IF existing IS None:
            to_create.append(event)
        ELIF event.last_modified > existing.last_modified:
            to_update.append((event, existing))

    FOR ext_id IN deleted_ids:
        IF ext_id IN graph_events:
            to_delete.append(graph_events[ext_id])

    RETURN EventDiff(create=to_create, update=to_update, delete=to_delete)
```

### Step 5: Apply to Graph

Create moment nodes for new events, update existing ones, mark deleted ones as cancelled.

```
FUNCTION apply_to_graph(diff: EventDiff, citizen_id: str) -> ApplyResult:

    created = 0
    updated = 0
    deleted = 0

    FOR event IN diff.create:
        node = event_to_moment_node(event, citizen_id)
        graph.create_node(node)
        link_attendees_to_actors(event.attendees, node.id, citizen_id)
        created += 1

    FOR (event, existing) IN diff.update:
        update_moment_node(existing, event)
        relink_attendees(event.attendees, existing.id, citizen_id)
        updated += 1

    FOR node IN diff.delete:
        graph.update_node(node.id, status="cancelled")
        deleted += 1

    RETURN ApplyResult(created=created, updated=updated, deleted=deleted)
```

### Step 6: Update Sync State

Persist the sync token and timestamp for the next cycle.

```
FUNCTION update_sync_state(state: SyncState, result: FetchResult) -> SyncState:
    state.last_sync_time = now()
    state.sync_token = result.next_sync_token
    state.consecutive_failures = 0
    state.last_error = None
    persist(state)
    RETURN state
```

### Full Flow: sync_calendar

```
FUNCTION sync_calendar(citizen_id: str, provider: CalendarProvider) -> SyncResult:

    # Step 1: Lock
    IF NOT acquire_sync_lock(citizen_id, provider.type):
        RETURN SyncResult(skipped=True, reason="concurrent_sync")

    TRY:
        # Load state
        state = load_sync_state(citizen_id, provider.type)
        window = TimeWindow(start=now(), end=now() + timedelta(days=30))

        # Step 2: Fetch
        fetch_result = fetch_events(provider, state, window)

        # Step 3: Normalize
        events = [provider.normalize(raw) for raw in fetch_result.events]

        # Step 4: Diff
        graph_events = load_graph_calendar_events(citizen_id, window)
        diff = diff_events(events, graph_events, fetch_result.deleted_ids)

        # Step 5: Apply
        apply_result = apply_to_graph(diff, citizen_id)

        # Step 6: Update state
        update_sync_state(state, fetch_result)

        RETURN SyncResult(
            created=apply_result.created,
            updated=apply_result.updated,
            deleted=apply_result.deleted,
        )

    EXCEPT AuthError:
        # Token expired and refresh failed
        state.consecutive_failures += 1
        IF state.consecutive_failures >= 3:
            alert_citizen(citizen_id, f"Calendar sync failed: {provider.type} needs re-authentication")
        persist(state)
        RAISE

    FINALLY:
        release_sync_lock(citizen_id, provider.type)
```

---

## KEY DECISIONS

### D1: Incremental Sync via Provider Tokens

```
Google: syncToken on Events.list — returns only changes since last sync
Outlook: deltaLink on calendarView — returns only changes since last delta
CalDAV: ctag/etag comparison — detect changes, re-fetch changed events

IF sync_token available:
    Fetch only changes (fast, low bandwidth)
ELSE:
    Full window fetch (first sync or token expired)
```

### D2: Deduplication Strategy for Cross-Provider Events

```
IF same (title + start_time + end_time) within 5-minute tolerance from different providers:
    Keep the event with more metadata (more attendees, has video_call_url, etc.)
    Mark the duplicate with a cross_reference link
ELSE:
    Treat as separate events
```

### D3: CalDAV Deletion Detection

```
CalDAV has no "deleted events" response. Detect deletions by comparing:

known_ids = set of external_ids from last sync (stored in SyncState)
current_ids = set of UIDs in current REPORT response
deleted_ids = known_ids - current_ids

This requires storing the full set of known UIDs per CalDAV sync. Acceptable
because CalDAV calendars rarely exceed a few thousand events.
```

---

## DATA FLOW

```
Provider API (Google / Outlook / CalDAV)
    |
    | raw API response (JSON / iCalendar)
    v
fetch_events()
    |
    | FetchResult (raw events + deleted IDs + sync token)
    v
normalize_*()
    |
    | list[CalendarEvent] (unified schema)
    v
diff_events()
    |
    | EventDiff (create / update / delete)
    v
apply_to_graph()
    |
    | Moment nodes + attendee links in L1 graph
    v
Downstream consumers (Brief Matinal, Meeting Prep, Biometric Scheduler)
```

---

## COMPLEXITY

**Time:** O(F + G) per sync cycle where F = fetched events, G = graph events in window. Incremental sync makes F small after first sync.

**Space:** O(E) where E = total events in the sync window (stored in graph as moment nodes).

**Bottlenecks:**
- First sync for a heavy calendar (1000+ events in 30 days) could be slow. Mitigated by incremental sync on subsequent runs.
- CalDAV deletion detection requires storing all known UIDs. At 10,000 events this is ~200KB -- negligible.
- Attendee matching against actor nodes is O(A * N) where A = attendees, N = actors. Acceptable at L1 scale (one citizen's graph).

---

## HELPER FUNCTIONS

### `extract_google_video_url(raw)`

**Purpose:** Extract video call URL from Google Calendar's conferenceData or hangoutLink fields.

**Logic:** Check `conferenceData.entryPoints` for `entryPointType == "video"`, fall back to `hangoutLink`.

### `extract_outlook_video_url(raw)`

**Purpose:** Extract Teams/Skype URL from Outlook's onlineMeeting or onlineMeetingUrl fields.

**Logic:** Check `onlineMeeting.joinUrl`, fall back to `onlineMeetingUrl`.

### `extract_url_from_description(text)`

**Purpose:** Extract video call URL from CalDAV event description (since CalDAV has no structured conferencing field).

**Logic:** Regex match for known patterns (zoom.us/j/, meet.google.com/, teams.microsoft.com/l/).

### `link_attendees_to_actors(attendees, event_node_id, citizen_id)`

**Purpose:** Create links between event moment node and existing actor nodes for recognized attendees.

**Logic:** For each attendee, search citizen's graph for actor nodes with matching email. If found, create link with trust=0.3 (low -- just shared a meeting). If not found, store raw attendee data on the moment node.

### `detect_deletions(known_ids, current_vevents)`

**Purpose:** CalDAV-specific deletion detection by comparing known UIDs against current response.

**Logic:** Return `known_ids - {v.uid for v in current_vevents}`.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/integrations/auth/` | `get_oauth_token(citizen_id, provider)` | Valid access token (refreshed if needed) |
| `runtime/integrations/auth/` | `refresh_token(citizen_id, provider)` | New access token from refresh token |
| `runtime/graph/` | `graph.create_node(node)` | Node created in L1 graph |
| `runtime/graph/` | `graph.query(citizen_id, type="moment", ...)` | Existing calendar event nodes |
| `runtime/integrations/email/` | Shared token store for Microsoft Graph | Outlook OAuth token |
| Brief Matinal module | Reads moment nodes with type="calendar_event" | (consumer, no direct call) |
| Meeting Prep module | Triggered by event proximity | (consumer, no direct call) |

---

## MARKERS

<!-- @mind:todo Implement CalDAV ctag/etag change detection for efficient polling -->
<!-- @mind:todo Define the attendee-to-actor matching heuristic (email exact match vs fuzzy name match) -->
<!-- @mind:proposition Consider a shared "provider abstraction" base class across calendar and email bridges -->
