# Stripe Paywall -- Behaviors: Subscription Lifecycle, Rate Limiting, and Conversational Upsell

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: not yet
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stripe_Paywall.md
PATTERNS:        ./PATTERNS_Stripe_Paywall.md
THIS:            BEHAVIORS_Stripe_Paywall.md (you are here)
ALGORITHM:       ./ALGORITHM_Stripe_Paywall.md
VALIDATION:      ./VALIDATION_Stripe_Paywall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stripe_Paywall.md
SYNC:            ./SYNC_Stripe_Paywall.md

IMPL:            mind-ops/billing/ (not yet created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Stripe Checkout Creates Subscription

**Why:** Users must be able to go from "I want to upgrade" to "I am paying" with a single click on a Stripe-hosted page. We never handle card data. Stripe Checkout gives us PCI SAQ-A compliance and a battle-tested payment UI. The checkout session encodes which tier (product/price) the user selected and their user_id as metadata so the webhook can link the subscription back to our user record.

```
GIVEN:  A user (free or lower tier) initiates an upgrade
WHEN:   The system creates a Stripe Checkout Session with the target tier's price_id
        and the user's user_id + current_tier as metadata
THEN:   The user is redirected to Stripe Checkout hosted page
AND:    On successful payment, Stripe fires a checkout.session.completed webhook
AND:    The system does NOT update the user's tier until the webhook arrives
```

### B2: Webhook Activates Tier on Successful Payment

**Why:** Tier state must come from Stripe, not from client-side redirect callbacks. The success_url redirect is unreliable (user can close the tab). The webhook is the canonical signal. Only upon receiving and verifying a checkout.session.completed event does the system activate the user's new tier.

```
GIVEN:  A checkout.session.completed webhook arrives from Stripe
WHEN:   The webhook signature is verified against the endpoint secret
        AND the event is not a duplicate (idempotency check on event ID)
THEN:   The user's tier is updated in the database to match the purchased product
AND:    The user's stripe_customer_id and subscription_id are stored
AND:    The rate limiter will reflect the new tier on the next request
```

### B3: Rate Limiter Enforces Tier Boundaries

**Why:** LLM calls are expensive. Free users get 10 messages/day. If the rate limiter fails to enforce this, a single free user can generate unbounded cost. Enforcement must happen before the LLM call is dispatched, at the request boundary in mind-mcp.

```
GIVEN:  A user sends a message to MIND via mind-mcp
WHEN:   mind-mcp reads the user's tier and today's message count from the database
THEN:   IF tier is Free AND message_count >= 10: reject the request with tier_limit_reached
        IF tier is Pro/Pro+/Premium: allow the request (unlimited messages)
AND:    The rejection payload includes: current_tier, limit, messages_used, upgrade_url
```

### B4: MIND Suggests Upgrades Conversationally

**Why:** A raw "upgrade now" error is hostile. MIND is a conversational agent. When the user approaches or hits a limit, MIND should explain what is happening and what upgrading would unlock. This is not a hardcoded message -- the LLM receives tier context and decides how to surface it.

```
GIVEN:  A user's request is rejected due to tier limits (B3) OR
        the user has used 8+ of 10 daily messages (approaching limit)
WHEN:   mind-mcp injects tier context into the LLM system prompt:
        {tier: "free", messages_used: 9, messages_limit: 10, locked_features: ["duo_mode", "priority_llm", "full_brief"]}
THEN:   MIND responds conversationally, acknowledging the limit and suggesting the relevant upgrade
AND:    The response includes a Stripe Checkout URL for the recommended tier
```

### B5: Subscription Cancellation Downgrades Tier

**Why:** When a user cancels their subscription (via Stripe Customer Portal or our admin), the system must downgrade them to Free immediately upon receiving the webhook. No grace period logic in our code -- Stripe handles the billing period end. We react to the event.

```
GIVEN:  A customer.subscription.deleted webhook arrives from Stripe
WHEN:   The webhook signature is verified and the event is not a duplicate
THEN:   The user's tier is set to Free in the database
AND:    The subscription_id is cleared
AND:    The rate limiter enforces Free tier limits on the next request
```

### B6: Subscription Upgrade/Downgrade Changes Tier

**Why:** Users may move between paid tiers (Pro to Pro+, Premium to Pro, etc.). Stripe handles prorated billing. We just need to update the stored tier when Stripe tells us the subscription's product changed.

```
GIVEN:  A customer.subscription.updated webhook arrives from Stripe
WHEN:   The webhook signature is verified and the subscription's product/price has changed
THEN:   The user's tier is updated in the database to match the new product
AND:    The rate limiter reflects the new tier on the next request
```

### B7: Payment Failure Triggers Grace Period Warning

**Why:** When a recurring payment fails (expired card, insufficient funds), Stripe retries according to its Smart Retries schedule. During this window, the user should keep access but MIND should be aware. If all retries fail and the subscription is canceled by Stripe, B5 handles the downgrade.

```
GIVEN:  An invoice.payment_failed webhook arrives from Stripe
WHEN:   The webhook is verified and the subscription is still active (Stripe is retrying)
THEN:   The user's payment_status is set to "past_due" in the database
AND:    MIND's tier context includes payment_status: "past_due"
AND:    The user retains their current tier access during the retry window
```

### B8: B2B Seat Addition Updates Stripe Quantity

**Why:** Enterprise tiers (Team, Business) charge per seat. When an organization admin adds or removes members, the Stripe subscription quantity must be updated to match the actual seat count. Stripe handles prorated charges.

```
GIVEN:  An organization admin adds or removes a member in a B2B plan
WHEN:   The system calculates the new seat count for the organization
THEN:   The Stripe subscription's quantity is updated via API call
AND:    Stripe prorates the billing automatically
AND:    The organization's seat_count in the database reflects the change
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Revenue activation | Direct path from "interested" to "paying" |
| B2 | Webhook-driven lifecycle | No polling, no stale state, instant activation |
| B3 | Rate limiting enforcement | Cost containment, tier value differentiation |
| B4 | Conversational upsell | Conversion without hostility, preserves user relationship |
| B5 | Webhook-driven lifecycle | Clean deactivation on cancel, no lingering access |
| B6 | Webhook-driven lifecycle | Tier changes reflected immediately |
| B7 | Webhook-driven lifecycle | Graceful handling of payment hiccups |
| B8 | B2B seat-based billing | Enterprise revenue scales with organization size |

---

## INPUTS / OUTPUTS

### Primary Function: Checkout Session Creation

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | The MIND user ID initiating the upgrade |
| target_tier | string | One of: pro, pro_plus, premium, solo, practice, studio, team, business |
| success_url | string | URL to redirect after successful payment |
| cancel_url | string | URL to redirect if user cancels checkout |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| checkout_url | string | Stripe Checkout Session URL to redirect the user to |

**Side Effects:**

- Stripe Checkout Session created in Stripe's system with user metadata

### Primary Function: Webhook Handler

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| stripe_signature | string | Stripe-Signature header for verification |
| payload | bytes | Raw request body from Stripe |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| status | int | HTTP 200 on success, 400 on verification failure |

**Side Effects:**

- User tier updated in database
- User stripe_customer_id and subscription_id stored
- User payment_status updated on payment failure events

### Primary Function: Rate Limit Check

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| user_id | string | The user making the request |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| allowed | bool | Whether the request is permitted |
| tier_context | dict | {tier, messages_used, messages_limit, locked_features, upgrade_url} |

**Side Effects:**

- message_count incremented in database/cache if request is allowed

---

## EDGE CASES

### E1: Duplicate Webhook Delivery

```
GIVEN:  Stripe delivers the same webhook event twice (network retry)
THEN:   The second delivery is detected via event ID deduplication and ignored
AND:    The handler returns HTTP 200 to prevent further retries
```

### E2: Webhook Arrives Before Success Redirect

```
GIVEN:  The checkout.session.completed webhook arrives before the user is redirected to success_url
THEN:   The tier is activated immediately via webhook -- the success_url page simply reflects current state
AND:    No race condition exists because the webhook is the sole state update path
```

### E3: User Closes Tab During Checkout

```
GIVEN:  The user opens Stripe Checkout but closes the tab without completing payment
THEN:   No webhook is sent. No state changes. The user remains on their current tier.
AND:    The Checkout Session expires after Stripe's default expiry (24 hours)
```

### E4: Free User Sends Message Exactly at Midnight Reset

```
GIVEN:  A free user has used 10 messages and the daily counter resets at midnight UTC
WHEN:   The user sends a message at 00:00:00 UTC
THEN:   The message count for the new day starts at 0 and the message is allowed
```

### E5: Subscription Created Outside Checkout (Manual/Admin)

```
GIVEN:  A subscription is created directly in the Stripe Dashboard by an admin
THEN:   The customer.subscription.created webhook fires
AND:    The system processes it identically to a Checkout-originated subscription
AND:    The user's tier is activated if stripe_customer_id can be mapped to a user
```

### E6: B2B Organization Exceeds Licensed Seats

```
GIVEN:  An organization has 10 seats on a Team plan and attempts to add an 11th member
THEN:   The system updates Stripe subscription quantity to 11 before granting access
AND:    If the Stripe API call fails (e.g., payment method declined), the seat addition is rejected
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Tier Activation Without Webhook Verification

```
GIVEN:   A user completes Stripe Checkout and is redirected to success_url
WHEN:    The success_url callback is received
MUST NOT: Activate the user's tier based on the redirect alone
INSTEAD:  Wait for the checkout.session.completed webhook, verified with the endpoint secret
```

### A2: Silent Rate Limit Failure

```
GIVEN:   The rate limiter encounters a database error when checking message count
WHEN:    The user sends a message
MUST NOT: Silently allow the request (fail open)
INSTEAD:  Return a clear error indicating temporary unavailability, log the failure loudly
```

### A3: Hardcoded Upsell Copy in Code

```
GIVEN:   A user hits their tier limit
WHEN:    The system prepares the response
MUST NOT: Include hardcoded marketing copy like "Upgrade to Pro for only $14.90!"
INSTEAD:  Pass tier context to the LLM and let it generate the suggestion naturally
```

### A4: Polling Stripe for Subscription State

```
GIVEN:   An engineer wants to verify subscription status
WHEN:    Writing code that checks subscription state
MUST NOT: Call Stripe's retrieve subscription API on every request or on a cron schedule
INSTEAD:  Read the locally stored tier, which is kept current by webhook events
```

---

## MARKERS

<!-- @mind:todo Define exact daily message counter reset mechanism (midnight UTC in DB vs Redis TTL) -->
<!-- @mind:todo Decide rate limiter behavior on database read failure: fail closed (deny) vs return error -->
<!-- @mind:escalation Need product decision: should Pro+ and Premium also have any message limit (even if very high), or truly unlimited? -->
