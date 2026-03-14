# React Native App — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet. Module is in DESIGNING phase. mind-app repo contains Expo 54 boilerplate only (App.tsx, index.ts stubs, no features).

**What's still being designed:**
- Screen architecture (8 screens: Onboarding, Chat, Brief, Dashboard, Profile, LLM Selector, Settings, Duo Mode)
- Biometric sync pipeline (HealthKit iOS + Health Connect Android)
- Push notification system (Firebase + APNs)
- WebSocket chat streaming protocol
- Shared design system with mind-platform WebApp
- State management approach (Zustand + TanStack Query)

**What's proposed (v2+):**
- Offline chat message queueing (beyond 5-message local buffer)
- Tablet-optimized layouts
- Apple Watch / WearOS complications
- On-device inference for latency-sensitive features
- Widget support (iOS 16+ / Android 12+)

---

## CURRENT STATE

The mind-app repo exists with Expo 54 bootstrapped. `App.tsx` and `index.ts` are stubs — no screens, no navigation, no API connectivity. The app does not connect to mind-platform, does not authenticate, and has no features.

This doc chain was created to capture the full design before implementation begins. The 7 doc files (OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH) define the target architecture.

Key design decisions made in this doc chain:
- Expo managed workflow with config plugins for health native modules
- File-based routing via Expo Router
- Thin client: all business logic stays in the membrane, app only renders
- Platform Bridge pattern for HealthKit vs Health Connect abstraction
- 90-second onboarding target (2 screens: Welcome, Chat)
- Maximum 3 push notifications per day by default
- Background biometric sync every 15 minutes
- Zustand for UI state, TanStack Query for server state

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (groundwork)
- **Status:** Complete
- **Context:** 7 doc files created covering full app architecture. No code written yet.

---

## RECENT CHANGES

### 2026-03-14: Full Doc Chain Created

- **What:** Created 7 documentation files: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH, SYNC
- **Why:** mind-app exists as boilerplate only. Before writing code, the design needs to be captured — screen architecture, data flows, validation invariants, health checks. The doc chain ensures implementation starts with clear intent.
- **Files:** `docs/product/react-native-app/` (7 files)
- **Insights:** The biometric sync pipeline is the most complex flow — it crosses two boundaries (native health API + remote API) and runs in background. This should be implemented and tested first, before chat or notifications.

---

## KNOWN ISSUES

### No Shared Design System Package

- **Severity:** medium
- **Symptom:** mind-platform WebApp has design tokens and components, but no mechanism to share them with mind-app
- **Suspected cause:** mind-platform was built as a standalone Next.js app without extracting a shared package
- **Attempted:** Nothing yet — this is a design-time identification

### Chart Library Decision Pending

- **Severity:** low
- **Symptom:** ALGORITHM doc references Victory Native vs Recharts but no decision is made
- **Suspected cause:** Need benchmarking on mid-range Android devices to choose
- **Attempted:** Nothing yet — needs device testing

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementing screens and services)

**Where I stopped:** Doc chain complete. No code written. mind-app repo has Expo 54 boilerplate only.

**What you need to understand:**
The app is a thin client. Do not put graph logic, LLM routing, or business rules in the app. Every smart operation goes through the mind-platform API. The app's job: render what the API sends, collect what the user provides, and bridge to native health APIs.

**Watch out for:**
- HealthKit and Health Connect have fundamentally different data models. The `biometric_platform_bridge.ts` must abstract this completely — no `Platform.OS` checks in hooks or screens.
- Expo managed workflow with config plugins. Do NOT eject to bare workflow. If a native module isn't available as an Expo config plugin, find one that is or write a plugin.
- Background fetch on iOS is unreliable — Apple throttles apps that abuse it. The 15-minute interval is aspirational, not guaranteed. Design sync to be resilient to 30-60 minute gaps.

