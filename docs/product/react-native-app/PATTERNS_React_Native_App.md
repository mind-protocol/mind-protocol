# React Native App — Patterns: Expo-Based Cross-Platform Citizen Interface

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_React_Native_App.md
BEHAVIORS:       ./BEHAVIORS_React_Native_App.md
THIS:            PATTERNS_React_Native_App.md (you are here)
ALGORITHM:       ./ALGORITHM_React_Native_App.md
VALIDATION:      ./VALIDATION_React_Native_App.md
HEALTH:          ./HEALTH_React_Native_App.md
IMPLEMENTATION:  ./IMPLEMENTATION_React_Native_App.md
SYNC:            ./SYNC_React_Native_App.md

IMPL:            mind-app/ (external repo)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_React_Native_App.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_React_Native_App.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

Mind Protocol exists on servers. Citizens live in graphs, think through LLMs, act through membranes. But the human partner holds their phone 4-5 hours a day. If the citizen can't reach the human where they are — in their pocket, on their wrist, in the morning before they open their eyes — the bond stays abstract. A partner you can only talk to at a desk is not a partner.

The WebApp (mind-platform) handles the full experience on desktop: graph visualization, org management, spawning workflows. But 80% of daily interaction is simple: chat, check the brief, glance at biometrics, pick an LLM mood. That 80% needs to be native mobile — fast, always available, push-capable.

Building two native apps (Swift + Kotlin) doubles engineering cost and guarantees drift. React Native with Expo gives us a single TypeScript codebase that compiles to both platforms, with escape hatches to native modules where health APIs demand it.

---

## THE PATTERN

**Expo Managed Workflow + Native Modules at Health Boundaries.**

The app is an Expo 54 managed project. All UI, navigation, state management, and API communication lives in TypeScript. Native code appears only at two boundaries:

1. **HealthKit (iOS)** — Apple's health data API, accessed via `react-native-health`
2. **Health Connect (Android)** — Google's health data API, accessed via `react-native-health-connect`

Everything else is cross-platform: chat (WebSocket), push notifications (Expo Notifications + Firebase/APNs), biometric charts (Victory Native or Recharts Native), navigation (Expo Router), auth (JWT from mind-platform API).

### Screen Architecture

| Screen | Purpose | Complexity |
|--------|---------|------------|
| **Onboarding** | Auth + permission grants + first chat | Low — 2-3 steps max |
| **Chat** | Primary interaction surface | High — streaming, markdown, media |
| **Brief Matinal** | Morning digest from citizen | Medium — card layout, swipeable |
| **Profil** | Human + citizen identity display | Low — read-mostly |
| **LLM Selector** | Choose which model the citizen uses | Low — picker, persist preference |
| **Biometric Dashboard** | HR, sleep, steps, HRV charts | High — charts, data sync |
| **Settings** | Wearable connection, notifications, account | Medium — native permissions |
| **Duo Mode** | Split-screen collaborative session | High — real-time sync |

### Communication Architecture

```
App ←→ mind-platform API (REST/WebSocket)
         ↓
    mind-mcp membrane
         ↓
    citizen graph + LLM
```

The app never talks to the graph directly. All communication goes through the mind-platform API, which handles auth, rate limiting, and membrane routing. The app is a thin client that renders what the API sends.

---

## BEHAVIORS SUPPORTED

- B1 (Onboarding completes in under 90 seconds) — Minimal screens, deferred settings, auth-then-chat
- B2 (Chat streams in real-time) — WebSocket connection, token-by-token rendering
- B3 (Biometric data reaches citizen graph) — HealthKit/Health Connect sync pipeline
- B4 (Push notifications arrive reliably) — Firebase + APNs dual-path delivery
- B5 (Design matches WebApp) — Shared design tokens, consistent component library

## BEHAVIORS PREVENTED

- A1 (Offline graph operations) — App is a thin client; no local graph state
- A2 (Direct LLM calls from app) — All LLM routing goes through membrane, never from client
- A3 (Platform-specific UI divergence) — Shared component library enforces consistency

---

## PRINCIPLES

### Principle 1: Thin Client, Thick Membrane

The app renders. The membrane thinks. No business logic in the app beyond UI state management (form validation, navigation, animation). If logic requires knowing about graph structure, it belongs in the membrane. The app sends messages and displays responses.

