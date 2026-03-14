# OBJECTIVES -- Email Bridge

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_Email_Bridge.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Email_Bridge.md
BEHAVIORS:      ./BEHAVIORS_Email_Bridge.md
ALGORITHM:      ./ALGORITHM_Email_Bridge.md
VALIDATION:     ./VALIDATION_Email_Bridge.md
IMPLEMENTATION: ./IMPLEMENTATION_Email_Bridge.md
SYNC:           ./SYNC_Email_Bridge.md

IMPL:           mind-mcp :: runtime/bridges/email/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **MIND reads all emails** -- The citizen's AI partner has complete visibility into every email the human receives and sends. Email is the universal communication substrate. Without it, MIND sees only the channels the human remembers to share. With it, MIND has ambient awareness of the human's professional and personal communication landscape.

2. **Universal provider coverage via IMAP/SMTP** -- Any email provider that supports IMAP works. Gmail, Outlook, Yahoo, iCloud, ProtonMail (via Bridge), Zoho, FastMail, OVH, Infomaniak, self-hosted -- all of them. No provider left behind. IMAP is the universal filet that guarantees 100% coverage regardless of the provider's proprietary API story.

3. **Progressive capability enrichment via native APIs** -- Where available, native APIs (Gmail API, Microsoft Graph) add features that IMAP cannot provide: full-text server-side search, labels/categories, thread grouping, contact sync, calendar integration, draft management. The citizen gets the best experience their provider can deliver.

4. **Seamless connection regardless of provider** -- OAuth for Gmail and Outlook (zero-friction). IMAP credentials for everything else (universal fallback). The user connects once and MIND adapts to whatever level of functionality their provider supports.

5. **Email content feeds the citizen's graph** -- Emails are not stored as dead data. They become stimuli in the citizen's L1 graph -- moments, narratives, relationships. MIND processes email content the same way it processes any other input: through the physics engine, creating nodes, propagating energy, building understanding.

## NON-OBJECTIVES

- **Replacing the user's email client** -- MIND reads email. MIND can send email (replies, forwards, drafts). MIND is not a webmail UI. The human continues using their preferred client.
- **Email marketing / bulk sending** -- This is a 1:1 bridge for the citizen's personal communication. Not a mass-email tool.
- **Archival / backup service** -- MIND processes emails for understanding, not for storage compliance. Old emails decay in the graph like any other content.
- **Cross-citizen email sharing** -- Each citizen's email bridge is private to the 1:1 bond. One citizen cannot access another citizen's emails.
- **Calendar / contacts as primary** -- Calendar and contacts are separate bridges. The email bridge may surface calendar invites or contact info found in emails, but dedicated bridges own those domains.

## TRADEOFFS (canonical decisions)

- When native API richness conflicts with universal availability, choose universal availability. IMAP is the floor; native APIs are the ceiling. Every provider must work at Level 1 minimum.
- When sync speed conflicts with server politeness (rate limits, IMAP throttling), choose server politeness. Getting blocked by the provider is worse than a 5-minute delay.
- When email volume overwhelms the graph, choose selective ingestion over total ingestion. MIND's physics handles decay -- but flooding the graph with spam newsletters is wasteful. Relevance filtering happens before graph ingestion.
- We accept that Level 1 (IMAP-only) providers lack server-side search. The citizen's graph compensates: once emails are ingested as nodes, MIND can search them via embeddings.

## SUCCESS SIGNALS (observable)

- Human connects their email in under 2 minutes (OAuth) or under 5 minutes (IMAP credentials)
- MIND can summarize "what happened in email today" for any connected account
- MIND can draft and send a reply to a specific email thread
- New emails appear in the citizen's graph within 5 minutes of arrival
- Level 3 (Gmail) users can search their full inbox via MIND
- Level 1 (IMAP) users can read, send, and organize folders -- no degraded core experience
