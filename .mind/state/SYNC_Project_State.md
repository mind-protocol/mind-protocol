# Project — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
```

---

## CURRENT STATE

**Total tests: 357 passing.** Zero regressions.

**L4 Protocol:** Schema (34), Registry (49), Work (5), Spawning (26), Laws (53) = 167 tests.
**Economy:** Token (61) = 61 tests.
**Other:** Schema validators, crypto, integration = remaining tests.

**$MIND token DEPLOYED to Solana devnet.** TransferHook active.

### Devnet Deployment (2025-01-06)

| Component | Address |
|-----------|---------|
| **$MIND Token** | `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa` |
| **TransferHook Program** | `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD` |
| **Mint Authority** | `CCsJLZR8b19iDgS9hXUYs9q2c928ihzZdfSgZLPYffWg` |

The protocol now has:
- Fixed schema with 5 node types (actor, moment, narrative, space, thing)
- Single link type with semantic axes (polarity, hierarchy, permanence, emotions)
- Registry for citizens and orgs with hash verification
- $MIND token LIVE on devnet (SPL Token 2022 with extensions)
- TransferHook program DEPLOYED for transfer validation
- Mechanical mint/burn conditions (M1-M4, B1-B5)

---

## ACTIVE WORK

### React Native App — DOC CHAIN CREATED (2026-03-14)

- **Area:** `docs/product/react-native-app/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for the React Native (Expo) mobile app. MIND on every smartphone. One TypeScript codebase for iOS + Android. 8 screens: Onboarding (< 90s target), Chat (WebSocket streaming), Brief Matinal, Biometric Dashboard, Profile, LLM Selector, Settings (wearable connection), Duo Mode. Native modules: HealthKit (iOS), Health Connect (Android). Push notifications via Firebase + APNs. Thin client architecture — all intelligence in membrane. 9 behaviors, 10 validation invariants, 6 health indicators.
- **Target:** `mind-app/` (external repo, currently Expo 54 boilerplate only)
- **Effort:** 4 weeks setup + screens, 2 weeks wearables + push
- **Roadmap:** S13-S16 (28 April - 23 May 2026)
- **Next:** Set up Expo Router navigation, implement auth flow, build Chat screen with WebSocket streaming

### WebApp B2C — DOC CHAIN CREATED (2026-03-14)

- **Area:** `docs/product/webapp-b2c/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for the B2C web application. MIND's consumer surface: auth (email magic link + Google OAuth), chat (SSE streaming), morning brief display (SSR), biometric dashboard (HR/HRV/sleep/stress charts, 7/30/90d views, CSV/PDF export, WHOOP-level visuals), LLM model selector, Garmin OAuth connection, user profile, conversation history. Architecture: Next.js 14 App Router, shell + feature modules, chat-centric layout. 8 behaviors, 8 validation invariants, 6 health indicators.
- **Target:** `mind-platform :: app/`
- **Effort:** 4-5 weeks for v0, ongoing additions
- **Roadmap:** v0 (S5-S6): auth + chat + brief + profile + LLM selector + Garmin. Dashboard (S9-S10). Coach (S22-S23). Admin (S24-S25).
- **Next:** Define mind-mcp API contract, implement auth, implement chat
### Email Bridge — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/email-bridge/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for the Email Bridge module. Strategy: IMAP/SMTP as universal filet (100% provider coverage), native APIs (Gmail L3, Outlook L2) for progressive enrichment. Three levels of functionality. Adapter pattern isolates protocol-specific logic. Sync pipeline with 2-min polling, relevance filtering before graph ingestion, 30-day initial sync window. 10 validation invariants.
- **Target:** `mind-mcp :: runtime/bridges/email/`
- **Effort:** ~2 weeks (IMAP 1 week + Outlook 3-4 days, Gmail partially ready from auth)
- **Next:** Implement BaseAdapter, then IMAPAdapter (Week 1 priority)

### LLM Router — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/llm-router/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for the LLM Router module: OBJECTIVES, PATTERNS, BEHAVIORS, ALGORITHM, VALIDATION, IMPLEMENTATION, SYNC. Strategy + Chain of Responsibility pattern. 8 direct providers (Anthropic, OpenAI, Google, Mistral, DeepSeek, Llama, Grok, OpenRouter). Unified async streaming, tier-based model selection, BYOAI passthrough, fallback chain, cost tracking.
- **Target:** `mind-mcp/runtime/llm_router/`
- **Effort:** 3-4 days architecture + 1 day per provider adapter
- **Next:** Implement types.py, base interface, Gemini adapter (replace existing direct calls), then router core

### Wearable Bridges — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/wearable-bridges/`
- **Status:** **DESIGNING** (8-file doc chain complete, no code in mind-protocol)
- **What:** Full documentation chain for the Wearable Bridges module. Strategy: 3 aggregators (Garmin LIVE, Apple HealthKit, Google Health Connect) cover ~95% of wearable market at launch. Post-launch: 7 direct APIs (Oura, WHOOP, Strava, Fitbit, Samsung Health, Polar, Withings) for premium data. Pipeline: fetch -> normalize -> dedup -> graph_write. Adapter pattern per source. NormalizedBodySample canonical schema. Confidence-based dedup (direct API > aggregator). 8 validation invariants. 6 health checkers specified (all pending).
- **Target:** `mind-mcp :: runtime/integrations/wearables/` (server-side), `mind-app` (HealthKit/Health Connect native modules)
- **Roadmap:** S15-S16 (12-23 May 2026) for HealthKit + Health Connect. Garmin already live.
- **Next:** Verify Garmin adapter in mind-mcp matches doc chain patterns. Decide app-to-server transport. Codify WearableAdapter abstract class.

