# Chat Bridges -- Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Bridge architecture pattern: stateless transport adapter with canonical message format
- Telegram bridge: LIVE, 795 LOC, polling-based, handling real production traffic
- WhatsApp bridge: LIVE, 274 LOC, WAHA webhook, handling real production traffic
- Voice bridge: LIVE, 385 LOC, WebSocket, handling real production traffic
- Inbound/outbound message flow algorithm (ALGORITHM doc)
- 10 validation invariants (V1-V10)

**What's still being designed:**
- Canonical message Pydantic models (shared types module not yet extracted)
- Shared rate limiter module (rate limiting currently inline per bridge)
- Onboarding flow specifics (token-based vs command-based linking)
- Messenger bridge implementation details
- Discord/Slack/Teams bridge specifics

**What's proposed (v2+):**
- Bridge health dashboard (per-platform throughput, error rates, latency)
- Shared base protocol/interface for bridges (evaluate after 4+ bridges exist)
- Post-launch platforms: WeChat, Line, KakaoTalk, Viber, Matrix, Instagram DM

---

## CURRENT STATE

Three bridges are live in production: Telegram (polling), WhatsApp (WAHA webhook), and Voice (WebSocket). All three follow the same pattern documented in this chain: receive message, authenticate user, route to orchestrator, deliver response. The pattern works. It has been validated by real production traffic.

The doc chain captures this proven pattern and extends it to the four planned bridges: Messenger (S3-S4), Discord (S7-S8), Slack (S9-S10), and Teams (S9-S10). The architecture is designed so that each new bridge is a 2-4 day implementation effort -- a single file that handles platform-specific ceremony while delegating all intelligence to the orchestrator.

No shared types module exists yet. Each bridge currently defines its own internal message format. Extracting `CanonicalMessage` and `CanonicalResponse` as Pydantic models in `shared/` is the first preparatory task before building Messenger.

The Telegram bridge at 795 LOC is in SPLIT territory and should be refactored before adding features. Media handling and keyboard formatting can be extracted to a separate file.

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (groundwork)
- **Status:** Complete
- **Context:** Full 7-file doc chain created for Chat Bridges module. Captures the proven pattern from three live bridges and projects it to four planned bridges. All content is real, based on the existing codebase and platform API documentation.

---

## RECENT CHANGES

### 2026-03-14: Doc Chain Created

- **What:** Created complete documentation chain (7 files) for Chat Bridges module
- **Why:** The pattern for building bridges is proven but undocumented. Four new bridges are planned for S3-S10. The doc chain captures the architecture, algorithm, validation invariants, and implementation plan so that any agent can build a new bridge by reading this chain and the existing code.
- **Files:** `docs/product/chat-bridges/` (7 files: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC)
- **Struggles/Insights:** The three existing bridges prove the pattern works, but they each independently implement canonical message translation. The shared types module is the obvious first extraction before building bridge #4.

---

## KNOWN ISSUES

### Telegram Bridge Over Size Threshold

- **Severity:** medium
- **Symptom:** 795 LOC in a single file, exceeds 700L SPLIT threshold
- **Suspected cause:** Organic growth -- media handling, keyboard rendering, and markdown formatting accumulated in the main bridge file
- **Attempted:** Not yet addressed. Documented for pre-Messenger extraction.

### No Shared Types Module

- **Severity:** medium
- **Symptom:** Each bridge defines its own internal message format. No `CanonicalMessage` Pydantic model exists.
- **Suspected cause:** Bridges were built incrementally. With only 2-3 bridges, the duplication was tolerable.
- **Attempted:** Not yet. Planned as first task before Messenger bridge.

### Messenger 24h Policy Unresolved

- **Severity:** medium
- **Symptom:** Meta requires approved message templates for bot messages sent more than 24h after user's last message. If a citizen needs to reach out proactively, standard text messages will fail.
- **Suspected cause:** Platform policy, not a bug.
- **Attempted:** Not yet. Needs product decision on whether citizens proactively message or only respond.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementing new bridges)

**Where I stopped:** Doc chain is complete. No code changes made in this session. The docs describe both what exists (3 live bridges) and what's planned (4 new bridges).

**What you need to understand:**
The three live bridges are in `mind-mcp/runtime/bridges/`. This doc chain is in `mind-protocol/docs/product/chat-bridges/`. The doc chain lives in the protocol repo because it describes the architectural pattern; the code lives in the runtime repo (mind-mcp). Read the existing Telegram and WhatsApp bridges to understand the pattern concretely before building a new one.

**Watch out for:**
- The Telegram bridge uses polling, not webhooks. Don't assume all bridges use webhooks just because the docs emphasize webhook verification.
- WhatsApp uses WAHA (a self-hosted WhatsApp Web bridge), not the official WhatsApp Cloud API. The webhook format is WAHA-specific.
- Discord uses a WebSocket Gateway for receiving events but REST API for sending. It is a hybrid transport pattern, not pure webhook or pure polling.

