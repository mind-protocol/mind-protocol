# Chat Bridges -- Algorithm: Message Flow Procedures

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: --
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Chat_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Chat_Bridges.md
PATTERNS:        ./PATTERNS_Chat_Bridges.md
THIS:            ALGORITHM_Chat_Bridges.md (you are here)
VALIDATION:      ./VALIDATION_Chat_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Chat_Bridges.md
SYNC:            ./SYNC_Chat_Bridges.md

IMPL:            mind-mcp/runtime/bridges/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Every chat bridge executes the same algorithm with platform-specific ceremony at the edges. The algorithm has two flows: inbound (human -> citizen) and outbound (citizen -> human). Both flows are simple pipelines with no branching logic beyond error handling. This simplicity is intentional -- complexity belongs in the orchestrator, not the bridges.

The algorithm described here is the universal pattern. Each bridge implements it with platform-specific adaptations (webhook verification methods, API call signatures, rate limit handling), but the logical flow is invariant.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| O1: Ubiquitous presence | B1, B2, B8 | The inbound/outbound flow IS presence |
| O2: Identical experience | B4, B7 | Canonical format ensures uniformity |
| O3: Minimal per-bridge cost | All | The algorithm is the reusable pattern |
| O4: Resilient delivery | B2, B5, B6 | Retry, verification, and rate limiting are algorithmic |
| O5: Auth at identity | B3, B9 | Authentication is step 2 of every inbound flow |

---

## DATA STRUCTURES

### CanonicalMessage

```
CanonicalMessage:
    sender_id: str              # Mind-internal user/bond identifier
    platform: str               # "telegram" | "whatsapp" | "messenger" | "discord" | "slack" | "teams"
    platform_user_id: str       # Platform-native user identifier
    chat_id: str                # Platform-native chat/channel identifier
    message_id: str             # Platform-native message identifier (for deduplication)
    text: str | None            # Message text content, null for media-only
    media: list[MediaAttachment] | None
    reply_to: str | None        # Platform-native ID of message being replied to
    timestamp: datetime         # When the message was sent (platform timestamp)
    raw_metadata: dict          # Platform-specific fields preserved for debugging
```

### MediaAttachment

```
MediaAttachment:
    type: str                   # "image" | "audio" | "video" | "document" | "voice_note" | "sticker"
    url: str | None             # Direct URL to media (if platform provides)
    binary: bytes | None        # Raw binary (if URL not available)
    mime_type: str              # "image/jpeg", "audio/ogg", etc.
    filename: str | None        # Original filename if available
    caption: str | None         # Caption attached to media
    duration_seconds: float | None  # For audio/video
    size_bytes: int | None      # File size
```

### CanonicalResponse

```
CanonicalResponse:
    text: str | None            # Response text
    media: list[MediaAttachment] | None
    reply_to: str | None        # Message ID to reply to (threading)
    platform_hints: dict | None # Optional: platform-specific rendering hints
                                # e.g., {"telegram": {"parse_mode": "MarkdownV2"},
                                #        "discord": {"embed": true}}
```

### PlatformConfig

```
PlatformConfig:
    platform: str               # Platform identifier
    api_token: str              # Bot token or API key
    webhook_secret: str | None  # For webhook signature verification
    webhook_url: str | None     # Public URL for webhook registration
    rate_limit: RateLimit       # Platform-specific rate limits
    max_message_length: int     # Platform's max chars per message
    features: set[str]          # Supported features: {"typing", "read_receipts", "reactions", "threads"}
```

### RateLimit

```
RateLimit:
    messages_per_second: float  # Max outbound messages per second
    messages_per_minute: float  # Max outbound messages per minute (some platforms use this)
    burst_size: int             # Max messages in a burst before throttling
```

---

## ALGORITHM: Inbound Message Flow

### Step 1: Receive Platform Event

The bridge receives a raw event from the platform. For webhook bridges, this is an HTTP POST. For polling bridges, this is the result of a periodic API call. For WebSocket bridges, this is a frame.

```
event = receive_platform_event()
# Webhook: Flask/FastAPI route handler
# Polling: telegram.getUpdates() loop
# WebSocket: on_message handler
```

### Step 2: Verify Event Authenticity

