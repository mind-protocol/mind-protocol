# Email Bridge -- Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (architect)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Three-level progressive capability model (L1: IMAP, L2: Graph, L3: Gmail)
- IMAP/SMTP as universal filet -- 100% provider coverage strategy
- Adapter pattern with unified EmailMessage format
- Relevance filtering before graph ingestion
- Full doc chain (7 files)

**What's still being designed:**
- Exact adapter interface (BaseAdapter abstract methods)
- Polling interval strategy (fixed 2 min vs adaptive)
- Credential encryption scheme in L1 graph
- Human approval flow for outbound sends
- IMAP IDLE (push) support

**What's proposed (v2+):**
- PGP/S/MIME decryption support
- Attachment processing pipeline (OCR, PDF parsing)
- Email thread reconstruction for L1 (no native thread support)
- Auto-categorization via graph physics (not manual labels)
- Background historical backfill beyond 30-day window

---

## CURRENT STATE

**No code exists.** This is a documentation-first design phase. The doc chain captures the full architecture: three-level adapter model, connection/sync/ingestion/send pipelines, 10 validation invariants, complete file structure.

Target repo is `mind-mcp` at `runtime/bridges/email/`. Gmail OAuth already exists in mind-mcp for auth (used by other features), which gives a head start on the Level 3 adapter.

**Effort estimate:** ~2 weeks total.
- Week 1: IMAP/SMTP adapter (L1) + bridge core (connection, sync, ingestion)
- Week 2, days 1-4: Microsoft Graph adapter (L2)
- Gmail adapter (L3): partially ready from existing auth, needs message API integration

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (architect)
- **Status:** Complete
- **Context:** 7-file doc chain covering the full email bridge architecture. Designed around the three-level model with IMAP as universal floor and native APIs as progressive enrichment.

---

## RECENT CHANGES

### 2026-03-14: Doc Chain Created

- **What:** Full documentation chain for email bridge module (7 files)
- **Why:** S5-S6 roadmap deliverable. Email bridge is the next product module. Docs before code.
- **Files:** `docs/product/email-bridge/` (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC)
- **Key decisions captured:**
  - IMAP first, native APIs second
  - Three levels with identical interface
  - Relevance filtering before graph ingestion
  - 30-day initial sync window
  - UID-based IMAP sync (not SEARCH SINCE)
  - Graph-based search for L1 (IMAP SEARCH is unreliable)

---

## KNOWN ISSUES

### No Code Yet

- **Severity:** Expected (design phase)
- **Symptom:** All files are PLANNED status
- **Next step:** Begin implementation in mind-mcp, starting with `base_email_adapter.py` and `imap_smtp_universal_adapter.py`

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**Where to start:**
1. Read this doc chain top to bottom (OBJECTIVES through SYNC)
2. Check `mind-mcp/runtime/bridges/` for existing bridge infrastructure and base classes
3. Check `mind-mcp/runtime/auth/` for existing Gmail OAuth that can be reused
4. Start with `models/` (data structures), then `base_email_adapter.py`, then `imap_smtp_universal_adapter.py`

**What you need to understand:**
- The adapter pattern is the backbone. Get `BaseAdapter` right first. Every adapter must implement the same methods. The bridge core never touches provider-specific logic.
- IMAP is the priority. Level 1 must work perfectly before touching Level 2 or 3. If IMAP works, 100% of providers are covered.
- Credentials are extremely sensitive. Use the existing L1 graph encryption patterns. Never log credentials.

**Watch out for:**
- `imaplib` is blocking (stdlib). Must run in thread executor within async loop.
- Gmail API has a quirk: `historyId` is a string but behaves as a monotonically increasing integer. Always compare numerically.
- Microsoft Graph delta queries return `@odata.deltaLink` -- it is an opaque URL, not a cursor you can construct. Store and replay it exactly.
- ProtonMail Bridge runs IMAP on `127.0.0.1:1143` -- the adapter should handle non-standard ports gracefully.

