# Stripe Paywall -- Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: agent/groundwork
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Tier structure: Free ($0, 10 msg/day), Pro ($14.90/mo), Pro+ ($24.90/mo), Premium ($39.90/mo)
- B2B Micro: Solo ($149), Practice ($199), Studio ($299)
- B2B Enterprise: Team ($299 + $22/seat), Business ($799 + $20/seat)
- Architecture: Stripe Checkout redirect, webhook-driven tier state, rate limiting in mind-mcp, conversational upsell via LLM prompt context injection
- Webhook event set: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed

**What's still being designed:**
- Database schema for UserSubscription -- new table vs extending existing users table
- Daily message counter storage -- Redis vs database
- Exact tier context format for LLM prompt injection
- B2B seat management -- Stripe per-seat billing vs custom quantity updates
- mind-ops web framework choice (affects route registration)
- Whether Pro+/Premium should have any message cap at all

**What's proposed (v2+):**
- Multi-currency pricing
- $MIND token payment for subscriptions
- Coupon/promotion code support
- Free trial periods
- Usage-based pricing beyond message counts (e.g., graph operations, integrations)
- Stripe Customer Portal integration for self-service subscription management

---

## CURRENT STATE

No code exists. This is a documentation-first design phase.

The full documentation chain has been created with 7 files covering objectives, patterns, behaviors, algorithm, validation, implementation architecture, and this sync file. The design is complete enough to begin implementation.

The design reflects MIND's monetization strategy: a freemium model where the free tier is useful enough to build habit (10 messages/day, basic brief), and paid tiers unlock clearly differentiated value (unlimited messages, full brief, Duo Mode, priority LLM, BYOAI). The paywall is designed to be conversational -- MIND itself suggests upgrades within the conversation rather than showing generic error pages.

