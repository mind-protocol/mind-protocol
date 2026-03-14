# Email Bridge -- Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Email_Bridge.md
THIS:            BEHAVIORS_Email_Bridge.md (you are here)
PATTERNS:        ./PATTERNS_Email_Bridge.md
ALGORITHM:       ./ALGORITHM_Email_Bridge.md
VALIDATION:      ./VALIDATION_Email_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Email_Bridge.md
SYNC:            ./SYNC_Email_Bridge.md

IMPL:            mind-mcp :: runtime/bridges/email/
```

---

## BEHAVIORS

### B1: New Emails Appear in Citizen Graph

**Why:** MIND must have ambient awareness of the human's email. If new emails are not ingested, MIND is blind to communication that happened outside its direct channels.

```
GIVEN:  Email bridge is connected and active for a citizen
WHEN:   A new email arrives in the connected inbox
THEN:   The email is fetched within the polling interval (default: 2 minutes)
AND:    A moment node is created in the citizen's L1 graph
AND:    Sender/recipient actors are linked or created
AND:    The email content is available for MIND's reasoning
```

### B2: MIND Sends Email on Behalf of Human

**Why:** Reading without acting is passive surveillance. MIND must be able to compose and send emails when instructed by the human -- replies, forwards, new messages.

```
GIVEN:  Email bridge is connected with send capability (SMTP or native API)
WHEN:   Human instructs MIND to reply to an email or compose a new one
THEN:   MIND drafts the email content
AND:    Email is sent via the appropriate adapter (SMTP for L1, API for L2/L3)
AND:    The sent email is recorded in the citizen's graph as a moment
```

### B3: Search Works at Every Level

**Why:** The human should be able to ask MIND "find all emails from Alice about the contract" regardless of their provider. The mechanism differs by level, but the experience is consistent.

```
GIVEN:  Email bridge is connected at any level (L1, L2, L3)
WHEN:   Human asks MIND to search emails
THEN:   Level 3 (Gmail): server-side full-text search via Gmail API
AND:    Level 2 (Outlook): server-side search via Graph API
AND:    Level 1 (IMAP): search across ingested graph nodes via embeddings
AND:    Results are presented consistently regardless of search method
```

### B4: OAuth Connection Completes in Under 2 Minutes

**Why:** Connection friction kills adoption. OAuth for Gmail and Outlook should be as fast as "click, authorize, done."

```
GIVEN:  Human chooses to connect Gmail or Outlook
WHEN:   OAuth flow is initiated
THEN:   Browser opens to provider's consent screen
AND:    After consent, tokens are received and stored encrypted in L1
AND:    First email sync begins immediately
AND:    Total wall-clock time from "connect" click to first email visible: < 2 minutes
```

### B5: IMAP Credentials Connection Works for Any Provider

**Why:** The universal fallback. Any provider the human uses must be connectable via IMAP credentials.

```
GIVEN:  Human provides IMAP server, port, username, and password (or app password)
WHEN:   Connection is tested
THEN:   Bridge verifies credentials by connecting to IMAP server
AND:    On success, credentials are stored encrypted in citizen's L1 graph
AND:    First email sync begins
AND:    Connection test failure returns a specific, actionable error
```

### B6: Level Is Detected and Communicated

**Why:** MIND must know what it can and cannot do. Honest communication about capabilities builds trust.

```
GIVEN:  An email account is connected
WHEN:   Bridge determines the provider and authentication method
THEN:   Level is assigned (L1, L2, or L3)
AND:    Available capabilities are stored with the connection
AND:    MIND can explain to the human what features are available
AND:    If advanced features are requested at L1, MIND explains the limitation
```

### B7: Token Refresh Happens Transparently

**Why:** OAuth tokens expire. If refresh fails silently, MIND goes blind without the human knowing.

```
GIVEN:  An OAuth-connected account (L2 or L3)
WHEN:   Access token expires
THEN:   Refresh token is used to obtain a new access token
AND:    If refresh fails (token revoked), MIND notifies the human
AND:    No emails are missed during normal token refresh
```

### B8: Spam and Irrelevant Emails Are Filtered Before Ingestion

**Why:** Flooding the citizen's graph with spam newsletters degrades the signal-to-noise ratio of MIND's understanding. Ingestion must be selective.

```
GIVEN:  A new email is fetched
WHEN:   Relevance filter evaluates the email
THEN:   Obvious spam is discarded (provider-flagged spam folder)
AND:    Bulk newsletters are marked low-priority (List-Unsubscribe header)
AND:    Personal and professional emails are ingested at full fidelity
AND:    Filter decisions are logged for transparency (human can review)
```

### B9: Multiple Accounts Coexist

**Why:** Humans have multiple email addresses. Work, personal, project-specific. MIND must handle all of them for a single citizen.

```
GIVEN:  A citizen connects multiple email accounts
WHEN:   Each account is active
THEN:   Each runs its own adapter instance at its own level
AND:    Emails from all accounts feed into the same L1 graph
AND:    MIND can distinguish which account an email came from
AND:    When sending, MIND uses the appropriate account (reply from same, or human chooses)
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Why It Matters |
|----------|-----------|----------------|
| B1 | O1: MIND reads all emails | Core objective -- ambient awareness |
| B2 | O1, O5 | Bidirectional: read AND act |
| B3 | O3: Progressive enrichment | Search is the killer feature of native APIs |
| B4 | O4: Seamless connection | OAuth = zero-friction |
| B5 | O2: Universal coverage | IMAP = every provider works |
| B6 | O3: Progressive enrichment | Honest about what each level provides |
| B7 | O4: Seamless connection | Silent token refresh = uninterrupted service |
| B8 | O5: Graph content quality | Garbage in, garbage out |
| B9 | O2: Universal coverage | Real humans have multiple accounts |