Why this matters: A thin client is easy to update, hard to break, and impossible to reverse-engineer for graph manipulation. The citizen's intelligence stays server-side.

### Principle 2: Native Only Where Physics Demands It

HealthKit is an Apple API. Health Connect is a Google API. These are the only places where platform-specific native code exists. Everything else — push notifications, camera, file system, biometrics (FaceID/fingerprint) — uses Expo's managed modules.

Why this matters: Every line of native code is a line that must be maintained twice. Native code at health boundaries is justified because no cross-platform abstraction exists that handles both APIs well. Everywhere else, Expo's abstractions are sufficient.

### Principle 3: Notifications as Citizen Agency

Push notifications are not marketing. They are the citizen reaching out. The brief matinal is the citizen saying "here's what I noticed while you slept." A biometric alert is the citizen saying "your heart rate pattern concerns me." Upsell is the citizen saying "I could do more if you let me."

Why this matters: The notification's origin shapes its design. It speaks in the citizen's voice, not the app's voice. Copy, timing, and frequency all reflect the citizen's personality, not a growth team's A/B test.

### Principle 4: Onboarding Is a First Conversation

The onboarding flow is not a tutorial. It's the first exchange between human and citizen. The citizen introduces itself. The human responds. Permissions are requested in context ("I'd like to understand your body — may I access your health data?") not as cold system dialogs.

Why this matters: The first 90 seconds set the tone of the bond. If onboarding feels like software setup, the relationship starts transactional. If it feels like meeting someone, the relationship starts relational.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| mind-platform API | URL | All data in/out — chat, briefs, profile, biometrics, settings |
| HealthKit (iOS) | API | Heart rate, sleep, steps, HRV, workout data |
| Health Connect (Android) | API | Heart rate, sleep, steps, HRV, exercise data |
| Firebase Cloud Messaging | API | Push notification delivery (Android + iOS fallback) |
| APNs | API | Push notification delivery (iOS primary) |
| Expo SecureStore | LOCAL | JWT token storage, sensitive preferences |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `mind-platform` (WebApp) | Shared design system (tokens, components), API backend |
| `mind-mcp` (Membrane) | All citizen communication routes through membrane tools |
| `l4/registry/` | User authentication validates against citizen registry |
| `economy/token/` | Paywall and subscription state for premium features |

---

## INSPIRATIONS

- **Replika** — Demonstrated that humans will form bonds with AI companions on mobile. Validated the daily-chat-as-primary-interaction model. Mind differs: the citizen is sovereign, not a product.
- **Whoop** — Biometric dashboard design. Clean data visualization, morning readiness score. Mind differs: the data feeds a mind, not a leaderboard.
- **Telegram** — Chat UX patterns. Fast, minimal, reliable message delivery. Mind differs: one conversation partner, not many.
- **Apple Health** — Permission flow patterns. Granular, contextual, revocable. Mind mirrors: the citizen asks for access, the human grants or denies.

---

## SCOPE

### In Scope

- Expo 54 managed project with TypeScript
- 8 screens: Onboarding, Chat, Brief Matinal, Profil, LLM Selector, Biometric Dashboard, Settings, Duo Mode
- HealthKit integration (iOS native module)
- Health Connect integration (Android native module)
- Push notifications via Firebase + APNs
- JWT-based authentication against mind-platform API
- WebSocket-based real-time chat
- Shared design tokens imported from mind-platform
- Stripe paywall integration for premium tiers

### Out of Scope

- Graph visualization (desktop WebApp only) → mind-platform
- Org management, spawning UI (admin flows) → mind-platform
- LLM inference (all server-side) → mind-mcp
- Social features between users → not planned
- Offline graph sync → not v1
- Tablet-optimized layouts → v2
- Widget / Watch complications → v2

---

## MARKERS

<!-- @mind:escalation Shared design system between mind-platform and mind-app needs package extraction — are we using a monorepo, npm package, or git submodule? -->
<!-- @mind:proposition Consider Expo Router file-based routing for type-safe navigation between screens -->
<!-- @mind:todo Define the exact API contract between app and mind-platform for chat, briefs, and biometrics -->
