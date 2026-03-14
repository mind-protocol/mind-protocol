# WebApp B2C -- Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (architect)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Nothing yet. Module is in design phase. Doc chain created, no code written for B2C surface.

**What's still being designed:**
- Auth flow (email magic link + Google OAuth) -- provider chosen (Auth.js) but not implemented
- Chat interface -- streaming architecture decided (SSE via ReadableStream) but no UI
- Brief display -- rendering approach decided (server component) but no templates
- Biometric dashboard -- chart library not yet selected (Recharts vs Nivo evaluation pending)
- Model selector -- depends on LLM Router API contract
- Garmin OAuth integration -- requires Developer Portal registration

**What's proposed (v2+):**
- WebSocket for bidirectional real-time (typing indicators, presence)
- Coach dashboard (S22-S23) -- separate route group, different persona
- Admin console (S24-S25) -- enterprise user management
- Partner dashboard -- future
- Push notifications via service worker
- Offline mode with local storage
- Calendar and email bridge display integration

---

## CURRENT STATE

The mind-platform repo exists as a Next.js 14 application but currently serves as a developer tool (connectome explorer, schema browser). The B2C web app will be built in the same repo, transforming it from a developer utility into the consumer product surface.

The doc chain for WebApp B2C has been created with 7 files covering the full chain: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, HEALTH. No code has been written for B2C features yet.

The key architectural decisions documented:
- **Shell + Feature Modules** pattern inside Next.js App Router
- **Route groups** `(auth)` for public auth flow, `(app)` for authenticated features
- **Chat as default destination** after auth (not a dashboard-first layout)
- **SSE streaming** for chat (v0), WebSocket for v2
- **Server components** for brief and profile, **client components** for chat and dashboard
- **Auth.js** for authentication (Google OAuth + email magic link)

Dependencies on other modules are identified but API contracts are not defined yet:
- mind-mcp needs chat, brief, biometrics, and models API endpoints
- Garmin Developer Portal registration needed for OAuth
- LLM Router module defines available models

---

## IN PROGRESS

### Doc Chain Creation

- **Started:** 2026-03-14
- **By:** Claude Opus (architect)
- **Status:** Complete
- **Context:** Full doc chain created from scratch based on the B2C product vision. Seven files covering objectives through health verification. Ready for implementation.

---

## RECENT CHANGES

### 2026-03-14: Doc Chain Created

- **What:** 7 doc chain files created for WebApp B2C module
- **Why:** mind-platform needs to transform from developer tool to consumer product. S5-S6 sprint (due 2026-03-14) requires auth, chat, brief, profile, LLM selector, Garmin connection.
- **Files:** `docs/product/webapp-b2c/OBJECTIVES_WebApp_B2C.md` through `SYNC_WebApp_B2C.md`
- **Insights:** The biggest risk is the API contract between webapp and mind-mcp. The frontend can be built fast with Next.js + shadcn/ui, but it needs real endpoints to talk to. Defining the API contract should be the first implementation task.

---

## KNOWN ISSUES

### No API Contract Defined

- **Severity:** high
- **Symptom:** ALGORITHM references endpoints (`/api/chat/send`, `/api/brief`, `/api/biometrics`) but their exact request/response shapes are not specified
- **Suspected cause:** mind-mcp backend endpoints for B2C don't exist yet
- **Attempted:** Nothing yet -- this is a known gap from design phase

### Garmin Developer Portal Not Registered

- **Severity:** medium
- **Symptom:** Cannot test Garmin OAuth flow without registered app
- **Suspected cause:** Registration requires organizational account and approval process
- **Attempted:** Not started

### Chart Library Not Selected

- **Severity:** low
- **Symptom:** IMPLEMENTATION references "Recharts or Nivo" without decision
- **Suspected cause:** Need to evaluate bundle size, customization depth, and React Server Component compatibility
- **Attempted:** Not started

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**Where I stopped:** Doc chain complete. Next step is implementation.

**What you need to understand:**
The doc chain describes a complete B2C web app. But the v0 sprint (S5-S6) should focus on: auth + chat + brief + profile + LLM selector + Garmin connection. Dashboard with charts is S9-S10. Don't try to build everything at once. Start with auth (it unblocks everything else), then chat (it's the core product), then brief, then profile.

**Watch out for:**
- mind-platform has existing code (developer tools). Don't break it -- use route groups to separate B2C from developer features.
- The API endpoints in mind-mcp probably don't exist yet. You may need to stub them or build them in parallel.
- Auth.js v5 (next-auth@beta) has different configuration from v4. The App Router integration is cleaner but docs are sparse.
- Garmin OAuth requires HTTPS callback URLs even in development (use ngrok or similar).