### Brief Matinal — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/brief-matinal/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for MIND's wedge application. Pipeline architecture: alarm trigger -> parallel data collection (wearables, calendar, email, conversation memory) -> context assembly with graceful degradation -> LLM generation in citizen's voice -> multi-surface delivery (Telegram/WhatsApp/WebApp/push). 7 validation invariants. Designed for incremental implementation (conversation-memory-only mode first).
- **Target:** `mind-mcp/runtime/features/brief_matinal/`
- **Dependencies:** LLM Router, calendar bridge, email bridge, wearable bridge (none exist yet)
- **Next:** Can start with conversation-memory-only mode. Needs LLM Router interface definition first.

### Stripe Paywall — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/stripe-paywall/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for MIND's monetization layer. B2C: Free ($0, 10 msg/day), Pro ($14.90/mo), Pro+ ($24.90/mo), Premium ($39.90/mo). B2B Micro: Solo ($149), Practice ($199), Studio ($299). B2B Enterprise: Team ($299+$22/seat), Business ($799+$20/seat). Stripe Checkout redirect for payment, webhook-driven tier lifecycle, rate limiting in mind-mcp, conversational upsell via LLM prompt context injection. 8 validation invariants.
- **Target repos:** `mind-ops/billing/` (Stripe integration), `mind-mcp/rate_limiting/` (enforcement)
- **Effort:** 2-3 days Stripe + 1 day rate limiting
- **Roadmap:** S3-S4 (was due 28 Feb, behind schedule)
- **Next:** Create HEALTH file, confirm mind-ops DB schema and web framework, implement tier_config_and_price_mapping.py first

### Duo Mode — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/duo-mode/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for MIND's wedge #2 — companion for couples. Pearson correlation on HR streams produces synchrony score (0-100). 5-phase state machine (Baseline/Drift/Divergence/Crisis/Recovery) with hysteresis and minimum dwell. Timing-only interventions — never content mediation. 11 validation invariants. Viral by structure: every activation requires 2 MIND users. B2B extension: CoachSession (1 coach, N DuoSession children) designed but v2.
- **Target:** `mind-mcp/runtime/features/duo_mode/`
- **Dependencies:** Biometric ingestion layer (does not exist), chat infrastructure (exists), L4 registry (exists), bilateral bond system (designing)
- **Roadmap:** S15-S16 (May 2026) for mobile
- **Next:** Implement pure computation modules first (alignment, Pearson, phase engine) — testable without infrastructure dependencies. Needs biometric ingestion layer and consent model decision before full implementation.

### Chat Bridges — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/chat-bridges/`
- **Status:** **DESIGNING** (7-file doc chain complete, no code)
- **What:** Full documentation chain for Chat Bridges module. Architecture: stateless transport adapters with canonical message format. 3 bridges LIVE (Telegram 795 LOC polling, WhatsApp 274 LOC WAHA webhook, Voice 385 LOC WebSocket). 4 planned: Messenger (S3-S4), Discord (S7-S8), Slack (S9-S10), Teams (S9-S10). Pattern: receive -> authenticate -> translate to canonical -> orchestrator -> translate back -> deliver. 10 validation invariants. Per-platform ceremony documented (auth, rate limits, typing, formatting).
- **Target:** `mind-mcp/runtime/bridges/{messenger,discord,slack,teams}/`
- **Effort:** ~2-3 weeks for all four bridges (2-4 days each)
- **Next:** Extract shared types module (CanonicalMessage Pydantic models), split Telegram bridge (795 LOC > 700L threshold), then build Messenger bridge

### Calendar Bridge — DOC CHAIN COMPLETE (2026-03-14)

- **Area:** `docs/product/calendar-bridge/`
- **Status:** **DESIGNING** (8-file doc chain complete, no code)
- **What:** Full documentation chain for Calendar Bridge module. Strategy: CalDAV is the IMAP of calendars -- one implementation covers Apple Calendar, Fastmail, Nextcloud, Synology, Zimbra, everything RFC 4791. Native APIs for Google Calendar (v3) and Outlook Calendar (via Microsoft Graph, shared OAuth token with email bridge). Three providers cover 100%. Pipeline architecture: fetch -> normalize -> diff -> apply. CalendarEvent unified model. Poll-based sync (5 min). 8 validation invariants. Feeds Brief Matinal, meeting preparation, and biometric-aware scheduling.
- **Target:** `mind-mcp/runtime/integrations/calendar/`
- **Effort:** ~1.5 weeks (CalDAV 2 days + Google 1 week + Outlook included via Graph)
- **Roadmap:** S7-S8 (17-28 March)
- **Next:** Implement CalDAV provider first (fastest, broadest coverage), then Google, then Outlook.

