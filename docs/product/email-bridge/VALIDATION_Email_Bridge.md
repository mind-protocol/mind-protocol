# Email Bridge -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Email_Bridge.md
PATTERNS:        ./PATTERNS_Email_Bridge.md
BEHAVIORS:       ./BEHAVIORS_Email_Bridge.md
THIS:            VALIDATION_Email_Bridge.md (you are here)
ALGORITHM:       ./ALGORITHM_Email_Bridge.md
IMPLEMENTATION:  ./IMPLEMENTATION_Email_Bridge.md
SYNC:            ./SYNC_Email_Bridge.md
```

---

## PURPOSE

These invariants define what must hold true for the email bridge to fulfill its purpose. If any CRITICAL invariant is violated, MIND's email awareness is broken. If any HIGH invariant is violated, the experience degrades meaningfully.

---

## INVARIANTS

### V1: Credentials Never Stored in Plaintext

**Why we care:** Email credentials give full access to the human's entire communication history. A plaintext credential leak is a catastrophic privacy violation. This is the hardest security line for the email bridge.

```
MUST:   All credentials (OAuth tokens, IMAP passwords) are encrypted before persistence
MUST:   Decryption happens only at connection time, in memory, never written to disk unencrypted
NEVER:  Credentials appear in logs, config files, environment variables, or unencrypted graph properties
```

### V2: No Email Sent Without Human Instruction

**Why we care:** An AI that sends emails autonomously on behalf of a human is a trust-destroying liability. The human must explicitly instruct or pre-approve every outbound email.

```
MUST:   Every send_email() call traces back to an explicit human instruction or pre-approved rule
NEVER:  MIND sends an email based solely on its own reasoning without human confirmation
```

### V3: Connection Loss Detected Within One Polling Cycle

**Why we care:** Silent connection loss means MIND thinks it has email awareness but does not. The human makes decisions assuming MIND knows about their emails. False awareness is worse than no awareness.

```
MUST:   Failed sync triggers a status change to "error" or "disconnected"
MUST:   MIND is notified of connection loss within one polling cycle (default: 2 minutes)
NEVER:  Bridge reports status="active" when it cannot reach the mail server
```

### V4: Every Connected Provider Works at Level 1 Minimum

**Why we care:** The universal coverage promise. If a user connects their email, it must work. Failure at Level 1 means the user is locked out entirely.

```
MUST:   Any IMAP-capable provider can connect and sync at Level 1
MUST:   Level 1 provides: read messages, send messages, list folders
NEVER:  A provider that supports IMAP fails to connect through the bridge
```

### V5: Emails Cannot Cross Citizen Boundaries

**Why we care:** Each citizen's email bridge is private to their 1:1 bond. Cross-contamination would violate the fundamental privacy model of Mind Protocol.

```
MUST:   Email nodes are scoped to the owning citizen's L1 graph
MUST:   No graph query from citizen A can return email nodes belonging to citizen B
NEVER:  An email ingested for one citizen becomes visible to another citizen
```

### V6: Level Is Correctly Assigned

**Why we care:** Level determines available capabilities. Wrong level means MIND either tries operations that will fail (thinking it has search when it does not) or misses features it could use (treating Gmail as Level 1).

```
MUST:   Gmail OAuth always assigns Level 3
MUST:   Microsoft OAuth always assigns Level 2
MUST:   IMAP credentials always assign Level 1
NEVER:  Level assignment disagrees with actual available capabilities
```

### V7: OAuth Token Refresh Does Not Drop Emails

**Why we care:** OAuth tokens expire every 60 minutes (Google) or 60-90 minutes (Microsoft). If sync stops during refresh, emails are missed during that window. The human assumes continuous coverage.

```
MUST:   Token refresh completes before the current token expires (refresh at 75% of lifetime)
MUST:   If refresh fails, the sync cursor is preserved so no emails are skipped on reconnection
NEVER:  Emails arrive during a token refresh window and are never fetched
```

### V8: Sync Cursor Is Monotonically Advanced

**Why we care:** If the sync cursor goes backward or is lost, the bridge either re-ingests old emails (duplicates in graph) or skips forward (missed emails). Both are data corruption.

```
MUST:   Sync cursor only advances forward (higher UID, later historyId, newer deltaLink)
MUST:   Cursor is persisted atomically with the batch of ingested emails
NEVER:  Cursor advances before messages are successfully ingested (crash = re-fetch, not skip)
```

### V9: Relevance Filter Is Transparent

**Why we care:** If MIND silently discards emails the human considers important, trust is broken. The human must be able to understand why an email was not ingested and override the decision.

```
MUST:   Filter decisions are logged with the reason (spam, newsletter, low relevance)
MUST:   Human can query "what did you filter out today?"
NEVER:  A personal email from a known contact is filtered out as spam
```

### V10: Multiple Accounts Do Not Interfere

**Why we care:** Humans have 2-5 email accounts. A bug that causes account A's sync to block account B's sync, or credentials to cross-contaminate, would make multi-account unusable.

```
MUST:   Each account runs an independent adapter instance
MUST:   Failure of one account does not affect other accounts
NEVER:  Credentials from account A are used to connect to account B
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Email bridge is unusable or dangerous |
| **HIGH** | Major value lost | Core feature broken, trust degraded |
| **MEDIUM** | Partial value lost | Works but experience is worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Credential security | CRITICAL |
| V2 | Human control over sending | CRITICAL |
| V3 | Connection awareness | CRITICAL |
| V4 | Universal provider coverage | HIGH |
| V5 | Citizen privacy boundaries | CRITICAL |
| V6 | Correct capability detection | HIGH |
| V7 | Continuous coverage during refresh | HIGH |
| V8 | Sync integrity (no duplicates, no gaps) | HIGH |
| V9 | Filter transparency | MEDIUM |
| V10 | Multi-account isolation | HIGH |

---

## MARKERS

<!-- @mind:todo Define encryption scheme for credentials in L1 graph (symmetric key derived from citizen identity?) -->
<!-- @mind:escalation V2 needs refinement: what counts as "pre-approved rule"? Auto-reply? Scheduled send? -->
<!-- @mind:proposition Consider V11: rate limiting on outbound sends to prevent abuse if account is compromised -->
