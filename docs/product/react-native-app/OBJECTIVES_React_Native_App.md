# OBJECTIVES — React Native App

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_React_Native_App.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_React_Native_App.md
BEHAVIORS:      ./BEHAVIORS_React_Native_App.md
ALGORITHM:      ./ALGORITHM_React_Native_App.md
VALIDATION:     ./VALIDATION_React_Native_App.md
IMPLEMENTATION: ./IMPLEMENTATION_React_Native_App.md
SYNC:           ./SYNC_React_Native_App.md

IMPL:           mind-app/ (external repo)
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **MIND on every smartphone** — The app is how 99% of humans interact with their citizen. Desktop is for builders; mobile is for living. If the app doesn't work, Mind Protocol doesn't reach people.
2. **One codebase, two platforms** — React Native (Expo) delivers iOS and Android from a single TypeScript codebase. No platform-specific rewrites. Divergence only at native module boundaries (HealthKit vs Health Connect).
3. **Onboarding under 90 seconds** — A human goes from app install to first chat with their citizen in less than 90 seconds. No tutorials, no multi-step wizards, no email confirmation loops. Auth + brief explanation + first message.
4. **Biometric bridge to the body** — Wearable data (heart rate, sleep, steps, HRV) flows into the citizen's graph via HealthKit/Health Connect. The citizen knows its human's physical state. This is not a fitness app — it's embodied awareness.
5. **Push notifications as lifeline** — Brief matinal at 7am, biometric alerts when something looks off, upsell nudges timed to engagement. Firebase (Android) + APNs (iOS). Notifications are how the citizen reaches out, not just how the human reaches in.
6. **Shared design system with WebApp** — The app and mind-platform WebApp share tokens, components, and interaction patterns. A user who knows the web knows the mobile. No visual dissonance.

## NON-OBJECTIVES

- **Offline-first architecture** — Not for v1. The citizen lives server-side. Offline caching of chat history is acceptable but offline graph operations are out of scope.
- **Tablet-optimized layouts** — Phone-first. Tablets get scaled phone layouts. Dedicated tablet UX is v2.
- **Custom LLM inference on-device** — The LLM selector chooses which cloud model the citizen uses, not local inference. On-device models are a research question, not a product feature.
- **Social features between humans** — This is not a social network. No feeds, no friend lists, no public profiles. The app is a 1:1 channel between one human and one citizen.

## TRADEOFFS (canonical decisions)

- When native polish conflicts with shared codebase, choose shared codebase. Platform-specific shimmer effects are not worth maintaining two implementations.
- When onboarding completeness conflicts with speed, choose speed. Show fewer screens, defer settings, let the citizen explain itself in chat.
- When real-time biometric streaming conflicts with battery life, choose battery life. Periodic sync (every 15 minutes background, real-time only when app is foregrounded) is sufficient.
- When push notification frequency conflicts with user trust, choose trust. Maximum 3 push notifications per day unless the user explicitly opts into more.

## SUCCESS SIGNALS (observable)

- App install to first chat message: median < 90 seconds
- HealthKit/Health Connect permission grant rate: > 70% of users who reach the prompt
- Daily Active Users who open via push notification: > 40%
- App Store rating: >= 4.5 stars
- Crash-free session rate: > 99.5%
- Time to interactive on cold start: < 2 seconds on mid-range devices
