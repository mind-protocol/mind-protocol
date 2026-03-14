# Chat Bridges -- Behaviors: Observable Message Flow Effects

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: --
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Chat_Bridges.md
THIS:            BEHAVIORS_Chat_Bridges.md (you are here)
PATTERNS:        ./PATTERNS_Chat_Bridges.md
ALGORITHM:       ./ALGORITHM_Chat_Bridges.md
VALIDATION:      ./VALIDATION_Chat_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Chat_Bridges.md
SYNC:            ./SYNC_Chat_Bridges.md

IMPL:            mind-mcp/runtime/bridges/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Inbound Messages Reach The Orchestrator

**Why:** The entire purpose of a bridge is to deliver human messages to the citizen's brain. If this fails, the citizen is deaf on that platform.

```
GIVEN:  A human sends a text message on a supported platform
WHEN:   The bridge receives the message (via webhook or poll)
THEN:   The message is translated to canonical format and forwarded to the orchestrator
AND:    The orchestrator receives: sender identity, message text, platform metadata, timestamp
AND:    The bridge does not interpret, modify, or filter message content
```

### B2: Orchestrator Responses Reach The Human

**Why:** A citizen that hears but cannot speak is worse than one that is absent. Response delivery is the second half of presence.

```
GIVEN:  The orchestrator produces a response for a human
WHEN:   The bridge receives the canonical response
THEN:   The response is translated to the platform's native format
AND:    The response is delivered via the platform's send API
AND:    Delivery failure triggers retry with exponential backoff (max 3 attempts)
AND:    If all retries fail, the failure is logged with full context (platform, user ID, error, response payload)
```

### B3: Unknown Users Are Rejected At The Edge

**Why:** Unauthenticated messages must never reach the orchestrator. The bridge is the perimeter. Letting unknown users through wastes orchestrator resources and creates security surface.

```
GIVEN:  A message arrives from a platform user ID not linked to any citizen bond
WHEN:   The bridge attempts authentication lookup
THEN:   The message is rejected before reaching the orchestrator
AND:    The bridge responds to the user with an onboarding prompt (platform-appropriate)
AND:    The rejection is logged (platform, user ID, timestamp) for monitoring
```

### B4: Typing Indicators Signal Citizen Presence

**Why:** When a human sends a message and sees nothing for 3-10 seconds (LLM inference time), they feel ignored. A typing indicator transforms waiting into anticipation. The citizen feels alive.

```
GIVEN:  A message has been accepted and forwarded to the orchestrator
WHEN:   The orchestrator is processing (LLM inference in progress)
THEN:   The bridge sends a typing indicator to the platform
AND:    The typing indicator is refreshed every N seconds (platform-specific interval)
AND:    The typing indicator stops when the response is delivered
```

### B5: Webhook Verification Protects Bridge Endpoints

**Why:** Webhook-based bridges expose HTTP endpoints. Without verification, anyone can POST fake messages. Each platform has its own verification scheme (Meta signature, Slack challenge, Teams JWT). The bridge must validate before processing.

```
GIVEN:  A webhook-based bridge receives an HTTP request
WHEN:   The request arrives at the bridge endpoint
THEN:   The bridge verifies the request signature/token using the platform's verification method
AND:    Invalid requests are rejected with 401/403 and logged
AND:    Valid requests proceed to message processing
```

### B6: Rate Limits Are Respected Preemptively

**Why:** Hitting platform rate limits causes message delivery failures, temporary bans, and degraded citizen presence. Respecting limits preemptively avoids reactive error handling.

```
GIVEN:  The bridge is sending responses to a platform
WHEN:   Outbound message rate approaches the platform's rate limit
THEN:   The bridge throttles outbound messages (queue with delay, not drop)
AND:    Queued messages are delivered in order when rate limit window resets
AND:    If queue depth exceeds threshold, the oldest non-critical messages are logged and dropped
```

### B7: Media Messages Are Forwarded With Type Metadata

**Why:** Citizens can receive images, voice notes, documents, and videos. The orchestrator needs to know the media type to invoke the right processing (vision model for images, speech-to-text for voice, etc.).

```
GIVEN:  A human sends a non-text message (image, voice note, document, video)
WHEN:   The bridge receives the media message
THEN:   The bridge downloads the media from the platform's CDN (if needed)
AND:    The canonical message includes: media_type, media_url or binary, mime_type, optional caption
AND:    The orchestrator receives enough information to process the media without platform-specific knowledge
```

### B8: Bridge Startup Registers With Platform

**Why:** Bridges need to tell the platform where to send messages (webhook URL) or begin polling. This is the boot sequence. If it fails, the bridge is running but deaf.

```
GIVEN:  A bridge process starts
WHEN:   Initialization runs
THEN:   For webhook bridges: register/verify the webhook URL with the platform API
THEN:   For polling bridges: begin the polling loop
AND:    Startup logs confirm: platform connected, webhook registered or polling started, auth verified
AND:    If registration fails, the bridge exits with a clear error (not a silent loop)
```

### B9: Human Onboards By Linking Platform Identity

