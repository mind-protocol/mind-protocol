# Calendar Bridge — Behaviors: Observable Effects of Schedule Synchronization

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Calendar_Bridge.md
THIS:            BEHAVIORS_Calendar_Bridge.md (you are here)
PATTERNS:        ./PATTERNS_Calendar_Bridge.md
ALGORITHM:       ./ALGORITHM_Calendar_Bridge.md
VALIDATION:      ./VALIDATION_Calendar_Bridge.md
HEALTH:          ./HEALTH_Calendar_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Calendar_Bridge.md
SYNC:            ./SYNC_Calendar_Bridge.md

IMPL:            mind-mcp/runtime/integrations/calendar/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Calendar Events Appear in Graph After Sync

**Why:** The entire purpose of the bridge. If events don't reach the graph, the citizen is schedule-blind. Brief Matinal has nothing to report. Meeting prep cannot fire. Biometric correlation has no schedule axis.

```
GIVEN:  A human has events in their connected calendar (Google, Outlook, or CalDAV)
WHEN:   The sync cycle runs (poll interval, default 5 minutes)
THEN:   New/modified events appear as moment nodes in the citizen's L1 graph
AND:    Each moment node includes: title, start_time, end_time, location, attendees, description, provider, external_id
AND:    Attendee names are linked to existing actor nodes when a match is found
```

### B2: Provider Differences Are Invisible to Consumers

**Why:** Brief Matinal and meeting prep must not care where an event came from. If they need provider-specific branching, the normalization layer has failed. Uniform data enables uniform downstream logic.

```
GIVEN:  Events synced from Google Calendar, Outlook, and CalDAV
WHEN:   A downstream consumer queries calendar events from the graph
THEN:   All events conform to the same CalendarEvent schema
AND:    The provider field is metadata, not a branching condition
AND:    No consumer needs provider-specific code to read events
```

### B3: Meeting Preparation Fires Before Meetings

**Why:** The citizen's value is anticipation, not reaction. Knowing who you're meeting, what you discussed last time, and what's relevant in the graph transforms a calendar entry into actionable intelligence.

```
GIVEN:  A calendar event with attendees exists in the graph
WHEN:   Current time is within the preparation window (default: 15 minutes before start)
THEN:   The meeting prep subsystem is triggered with the event's attendee list
AND:    Graph traversal assembles context: recent interactions with attendees, shared topics, open items
AND:    The preparation is delivered to the citizen (via chat bridge or app)
```

### B4: Deleted Events Are Removed from Graph

**Why:** Stale events poison downstream consumers. A cancelled meeting that still shows in Brief Matinal erodes trust. The graph must reflect current reality, not historical bookings.

```
GIVEN:  An event previously synced to the graph is deleted or cancelled in the source calendar
WHEN:   The next sync cycle runs
THEN:   The corresponding moment node is marked as cancelled or removed
AND:    Downstream consumers no longer include it in active schedule queries
```

### B5: Recurring Events Expand Within Window

