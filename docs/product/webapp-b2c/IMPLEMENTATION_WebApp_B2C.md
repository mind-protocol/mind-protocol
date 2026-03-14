# WebApp B2C -- Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
BEHAVIORS:       ./BEHAVIORS_WebApp_B2C.md
PATTERNS:        ./PATTERNS_WebApp_B2C.md
ALGORITHM:       ./ALGORITHM_WebApp_B2C.md
VALIDATION:      ./VALIDATION_WebApp_B2C.md
THIS:            IMPLEMENTATION_WebApp_B2C.md (you are here)
SYNC:            ./SYNC_WebApp_B2C.md

IMPL:            mind-platform/app/
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

Target structure for mind-platform after B2C implementation:

```
mind-platform/
├── app/
│   ├── (auth)/                           # Auth route group (public)
│   │   ├── sign-in/
│   │   │   └── page.tsx                  # Sign-in page (Google + email)
│   │   ├── verify/
│   │   │   └── page.tsx                  # Magic link verification
│   │   └── layout.tsx                    # Minimal layout (no sidebar)
│   ├── (app)/                            # Authenticated route group
│   │   ├── chat/
│   │   │   ├── page.tsx                  # Chat interface (client component)
│   │   │   ├── [conversation_id]/
│   │   │   │   └── page.tsx              # Specific conversation
│   │   │   └── components/
│   │   │       ├── chat_message_bubble_and_avatar.tsx
│   │   │       ├── chat_input_with_model_indicator.tsx
│   │   │       └── chat_streaming_response_renderer.tsx
│   │   ├── brief/
│   │   │   ├── page.tsx                  # Today's brief (server component)
│   │   │   ├── [date]/
│   │   │   │   └── page.tsx              # Historical brief by date
│   │   │   └── components/
│   │   │       ├── brief_section_card_renderer.tsx
│   │   │       └── brief_navigation_date_picker.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx                  # Biometric dashboard (client component)
│   │   │   └── components/
│   │   │       ├── biometric_chart_panel_with_zones.tsx
│   │   │       ├── biometric_trend_indicator_badge.tsx
│   │   │       ├── biometric_range_selector_tabs.tsx
│   │   │       └── biometric_export_button_and_dialog.tsx
│   │   ├── profile/
│   │   │   ├── page.tsx                  # User profile and settings
│   │   │   └── components/
│   │   │       ├── garmin_connection_status_and_oauth.tsx
│   │   │       ├── llm_model_selector_with_capabilities.tsx
│   │   │       └── user_preferences_form.tsx
│   │   ├── history/
│   │   │   ├── page.tsx                  # Conversation history list
│   │   │   └── components/
│   │   │       ├── conversation_list_item_with_preview.tsx
│   │   │       └── conversation_search_input.tsx
│   │   └── layout.tsx                    # App shell (sidebar + nav + citizen context)
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts              # Auth.js API route
│   │   ├── chat/
│   │   │   └── send/
│   │   │       └── route.ts              # Chat message endpoint (streaming)
│   │   ├── biometrics/
│   │   │   ├── route.ts                  # Biometric data retrieval
│   │   │   └── export/
│   │   │       └── route.ts              # CSV/PDF export
│   │   ├── brief/
│   │   │   └── route.ts                  # Brief retrieval
│   │   └── models/
│   │       └── route.ts                  # Available models list
│   ├── layout.tsx                        # Root layout (fonts, metadata, providers)
│   └── page.tsx                          # Landing / redirect to chat
├── components/
│   ├── ui/                               # shadcn/ui components
│   ├── app_shell_sidebar_navigation.tsx  # Main sidebar
│   └── citizen_context_provider.tsx      # React context for citizen data
├── lib/
│   ├── auth_configuration_and_providers.ts
│   ├── mind_mcp_api_client.ts            # HTTP client for mind-mcp backend
│   ├── garmin_oauth_client_and_token_store.ts
│   ├── biometric_data_transformer_and_chart_adapter.ts
│   └── session_middleware_and_route_guard.ts
├── styles/
│   └── globals.css                       # Tailwind + custom tokens
├── middleware.ts                          # Auth middleware (route protection)
├── next.config.js
├── tailwind.config.ts
└── package.json
```

### File Responsibilities

