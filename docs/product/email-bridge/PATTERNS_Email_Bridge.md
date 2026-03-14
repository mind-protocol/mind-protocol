# Email Bridge -- Patterns: IMAP Universal Filet with Progressive Native API Enrichment

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Email_Bridge.md
THIS:            PATTERNS_Email_Bridge.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Email_Bridge.md
ALGORITHM:       ./ALGORITHM_Email_Bridge.md
VALIDATION:      ./VALIDATION_Email_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Email_Bridge.md
SYNC:            ./SYNC_Email_Bridge.md

IMPL:            mind-mcp :: runtime/bridges/email/
```

---

## THE PROBLEM

MIND needs to understand the human's communication landscape. Email remains the universal substrate of digital communication -- every professional interaction, every account confirmation, every invoice, every personal exchange passes through it. Without email visibility, MIND is blind to the majority of the human's daily informational life.

The problem is fragmentation. Gmail has the Gmail API. Microsoft has Graph API. Yahoo has nothing. ProtonMail encrypts everything client-side. Self-hosted mail servers speak IMAP and nothing else. A bridge that only supports Gmail leaves 40% of users behind. A bridge that only supports IMAP misses Gmail's powerful search and thread features.

No single protocol covers everything. But IMAP/SMTP come closest -- they are the lowest common denominator that every email provider implements. The question is not "IMAP or native API?" but "IMAP as floor, native APIs as ceiling."

---

## THE PATTERN

**Three-level progressive capability model.**

Every email account connects at one of three levels. The level is determined by the provider and the authentication method. MIND adapts its behavior to the available capabilities.

```
Level 3 (complete):   Gmail API
                      Full-text search, labels, threads, contacts, drafts, push notifications
                      Auth: OAuth 2.0

Level 2 (advanced):   Microsoft Graph API
                      Search, calendar, contacts, OneDrive, categories
                      Auth: OAuth 2.0

Level 1 (standard):   IMAP/SMTP
                      Read, send, folders, flags -- no server-side search
                      Auth: IMAP credentials (host/port/user/password or app password)
                      Covers: Yahoo, iCloud, ProtonMail Bridge, Zoho, FastMail,
                              OVH, Infomaniak, self-hosted, everything else
```

The key insight: **the interface layer is identical across all three levels**. The bridge exposes the same operations to the rest of MIND -- `list_messages`, `get_message`, `send_message`, `search`, `list_folders`. The implementation behind each operation varies by level. Level 1 `search` does client-side filtering. Level 3 `search` uses Gmail's full-text search API. The caller does not know or care.

```
                    MIND (caller)
                         |
                    EmailBridge (unified interface)
                    /         |         \
            GmailAdapter  GraphAdapter  IMAPAdapter
               (L3)          (L2)          (L1)
```

---

## BEHAVIORS SUPPORTED

- B1 (New emails ingested) -- Adapters poll or receive push notifications per their level
- B2 (Email content becomes graph stimuli) -- Unified message format feeds into graph ingestion
- B3 (MIND sends replies) -- Adapters handle send via native API or SMTP
- B4 (Search works at every level) -- Level-appropriate search: server-side (L2/L3) or client-side (L1)
- B5 (Connection flow adapts to provider) -- OAuth for L2/L3, credentials form for L1

## BEHAVIORS PREVENTED

- A1 (Provider lock-in) -- IMAP floor prevents any single provider from being required
- A2 (Silent degradation) -- MIND knows its level and communicates what it can/cannot do

---

## PRINCIPLES

### Principle 1: IMAP Is the Universal Filet

IMAP/SMTP support is not the backup plan. It is the primary strategy. Every email provider on earth supports IMAP (ProtonMail via their Bridge app, iCloud via app passwords, even legacy providers). Building IMAP first means 100% provider coverage from day one. Native APIs are enrichment, not foundation.

This is the opposite of how most email integrations are built (Gmail first, then "we'll add others later" which never happens). We build the universal layer first, then add the fancy features for providers that support them.

### Principle 2: Adapter Isolation

Each provider level is a separate adapter class with the same interface. No `if provider == "gmail"` scattered through the codebase. The adapter encapsulates all provider-specific logic: auth, message retrieval, search, sending, folder management. Adding a new Level 2 provider (e.g., Yahoo's future API) means writing one new adapter class. Nothing else changes.

### Principle 3: Level Transparency

MIND knows what level it is operating at and communicates this honestly. If a user asks MIND to "search all emails for invoices from 2024" on a Level 1 account, MIND says "I can search emails I have already ingested into your graph, but I cannot search your full server-side inbox. For that, connect via Gmail or Outlook." No silent failure. No pretending IMAP has capabilities it lacks.

### Principle 4: Ingestion Over Storage

The email bridge does not create an email archive. It ingests emails into the citizen's L1 graph as stimuli -- moments, narratives, contacts as actors. The graph physics handle relevance, decay, and organization. The bridge fetches, the graph absorbs. If the human needs their full email archive, they use their email client.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| IMAP server | PROTOCOL | Universal email read access |
| SMTP server | PROTOCOL | Universal email send access |
| Gmail API (googleapis.com) | API | Level 3 features: search, labels, threads |
| Microsoft Graph API (graph.microsoft.com) | API | Level 2 features: search, calendar, contacts |
| OAuth tokens | CREDENTIAL | Stored encrypted in citizen's L1 graph |
| IMAP credentials | CREDENTIAL | Host, port, user, app password -- encrypted in L1 |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `runtime/bridges/` (mind-mcp) | Bridge infrastructure, base adapter class |
| `runtime/auth/` (mind-mcp) | OAuth flow management, token refresh |
| L1 graph (citizen brain) | Where email content is ingested as nodes |
| L4 registry | Citizen identity verification before bridge activation |
| MCP membrane | `send` tool for outbound emails, `media` for attachments |

---

## SCOPE

### In Scope

- IMAP connection, authentication, polling, message retrieval
- SMTP connection, authentication, sending
- Gmail API adapter (OAuth, search, labels, threads, drafts)
- Microsoft Graph adapter (OAuth, search, calendar integration)
- Unified message format across all levels
- Email-to-graph ingestion pipeline
- Relevance filtering before ingestion (spam/newsletter detection)
- Credential storage (encrypted in citizen L1 graph)
- Connection management (reconnect, token refresh, error recovery)

### Out of Scope

- Webmail UI -- MIND is not a mail client
- Calendar bridge -- separate module at `docs/product/calendar-bridge/`
- Contact sync as primary -- contacts extracted from emails feed into L1, but dedicated contact bridge is separate
- Email migration between providers
- POP3 -- deprecated protocol, IMAP covers all POP3 use cases
- Email encryption/decryption (PGP, S/MIME) -- v2 consideration

---

## MARKERS

<!-- @mind:todo Define exact OAuth scopes needed for Gmail API (readonly vs full access) -->
<!-- @mind:todo Determine ProtonMail Bridge detection strategy (local IMAP on 127.0.0.1:1143) -->
<!-- @mind:proposition Consider Level 2.5 for Yahoo (partial API but limited) -->
<!-- @mind:escalation Decision needed: should MIND have full send access by default, or require explicit human approval per-send? -->