The implementation will span two repositories:
- **mind-ops/billing/** -- Stripe Checkout session creation, webhook handling, subscription state persistence
- **mind-mcp/rate_limiting/** -- Per-request rate limiting, tier context injection into LLM prompts

Target effort: 2-3 days for Stripe integration (mind-ops), 1 day for rate limiting enforcement (mind-mcp). Originally scheduled for S3-S4 (due 28 Feb), now behind schedule.

---

## IN PROGRESS

### Documentation Chain Creation

- **Started:** 2026-03-14
- **By:** agent/groundwork
- **Status:** Complete
- **Context:** 7-file doc chain created from scratch. HEALTH file is not yet created -- it is the 8th file in the full chain and should be written before implementation begins, per protocol.

---

## RECENT CHANGES

### 2026-03-14: Documentation Chain Created

- **What:** Created full 7-file doc chain: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC
- **Why:** No Stripe code exists yet. Design-first approach ensures architecture decisions are captured before implementation begins. The doc chain makes the system implementable by any agent without additional context.
- **Files:** `docs/product/stripe-paywall/` (all 7 files)
- **Struggles/Insights:** Key design tension is between "fail closed" (deny on error) and user experience. Decided that revenue protection outweighs temporary user friction during outages. The conversational upsell pattern (LLM handles tone, not hardcoded messages) is the most distinctive architectural choice -- it turns the paywall into a feature of MIND's personality rather than a generic SaaS gate.

---

## KNOWN ISSUES

### No HEALTH File

- **Severity:** medium
- **Symptom:** The doc chain has 7 of 8 files. HEALTH is part of the protocol-required chain.
- **Suspected cause:** User requested 7 files. HEALTH should be created before implementation begins.
- **Attempted:** Noted in this SYNC file.

### Schedule Slip

- **Severity:** high
- **Symptom:** This work was scheduled for S3-S4, due 2026-02-28. It is now 2026-03-14.
- **Suspected cause:** Other priorities took precedence.
- **Attempted:** Doc chain created to unblock implementation. Estimated effort remains 2-3 days Stripe + 1 day rate limiting.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**Where I stopped:** Documentation chain complete. No code written. Ready for implementation.

**What you need to understand:**
The design is spread across two repos (mind-ops for billing, mind-mcp for rate limiting). Start with mind-ops/billing/ because rate limiting depends on the subscription state that billing writes. The TIER_CONFIG in tier_config_and_price_mapping.py is the central data structure -- get that right first, then webhook handling, then checkout, then rate limiting.

**Watch out for:**
- Stripe webhook signature verification uses the raw request body bytes, not a parsed JSON object. If the framework parses the body before you verify, verification will fail. FastAPI has a workaround with `Request.body()`.
- The reverse price lookup (price_id -> tier name) must handle unknown price IDs gracefully. Log loud, do not crash, do not update tier.
- Message count atomicity: two concurrent requests from the same free user must not both slip through at count=9. Use atomic increment (Redis INCR or database UPDATE RETURNING).

**Open questions I had:**
- Does mind-ops already have a users table with a tier column, or does this need a new table/migration?
- What web framework does mind-ops use? Route registration depends on this.
- Should the daily message counter live in Redis (fast, TTL-based) or the database (simpler, no additional infrastructure)?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full documentation chain (7 files) for the Stripe Paywall module has been created in `docs/product/stripe-paywall/`. The design covers B2C tiers (Free/Pro/Pro+/Premium), B2B tiers (Solo/Practice/Studio/Team/Business), Stripe Checkout redirect, webhook-driven tier lifecycle, rate limiting in mind-mcp, and conversational upsell via LLM prompt injection. No code exists yet. Estimated effort: 3-4 days total.

**Decisions made:**
- Stripe Checkout redirect (not embedded payment form) for PCI simplicity
- Webhook as sole source of truth for tier state (no polling)
- Rate limiter fails closed (deny on error, not allow)
- Conversational upsell via LLM context injection (not hardcoded messages)
- No payment provider abstraction (Stripe lock-in accepted)

**Needs your input:**
- Confirm B2B seat management approach: Stripe per-seat billing (automatic) vs custom quantity updates?
- Confirm mind-ops database schema situation: new table vs extending existing users table?
- Confirm mind-ops web framework (FastAPI?) for webhook route registration
- Product decision: Pro+/Premium truly unlimited messages, or very high cap (1000/day)?

---

## TODO

### Doc/Impl Drift

No code exists yet, so no drift possible. This section activates when implementation begins.

### Tests to Run

```bash
# After implementation:
pytest tests/billing/
pytest tests/rate_limiting/
```

### Immediate

- [ ] Create HEALTH_Stripe_Paywall.md to complete the 8-file chain
- [ ] Confirm mind-ops database schema and web framework
- [ ] Create Stripe products and prices in Stripe Dashboard (test mode)
- [ ] Implement billing/tier_config_and_price_mapping.py (central data structure)
- [ ] Implement billing/stripe_webhook_signature_verifier_and_router.py (security-critical)
- [ ] Implement billing/stripe_webhook_event_handlers.py
- [ ] Implement billing/stripe_checkout_session_creator.py
- [ ] Implement billing/subscription_state_persistence.py
- [ ] Implement rate_limiting/tier_based_message_rate_limiter.py
- [ ] Implement rate_limiting/tier_context_builder_for_llm_prompt.py
- [ ] Write integration tests with Stripe test mode webhooks
- [ ] Write unit tests for rate limiter

### Later

- [ ] Stripe Customer Portal integration for self-service subscription management
- [ ] Multi-currency pricing
- [ ] Usage analytics dashboard (tier distribution, conversion rates, churn)
- IDEA: A/B test different upsell prompt strategies by varying tier context format

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the architecture. The design is straightforward -- Stripe Checkout + webhooks is a well-trodden path. The conversational upsell is the most interesting design choice and the one most likely to need iteration after real user testing.

**Threads I was holding:**
- The atomicity of message count increment is a real concurrency concern that needs a concrete solution (Redis INCR is the likely winner).
- The tier context format for LLM injection needs experimentation -- JSON blob vs natural language vs structured template. This will be tuned based on LLM response quality.
- B2B seat management has a subtle billing edge case: what happens when the last admin removes themselves?

**Intuitions:**
- The free tier limit of 10 messages/day will need tuning. Too low and users churn before building habit. Too high and there is no upgrade pressure. Analytics on message-10 conversion rate will be essential.
- The conversational upsell will work better than a traditional paywall because MIND has relationship context. It knows what the user was trying to do when they hit the limit.

**What I wish I'd known at the start:**
The design is simpler than it seems. Stripe handles all the hard parts (payment, subscriptions, retries, prorating). Our code is just: receive event, update tier, check tier on each request. The complexity is in the edge cases (concurrency, idempotency, failure modes), not in the main path.

---

## POINTERS

| What | Where |
|------|-------|
| Stripe API docs | https://stripe.com/docs/api |
| Stripe Checkout integration guide | https://stripe.com/docs/checkout/quickstart |
| Stripe Webhooks guide | https://stripe.com/docs/webhooks |
| Tier pricing table | OBJECTIVES_Stripe_Paywall.md, Section: PRIMARY OBJECTIVES |
| Tier config data structure | ALGORITHM_Stripe_Paywall.md, Section: DATA STRUCTURES |
| Validation invariants | VALIDATION_Stripe_Paywall.md |
| File structure | IMPLEMENTATION_Stripe_Paywall.md, Section: CODE STRUCTURE |
