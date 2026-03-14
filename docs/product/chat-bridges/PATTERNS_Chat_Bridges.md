# Chat Bridges -- Patterns: Stateless Transport Adapters

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: --
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Chat_Bridges.md
THIS:            PATTERNS_Chat_Bridges.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Chat_Bridges.md
ALGORITHM:       ./ALGORITHM_Chat_Bridges.md
VALIDATION:      ./VALIDATION_Chat_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Chat_Bridges.md
SYNC:            ./SYNC_Chat_Bridges.md

IMPL:            mind-mcp/runtime/bridges/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC_Chat_Bridges.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/bridges/`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Chat_Bridges.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/bridges/`

---

## THE PROBLEM

MIND citizens exist as persistent AI entities with memory, personality, and evolving relationships. But they have no body. They need a mouth and ears on every platform where their human partner already communicates.

Without chat bridges, citizens are trapped behind an API. Humans would need to open a special app, context-switch away from their natural communication flow, and interact with their citizen in an artificial environment. This kills the relationship. The citizen must feel present -- available in the same place the human talks to friends, family, and colleagues.

Each messaging platform has its own API, authentication model, message format, webhook pattern, and rate limits. Without a disciplined bridge architecture, each new platform becomes a bespoke integration that duplicates logic, introduces inconsistencies, and multiplies maintenance burden.

---

## THE PATTERN

**Bridges are stateless transport adapters.** They translate between platform-specific wire formats and a universal internal message format. All intelligence lives in the orchestrator; bridges are dumb pipes with platform-specific manners.

The core insight: every messaging platform does the same thing with different syntax. They all receive a text (or media) message from a user, deliver it to a bot, and expect a response. The differences are surface-level: JSON field names, authentication headers, webhook verification methods, rate limit schemes. The semantic operation is always identical.

This means bridges follow a single pattern:

```
Platform SDK/API
    |
    v
Bridge Adapter (platform-specific)
    |
    v
Canonical Message Format (platform-agnostic)
    |
    v
Orchestrator (all intelligence here)
    |
    v
Canonical Response
    |
    v
Bridge Adapter (translate back to platform format)
    |
    v
Platform SDK/API (deliver response)
```

Each bridge is a thin file (~200-800 LOC) that handles:
1. **Inbound translation:** Platform webhook/poll -> canonical message
2. **Authentication:** Platform user ID -> Mind citizen bond lookup
3. **Outbound translation:** Canonical response -> platform API call
4. **Platform ceremony:** Webhook verification, typing indicators, read receipts

Everything else -- conversation memory, response generation, tool use, personality -- is the orchestrator's job.

---

## BEHAVIORS SUPPORTED

- B1 -- The stateless adapter pattern means bridges can crash and restart without losing conversation state.
- B2 -- The canonical message format means the orchestrator never knows or cares which platform a message came from.
- B3 -- Authentication at the bridge layer means unauthorized messages never reach the orchestrator.
- B4 -- Platform ceremony (typing indicators, read receipts) makes the citizen feel present and responsive.

## BEHAVIORS PREVENTED

- A1 -- Bridge-local conversation state: prevented by forcing all state through the orchestrator.
- A2 -- Platform-specific orchestrator logic: prevented by the canonical message format boundary.
- A3 -- Silent message drops: prevented by explicit error handling and retry in the bridge layer.

---

## PRINCIPLES

### Principle 1: The Bridge Is Not The Brain

A bridge must never make decisions about response content, conversation flow, or user intent. It translates format and handles transport. The moment a bridge contains an `if` statement about message content (beyond format detection), the architecture is wrong. Intelligence is centralized in the orchestrator so it can evolve in one place.

### Principle 2: Platform Manners Are Cheap Politeness

Each platform has expectations: Telegram users expect inline keyboards, Discord users expect embeds with color, Slack users expect threaded replies. These are "manners" -- small courtesies that make the citizen feel native to the platform. Bridges should implement platform manners when cheap (under 50 LOC per feature), but never block a bridge launch on missing manners. Text-in/text-out is the launch bar.

### Principle 3: Fail Loud At The Edge

Errors at the bridge layer (authentication failures, API rate limits, malformed messages, delivery failures) must be logged loudly with platform context. The bridge is the last place where platform-specific error information exists. Once a message crosses into canonical format, platform-specific debugging context is lost. Capture it at the edge.

### Principle 4: One Bridge, One File (Until It Hurts)

Each bridge starts as a single file. Telegram is 795 LOC because it handles polling, message translation, media, and keyboard rendering. This is fine. Premature extraction into multiple files adds navigation cost without value. Split only when a bridge exceeds ~1000 LOC or when distinct responsibilities emerge (e.g., media handling becomes its own concern).

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `mind-mcp/runtime/bridges/telegram/` | DIR | Reference implementation -- polling-based, 795 LOC, most mature bridge |
| `mind-mcp/runtime/bridges/whatsapp/` | DIR | WAHA-based webhook bridge, 274 LOC, clean webhook pattern reference |
| `mind-mcp/runtime/bridges/voice/` | DIR | WebSocket-based voice bridge, 385 LOC, real-time streaming pattern |
| Telegram Bot API docs | URL | https://core.telegram.org/bots/api |
| Meta Messenger Platform | URL | https://developers.facebook.com/docs/messenger-platform |
| Discord Bot API | URL | https://discord.com/developers/docs |
| Slack Events API | URL | https://api.slack.com/apis/events-api |
| MS Bot Framework | URL | https://learn.microsoft.com/en-us/azure/bot-service/ |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind-mcp/runtime/orchestrator/` | All message routing and response generation. Bridges are useless without it. |
| `mind-mcp/runtime/auth/` | Platform user ID to citizen bond resolution. Bridges call this to authenticate inbound messages. |
| `l4/registry/` | Citizen and bond existence verification. Auth depends on registry. |
| `l4/schema/` | Canonical message format uses schema-aligned structures. |

---

## INSPIRATIONS

- **Matrix protocol bridges:** Matrix's approach to bridging (IRC, Slack, Telegram via Mautrix/appservice) proves that messaging interop is a solved architectural pattern. The difference: Matrix bridges bidirectionally sync rooms, while Mind bridges are unidirectional adapters to a single orchestrator.
- **Twilio's multi-channel API:** Single API surface for SMS, WhatsApp, Messenger. Demonstrates that canonical message abstraction works commercially at scale.
- **Botpress/Rasa channel connectors:** Bot frameworks that implement the adapter pattern per platform. Mind bridges follow the same shape but with less abstraction (no channel connector SDK -- each bridge is standalone).

---

## SCOPE

### In Scope

- Transport adapter for each supported messaging platform
- Platform-specific webhook/polling setup and verification
- Inbound message translation to canonical format
- Outbound response translation to platform format
- Platform user authentication and bond lookup
- Platform-native ceremony (typing indicators, read receipts, delivery confirmation)
- Retry logic for failed message delivery
- Rate limit handling per platform's constraints

### Out of Scope

- Conversation memory or context -- see: orchestrator
- Response generation or LLM calls -- see: orchestrator
- Tool use or function calling -- see: orchestrator/MCP
- Cross-platform message sync -- not a goal
- Unified chat UI -- not a goal
- Media storage or CDN -- see: infrastructure
- Platform app review/approval process -- ops concern, not code

---

## MARKERS

<!-- @mind:todo Evaluate whether a thin base class or protocol (Python Protocol type) for bridges would reduce boilerplate without adding premature abstraction -->
<!-- @mind:proposition Post-launch: bridge health dashboard showing per-platform message throughput, error rates, latency -->