Each platform has a verification method. This MUST happen before any processing.

```
IF platform uses webhook:
    signature = extract_signature(event.headers)
    expected = compute_signature(event.body, webhook_secret)
    IF signature != expected:
        LOG warning: "Invalid webhook signature", source_ip, headers
        RETURN 401

IF platform uses challenge-response (Slack):
    IF event.type == "url_verification":
        RETURN event.challenge  # One-time setup handshake

IF platform uses JWT (Teams):
    token = extract_bearer_token(event.headers)
    IF NOT verify_jwt(token, microsoft_jwks):
        RETURN 401
```

### Step 3: Extract and Deduplicate

Parse the platform-specific payload into fields. Deduplicate using message ID.

```
message_id = extract_message_id(event)

IF message_id IN recent_ids_cache:
    LOG debug: "Duplicate event", message_id
    RETURN 200  # Acknowledge but don't process

recent_ids_cache.add(message_id, ttl=300s)
```

### Step 4: Authenticate Sender

Map platform user ID to a Mind citizen bond. This is the security perimeter.

```
platform_user_id = extract_sender_id(event)
bond = auth.lookup_bond(platform=platform, platform_user_id=platform_user_id)

IF bond is None:
    send_onboarding_prompt(platform_user_id, chat_id)
    LOG info: "Unknown user, onboarding prompted", platform, platform_user_id
    RETURN 200
```

### Step 5: Translate to Canonical Format

Build a CanonicalMessage from the platform event.

```
canonical = CanonicalMessage(
    sender_id=bond.citizen_id,
    platform=platform,
    platform_user_id=platform_user_id,
    chat_id=extract_chat_id(event),
    message_id=message_id,
    text=extract_text(event),
    media=extract_media(event),  # Downloads media if needed
    reply_to=extract_reply_to(event),
    timestamp=extract_timestamp(event),
    raw_metadata=extract_metadata(event)
)
```

### Step 6: Send Typing Indicator

Before forwarding to orchestrator, signal that the citizen is "thinking."

```
IF "typing" IN platform_config.features:
    send_typing_indicator(chat_id)
    start_typing_refresh_loop(chat_id, interval=platform_typing_interval)
```

### Step 7: Forward to Orchestrator

Send the canonical message to the orchestrator and await response.

```
response = await orchestrator.process(canonical)
# This is the slow step -- LLM inference happens here
# Typing indicator keeps refreshing during this wait
```

### Step 8: Handle Orchestrator Response

Translate the response back and deliver. See Outbound Flow.

```
stop_typing_refresh_loop(chat_id)
await deliver_response(response, chat_id, platform_config)
```

---

## ALGORITHM: Outbound Message Flow

### Step 1: Receive Canonical Response

The orchestrator returns a CanonicalResponse. The bridge translates it.

```
response = canonical_response from orchestrator
```

### Step 2: Apply Platform Formatting

Translate canonical format to platform-native format. This is where platform manners live.

```
formatted = format_for_platform(response, platform_config)

# Telegram: MarkdownV2 formatting, inline keyboards if hints present
# Discord: Embed objects, markdown formatting
# Slack: Block Kit JSON
# WhatsApp: Simple text (limited formatting)
# Messenger: Generic templates or plain text
# Teams: Adaptive Cards or plain text
```

### Step 3: Split If Necessary

If the response exceeds platform character limits, split at natural breakpoints.

```
IF len(formatted.text) > platform_config.max_message_length:
    chunks = split_at_breakpoints(formatted.text, platform_config.max_message_length)
ELSE:
    chunks = [formatted.text]
```

### Step 4: Rate-Limited Delivery

Send each chunk respecting platform rate limits.

```
FOR chunk IN chunks:
    await rate_limiter.acquire()  # Blocks if rate limit approached

    result = send_message(chat_id, chunk)

    IF result.failed:
        FOR attempt IN range(1, MAX_RETRIES + 1):
            wait = BACKOFF_BASE * (2 ** attempt)  # Exponential backoff
            await sleep(wait)
            result = send_message(chat_id, chunk)
            IF result.succeeded:
                BREAK

        IF result.failed:
            LOG error: "Delivery failed after retries", chat_id, platform, error
            # Message is lost -- logged for investigation
```

