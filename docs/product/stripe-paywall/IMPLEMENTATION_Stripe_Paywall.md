# Stripe Paywall -- Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stripe_Paywall.md
BEHAVIORS:       ./BEHAVIORS_Stripe_Paywall.md
PATTERNS:        ./PATTERNS_Stripe_Paywall.md
ALGORITHM:       ./ALGORITHM_Stripe_Paywall.md
VALIDATION:      ./VALIDATION_Stripe_Paywall.md
THIS:            IMPLEMENTATION_Stripe_Paywall.md (you are here)
HEALTH:          (not yet created)
SYNC:            ./SYNC_Stripe_Paywall.md

IMPL:            mind-ops/billing/ (not yet created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

The implementation spans two repositories and three concerns:

```
mind-ops/
├── billing/
│   ├── __init__.py                                    # Exports: create_checkout_session, handle_webhook
│   ├── stripe_checkout_session_creator.py             # Checkout Session creation for all tiers
│   ├── stripe_webhook_signature_verifier_and_router.py # Signature verification, deduplication, event routing
│   ├── stripe_webhook_event_handlers.py               # Per-event-type handlers (checkout, subscription, invoice)
│   ├── tier_config_and_price_mapping.py               # TIER_CONFIG, reverse price lookup, feature definitions
│   └── subscription_state_persistence.py              # DB read/write for user subscription state

mind-mcp/
├── rate_limiting/
│   ├── tier_based_message_rate_limiter.py             # Per-request rate limit check, message counting
│   └── tier_context_builder_for_llm_prompt.py         # Formats tier context for LLM system prompt injection
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `billing/stripe_checkout_session_creator.py` | Creates Stripe Checkout Sessions with correct price, customer, metadata | `create_checkout_session()` | ~80 | OK |
| `billing/stripe_webhook_signature_verifier_and_router.py` | Verifies webhook signature, deduplicates events, routes to handlers | `handle_webhook()`, `verify_signature()`, `deduplicate_event()` | ~100 | OK |
| `billing/stripe_webhook_event_handlers.py` | Handles each webhook event type, updates user tier | `handle_checkout_completed()`, `handle_subscription_updated()`, `handle_subscription_deleted()`, `handle_payment_failed()` | ~120 | OK |
| `billing/tier_config_and_price_mapping.py` | Static tier configuration, price-to-tier reverse lookup | `TIER_CONFIG`, `reverse_lookup_tier()`, `compute_locked_features()`, `recommended_upgrade()` | ~80 | OK |
| `billing/subscription_state_persistence.py` | Database operations for subscription state | `get_user_subscription()`, `update_user()`, `get_user_by_stripe_customer()`, `record_event()`, `event_exists()` | ~100 | OK |
| `rate_limiting/tier_based_message_rate_limiter.py` | Rate limit check per request, message count management | `check_rate_limit()`, `increment_message_count()`, `get_message_count()` | ~80 | OK |
| `rate_limiting/tier_context_builder_for_llm_prompt.py` | Builds tier context dict for LLM prompt injection | `build_tier_context()` | ~50 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

All estimated sizes are well within OK range. Each file has a single clear responsibility.

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Event-Driven + Service Layer

**Why this pattern:** Stripe webhooks are inherently event-driven. The billing service reacts to external events (webhooks) and translates them into state changes. The rate limiter is a service layer that reads state and enforces policy. No orchestration layer needed -- the event flow is linear.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Event Router | `stripe_webhook_signature_verifier_and_router.py` | Maps event types to handler functions without conditional chains |
| Static Config | `tier_config_and_price_mapping.py` | Single source of truth for tier definitions loaded at startup |
| Fail-Closed Guard | `tier_based_message_rate_limiter.py` | Denies on any error, never defaults to allow |
| Idempotency Table | `subscription_state_persistence.py` | Stores processed event IDs to prevent duplicate processing |

### Anti-Patterns to Avoid

- **Payment provider abstraction layer**: Do not abstract Stripe behind a generic "PaymentProvider" interface. We are committed to Stripe. An abstraction adds complexity for a migration scenario that is unlikely and would require a full rewrite anyway.
- **In-memory tier cache without invalidation**: Do not cache user tiers in process memory without a mechanism to invalidate on webhook receipt. Stale caches violate V1.
- **Fallback to allow on rate limiter failure**: Do not add a "fail open" fallback. This directly violates V6.
- **Client-side tier checks**: Do not rely on the client to enforce tier limits. The client can be modified. Enforcement lives server-side in mind-mcp.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Billing service | Stripe communication, subscription state | Rate limiting, LLM calls, user auth | `create_checkout_session()`, `handle_webhook()` |
| Rate limiter | Message counting, tier enforcement | Stripe API, payment processing | `check_rate_limit() -> RateLimitResult` |
| Tier context | Context formatting for LLM | LLM call itself, prompt engineering | `build_tier_context() -> dict` |

---

## SCHEMA

### UserSubscription (database table)

```yaml
UserSubscription:
  required:
    - user_id: string               # MIND user ID, primary key
    - tier: string                   # free|pro|pro_plus|premium|solo|practice|studio|team|business
    - payment_status: string         # ok|past_due
    - updated_at: timestamp          # Last state change
  optional:
    - stripe_customer_id: string     # Stripe Customer ID (null for users who never started checkout)
    - subscription_id: string        # Stripe Subscription ID (null for free users)
    - org_id: string                 # Organization ID for B2B tiers
  constraints:
    - tier defaults to "free"
    - payment_status defaults to "ok"
    - stripe_customer_id is unique when not null
```

### DailyMessageCount (database table or Redis key)

```yaml
DailyMessageCount:
  required:
    - user_id: string
    - date: date                     # UTC calendar date
    - count: integer                 # Messages sent today
  constraints:
    - count starts at 0
    - Composite key: (user_id, date)
    - Records older than 7 days can be purged
```

### ProcessedWebhookEvent (database table)

```yaml
ProcessedWebhookEvent:
  required:
    - event_id: string               # Stripe event ID, primary key
    - processed_at: timestamp
  constraints:
    - Records older than 30 days can be purged
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| create_checkout_session | `billing/stripe_checkout_session_creator.py` | REST API call from frontend when user clicks upgrade |
| handle_webhook | `billing/stripe_webhook_signature_verifier_and_router.py` | HTTP POST from Stripe to /webhooks/stripe |
| check_rate_limit | `rate_limiting/tier_based_message_rate_limiter.py` | mind-mcp on every incoming user message |
| build_tier_context | `rate_limiting/tier_context_builder_for_llm_prompt.py` | mind-mcp before constructing LLM prompt |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Checkout Flow: User Initiates Upgrade

This flow covers the path from a user's upgrade action to a Stripe Checkout redirect. It crosses the API boundary and calls the Stripe API.

```yaml
flow:
  name: checkout_flow
  purpose: Convert a user's upgrade intent into a Stripe Checkout Session URL
  scope: API request in, Stripe Checkout URL out
  steps:
    - id: step_1
      description: Receive upgrade request with user_id and target_tier
      file: billing/stripe_checkout_session_creator.py
      function: create_checkout_session
      input: user_id, target_tier, success_url, cancel_url
      output: checkout_url
      trigger: REST API POST /billing/checkout
      side_effects: Stripe Customer created (if new), Checkout Session created in Stripe
  docking_points:
    guidance:
      include_when: API boundary, Stripe API call
      omit_when: internal variable passing
      selection_notes: Dock at the API entry and the Stripe API call
    available:
      - id: dock_checkout_request
        type: api
        direction: input
        file: billing/stripe_checkout_session_creator.py
        function: create_checkout_session
        trigger: POST /billing/checkout
        payload: {user_id, target_tier}
        async_hook: not_applicable
        needs: none
        notes: Entry point for checkout flow
      - id: dock_stripe_session_created
        type: api
        direction: output
        file: billing/stripe_checkout_session_creator.py
        function: create_checkout_session
        trigger: stripe.checkout.Session.create() returns
        payload: {session_id, checkout_url}
        async_hook: not_applicable
        needs: none
        notes: Confirms Stripe session was created successfully
    health_recommended:
      - dock_id: dock_checkout_request
        reason: Monitors checkout initiation volume and failure rate
```

### Webhook Flow: Stripe Notifies State Change

This flow covers webhook receipt, verification, deduplication, and tier state mutation. It is the most critical flow -- all billing state changes pass through it.

```yaml
flow:
  name: webhook_flow
  purpose: Process Stripe webhook events and update user subscription state
  scope: Stripe HTTP POST in, database state change out
  steps:
    - id: step_1
      description: Verify webhook signature against endpoint secret
      file: billing/stripe_webhook_signature_verifier_and_router.py
      function: verify_signature
      input: raw_payload, stripe_signature_header
      output: verified_event
      trigger: POST /webhooks/stripe
      side_effects: none
    - id: step_2
      description: Check event ID for deduplication
      file: billing/stripe_webhook_signature_verifier_and_router.py
      function: deduplicate_event
      input: event.id
      output: is_new (bool)
      trigger: after signature verification
      side_effects: event_id recorded in ProcessedWebhookEvent table
    - id: step_3
      description: Route to event-type-specific handler
      file: billing/stripe_webhook_event_handlers.py
      function: handle_checkout_completed / handle_subscription_updated / handle_subscription_deleted / handle_payment_failed
      input: verified_event
      output: none (side effect: DB update)
      trigger: event type match
      side_effects: user tier, subscription_id, payment_status updated in UserSubscription table
  docking_points:
    guidance:
      include_when: Security boundary (signature verification), state mutation (tier update)
      omit_when: Internal routing logic
      selection_notes: Dock at signature verification (security) and tier update (state change)
    available:
      - id: dock_webhook_received
        type: api
        direction: input
        file: billing/stripe_webhook_signature_verifier_and_router.py
        function: handle_webhook
        trigger: POST /webhooks/stripe
        payload: {raw_body, stripe_signature}
        async_hook: not_applicable
        needs: none
        notes: Entry point for all billing state changes
      - id: dock_signature_result
        type: auth
        direction: output
        file: billing/stripe_webhook_signature_verifier_and_router.py
        function: verify_signature
        trigger: signature check completes
        payload: {verified: bool, event_type: string}
        async_hook: not_applicable
        needs: none
        notes: Critical security checkpoint
      - id: dock_tier_updated
        type: db
        direction: output
        file: billing/subscription_state_persistence.py
        function: update_user
        trigger: after event handler processes event
        payload: {user_id, old_tier, new_tier}
        async_hook: optional
        needs: add event emission after tier change for cache invalidation
        notes: The moment billing state changes -- most important dock
    health_recommended:
      - dock_id: dock_signature_result
        reason: Monitors for spoofed webhook attempts (security)
      - dock_id: dock_tier_updated
        reason: Monitors tier state changes for correctness and audit
```

### Rate Limit Flow: Message Gating

This flow runs on every user message in mind-mcp. It determines whether the message is allowed based on the user's tier and daily usage.

```yaml
flow:
  name: rate_limit_flow
  purpose: Gate user messages based on tier and daily usage
  scope: User message in, allow/deny decision out
  steps:
    - id: step_1
      description: Load user subscription state and daily message count
      file: rate_limiting/tier_based_message_rate_limiter.py
      function: check_rate_limit
      input: user_id
      output: RateLimitResult(allowed, tier_context)
      trigger: Every incoming user message
      side_effects: message count incremented if allowed
  docking_points:
    guidance:
      include_when: Rate limit decision point
      omit_when: DB read details
      selection_notes: Dock at the decision point (allow/deny)
    available:
      - id: dock_rate_limit_decision
        type: api
        direction: output
        file: rate_limiting/tier_based_message_rate_limiter.py
        function: check_rate_limit
        trigger: after tier and count lookup
        payload: {user_id, allowed, tier, messages_used, messages_limit}
        async_hook: not_applicable
        needs: none
        notes: Every message passes through this decision
    health_recommended:
      - dock_id: dock_rate_limit_decision
        reason: Monitors rate limit enforcement and denial rates per tier
```

---

## LOGIC CHAINS

### LC1: Upgrade-to-Active Subscription

**Purpose:** Full path from user upgrade intent to active tier access.

```
User clicks "Upgrade to Pro"
  -> billing.create_checkout_session(user_id, "pro")
    -> stripe.checkout.Session.create(price=STRIPE_PRO, customer=cust_id)
      -> return checkout_url
        -> User completes payment on Stripe
          -> Stripe fires checkout.session.completed
            -> billing.handle_webhook(payload, signature)
              -> billing.handle_checkout_completed(event)
                -> db.update_user(user_id, tier="pro")
```

**Data transformation:**
- Input: `user_id + "pro"` -- user intent
- After checkout creation: `checkout_url` -- Stripe-hosted page
- After payment: `webhook event` -- Stripe confirmation
- Output: `user.tier = "pro"` in database -- access activated

### LC2: Message with Rate Limiting and Upsell

**Purpose:** Full path from user message to LLM response with tier awareness.

```
User sends message
  -> mcp.check_rate_limit(user_id)
    -> db.get_user_subscription(user_id) -> {tier: "free"}
    -> db.get_message_count(user_id, today) -> 9
    -> TIER_CONFIG["free"].msg_limit -> 10
    -> 9 < 10 -> allowed
    -> db.increment_message_count(user_id, today) -> 10
  -> mcp.build_tier_context(user_sub, 10, 10)
    -> {tier: "free", messages_used: 10, messages_limit: 10, locked_features: [...]}
  -> inject tier_context into LLM system prompt
  -> LLM responds, possibly mentioning "you've used your last free message today"
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
billing/stripe_checkout_session_creator.py
    └── imports -> billing/tier_config_and_price_mapping.py
    └── imports -> billing/subscription_state_persistence.py

billing/stripe_webhook_signature_verifier_and_router.py
    └── imports -> billing/stripe_webhook_event_handlers.py
    └── imports -> billing/subscription_state_persistence.py

billing/stripe_webhook_event_handlers.py
    └── imports -> billing/tier_config_and_price_mapping.py
    └── imports -> billing/subscription_state_persistence.py

rate_limiting/tier_based_message_rate_limiter.py
    └── imports -> (shared DB module, reads UserSubscription)

rate_limiting/tier_context_builder_for_llm_prompt.py
    └── imports -> (tier config, either shared or duplicated read-only copy)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `stripe` | Stripe API client (Checkout, Webhooks, Subscriptions) | `stripe_checkout_session_creator.py`, `stripe_webhook_signature_verifier_and_router.py`, `stripe_webhook_event_handlers.py` |
| `fastapi` or framework router | HTTP endpoint definitions | webhook handler, checkout API |
| Database driver (psycopg2/asyncpg/sqlalchemy) | User subscription state persistence | `subscription_state_persistence.py` |
| `redis` (optional) | Daily message count with TTL | `tier_based_message_rate_limiter.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| User tier | `UserSubscription` table | Per user | Created on first login (default: free), updated by webhooks |
| Daily message count | `DailyMessageCount` table or Redis | Per user per day | Created on first message of the day, expires/purges after 7 days |
| Processed event IDs | `ProcessedWebhookEvent` table | Per Stripe event | Created on first processing, purged after 30 days |
| TIER_CONFIG | In-memory (loaded at startup) | Global | Static for the lifetime of the process |

### State Transitions

```
User Tier:
free ──checkout.session.completed──> pro/pro_plus/premium/solo/practice/studio/team/business
pro  ──subscription.updated──> pro_plus/premium
pro_plus ──subscription.updated──> pro/premium
premium ──subscription.updated──> pro/pro_plus
any_paid ──subscription.deleted──> free

Payment Status:
ok ──invoice.payment_failed──> past_due
past_due ──invoice.paid──> ok
past_due ──subscription.deleted──> ok (tier also goes to free)
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Load TIER_CONFIG from environment variables (price IDs)
2. Verify Stripe API key is set (STRIPE_SECRET_KEY)
3. Verify webhook endpoint secret is set (STRIPE_WEBHOOK_SECRET)
4. Register HTTP routes: POST /billing/checkout, POST /webhooks/stripe
5. System ready
```

### Main Loop / Request Cycle (Webhook)

```
1. POST /webhooks/stripe received
2. Verify signature -> reject if invalid
3. Deduplicate event -> ignore if already processed
4. Route to handler by event type
5. Handler updates database
6. Return HTTP 200
```

### Main Loop / Request Cycle (Rate Limit)

```
1. User message arrives at mind-mcp
2. check_rate_limit(user_id) called
3. Read tier and message count from DB
4. If over limit: return deny with tier_context
5. If under limit: increment count, return allow with tier_context
6. Tier context injected into LLM prompt
7. LLM call proceeds
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| Webhook handler | Async (single-threaded event loop) | Webhooks arrive sequentially per endpoint, but concurrent with user requests |
| Rate limiter | Async per request | Multiple users checked concurrently; message count increment must be atomic |
| Checkout session creation | Async per request | Stripe API call is I/O-bound |

**Key concurrency concern:** Message count increment must be atomic. Two concurrent requests from the same user must not both read count=9, both decide to allow, and both increment to 10. Use Redis INCR (atomic) or database UPDATE ... RETURNING (atomic).

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `STRIPE_SECRET_KEY` | Environment variable | none (required) | Stripe API secret key |
| `STRIPE_WEBHOOK_SECRET` | Environment variable | none (required) | Webhook endpoint signing secret |
| `STRIPE_PRO` | Environment variable | none (required) | Stripe Price ID for Pro tier |
| `STRIPE_PROPLUS` | Environment variable | none (required) | Stripe Price ID for Pro+ tier |
| `STRIPE_PREMIUM` | Environment variable | none (required) | Stripe Price ID for Premium tier |
| `STRIPE_SOLO` | Environment variable | none (required) | Stripe Price ID for Solo tier |
| `STRIPE_PRACTICE` | Environment variable | none (required) | Stripe Price ID for Practice tier |
| `STRIPE_STUDIO` | Environment variable | none (required) | Stripe Price ID for Studio tier |
| `STRIPE_TEAM` | Environment variable | none (required) | Stripe Price ID for Team tier |
| `STRIPE_BUSINESS` | Environment variable | none (required) | Stripe Price ID for Business tier |
| `FREE_DAILY_MESSAGE_LIMIT` | Environment variable | 10 | Max messages per day for free tier |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

No code exists yet. When code is written, each file should include:

```python
# DOCS: docs/product/stripe-paywall/IMPLEMENTATION_Stripe_Paywall.md
```

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM: Checkout Session Creation | `billing/stripe_checkout_session_creator.py:create_checkout_session` |
| ALGORITHM: Webhook Processing | `billing/stripe_webhook_signature_verifier_and_router.py:handle_webhook` |
| ALGORITHM: Rate Limit Check | `rate_limiting/tier_based_message_rate_limiter.py:check_rate_limit` |
| BEHAVIOR B1 | `billing/stripe_checkout_session_creator.py:create_checkout_session` |
| BEHAVIOR B2 | `billing/stripe_webhook_event_handlers.py:handle_checkout_completed` |
| BEHAVIOR B3 | `rate_limiting/tier_based_message_rate_limiter.py:check_rate_limit` |
| BEHAVIOR B4 | `rate_limiting/tier_context_builder_for_llm_prompt.py:build_tier_context` |
| BEHAVIOR B5 | `billing/stripe_webhook_event_handlers.py:handle_subscription_deleted` |
| VALIDATION V2 | `billing/stripe_webhook_signature_verifier_and_router.py:verify_signature` |
| VALIDATION V3 | `billing/stripe_webhook_signature_verifier_and_router.py:deduplicate_event` |

---

## EXTRACTION CANDIDATES

No extraction needed. All files are estimated under 120 lines.

---

## MARKERS

<!-- @mind:todo Decide whether mind-mcp rate limiter imports tier_config directly or receives it via shared config -->
<!-- @mind:todo Determine database migration strategy for UserSubscription table -- does it extend existing users table or is it a new table? -->
<!-- @mind:escalation Need to confirm mind-ops web framework (FastAPI? Flask?) to determine webhook route registration pattern -->