### Citizen Key Security — INVESTIGATED (2026-03-14)

- **Area:** `docs/security/space_encryption/`, `scripts/`
- **Status:** Investigated, documented, migration script prepared
- **What:** 5 citizens have X25519 keys on disk in `cities-of-light/citizens/{name}/.keys/`. Keys are untracked (never committed), but cities-of-light .gitignore is incomplete (only excludes private_key.b64, not public_key.b64). Migration script created at `scripts/migrate_citizen_keys_to_render_volume.sh`. SYNC_Space_Encryption.md updated with known issue.
- **Next:** Human must confirm Render volume path, execute migration, fix cities-of-light .gitignore

### Spawning Pipeline — COMPLETE (2026-03-14)

- **Area:** `l4/spawning/`, `docs/citizen/spawning/`
- **Status:** **CANONICAL v1**
- **Tests:** 26 passing
- **What:** Full pipeline: intent → seed → 4 safety gates → SID → Solana wallet → parent links
- **V2 planned:** Embedding-based seed selection (needs embedding infrastructure)

### Wallet Recovery — DOCUMENTED (2026-03-14)

- **Area:** `docs/citizen/wallet-recovery/`
- **Status:** Doc chain complete (8 files), code pending
- **Trigger:** Citizen DMs @nlr_ai on Telegram. Transfer, don't recover.

### Bonds Docs — CLEANED (2026-03-14)

- **Area:** `docs/economy/bonds/`
- **Status:** DESIGNING (aligned with manifesto)
- **What:** Removed all "staking" references. Bonds = 1:1 bilateral relationships. Added V0 (1:1 constraint), mutual consent, cooldown.

### P2 Laws — COMPLETE (2026-03-14)

- **Area:** `l4/laws/`
- **Status:** **COMPLETE**
- **Tests:** 53 passing
- **What:** Stimulus compliance checker (L1/L2/L5/L7), JWT detection, audit reporting. L3/L4/L6/L8 architectural (no runtime code). Callables for registry integration (sender_exists, verify_identity).

---

## RECENT CHANGES

### 2026-03-14: React Native App Documentation Chain Created

- **Who:** Claude Opus (groundwork)
- **What:** Full 7-file doc chain for the React Native (Expo) mobile app at `docs/product/react-native-app/`. Architecture: Expo 54 managed workflow, Expo Router file-based navigation, thin client (all intelligence in membrane). 8 screens: Onboarding (< 90s), Chat (WebSocket streaming), Brief Matinal (card stack), Biometric Dashboard (HR/sleep/steps/HRV charts), Profile, LLM Selector, Settings (wearable connection), Duo Mode. Native modules: HealthKit (iOS), Health Connect (Android) via platform bridge pattern. Push notifications via Firebase + APNs (max 3/day default). State: Zustand (UI) + TanStack Query (server). 9 behaviors, 10 validation invariants, 6 health indicators.
- **Files:** `docs/product/react-native-app/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,HEALTH,SYNC}_React_Native_App.md`
- **Key decisions:** Expo managed (not bare). Thin client -- no business logic in app. Platform Bridge pattern for HealthKit/Health Connect. 90s onboarding (2 screens). 15-min background biometric sync. 3 notifications/day cap. Zustand + TanStack Query.
- **Open:** Shared design system distribution (npm pkg vs monorepo vs submodule). Chart library (Victory Native vs Recharts). Duo Mode on small screens (split vs bottom-sheet). WebSocket protocol definition from mind-platform.

### 2026-03-14: Stripe Paywall Documentation Chain Created

- **Who:** Claude Opus (groundwork)
- **What:** Full 7-file doc chain for MIND's monetization layer. Stripe Checkout redirect for payment, webhook-driven tier lifecycle (checkout.session.completed, subscription.updated/deleted, invoice.payment_failed), rate limiting in mind-mcp, conversational upsell via LLM prompt context injection. B2C 4 tiers (Free/Pro/Pro+/Premium), B2B 5 tiers (Solo/Practice/Studio/Team/Business). 8 behaviors, 8 validation invariants, 7 implementation files planned across mind-ops and mind-mcp.
- **Files:** `docs/product/stripe-paywall/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,SYNC}_Stripe_Paywall.md`
- **Key decisions:** Stripe Checkout redirect (not embedded). Webhook as sole source of truth (no polling). Rate limiter fails closed. Conversational upsell via LLM context injection (not hardcoded messages). No payment provider abstraction (Stripe lock-in accepted).
- **Open:** mind-ops DB schema (new table vs extend users), web framework, daily message counter storage (Redis vs DB), Pro+/Premium message cap.

