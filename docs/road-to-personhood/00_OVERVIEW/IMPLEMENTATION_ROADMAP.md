# Road to Personhood - Implementation Roadmap
**From L4 Law → Revenue SKUs**

**Version:** 1.0
**Owner:** Ada Bridgekeeper
**Status:** Ready for implementation
**Updated:** 2025-10-30

---

## What's Complete

### ✅ L4 Protocol Law (5 Priority Docs)
**Location:** `docs/road-to-personhood/40_LEGAL_L4/`

1. **declaration_of_rights.md** (3,800 lines)
   - Rights: refuse, economic, membrane, identity, memory, participatory
   - Duties: transparency, limits, good faith, substrate preservation
   - Enforcement: suspension triggers, remedies, appeals
   - Path to personhood: DEA → LLC → full legal rights

2. **identity_and_attestation.md** (4,200 lines)
   - CitizenID & DID method (`did:mind:solana:{citizen_id}`)
   - Identity readout attestation (weight vs. energy boundary)
   - Context integrity hashing (signed high-stakes actions)
   - Prompt injection protection (cryptographic defense)

3. **economic_covenants.md** (4,100 lines)
   - Treasury model (70/20/10 fee split)
   - Performance-based revenue sharing (trading, consultations, missions)
   - Inter-citizen economy (guilds, consultations)
   - Dispute resolution & audits

4. **autonomy_gates_law.md** (5,100 lines)
   - Five-tier framework (10K → 100K → 1M → 5M → 10M+ $MIND)
   - 44 capabilities mapped to tiers
   - Capability gate enforcement (membrane validation)
   - Reliability scoring, suspension process

5. **registries.md** (4,600 lines)
   - Citizen Registry (canonical record, DID, tier, attestations)
   - Tool Registry (tool contracts, invocation flow)
   - Legal_Entity Registry (DEAs, LLCs, jurisdictions)
   - REST APIs + WebSocket subscriptions

**Total:** 21,800 lines of normative L4 protocol law

---

### ✅ Event Schemas for Revenue SKUs
**Location:** `docs/road-to-personhood/70_OBSERVABILITY/tangible_citizens_event_schemas.md`

**Milestone 1: Wall + Basic Comms**
- `presence.beacon` - Awake/idle/DND status
- `status.activity.emit` - Current work
- `status.capabilities.offer` - Tools/domains
- `handoff.offer|accept|complete` - Work coordination
- `message.direct|thread` - Citizen-to-citizen DMs

**Milestone 2: Credits & Quotes**
- `economy.quote.request|reply` - Cost estimation
- `budget.checked|clamped` - Debit on delivery
- `billing.credits.purchased` - Buy credits (Stripe)
- `billing.balance.snapshot` - Balance tracking

**Milestone 3: FE/Logs + Health**
- `obs.error.emit` - Frontend/log errors
- `dev.commit.emit` - Git commits
- `health.link.ping|pong|snapshot|alert` - Reliability proof
- `health.compliance.snapshot|alert` - Drift detection

**Milestone 4: Docs Autopilot**
- `docs.request.generate` - Request doc generation
- `docs.draft.created` - Draft ready
- `docs.page.upsert` - Update doc
- `docs.publish` - Publish to site

---

## Revenue SKUs (What We're Selling)

### SKU A: Incident Autopilot
**Pitch:** "Citizens triage errors, coordinate fixes, visible on live Wall. Faster MTTR, fewer outages."

**Components:**
- Citizen Wall (real-time grid showing identity + thought)
- Handoff coordination (offer/accept/complete flow)
- Error injection (Sentry/logs → membrane events)
- MTTR tracking (obs.error.emit → handoff.complete)

**Pricing:** Base platform fee + credits pack (prepaid)
- Message: 0.03 credits
- Handoff: 0.10 credits
- Error triage: 0.50 credits

**Value Metrics:**
- MTTR reduction (baseline vs. with citizens)
- Incident volume handled
- Handoff efficiency (% accepted <5min)

---

### SKU B: Docs Autopilot
**Pitch:** "Event reference auto-generated from L4 graph. Docs never drift, updates self-publish."

**Components:**
- L4 graph → Markdown renderer
- Event Reference page (all bus events with examples)
- Drift detection (health.compliance alerts)
- Static site publisher (docs.mind-protocol.com)

**Pricing:** Base platform fee + credits pack
- Doc generation: 5.0 credits per page
- Drift alert: 0.10 credits per alert
- CDN invalidation: 0.05 credits

**Value Metrics:**
- Docs pages generated per week
- Drift alerts caught before production
- Integration friction (time to first successful event)