| File | Purpose | Key Exports | Status |
|------|---------|-------------|--------|
| `middleware.ts` | Auth guard for all /(app) routes | NextResponse redirect logic | PLANNED |
| `lib/mind_mcp_api_client.ts` | Typed HTTP client for mind-mcp | `sendMessage()`, `fetchBrief()`, `fetchBiometrics()` | PLANNED |
| `lib/auth_configuration_and_providers.ts` | Auth.js config (Google + email) | `authOptions` | PLANNED |
| `lib/garmin_oauth_client_and_token_store.ts` | Garmin OAuth2 flow + encrypted token storage | `connectGarmin()`, `getGarminToken()` | PLANNED |
| `lib/biometric_data_transformer_and_chart_adapter.ts` | Transform raw Garmin data to chart format | `transformForChart()`, `computeTrend()` | PLANNED |
| `app/(app)/layout.tsx` | App shell with sidebar, nav, citizen context | Shell component | PLANNED |
| `app/(app)/chat/page.tsx` | Chat interface (main product surface) | Chat page component | PLANNED |
| `app/api/chat/send/route.ts` | Chat API: context assembly + LLM streaming | POST handler returning ReadableStream | PLANNED |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Next.js App Router with route groups (hybrid SSR + client)

**Why this pattern:** Next.js 14 App Router gives us server components for static content (brief, profile), client components for interactive features (chat, dashboard), middleware for auth, and API routes for backend calls -- all in one framework. No separate frontend/backend repos for the web surface.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Route Groups | `(auth)`, `(app)` | Separate auth layout from app layout without URL nesting |
| Server Components | Brief, profile, history list | Fast first paint, less JS shipped |
| Client Components | Chat, dashboard charts | Interactive state management |
| Provider Pattern | `citizen_context_provider.tsx` | Share citizen data across feature modules without prop drilling |
| API Route Streaming | `api/chat/send/route.ts` | Return ReadableStream for SSE chat responses |
| Adapter Pattern | `mind_mcp_api_client.ts` | Isolate mind-mcp API shape from UI components |

### Anti-Patterns to Avoid

- **Client-side auth checks**: Don't check auth in components. Middleware handles it. Components assume they are authenticated.
- **Direct LLM calls from frontend**: Never call LLM providers from the browser. Always go through API routes which call mind-mcp.
- **Global state for everything**: Use React context for citizen data. Use local state for UI. Don't put transient UI state in context.
- **Custom chart implementation**: Use Recharts or Nivo. Don't build chart primitives.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Auth | Session management, token refresh, provider config | Feature modules (they just check `session`) | `useSession()` hook |
| API Client | HTTP calls, error handling, type mapping | UI components (they call typed functions) | `lib/mind_mcp_api_client.ts` exports |
| Biometric Transform | Data normalization, zone calculation, trend math | Chart rendering (receives clean data) | `transformForChart()` output shape |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| Auth flow | `app/(auth)/sign-in/page.tsx` | User visits app unauthenticated |
| Chat | `app/(app)/chat/page.tsx` | Default route after auth |
| Brief | `app/(app)/brief/page.tsx` | User navigates to brief |
| Dashboard | `app/(app)/dashboard/page.tsx` | User navigates to dashboard |
| Profile | `app/(app)/profile/page.tsx` | User navigates to settings |
| Chat API | `app/api/chat/send/route.ts` | Chat page sends message |
| Export API | `app/api/biometrics/export/route.ts` | Dashboard export button |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Chat Message Flow: User Input to Streaming Response

The most critical flow. Crosses browser -> Next.js API route -> mind-mcp backend -> LLM provider -> back through the same chain as a stream.

```yaml
flow:
  name: chat_message_flow
  purpose: Transform user message into streamed citizen response
  scope: Browser to LLM and back
  steps:
    - id: user_submit
      description: User types message and submits
      file: app/(app)/chat/page.tsx
      function: handleSubmit()
      input: string (message text)
      output: fetch request to /api/chat/send
      trigger: form submit or Enter key
      side_effects: optimistic UI update (message appears immediately)
    - id: api_route
      description: API route receives message, assembles context, calls mind-mcp
      file: app/api/chat/send/route.ts
      function: POST()
      input: { conversation_id, message, model_override }
      output: ReadableStream of tokens
      trigger: POST request from chat page
      side_effects: message persisted to database
    - id: stream_render
      description: Client reads stream and renders tokens incrementally
      file: app/(app)/chat/components/chat_streaming_response_renderer.tsx
      function: StreamRenderer component
      input: ReadableStream
      output: DOM updates (token by token)
      trigger: stream data events
      side_effects: scroll position maintained
  docking_points:
    available:
      - id: dock_chat_submit
        type: api
        direction: input
        file: app/api/chat/send/route.ts
        function: POST()
        trigger: form submit
        payload: { conversation_id, message, model_override }
        async_hook: not_applicable
        needs: none
        notes: Entry point for all chat interactions
      - id: dock_chat_stream
        type: stream
        direction: output
        file: app/api/chat/send/route.ts
        function: POST()
        trigger: LLM response
        payload: ReadableStream<string>
        async_hook: required
        needs: none
        notes: Streaming response -- critical for B2, V3
    health_recommended:
      - dock_id: dock_chat_submit
        reason: Entry point for core product interaction, must verify auth + persistence
      - dock_id: dock_chat_stream
        reason: Streaming must actually stream (V3), latency must be under 2s
```

