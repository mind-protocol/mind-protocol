# OBJECTIVES — Calendar Bridge

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_Calendar_Bridge.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Calendar_Bridge.md
BEHAVIORS:      ./BEHAVIORS_Calendar_Bridge.md
ALGORITHM:      ./ALGORITHM_Calendar_Bridge.md
VALIDATION:     ./VALIDATION_Calendar_Bridge.md
HEALTH:         ./HEALTH_Calendar_Bridge.md
IMPLEMENTATION: ./IMPLEMENTATION_Calendar_Bridge.md
SYNC:           ./SYNC_Calendar_Bridge.md

IMPL:           mind-mcp/runtime/integrations/calendar/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **MIND knows your schedule** — The citizen's AI partner has real-time awareness of what the human is doing, when meetings start, when there is free time, and what preparation is needed. Without this, the AI partner is blind to the most structuring element of human daily life.

2. **Three providers cover 100% of calendar users** — Google Calendar API, Microsoft Outlook (via Graph API, shared with email bridge), and CalDAV (Apple Calendar, Fastmail, Nextcloud, Synology, Zimbra, and everything else). No user left out. No fifth provider needed.

3. **Calendar data feeds downstream features** — Brief Matinal (morning briefing), meeting preparation (context assembly from graph before meetings), and biometric-aware scheduling (health data + calendar = "don't schedule deep work at 3pm when your HRV crashes"). The calendar bridge is infrastructure, not a product in itself.

4. **Bidirectional where possible** — Read is the minimum. Write (create/modify events) enables the AI to block focus time, suggest rescheduling based on energy, and create preparation reminders. Write requires higher trust.

## NON-OBJECTIVES

- Building a calendar UI or replacing existing calendar apps
- Supporting calendar sharing or delegation between multiple humans (L1 scope: one human, one citizen)
- Real-time collaborative editing of events (humans use their native calendar app for that)
- Push notification delivery (that's the notification subsystem, not the bridge)
- Historical analytics on past calendar usage (the graph accumulates naturally; no special analytics module)

## TRADEOFFS (canonical decisions)

- When provider-specific richness conflicts with cross-provider consistency, choose consistency. The downstream consumers (Brief Matinal, meeting prep) need a uniform event model, not provider-specific fields.
- When polling frequency conflicts with API rate limits, choose respecting limits. Missing a 5-minute calendar update is acceptable; getting the OAuth token revoked is not.
- When CalDAV edge cases conflict with implementation speed, choose working CalDAV for the 80% case. Synology's non-standard VTODO extensions can wait.
- We accept Google Calendar and Outlook requiring separate OAuth flows because their APIs provide richer data (attendee RSVP status, video call links, room bookings) that CalDAV cannot.

## SUCCESS SIGNALS (observable)

- A new calendar event created in Google Calendar appears in the citizen's graph within the sync interval
- Brief Matinal includes today's meetings with correct times, attendees, and locations
- Meeting preparation fires 15 minutes before a meeting with relevant context from the graph
- CalDAV sync works with Apple Calendar (iCloud), Fastmail, and Nextcloud without provider-specific code
- Outlook calendar sync reuses the Microsoft Graph OAuth token from the email bridge
