# Calendar Bridge — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Three-provider strategy: Google Calendar API, Outlook via Graph, CalDAV for everything else
- CalendarEvent normalized model (schema defined)
- Sync pipeline architecture: fetch -> normalize -> diff -> apply
- Provider abstraction via CalendarProvider ABC

**What's still being designed:**
- CalendarEvent field list (needs validation against Brief Matinal and meeting prep requirements)
- Attendee matching heuristic (email exact match vs fuzzy name match against actor nodes)
- Deduplication strategy for cross-provider events (title+time matching, false-positive risk)
- CalDAV deletion detection via UID set comparison

**What's proposed (v2+):**
- Webhook/push notification support to reduce polling (Google push, MS subscriptions, CalDAV webpush)
- Bidirectional write support (AI creates/modifies events)
- VTODO/task sync from CalDAV for task-aware scheduling
- Multi-calendar support per provider (personal + work calendars)

---

## CURRENT STATE

Documentation chain is complete (8 files). No code exists yet. The doc chain captures the full architecture: three providers behind a common abstraction, normalized CalendarEvent model, poll-based sync loop with incremental sync via provider tokens, graph injection as moment nodes.

Key architectural decisions are locked:
- CalDAV is the default provider. One implementation covers Apple Calendar, Fastmail, Nextcloud, Synology, Zimbra, and any RFC 4791-compliant server.
- Outlook Calendar reuses the Microsoft Graph OAuth token from the email bridge. No separate OAuth flow.
- Google Calendar gets its own OAuth scope via Google Calendar API v3.
- Poll interval default is 5 minutes. Webhooks are v2.

The target repo is mind-mcp. Code will live at `runtime/integrations/calendar/`.

---

## IN PROGRESS

### Documentation Chain

- **Started:** 2026-03-14
- **By:** Claude Opus (groundwork)
- **Status:** Complete
- **Context:** All 8 doc chain files written. Ready for implementation in S7-S8.

---

## RECENT CHANGES

### 2026-03-14: Documentation Chain Created

- **What:** Full doc chain (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, HEALTH, IMPLEMENTATION, SYNC) for Calendar Bridge module.
- **Why:** Calendar bridge is scheduled for S7-S8 (17-28 March). Docs-first approach per protocol principles.
- **Files:** 8 files in `docs/product/calendar-bridge/`
- **Struggles/Insights:** The CalDAV deletion detection problem is interesting -- CalDAV has no "deleted events" response, so we need to track known UIDs and diff against current responses. This is a clean solution but requires per-sync UID set storage.

---

## KNOWN ISSUES

### Deduplication False Positives

- **Severity:** medium
- **Symptom:** Cross-provider deduplication (A4 in BEHAVIORS) matches by title+time. Common meeting names like "1:1" or "Standup" with similar times could false-match across providers.
- **Suspected cause:** Title-based matching is inherently fuzzy for generic event names.
- **Attempted:** Documented as escalation in BEHAVIORS. Not yet solved.

### CalDAV Server Compatibility Unknown

- **Severity:** medium
- **Symptom:** V8 (CalDAV works without vendor-specific code) is aspirational. Some CalDAV servers (Synology DSM, older Zimbra) have known non-standard behaviors.
- **Suspected cause:** RFC 4791 compliance varies. Need to test against real servers.
- **Attempted:** Noted as escalation in VALIDATION. Will test during implementation.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** Implement calendar bridge in mind-mcp repo

**Where I stopped:** Documentation complete. No code written.

**What you need to understand:**
- This module lives in mind-mcp, NOT in mind-protocol. The doc chain lives here in mind-protocol because this is where architectural docs live, but the code goes in `mind-mcp/runtime/integrations/calendar/`.
- The Outlook provider depends on the email bridge's Microsoft Graph token. If the email bridge isn't built yet, implement Outlook with its own token store and refactor to shared token later.
- CalDAV is the fastest to implement (~2 days). Google is the most effort (~1 week). Outlook is nearly free if Graph token already exists from email bridge.

**Watch out for:**
- `python-caldav` library quality varies. Test against iCloud, Fastmail, and Nextcloud CalDAV endpoints before declaring CalDAV "done."
- Google Calendar's `singleEvents=True` parameter expands recurring events server-side. Without it, you get RRULE strings and must expand client-side. Use `singleEvents=True`.
- Microsoft Graph's calendarView endpoint also expands recurrences. The `/events` endpoint does not. Use `/calendarView`.

