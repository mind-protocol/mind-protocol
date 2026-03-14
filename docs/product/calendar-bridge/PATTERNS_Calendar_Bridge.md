# Calendar Bridge — Patterns: Standard-First Multi-Provider Calendar Integration

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Calendar_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Calendar_Bridge.md
THIS:            PATTERNS_Calendar_Bridge.md (you are here)
ALGORITHM:       ./ALGORITHM_Calendar_Bridge.md
VALIDATION:      ./VALIDATION_Calendar_Bridge.md
HEALTH:          ./HEALTH_Calendar_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Calendar_Bridge.md
SYNC:            ./SYNC_Calendar_Bridge.md

IMPL:            mind-mcp/runtime/integrations/calendar/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Calendar_Bridge.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/integrations/test_calendar_bridge.py`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Calendar_Bridge.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/integrations/test_calendar_bridge.py`

---

## THE PROBLEM

The AI partner is blind to the most rigid structure in human life: the calendar. Without schedule awareness, the citizen cannot:
- Prepare for meetings (who's attending, what context matters, what happened last time)
- Know when the human is available for deep work vs in back-to-back calls
- Correlate energy/biometric data with schedule patterns
- Generate a morning briefing that accounts for the day's structure

Calendar data is fragmented across providers with incompatible APIs. Google has its own REST API. Microsoft has Graph API. Apple, Fastmail, Nextcloud, Synology, and dozens more use CalDAV -- an open standard from 2007 that still works.

The problem is not "how to talk to calendars" -- that's solved. The problem is "how to normalize heterogeneous calendar data into a single event model the citizen's graph can absorb, with a provider abstraction that keeps downstream consumers ignorant of the source."

---

## THE PATTERN

**CalDAV is the IMAP of calendars.** One implementation covers the entire open-standard ecosystem. Native APIs for the two walled gardens (Google, Microsoft) get richer data. Three providers total. No more.

```
Provider Layer:          GoogleCalendarProvider | OutlookCalendarProvider | CalDAVProvider
                                    ↓                      ↓                     ↓
Normalization Layer:         normalize_google()    normalize_outlook()    normalize_caldav()
                                    ↓                      ↓                     ↓
Unified Event Model:                        CalendarEvent (single schema)
                                                     ↓
Graph Injection:                           event → moment node in L1 graph
                                                     ↓
Downstream Consumers:           Brief Matinal | Meeting Prep | Biometric Scheduler
```

The key insight: **CalDAV handles 80% of providers with one codebase.** Google and Outlook justify native APIs because (a) they're the two biggest providers and (b) their APIs expose data CalDAV cannot (attendee RSVP status, video conferencing links, room resources, recurrence exceptions with metadata). But CalDAV is the default, not the exception.

---

## BEHAVIORS SUPPORTED

- B1 (Schedule Sync) — Provider abstraction enables polling any calendar source and producing the same CalendarEvent model
- B2 (Meeting Preparation) — Normalized events include attendees, which enables graph traversal for context assembly
- B3 (Biometric-Aware Scheduling) — Normalized events include time slots, enabling correlation with wearable energy data
- B4 (Brief Matinal Integration) — Uniform event model means the briefing generator never knows which provider the data came from

## BEHAVIORS PREVENTED

- A1 (Provider Lock-in) — The normalized model prevents any downstream system from depending on Google-specific or Outlook-specific fields
- A2 (N-Provider Sprawl) — CalDAV absorbs the long tail; we never need a "Fastmail provider" or "Nextcloud provider"

---

## PRINCIPLES

### Principle 1: Standard First, Native When Justified

CalDAV covers Apple Calendar (iCloud), Fastmail, Nextcloud, Synology, Zimbra, Radicale, Baikal, SOGo, and any RFC 4791-compliant server. One provider class, one test suite, dozens of services. Google and Outlook get native providers only because their walled-garden APIs offer data CalDAV cannot deliver. If Google opened full CalDAV tomorrow, we would drop the native provider.

### Principle 2: Normalize Early, Enrich in Graph

Raw provider data gets normalized into CalendarEvent at the bridge boundary. Enrichment (linking attendees to citizen nodes, linking locations to space nodes, linking agenda items to narrative nodes) happens in the graph, not in the bridge. The bridge is a data pipeline, not a knowledge engine.

### Principle 3: Shared OAuth Where Possible

Outlook Calendar reuses the Microsoft Graph OAuth token from the email bridge. One OAuth consent screen, one token refresh cycle, two data sources (email + calendar). This reduces user friction and simplifies token management. Google Calendar has its own OAuth scope but follows the same token storage pattern.

### Principle 4: Poll, Don't Push (v1)

Webhooks (Google push notifications, Microsoft subscriptions, CalDAV webpush) are v2. v1 polls on a configurable interval (default: 5 minutes). Polling is simpler to implement, debug, and rate-limit. The 5-minute delay is acceptable for calendar data which changes slowly compared to chat or email.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Google Calendar API v3 | API | Full CRUD for Google Calendar events, attendees, conferencing |
| Microsoft Graph API /me/events | API | Calendar events via same Graph token as email bridge |
| Any CalDAV server (RFC 4791) | PROTOCOL | VEVENT/VTODO via WebDAV PROPFIND/REPORT/MKCALENDAR |
| iCalendar format (RFC 5545) | STANDARD | VEVENT/VTODO/VFREEBUSY format used by CalDAV responses |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind-mcp/runtime/integrations/email/` | Shared Microsoft Graph OAuth token for Outlook Calendar |
| `mind-mcp/runtime/graph/` | Graph injection of normalized events as moment nodes |
| `mind-mcp/runtime/integrations/auth/` | OAuth token storage, refresh, and scoping |
| `docs/product/brief-matinal/` | Primary downstream consumer of calendar events |

---

## INSPIRATIONS

**IMAP/CalDAV parallel.** IMAP became the standard bridge protocol for email because it worked with everything. CalDAV plays the same role for calendars. The mental model is identical: one standard protocol covers the open ecosystem, native APIs cover the walled gardens.

**Unix pipeline philosophy.** The bridge does one thing: fetch calendar data, normalize it, emit CalendarEvents. It does not prepare meetings, generate briefings, or schedule. Those are separate concerns consuming the same normalized data.

---

## SCOPE

### In Scope

- Google Calendar provider with OAuth 2.0 and full event CRUD
- Outlook Calendar provider via Microsoft Graph (shared token with email bridge)
- CalDAV provider supporting any RFC 4791 server
- Normalized CalendarEvent model
- Graph injection as moment nodes with attendee/location links
- Poll-based sync with configurable interval
- Token refresh and error handling per provider

### Out of Scope

- Calendar UI or event editing interface -> human uses their native calendar app
- Push notifications / webhooks (v2) -> polling is sufficient for v1
- Recurring event expansion beyond 30-day window -> expanded on demand
- Multi-user calendar sharing or delegation -> L1 scope, one human
- Free/busy lookup for external contacts -> not needed for L1
- VTODO/task sync -> separate module if needed

---

## MARKERS

<!-- @mind:todo Design CalendarEvent schema with all fields needed by Brief Matinal and meeting prep -->
<!-- @mind:proposition Consider CalDAV VTODO sync for task-aware scheduling -->
<!-- @mind:proposition Webhook/push notification support as v2 to reduce polling load -->