**Open questions I had:**
- Should the shared types module (`CanonicalMessage`) be in `mind-mcp/runtime/bridges/shared/` or in a more central location like `mind-mcp/runtime/types/`?
- For onboarding (B9), is the linking flow token-based (human enters a code) or command-based (human sends `/link <mind_id>`)? Nicolas needs to decide.
- Should bridges support proactive messaging (citizen initiates conversation)? This affects Messenger (24h policy), Slack (DM scope), and Teams (proactive installation).

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete doc chain created for Chat Bridges module (7 files). Documents the proven architecture from 3 live bridges (Telegram, WhatsApp, Voice) and projects it to 4 planned bridges (Messenger, Discord, Slack, Teams). Implementation effort: ~2-3 weeks for all four. Pattern is validated; each bridge is a 2-4 day task.

**Decisions made:**
- Bridges are stateless transport adapters. All intelligence in orchestrator.
- Shared types module (`CanonicalMessage`, `CanonicalResponse`) should be extracted before building Messenger.
- Telegram bridge should be split (795 LOC > 700L threshold) before adding features.
- Build order: Messenger (S3-S4) -> Discord (S7-S8) -> Slack+Teams (S9-S10).

**Needs your input:**
- Onboarding flow for new platform users: token-based or command-based linking?
- Should citizens be able to proactively message humans? Affects Messenger 24h policy and Slack DM scope.
- Confirm the build order: Messenger first, or reprioritize?

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Shared types module (`canonical_message_and_response_types.py`) documented but not yet created
- [ ] DOCS->IMPL: Shared rate limiter module documented but not yet extracted
- [ ] IMPL->DOCS: Telegram bridge internals not fully documented (795 LOC, needs audit)

### Tests to Run

```bash
# When bridges have tests (currently in mind-mcp):
pytest mind-mcp/tests/bridges/
```

### Immediate

- [ ] Extract shared types module (`CanonicalMessage`, `CanonicalResponse`, `MediaAttachment`) as Pydantic models
- [ ] Extract shared rate limiter (`rate_limiter_with_token_bucket.py`)
- [ ] Split Telegram bridge: extract media + keyboard formatting (~300 LOC)
- [ ] Build Messenger bridge (S3-S4, estimated 3-4 days)

### Later

- [ ] Build Discord bridge (S7-S8, estimated 2-3 days)
- [ ] Build Slack bridge (S9-S10, estimated 3-4 days)
- [ ] Build Teams bridge (S9-S10, estimated 4-5 days)
- [ ] Parameterized integration test suite (one suite, all bridges)
- IDEA: Bridge health dashboard showing per-platform metrics
- IDEA: After 4+ bridges, evaluate if a Python Protocol type for bridges reduces boilerplate

### Post-Launch

- [ ] WeChat (1 week, China compliance requirements)
- [ ] Line (2-3 days, Japan)
- [ ] KakaoTalk (2-3 days, Korea)
- [ ] Viber (2-3 days, Eastern Europe)
- [ ] Matrix/Element (2-3 days, open protocol)
- [ ] Instagram DM (2-3 days, business accounts only)

### NOT Possible

- Signal: No Bot API. Cannot build a bridge.
- Snapchat: No Bot API. Cannot build a bridge.

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident. The pattern is clean and proven by three live bridges. The doc chain captures the architecture faithfully and the planned bridges are straightforward implementations of the same pattern with platform-specific ceremony.

**Threads I was holding:**
- Discord's hybrid transport (WebSocket Gateway + REST) makes it slightly different from pure webhook bridges. The algorithm still applies but the transport setup in Step 1 and Step 8 differs.
- Slack's Block Kit is significantly richer than other platforms' formatting. The `format_for_platform()` function for Slack will be more complex.
- Teams' Bot Framework SDK is heavier than the other SDKs. It may pull in more dependencies. Worth evaluating `botbuilder-core` size before committing to it vs raw HTTP.

**Intuitions:**
- The shared types module should use Pydantic v2 with strict validation. Canonical messages are the contract between bridges and orchestrator -- they must be validated, not duck-typed.
- Discord will be the most popular bridge after Telegram. Its community features (servers, channels, threads) open possibilities for multi-human citizen interaction that 1:1 bridges don't have.
- Slack and Teams bridges are the B2B entry point. They will need workspace/tenant installation flows that are more complex than consumer platform onboarding.

**What I wish I'd known at the start:**
The existing bridges are in mind-mcp, not mind-protocol. The doc chain lives here (mind-protocol) because it describes the architectural pattern at the protocol level. The implementation lives in the runtime repo (mind-mcp).

---

## POINTERS

| What | Where |
|------|-------|
| Existing Telegram bridge | `mind-mcp/runtime/bridges/telegram/` |
| Existing WhatsApp bridge | `mind-mcp/runtime/bridges/whatsapp/` |
| Existing Voice bridge | `mind-mcp/runtime/bridges/voice/` |
| Orchestrator (intelligence target) | `mind-mcp/runtime/orchestrator/` |
| Auth module (bond lookup) | `mind-mcp/runtime/auth/` |
| This doc chain | `mind-protocol/docs/product/chat-bridges/` |
| L4 Registry (citizen bonds) | `mind-protocol/l4/registry/` |
| L4 Schema (canonical types basis) | `mind-protocol/l4/schema/` |
