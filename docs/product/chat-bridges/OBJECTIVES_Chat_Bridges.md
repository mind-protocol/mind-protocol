# OBJECTIVES -- Chat Bridges

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: —
```

---

## CHAIN

```
THIS:            OBJECTIVES_Chat_Bridges.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Chat_Bridges.md
BEHAVIORS:      ./BEHAVIORS_Chat_Bridges.md
ALGORITHM:      ./ALGORITHM_Chat_Bridges.md
VALIDATION:     ./VALIDATION_Chat_Bridges.md
IMPLEMENTATION: ./IMPLEMENTATION_Chat_Bridges.md
SYNC:           ./SYNC_Chat_Bridges.md

IMPL:           mind-mcp/runtime/bridges/{telegram,whatsapp,voice,messenger,discord,slack,teams}/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Ubiquitous presence -- MIND lives where humans already are.** Citizens must be reachable on every messaging app the human uses. No app installs, no new habits. The bridge disappears; the relationship remains. This is the single most important product decision: meet humans in their existing communication channels.

2. **Identical experience regardless of channel.** A conversation with your citizen on Telegram must feel indistinguishable from one on WhatsApp or Discord. The orchestrator produces the response; the bridge only translates transport. Channel-specific features (reactions, threads, voice notes) are additive, never required.

3. **Minimal per-bridge engineering cost.** Each new bridge should take 2-4 days to build because the pattern is identical: receive message, authenticate user, route to orchestrator, get response, send back. The architecture must make new bridges boring to implement.

4. **Resilient message delivery.** Messages must not be silently lost. If delivery fails, the system must retry with backoff or surface the failure visibly. A citizen that drops messages destroys trust.

5. **Authentication anchored to existing identity.** Each bridge maps a platform-specific user ID to a Mind citizen-human bond. No separate Mind login. The platform identity IS the authentication, verified once during onboarding.

## NON-OBJECTIVES

- **Building a unified chat UI.** We are not building a new messaging app. Each bridge uses the native platform UI. There is no Mind-branded chat interface.
- **Cross-platform message sync.** If a human talks to their citizen on Telegram, that conversation does not replay on WhatsApp. The orchestrator holds context; bridges are stateless transport.
- **Platform-specific feature parity.** WhatsApp has ephemeral messages, Discord has slash commands, Telegram has inline keyboards. Bridges may expose these when natural, but no bridge is required to implement features another bridge has.
- **Scaling to millions of concurrent connections.** Phase 1 bridges serve hundreds to low thousands of active citizens. Horizontal scaling is a later concern.

## TRADEOFFS (canonical decisions)

- When **speed of new bridge delivery** conflicts with **platform-specific polish**, choose speed. Ship the bridge with text-in/text-out first. Add rich media, reactions, and platform-native features later.
- When **webhook reliability** conflicts with **polling simplicity**, choose webhooks for platforms that support them well (WhatsApp, Messenger, Slack, Teams). Use polling only where webhooks are unstable or unavailable (Telegram, as currently implemented).
- When **bridge-local state** conflicts with **orchestrator-owns-all-state**, the orchestrator wins. Bridges must be stateless and replaceable. If a bridge process dies and restarts, no conversation context is lost because it was never held there.
- We accept **platform API rate limits** as constraints rather than fighting them. Design around limits from the start rather than hitting them and patching.

## SUCCESS SIGNALS (observable)

- A new bridge (text-in/text-out) can be implemented in under 3 days by an agent reading this doc chain and the existing bridge code.
- Message round-trip latency (user sends message -> user sees response) is under 5 seconds for 95th percentile, excluding LLM inference time.
- Zero silent message drops over a 30-day window per bridge.
- Human onboarding to a new bridge (linking platform identity to citizen bond) completes in under 2 minutes.
- All bridges pass the same integration test suite (parameterized by platform).
