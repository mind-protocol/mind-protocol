# Chat Bridges -- Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Chat_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Chat_Bridges.md
PATTERNS:        ./PATTERNS_Chat_Bridges.md
ALGORITHM:       ./ALGORITHM_Chat_Bridges.md
VALIDATION:      ./VALIDATION_Chat_Bridges.md
THIS:            IMPLEMENTATION_Chat_Bridges.md (you are here)
SYNC:            ./SYNC_Chat_Bridges.md

IMPL:            mind-mcp/runtime/bridges/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-mcp/runtime/bridges/
├── telegram/
│   ├── __init__.py
│   └── telegram_polling_bridge_and_message_handler.py     # 795 LOC, LIVE
├── whatsapp/
│   ├── __init__.py
│   └── whatsapp_waha_webhook_bridge_and_message_handler.py  # 274 LOC, LIVE
├── voice/
│   ├── __init__.py
│   └── voice_websocket_bridge_and_stream_handler.py       # 385 LOC, LIVE
├── messenger/                                              # S3-S4, PLANNED
│   ├── __init__.py
│   └── messenger_meta_webhook_bridge_and_message_handler.py
├── discord/                                                # S7-S8, PLANNED
│   ├── __init__.py
│   └── discord_gateway_bridge_and_message_handler.py
├── slack/                                                  # S9-S10, PLANNED
│   ├── __init__.py
│   └── slack_events_webhook_bridge_and_message_handler.py
├── teams/                                                  # S9-S10, PLANNED
│   ├── __init__.py
│   └── teams_botframework_webhook_bridge_and_message_handler.py
└── shared/
    ├── __init__.py
    ├── canonical_message_and_response_types.py             # CanonicalMessage, CanonicalResponse, MediaAttachment
    └── rate_limiter_with_token_bucket.py                   # Shared rate limiter (token bucket algorithm)