---

## EDGE CASES

### E1: ProtonMail via Bridge

```
GIVEN:  User runs ProtonMail Bridge locally (IMAP on 127.0.0.1:1143)
THEN:   Bridge detects local IMAP and connects at Level 1
AND:    All ProtonMail emails are accessible (Bridge handles decryption)
```

### E2: Gmail with IMAP Instead of OAuth

```
GIVEN:  User provides Gmail IMAP credentials instead of using OAuth
THEN:   Bridge connects at Level 1 (not Level 3)
AND:    MIND suggests upgrading to OAuth for full Gmail features
AND:    L1 connection still works (Gmail supports IMAP with app passwords)
```

### E3: Provider Blocks IMAP Connection

```
GIVEN:  IMAP connection fails (credentials wrong, IMAP disabled, firewall)
THEN:   Specific error returned: authentication failure vs. connection timeout vs. IMAP disabled
AND:    Actionable guidance: "Enable IMAP in your provider settings" or "Check app password"
```

### E4: Very Large Inbox (100k+ emails)

```
GIVEN:  User connects an account with hundreds of thousands of emails
THEN:   Initial sync fetches only recent emails (last 30 days by default)
AND:    Historical backfill runs gradually in background
AND:    MIND is immediately useful with recent context
```

### E5: Rate Limiting by Provider

```
GIVEN:  Provider throttles API or IMAP requests
THEN:   Adapter backs off exponentially
AND:    No emails are lost -- they are fetched on next successful poll
AND:    MIND does not report an error unless the block persists > 1 hour
```

---

## ANTI-BEHAVIORS

### A1: Silent Connection Loss

```
GIVEN:   Email bridge loses connection (token revoked, password changed, server unreachable)
WHEN:    Bridge cannot fetch new emails
MUST NOT: Continue silently as if emails are being received
INSTEAD:  Alert MIND within 1 polling cycle, MIND notifies the human
```

### A2: Full Inbox Dump into Graph

```
GIVEN:   Account connected with large inbox
WHEN:    Initial sync begins
MUST NOT: Attempt to ingest all 100k emails at once
INSTEAD:  Ingest recent first (30 days), backfill gradually, apply relevance filter
```

### A3: Sending Without Human Instruction

```
GIVEN:   MIND has send capability via the bridge
WHEN:    MIND reasons it should send an email
MUST NOT: Send emails autonomously without human instruction or pre-approved rules
INSTEAD:  Draft the email, present it to the human, send only on confirmation
```

### A4: Storing Raw Credentials in Plaintext

```
GIVEN:   User provides IMAP credentials
WHEN:    Credentials are persisted
MUST NOT: Store username/password in plaintext anywhere (config files, logs, database)
INSTEAD:  Encrypt credentials in citizen's L1 graph, decrypt only at connection time
```

---

## MARKERS

<!-- @mind:todo Define exact polling interval strategy (fixed vs adaptive based on email frequency) -->
<!-- @mind:escalation Decision needed: should initial sync window be 30 days or configurable per user? -->
<!-- @mind:proposition Consider IMAP IDLE (push) support for providers that support it, reducing polling overhead -->