**Open questions I had:**
- How should the shared design system be distributed? npm package? git submodule? Monorepo with turborepo?
- What's the WebSocket message protocol? mind-platform needs to define the event types and payload shapes.
- Should Duo Mode use a different screen architecture (bottom sheet vs split view) for phones under 6 inches?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Full doc chain (7 files) created for the React Native App module. Defines screen architecture (8 screens), biometric sync pipeline (HealthKit + Health Connect), push notification system (Firebase + APNs), and chat WebSocket streaming. mind-app repo currently has Expo 54 boilerplate only — no features implemented. Roadmap: S13-S16 (28 April - 23 May), 4 weeks screens + 2 weeks wearables/push.

**Decisions made:**
- Expo managed workflow (not bare) — Expo handles builds, signing, OTA updates
- Thin client architecture — all intelligence stays in membrane
- 90-second onboarding (2 screens only: Welcome + Chat)
- Max 3 notifications/day default (biometric alerts can bypass)
- 15-minute background biometric sync interval
- Zustand + TanStack Query for state management
- Platform Bridge pattern for HealthKit/Health Connect abstraction

**Needs your input:**
- Shared design system distribution strategy (npm package vs monorepo vs submodule)
- WebSocket protocol definition from mind-platform side
- Chart library choice: Victory Native (native perf) vs Recharts (web compat) — needs benchmarking
- Duo Mode viability on small screens (< 6")

---

## TODO

### Doc/Impl Drift

- [ ] DOCS->IMPL: Full app architecture documented, zero code exists — everything needs implementing

### Tests to Run

```bash
# No tests exist yet — module is boilerplate only
cd mind-app && npx expo start  # verify Expo setup still works
```

### Immediate

- [ ] Set up Expo Router file-based navigation in mind-app
- [ ] Implement auth flow (JWT from mind-platform API, SecureStore)
- [ ] Build Chat screen with WebSocket streaming
- [ ] Build biometric platform bridge (HealthKit + Health Connect)
- [ ] Set up push notification registration (Expo Notifications)

### Later

- [ ] Build Brief Matinal screen with card stack UI
- [ ] Build Biometric Dashboard with charts
- [ ] Implement Duo Mode
- [ ] Set up Sentry crash monitoring
- [ ] Build Detox e2e test suite
- [ ] OTA updates via expo-updates
- IDEA: Consider Flipper plugin for development-time health indicator visibility

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident in the design. The doc chain covers the full scope without overspecifying implementation details. The biometric sync pipeline is clearly the riskiest component — two boundary crossings, background execution, platform-specific native APIs. Chat streaming is well-understood. Push notifications are standard Expo territory.

**Threads I was holding:**
- The shared design system question is unresolved and will become a blocker as soon as UI work starts
- Background fetch reliability on iOS is a known industry problem — the 15-minute interval is optimistic and the sync pipeline must tolerate longer gaps
- Duo Mode on small phones is questionable — may need to become a bottom-sheet overlay rather than true split-screen

**Intuitions:**
- Start with biometric sync, not chat. Chat is the primary feature but sync is the hardest engineering challenge. Getting the native bridge right early prevents late-stage rearchitecting.
- The onboarding flow should feel like the citizen is already alive and waiting for the human, not like the human is setting up software.

**What I wish I'd known at the start:**
The HEALTH template is elaborate. For a DESIGNING module with no code, the health doc is necessarily aspirational. It documents what checkers will exist, not what checkers run. That's fine — the purpose is to plan verification before writing code.

---

## POINTERS

| What | Where |
|------|-------|
| mind-app repo (boilerplate) | `mind-app/` (external repo) |
| mind-platform API (backend) | `mind-platform/` (external repo) |
| mind-mcp membrane | `mind-mcp/` (external repo) |
| Spawning pipeline (citizen creation) | `l4/spawning/` |
| Economy docs (paywall context) | `docs/economy/token/` |
| Bilateral Bond manifesto | `.mind/manifesto/THE_BILATERAL_BOND_MANIFESTO.md` |
| Project-level SYNC | `.mind/state/SYNC_Project_State.md` |