**Why:** A "Weekly Team Standup" is one event in the calendar but N events on the schedule. The graph needs concrete instances (next Monday's standup, not "every Monday forever") for meeting prep to fire at the right time.

```
GIVEN:  A recurring event exists in the source calendar
WHEN:   The sync cycle runs
THEN:   Individual instances within the expansion window (default: 30 days) are created as separate moment nodes
AND:    Each instance has its own start_time, end_time, and can have per-instance modifications (different room, extra attendee)
AND:    Instances beyond the window are not expanded (avoids graph bloat)
```

### B6: OAuth Token Refresh Happens Transparently

**Why:** Expired tokens mean silent sync failure. The human should never see "reconnect your calendar." Token refresh is infrastructure, not a user interaction.

```
GIVEN:  A provider's OAuth access token has expired
WHEN:   The sync cycle attempts to fetch events
THEN:   The refresh token is used to obtain a new access token before the fetch
AND:    The new token is stored in the token store
AND:    If refresh fails (revoked access), an alert is raised to the citizen, not silently swallowed
```

### B7: Outlook Calendar Reuses Email Bridge Token

**Why:** One OAuth consent screen for both email and calendar. Less friction during onboarding. One token refresh cycle instead of two. The human grants Microsoft Graph access once.

```
GIVEN:  The email bridge has an active Microsoft Graph OAuth token with Calendar.Read scope
WHEN:   The calendar bridge initializes for Outlook
THEN:   It reuses the existing Graph token from the email bridge's token store
AND:    No additional OAuth consent is required from the human
AND:    Token refresh is handled by the shared auth module
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | MIND knows your schedule | Core sync loop -- events reach the graph |
| B2 | Three providers, uniform model | Downstream consumers work identically regardless of source |
| B3 | Calendar feeds downstream features | Meeting prep is the highest-value downstream consumer |
| B4 | MIND knows your schedule | Accuracy requires removing cancelled events, not just adding new ones |
| B5 | Calendar feeds downstream features | Recurring events are the majority of most calendars; expanding them enables per-instance prep |
| B6 | Three providers cover 100% | Token failure = provider failure; transparent refresh keeps coverage |
| B7 | Three providers cover 100% | Shared token reduces onboarding friction for Outlook users |

---

## INPUTS / OUTPUTS

### Primary Function: `sync_calendar(provider, citizen_id)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| provider | CalendarProvider | Configured provider instance (Google, Outlook, or CalDAV) |
| citizen_id | str | The citizen whose calendar is being synced |
| sync_window | tuple[datetime, datetime] | Time range to fetch events (default: now to now+30d) |
| last_sync_token | str or None | Opaque token from previous sync for incremental fetch |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| events | list[CalendarEvent] | Normalized events within the window |
| deleted_ids | list[str] | External IDs of events removed since last sync |
| next_sync_token | str | Token for next incremental sync |

**Side Effects:**

- Moment nodes created/updated/cancelled in citizen's L1 graph
- Actor node links created for recognized attendees
- Sync state (last_sync_token, last_sync_time) persisted

---

## EDGE CASES

### E1: All-Day Events Span Timezone Boundaries

```
GIVEN:  An all-day event (no specific time) created in UTC+2
THEN:   The event is stored with the human's local timezone
AND:    Start is 00:00 local, end is 23:59 local
AND:    Brief Matinal displays it as an all-day marker, not a 24-hour block
```

### E2: Attendee Name Does Not Match Any Actor Node

```
GIVEN:  An event attendee email does not match any known actor in the graph
THEN:   The attendee is stored as raw data (name + email) on the moment node
AND:    No phantom actor node is created
AND:    If the attendee appears in 3+ events, a proposition is raised to create an actor node
```

### E3: CalDAV Server Returns Malformed VEVENT

```
GIVEN:  A CalDAV REPORT response contains a VEVENT missing DTSTART
THEN:   The event is skipped with a warning log
AND:    Other events in the response are processed normally
AND:    The malformed event ID is recorded for manual review
```

### E4: Sync Cycle Overlaps With Previous Cycle

```
GIVEN:  A sync cycle is still running when the next poll interval fires
THEN:   The new cycle is skipped (no concurrent syncs per provider per citizen)
AND:    A warning is logged if this happens 3+ times consecutively (indicates interval too short or provider too slow)
```

---

## ANTI-BEHAVIORS

### A1: Provider-Specific Fields Leak to Consumers

```
GIVEN:   An event is synced from Google Calendar
WHEN:    A downstream consumer reads the event from the graph
MUST NOT: The consumer sees Google-specific fields (hangoutLink, conferenceData.entryPoints)
INSTEAD:  Video call URL is in the normalized video_call_url field
```

### A2: Silent Sync Failure

```
GIVEN:   A provider API returns an error or token is expired
WHEN:    The sync cycle runs
MUST NOT: The cycle fails silently, leaving the graph stale with no indication
INSTEAD:  Error is logged, alert is raised after N consecutive failures, graph retains last-known-good state
```

### A3: Graph Bloat From Unbounded Recurrence Expansion

```
GIVEN:   A recurring event with no end date ("every Monday forever")
WHEN:    The sync cycle expands instances
MUST NOT: Expand beyond the 30-day window, creating thousands of moment nodes
INSTEAD:  Expand only within window, re-expand on next sync if window has advanced
```

### A4: Duplicate Events From Multiple Providers

```
GIVEN:   A human has the same event in Google Calendar and Outlook (mirrored calendars)
WHEN:    Both providers sync
MUST NOT: Create two separate moment nodes for the same real-world event
INSTEAD:  Deduplicate by matching on (title + start_time + end_time) within a tolerance window, keeping the richer record
```

---

## MARKERS

<!-- @mind:todo Define the exact CalendarEvent fields needed by Brief Matinal -->
<!-- @mind:todo Define attendee matching strategy against existing actor nodes -->
<!-- @mind:escalation Deduplication strategy (A4) needs validation -- matching by title+time may false-positive on common meeting names -->