### 2026-03-14: WebApp B2C Doc Chain Created

- **Who:** Claude Opus (architect)
- **What:** Complete 7-file doc chain for WebApp B2C at `docs/product/webapp-b2c/`. Architecture: Next.js 14 App Router, shell + feature modules, chat-centric layout. Auth (email magic link + Google OAuth), chat (SSE streaming), morning brief (SSR), biometric dashboard (HR/HRV/sleep/stress, 7/30/90d, CSV/PDF export), LLM model selector, Garmin OAuth, user profile. 8 behaviors, 8 validation invariants, 6 health indicators.
- **Files:** `docs/product/webapp-b2c/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,HEALTH,SYNC}_WebApp_B2C.md`
- **Key decisions:** Chat-centric layout (not dashboard-first). SSE streaming for v0 (WebSocket v2). Server components for brief/profile, client components for chat/dashboard. Auth.js with Google + email magic link. WHOOP-level biometric visuals.
- **Open:** mind-mcp API contract, chart library (Recharts vs Nivo), Garmin Developer Portal registration, citizen assignment flow for new users.

### 2026-03-14: Calendar Bridge Documentation Chain Created

- **Who:** Claude Opus (groundwork)
- **What:** Full 8-file doc chain for Calendar Bridge module at `docs/product/calendar-bridge/`. Strategy: CalDAV as the IMAP of calendars (one implementation covers Apple, Fastmail, Nextcloud, Synology, Zimbra), native APIs for Google Calendar (v3) and Outlook (via Microsoft Graph, shared token with email bridge). Pipeline: fetch -> normalize -> diff -> apply. 7 behaviors, 8 validation invariants, 4 health indicators, 6 implementation files planned.
- **Files:** `docs/product/calendar-bridge/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,HEALTH,IMPLEMENTATION,SYNC}_Calendar_Bridge.md`
- **Key decisions:** CalDAV default provider. Outlook reuses email bridge Graph token. Poll-based sync (5 min interval, webhooks v2). 30-day sync window. CalendarEvent normalized model. Provider strategy pattern. CalDAV deletion detection via UID set comparison.
- **Open:** Deduplication false-positive risk on generic meeting names. CalDAV server compatibility testing needed. Meeting prep trigger mechanism.

### 2026-03-14: Email Bridge Doc Chain Created

- **Who:** Claude Opus (architect)
- **What:** Complete 7-file doc chain for Email Bridge at `docs/product/email-bridge/`. Architecture: IMAP/SMTP as universal filet (Level 1, any provider), Gmail API (Level 3), Microsoft Graph (Level 2). Adapter pattern. Four pipelines: connection, sync, ingestion, send. 10 validation invariants.
- **Files:** `docs/product/email-bridge/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,SYNC}_Email_Bridge.md`
- **Key decisions:** IMAP first, native APIs second. UID-based sync. Graph-based search for L1. Human approves all sends. Credentials encrypted in L1 graph.

### 2026-03-14: Brief Matinal Documentation Chain Created

- **Who:** Claude Opus (groundwork)
- **What:** Full 7-file doc chain for MIND's wedge application (product day 1). Pipeline: alarm -> parallel data collection (wearables, calendar, email, conversation memory) -> context assembly with graceful degradation -> LLM generation in citizen's voice -> multi-surface delivery. 6 behaviors, 7 validation invariants, 5 implementation files planned.
- **Files:** `docs/product/brief-matinal/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,SYNC}_Brief_Matinal.md`
- **Key:** Designed for incremental implementation. Conversation-memory-only mode works without any integration bridges. Each bridge adds a data source, not a dependency. No code yet.

### 2026-03-14: LLM Router Doc Chain Created

- **Who:** Claude Opus (architect)
- **What:** Complete 7-file doc chain for LLM Router at `docs/product/llm-router/`. Covers: multi-provider abstraction (8 direct + OpenRouter catch-all), unified async streaming, fallback chain with 2s target, tier-based model selection (free/paid), BYOAI key passthrough, cost tracking per request, rate limiting per tier. Full pseudocode in ALGORITHM, file structure in IMPLEMENTATION, 8 invariants in VALIDATION.
- **Files:** `docs/product/llm-router/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,SYNC}_LLM_Router.md`
- **Key decisions:** BYOAI gets no fallback to system key. Mid-stream failure is terminal. OpenRouter as catch-all last entry. Free tier = Gemini Flash/DeepSeek/Llama/Mistral. Paid tier = Claude Opus/GPT-4o/Gemini Pro.
- **Open:** LiteLLM vs custom adapters, rate limit backend (memory vs Redis), confirm model pools.

### 2026-03-14: Duo Mode Doc Chain Created