```

### File Responsibilities

**LIVE (existing)**

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `telegram/telegram_polling_bridge_and_message_handler.py` | Telegram long-polling bridge | `TelegramBridge`, `handle_update`, `send_response` | ~795 | WATCH |
| `whatsapp/whatsapp_waha_webhook_bridge_and_message_handler.py` | WhatsApp WAHA webhook bridge | `WhatsAppBridge`, `handle_webhook`, `send_message` | ~274 | OK |
| `voice/voice_websocket_bridge_and_stream_handler.py` | Voice WebSocket real-time bridge | `VoiceBridge`, `on_message`, `stream_response` | ~385 | OK |

**PLANNED**

| File | Purpose | Key Functions/Classes | Est. Lines | Sprint |
|------|---------|----------------------|------------|--------|
| `messenger/messenger_meta_webhook_bridge_and_message_handler.py` | Facebook Messenger bridge | `MessengerBridge`, `verify_webhook`, `handle_message_event` | ~350 | S3-S4 |
| `discord/discord_gateway_bridge_and_message_handler.py` | Discord bot bridge | `DiscordBridge`, `on_message`, `send_embed` | ~400 | S7-S8 |
| `slack/slack_events_webhook_bridge_and_message_handler.py` | Slack app bridge | `SlackBridge`, `handle_event`, `send_block_kit` | ~450 | S9-S10 |
| `teams/teams_botframework_webhook_bridge_and_message_handler.py` | Microsoft Teams bot bridge | `TeamsBridge`, `verify_jwt`, `send_adaptive_card` | ~500 | S9-S10 |
| `shared/canonical_message_and_response_types.py` | Shared Pydantic models | `CanonicalMessage`, `CanonicalResponse`, `MediaAttachment` | ~120 | S3 |
| `shared/rate_limiter_with_token_bucket.py` | Token bucket rate limiter | `RateLimiter`, `acquire`, `reset` | ~80 | S3 |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

> Telegram bridge is at 795 LOC (SPLIT territory). Before adding features, extract media handling or keyboard rendering into a separate file.

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Transport Adapter (variant of Strategy pattern)

**Why this pattern:** Each bridge is a concrete adapter implementing the same logical flow (receive -> auth -> translate -> forward -> deliver) with platform-specific ceremony. The orchestrator is agnostic to which adapter delivered the message.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Adapter | Each bridge file | Translates platform API to canonical format |
| Token Bucket | `rate_limiter_with_token_bucket.py` | Prevents platform rate limit violations |
| Deduplication Cache | In-memory dict with TTL | Prevents double-processing of at-least-once delivered webhooks |
| Exponential Backoff | Outbound delivery retry | Graceful handling of transient platform API failures |

### Anti-Patterns to Avoid

- **Shared base class with template methods**: Tempting to create `BaseBridge` with hooks. But bridges differ in transport (HTTP vs WebSocket vs polling), making a shared base class misleading. Use shared utility functions instead.
- **Bridge-local message queue**: Tempting to buffer messages. But bridges must be stateless. Use the orchestrator's queue if queueing is needed.
- **Platform SDK wrappers**: Tempting to wrap each platform SDK in an abstraction layer. But bridges are already the abstraction. Adding another layer doubles the translation cost for zero benefit.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Bridge perimeter | Platform API calls, format translation, auth lookup | Response generation, conversation memory, tool use | `CanonicalMessage` / `CanonicalResponse` |
| Auth boundary | Bond lookup, platform ID mapping | Citizen identity management, bond creation | `auth.lookup_bond()` |
| Rate limit boundary | Token bucket, throttle logic | Platform API rate limit definitions | `PlatformConfig.rate_limit` |

---

## SCHEMA

### CanonicalMessage (Pydantic model)

```yaml
CanonicalMessage:
  required:
    - sender_id: str            # Mind citizen bond ID
    - platform: str             # Platform identifier
    - platform_user_id: str     # Platform-native user ID
    - chat_id: str              # Platform-native chat ID
    - message_id: str           # Platform-native message ID
    - timestamp: datetime       # Message timestamp
  optional:
    - text: str | None          # Text content
    - media: list[MediaAttachment] | None
    - reply_to: str | None      # Reply-to message ID
    - raw_metadata: dict        # Platform-specific debug info
  constraints:
    - At least one of text or media must be present
    - sender_id must correspond to a valid bond in the registry
```

### MediaAttachment

```yaml
MediaAttachment:
  required:
    - type: str                 # image | audio | video | document | voice_note | sticker
    - mime_type: str            # Standard MIME type
  optional:
    - url: str | None           # Direct download URL
    - binary: bytes | None      # Raw binary data
    - filename: str | None
    - caption: str | None
    - duration_seconds: float | None
    - size_bytes: int | None
  constraints:
    - At least one of url or binary must be present
    - type must be one of the allowed enum values
