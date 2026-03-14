# Stripe Paywall -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stripe_Paywall.md
PATTERNS:        ./PATTERNS_Stripe_Paywall.md
BEHAVIORS:       ./BEHAVIORS_Stripe_Paywall.md
THIS:            VALIDATION_Stripe_Paywall.md (you are here)
ALGORITHM:       ./ALGORITHM_Stripe_Paywall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stripe_Paywall.md
HEALTH:          (not yet created)
SYNC:            ./SYNC_Stripe_Paywall.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, mean the paywall has failed its purpose. Money is involved. Access control is involved. Every invariant here protects either revenue integrity, user trust, or system security.

---

## INVARIANTS

### V1: Tier State Matches Stripe Reality

**Why we care:** If the user's tier in our database diverges from their actual Stripe subscription status, one of two things happens: (a) a paying user loses access they paid for, causing support tickets and churn, or (b) a non-paying user retains access they should not have, causing revenue loss. Both outcomes are unacceptable.

```
MUST:   The user's tier in the database must match their active Stripe subscription's product at all times,
        with at most a 30-second propagation delay after a Stripe event.
NEVER:  A user's tier must never be updated by any path other than a verified Stripe webhook or
        an explicit admin override.
```

### V2: Webhook Signatures Are Always Verified

**Why we care:** An unverified webhook is a potential attack vector. Anyone who discovers the webhook endpoint could send fabricated events to grant themselves Premium access or cancel other users' subscriptions. Signature verification is the only defense.

```
MUST:   Every incoming webhook request must be verified against the Stripe endpoint secret
        using stripe.Webhook.construct_event() before any processing occurs.
NEVER:  A webhook event must never be processed if signature verification fails.
        The handler must return HTTP 400 and log the attempt.
```

### V3: Webhook Events Are Processed Exactly Once

**Why we care:** Duplicate processing of a checkout.session.completed event is mostly harmless (idempotent tier update), but duplicate processing of edge-case events could cause inconsistent state. More importantly, if we lack deduplication, a replay attack could force repeated state transitions.

```
MUST:   Each Stripe event ID must be recorded after processing. Subsequent deliveries of the
        same event ID must be acknowledged (HTTP 200) but not processed again.
NEVER:  The same event must never cause a tier state mutation more than once.
```

### V4: Free Users Cannot Exceed Message Limits

**Why we care:** LLM calls are the primary cost driver. A free user generating unlimited messages is a direct financial liability. The rate limit is the economic foundation of the freemium model.

```
MUST:   A free-tier user must be denied message processing after reaching 10 messages
        in a UTC calendar day. The denial must include tier context for the LLM.
NEVER:  A free-tier user must never have an LLM call dispatched after their daily limit
        is reached. The check must occur before the LLM call, not after.
```

### V5: No Payment Data Enters Our Systems

**Why we care:** PCI compliance. If card numbers, CVVs, or bank account details pass through our servers, we move from SAQ-A (minimal compliance scope) to SAQ-D (full compliance scope), which requires penetration testing, quarterly scans, and extensive documentation. Stripe Checkout redirect keeps all payment data on Stripe's servers.

```
MUST:   All payment collection must go through Stripe Checkout redirect. Our servers must
        never receive, store, log, or transmit raw payment instrument data.
NEVER:  Card numbers, CVVs, bank account numbers, or other payment method details must
        never appear in our logs, database, request bodies, or error messages.
```

### V6: Rate Limiter Fails Closed

**Why we care:** If the rate limiter cannot determine a user's tier or message count (database down, cache miss, network error), failing open means free users get unlimited access during every outage. Failing closed means temporary denial, which is recoverable. Revenue loss from failing open is permanent.

```
MUST:   When the rate limiter cannot read user tier or message count due to any error,
        the request must be denied with a clear temporary-error response.
NEVER:  The rate limiter must never default to "allow" when state cannot be determined.
```

### V7: Tier Context Is Always Available to the LLM

**Why we care:** The conversational upsell depends on the LLM knowing the user's tier, limits, and locked features. If this context is missing, MIND cannot suggest upgrades, and the paywall's conversion mechanism is broken. The user hits a wall with no explanation.

```
MUST:   Every LLM request must include tier_context in the system prompt, containing at minimum:
        current_tier, messages_used (if applicable), messages_limit (if applicable),
        locked_features, and payment_status.
NEVER:  An LLM request must never be sent without tier_context when the user is on a limited tier.
```

### V8: B2B Seat Count Matches Stripe Quantity

**Why we care:** If an organization has 15 active members but Stripe is charging for 10 seats, we are losing revenue. If Stripe is charging for 15 but only 10 are active, we are overcharging the customer and creating churn risk.

```
MUST:   The Stripe subscription quantity for a B2B organization must equal the number of
        active members in that organization, updated within one API call of any membership change.
NEVER:  The Stripe quantity must never differ from the actual member count for more than
        the duration of a single seat change operation.
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable or financially dangerous |
| **HIGH** | Major value lost | Degraded severely, security or revenue at risk |
| **MEDIUM** | Partial value lost | Works but conversion or experience suffers |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Tier accuracy -- users get what they pay for | CRITICAL |
| V2 | Webhook authenticity -- no spoofed billing events | CRITICAL |
| V3 | Event idempotency -- no duplicate state mutations | HIGH |
| V4 | Free tier cost containment -- LLM spend bounded | CRITICAL |
| V5 | PCI compliance -- no payment data in our systems | CRITICAL |
| V6 | Rate limiter resilience -- no free access during outages | HIGH |
| V7 | Upsell context availability -- LLM can suggest upgrades | MEDIUM |
| V8 | B2B seat billing accuracy -- charge matches usage | HIGH |

---

## MARKERS

<!-- @mind:todo V4 needs exact specification of how "10 messages per UTC day" is counted -- does a rejected message count? -->
<!-- @mind:todo V6 needs specification of what "clear temporary-error response" looks like in the API contract -->
<!-- @mind:proposition Consider V9: audit log of all tier state changes for dispute resolution -->