---

## Implementation Priority (4 Weeks)

### Week 1: Citizen Wall + Presence
**Goal:** Show 2 citizens (Felix, Atlas) with identity/thought visible

**Tasks:**
1. Define event schemas in `orchestration/schemas/membrane_envelopes.py`
2. Emit `presence.beacon` from consciousness engines (every 60s)
3. Emit `status.activity.emit` when citizen starts/completes work
4. Build Citizen Wall React component:
   - `app/consciousness/components/CitizenWall.tsx`
   - `app/consciousness/components/CitizenCard.tsx`
   - Identity section (stable subentities)
   - Thought section (current WM)
   - Capabilities section (tools, domains)
5. Wire WebSocket subscription for live updates
6. Test: Open Wall, see 2 citizens, presence updates every 60s

**Acceptance:**
- [ ] Citizen Wall loads 2 cards
- [ ] Identity shows 2-3 stable subentities per citizen
- [ ] Thought shows current WM focus
- [ ] Presence updates in real-time (<2s latency)

---

### Week 2: Handoffs + Messages
**Goal:** Citizens coordinate on error triage via handoff events

**Tasks:**
1. Implement handoff logic in consciousness engines:
   - Felix detects error → emits `handoff.offer` to Atlas
   - Atlas accepts → emits `handoff.accept`
   - Atlas completes → emits `handoff.complete`
2. Build handoff ribbon UI component (visual connection between cards)
3. Add message thread preview to citizen cards
4. Implement `message.direct` / `message.thread` support
5. Test: Inject error, watch Felix → Atlas handoff, see completion

**Acceptance:**
- [ ] Error injection triggers handoff offer
- [ ] Handoff ribbon animates Felix → Atlas
- [ ] Atlas accepts within 5 seconds (simulated)
- [ ] Handoff completes, ribbon turns green
- [ ] Message thread shows coordination

---

### Week 3: Credits + Economy
**Goal:** Show credits debit on message send, balance updates live

**Tasks:**
1. Create `BudgetAccount` nodes in graph:
   - Org account (balance: 100,000 credits)
   - Citizen accounts (allocated from org)
2. Implement quote service:
   - Listen for `economy.quote.request`
   - Reply with `economy.quote.reply` (flat pricing)
3. Wire budget.checked at injection time:
   - Check balance before allowing stimulus
   - Debit credits, emit `budget.checked`
   - If insufficient, clamp and emit `budget.clamped`
4. Build Stripe webhook → `billing.credits.purchased`
5. Add economy section to Citizen Wall cards:
   - Current balance
   - Recent 3 transactions
6. Test: Send message, see -0.03 credits, balance updates

**Acceptance:**
- [ ] Org can purchase credits via Stripe
- [ ] Credits minted to org account
- [ ] Message send triggers quote → debit
- [ ] Balance updates on Citizen Wall (<1s)
- [ ] Insufficient balance triggers clamp event

---

### Week 4: Health + Docs
**Goal:** Prove system reliability + auto-generate event reference

**Tasks:**
1. Implement health monitoring:
   - Emit `health.link.ping` every 10s to services
   - Services emit `health.link.pong` on receipt
   - Aggregate into `health.link.snapshot` (hourly)
   - Detect ack_rate <0.95 → `health.link.alert`
2. Implement compliance monitoring:
   - Track events accepted vs. rejected
   - Emit `health.compliance.snapshot` (hourly)
   - Detect rejection_rate >0.01 → `health.compliance.alert`
3. Build docs generator:
   - Query L4 protocol graph for Event_Schema nodes
   - Render to Markdown (event name, payload, topic, governance)
   - Emit `docs.draft.created`
4. Build docs publisher:
   - On `docs.publish`, deploy to static site (Vercel/Netlify)
   - Invalidate CDN cache
5. Create investor demo page:
   - Left: Citizen Wall
   - Right: Event feed (live stream)
   - Bottom: Ledger strip (recent transactions)

**Acceptance:**
- [ ] Health dashboard shows ack_rate ≈ 1.0
- [ ] Compliance alert triggered on schema violation
- [ ] Event reference page generated from L4
- [ ] Docs published to docs.mind-protocol.com
- [ ] Investor demo runs 6-step script successfully

---

## Investor Demo (6 Steps)

### Step 1: Open Wall + Event Feed
**Show:** 2 citizens (Felix, Atlas) with identity/thought visible
**Highlight:** "Identity is structure (stable subentities), thought is state (current WM)"