```

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| Telegram poll loop | `telegram/telegram_polling_bridge_and_message_handler.py` | Process startup (asyncio loop) |
| WhatsApp webhook | `whatsapp/whatsapp_waha_webhook_bridge_and_message_handler.py` | HTTP POST from WAHA |
| Voice WebSocket | `voice/voice_websocket_bridge_and_stream_handler.py` | WebSocket connection |
| Messenger webhook | `messenger/messenger_meta_webhook_bridge_and_message_handler.py` | HTTP POST from Meta |
| Discord gateway | `discord/discord_gateway_bridge_and_message_handler.py` | WebSocket from Discord Gateway |
| Slack events | `slack/slack_events_webhook_bridge_and_message_handler.py` | HTTP POST from Slack |
| Teams webhook | `teams/teams_botframework_webhook_bridge_and_message_handler.py` | HTTP POST from Bot Framework |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Inbound Message Flow: Platform to Orchestrator

This is the primary flow. Every bridge implements it. It transforms a platform-specific event into a canonical message and delivers it to the orchestrator. This flow carries risk because it crosses the auth boundary and handles untrusted input.

```yaml
flow:
  name: inbound_message
  purpose: Deliver authenticated human messages to orchestrator in canonical format
  scope: Platform event -> CanonicalMessage -> orchestrator.process()
  steps:
    - id: receive_event
      description: Receive raw event from platform API
      file: bridges/{platform}/{bridge_file}.py
      function: handle_webhook / poll_loop
      input: HTTP POST body or poll response
      output: Raw platform event dict
      trigger: Platform webhook or poll interval
      side_effects: none
    - id: verify_signature
      description: Verify webhook signature or auth token
      file: bridges/{platform}/{bridge_file}.py
      function: verify_webhook / verify_signature
      input: Request headers + body + webhook_secret
      output: Boolean (valid/invalid)
      trigger: receive_event
      side_effects: 401 response on failure
    - id: authenticate_sender
      description: Map platform user ID to Mind citizen bond
      file: runtime/auth/
      function: lookup_bond(platform, platform_user_id)
      input: Platform name + platform user ID
      output: Bond object or None
      trigger: verify_signature (passed)
      side_effects: Onboarding prompt on unknown user
    - id: translate_to_canonical
      description: Build CanonicalMessage from platform event
      file: bridges/{platform}/{bridge_file}.py
      function: translate_message / build_canonical
      input: Raw event + bond
      output: CanonicalMessage
      trigger: authenticate_sender (bond found)
      side_effects: Media download if needed
    - id: forward_to_orchestrator
      description: Send canonical message to orchestrator
      file: runtime/orchestrator/
      function: orchestrator.process(canonical_message)
      input: CanonicalMessage
      output: CanonicalResponse
      trigger: translate_to_canonical
      side_effects: LLM inference, memory update, tool calls
  docking_points:
    guidance:
      include_when: Auth boundary crossing, untrusted input processing, format transformation
      omit_when: Simple field extraction with no risk
      selection_notes: Focus on verify_signature and authenticate_sender as primary risk points
    available:
      - id: dock_webhook_receive
        type: api
        direction: input
        file: bridges/{platform}/{bridge_file}.py
        function: handle_webhook
        trigger: HTTP POST
        payload: Raw request body
        async_hook: not_applicable
        needs: none
        notes: Entry point -- all untrusted data enters here
      - id: dock_auth_lookup
        type: auth
        direction: input
        file: runtime/auth/
        function: lookup_bond
        trigger: authenticate_sender step
        payload: platform + platform_user_id
        async_hook: optional
        needs: none
        notes: Security perimeter -- determines if message proceeds
      - id: dock_orchestrator_input
        type: api
        direction: output
        file: runtime/orchestrator/
        function: orchestrator.process
        trigger: forward_to_orchestrator step
        payload: CanonicalMessage
        async_hook: required
        needs: none
        notes: Handoff point -- bridge responsibility ends here
    health_recommended:
      - dock_id: dock_auth_lookup
        reason: Authentication is the security perimeter -- failures here mean unauthorized access or blocked legitimate users
      - dock_id: dock_orchestrator_input
        reason: If canonical messages fail to reach orchestrator, citizen is deaf