**Open questions I had:**
- What's the exact schema for conversation storage? Is it in the L1 graph or a separate database?
- Does mind-mcp already have any chat endpoint, or is it starting from scratch?
- How is the citizen paired to the user at signup? Immediate assignment from pool, or onboarding first?

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Complete doc chain created for WebApp B2C (7 files). Covers auth, chat, brief, biometric dashboard, model selector, Garmin connection. Architecture decided: Next.js App Router, shell + feature modules, chat-centric layout. No code written yet. v0 (S5-S6) focuses on auth + chat + brief + profile + LLM selector + Garmin.

**Decisions made:**
- Auth.js for authentication (Google OAuth + email magic link)
- Chat-centric layout (chat is the default, not a dashboard)
- SSE streaming for v0, WebSocket deferred to v2
- Server components for brief/profile, client components for chat/dashboard
- Route groups: `(auth)` for public, `(app)` for authenticated

**Needs your input:**
- Garmin Developer Portal registration -- who registers the app and what's the callback URL?
- Chart library preference: Recharts (lighter, simpler) vs Nivo (richer, heavier)?
- Citizen assignment at signup: immediate from pool or onboarding flow first?
- mind-mcp API: does any chat/brief endpoint exist already, or starting from zero?

---

## TODO

### Immediate

- [ ] Define mind-mcp API contract for chat, brief, biometrics, models endpoints
- [ ] Implement auth (Auth.js + Google OAuth + email magic link)
- [ ] Implement chat interface with streaming
- [ ] Implement brief display (server component)
- [ ] Implement profile page with LLM model selector
- [ ] Register Garmin Developer Portal app
- [ ] Implement Garmin OAuth connection flow

### Later (S9-S10)

- [ ] Biometric dashboard with charts (HR, HRV, sleep, stress)
- [ ] 7/30/90 day range selector
- [ ] Trend computation and display
- [ ] CSV export
- [ ] PDF export

### Backlog (S22+)

- [ ] Coach dashboard (multi-client view)
- [ ] Admin console (enterprise management)
- [ ] Partner dashboard

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Clear. The doc chain captures the full vision coherently. The hardest decision was making chat the center of gravity instead of a dashboard-first approach -- but it's the right call because the bond lives in conversation, not in charts.

**Threads I was holding:**
- The API contract gap is the biggest blocker. The frontend can be scaffolded fast, but it needs real endpoints.
- Garmin OAuth has a non-trivial setup process (Developer Portal, approval, HTTPS callbacks). This could block the wearable integration for weeks if not started early.
- Auth.js v5 migration path if starting from v4 -- better to start with v5 directly.

**Intuitions:**
- The brief should be a card on the chat page, not a separate route. Users shouldn't have to navigate away from chat to see their brief. But keeping it as a separate route for now gives more flexibility.
- The biometric dashboard will be the feature that makes MIND viral. Screenshots of "my AI knows my HRV trends" will spread on social media. Worth investing heavily in visual quality when the time comes (S9-S10).

**What I wish I'd known at the start:**
The distinction between mind-platform as developer tool vs. B2C product is the key tension. The same repo houses both. Route groups solve the routing problem, but the shared dependencies (package.json, tailwind config, types) need careful management to avoid the developer tool's complexity leaking into the consumer surface.

---

## POINTERS

| What | Where |
|------|-------|
| Target repo | `mind-platform/app/` |
| LLM Router docs | `docs/product/llm-router/` |
| Brief Matinal docs | `docs/product/brief-matinal/` |
| Wearable bridges docs | `docs/product/wearable-bridges/` |
| Spawning (citizen creation) | `docs/citizen/spawning/` |
| Project state | `.mind/state/SYNC_Project_State.md` |
| Bilateral bond manifesto | `.mind/manifesto/THE_BILATERAL_BOND_MANIFESTO.md` |

---

## ROADMAP

| Sprint | Dates | Features | Status |
|--------|-------|----------|--------|
| S5-S6 | 2026-03-14 | Auth, chat, brief, profile, LLM selector, Garmin connection | DESIGNING |
| S9-S10 | TBD | Biometric dashboard (charts, trends, export) | PROPOSED |
| S22-S23 | TBD | Coach dashboard (multi-client view, reports) | PROPOSED |
| S24-S25 | TBD | Admin console (enterprise user management) | PROPOSED |