**Why:** Before a bridge can route messages, it needs to know which citizen bond this platform user belongs to. Onboarding links a platform-specific ID (Telegram user ID, Discord user ID) to a Mind citizen-human bond. This happens once per platform per human.

```
GIVEN:  A new user messages the bridge for the first time
WHEN:   The bridge finds no existing bond link for this platform user ID
THEN:   The bridge initiates the onboarding flow
AND:    The human provides their Mind identity (e.g., via a token, QR code, or DM command)
AND:    The bridge creates the platform_user_id -> citizen_bond mapping
AND:    Subsequent messages from this user are routed to their citizen automatically
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Ubiquitous presence | The citizen can hear on this platform |
| B2 | O1: Ubiquitous presence, O4: Resilient delivery | The citizen can speak on this platform, with retry |
| B3 | O5: Auth anchored to identity | Security perimeter at the edge |
| B4 | O2: Identical experience | Presence feeling consistent across platforms |
| B5 | O4: Resilient delivery | Protects against spoofed messages |
| B6 | O4: Resilient delivery | Prevents platform bans from rate limit violations |
| B7 | O2: Identical experience | Rich media works across platforms |
| B8 | O1: Ubiquitous presence | Bridge must boot correctly to function at all |
| B9 | O5: Auth anchored to identity | Maps platform identity to Mind identity once |

---

## INPUTS / OUTPUTS

### Primary Function: `handle_inbound_message()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| platform_event | dict | Raw event payload from platform webhook or poll |
| platform_config | PlatformConfig | API keys, webhook secrets, rate limit params |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| canonical_message | CanonicalMessage | Platform-agnostic message with sender, text, media, metadata |

**Side Effects:**

- Typing indicator sent to platform
- Authentication lookup against bond registry
- Rejection response sent for unknown users

### Primary Function: `handle_outbound_response()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| canonical_response | CanonicalResponse | Platform-agnostic response from orchestrator |
| platform_context | PlatformContext | Chat ID, thread ID, reply-to metadata |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| delivery_status | DeliveryStatus | success/failed/retrying with platform message ID |

**Side Effects:**

- Message sent via platform API
- Typing indicator cleared
- Delivery logged

---

## EDGE CASES

### E1: Platform API Is Down

```
GIVEN:  The platform's API returns 5xx errors or times out
THEN:   The bridge queues outbound messages for retry (max queue: 100 messages, max age: 5 minutes)
AND:    If the platform stays down beyond max age, queued messages are logged as undeliverable and dropped
AND:    The bridge does NOT crash -- it continues accepting inbound messages for when the platform recovers
```

### E2: Orchestrator Is Slow (>30 seconds)

```
GIVEN:  The orchestrator takes more than 30 seconds to respond
THEN:   The bridge continues refreshing the typing indicator
AND:    If the orchestrator exceeds 120 seconds, the bridge sends a fallback: "I'm thinking about this -- give me a moment"
AND:    The actual response is delivered when it arrives, as a follow-up message
```

### E3: Duplicate Webhook Delivery

```
GIVEN:  The platform delivers the same webhook event twice (common with at-least-once delivery)
THEN:   The bridge deduplicates using the platform's event/message ID
AND:    The second delivery is acknowledged (200 OK) but not processed
```

### E4: Human Sends Rapid-Fire Messages

```
GIVEN:  A human sends 5+ messages in quick succession
THEN:   Each message is forwarded individually to the orchestrator
AND:    The orchestrator handles context assembly -- the bridge does not batch or debounce
```

### E5: Message Exceeds Platform Character Limit

```
GIVEN:  The orchestrator response exceeds the platform's max message length (e.g., 4096 chars for Telegram)
THEN:   The bridge splits the response into multiple messages at natural breakpoints (paragraph, sentence)
AND:    Messages are sent in order with minimal delay between them
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Bridge Interprets Message Content

```
GIVEN:   Any inbound message
WHEN:    The bridge processes it
MUST NOT: Parse, filter, or route based on message content (no keyword detection, no command parsing beyond platform-native bot commands)
INSTEAD:  Forward everything to the orchestrator as canonical text
```

### A2: Bridge Stores Conversation History

```
GIVEN:   Messages flowing through the bridge
WHEN:    Processing completes
MUST NOT: Persist messages in local storage, database, or files
INSTEAD:  The orchestrator owns all conversation state; the bridge is a stateless pipe
```

### A3: Silent Message Drop

```
GIVEN:   A message that fails to deliver
WHEN:    Retry attempts are exhausted
MUST NOT: Silently discard the message with no trace
INSTEAD:  Log the failure with full context (message content hash, platform error, user ID, timestamp)
```

### A4: Bridge Makes LLM Calls

```
GIVEN:   Any processing step
WHEN:    The bridge handles a message
MUST NOT: Call any LLM API, embedding API, or AI service directly
INSTEAD:  All intelligence routes through the orchestrator
```

---

## MARKERS

<!-- @mind:todo Define exact onboarding flow for B9 -- token-based or command-based linking? -->
<!-- @mind:proposition Consider B10: Read receipts (mark orchestrator-consumed messages as read on platforms that support it) -->