```

### Outbound Response Flow: Orchestrator to Platform

Transforms orchestrator response back to platform format and delivers it. Carries risk because delivery failure means citizen is mute.

```yaml
flow:
  name: outbound_response
  purpose: Deliver citizen response to human via platform API
  scope: CanonicalResponse -> format -> rate limit -> platform API
  steps:
    - id: receive_response
      description: Receive canonical response from orchestrator
      file: bridges/{platform}/{bridge_file}.py
      function: deliver_response / send_response
      input: CanonicalResponse + platform context
      output: Formatted platform message
      trigger: orchestrator.process() returns
      side_effects: Typing indicator stopped
    - id: format_for_platform
      description: Translate canonical format to platform-native format
      file: bridges/{platform}/{bridge_file}.py
      function: format_response / build_platform_message
      input: CanonicalResponse
      output: Platform-specific message payload
      trigger: receive_response
      side_effects: none
    - id: rate_limited_send
      description: Send via platform API respecting rate limits
      file: bridges/shared/rate_limiter_with_token_bucket.py + platform bridge
      function: rate_limiter.acquire() + send_message()
      input: Platform message payload
      output: Delivery confirmation or error
      trigger: format_for_platform
      side_effects: Message delivered to human, retry on failure
  docking_points:
    guidance:
      include_when: Delivery failure, rate limit enforcement
      omit_when: Simple format translation
      selection_notes: Focus on rate_limited_send as the critical delivery point
    available:
      - id: dock_platform_send
        type: api
        direction: output
        file: bridges/{platform}/{bridge_file}.py
        function: send_message
        trigger: rate_limited_send step
        payload: Platform message payload
        async_hook: required
        needs: none
        notes: Final delivery -- failure here means citizen is mute
    health_recommended:
      - dock_id: dock_platform_send
        reason: Delivery failure rate directly measures citizen presence quality
```

---

## LOGIC CHAINS

### LC1: Full Message Round-Trip

**Purpose:** Complete path from human message to citizen response delivered.

```
Platform webhook/poll
  -> bridge.handle_event()           # Receive + verify
    -> auth.lookup_bond()            # Authenticate
      -> bridge.translate()          # To canonical
        -> orchestrator.process()    # LLM inference
          -> bridge.format()         # To platform format
            -> bridge.send()         # Deliver response
              -> Platform API
```

**Data transformation:**
- Input: `dict` -- Raw platform event (JSON body)
- After auth: `Bond` -- Verified sender identity
- After translate: `CanonicalMessage` -- Platform-agnostic message
- After orchestrator: `CanonicalResponse` -- Platform-agnostic response
- After format: `dict` -- Platform-specific payload
- Output: `DeliveryStatus` -- Success or failure with metadata

### LC2: Onboarding New User

**Purpose:** Link a new platform user to their Mind citizen bond.

```
Unknown platform user sends message
  -> auth.lookup_bond() returns None
    -> bridge.send_onboarding_prompt()  # Platform-native prompt
      -> User provides Mind identity token
        -> auth.create_bond_link()      # Creates mapping
          -> Subsequent messages now route correctly
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
bridges/{platform}/
    └── imports -> bridges/shared/canonical_message_and_response_types.py
    └── imports -> bridges/shared/rate_limiter_with_token_bucket.py
    └── calls  -> runtime/auth/
    └── calls  -> runtime/orchestrator/
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `python-telegram-bot` | Telegram Bot API SDK | `telegram/` |
| `aiohttp` | HTTP client for WhatsApp WAHA, Messenger, Slack APIs | `whatsapp/`, `messenger/`, `slack/` |
| `discord.py` | Discord Gateway + REST API | `discord/` |
| `slack-sdk` | Slack Web API + Events API | `slack/` |
| `botbuilder-core` | Microsoft Bot Framework SDK | `teams/` |
| `pydantic` | CanonicalMessage/Response models | `shared/` |
| `cryptography` | Webhook signature verification (HMAC, JWT) | All webhook bridges |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Dedup cache | Bridge process memory (dict) | Per-bridge-instance | TTL 5 minutes, cleared on restart |
| Rate limiter tokens | Bridge process memory | Per-bridge-instance | Refills continuously, reset on restart |
| Bot token / webhook secret | Environment variables | Per-deployment | Set at deploy, never changes at runtime |

Bridges hold NO persistent state. Both the dedup cache and rate limiter tokens are ephemeral and reconstructable. Losing them on restart causes at worst one duplicate message (dedup miss) or a brief burst before rate limiter stabilizes.

### State Transitions

