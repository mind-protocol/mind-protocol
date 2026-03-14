# Chat Bridges -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Chat_Bridges.md
PATTERNS:        ./PATTERNS_Chat_Bridges.md
BEHAVIORS:       ./BEHAVIORS_Chat_Bridges.md
THIS:            VALIDATION_Chat_Bridges.md (you are here)
ALGORITHM:       ./ALGORITHM_Chat_Bridges.md
IMPLEMENTATION:  ./IMPLEMENTATION_Chat_Bridges.md
SYNC:            ./SYNC_Chat_Bridges.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants define the properties that, if violated, would mean the chat bridge system has failed its purpose. A bridge that violates any CRITICAL invariant is not a bridge -- it is a broken pipe that either leaks messages, accepts impostors, or silently fails.

---

## INVARIANTS

### V1: Message Integrity Through Transport

**Why we care:** If a message arrives garbled, truncated, or with wrong attribution, the citizen hears something the human never said. The relationship is built on accurate communication. Corrupted transport is a lie.

```
MUST:   Every inbound message delivered to the orchestrator contains the exact text
        the human sent, with correct sender identity, and accurate timestamp.
NEVER:  Message text is modified, truncated, or attributed to the wrong sender
        between platform receipt and orchestrator delivery.
```

### V2: Authentication Perimeter Holds

**Why we care:** If unauthenticated messages reach the orchestrator, unknown users can interact with citizens, consume resources, and potentially access private conversation context. The bridge is the only security boundary between the public internet and the citizen's mind.

```
MUST:   Every message forwarded to the orchestrator has a verified sender identity
        linked to an existing citizen bond.
NEVER:  A message from an unlinked platform user ID reaches the orchestrator.
```

### V3: No Silent Message Loss

**Why we care:** If a citizen's response is generated but never delivered, the human experiences abandonment. If a human's message is received but never forwarded, the citizen is deaf. Silent loss is the worst failure mode because no one knows it happened.

```
MUST:   Every message that enters the pipeline either reaches its destination
        or produces a logged, traceable failure record.
NEVER:  A message disappears without either successful delivery or an explicit
        error log entry with message ID, timestamp, platform, and failure reason.
```

### V4: Webhook Verification Prevents Spoofing

**Why we care:** Webhook endpoints are public URLs. Without signature verification, anyone can POST fabricated messages. A spoofed message could impersonate a human and inject content into a citizen's conversation.

```
MUST:   Every webhook-delivered event is verified using the platform's signature
        scheme before any processing occurs.
NEVER:  An event with an invalid or missing signature is processed beyond the
        verification step.
```

### V5: Platform Rate Limits Are Never Exceeded

**Why we care:** Exceeding rate limits causes platform-imposed throttling, temporary bans, or permanent API key revocation. A banned bridge is a dead channel. Rate limit compliance is a survival constraint, not a courtesy.

```
MUST:   Outbound message rate stays at or below the platform's published rate limits
        at all times, including burst scenarios.
NEVER:  The bridge sends messages faster than the platform allows, even under load.
```

### V6: Bridge Statelesness Is Preserved

**Why we care:** If a bridge stores conversation state locally, a bridge restart loses context. If two bridge instances run simultaneously (scaling, rolling deploy), state diverges. Statelessness is what makes bridges disposable and replaceable.

```
MUST:   A bridge can be killed and restarted at any time without losing any
        conversation context or message history.
NEVER:  Conversation state, message history, or user context is stored in the
        bridge process memory or local filesystem.
```

### V7: Bridge Does Not Contain Intelligence

**Why we care:** If bridges contain LLM calls, content filtering, or routing logic, intelligence fragments across N bridges. Changes to citizen behavior require N updates instead of 1. The orchestrator is the single source of intelligence; bridges are transport.

```
MUST:   All response generation, content decisions, and conversation management
        happen in the orchestrator.
NEVER:  A bridge calls an LLM API, makes content-based routing decisions, or
        modifies response text beyond format translation.
```

### V8: Deduplication Prevents Double Processing

**Why we care:** Platforms use at-least-once delivery for webhooks. Without deduplication, a human's single message could be processed twice, generating two citizen responses. This is confusing and breaks conversation flow.

```
MUST:   Each unique platform message is processed exactly once, identified by
        the platform's native message ID.
NEVER:  The same message (same platform message ID) is forwarded to the
        orchestrator more than once.
```

### V9: Onboarding Completes Before Message Routing

**Why we care:** A human who messages a bridge for the first time must link their platform identity to their Mind citizen bond before any conversation flows. Without this link, the bridge cannot authenticate or route messages.

```
MUST:   New platform users complete identity linking before their messages
        are forwarded to the orchestrator.
NEVER:  Messages from unlinked users are silently discarded or routed to
        a default/shared citizen.
```

### V10: Media Type Is Accurately Reported

**Why we care:** The orchestrator uses media type to select processing (vision model for images, STT for voice notes). If an image is reported as a document, the wrong model processes it. Media type accuracy determines processing correctness.

```
MUST:   Media attachments include accurate type, mime_type, and binary/URL
        that the orchestrator can process without platform-specific knowledge.
NEVER:  Media type is guessed from file extension alone when the platform
        provides explicit type information.
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Bridge is unusable or dangerous |
| **HIGH** | Major value lost | Bridge works but is unreliable or insecure |
| **MEDIUM** | Partial value lost | Bridge works but with degraded experience |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Message integrity | CRITICAL |
| V2 | Authentication perimeter | CRITICAL |
| V3 | No silent message loss | CRITICAL |
| V4 | Webhook spoofing prevention | CRITICAL |
| V5 | Platform rate limit compliance | HIGH |
| V6 | Bridge statelessness | HIGH |
| V7 | Intelligence centralization | HIGH |
| V8 | Message deduplication | HIGH |
| V9 | Onboarding before routing | MEDIUM |
| V10 | Media type accuracy | MEDIUM |

---

## MARKERS

<!-- @mind:todo V4 needs per-platform test: verify signature verification logic against each platform's documented scheme -->
<!-- @mind:proposition V11 candidate: Latency budget -- bridge processing (excluding orchestrator) should add <500ms to end-to-end latency -->
<!-- @mind:escalation V5: Need exact rate limit numbers for Teams Bot Framework -- Microsoft docs are vague on specific limits -->