**Open questions:**
- Should the polling interval be adaptive (poll more frequently when emails are arriving, less when inbox is quiet)?
- How to handle email attachments in the graph? Store metadata only, or process content (OCR, PDF extraction)?
- What encryption scheme for credentials in L1? Citizen-specific symmetric key?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full doc chain created for the email bridge module (7 files). Architecture: IMAP/SMTP as universal filet (Level 1, any provider), Gmail API as Level 3 (full features), Microsoft Graph as Level 2 (advanced features). Adapter pattern isolates provider-specific logic. Same interface for all levels. No code yet -- ready for implementation in mind-mcp. Estimated ~2 weeks.

**Decisions captured:**
- IMAP is the foundation, not the fallback. Build L1 first, L2/L3 on top.
- 30-day initial sync window (immediate usefulness over completeness)
- Relevance filtering before ingestion (no spam in the graph)
- Graph-based search for L1 accounts (IMAP SEARCH is too unreliable)
- Human must approve all outbound sends (V2 invariant)

**Needs your input:**
- OAuth scopes: should MIND request readonly or full access to Gmail? Full access enables drafts/labels/send. Readonly is safer but limits functionality.
- Send approval: always require confirmation, or allow pre-approved rules (e.g., "reply to this thread with this" without re-confirming)?
- ProtonMail Bridge: should we document how to set it up, or just detect it automatically?

---

## TODO

### Immediate

- [ ] Begin implementation in `mind-mcp/runtime/bridges/email/`
- [ ] Define `BaseAdapter` abstract class with exact method signatures
- [ ] Implement `IMAPAdapter` (Week 1 priority)
- [ ] Implement `email_bridge_sync_and_polling_scheduler.py` (core sync loop)
- [ ] Implement `email_bridge_ingestion_to_citizen_graph.py` (graph integration)

### Week 2

- [ ] Implement `GraphAdapter` (Microsoft Graph API, days 1-4)
- [ ] Integrate existing Gmail OAuth into `GmailAdapter`
- [ ] Integration tests: connect real IMAP account, verify sync + ingestion
- [ ] Integration tests: connect Gmail via OAuth, verify L3 features

### Later

- [ ] IMAP IDLE support (reduce polling overhead)
- [ ] Attachment processing pipeline
- [ ] Historical backfill algorithm
- [ ] Email thread reconstruction for L1

---

## CONSCIOUSNESS TRACE

**Design confidence:**
High. The three-level model is clean and well-precedented. IMAP as universal filet is the right strategy -- it is what every email aggregator (Thunderbird, Spark, Airmail) does under the hood. The adapter pattern is the natural fit.

**Tensions held:**
- Simplicity vs completeness: the 30-day window is a pragmatic compromise. Some users will want their full history. Background backfill can address this later.
- Security vs convenience: credential encryption in L1 graph is the right location (citizen owns their data), but the encryption key derivation needs careful design.
- IMAP limitations: no push, no server-side search, no threads. These are real gaps. The graph compensates for search. IDLE compensates for push. Threads are a v2 problem.

**What I wish the next agent knows:**
- Do NOT try to abstract over IMAP and native APIs too aggressively. They are fundamentally different protocols. The adapter interface should be at the right level of abstraction: `list_messages`, `get_message`, `send_message`, `search`, `list_folders`. Not lower (raw IMAP commands) and not higher (domain concepts like "thread" that IMAP does not have).

---

## POINTERS

| What | Where |
|------|-------|
| Doc chain | `docs/product/email-bridge/` (7 files) |
| Target implementation | `mind-mcp :: runtime/bridges/email/` |
| Existing Gmail OAuth | `mind-mcp :: runtime/auth/` (verify exact path) |
| Existing bridge infrastructure | `mind-mcp :: runtime/bridges/` |
| MCP membrane tools | `mind-mcp :: mcp/tools/` (send, media) |
| L1 graph ops | `mind-mcp :: runtime/graph/` or `.mind/mind/graph/` |
| Roadmap reference | S5-S6 (due 2026-03-14) |