### Step 5: Send Media (If Present)

Media is sent as separate messages or attachments depending on platform.

```
IF response.media:
    FOR attachment IN response.media:
        media_payload = format_media_for_platform(attachment, platform_config)
        await rate_limiter.acquire()
        send_media(chat_id, media_payload)
```

---

## KEY DECISIONS

### D1: Webhook vs Polling Per Platform

```
IF platform has reliable webhook support AND we control a public URL:
    USE webhook  # WhatsApp, Messenger, Slack, Teams, Discord
    WHY: Lower latency, no wasted API calls, platform-preferred

ELSE IF platform webhook is unreliable OR setup is complex:
    USE polling  # Telegram (currently)
    WHY: Telegram webhooks require SSL cert setup; polling is simpler for single-instance deployment
```

### D2: Media Download Timing

```
IF platform provides a stable CDN URL with long TTL:
    PASS URL to orchestrator (lazy download)
    WHY: Avoid unnecessary downloads for messages orchestrator may not need media for

ELSE IF platform URL is ephemeral (expires quickly):
    DOWNLOAD immediately, pass binary or re-hosted URL
    WHY: URL may expire before orchestrator processes the message
```

### D3: Typing Indicator Refresh Interval

```
IF platform typing indicator auto-expires (Telegram: 5s, Discord: 10s):
    REFRESH at 80% of expiry interval (Telegram: 4s, Discord: 8s)
    WHY: Prevents visible gap between indicator expiry and refresh

ELSE IF platform typing indicator persists until message sent (Slack, Teams):
    SEND once, do not refresh
```

---

## DATA FLOW

```
Platform API / Webhook
    |
    v
[1. Receive Event]
    |
    v
[2. Verify Authenticity] -----(invalid)-----> 401 + log
    |
    v (valid)
[3. Deduplicate] -----(duplicate)-----> 200 OK (no-op)
    |
    v (new)
[4. Authenticate Sender] -----(unknown)-----> onboarding prompt
    |
    v (known)
[5. Translate to Canonical]
    |
    v
[6. Typing Indicator ON]
    |
    v
[7. Forward to Orchestrator] -------> (LLM inference)
    |
    v
[8. Receive Response]
    |
    v
[9. Typing Indicator OFF]
    |
    v
[10. Format for Platform]
    |
    v
[11. Split if needed]
    |
    v
[12. Rate-limited Delivery] -----(failed after retry)-----> log error
    |
    v
Platform API (response delivered)
```

---

## COMPLEXITY

**Time:** O(1) per message -- Each message is a fixed pipeline of steps. No iteration over message history.

**Space:** O(n) where n = deduplication cache size -- A small in-memory cache of recent message IDs (TTL 5 minutes, bounded to ~10K entries).

**Bottlenecks:**
- LLM inference time in the orchestrator (step 7) dominates end-to-end latency. Bridges cannot improve this.
- Platform API rate limits are the ceiling for outbound throughput. Bridges must respect, not fight them.
- Media download for large files (video, documents) can add seconds to inbound processing.

---

## HELPER FUNCTIONS

### `split_at_breakpoints(text, max_length)`

**Purpose:** Split long text into chunks that respect platform character limits without cutting mid-sentence.

**Logic:** Try splitting at paragraph breaks (\n\n) first. If paragraphs are too long, split at sentence boundaries (period + space). If sentences are too long, split at word boundaries. Never split mid-word.

### `format_for_platform(response, config)`

**Purpose:** Apply platform-specific formatting to a canonical response.

**Logic:** Check response.platform_hints for platform-specific instructions. Apply platform's markdown dialect. Convert generic formatting (bold, italic, code blocks) to platform-native syntax.

### `compute_webhook_signature(body, secret)`

**Purpose:** Verify webhook authenticity using platform's signature scheme.

**Logic:** Platform-specific HMAC computation. Meta uses SHA-256 HMAC. Slack uses SHA-256 HMAC with timestamp. Teams uses JWT with Microsoft's JWKS.

### `extract_media(event)`

**Purpose:** Parse media attachments from platform-specific event format.

