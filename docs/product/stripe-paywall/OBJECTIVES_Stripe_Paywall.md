# OBJECTIVES -- Stripe Paywall

```
STATUS: DESIGNING
CREATED: 2026-03-14
VERIFIED: not yet
```

---

## CHAIN

```
THIS:            OBJECTIVES_Stripe_Paywall.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Stripe_Paywall.md
BEHAVIORS:      ./BEHAVIORS_Stripe_Paywall.md
ALGORITHM:      ./ALGORITHM_Stripe_Paywall.md
VALIDATION:     ./VALIDATION_Stripe_Paywall.md
IMPLEMENTATION: ./IMPLEMENTATION_Stripe_Paywall.md
SYNC:           ./SYNC_Stripe_Paywall.md

IMPL:           mind-ops/billing/ (not yet created)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Revenue activation through tier-gated access** -- MIND needs monetization to sustain infrastructure costs (LLM calls, Solana transactions, hosting). Without a paywall, usage scales but revenue stays at zero. Stripe Checkout provides immediate conversion from free users to paying subscribers with minimal friction.

2. **Rate limiting enforcement that reflects subscription tier** -- Free users get 10 messages/day. Pro users get unlimited. The MCP server must enforce these limits in real time. If enforcement is loose or bypassable, paying users see no value in upgrading and free users consume resources without bound.

3. **Conversational upsell driven by MIND itself** -- When a user hits a tier boundary (message cap, missing integration, no Duo Mode), MIND should surface the upgrade naturally within the conversation. Not a banner. Not a modal. A sentence from MIND explaining what they are missing and offering the path. This makes the paywall feel like guidance, not obstruction.

4. **Webhook-driven tier lifecycle with no polling** -- Stripe webhooks must be the single source of truth for subscription state changes. Activation, cancellation, upgrade, downgrade, payment failure -- all flow through webhooks. No cron jobs polling Stripe. No stale subscription caches. The system reacts to events, not polls for state.

5. **B2B seat-based billing that scales with organization size** -- Enterprise tiers charge per seat. Adding or removing members must adjust the Stripe subscription quantity in real time. Prorated billing must be handled by Stripe, not by custom code.

## NON-OBJECTIVES

- Building a custom payment UI. Stripe Checkout handles the entire payment flow. We redirect, Stripe collects, we receive the webhook.
- Implementing refund logic beyond what Stripe provides out of the box. Refunds are handled in the Stripe dashboard by the operator.
- Multi-currency pricing at launch. All prices in USD. Multi-currency is a v2 concern.
- Crypto payment integration. $MIND token payments for subscriptions are a separate module, not part of this paywall.
- Custom invoice generation. Stripe handles invoicing for subscriptions natively.

## TRADEOFFS (canonical decisions)

- When **speed of implementation** conflicts with **custom payment UI**, choose Stripe Checkout redirect. We lose brand control over the payment page but gain 2 days of saved work and PCI compliance for free.
- When **real-time accuracy** conflicts with **resilience to webhook failures**, choose webhook idempotency with retry. We accept a small window (seconds) of stale state during Stripe outages rather than building a polling fallback.
- When **conversational upsell elegance** conflicts with **implementation complexity in mind-mcp**, choose a simple tier-context injection into the LLM prompt. MIND receives the user's current tier and limits as context. The LLM decides when and how to suggest upgrades. No hardcoded upsell triggers.
- We accept **Stripe vendor lock-in** to preserve simplicity. Abstracting behind a payment provider interface adds complexity for a migration scenario that may never happen.

## SUCCESS SIGNALS (observable)

- A free user hitting 10 messages/day receives a conversational suggestion to upgrade, with a Stripe Checkout link, and can complete payment in under 60 seconds.
- A webhook for `checkout.session.completed` triggers tier activation within 5 seconds. The user's next message reflects the new tier's limits.
- A webhook for `customer.subscription.deleted` triggers tier downgrade to Free within 5 seconds. The user's next message is rate-limited accordingly.
- B2B seat additions via the admin panel reflect in Stripe subscription quantity within one API call.
- Zero Stripe API polling in production. All state changes flow through webhooks.
