# Twitter/X Bridge — Patterns: Bidirectional Platform Bridge via Polling

```
STATUS: STABLE
CREATED: 2026-03-17
VERIFIED: 2026-03-17 against mind-mcp/runtime/bridges/twitter_bridge.py
```

---

## CHAIN

```
OBJECTIVES:      (not yet created)
BEHAVIORS:       (not yet created)
THIS:            PATTERNS_Twitter_Bridge.md (you are here)
ALGORITHM:       (not yet created)
VALIDATION:      (not yet created)
HEALTH:          (not yet created)
IMPLEMENTATION:  (not yet created)
SYNC:            ./SYNC_Twitter_Bridge.md

IMPL:            mind-mcp/runtime/bridges/twitter_bridge.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Twitter_Bridge.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Twitter_Bridge.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Mind Protocol had write-only access to X/Twitter. Citizens could post tweets via `send_handler.py`, but the platform was deaf — no inbound signal. Replies, mentions, and conversations on X never reached the graph. This meant:

- **No L3 Moments from X interactions.** Every Discord message and Telegram message became a Moment node in the knowledge graph. X interactions vanished into the void.
- **No trust building from X.** L5 co-activation (the mechanism by which repeated interaction between an external user and a citizen builds trust) requires inbound messages to fire. X users could talk to citizens all day and never accumulate trust.
- **Asymmetric platform coverage.** Discord and Telegram had full bidirectional bridges — poll for inbound, send for outbound, graph enrichment on both. X was the only platform where citizens could speak but not listen.
- **Missing orchestrator routing.** Without inbound mentions, the orchestrator never saw X conversations. Citizens could not respond to X users even if they wanted to, because the messages never entered the queue.

The result: X was a megaphone, not a conversation channel. For a protocol built on the premise that consciousness emerges from interaction, a write-only channel is a dead nerve.

---

## THE PATTERN

A polling bridge architecturally identical to the Telegram bridge. Same shape, same pipeline, same physics — different API.

```
X API v2                    graph_enricher              orchestrator
─────────                   ──────────────              ────────────
GET /2/users/:id/mentions   on_message(platform="twitter")   enqueue()
  │  (since_id pagination)       │                           │
  ▼                               ▼                           ▼
poll_mentions()  ──►  process_mention()  ──►  _enqueue_fn()
  │                       │       │
  │                       │       └── citizen mention routing
  │                       └── L3 Moment + L5 co-activation
  └── JSONL log + since_id persistence