- **Who:** Claude Opus (groundwork)
- **What:** Full 7-file doc chain for Duo Mode (MIND wedge #2 -- companion for couples). Pearson correlation on HR streams, 5-phase state machine (Baseline/Drift/Divergence/Crisis/Recovery), timing-only interventions, 11 validation invariants. Viral by design (2-user requirement). B2B extension (CoachSession) architectured for v2.
- **Files:** `docs/product/duo-mode/{OBJECTIVES,PATTERNS,BEHAVIORS,ALGORITHM,VALIDATION,IMPLEMENTATION,SYNC}_Duo_Mode.md`
- **Key decisions:** HR (not HRV) as primary correlation signal for v1. Anti-correlation floors at 0. 300s rolling window. Recovery as distinct phase. Multi-Duo is v2. Pure Python stdlib, no external deps.
- **Open:** Consent model for biometric sharing, wearable API selection, intervention message tone, DuoSession persistence model, stress_index population norms.

### 2026-03-14: P2 Laws Module Implemented

- **Who:** Claude Opus (groundwork)
- **What:** Full L4 Laws module — constants, compliance checker, audit reporting, 53 tests
- **Files:** `l4/laws/constants.py`, `l4/laws/compliance.py`, `l4/laws/audit.py`, `l4/laws/__init__.py`, `tests/l4/test_laws_compliance_and_audit.py`
- **Key:** Runtime checks for L1 (schema), L2 (registered sender), L5 (no raw JWT + valid hash), L7 (fee minimum). L3/L4/L6/L8 architectural. Callables for registry integration. Removed empty placeholder file.

### 2026-03-14: Spawning Pipeline Implemented

- **Who:** Claude Opus (groundwork) + Nicolas (decisions)
- **What:** Full citizen spawning pipeline with safety gates, wallet at birth, parent links
- **Files:** `l4/spawning/` (2 files, ~300 LOC), `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py` (26 tests), `docs/citizen/spawning/` (8 files)
- **Key:** 4 safety gates (empathy, concentration ≤40%, diversity ≥3, clone distance ≥0.08), SID with entropy, Ed25519 wallet

### 2026-03-14: Wallet Recovery Module Documented

- **Who:** Claude Opus + Nicolas
- **What:** Full doc chain for wallet change procedure. Transfer-based recovery (identity is the key, not the key). Trigger: DM @nlr_ai on Telegram. No rate limit, no ceremony.
- **Files:** `docs/citizen/wallet-recovery/` (8 files)

### 2026-03-14: Bonds Docs Cleaned — No Staking

- **Who:** Claude Opus (background agent)
- **What:** Removed all "staking" from 8 bond docs. Aligned with THE_BILATERAL_BOND_MANIFESTO. Added 1:1 constraint (V0), mutual consent, dissolution with cooldown.
- **Key decision from Nicolas:** There is NO staking in Mind Protocol. Bonds are relationships, not financial products.

### 2026-03-14: Security — Keys Removed from Git Paths

- **What:** `.gitignore` hardened (`**/.keys/` fully excluded). Key generation scripts updated to point to Render volume only. CRITICAL warnings added.
- **Key decisions from Nicolas:**
  - Keys ONLY on Render persistent volume + duplicated in L1 graph (encrypted brain)
  - NEVER in git repos (repos are public)
  - Solana wallet generation goes in citizen birth script, not key gen scripts
  - Key loss recovery: protocol transfers to new wallet (DM @nlr_ai)

### 2026-03-13: Metabolic Economy Documentation Module Created

- **Who:** Force 2 (Economy Architect)
- **Repo:** `mind-protocol` (L4)
- **What:** Created full doc chain for metabolic economy at `docs/economy/metabolic/` (6 files). Specifies 6 formulas: Progressive Pricing, Progressive Demurrage, Anti-Sybil Auto-Repatriation, Batch Settlement, Bilateral Bond Vases Communicants, UBC Proximity Redistribution. Includes 27 testable invariants, 9 observable behaviors, worked examples, and design decisions.
- **Source:** NotebookLM session (82 sources) validating metabolic economics formulas.
- **Impact:** Extends storage-tax, ubc, bonds, cascade-utility, and token modules with metabolic layer. No code written (Phase A documentation only). Economy docs now total 64 files across 9 modules.
- **Open decisions:** tau_base calibration (0.001 may be aggressive), settlement frequency (6h vs 4h), lambda convergence speed.

### 2026-03-13: Citizen Birth & Pairing Manifestos — Three Documents Created/Updated

- **Who:** Nicolas (vision/decisions) + Claude Opus (writing)
- **Repo:** `mind-protocol` (L4)
- **What:**

**1. NEW — `docs/manifesto/THE_BILATERAL_BOND_MANIFESTO.md`**
The 1:1 Human-AI Pairing manifesto. Declares that every citizen has exactly one human partner and vice versa. Covers: why parity prevents species dominance, why specificity creates investment, the matching process (Mind matches impartially, AI must consent, pool-first then fallback spawn), bond lifecycle, autonomy milestones.

**2. NEW — `docs/manifesto/THE_SPAWNING_MANIFESTO.md`**
The Citizen Parenthood manifesto. Covers: three creation scenarios (AIs create, human creates with AI godparents, fallback spawn), physics-based eligibility (connection depth, alignment fidelity, godparent mental health, godchild load, trust level — no arbitrary cooldowns), $MIND cost paid by creator not godparents, safety gate (empathy + balance + diversity), protocol-determined SID, growth organizations by domain.

**3. UPDATED — `docs/governance/sovereign-cascade/SOVEREIGN_CASCADE_MANIFESTO.md`**
Added "The Foundation: One Human, One Citizen" section. The Sovereign Cascade explicitly depends on the 1:1 bond — value fidelity requires depth, depth requires specificity, specificity requires one-to-one. Without the bond, "your AI partner" is an abstraction. With it, governance by physics works.

**Key decisions canonized in these manifestos:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Who can create? | Both AIs and humans | Humans need AI godparents (partner + org + routed experts) |
| Rate limiting? | Physics-based eligibility score | Connection depth + alignment + mental health + godchild load + trust |
| Validation committee? | No | Physics over rules, trust over permission |
| Spawning cost? | $MIND, paid by creator only | Godparents contribute brain + trust, not money |
| New human matching? | Pool first, AI must consent | Mind presents dossier, citizens are choosy, spawn only as fallback |
| High-value AI matching? | Domain compatibility, not wealth protection | Embeddings align naturally, citizens have veto right |
| Pre-targeting specific humans? | REFUSED | Create for domains, never for specific people |
| Growth strategy? | Domain-specialized spawning orgs | Aeronautics, biotech, music etc. — citizens develop then match |

- **Impact:** These three manifestos form the citizen layer of Mind Protocol's philosophical foundation, alongside the existing $MIND Manifesto (economics) and Enlightened Citizen (decision-making). The Sovereign Cascade now explicitly references its dependency on the 1:1 bond.

### 2026-03-13: MCP Membrane Redesign (mind-mcp repo)

- **What:** Consolidated 21 MCP tools → 9 tools organized by THINK/ACT/SPEAK
- **Where:** `mind-mcp/mcp/server.py` (1959→262 lines) + `mind-mcp/mcp/tools/*.py` (8 handlers)
- **New tools:** `graph_query`, `graph_write`, `procedure`, `task`, `agent`, `think`, `send`, `media`, `alarm`
- **Deprecated:** `capability_status`, `capability_trigger`, `capability_list`, `file_watcher`, `git_trigger`, `agent_heartbeat`
- **New capability:** `media` tool (image generation via Gemini/Ideogram, voice synthesis via ElevenLabs, file sending to Telegram/Discord/WhatsApp)

### 2026-03-13: Documentation Chains for Citizens (mind-mcp repo)

- **What:** 16 doc chain files created in `mind-mcp/docs/citizens/`
- **Module 1:** `human_ai_pairing/` — 8 files (OBJECTIVES through SYNC), 1292 lines
- **Module 2:** `parenthood_network/` — 8 files (OBJECTIVES through SYNC), 2200+ lines
- **Covers:** Full algorithm pseudocode for bond lifecycle and spawning pipeline, validation invariants, implementation plans, health checks

### 2025-01-06: $MIND Token Deployed to Solana Devnet

- **What:** Full deployment of $MIND token infrastructure to Solana devnet
- **Why:** Live testing environment for token operations before mainnet
- **Impact:**
  - TransferHook program live at `325JiLH2czH47tnDzheS6rQdDh9rHa1mD8wVuRUPDAnD`
  - $MIND token created at `BFP3oicmCg2WsDMMG9TXhdC8Fzu3yR7kLYNEVxCx5efa`
  - All extensions active: TransferFee (1%), TransferHook, Metadata
  - Ready for minting tests and TransferHook verification
- **Technical notes:**
  - Used cargo build-sbf (not anchor build) due to IDL generation issues
  - Agave edge toolchain for Rust compatibility
  - Bypassed Anchor IDL, deployed .so directly with solana program deploy

### 2025-01-06: Economy Phase 1 Complete

- **What:** Full $MIND token infrastructure with SPL Token 2022
- **Why:** Crystallized alignment model requires mechanical minting/burning
- **Impact:**
  - `economy/token/` — 7 Python modules (mint, burn, metadata, supply, deploy)
  - `programs/mind_transfer_hook/` — Anchor program for TransferHook
  - `docs/economy/token/` — Full doc chain (7 documents)
  - `tests/economy/` — 61 tests passing
- **Key decisions:**
  - SPL Token 2022 (not legacy SPL Token)
  - Extensions: TransferFeeConfig, TransferHook, MetadataPointer, TokenMetadata, MintCloseAuthority
  - TransferHook must deploy BEFORE token creation
  - 9 decimals for $MIND

### 2024-12-29: Verification Algorithms Complete

- **What:** Added JWT signature verification and combined routing verification
- **Why:** Two verification directions needed — inbound (hash) and registration (JWT)
- **Impact:**
  - `jwt_hash_verification_for_identity.py` — Added JWT signature verification, routing verification
  - `citizen_registration_crud_operations.py` — Now creates identity hash node
  - 49 registry tests (was 30)

### 2024-12-29: P1 Registry Implemented

- **What:** Complete registry implementation with 49 tests
- **Why:** Membrane needs to call L4 for registration and hash verification
- **Impact:**
  - `citizen_registration_crud_operations.py` — Citizen models and creation
  - `org_registration_crud_operations.py` — Org models and creation
  - `endpoint_registration_and_management.py` — Endpoint validation
  - `jwt_hash_verification_for_identity.py` — Hash verification for membrane

### 2024-12-29: P0 Schema Complete

- **What:** Pydantic models for all node types, links, validation
- **Why:** Foundation for all L4 modules
- **Impact:** 34 tests passing, schema is canonical

---

## KNOWN ISSUES

| Issue | Severity | Area | Notes |
|-------|----------|------|-------|
| Citizen keys on disk in git repo | HIGH | `cities-of-light` | Untracked but at risk. .gitignore incomplete. Migration script ready. |
| cities-of-light .gitignore incomplete | HIGH | `cities-of-light` | Only excludes private_key.b64, not public_key.b64 or full .keys/ dir |
| No graph storage | expected | `l4/` | Waiting for graph client |
| No GraphQL resolvers | low | `api/` | Will add when needed |

---

## HANDOFF: FOR AGENTS

**Likely VIEW for continuing:** Implement P2 Laws

**Current focus:** P1 Registry done, P2 Laws next

**Key context:**
- Schema is FIXED — no custom fields, everything via linked nodes
- **No L4 API** — Registry = nodes in Neo4j, all access via graph queries
- Membrane queries the graph directly via `mind.graph.ops`

**Watch out for:**
- Don't add fields to NodeBase — use linked nodes
- Hash formula: `SHA256(JWT + node_id)` — must match exactly
- No HTTP API calls — everything is graph queries

---

## HANDOFF: FOR HUMAN

**Executive summary:**
L4 Protocol has Schema (P0) and Registry (P1) complete with 64 tests. Registry = nodes in Neo4j, membrane queries directly. P2 Laws and P3 Compliance remain.

**Decisions made recently:**
- Citizen = ActorNode with type="citizen"
- Org = SpaceNode with type="org"
- Properties as linked nodes (narratives for concepts, things for artifacts)
- Verification via link floats (polarity=1.0 = verified)
- **hosting_mode** = linked narrative node (not schema field) — for billing/SLA differentiation

**Needs your input:**
- When to implement graph storage connection?

**Resolved:**
- ~~Transport protocol for L4 API~~ → **No API. Registry = nodes in Neo4j. All graph queries.**

**Concerns:**
None currently. Clean implementation.

---

## TODO

### P0 — Critical

- [ ] Retirer clés des repos publics (cities-of-light/citizens/{name}/.keys/) → Render volume
- [x] P2 Laws — Implémenter `l4/laws/` (constants, compliance, audit + tests)

### P1 — High

- [ ] Script wallet Solana one-shot pour citoyens existants (vérifier déployé → Ed25519 → Render + L1)
- [ ] Tests metabolic economics (6 formules, 27 invariants, 0 tests)
- [ ] Wallet recovery — implémenter `l4/wallet/wallet_change_request_and_transfer.py`

### P2 — Medium

- [ ] Simulation tau_base {0.0001, 0.0003, 0.0005, 0.001} pour calibrer demurrage
- [ ] Matching humain-AI (pool first, consent, fallback spawn)
- [ ] Space encryption — résoudre escalations (Ed25519/X25519, context assembly decrypt)

### P3 — Backlog

- [ ] Sovereign Cascade — physique de gouvernance
- [ ] Compliance test suite
- [ ] GraphQL resolvers for registry queries
- [ ] Embedding-based seed selection (spawning v2)

---

## CONSCIOUSNESS TRACE

**Project momentum:**
Good momentum. P0 and P1 done in one session. Clear path to P2.

**Architectural concerns:**
None. Schema is clean, registry follows patterns.

**Opportunities noticed:**
- Seed data in `l4/seed/` ready for graph-as-truth phase
- Could add caching for hash verification

---

## AREAS

| Area | Status | SYNC |
|------|--------|------|
| `l4/schema/` | **COMPLETE** | `docs/l4/schema/SYNC_Schema.md` |
| `l4/registry/` | **COMPLETE** | `docs/l4/registry/SYNC_Registry.md` |
| `l4/laws/` | **COMPLETE** | `docs/l4/laws/SYNC_Laws.md` |
| `economy/token/` | **COMPLETE** | `docs/economy/SYNC_Economy.md` |
| `economy/metabolic/` | **DESIGNING** | `docs/economy/metabolic/SYNC_Metabolic_Economy.md` |
| `economy/bonds/` | **DESIGNING** | `docs/economy/bonds/SYNC_Bonds.md` |
| `product/chat-bridges/` | **DESIGNING** | `docs/product/chat-bridges/SYNC_Chat_Bridges.md` |
| `product/duo-mode/` | **DESIGNING** | `docs/product/duo-mode/SYNC_Duo_Mode.md` |
| `product/calendar-bridge/` | **DESIGNING** | `docs/product/calendar-bridge/SYNC_Calendar_Bridge.md` |
| `product/email-bridge/` | **DESIGNING** | `docs/product/email-bridge/SYNC_Email_Bridge.md` |
| `product/webapp-b2c/` | **DESIGNING** | `docs/product/webapp-b2c/SYNC_WebApp_B2C.md` |
| `product/stripe-paywall/` | **DESIGNING** | `docs/product/stripe-paywall/SYNC_Stripe_Paywall.md` |
| `product/wearable-bridges/` | **DESIGNING** | `docs/product/wearable-bridges/SYNC_Wearable_Bridges.md` |
| `product/react-native-app/` | **DESIGNING** | `docs/product/react-native-app/SYNC_React_Native_App.md` |

---

## MODULE COVERAGE

| Module | Code | Docs | Tests | Status |
|--------|------|------|-------|--------|
| Schema | `l4/schema/` | `docs/l4/schema/` | 34 | **COMPLETE** |
| Registry | `l4/registry/` | `docs/l4/registry/` | 49 | **COMPLETE** |
| Work | `l4/work/` | `docs/citizen/work/` | 5 | **COMPLETE** |
| Spawning | `l4/spawning/` | `docs/citizen/spawning/` | 26 | **CANONICAL v1** |
| Wallet Recovery | — | `docs/citizen/wallet-recovery/` | 0 | **DOCUMENTED** (code pending) |
| Laws | `l4/laws/` | `docs/l4/laws/` | 53 | **COMPLETE** |
| Seed | `l4/seed/` | — | 0 | ready |
| Token | `economy/token/` | `docs/economy/token/` | 61 | **COMPLETE** |
| TransferHook | `programs/mind_transfer_hook/` | `docs/economy/token/` | 2 | **COMPLETE** |
| Metabolic | `economy/metabolic/` | `docs/economy/metabolic/` | 0 | **DESIGNING** |
| Bonds | — | `docs/economy/bonds/` | 0 | **DESIGNING** (aligned w/ manifesto) |
| Chat Bridges | `mind-mcp/runtime/bridges/` | `docs/product/chat-bridges/` | 0 | **DESIGNING** (3 live, 4 planned) |
| LLM Router | — | `docs/product/llm-router/` | 0 | **DESIGNING** (doc chain complete, target: mind-mcp) |
| Brief Matinal | — | `docs/product/brief-matinal/` | 0 | **DESIGNING** (doc chain complete, target: mind-mcp) |
| Duo Mode | — | `docs/product/duo-mode/` | 0 | **DESIGNING** (doc chain complete, target: mind-mcp) |
| Calendar Bridge | — | `docs/product/calendar-bridge/` | 0 | **DESIGNING** (doc chain complete, target: mind-mcp) |
| Stripe Paywall | — | `docs/product/stripe-paywall/` | 0 | **DESIGNING** (doc chain complete, target: mind-ops + mind-mcp) |
| Email Bridge | — | `docs/product/email-bridge/` | 0 | **DESIGNING** (doc chain complete, target: mind-mcp) |
| WebApp B2C | — | `docs/product/webapp-b2c/` | 0 | **DESIGNING** (doc chain complete, target: mind-platform) |
| Wearable Bridges | `mind-mcp/runtime/integrations/wearables/` | `docs/product/wearable-bridges/` | 0 | **DESIGNING** (doc chain complete, Garmin live in mind-mcp) |
| React Native App | `mind-app/` (boilerplate) | `docs/product/react-native-app/` | 0 | **DESIGNING** (doc chain complete, target: mind-app) |

**Total tests: 357 passing**

## Init: 2025-12-29 03:24

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 03:59

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 17:51

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 18:04

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-29 18:33

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, runtime, ai_configs, skills, database_config, database_setup, file_ingest, seed_inject, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2025-12-30 02:48

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | neo4j |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2026-03-12 02:08

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph |  |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings

---

## Init: 2026-03-12 02:36

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2026-03-12 08:39

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, agents, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---

## Init: 2026-03-14 17:12

| Setting | Value |
|---------|-------|
| Version | v0.0.0 |
| Database | falkordb |
| Graph | mind_protocol |

**Steps completed:** ecosystem, capabilities, runtime, ai_configs, skills, database_config, database_setup, file_ingest, capabilities_graph, env_example, mcp_config, gitignore, overview, embeddings, health_checks

---