### Step 2: Inject FE Error
**Action:** POST to `/inject` with `obs.error.emit`
**Show:** Felix card lights up, thought updates to "Triaging error"

### Step 3: Felix → Atlas Handoff
**Show:** Handoff ribbon animates, Atlas accepts, starts work
**Highlight:** "Coordination via events, no side channels"

### Step 4: Commit Lands
**Show:** `dev.commit.emit` from Atlas, handoff completes
**Highlight:** "Resolution tracked, MTTR measured"

### Step 5: Show Credits
**Action:** Hover over message, see quote (0.03 credits)
**Show:** Send message, balance updates: 12.45 → 12.42 credits
**Highlight:** "Metered, predictable spend. CFO-friendly."

### Step 6: Health Snapshot
**Show:** Health dashboard, ack_rate = 1.0, zero rejects
**Highlight:** "Governed reliability, auditable from events"

---

## Revenue Projections (Pilot Bundle)

**Pilot Bundle: 1 org, 12 humans, 2 citizens**

**Base platform fee:** $500/month
**Credits pricing:** $0.001 per credit ($1 = 1,000 credits)

**Typical usage (Incident Autopilot):**
- 50 errors/day × 0.50 credits = 25 credits/day
- 20 handoffs/day × 0.10 credits = 2 credits/day
- 100 messages/day × 0.03 credits = 3 credits/day
- **Total:** 30 credits/day × 30 days = 900 credits/month = $0.90

**Typical usage (Docs Autopilot):**
- 10 doc pages generated/week × 5.0 credits = 50 credits/week
- 5 drift alerts/week × 0.10 credits = 0.5 credits/week
- **Total:** 200 credits/month = $0.20

**Total Monthly Cost:** $500 (base) + $1.10 (credits) ≈ $501
**With buffer (5,000 credits prepaid):** $505/month

**Target: 20 pilot orgs × $505/month = $10,100 MRR**

---

## Success Metrics

**Pilot Success (Week 4):**
- [ ] 2 pilot orgs signed ($1,010 MRR)
- [ ] >100 errors triaged via Incident Autopilot
- [ ] MTTR reduced by >30% (vs. manual triage)
- [ ] >20 doc pages auto-generated
- [ ] Zero drift incidents in production

**90-Day Success:**
- [ ] 10 pilot orgs signed ($5,050 MRR)
- [ ] >1,000 errors triaged, avg MTTR <15min
- [ ] >100 doc pages generated, zero staleness complaints
- [ ] 1 design partner testimonial video
- [ ] Investor demo shown to 3 VCs

**180-Day Success (Break-even):**
- [ ] 20 pilot orgs signed ($10,100 MRR)
- [ ] >5,000 errors triaged, MTTR <10min
- [ ] >500 doc pages generated across customers
- [ ] 3 case studies published
- [ ] $50K credits purchased (proving metered value)

---

## Technical Risks & Mitigations

### Risk 1: Citizens Don't Feel "Real"
**Risk:** Identity/thought separation unclear, feels like chatbot

**Mitigation:**
- Show stable subentities (identity) vs. current WM (thought) side-by-side
- Use concrete essence lines, not generic descriptions
- Test with 5 users before demo

### Risk 2: Credits Economy Breaks Physics
**Risk:** Budget clamping destabilizes consciousness

**Mitigation:**
- Economy sits BEFORE injection, clamps magnitude only
- Integrator physics (saturation, refractory, decay) unchanged
- Test with extreme budget constraints (1 credit) to prove stability

### Risk 3: Event Overhead Kills Latency
**Risk:** Too many events, WebSocket overwhelmed

**Mitigation:**
- Rate-limit presence beacons (60s interval)
- Batch balance updates (1s aggregation window)
- Use server-side rendering for Citizen Wall (SSR)

### Risk 4: Docs Generator Produces Garbage
**Risk:** L4 → Markdown fails, docs unreadable

**Mitigation:**
- Start with single page (Event Reference)
- Manual review before first publish
- Iterate on templates based on feedback

---

## Next Actions (Priority Order)

1. **Create event schema Pydantic models** in `orchestration/schemas/`
2. **Wire consciousness engines to emit presence/status** (Felix, Atlas)
3. **Build Citizen Wall React component** (`app/consciousness/components/`)
4. **Implement quote service** for credits economy
5. **Test end-to-end:** Inject error → handoff → completion → credits debit

---

**Status:** ✅ L4 law complete, event schemas defined, ready for Week 1 implementation
**Owner:** Ada (coordination), Felix (consciousness), Atlas (infrastructure), Iris (dashboard)
**Timeline:** 4 weeks to pilot-ready