**Open questions I had:**
- Should the CalendarEvent model include a `category` field (work/personal)? Some calendars support it, others don't.
- How does the meeting prep subsystem discover that it should fire? Does it poll graph moment nodes, or does the calendar bridge emit an event?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full documentation chain for Calendar Bridge (8 files). Architecture: three providers (Google Calendar API, Outlook via Graph, CalDAV standard) behind a unified CalendarEvent model, syncing to L1 graph as moment nodes. No code yet. Ready for implementation during S7-S8 (17-28 March). Estimated effort: ~1.5 weeks total.

**Decisions made:**
- CalDAV as default (covers Apple, Fastmail, Nextcloud, etc.) -- standard-first approach
- Outlook shares Microsoft Graph token with email bridge -- one OAuth, two data sources
- Poll-based sync at 5-minute intervals (webhooks are v2)
- 30-day sync window with bounded recurrence expansion

**Needs your input:**
- Confirm the implementation order: CalDAV first (fastest, broadest), then Google, then Outlook?
- Do you want meeting prep to be a separate module or embedded in the calendar bridge?
- CalDAV server test targets: iCloud, Fastmail, Nextcloud -- any others?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: All docs written, no implementation exists yet. Implementation starts S7.

### Tests to Run

```bash
# No tests yet -- tests will live at:
pytest mind-mcp/runtime/integrations/calendar/tests/
```

### Immediate (S7: 17-21 March)

- [ ] Create `runtime/integrations/calendar/` directory structure in mind-mcp
- [ ] Implement CalendarEvent dataclass and EventAttendee
- [ ] Implement CalDAV provider (~2 days)
- [ ] Implement sync loop and diff logic
- [ ] Unit tests for CalDAV normalization and sync diff

### Next (S8: 24-28 March)

- [ ] Implement Google Calendar provider with OAuth flow
- [ ] Implement Outlook Calendar provider (shared Graph token)
- [ ] Integration tests with real provider accounts
- [ ] Health check implementation (sync_freshness_checker, provider_availability_checker)

### Later

- [ ] Webhook/push notification support (v2)
- [ ] Bidirectional write support (AI modifies calendar)
- [ ] Multi-calendar support per provider
- IDEA: Shared ProviderBase class across calendar and email bridges to reduce duplication

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the architecture. The CalDAV-as-IMAP analogy is strong and the three-provider strategy is clean. The deduplication problem is the one area that needs real-world testing to validate.

**Threads I was holding:**
- Brief Matinal depends on this module. The CalendarEvent schema should be validated against what Brief Matinal actually needs before implementation.
- Meeting prep needs a trigger mechanism. The calendar bridge syncs events to graph, but something needs to watch the clock and fire prep 15 minutes before events. That's probably a separate scheduler concern, not the bridge's job.
- The email bridge in mind-mcp may or may not exist by S7. If it doesn't, the Outlook provider needs its own Graph token management (refactored later).

**Intuitions:**
- CalDAV will be easier than expected. The `python-caldav` library handles most of the RFC 4791 complexity.
- Google Calendar will take the full week. OAuth setup, consent screen, API quotas, testing with real data.
- The biggest risk is not the providers but the graph injection -- making sure moment nodes are correctly linked to actor nodes for attendees.

**What I wish I'd known at the start:**
The interplay between calendar bridge, email bridge, and Brief Matinal is tight. These three modules should probably be designed together rather than in sequence. But that ship has sailed for S7-S8.

---

## POINTERS

| What | Where |
|------|-------|
| Target code location | `mind-mcp/runtime/integrations/calendar/` |
| Shared auth module | `mind-mcp/runtime/integrations/auth/` |
| Email bridge (shared Graph token) | `mind-mcp/runtime/integrations/email/` |
| Brief Matinal (primary consumer) | `docs/product/brief-matinal/` |
| CalDAV RFC | RFC 4791 (https://www.rfc-editor.org/rfc/rfc4791) |
| iCalendar RFC | RFC 5545 (https://www.rfc-editor.org/rfc/rfc5545) |
| Google Calendar API | https://developers.google.com/calendar/api/v3/reference |
| Microsoft Graph Calendar | https://learn.microsoft.com/en-us/graph/api/resources/calendar |