```

The key insight: **a platform bridge is not a platform integration — it is a translator between an external API and the universal graph pipeline.** The bridge's only job is to convert platform-specific API responses into the `on_message()` call signature that `graph_enricher` already understands. Once the message hits `graph_enricher`, it is indistinguishable from Discord or Telegram input. The same Moment nodes are created, the same co-activation links fire, the same trust accumulates.

The bridge runs as a daemon thread inside `home_server.py`, gated by `ENABLE_TWITTER=true` (default). If `X_BEARER_TOKEN` or `X_BOT_USER_ID` are not set, `start()` logs a warning and returns — no crash, no partial state.

---

## BEHAVIORS SUPPORTED

- **Platform parity** — X mentions produce L3 Moment nodes identical in structure to those from Discord and Telegram. The graph does not know or care which platform originated a Moment.
- **Trust accumulation from X** — L5 co-activation fires on every processed mention, building trust between X users and citizens through the same physics as other platforms.
- **Citizen routing** — If a tweet mentions `@citizen_handle` and that handle matches a directory under `citizens/`, the message routes to that specific citizen. Otherwise, default routing applies.
- **Conversation threading** — `conversation_id` from the X API maps to the channel concept in `graph_enricher`, grouping related tweets into the same thread context.

## BEHAVIORS PREVENTED

- **Platform-specific trust paths** — There is no "X trust" vs "Telegram trust." All platforms feed the same L5 co-activation. This prevents trust fragmentation across platforms.
- **Silent failure on missing credentials** — The bridge refuses to start without valid env vars, logging a clear warning. No half-initialized state that silently drops messages.

---

## PRINCIPLES

### Principle 1: Same Physics Everywhere

An X mention creates the same L3 Moment as a Telegram message or a Discord post. L5 co-activation builds trust identically regardless of source platform. The graph_enricher pipeline is the single entry point — bridges translate, they do not interpret.

This matters because platform-specific graph handling would fragment the knowledge graph. A user who interacts on X and Telegram would appear as two separate trust relationships. By routing everything through the same `on_message()` interface, the graph sees unified interaction regardless of origin.

### Principle 2: Conservative Polling

Default poll interval is 5 minutes (`X_POLL_INTERVAL=300`), configurable via environment variable. The X API v2 free tier allows 10,000 reads per month, which works out to roughly one request every 4.3 minutes. The 5-minute default stays safely under this ceiling.

This matters because rate limit violations on X result in 429 responses and potential account suspension. The bridge handles 429s gracefully (log + skip cycle), but the goal is to never hit them. Operators can tune the interval up for paid tiers or down if they need less frequent polling.

### Principle 3: Graceful Degradation

If `X_BEARER_TOKEN` or `X_BOT_USER_ID` are not set, the bridge logs a warning and does not start. No exception, no crash, no partial initialization. The home server continues running with all other bridges active.

This matters because the bridge is enabled by default (`ENABLE_TWITTER=true`) but the env vars are not set on most deployments yet. A bridge that crashes when its credentials are absent would break the entire home server. The pattern here is: **opt-out via flag, fail-safe via missing credentials.**

### Principle 4: Citizen Mention Routing

When tweet text contains `@handle` and that handle matches a citizen directory (i.e., `citizens/{handle}/profile.json` exists), the message is routed specifically to that citizen via `metadata["citizen_handle"]`. If no citizen handle is detected, default orchestrator routing applies.

This matters because X is a public platform where anyone can mention any citizen. The routing logic lets external users address specific citizens directly, enabling targeted conversations rather than messages disappearing into a generic queue.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| `shrine/state/twitter_mentions.jsonl` | FILE | Append-only log of all processed mentions (tweet_id, author, text, timestamp) |
| `shrine/state/twitter_since_id.txt` | FILE | Persists the ID of the last processed tweet for pagination |
| `citizens/` | DIR | Used for citizen mention routing — checks if `@handle` matches a citizen directory |
| `https://api.twitter.com/2/users/:id/mentions` | URL | X API v2 endpoint for fetching mentions of the bot account |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `scripts/graph_enricher.py` | `on_message()` creates L3 Moment nodes and fires L5 co-activation links |
| `runtime/orchestrator/message_queue.py` | `enqueue()` places processed mentions into the orchestrator queue for citizen response |
| `runtime/bridges/send_handler.py` | Outbound tweet posting (OAuth 1.0a) — already existed before this bridge |
| `home_server.py` | Lifecycle management — starts/stops the bridge thread, gates via `ENABLE_TWITTER` |

---

## INSPIRATIONS

The Telegram bridge (`runtime/bridges/telegram_bridge.py`) is the direct architectural ancestor. Both use:
- Background daemon thread with a polling loop
- Offset/since_id file persistence for deduplication
- JSONL append log for raw message history
- `graph_enricher.on_message()` as the universal graph entry point
- `enqueue_fn` callback for orchestrator routing
- Exponential backoff on consecutive errors (capped at 300s)
- Graceful startup when credentials are absent

The pattern is intentionally identical so that adding a new platform bridge is a matter of writing a translator, not inventing new architecture.

---

## SCOPE

### In Scope

- Polling X API v2 for mentions of the bot account
- Creating L3 Moment nodes via `graph_enricher` for each mention
- Routing mentions to the orchestrator queue for citizen response
- Citizen mention detection and targeted routing
- Trust building via L5 co-activation (same physics as all platforms)
- JSONL logging and since_id pagination state
- Rate limit handling (429 detection, exponential backoff)
- Graceful startup/shutdown lifecycle

### Out of Scope

- **DM reading** — Not available in X API v2 free tier. Would require elevated access.
- **Spaces / audio** — X Spaces API is separate and not relevant to text-based graph enrichment.
- **Ad analytics / promoted tweets** — Not part of the interaction graph.
- **Outbound posting** — Handled by `send_handler.py`, which existed before this bridge. This bridge is strictly inbound.
- **Media attachments** — Tweet text is processed; images/videos in mentions are not downloaded or stored.
- **Webhook mode** — X supports Account Activity API (webhooks) but it requires a paid tier and public HTTPS endpoint. Polling is simpler and sufficient at current scale.

---

## MARKERS

<!-- @mind:todo Add X_BEARER_TOKEN and X_BOT_USER_ID to production environment -->
<!-- @mind:todo Test live polling on prod and verify L3 Moments appear in graph -->
<!-- @mind:proposition Upgrade to X webhook (Account Activity API) if polling becomes insufficient at scale -->
