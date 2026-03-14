# Calendar Bridge — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Calendar_Bridge.md
PATTERNS:        ./PATTERNS_Calendar_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Calendar_Bridge.md
THIS:            VALIDATION_Calendar_Bridge.md (you are here)
ALGORITHM:       ./ALGORITHM_Calendar_Bridge.md
HEALTH:          ./HEALTH_Calendar_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Calendar_Bridge.md
SYNC:            ./SYNC_Calendar_Bridge.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, would mean the calendar bridge has failed its purpose. A citizen with a broken calendar bridge is worse than a citizen with no calendar bridge -- stale or incorrect schedule data causes the AI to make wrong predictions, prepare for cancelled meetings, and miss real ones.

---

## INVARIANTS

### V1: Every Source Event Reaches the Graph

**Why we care:** If events are lost during sync, the citizen's schedule is incomplete. Brief Matinal shows a partial day. Meeting prep doesn't fire for unsynced meetings. The human loses trust because the AI "forgot" a meeting that's clearly on the calendar.

```
MUST:   Every non-cancelled event within the sync window that exists in the source calendar
        must have a corresponding moment node in the citizen's L1 graph after a successful sync cycle.
NEVER:  An event is silently dropped because of a normalization error, API pagination bug,
        or unhandled edge case.
```

### V2: Normalized Events Are Provider-Agnostic

**Why we care:** If downstream consumers need provider-specific branching, we've failed. Brief Matinal checking `if provider == "google"` means the normalization layer is leaking. Every additional provider would then require changes in every consumer.

```
MUST:   Every CalendarEvent produced by normalization conforms to the unified schema.
        All required fields (external_id, title, start_time, end_time, provider, status)
        are populated for every event regardless of source provider.
NEVER:  A downstream consumer requires provider-specific code to read or interpret a CalendarEvent.
```

### V3: Cancelled Events Are Removed

**Why we care:** A cancelled meeting that still appears in Brief Matinal or triggers meeting prep is actively harmful. It wastes the human's attention and erodes trust in the system.

```
MUST:   An event deleted or cancelled in the source calendar is marked cancelled in the graph
        within the next sync cycle.
NEVER:  A cancelled event appears as active in any downstream consumer query.
```

### V4: No Concurrent Sync Corruption

**Why we care:** Two sync cycles writing to the same graph simultaneously could create duplicates, miss deletions, or apply diffs out of order. Calendar data has low tolerance for duplicates -- "Team Standup" appearing twice in Brief Matinal is immediately visible and embarrassing.

```
MUST:   At most one sync cycle per citizen per provider runs at any time.
        The sync lock prevents overlap.
NEVER:  Two concurrent syncs for the same citizen+provider produce duplicate moment nodes
        or conflicting graph state.
```

### V5: Token Failure Surfaces, Never Hides

**Why we care:** Silent sync failure is the worst failure mode. The human thinks their calendar is connected. The graph quietly goes stale. Days pass before anyone notices. By then, trust is damaged.

```
MUST:   If OAuth token refresh fails, the citizen is alerted within 3 consecutive failures.
        The failure reason is logged with enough detail to diagnose.
NEVER:  A sync failure is swallowed silently. Never try/except: pass on auth errors.
```

### V6: Recurring Events Expand Correctly

**Why we care:** Most calendar events are recurring. "Weekly Team Standup" is one event in the calendar but the most important meeting of the week -- every week. If recurrence expansion is wrong, the citizen misses preparation for their most predictable meetings.

```
MUST:   Recurring events within the sync window are expanded into individual instances.
        Each instance has its own start_time, end_time, and per-instance modifications.
NEVER:  A recurring event produces only one moment node for the master event.
NEVER:  Expansion runs beyond the sync window (default 30 days), creating unbounded nodes.
```

### V7: Outlook Token Is Shared, Not Duplicated

**Why we care:** Asking the human to authenticate Microsoft twice (once for email, once for calendar) is friction that costs user trust during onboarding. If two separate tokens exist for the same Graph API, token refresh races can invalidate each other.

```
MUST:   Outlook Calendar uses the same Microsoft Graph OAuth token as the email bridge.
        One token store entry, one refresh cycle.
NEVER:  A separate OAuth flow is triggered for Outlook Calendar when the email bridge
        already has a valid Graph token with Calendar.Read scope.
```

### V8: CalDAV Works Without Provider-Specific Code

**Why we care:** The entire value proposition of CalDAV is "one implementation, many servers." If we need special handling for iCloud vs Fastmail vs Nextcloud, we've recreated the N-provider problem CalDAV was supposed to solve.

```
MUST:   The CalDAV provider works with any RFC 4791-compliant server using the same code path.
        No if/elif branches on server vendor.
NEVER:  A CalDAV provider subclass for a specific vendor (AppleCalDAVProvider, FastmailCalDAVProvider).
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizen is schedule-blind or receives wrong schedule |
| **HIGH** | Major value lost | Sync degrades silently or user experience breaks |
| **MEDIUM** | Partial value lost | Reduced efficiency or extra maintenance burden |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Every event reaches the graph | CRITICAL |
| V2 | Provider-agnostic normalized events | HIGH |
| V3 | Cancelled events are removed | CRITICAL |
| V4 | No concurrent sync corruption | HIGH |
| V5 | Token failure surfaces | CRITICAL |
| V6 | Recurring events expand correctly | HIGH |
| V7 | Outlook token is shared | MEDIUM |
| V8 | CalDAV works without vendor-specific code | MEDIUM |

---

## MARKERS

<!-- @mind:todo Write tests for V1 with mock provider returning 50+ events and verifying all reach graph -->
<!-- @mind:todo Write tests for V3 covering Google cancelled status, Outlook @removed, and CalDAV UID disappearance -->
<!-- @mind:escalation V8 may need exceptions for known-broken CalDAV implementations (e.g., some Synology DSM versions) -- need to test against real servers -->
