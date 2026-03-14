# Stripe Paywall -- Patterns: Webhook-Driven Tier Gating with Conversational Upsell

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: not yet
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Stripe_Paywall.md
THIS:            PATTERNS_Stripe_Paywall.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Stripe_Paywall.md
ALGORITHM:       ./ALGORITHM_Stripe_Paywall.md
VALIDATION:      ./VALIDATION_Stripe_Paywall.md
IMPLEMENTATION:  ./IMPLEMENTATION_Stripe_Paywall.md
SYNC:            ./SYNC_Stripe_Paywall.md

IMPL:            mind-ops/billing/ (not yet created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Stripe_Paywall.md: "Docs updated, implementation needs: {what}"
3. Run tests: `pytest tests/billing/`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Stripe_Paywall.md: "Implementation changed, docs need: {what}"
3. Run tests: `pytest tests/billing/`

---

## THE PROBLEM

MIND provides conversational AI with a personal knowledge graph. LLM inference costs money. Solana transactions cost money. Hosting costs money. Without monetization, every new user increases burn rate. The system needs a paywall that converts free users to paying subscribers, enforces usage limits per tier, and handles the full subscription lifecycle.

The paywall must not feel like a wall. MIND is a conversational product. Hitting a limit and seeing a generic "upgrade now" page breaks the relationship the user has with MIND. The monetization layer must be invisible when you are within your tier and conversational when you hit a boundary.

Stripe is the payment processor. The integration must be minimal: redirect to Stripe Checkout for payment, receive webhooks for state changes, store tier status, enforce limits. No custom payment forms. No stored card numbers. No PCI scope beyond Stripe Checkout's SAQ-A.

---

## THE PATTERN

**Event-sourced tier state driven by Stripe webhooks.**

The core insight: subscription state is not something we compute. It is something Stripe tells us. We listen to webhook events, extract the tier, and store it as the user's current subscription state. The MCP server reads this state on every request and enforces rate limits accordingly.

Three distinct concerns, three distinct locations:

1. **Billing service** (mind-ops/billing/) -- Receives Stripe webhooks, manages Stripe Checkout sessions, stores subscription state in the database. Pure backend. No user-facing logic.

2. **Rate limiter** (mind-mcp) -- Reads user tier from the database on each request. Enforces message limits, feature gates, and LLM routing based on tier. Returns structured limit information when a user is throttled.

3. **Conversational upsell** (mind-mcp prompt context) -- Injects tier context into the LLM system prompt. When the user is near or at their limit, MIND knows and can suggest upgrades naturally. The LLM receives: current tier, messages remaining today, features locked. The LLM decides how to surface this.

This separation means the billing service never touches the conversation, the rate limiter never talks to Stripe, and the upsell logic lives entirely in prompt engineering -- not in hardcoded trigger rules.

---

## BEHAVIORS SUPPORTED

- B1 (Stripe Checkout Creates Subscription) -- The pattern routes all payment through Stripe Checkout, keeping PCI compliance trivial and payment UI zero-effort.
- B2 (Webhook Activates Tier) -- Event-sourced tier state means activation is immediate upon webhook receipt, no polling required.
- B3 (Rate Limiter Enforces Tier Boundaries) -- Separating rate limiting into mind-mcp means enforcement happens at the request boundary, before any LLM call is made.
- B4 (MIND Suggests Upgrades Conversationally) -- Tier context injection means the LLM handles upsell tone and timing, not hardcoded rules.
- B5 (Subscription Cancellation Downgrades Tier) -- Webhook-driven state means cancellation takes effect immediately, no grace period logic in our code.

## BEHAVIORS PREVENTED

- A1 (Stale Tier State) -- Webhook-driven updates prevent cached/polled state from drifting.
- A2 (Payment Data in Our Systems) -- Stripe Checkout redirect means we never see card numbers, CVVs, or bank details.
- A3 (Hardcoded Upsell Messages) -- LLM-driven upsell prevents brittle, annoying, context-free upgrade prompts.

---

## PRINCIPLES

### Principle 1: Stripe Is the Source of Truth for Billing State

We do not compute subscription state. We do not infer it from payment history. We do not cache it with TTLs. Stripe tells us the current state via webhooks, and we store exactly what Stripe says. If Stripe says the subscription is active, it is active. If Stripe says it is canceled, it is canceled. Our database is a projection of Stripe's state, not an independent authority.

This matters because billing disputes, refunds, payment failures, and plan changes all happen inside Stripe. If we maintain independent state, it will drift. Drift in billing state means users get charged for tiers they lost access to, or get free access to tiers they stopped paying for. Both are unacceptable.

### Principle 2: Enforcement at the Request Boundary

Rate limiting happens in mind-mcp, at the moment a user sends a message, before any LLM call is dispatched. Not after. Not in a background job. Not in middleware that can be bypassed. The check is: read the user's tier, read today's message count, decide if the request proceeds or is rejected with tier information.

This matters because LLM calls are the primary cost driver. A single bypassed rate limit check on a free user can cost more than their entire lifetime value. Enforcement must be the first thing that happens, not the last.

### Principle 3: The Paywall Is a Conversation, Not a Wall

When a free user hits 10 messages, they should not see an HTTP 429 and a Stripe link. They should see MIND saying something like: "I've reached my daily limit for free conversations. If you'd like to keep going, Pro gives you unlimited messages for $14.90/mo." The tone, timing, and phrasing are the LLM's job. Our job is to give the LLM the context it needs: current tier, remaining messages, locked features.

This matters because MIND is a relationship product. The monetization moment is the most delicate moment in that relationship. Getting it wrong means the user leaves. Getting it right means the user upgrades because MIND made a compelling case, not because a modal blocked their screen.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| Stripe API | URL | Payment processing, subscription management, webhook delivery |
| mind-ops database (users table) | DB | Stores stripe_customer_id, current_tier, subscription_id per user |
| mind-mcp request context | RUNTIME | Carries user_id, tier, message_count per session for rate limiting |
| Stripe Checkout Session | URL | Hosted payment page, no PCI scope for us |
| Stripe Webhook Events | URL | checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| mind-ops/billing/ | Stripe webhook handler, Checkout session creation, subscription state storage |
| mind-mcp | Rate limiting enforcement, tier context injection into LLM prompts |
| mind-ops database | User table with stripe_customer_id, tier, subscription_id columns |
| Stripe API (external) | All payment processing, subscription lifecycle, webhook delivery |

---

## INSPIRATIONS

**Stripe's own recommended integration pattern:** Checkout Sessions for payment collection, webhook listeners for lifecycle events. This is not novel architecture -- it is Stripe's documented best practice. We follow it exactly.

**Conversational commerce:** The idea that purchase decisions happen inside conversation, not in separate purchase flows. MIND's upsell is conversational commerce applied to SaaS. The product itself makes the case for upgrading.

**Usage-based SaaS gating:** Products like Notion, Linear, and Slack that offer generous free tiers with natural upgrade points. The free tier must be useful enough to create habit. The upgrade must unlock clearly valuable capability.

---

## SCOPE

### In Scope

- Stripe Checkout session creation for B2C and B2B tiers
- Webhook handler for subscription lifecycle events
- User tier storage and retrieval
- Rate limiting based on tier in mind-mcp
- Tier context injection for conversational upsell
- B2B seat-based subscription quantity management
- Webhook signature verification and idempotency

### Out of Scope

- Custom payment form or embedded Stripe Elements -- see: Stripe Checkout redirect
- Crypto/$MIND token payments -- see: future economy module
- Refund processing -- handled in Stripe dashboard
- Multi-currency support -- v2
- Tax calculation -- Stripe Tax or manual, not our code
- Free trial logic -- not in v1 tier structure
- Coupon/promotion codes -- Stripe native, not custom code

---

## MARKERS

<!-- @mind:todo Confirm Stripe product/price IDs will be stored in environment variables, not hardcoded -->
<!-- @mind:todo Decide whether B2B seat management uses Stripe's per-seat billing or custom quantity updates -->
<!-- @mind:escalation Need confirmation on whether mind-ops database schema already has user table columns for stripe_customer_id and tier, or if migration is needed -->