**Logic:** Identify media type from platform fields. Download if URL is ephemeral. Build MediaAttachment objects with mime type detection.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| `runtime/orchestrator/` | `orchestrator.process(canonical_message)` | CanonicalResponse with text and/or media |
| `runtime/auth/` | `auth.lookup_bond(platform, platform_user_id)` | Bond object or None |
| `runtime/auth/` | `auth.create_bond_link(platform, platform_user_id, citizen_id)` | Bond link confirmation |
| Platform SDK | `send_message(chat_id, content)` | Delivery confirmation or error |
| Platform SDK | `send_typing_action(chat_id)` | Acknowledgement |

---

## PLATFORM-SPECIFIC CEREMONY

This section documents the ceremony differences that each bridge must handle. The core algorithm is identical; only the ceremony varies.

### Telegram (LIVE -- Reference)

| Aspect | Detail |
|--------|--------|
| Transport | Long polling via `getUpdates` |
| Auth verification | Bot token in URL path |
| Message format | JSON with `message.text`, `message.photo`, etc. |
| Typing | `sendChatAction(action="typing")`, expires 5s |
| Rate limits | 30 msg/s global, 1 msg/s per chat |
| Max message length | 4096 chars |
| Rich features | InlineKeyboard, MarkdownV2, HTML parse modes |

### WhatsApp (LIVE -- Reference)

| Aspect | Detail |
|--------|--------|
| Transport | WAHA webhook (self-hosted WhatsApp API) |
| Auth verification | Webhook secret signature |
| Message format | JSON with `body`, `type`, media objects |
| Typing | Not natively supported in WAHA |
| Rate limits | Per-number, varies by tier |
| Max message length | 4096 chars |
| Rich features | Templates, buttons (limited), media captions |

### Messenger (S3-S4 -- Next)

| Aspect | Detail |
|--------|--------|
| Transport | Webhook (Meta Platform API) |
| Auth verification | X-Hub-Signature-256 (HMAC SHA-256) |
| Message format | JSON with `messaging[].message.text` |
| Typing | `sender_actions: typing_on/typing_off` |
| Rate limits | 200 calls/user/hour |
| Max message length | 2000 chars |
| Rich features | Generic templates, quick replies, buttons |
| Onboarding | User must initiate conversation (24h policy) |

### Discord (S7-S8)

| Aspect | Detail |
|--------|--------|
| Transport | Gateway WebSocket + REST API for responses |
| Auth verification | Bot token + Ed25519 signature for interactions |
| Message format | JSON with `content`, `embeds`, `attachments` |
| Typing | `POST /channels/{id}/typing`, expires 10s |
| Rate limits | 50 requests/s per bot, 5 msg/s per channel |
| Max message length | 2000 chars |
| Rich features | Embeds, reactions, threads, slash commands, components |

### Slack (S9-S10)

| Aspect | Detail |
|--------|--------|
| Transport | Events API webhook + Web API for responses |
| Auth verification | Signing secret (HMAC SHA-256 with timestamp) |
| Message format | JSON with `event.text`, `event.files` |
| Typing | Not supported for bots |
| Rate limits | Tier-based (1+ req/s for most methods) |
| Max message length | 40000 chars (but 3000 chars recommended for readability) |
| Rich features | Block Kit (sections, actions, modals), threads, reactions |
| B2B angle | Workspace installation, OAuth flow, enterprise grid |

### Teams (S9-S10)

| Aspect | Detail |
|--------|--------|
| Transport | Bot Framework webhook |
| Auth verification | JWT (Azure AD) with JWKS validation |
| Message format | Activity object with `text`, `attachments` |
| Typing | `sendActivities` with `typing` activity type |
| Rate limits | Throttled by Bot Framework (exact limits vary) |
| Max message length | 28000 chars (Adaptive Card), plain text varies |
| Rich features | Adaptive Cards, task modules, message extensions |
| B2B angle | Teams app catalog, admin-approved deployment |

---

## MARKERS

<!-- @mind:todo Define canonical message format as a Pydantic model in shared types module -->
<!-- @mind:proposition Voice bridge could be generalized: WebSocket transport adapter pattern for any real-time protocol -->
<!-- @mind:escalation Messenger 24h policy: after 24h of user inactivity, bot can only send via approved message templates. Need product decision on how citizen handles this constraint. -->