```
STARTING ──(register webhook / start poll)──> RUNNING ──(shutdown signal)──> STOPPING ──(cleanup)──> STOPPED
                                                 |
                                         (platform API down)
                                                 |
                                                 v
                                             DEGRADED ──(API recovers)──> RUNNING
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load platform config from environment variables
2. Initialize rate limiter with platform-specific limits
3. Initialize dedup cache (empty dict with TTL support)
4. Register webhook URL with platform API (webhook bridges)
   OR start polling loop (polling bridges)
   OR open WebSocket connection (WebSocket bridges)
5. Log: "Bridge started", platform, transport_type, webhook_url or poll_interval
```

### Main Loop / Request Cycle

```
1. Receive platform event (webhook POST / poll result / WebSocket frame)
2. Verify authenticity (signature / token / challenge)
3. Deduplicate (check message ID cache)
4. Authenticate sender (bond lookup)
5. Translate to CanonicalMessage
6. Start typing indicator
7. Forward to orchestrator (await response)
8. Stop typing indicator
9. Format response for platform
10. Deliver via rate-limited send (with retry)
```

### Shutdown

```
1. Stop accepting new events (close webhook server / stop poll loop / close WebSocket)
2. Await in-flight messages (up to 30s timeout)
3. Log: "Bridge stopped", platform, messages_in_flight
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Webhook bridges | async (asyncio) | Single event loop, concurrent request handling |
| Polling bridge (Telegram) | async (asyncio) | Poll + process in same event loop |
| WebSocket bridge (Voice) | async (asyncio) | WebSocket frames processed concurrently |
| Rate limiter | async-safe | Token bucket with asyncio.Lock |
| Orchestrator calls | async (await) | Non-blocking wait for LLM inference |

All bridges use asyncio. No threads. No multiprocessing. The event loop handles concurrent messages naturally. The bottleneck is orchestrator response time (LLM inference), not bridge processing.

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | env var | -- | Telegram bot API token |
| `WHATSAPP_WAHA_URL` | env var | -- | WAHA instance URL |
| `WHATSAPP_WEBHOOK_SECRET` | env var | -- | WAHA webhook verification secret |
| `MESSENGER_PAGE_TOKEN` | env var | -- | Facebook page access token |
| `MESSENGER_VERIFY_TOKEN` | env var | -- | Webhook verification token |
| `MESSENGER_APP_SECRET` | env var | -- | App secret for signature verification |
| `DISCORD_BOT_TOKEN` | env var | -- | Discord bot token |
| `SLACK_BOT_TOKEN` | env var | -- | Slack bot OAuth token |
| `SLACK_SIGNING_SECRET` | env var | -- | Slack request signing secret |
| `TEAMS_APP_ID` | env var | -- | Teams bot app ID |
| `TEAMS_APP_PASSWORD` | env var | -- | Teams bot app password |
| `BRIDGE_RETRY_MAX` | env var | 3 | Max retry attempts for failed delivery |
| `BRIDGE_RETRY_BACKOFF_BASE` | env var | 1.0 | Base seconds for exponential backoff |
| `BRIDGE_DEDUP_TTL` | env var | 300 | Seconds to keep message IDs for deduplication |

---

## EXTRACTION CANDIDATES

Files approaching WATCH/SPLIT status -- identify what can be extracted:

| File | Current | Target | Extract To | What to Move |
|------|---------|--------|------------|--------------|
| `telegram/telegram_polling_bridge_and_message_handler.py` | ~795L | <400L | `telegram/telegram_media_and_keyboard_formatter.py` | `format_inline_keyboard()`, `download_media()`, `render_markdown_v2()` -- estimated ~300 LOC of formatting/media logic |

---

## MARKERS

<!-- @mind:todo Extract shared/canonical_message_and_response_types.py as first task before building Messenger bridge -->
<!-- @mind:todo Split Telegram bridge before adding any new features to it -->
<!-- @mind:proposition Consider a bridge_registry.py that auto-discovers and registers active bridges for health monitoring -->
