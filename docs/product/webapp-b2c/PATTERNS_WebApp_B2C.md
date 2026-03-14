# WebApp B2C -- Patterns: The Human Surface of Mind Protocol

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
THIS:            PATTERNS_WebApp_B2C.md (you are here)
BEHAVIORS:       ./BEHAVIORS_WebApp_B2C.md
ALGORITHM:       ./ALGORITHM_WebApp_B2C.md
VALIDATION:      ./VALIDATION_WebApp_B2C.md
IMPLEMENTATION:  ./IMPLEMENTATION_WebApp_B2C.md
SYNC:            ./SYNC_WebApp_B2C.md

IMPL:            mind-platform/app/
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC_WebApp_B2C.md: "Docs updated, implementation needs: {what}"

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_WebApp_B2C.md: "Implementation changed, docs need: {what}"

---

## THE PROBLEM

mind-platform exists as a Next.js 14 app but it serves developers: connectome explorer, schema browser, graph visualizations. No end user would open it. No bond forms through it. The entire MIND infrastructure -- citizens, bonds, briefs, LLM routing, biometrics -- has no human-facing surface.

Without the B2C web app, MIND is a backend with no front door. Users can't talk to their citizen, can't see their brief, can't review their biometrics, can't feel the bond. The product doesn't exist until the surface exists.

---

## THE PATTERN

**Shell + Feature Modules inside a single Next.js App Router application.**

The app is organized as a shell (layout, nav, auth boundary) containing feature modules that are independently developable:

```
Shell (layout + auth + nav)
  |
  +-- /chat         -- Primary interaction surface (real-time, streaming)
  +-- /brief        -- Morning brief display (SSR, mostly static)
  +-- /dashboard    -- Biometric charts and trends (client-side, data-heavy)
  +-- /profile      -- User settings, Garmin connection, LLM selector
  +-- /history      -- Conversation archive (search + pagination)
```

Each feature module is a route group with its own loading states, error boundaries, and data fetching. The shell provides the authenticated layout and navigation. Feature modules don't know about each other -- they communicate through shared state (the user's citizen context) and the backend API.

Key architectural insight: **the chat is the center of gravity.** Every other feature exists to enrich the chat. The brief is context the citizen surfaces. The dashboard is data the citizen interprets. The profile configures the chat experience. The layout reflects this -- chat is the default route, everything else is secondary navigation.

---

## BEHAVIORS SUPPORTED

- B1 (Auth Flow) -- Shell handles auth boundary, redirects unauthenticated users
- B2 (Chat Interaction) -- Chat module is the primary route, optimized for real-time
- B3 (Brief Display) -- Brief module is SSR for fast first paint
- B5 (Biometric Dashboard) -- Dashboard module handles data-heavy client rendering
- B6 (Model Selection) -- Profile module surfaces Router capabilities

## BEHAVIORS PREVENTED

- A1 (Unauthenticated Access) -- Auth middleware blocks all feature routes
- A2 (Developer Tool Leakage) -- Developer features separated by route group, behind flag

---

## PRINCIPLES

### Principle 1: Chat-Centric Layout

The chat is the default destination after auth. Navigation treats everything else as secondary. The user should feel they are "in conversation with their citizen" at all times, with other features as enrichments accessible from the chat context. Not a dashboard app with a chat sidebar -- a chat app with dashboard capabilities.

### Principle 2: Progressive Data Enrichment

Not every user has Garmin. Not every user has configured their LLM preference. Not every morning brief has biometric data. The UI adapts to what's available without showing empty states that feel broken. A user with only chat sees a clean chat. A user with Garmin sees biometric insights woven into the experience. The UI grows with the user's integration depth.

### Principle 3: Server Components for Static, Client Components for Interactive

Next.js App Router gives us the choice. Brief display, profile pages, history lists -- these are server components (fast, SEO-friendly, cacheable). Chat streaming, biometric charts, real-time updates -- these are client components (interactive, stateful). The boundary is explicit and intentional, not accidental.

### Principle 4: Auth as Invisible Infrastructure

The user should never "think about" authentication. Magic link email (click and you're in) or Google OAuth (one tap). Session persists via HTTP-only cookies. Middleware handles refresh. No login page that feels like a wall -- a flow that feels like opening a door.

### Principle 5: WHOOP-Level Visual Quality for Biometrics

The biometric dashboard is not a data dump. It is a health narrative with visual clarity on par with WHOOP or Oura Ring apps. Clean charts (Recharts or Nivo), meaningful color coding (green/yellow/red zones), trend lines that tell a story (7/30/90 day windows), and export capabilities (CSV for data people, PDF for sharing with coaches or doctors).

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| mind-mcp API | API | Chat messages, brief content, conversation history, citizen context |
| Garmin Connect API | API | HR, HRV, sleep stages, stress, body battery -- via OAuth2 connection |
| NextAuth / Auth.js | Library | Authentication providers (email magic link, Google OAuth) |
| User preferences | DB | LLM model selection, notification preferences, display settings |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `docs/product/llm-router/` | Chat requires LLM routing; model selector surfaces Router capabilities |
| `docs/product/brief-matinal/` | Brief display renders the brief this module generates |
| `docs/product/wearable-bridges/` | Biometric dashboard consumes data from Garmin bridge |
| `docs/product/chat-bridges/` | Chat backend that the web interface calls |
| `l4/registry/` | User identity, citizen pairing, trust level |

---

## INSPIRATIONS

- **ChatGPT web app** -- Chat-centric layout with sidebar history. But impersonal -- no bond, no biometrics, no morning ritual.
- **WHOOP app** -- Biometric visualization quality. HRV trends, sleep staging, recovery score. The bar for what "good health data display" looks like.
- **Oura Ring app** -- Readiness score, sleep quality visualization. Clean, approachable, not clinical.
- **Linear** -- App shell pattern: fast, keyboard-navigable, feature modules in a consistent frame. The gold standard for SaaS UI responsiveness.
- **Vercel dashboard** -- Next.js dogfooding. Server components for static content, client for interactive. Proof the pattern works at scale.

---

## SCOPE

### In Scope

- Authentication (email magic link + Google OAuth)
- Chat interface with streaming responses
- Morning brief display
- User profile and settings
- LLM model selector
- Garmin OAuth connection flow
- Biometric dashboard (HR, HRV, sleep, stress -- charts with 7/30/90 day views)
- Biometric export (CSV + PDF)
- Conversation history with search
- Responsive layout (works on mobile browsers, optimized for desktop)

### Out of Scope

- Coach dashboard (multi-client view) --> S22-S23, separate route group
- Admin console (enterprise user management) --> S24-S25, separate route group
- Partner dashboard --> future, separate route group
- React Native mobile app --> `docs/product/react-native-app/`
- Stripe integration / paywall --> `docs/product/stripe-paywall/`
- Push notifications --> requires service worker, v2
- Offline mode --> v2, requires service worker + local storage strategy
- Calendar / email bridge display --> separate product modules, integrated later

---

## MARKERS

<!-- @mind:escalation Garmin OAuth2 flow requires Garmin Developer Portal registration -- who registers the app? -->
<!-- @mind:proposition Consider WebSocket for chat instead of SSE to enable bidirectional real-time features later -->
<!-- @mind:todo Define the exact API contract between webapp and mind-mcp for chat, brief, and biometrics endpoints -->
