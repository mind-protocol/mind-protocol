# Stripe Paywall -- Algorithm: Checkout, Webhook Processing, Rate Limiting, and Upsell Injection

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: not yet
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stripe_Paywall.md
BEHAVIORS:       ./BEHAVIORS_Stripe_Paywall.md
PATTERNS:        ./PATTERNS_Stripe_Paywall.md
THIS:            ALGORITHM_Stripe_Paywall.md (you are here)
VALIDATION:      ./VALIDATION_Stripe_Paywall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stripe_Paywall.md
SYNC:            ./SYNC_Stripe_Paywall.md

IMPL:            mind-ops/billing/ (not yet created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

The Stripe Paywall module has four algorithms that operate independently but share state through the database:

1. **Checkout Session Creation** -- generates a Stripe Checkout URL for a given user and target tier.
2. **Webhook Processing** -- receives Stripe events, verifies signatures, deduplicates, and updates user tier state.
3. **Rate Limit Check** -- reads user tier and message count, decides allow/deny, returns tier context.
4. **Tier Context Injection** -- prepares tier-aware context for LLM prompt to enable conversational upsell.

Each algorithm is simple in isolation. The complexity is in ensuring they compose correctly: the webhook updates state that the rate limiter reads, and the rate limiter produces context that the upsell injector formats.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Revenue activation | B1 | Checkout session creation is the entry point for all paid conversions |
| Webhook-driven lifecycle | B2, B5, B6, B7 | Webhook processing is the sole state mutation path for tier changes |
| Rate limiting enforcement | B3 | Rate limit check prevents unbounded free usage and differentiates tiers |
| Conversational upsell | B4 | Tier context injection makes MIND aware of the user's limits and locked features |
| B2B seat billing | B8 | Seat update algorithm keeps Stripe quantity in sync with org membership |

---

## DATA STRUCTURES

### TierConfig (static, loaded at startup)

```
TIER_CONFIG = {
    "free":     { price_id: null,              msg_limit: 10,   features: ["basic_brief"] },
    "pro":      { price_id: env.STRIPE_PRO,    msg_limit: null, features: ["basic_brief", "full_brief", "all_integrations"] },
    "pro_plus": { price_id: env.STRIPE_PROPLUS, msg_limit: null, features: ["basic_brief", "full_brief", "all_integrations", "duo_mode", "priority_llm"] },
    "premium":  { price_id: env.STRIPE_PREMIUM, msg_limit: null, features: ["basic_brief", "full_brief", "all_integrations", "duo_mode", "priority_llm", "byoai"] },
    "solo":     { price_id: env.STRIPE_SOLO,    msg_limit: null, features: ["b2b_base"], seats: 1 },
    "practice": { price_id: env.STRIPE_PRACTICE, msg_limit: null, features: ["b2b_base"], seats: 1 },
    "studio":   { price_id: env.STRIPE_STUDIO,  msg_limit: null, features: ["b2b_base"], seats: 1 },
    "team":     { price_id: env.STRIPE_TEAM,    msg_limit: null, features: ["b2b_base", "b2b_seats"], per_seat: 22.00 },
    "business": { price_id: env.STRIPE_BUSINESS, msg_limit: null, features: ["b2b_base", "b2b_seats"], per_seat: 20.00 },
}
```

### UserSubscriptionState (per user, in database)

```
user_subscription:
    user_id:             string (PK)
    tier:                string (default: "free")
    stripe_customer_id:  string (nullable)
    subscription_id:     string (nullable)
    payment_status:      string (default: "ok")  -- ok | past_due
    org_id:              string (nullable, for B2B)
    updated_at:          timestamp
```

### DailyMessageCount (per user, in cache or database)

```
daily_messages:
    user_id:    string
    date:       date (UTC)
    count:      integer (default: 0)
```

### ProcessedWebhookEvent (for idempotency)

```
processed_events:
    event_id:      string (PK, Stripe event ID)
    processed_at:  timestamp
```

---

## ALGORITHM: Checkout Session Creation

### Step 1: Validate Target Tier

Receive user_id and target_tier. Look up the tier in TIER_CONFIG. If the tier does not exist or has no price_id (e.g., "free"), return an error. Verify that the user is not already on the target tier.

```
target = TIER_CONFIG[target_tier]
if target is None or target.price_id is None:
    raise InvalidTier(target_tier)

current = db.get_user_subscription(user_id)
if current.tier == target_tier:
    raise AlreadyOnTier(target_tier)
```

### Step 2: Resolve or Create Stripe Customer

Check if the user already has a stripe_customer_id in the database. If not, create a Stripe Customer with the user's email and store the ID.

```
if current.stripe_customer_id is None:
    customer = stripe.Customer.create(email=user.email, metadata={"mind_user_id": user_id})
    db.update_user(user_id, stripe_customer_id=customer.id)
    customer_id = customer.id
else:
    customer_id = current.stripe_customer_id
```

### Step 3: Create Checkout Session

Create a Stripe Checkout Session in subscription mode, with the target tier's price_id, the user's customer_id, and metadata linking back to the user.

```
session = stripe.checkout.Session.create(
    customer=customer_id,
    mode="subscription",
    line_items=[{ price: target.price_id, quantity: 1 }],
    success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
    cancel_url=cancel_url,
    metadata={ "mind_user_id": user_id, "target_tier": target_tier },
)
return session.url
```

For B2B seat-based tiers (team, business), set quantity to the organization's current seat count.

---

## ALGORITHM: Webhook Processing

### Step 1: Verify Signature

Stripe sends a Stripe-Signature header with every webhook. Verify it against the webhook endpoint secret. If verification fails, return HTTP 400 immediately. This prevents spoofed webhook calls.

```
try:
    event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
except stripe.error.SignatureVerificationError:
    return HTTP 400
```

### Step 2: Deduplicate

Check if the event ID has already been processed. Stripe may deliver the same event multiple times. If already processed, return HTTP 200 immediately (acknowledge receipt, do nothing).

```
if db.event_exists(event.id):
    return HTTP 200

db.record_event(event.id)
```

### Step 3: Route by Event Type

```
match event.type:
    "checkout.session.completed"        -> handle_checkout_completed(event)
    "customer.subscription.updated"     -> handle_subscription_updated(event)
    "customer.subscription.deleted"     -> handle_subscription_deleted(event)
    "invoice.payment_failed"            -> handle_payment_failed(event)
    _                                   -> log and ignore
```

### Step 4a: Handle Checkout Completed

Extract user_id from session metadata. Extract subscription_id from the session. Retrieve the subscription to get the product/price. Map the price_id to a tier name using TIER_CONFIG (reverse lookup). Update the user's tier, subscription_id, stripe_customer_id, and payment_status.

```
session = event.data.object
user_id = session.metadata["mind_user_id"]
subscription_id = session.subscription
subscription = stripe.Subscription.retrieve(subscription_id)
price_id = subscription.items.data[0].price.id
tier = reverse_lookup_tier(price_id)

db.update_user(user_id,
    tier=tier,
    subscription_id=subscription_id,
    stripe_customer_id=session.customer,
    payment_status="ok"
)
```

### Step 4b: Handle Subscription Updated

Fires when the subscription's product/price changes (upgrade/downgrade) or other properties change. Extract the customer ID, find the user by stripe_customer_id, update the tier if the price changed.

```
subscription = event.data.object
customer_id = subscription.customer
user = db.get_user_by_stripe_customer(customer_id)

price_id = subscription.items.data[0].price.id
new_tier = reverse_lookup_tier(price_id)

if user.tier != new_tier:
    db.update_user(user.user_id, tier=new_tier)
```

### Step 4c: Handle Subscription Deleted

Fires when the subscription is canceled (after billing period ends or immediately). Downgrade the user to Free.

```
subscription = event.data.object
customer_id = subscription.customer
user = db.get_user_by_stripe_customer(customer_id)

db.update_user(user.user_id,
    tier="free",
    subscription_id=None,
    payment_status="ok"
)
```

### Step 4d: Handle Payment Failed

Fires when a recurring invoice payment fails. Mark payment_status as past_due but do not change the tier. Stripe will retry.

```
invoice = event.data.object
customer_id = invoice.customer
user = db.get_user_by_stripe_customer(customer_id)

db.update_user(user.user_id, payment_status="past_due")
```

---

## ALGORITHM: Rate Limit Check

### Step 1: Load User State

Read the user's tier and today's message count. "Today" is defined as the current UTC date.

```
user = db.get_user_subscription(user_id)
today = utc_today()
count = db.get_message_count(user_id, today)
```

### Step 2: Check Limit

Look up the tier's message limit from TIER_CONFIG. If limit is null (unlimited), allow. If count >= limit, deny.

```
tier_config = TIER_CONFIG[user.tier]
limit = tier_config.msg_limit

if limit is not None and count >= limit:
    return RateLimitResult(
        allowed=False,
        tier_context={
            tier: user.tier,
            messages_used: count,
            messages_limit: limit,
            locked_features: compute_locked_features(user.tier),
            upgrade_url: generate_checkout_url(user_id, recommended_upgrade(user.tier)),
            payment_status: user.payment_status,
        }
    )
```

### Step 3: Allow and Increment

If allowed, increment today's message count and return the tier context (the LLM always receives tier context, not just when denied).

```
db.increment_message_count(user_id, today)

return RateLimitResult(
    allowed=True,
    tier_context={
        tier: user.tier,
        messages_used: count + 1,
        messages_limit: limit,
        locked_features: compute_locked_features(user.tier),
        payment_status: user.payment_status,
    }
)
```

---

## ALGORITHM: B2B Seat Update

### Step 1: Calculate New Seat Count

When a member is added or removed from a B2B organization, count the active members.

```
seat_count = db.count_org_members(org_id)
```

### Step 2: Update Stripe Quantity

Retrieve the organization's subscription and update the quantity on the seat line item.

```
org = db.get_org(org_id)
subscription = stripe.Subscription.retrieve(org.subscription_id)
stripe.SubscriptionItem.modify(
    subscription.items.data[0].id,
    quantity=seat_count,
    proration_behavior="create_prorations"
)
```

### Step 3: Store Updated Count

```
db.update_org(org_id, seat_count=seat_count)
```

---

## KEY DECISIONS

### D1: Fail Closed on Rate Limiter Errors

```
IF the database is unreachable when checking message count:
    DENY the request with a temporary-error response
    Log the failure at ERROR level
    WHY: Failing open would allow unbounded free usage during outages.
ELSE:
    Proceed with normal rate limit check
```

### D2: Recommended Upgrade Tier

```
IF user is on "free":
    Recommend "pro" ($14.90/mo -- the natural next step)
IF user is on "pro":
    Recommend "pro_plus" ($24.90/mo -- Duo Mode is the draw)
IF user is on "pro_plus":
    Recommend "premium" ($39.90/mo -- BYOAI)
ELSE:
    No recommendation (already on highest tier or B2B)
```

### D3: Price-to-Tier Reverse Lookup

```
IF a webhook contains a price_id not found in TIER_CONFIG:
    Log a CRITICAL error with the unknown price_id
    Do NOT update the user's tier
    Return HTTP 200 to Stripe (to prevent retries of an unmappable event)
    WHY: Unknown price IDs indicate a configuration mismatch. Silent failure
         is worse than logging loudly and leaving state unchanged.
```

---

## DATA FLOW

```
User clicks "Upgrade"
    |
    v
Checkout Session Creation
    |   (returns checkout_url)
    v
User completes payment on Stripe Checkout
    |
    v
Stripe fires checkout.session.completed webhook
    |
    v
Webhook Processing
    |   (verifies signature, deduplicates, extracts tier)
    |   (updates user tier in database)
    v
User sends next message
    |
    v
Rate Limit Check (mind-mcp)
    |   (reads tier from DB, checks message count)
    |   (returns allow/deny + tier_context)
    v
Tier Context Injection (mind-mcp)
    |   (formats tier_context into LLM system prompt)
    v
LLM generates response
    |   (may include upgrade suggestion if near/at limit)
    v
User sees response
```

---

## COMPLEXITY

**Time:** O(1) per request for rate limit checks -- single DB read (user tier) + single DB read/write (daily message count). Both are keyed lookups.

**Time:** O(1) per webhook -- single signature verification + single DB write. Stripe API calls (retrieve subscription) add network latency but not algorithmic complexity.

**Space:** O(n) where n = number of users -- one subscription state record per user, one daily message count record per user per day (TTL'd or cleaned up).

**Bottlenecks:**
- Database reads on every message for rate limiting. Mitigation: cache user tier in memory with short TTL (60s), invalidated by webhook processing. Daily message counts can use Redis INCR with TTL.
- Stripe API calls in webhook handler (retrieve subscription). Mitigation: batch lookup or extract price_id directly from the event data when available.

---

## HELPER FUNCTIONS

### `reverse_lookup_tier(price_id)`

**Purpose:** Maps a Stripe price_id back to a MIND tier name.

**Logic:** Iterates TIER_CONFIG, finds the entry whose price_id matches. Returns the tier name. Returns None if no match (triggers D3 error handling).

### `compute_locked_features(current_tier)`

**Purpose:** Returns the list of features available in higher tiers but not in the current tier.

**Logic:** Collects all features from all tiers above the current one that are not in the current tier's feature set. Used to inform the LLM what the user is missing.

### `recommended_upgrade(current_tier)`

**Purpose:** Returns the next logical tier for upsell.

**Logic:** Follows the upgrade path: free -> pro -> pro_plus -> premium. Returns None for premium or B2B tiers.

### `generate_checkout_url(user_id, target_tier)`

**Purpose:** Creates a Stripe Checkout Session and returns the URL.

**Logic:** Calls the Checkout Session Creation algorithm. Returns the checkout URL string.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| Stripe API | checkout.Session.create() | Checkout session with URL |
| Stripe API | Webhook.construct_event() | Verified event object |
| Stripe API | Subscription.retrieve() | Subscription with price details |
| Stripe API | SubscriptionItem.modify() | Updated seat quantity |
| mind-ops DB | get_user_subscription(user_id) | UserSubscriptionState |
| mind-ops DB | update_user(user_id, ...) | Confirmation of write |
| mind-ops DB | get_message_count(user_id, date) | Integer count |
| mind-ops DB | increment_message_count(user_id, date) | Confirmation of increment |
| mind-mcp | LLM system prompt injection | tier_context dict merged into prompt |

---

## MARKERS

<!-- @mind:todo Evaluate whether daily message counts should live in Redis (INCR + EXPIRE) vs database table -->
<!-- @mind:todo Design the tier context format for the LLM prompt -- JSON blob vs natural language summary -->
<!-- @mind:proposition Consider caching user tier in mind-mcp process memory with 60s TTL to reduce DB reads per message -->