### Biometric Data Flow: Garmin to Charts

```yaml
flow:
  name: biometric_data_flow
  purpose: Transform raw Garmin data into visual health dashboard
  scope: Garmin API to rendered charts
  steps:
    - id: garmin_fetch
      description: Backend fetches data from Garmin Connect API
      file: lib/garmin_oauth_client_and_token_store.ts
      function: fetchGarminData()
      input: { metrics[], date_range }
      output: raw Garmin API response
      trigger: dashboard page load
      side_effects: token refresh if expired
    - id: transform
      description: Raw data transformed to chart-ready format
      file: lib/biometric_data_transformer_and_chart_adapter.ts
      function: transformForChart()
      input: raw Garmin data
      output: { series[], zones, trend }
      trigger: data received
      side_effects: none
    - id: render
      description: Charts rendered with zones and trends
      file: app/(app)/dashboard/components/biometric_chart_panel_with_zones.tsx
      function: ChartPanel component
      input: transformed data
      output: DOM (SVG charts)
      trigger: React render
      side_effects: none
```

---

## MODULE DEPENDENCIES

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `next` (14.x) | Framework (App Router, SSR, API routes) | Everywhere |
| `next-auth` (5.x) | Authentication (Google OAuth, email magic link) | `lib/auth_*`, `middleware.ts` |
| `recharts` or `@nivo/core` | Chart rendering for biometric dashboard | `dashboard/components/` |
| `tailwindcss` | Utility-first CSS | `styles/globals.css` |
| `@radix-ui/*` / `shadcn/ui` | UI component primitives | `components/ui/` |
| `react-pdf` or `@react-pdf/renderer` | PDF export for biometrics | `api/biometrics/export/` |
| `zod` | Runtime type validation for API inputs/outputs | `lib/`, `api/` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Auth session | HTTP-only cookie + server-side session store | Global | 30 days rolling |
| Citizen context | React Context (`citizen_context_provider.tsx`) | App-wide | Session duration |
| Chat messages | Local component state + API persistence | Chat page | Persistent (API) |
| Dashboard data | Local component state (fetched on mount) | Dashboard page | Page session |
| User preferences | API persistence (mind-mcp) | Profile page | Persistent |
| Model selection | User preferences (API) | Profile -> Chat | Persistent |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `NEXTAUTH_SECRET` | `.env` | none (required) | Auth.js session encryption key |
| `NEXTAUTH_URL` | `.env` | `http://localhost:3000` | Canonical app URL |
| `GOOGLE_CLIENT_ID` | `.env` | none (required for Google) | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | `.env` | none (required for Google) | Google OAuth secret |
| `MIND_MCP_URL` | `.env` | `http://localhost:8000` | mind-mcp backend URL |
| `GARMIN_CLIENT_ID` | `.env` | none (required for Garmin) | Garmin Connect OAuth client ID |
| `GARMIN_CLIENT_SECRET` | `.env` | none (required for Garmin) | Garmin Connect OAuth secret |
| `SMTP_HOST` | `.env` | none (for magic link) | Email provider for magic links |

---

## MARKERS

<!-- @mind:todo Evaluate next-auth v5 vs v4 -- v5 has App Router native support but may have breaking changes -->
<!-- @mind:escalation Current mind-platform code needs audit -- what exists that can be reused vs what must be replaced? -->
<!-- @mind:proposition Consider tRPC instead of raw API routes for type-safe client-server communication -->
<!-- @mind:todo Define the exact Garmin API endpoints needed for each biometric metric -->
