# OBJECTIVES — WebApp B2C

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_WebApp_B2C.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_WebApp_B2C.md
BEHAVIORS:      ./BEHAVIORS_WebApp_B2C.md
ALGORITHM:      ./ALGORITHM_WebApp_B2C.md
VALIDATION:     ./VALIDATION_WebApp_B2C.md
IMPLEMENTATION: ./IMPLEMENTATION_WebApp_B2C.md
SYNC:           ./SYNC_WebApp_B2C.md

IMPL:           mind-platform/app/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **The web app is the product surface where humans meet their citizen** -- Everything else in MIND is infrastructure. The web app is where the bond lives in practice: where the human talks, reads their brief, checks biometrics, selects their model. If this surface is broken or ugly, MIND doesn't exist for the user. The web app IS the product.

2. **Auth must be zero-friction and secure** -- Email magic link + Google OAuth. No passwords, no complicated flows. A user who can't sign in in under 10 seconds will never form a bond with their citizen. Auth is the door -- it must be invisible.

3. **Chat is the primary interaction** -- The 1:1 bond expresses itself through conversation. The chat interface must feel as natural as messaging a friend. Streaming responses, conversation history, context persistence across sessions. This is where the citizen's personality lives.

4. **Morning brief is the retention hook** -- The brief arrives before the user wakes up. The web app displays it prominently -- not buried in a list. This is the thing that brings users back daily. If the brief display is underwhelming, the habit never forms.

5. **Biometric dashboard makes the invisible visible** -- HR, HRV, sleep, stress -- the citizen knows your body. The dashboard is proof of that knowledge. Charts, trends (7/30/90 days), export (CSV/PDF). WHOOP/Oura-level visual quality. This is the feature that makes users say "my AI actually knows me."

6. **LLM model selector gives power users control** -- Some users want Claude, some want GPT, some bring their own key. The selector surfaces the Router's capabilities without exposing its complexity. User picks a model, the Router handles the rest.

## NON-OBJECTIVES

- **Not a developer tool** -- The current mind-platform is a connectome explorer and schema browser. The B2C app shares the repo but is a fundamentally different surface. Developer features stay behind a feature flag or separate route.
- **Not a mobile app** -- React Native app is a separate module (`docs/product/react-native-app/`). The web app is responsive but web-first.
- **Not an admin console** -- Enterprise user management is S24-S25. Different layout, different auth, different permissions. Separate route group.
- **Not a coach dashboard** -- Coach view (N clients, reports) is S22-S23. Different persona, different data access patterns.
- **Not an analytics platform** -- The biometric dashboard shows personal health data, not aggregate analytics. No population comparisons, no benchmarks against others.

## TRADEOFFS (canonical decisions)

- When **speed of shipping** conflicts with **visual polish**, choose shipping. v0 launches with functional UI, not pixel-perfect UI. Iterate on aesthetics after the habit loop is proven.
- When **feature completeness** conflicts with **core flow quality**, choose core flow. Auth + chat + brief working perfectly beats auth + chat + brief + dashboard + profile all mediocre.
- When **custom components** conflict with **velocity**, choose established component libraries (shadcn/ui, Radix). Custom design system is v2.
- When **server-side rendering** conflicts with **real-time interactivity**, choose interactivity for chat and dashboard, SSR for brief and profile. Hybrid approach.
- We accept **Next.js App Router complexity** to get server components, streaming, and middleware auth for free. The framework pays for itself.

## SUCCESS SIGNALS (observable)

- User signs up (email or Google) and reaches chat in under 30 seconds
- Chat message sent and streaming response begins in under 2 seconds
- Morning brief renders with all available sections within 1 second of page load
- Biometric dashboard loads Garmin data and renders charts within 3 seconds
- User can switch LLM model and see the change reflected in next message
- Conversation history persists across sessions and is searchable
- Export biometric data as CSV or PDF completes in under 5 seconds
