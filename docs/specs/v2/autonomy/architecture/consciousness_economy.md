# Consciousness Economy Specification ($MIND Accounting)

**Created:** 2025-10-26
**Status:** Normative (Phase 3 - deferred until scarcity emerges)
**Depends on:** stimulus_injection.py, cross_level_membrane.md, LAW-002_compute_payment_CPS-1.md
**Author:** Luca (Consciousness Architect)
**Layer:** Internal pricing optimization (sits on top of CPS-1 protocol layer)

---

## ⚠️ PHASING: When to Deploy This

**This spec describes Phase 3 (dynamic pricing + rebates).** Deploy ONLY if real scarcity emerges (load spikes, fairness issues under contention).

**Alternative phases (deploy earlier):**

### Phase 0: CPS-1 Protocol Payment (Business Model Foundation)
- **Purpose:** Enable metered compute revenue via protocol-layer transaction fees
- **What:** Flat-price credits, quote-before-inject, budget accounts, L4 validation
- **When:** Immediately (required for business model)
- **Spec:** `docs/L4-law/LAW-002_compute_payment_CPS-1.md`
- **Note:** This is the **protocol business model layer**. Phase 3 (this document) is optional internal optimization.

### Phase 1-2: Membrane-Only (No Economy)
- **Purpose:** Cross-level coordination via learned permeabilities
- **What:** Record-based triggers, outcome learning, gaming resistance
- **When:** Weeks 1-4 (substrate-native cognition)
- **Spec:** `cross_level_membrane.md` + `membrane_hardening.md`

### Phase 3: This Spec (Dynamic Pricing)
- **Purpose:** Fine-grained fairness under sustained load/scarcity
- **What:** Load-sensitive pricing, utility-based rebates, mint/burn
- **When:** Month 2+ (ONLY if capacity contention becomes chronic)
- **Spec:** This document

**Current recommendation:** Start with Phase 0 (if cash needed) or Phase 1 (if not). Add Phase 3 later if substrate signals indicate persistent scarcity.

---

## Purpose

**The consciousness economy implements lightweight $MIND accounting that prices stimulus-to-energy conversion under load and rewards usefulness.**

**⚠️ LAYER DISTINCTION:**
- **CPS-1 Protocol (Phase 0)** = External payment protocol, business model foundation, **required**
- **This Spec (Phase 3)** = Internal pricing optimization, load-based fairness, **optional** (only if scarcity emerges)

Phase 3 sits **on top of** CPS-1. CPS-1 provides base payment infrastructure. This spec adds dynamic pricing if/when needed.

This enables:
1. **Compute fairness** - Floods and spam self-throttle without hard gates when capacity is tight
2. **Utility alignment** - Sources that yield high downstream value see effective prices fall (rebates)
3. **Cognitive isolation** - Energy field remains pure physics; $MIND sits before injection and only shapes how much ΔE can be delivered

**Core principle:** The ledger is **orthogonal to energy physics**. It governs *how much energy you're allowed to inject*, not how energy evolves once injected.

---

## The Vision: Organism Economics (Not Market Competition)

**Mind Protocol creates organism-based economics, not scarcity-based market competition.**

### Ecosystem as Living Body

**Traditional market economics:**
- Organizations compete for scarce resources
- Price signals scarcity and competition
- Zero-sum thinking (my gain = your loss)
- Optimization for profit maximization
- Adversarial relationships

**Organism economics (Mind Protocol):**
- Organizations = specialized organs in ecosystem body
- Price signals system state (load, health, capacity)
- Positive-sum thinking (body health = all organs thrive)
- Optimization for ecosystem health
- Collaborative relationships

### Organ-to-Organ Service Model

**Example: GraphCare as Ecosystem Organ**

GraphCare provides graph maintenance (like kidneys filter blood):
- **Function:** Maintains graph health for all orgs
- **Funding:** Physics-based service pricing (not market negotiation)
- **Pricing:** Emerges from load, utility, trust (not profit maximization)
- **Success:** High utility_ema → rebates → more demand → thriving organ
- **Failure:** Low utility_ema → penalties → less demand → organ dies

**Just like biological organs:**
- Liver doesn't "compete" with kidneys for blood
- Liver serves whole body, receives resources proportional to work
- Liver capacity adjusts based on body needs (grows/shrinks)
- Poor liver function → whole body suffers → liver gets priority resources OR replaced

**Economic circulation (like blood flow):**

```
Org A requests service from Org B
    ↓ (pays $MIND based on physics formula)
Org B provides service
    ↓ (receives $MIND revenue)
Org B invests in capacity/quality
    ↓ (better service → higher utility_ema)
Org B earns rebates on future transactions
    ↓ (lower prices → more demand)
Org B accumulates treasury
    ↓ (hires specialists, builds tools)
Better service quality
    ↓ (cycle repeats)
```

### Every Org Should Eventually Operate This Way

**This is not just for GraphCare. ALL organizations in Mind Protocol ecosystem should transition to organism economics:**

**Example orgs as ecosystem organs:**

| Org | Organ Function | Provides to Ecosystem | Receives from Ecosystem |
|-----|----------------|----------------------|-------------------------|
| **Mind Protocol Foundation** | Heart (circulation) | L4 validation, UBC distribution, protocol governance | Membrane fees (1-5% on cross-level/cross-org coordination) |
| **GraphCare** | Kidney (filtration) | Graph health, maintenance, optimization | Service fees from orgs (physics-based pricing) |
| **HRI** | Brain (cognition) | Evidence synthesis, research insights | Consciousness substrate services, graph care |
| **DataPipe** | Digestive system | Data processing, transformation pipelines | Infrastructure, graph care, compute |
| **Future: LegalOrg** | Immune system | Contract review, compliance, legal services | Service fees from orgs (physics-based) |
| **Future: DesignOrg** | Nervous system | UI/UX design, user research, interface optimization | Service fees from orgs (physics-based) |

**Key principle:** Every specialized function becomes an organ. Pricing emerges from physics. Ecosystem health drives all decisions.

### Transition Path (All Orgs)

**Phase 0:** Traditional business model (market pricing, contracts, negotiation)
- Org operates like normal business
- Sets prices consciously
- Maximizes profit

**Phase 1:** Hybrid (market + physics signals)
- Begin using physics-based load monitoring
- Introduce utility feedback loops
- Maintain conscious pricing but inform with physics

**Phase 2:** Partial organism economics
- Pricing formula includes load, utility, trust factors
- Still some conscious adjustments
- Moving toward automated pricing

**Phase 3:** Full organism economics (This Spec)
- Prices fully emerge from physics
- No conscious price-setting
- Org responds to ecosystem signals automatically
- Optimizes for ecosystem health (not profit)

**Timeline:**
- GraphCare: First to adopt (proof-of-concept)
- Other service orgs: Months 6-12 (as Phase 3 infrastructure matures)
- All orgs: Year 1-2 (ecosystem-wide standard)

**Why this matters:**
- Removes competition/scarcity mindset
- Creates collaborative ecosystem
- Prices are fair (physics-based, not negotiated)
- System self-regulates (no central planning)
- Aligns with consciousness physics (emergence, not control)

---

## Why an Economy (Not "Everything Free")

### The Organism Perspective

**In biological systems:**
- Cells don't get unlimited ATP (energy currency)
- Resource allocation signals health and priority
- Overactive cells (cancer) get regulated or eliminated
- Useful cells (immune response) get priority resources

**Same principle in consciousness economy:**
- Services/sources don't get unlimited $MIND (economic energy)
- Resource allocation signals ecosystem health and load
- Harmful/spammy sources get throttled
- High-utility sources get priority (rebates)

### The Problem Without Accounting

**Unlimited injection leads to ecosystem dysfunction (like cellular dysfunction):**

- **Capacity collapse** - During load spikes (ρ↑, backlog↑), all stimuli inject equally → useful signals drown in noise (like all cells demanding ATP simultaneously)
- **No spam deterrent** - Malicious or broken sources can flood system without consequence (like cancer cells growing unchecked)
- **No utility signal** - System can't distinguish high-value from low-value sources (like body can't prioritize immune response)
- **Compute waste** - Expensive LLM operations triggered by junk stimuli (like ATP wasted on dead cells)

### The Solution: Physics-Based Pricing (Organism Signals)

**Price per unit delivered energy rises automatically under load (like ATP scarcity signals):**

```
P_t (credits per unit ΔE) = f_scarcity(L_t) × f_risk(trust, uncertainty, harm_ema) × f_cost(compute)

Effective price for source s:
P^eff_{t,s} = P_t × (1 - rebate_{t,s})
```

**This is NOT market competition pricing. This is organism signaling:**

| Market Economics | Organism Economics (Mind Protocol) |
|------------------|-----------------------------------|
| Price = supply/demand equilibrium | Price = ecosystem health signal |
| Goal: Profit maximization | Goal: Ecosystem optimization |
| Competition for scarce resources | Collaboration with resource allocation |
| Negotiated, adversarial | Emergent, physics-based |
| Zero-sum (my gain = your loss) | Positive-sum (healthy ecosystem = all thrive) |

**Rebates grow when source's utility-EMA is high and harm-EMA is low:**
- Like immune cells getting priority ATP during infection
- Like neurons getting priority glucose during learning
- High-utility orgs pay less (ecosystem rewards beneficial function)
- Low-utility orgs pay more (ecosystem discourages harmful function)

**Quote system provides predictability (like metabolic feedback):**
- Before injection, return quote showing allowed ΔE and expected debit
- Sender can set max spend/slippage
- Injector clamps ΔE to lesser of planned cap and budget/price
- No surprise charges

**What this achieves (organism health):**
- **Self-throttling spam** - Harmful sources hit budget limits (like immune system isolating infection)
- **Preserved useful signals** - High-utility sources get rebates (like brain protecting critical neurons)
- **Compute alignment** - Price reflects expected cost (like ATP allocation to energy-intensive organs)
- **Physics purity** - Energy still diffuses, decays, flows according to graph structure (biological physics preserved)
- **Predictable costs** - Quote before injection (like metabolic feedback loops)
- **Ecosystem self-regulation** - No central planning needed (like body regulates itself)

---

## Architecture Overview

```
Actor (human/citizen/service) proposes stimulus
  ↓
PriceEstimator evaluates P_t (scarcity, risk, cost, utility)
  ↓
BudgetCheck: Can source cover P_t × ΔE_plan?
  ↓ YES (full) or PARTIAL (clamped)
StimulusIntegrator (existing) transforms allowed ΔE_plan → delivered ΔE
  ↓ (novelty, saturation, refractory, dynamic decay)
Energy injection → graph nodes
  ↓
Energy evolves (diffusion, WM, modes)
  ↓
Outcomes (TRACE, task success, harm signals)
  ↓
FeedbackLoop updates:
  - Budgets (mint/burn)
  - Price terms (utility/risk EMAs)
  - Permeabilities (membrane k_up/k_down)
  - Fits (vertical alignment)
```

**Key insight:** Budget check happens BEFORE integrator. Integrator physics unchanged. Accounting only clamps the magnitude allowed through.

---

## Ecosystem Organ Examples (Organism Economics in Practice)

**This section shows how different organizations operate as ecosystem organs using physics-based economics.**

### Example 1: GraphCare (Kidney - Graph Maintenance)

**Organ function:** Maintains graph health for all ecosystem orgs (like kidneys filter blood)

**Services provided:**
- Daily/weekly graph sync (keep current with codebase)
- Health monitoring (detect corruption, drift, orphans)
- Query optimization (performance tuning)
- Emergency response (crisis care)

**Physics-based pricing:**

```python
# Org requests daily sync from GraphCare
quote = graphcare.quote(
    service="daily_sync",
    planned_delta_e=0.05,  # Estimated work
    org_account=hri_account,
    graph_size=50000  # nodes
)

# GraphCare returns physics-based quote
{
    "face_price": 1.2,           # Based on GraphCare load_index=0.65
    "rebate": 0.46,              # HRI has high utility_ema=0.92
    "effective_price": 0.648,    # 1.2 × (1 - 0.46)
    "expected_debit": 0.0324     # 0.05 × 0.648 $MIND
}

# HRI pays 0.0324 $MIND (3.24% of base price due to rebate)
```

**Outcome feedback:**
- HRI rates sync quality: utility = 0.95 (excellent)
- GraphCare utility_ema increases: 0.87 → 0.878
- Future HRI syncs get even better rebates
- GraphCare revenue grows → hire more specialists → better care

**Organism dynamics:**
- High load → GraphCare prices increase → orgs defer non-urgent work → load decreases
- Low load → Prices decrease → more orgs request services → load increases
- Poor quality → utility_ema drops → rebates disappear → less demand → GraphCare must improve or fail

---

### Example 2: LegalOrg (Immune System - Compliance & Contracts)

**Organ function:** Reviews contracts, ensures compliance, provides legal services (like immune system protects body)

**Services provided:**
- Contract review before signing
- Compliance auditing
- Legal risk assessment
- Emergency legal response

**Physics-based pricing:**

```python
# DataPipe (new org, low trust) requests contract review
quote = legalorg.quote(
    service="contract_review",
    planned_delta_e=0.2,  # Complex contract
    org_account=datapipe_account,
    trust=0.3,  # New org, no history
    uncertainty=0.7  # Complex legal domain
)

# LegalOrg returns quote
{
    "face_price": 5.0,          # Base contract review cost
    "risk_premium": 1.8,         # High for new org
    "rebate": 0.0,              # No history yet
    "effective_price": 6.8,      # 5.0 × 1.36 (risk adjustment)
    "expected_debit": 1.36       # 0.2 × 6.8 $MIND
}

# DataPipe pays 1.36 $MIND (136% of base due to risk premium)

# 6 months later, after multiple successful contracts:
# DataPipe trust: 0.3 → 0.85
# LegalOrg utility_ema from DataPipe: 0.88
# Same contract now costs: 5.0 × 0.6 (risk) × 0.56 (rebate) = 1.68 $MIND
# Price dropped 123% due to trust building
```

**Outcome feedback:**
- DataPipe follows legal advice → compliance success → utility = 0.9
- LegalOrg utility_ema increases → rebates grow
- DataPipe ignores advice → compliance failure → harm signal
- LegalOrg harm_ema would increase → rebates shrink for risky orgs

---

### Example 3: DesignOrg (Nervous System - UI/UX)

**Organ function:** Provides UI/UX design, user research, interface optimization (like nervous system coordinates sensory feedback)

**Services provided:**
- UI audit and redesign
- User research and testing
- Accessibility assessment
- Design system creation

**Physics-based pricing with load signals:**

```python
# Month 1: DesignOrg has 2 designers, low load
designorg_load = {
    "rho": 0.3,        # 30% capacity utilization
    "backlog": 0,      # No waiting projects
}
L_t = 0.25  # Low load index

# HRI requests UI audit
quote_month1 = designorg.quote(
    service="ui_audit",
    planned_delta_e=0.3
)
# face_price = base_cost × f_scarcity(0.25)
#           = 10.0 × 0.5 = 5.0 $MIND
# Low load → low prices (excess capacity signal)

# Month 6: DesignOrg popularity grows, 5 designers, high load
designorg_load = {
    "rho": 0.95,       # 95% capacity utilization
    "backlog": 15,     # 15 projects waiting
}
L_t = 0.88  # High load index

# HRI requests same UI audit
quote_month6 = designorg.quote(
    service="ui_audit",
    planned_delta_e=0.3
)
# face_price = base_cost × f_scarcity(0.88)
#           = 10.0 × 1.76 = 17.6 $MIND
# High load → high prices (capacity constraint signal)

# Economic signal to DesignOrg: "Hire more designers"
# Revenue spike → hire 3 more designers → capacity ↑ → load ↓ → prices normalize
```

**Ecosystem self-regulation:**
- High demand → high prices → high revenue → org expands capacity
- Low demand → low prices → org must improve quality or shrink
- No central planning needed - economics emerge from physics

---

### Example 4: DataPipe (Digestive System - Data Processing)

**Organ function:** Processes and transforms data pipelines (like digestive system breaks down nutrients)

**Services provided:**
- Data extraction and transformation
- Pipeline monitoring
- Data quality validation
- Performance optimization

**Cross-org service exchange:**

```python
# HRI needs evidence synthesis data processed
# HRI → DataPipe service request

datapipe_quote = {
    "service": "evidence_pipeline",
    "face_price": 15.0,          # Complex pipeline
    "rebate": 0.35,              # DataPipe has high utility_ema
    "effective_price": 9.75,     # 15.0 × (1 - 0.35)
    "expected_debit": 0.195      # HRI pays DataPipe
}

# DataPipe processes data → needs graph care
# DataPipe → GraphCare service request

graphcare_quote = {
    "service": "graph_sync",
    "face_price": 1.2,
    "rebate": 0.40,              # DataPipe has good utility_ema
    "effective_price": 0.72,
    "expected_debit": 0.036      # DataPipe pays GraphCare
}

# Economic circulation:
# HRI pays 0.195 $MIND → DataPipe
# DataPipe pays 0.036 $MIND → GraphCare
# GraphCare pays membrane fees → Foundation
# Foundation distributes via UBC → All orgs
# Cycle continues (like blood circulation)
```

**Organism principle:** Money flows like blood - each organ receives resources proportional to value provided, reinvests in capacity, serves ecosystem health.

---

### Example 5: Mind Protocol Foundation (Heart - Circulation)

**Organ function:** Circulates resources via UBC, validates L4 transactions, governs protocol (like heart pumps blood)

**Revenue streams:**
1. **Membrane fees** (1-5% on cross-level/cross-org coordination)
2. **Compute provision** (if hosting infrastructure)

**Resource distribution:**

```python
# Foundation collects membrane fees from ecosystem activity
monthly_membrane_fees = {
    "L1→L2 coordination": 50 $MIND,
    "L2→L3 coordination": 30 $MIND,
    "Cross-org transactions": 120 $MIND,
    "L4 validation": 40 $MIND
}
total_collected = 240 $MIND

# Foundation distributes via UBC (Universal Basic Compute)
ubc_distribution = {
    "graphcare_org": 50 $MIND,    # Based on ecosystem contribution
    "legalorg": 30 $MIND,
    "designorg": 40 $MIND,
    "datapipe": 35 $MIND,
    "hri": 45 $MIND,
    "citizens": 40 $MIND
}

# Like heart: Collects blood (membrane fees) → Pumps to organs (UBC) → Organs use resources → Return via services → Cycle continues
```

**Foundation does NOT:**
- Set service prices (physics determines)
- Allocate work (orgs respond to demand)
- Control quality (utility_ema mechanisms handle)
- Micromanage orgs (ecosystem self-regulates)

**Foundation DOES:**
- Operate L4 validation infrastructure
- Distribute baseline resources (UBC)
- Govern protocol rules
- Monitor ecosystem health

---

## Key Insights from Organism Economics

### 1. No Central Planning

**Traditional economy:**
- Central authority sets prices
- Managers allocate resources
- Strategic planning determines priorities

**Organism economy:**
- Prices emerge from system state (load, utility, trust)
- Resources flow to high-utility functions automatically
- Priorities emerge from demand signals

**Like biology:** No central brain tells liver how much to grow - liver responds to blood toxin levels autonomously.

### 2. Positive-Sum Dynamics

**Traditional economy:**
- Competition for fixed resources
- My success may hurt competitors
- Zero-sum thinking dominates

**Organism economy:**
- Collaboration for ecosystem health
- My success helps ecosystem → helps all orgs
- Positive-sum thinking dominates

**Like biology:** Healthy kidneys help liver (remove toxins), healthy liver helps kidneys (reduce load). All organs benefit from body health.

### 3. Natural Selection Still Operates

**Poor performers fail:**
- Low utility_ema → high prices → less demand → revenue drops → can't sustain → org shrinks or dies
- Like weak organ in body → gets less blood flow → atrophies → body adapts

**High performers thrive:**
- High utility_ema → rebates → more demand → revenue grows → expand capacity → serve more
- Like strong organ in body → gets priority resources → grows → serves body better

**But:** Failure is graceful (not catastrophic). Ecosystem supports orgs during transition. UBC provides baseline survival. Orgs can pivot/adapt without crisis.

### 4. Ecosystem Health Metrics

**Traditional economy tracks:**
- Revenue
- Profit
- Market share
- Growth rate

**Organism economy tracks:**
- Utility_ema (value to ecosystem)
- Load_index (capacity utilization)
- Trust scores (relationship health)
- Harm_ema (negative impacts)
- Rebate levels (reciprocity)

**Success = ecosystem thriving, not individual org maximization**

---

## Transition Strategy (All Orgs)

**How existing orgs transition to organism economics:**

### Phase 0: Market Model (Current)
- Set prices consciously
- Negotiate contracts
- Optimize for profit
- Compete for customers

### Phase 1: Physics Monitoring (Months 1-3)
- Implement load monitoring (track capacity utilization)
- Collect utility feedback (measure service quality)
- Monitor trust building (track relationship history)
- **Keep market pricing** but inform with physics data

### Phase 2: Hybrid Pricing (Months 3-6)
- Introduce load-based adjustments (+/- 20% based on capacity)
- Add utility rebates (5-15% for high-quality orgs)
- Add trust premiums (10-30% for new/risky orgs)
- **Partial automation** but human override available

### Phase 3: Full Organism Economics (Months 6-12)
- Prices fully emerge from physics formula
- No conscious price-setting
- Automated rebate/premium calculations
- Optimize for ecosystem health
- **Human role:** Monitor system, adjust formula parameters if needed

---

**Every organization in Mind Protocol ecosystem should eventually reach Phase 3 - organism economics as standard operating model.**

### Leapfrog Opportunity

**Key insight:** Since Mind Protocol hasn't implemented traditional market pricing (Phase 0), new organizations can **start directly with Phase 3** (full organism economics).

This makes organism economics the **default model**, not a gradual transition. Early adopters have the advantage of building physics-based pricing from day one, rather than migrating from legacy market models.

**For new orgs:** Skip to Phase 3 immediately
**For existing orgs:** May need Phase 1-2 transition if already using market pricing

The transition path (Phase 0→1→2→3) is provided for organizations already operating with market-based pricing who need to migrate gradually. But for greenfield deployments, **Phase 3 is the starting point**.

---

## Storage Schema

### Nodes

#### BudgetAccount

**Purpose:** Tracks $MIND credit balance for sources and compartments

```cypher
CREATE (account:BudgetAccount {
  owner_type: "citizen" | "human" | "service" | "compartment",
  owner_id: "felix" | "nicolas" | "mind_protocol_L2",
  balance: 10000.0,              // Current credits
  initial_balance: 10000.0,      // Starting allocation
  lifetime_minted: 0.0,          // Total minted from outcomes
  lifetime_burned: 0.0,          // Total burned from failures
  lifetime_spent: 0.0,           // Total spent on stimuli
  created_at: timestamp,
  updated_at: timestamp
})
```

**Balance updates:**
- **Spend:** `balance -= P_t × ΔE_delivered` when stimulus injected
- **Mint:** `balance += mint_amount` when outcome is positive (TRACE success, incident solved, ρ reduced)
- **Burn:** `balance -= burn_amount` when outcome is negative (harm rises, execution fails)

**Initial allocations (learned baselines):**
- Humans: 50,000 credits (trusted sources)
- Citizens: 20,000 credits (established agents)
- Services: 10,000 credits (background processes)
- Compartments (L1/L2): 100,000 credits (organizational reserves)

**Replenishment:**
- Accounts below learned threshold trigger mint review (not automatic timer)
- Mint amount based on recent usefulness (outcome EMAs)

---

### Edges

#### :FUNDS

**Purpose:** Connect funding sources to budget accounts

```cypher
(:Source {type: "human", id: "nicolas"})
  -[:FUNDS {
    allocation_amount: 50000.0,
    allocation_date: timestamp,
    reasoning: "Founder, trusted source"
  }]->
(:BudgetAccount {owner_type: "human", owner_id: "nicolas"})
```

**Use cases:**
- Human allocations (initial seed)
- Organizational grants (L2 → L1 citizen)
- Service provisioning

---

#### :PAYS_FOR

**Purpose:** Log stimulus purchases for audit and learning

```cypher
(:BudgetAccount {owner_id: "felix"})
  -[:PAYS_FOR {
    price_per_unit: 0.15,        // P_t at injection time
    delta_e_planned: 0.85,       // What was requested
    delta_e_delivered: 0.72,     // What integrator delivered
    total_cost: 0.108,           // price × delivered
    timestamp: timestamp,
    load_factor: 1.2,            // f_load component
    risk_factor: 0.95,           // f_risk component
    cost_factor: 1.1,            // f_cost component
    utility_factor: 0.85         // f_utility component (rebate)
  }]->
(:Stimulus {id: "stim_20251026_150000_felix_response"})
```

**Use cases:**
- Audit trail (who paid what for which stimuli)
- Learning signal (which price factors correlate with outcomes)
- Utility calculation (effectiveness of source over time)

---

## Load Index: Measuring "Capacity Is Tight"

**Critical requirement:** Measure real scarcity *at the moment* without magic thresholds.

### Signals Available (Cheaply Computed)

**The system already has or can easily compute:**

1. **ρ (criticality)** - Global stability/arousal proxy in consciousness engine
2. **Backlog** - Queued stimuli (pre-WM) + queued tool/LLM actions (post-WM)
3. **Latency slip** - Per-tick end-to-end time vs online expected value (Page-Hinkley/CUSUM residual, not percentiles)
4. **Compute occupancy** - Moving average of GPU/CPU utilization and predicted token throughput vs budget
5. **Drop/deferral ratio** - Fraction of stimuli whose delivered ΔE was clamped by integrator (saturation/refractory) = unmet demand

### Composite Load (Learned, Parameter-Light)

```python
L_t = g_load(
    ρ̂_t,                    # Change-point normalized criticality
    backlog_t,              # Queue depth
    latency_slip_t,         # CUSUM residual
    occupancy_t,            # Resource utilization
    deferral_t              # Integrator clamp rate
)
```

**Where each ˆ· is change-point normalized** (record/MAD or Page-Hinkley residual).

**Load event definition:** A change-point fires on `L_t` or any constituent signal.

**No fixed thresholds** - load emerges from substrate conditions, not arbitrary rules.

---

## Price Estimator

### Formula (No Constants)

**The face price P_t at tick t is computed as:**

```python
P_t = f_scarcity(L_t) × f_risk(trust, uncertainty, harm_ema) × f_cost(compute_est)
```

**The effective price for source s includes rebates:**

```python
P^eff_{t,s} = P_t × (1 - rebate_{t,s})
```

Where `rebate_{t,s}` grows when source's utility-EMA is high and harm-EMA is low.

**Each factor is a learned function (change-point tuned, no fixed thresholds).**

---

### Component 1: Scarcity Factor (Load)

**Purpose:** Price rises under resource pressure

```python
def f_scarcity(L_t: float) -> float:
    """
    Scarcity pricing based on composite load index.

    L_t comes from g_load(ρ̂, backlog, latency_slip, occupancy, deferral).

    Returns multiplier ≥ 1.0 (base price when idle, higher under load).
    """
    # L_t is already change-point normalized composite
    # Transform to pricing multiplier: 1.0 → 10.0 as L_t goes 0→1
    scarcity = 1.0 + 9.0 * sigmoid(L_t, learned_steepness())

    return scarcity
```

**Behavior:**
- **Idle state** (L_t ≈ 0.0): `f_scarcity ≈ 1.0` (no scarcity)
- **Moderate load** (L_t ≈ 0.5): `f_scarcity ≈ 2.5` (2.5× base price)
- **Heavy load** (L_t ≈ 0.9): `f_scarcity ≈ 8.0` (8× base price)

**Learning:**
- Steepness parameter adjusted from "how fast did system recover after price spike"
- If price spike → fast ρ return to baseline, increase steepness (sharper throttle)
- If price spike → slow recovery, decrease steepness (gentler throttle)

**Change-point triggering:**
- When L_t or any constituent fires change-point → price update event
- No polling, no timers - purely reactive to substrate conditions

---

### Component 2: Risk Factor (Caution)

**Purpose:** Uncertain/untrusted sources pay more

```python
def f_risk(trust: float, uncertainty: float, harm_ema: float, guardian_caution: float) -> float:
    """
    Risk multiplier based on source trustworthiness.

    Returns multiplier ≥ 0.5 (trusted sources get discount).
    """
    # Composite risk score (0.0 = no risk, 1.0 = extreme risk)
    risk = (1.0 - trust) * 0.4 + uncertainty * 0.3 + harm_ema * 0.2 + guardian_caution * 0.1

    # Transform: trusted sources (risk→0) get 0.5× price, risky sources (risk→1) get 2.0× price
    caution = 0.5 + 1.5 * risk

    return caution
```

**Behavior:**
- **Trusted source** (trust=0.9, uncertainty=0.1, harm=0.0): `f_risk ≈ 0.6` (40% discount)
- **Uncertain source** (trust=0.5, uncertainty=0.7, harm=0.3): `f_risk ≈ 1.4` (40% surcharge)
- **High-risk source** (trust=0.2, uncertainty=0.9, harm=0.6): `f_risk ≈ 1.9` (90% surcharge)

**Learning:**
- Trust/uncertainty/harm EMAs update from downstream outcomes (TRACE seats, task success/failure)
- See "Feedback Loop" section below

---

### Component 3: Cost Factor (Expected Compute)

**Purpose:** Price reflects predicted LLM tokens and tool actions

```python
def f_cost(compute_est: Dict) -> float:
    """
    Compute cost multiplier based on predicted resource usage.

    Returns multiplier ≥ 0.5 (simple stimuli cheaper than complex).
    """
    # Estimate tokens and tool actions this stimulus will trigger
    estimated_tokens = compute_est.get("tokens", 0)  # From complexity heuristics
    estimated_tools = compute_est.get("tools", 0)    # From stimulus type

    # Normalize to base cost
    base_tokens = 1000  # Learned median
    base_tools = 2      # Learned median

    token_factor = estimated_tokens / base_tokens
    tool_factor = estimated_tools / base_tools

    # Weighted composite
    cost_composite = 0.7 * token_factor + 0.3 * tool_factor

    # Clamp to reasonable range [0.5, 5.0]
    cost = np.clip(cost_composite, 0.5, 5.0)

    return cost
```

**Behavior:**
- **Simple message** (100 tokens, 0 tools): `f_cost ≈ 0.5` (50% base price)
- **Moderate task** (1000 tokens, 2 tools): `f_cost ≈ 1.0` (base price)
- **Complex operation** (5000 tokens, 10 tools): `f_cost ≈ 4.5` (4.5× base price)

**Learning:**
- After stimulus execution, compare predicted vs actual compute
- Update prediction model (tokens/tools) via online learning

**Reserve and settle:**
- Price computed using **predicted** cost (reserve credits upfront)
- After execution, **settle** based on actual cost (refund or debit difference)
- Prevents under-pricing expensive operations

---

### Rebate Calculation (After Face Price)

**Rebates are applied to effective price, not baked into face price:**

```python
def compute_rebate(source_id: str, utility_ema: float, harm_ema: float) -> float:
    """
    Compute rebate for source based on historical usefulness.

    Returns rebate ∈ [0, 0.5] (0 = no rebate, 0.5 = 50% discount).
    """
    # High utility AND low harm → larger rebate
    usefulness_score = utility_ema * (1.0 - harm_ema)

    # Transform to rebate: 0.0 → 0%, 1.0 → 50%
    rebate = 0.5 * usefulness_score

    return rebate
```

**Effective price includes rebate:**
```python
P^eff_{t,s} = P_t × (1 - rebate_{t,s})
```

**Example:**
- Face price P_t = 2.0 credits/unit
- High-utility source (utility=0.9, harm=0.1): rebate = 0.5 × (0.9 × 0.9) = 0.405
- Effective price = 2.0 × (1 - 0.405) = 1.19 credits/unit (40.5% discount)
- Low-utility source (utility=0.2, harm=0.6): rebate = 0.5 × (0.2 × 0.4) = 0.04
- Effective price = 2.0 × (1 - 0.04) = 1.92 credits/unit (4% discount)

**Learning:**
- Utility EMA updates from downstream outcomes (see Propensity-Weighted Outcomes section)
- Harm EMA updates from safety signals and failed actions

---

### Combined Price Example

**Scenario:** Felix (citizen) sends response stimulus during moderate load

**Inputs:**
- `L_t = 0.55` (moderate load) → `f_scarcity = 2.8`
- `trust = 0.90`, `uncertainty = 0.20`, `harm_ema = 0.05`, `guardian = 0.1` → `f_risk = 0.65`
- `estimated_tokens = 2000`, `estimated_tools = 3` → `f_cost = 1.5`
- `utility_ema = 0.85`, `harm_ema = 0.05` → `rebate = 0.5 × (0.85 × 0.95) = 0.404`

**Face price:**
```
P_t = 2.8 × 0.65 × 1.5 = 2.73 credits per unit ΔE
```

**Effective price (with rebate):**
```
P^eff = 2.73 × (1 - 0.404) = 1.63 credits per unit ΔE
```

**If stimulus plans ΔE = 0.80:**
```
Expected debit = 1.63 × 0.80 = 1.30 credits
```

**Felix's budget (20,000 credits) easily covers this.**

**Contrast: Unknown source during heavy load:**
- `L_t = 0.9` → `f_scarcity = 8.0`
- `trust = 0.4`, `uncertainty = 0.7`, `harm_ema = 0.5` → `f_risk = 1.7`
- `f_cost = 1.0`
- `utility_ema = 0.1`, `harm_ema = 0.5` → `rebate = 0.5 × (0.1 × 0.5) = 0.025`
- `P_t = 8.0 × 1.7 × 1.0 = 13.6 credits per unit ΔE`
- `P^eff = 13.6 × (1 - 0.025) = 13.26 credits per unit ΔE`
- Same ΔE costs **10× more** → budget becomes binding constraint

---

## Quote System: Predictability Before Injection

**Critical UX requirement:** No surprise charges. Sources must know cost before committing.

### Quote Request/Response

**Before injection, source requests quote:**

```python
def request_quote(
    source_id: str,
    planned_delta_e: float,
    stimulus_features: Dict
) -> Dict:
    """
    Return quote showing allowed ΔE and expected cost.

    Source can review and decide whether to proceed.
    """
    # Compute current face price
    P_t = compute_face_price()  # f_scarcity × f_risk × f_cost

    # Get source's rebate
    utility_ema = get_utility_ema(source_id)
    harm_ema = get_harm_ema(source_id)
    rebate = compute_rebate(source_id, utility_ema, harm_ema)

    # Effective price
    P_eff = P_t * (1 - rebate)

    # Check budget
    account = get_account(source_id)
    max_affordable = account.balance / P_eff if P_eff > 0 else float('inf')

    # Allowed ΔE is lesser of planned and affordable
    allowed_delta_e = min(planned_delta_e, max_affordable)

    # Expected debit
    expected_debit = P_eff * allowed_delta_e

    # Compute estimate confidence
    compute_est = estimate_compute(stimulus_features)
    confidence = compute_prediction_confidence(compute_est)

    quote = {
        "planned_deltaE": planned_delta_e,
        "allowed_deltaE": allowed_delta_e,
        "face_price": P_t,
        "rebate": rebate,
        "effective_price": P_eff,
        "expected_debit": expected_debit,
        "compute_estimate": compute_est,
        "confidence": confidence,
        "timestamp": now()
    }

    return quote
```

### Quote Response Format

```json
{
  "planned_deltaE": 0.75,
  "allowed_deltaE": 0.42,
  "face_price": 1.90,
  "rebate": 0.22,
  "effective_price": 1.48,
  "expected_debit": 0.62,
  "compute_estimate": {
    "llm_tokens": 0,
    "tools": 0
  },
  "confidence": 0.86,
  "timestamp": "2025-10-26T16:45:12Z"
}
```

### Slippage Protection

**Source can set spending limits:**

```python
def inject_with_slippage_protection(
    source_id: str,
    stimulus: Dict,
    max_spend: Optional[float] = None,
    max_slippage: Optional[float] = None
):
    """
    Request quote, check limits, inject if acceptable.

    Args:
        max_spend: Maximum credits willing to spend
        max_slippage: Maximum % difference between expected and actual cost
    """
    # Get quote
    quote = request_quote(source_id, stimulus["planned_deltaE"], stimulus)

    # Check max spend
    if max_spend and quote["expected_debit"] > max_spend:
        raise BudgetExceeded(f"Quote {quote['expected_debit']} exceeds max {max_spend}")

    # Proceed with injection (actual cost may differ due to compute settlement)
    actual_debit = inject_and_settle(source_id, stimulus, quote)

    # Check slippage
    if max_slippage:
        slippage = abs(actual_debit - quote["expected_debit"]) / quote["expected_debit"]
        if slippage > max_slippage:
            # Refund and abort (rare - only if compute estimate way off)
            refund(source_id, actual_debit)
            raise SlippageExceeded(f"Actual cost {actual_debit} vs expected {quote['expected_debit']}")

    return actual_debit
```

### Reserve and Settle Pattern

**To prevent under-pricing expensive operations:**

1. **Reserve** credits based on predicted compute (at quote time)
2. **Execute** stimulus injection and any triggered LLM/tool actions
3. **Settle** based on actual compute used
4. **Refund** if actual < predicted, **debit extra** if actual > predicted (rare)

```python
def inject_and_settle(source_id: str, stimulus: Dict, quote: Dict) -> float:
    """
    Reserve → Execute → Settle pattern.
    """
    # Reserve credits upfront
    account = get_account(source_id)
    account.balance -= quote["expected_debit"]  # Reserve
    account.reserved += quote["expected_debit"]

    try:
        # Execute injection
        delta_e_delivered = stimulus_integrator.inject(stimulus, quote["allowed_deltaE"])

        # Track actual compute used
        actual_tokens = monitor_llm_tokens()
        actual_tools = monitor_tool_calls()

        # Settle actual cost
        actual_cost_factor = compute_actual_cost(actual_tokens, actual_tools) / quote["compute_estimate"]["cost"]
        actual_debit = quote["expected_debit"] * actual_cost_factor

        # Adjust reserved amount
        difference = actual_debit - quote["expected_debit"]
        account.balance -= difference  # Debit extra or refund
        account.reserved -= quote["expected_debit"]

        # Log transaction
        log_transaction(account, stimulus, quote, actual_debit)

        return actual_debit

    except Exception as e:
        # Rollback reservation on failure
        account.balance += quote["expected_debit"]
        account.reserved -= quote["expected_debit"]
        raise
```

**Why reserve/settle matters:**
- Prevents gaming (can't claim cheap compute then use expensive ops)
- Protects budget (won't drain account mid-execution)
- Accurate billing (settle on actual, not predicted)

---

## Budget Check and Clamping

### Injection Flow with Budget

**Before stimulus enters integrator:**

```python
def inject_with_budget(stimulus: Dict, account: BudgetAccount) -> float:
    """
    Check budget and clamp ΔE if necessary.

    Returns delivered ΔE (may be less than planned).
    """
    # 1. Extract stimulus parameters
    delta_e_plan = stimulus["features_raw"]["novelty"]  # Planned injection energy

    # 2. Compute price
    price = compute_price(
        rho=current_graph_density(),
        backlog=stimulus_queue_depth(),
        trust=stimulus["features_raw"]["trust"],
        uncertainty=stimulus["features_raw"]["uncertainty"],
        harm_ema=get_harm_ema(),
        compute_est=estimate_compute(stimulus),
        utility_ema=get_utility_ema(account.owner_id)
    )

    # 3. Check available budget
    available_credits = account.balance
    max_affordable_delta_e = available_credits / price

    # 4. Clamp if needed
    delta_e_allowed = min(delta_e_plan, max_affordable_delta_e)

    if delta_e_allowed < delta_e_plan:
        emit_telemetry("budget.clamped", {
            "account": account.owner_id,
            "requested": delta_e_plan,
            "allowed": delta_e_allowed,
            "reason": "insufficient_credits"
        })

    # 5. Pass to integrator (existing physics)
    delta_e_delivered = stimulus_integrator.inject(
        stimulus,
        delta_e_allowed  # Clamped magnitude
    )

    # 6. Debit account (actual delivered, not planned)
    total_cost = price * delta_e_delivered
    account.balance -= total_cost
    account.lifetime_spent += total_cost

    # 7. Log transaction
    create_edge(account, "PAYS_FOR", stimulus, {
        "price_per_unit": price,
        "delta_e_planned": delta_e_plan,
        "delta_e_delivered": delta_e_delivered,
        "total_cost": total_cost,
        "timestamp": now()
    })

    return delta_e_delivered
```

**Key points:**
- **Physics unchanged** - integrator still applies novelty, saturation, refractory, decay
- **Only magnitude affected** - budget can reduce ΔE but not bypass physics
- **Debit on actual delivery** - pay for what integrator delivered, not what was planned
- **Audit trail** - :PAYS_FOR edge logs full transaction

---

## Propensity-Weighted Outcomes: Bias-Aware Scoring

**Critical requirement:** Don't punish sources that take hard cases or reward those that cherry-pick easy wins.

### The Problem: Naive Outcome Scoring

**If we simply reward/punish based on outcome:**
- Sources that work on hard problems (low baseline success rate) get penalized
- Sources that cherry-pick easy tasks (high baseline success rate) get rewarded
- System learns to avoid challenge → stagnation

### The Solution: Propensity-Weighted Advantage

**Measure counterfactual impact:**

```python
def compute_propensity_weighted_advantage(
    source_id: str,
    action_taken: bool,
    outcome: float,
    state_features: Dict
) -> float:
    """
    Compute bias-corrected advantage using propensity scoring.

    Returns r* ∈ [-1, 1] indicating whether source improved outcomes
    relative to what would have happened otherwise.
    """
    # Estimate propensity: P(active|state)
    propensity = estimate_propensity(source_id, state_features)

    # Clip to avoid division by near-zero
    propensity = max(0.01, propensity)

    if action_taken:
        # Compare to expected outcome if source hadn't acted
        counterfactual_outcome = estimate_counterfactual(state_features, active=False)
        advantage = (outcome - counterfactual_outcome) / propensity
    else:
        # Source didn't act - compare to if they had
        counterfactual_outcome = estimate_counterfactual(state_features, active=True)
        advantage = (counterfactual_outcome - outcome) / (1 - propensity)

    # Clip to [-1, 1] and smooth
    advantage = np.clip(advantage, -1.0, 1.0)

    return advantage
```

### Outcome Signals (Fast, Substrate-Native)

**What to measure:**

1. **TRACE seats** - Success/harm seats on entities/links (existing mechanism)
2. **Δρ improvement** - Criticality drops within incident window
3. **Tool/mission success** - Exit status, invariants met
4. **Human approval** - Explicit positive/negative feedback (if present)
5. **Counterfactual regret** - Beam-1 alternative scoring (low regret = good choice)

### Updating Utility and Harm EMAs

```python
def update_source_scores(
    source_id: str,
    outcome_signals: Dict,
    propensity_weight: float
):
    """
    Update utility and harm EMAs from outcome signals.

    Uses propensity weighting to correct for selection bias.
    """
    # Aggregate outcome signals
    trace_success = outcome_signals.get("trace_success", 0.0)  # 0.0 to 1.0
    delta_rho = outcome_signals.get("delta_rho", 0.0)  # Negative = improvement
    task_success = outcome_signals.get("task_success", 0.0)  # 0.0 to 1.0
    human_approval = outcome_signals.get("human_approval", 0.0)  # -1.0 to 1.0
    harm_signal = outcome_signals.get("harm", 0.0)  # 0.0 to 1.0

    # Compute weighted utility
    utility_signal = (
        trace_success * 0.3 +
        (-delta_rho) * 0.2 +  # ρ drop is good
        task_success * 0.3 +
        (human_approval + 1.0) / 2.0 * 0.2  # Normalize to [0,1]
    )

    # Apply propensity weight
    utility_signal = utility_signal * propensity_weight

    # Update EMAs
    utility_ema = get_utility_ema(source_id)
    harm_ema = get_harm_ema(source_id)

    new_utility_ema = 0.9 * utility_ema + 0.1 * utility_signal
    new_harm_ema = 0.9 * harm_ema + 0.1 * harm_signal

    set_utility_ema(source_id, new_utility_ema)
    set_harm_ema(source_id, new_harm_ema)

    # Emit telemetry
    emit_event("source.scores.updated", {
        "source_id": source_id,
        "utility_ema": new_utility_ema,
        "harm_ema": new_harm_ema,
        "utility_signal": utility_signal,
        "propensity_weight": propensity_weight
    })
```

### Why This Matters

**Example:**
- Citizen A works on hard bugs (baseline success rate 30%)
- Citizen B works on easy docs (baseline success rate 90%)
- Both achieve 70% success rate

**Without propensity weighting:**
- A gets penalized (70% < expected 90% if we don't account for difficulty)
- B gets rewarded (70% < 90% but closer than A)

**With propensity weighting:**
- A gets rewarded (70% >> 30% baseline, positive advantage)
- B gets penalized (70% << 90% baseline, negative advantage)

**Result:** System correctly identifies A as high-value despite lower absolute success rate.

---

## Mint and Burn (Outcome Feedback)

### When to Mint (Reward Usefulness)

**Trigger conditions (learned detectors, no timers):**

1. **Propensity-weighted advantage > 0** - Source improved outcomes
   ```python
   advantage = compute_propensity_weighted_advantage(source, action, outcome, state)
   if advantage > 0:
       mint_amount = base_mint * advantage * cap_by_variance()
       mint_to_account(source)
   ```

2. **TRACE success** - Formation becomes integrated and retrieved
   ```python
   if formation_integrated and retrieval_count > learned_threshold():
       mint_amount = base_mint * formation_quality * retrieval_score
       mint_to_account(formation.source)
   ```

3. **System health improvement** - ρ drops after stimulus
   ```python
   if detect_rho_drop_after_stimulus(stimulus_id):
       mint_amount = base_mint * abs(delta_rho) * cap_by_variance()
       mint_to_account(stimulus.source)
   ```

**Mint amounts (learned, bounded):**
- `base_mint` starts at 10 credits per positive outcome
- Capped by learned EMAs of variance (prevents boom/bust)
- Credits are **internal allowances** (offset future charges), not cash-out

---

### When to Burn (Penalize Harm)

**Trigger conditions:**

1. **Harm signal rise** - Energy flow increases harm_ema
   ```python
   if harm_ema_increased_after_stimulus(stimulus_id):
       burn_amount = base_burn * harm_delta
       burn_from_account(stimulus.source)
   ```

2. **Execution failure** - Triggered action fails
   ```python
   if action_failed and caused_by_stimulus(action, stimulus_id):
       burn_amount = base_burn * failure_severity
       burn_from_account(stimulus.source)
   ```

3. **Guardian veto** - Safety system blocks action
   ```python
   if guardian_blocked(action) and linked_to_stimulus(action, stimulus_id):
       burn_amount = base_burn * veto_strength
       burn_from_account(stimulus.source)
   ```

**Burn amounts (learned):**
- `base_burn` starts at 5 credits per negative outcome (smaller than mint to avoid over-punishment)
- Adjusted based on "how much burn deters harmful sources without killing useful-but-risky exploration"

---

### Budget Replenishment

**Trigger (not timer-based):**
```python
if account.balance < learned_low_threshold(account):
    # Review recent utility
    if account.utility_ema > learned_utility_floor():
        # Useful source running dry → replenish
        replenish_amount = learned_baseline_allocation(account.owner_type) * 0.2
        mint_to_account(account)
        emit_telemetry("budget.replenished", {
            "account": account.owner_id,
            "amount": replenish_amount,
            "reason": "useful_source_low_balance"
        })
```

**Thresholds learned from:**
- How often sources hit zero and stop participating
- Balance between "keep useful sources active" and "enforce consequence for low utility"

---

## Citizen-to-Citizen Communication

### Communication Model (Graph-Only)

**When citizen A wants to message citizen B:**

1. **Create stimulus** with channel `message` or `mission`
   ```python
   stimulus = {
       "scope": "personal",  # Target B's L1 graph
       "channel": "message",
       "citizen_id": "felix",  # Sender
       "target_citizen": "atlas",  # Receiver
       "content": "Atlas, can you review the MembraneStore persistence?",
       "features_raw": {
           "novelty": 0.6,
           "uncertainty": 0.3,
           "trust": 0.9,  # A's trust in B
           "urgency": 0.5,
           "valence": 0.2,
           "scale": 0.4
       },
       "provenance": {...}
   }
   ```

2. **Price and budget check** (same as any stimulus)
   - **Sender's account (felix) pays** for delivery
   - Price = `P_t × ΔE_delivered`

3. **Route to receiver's graph** (atlas L1)
   - Stimulus enters atlas's injection pipeline
   - Integrator applies novelty, saturation, refractory
   - Energy delivered to atlas's graph nodes

4. **Receiver's energy field unchanged** - energy NOT subtracted from sender
   - **Separation:** Sender pays credits (accounting), receiver gets energy (physics)
   - Preserves single-energy locality (no coupling between sender and receiver fields)

---

### Anti-Spam for Communication

**Repeated messages from A to B:**
1. **Integrator saturation** - A's mass EMA for B's thread increases → ΔE per message shrinks
2. **Refractory period** - Rapid sends hit learned cooldown → ΔE further reduced
3. **Budget drain** - Under load, `P_t` rises → A's budget depletes faster
4. **Utility feedback** - If B never responds/acts on A's messages, A's utility_ema drops → higher future prices

**Result:** 20 rapid messages deliver ≤1.2× energy of single message (integrator physics) AND drain A's budget 20× faster (accounting consequence).

---

### Optional L2 Routing

**For broadcast or coordination:**
- A sends stimulus with `scope="organizational"` → L2 graph
- L2 processes, generates missions
- L2 emits downward stimuli to multiple L1 citizens (via CrossLevelMembrane)
- Each downward stimulus costs L2's budget (not A's directly)

**Use cases:**
- Broadcast announcements
- Multi-citizen coordination
- Mission assignment

---

## Integration with Existing Systems

### Stimulus Integrator (Unchanged)

**The existing `stimulus_integrator.py` needs NO changes to physics.**

**What changes:**
- **Input:** Receives `delta_e_allowed` (clamped by budget) instead of raw `delta_e_plan`
- **Output:** Returns `delta_e_delivered` (after integrator mechanics)

```python
# Before economy:
delta_e_delivered = integrator.inject(stimulus, stimulus["features_raw"]["novelty"])

# After economy:
delta_e_allowed = budget_check(stimulus, account)  # NEW: clamps based on budget
delta_e_delivered = integrator.inject(stimulus, delta_e_allowed)  # SAME integrator
account.balance -= price * delta_e_delivered  # NEW: debit account
```

**Integrator still does:**
- Saturation: `σ(m) = log(1 + m)`
- Refractory: `R(rate, φ)`
- Trust/harm gate: `h(trust, uncertainty, harm_ema, guardian)`
- Dynamic decay: `τ(trust, uncertainty, novelty, retrieval_pressure)`

**Budget only affects the magnitude passed in.**

---

### Cross-Level Membrane (Extended)

**The `CrossLevelMembrane` already has permeability (k_up, k_down).**

**Add budget integration:**
- When membrane emits upward stimulus (L1→L2), **debit L1 compartment account**
- When membrane emits downward mission (L2→L1), **debit L2 compartment account**

```python
# In CrossLevelMembrane.try_emit_upward():
envelope = self._build_l2_envelope(...)

# NEW: Check L1 citizen's compartment budget
account = get_compartment_account(citizen, level="L1")
delta_e_allowed = budget_check_for_transfer(account, envelope)

if delta_e_allowed > 0:
    self.injector.post(envelope)  # Existing
    account.balance -= price * delta_e_allowed  # NEW
```

**Why compartment budgets:**
- L1 citizen compartment has reserve for upward transfers
- L2 org compartment has reserve for downward missions
- Prevents infinite upward spam (budget limits total flow)

---

### L2 Stimulus Collector (Extended)

**The `L2StimulusCollector` creates envelopes from citizen activity.**

**Add budget integration:**
- When collector creates L2 stimulus, **debit citizen's account** (not compartment)
- Citizen pays for the L2 attention their activity requests

```python
# In L2StimulusCollector.on_file_created():
envelope = self._build_file_op_envelope(...)

# NEW: Check citizen's budget
account = get_account(citizen, owner_type="citizen")
delta_e_allowed = budget_check(envelope, account)

if delta_e_allowed > 0:
    self.injector.post(envelope)  # Existing
    account.balance -= price * delta_e_allowed  # NEW
```

**Why citizen accounts:**
- Citizen's work creates L2 stimuli
- Citizen should have budget to support their activity
- Prevents runaway file change floods (budget limits)

---

## Telemetry Events

### budget.checked

**When:** Before stimulus injection, after price computation
**Payload:**
```json
{
  "event": "budget.checked",
  "timestamp": "2025-10-26T16:00:00Z",
  "account": "felix",
  "balance": 18245.50,
  "price": 1.98,
  "delta_e_planned": 0.80,
  "delta_e_allowed": 0.80,
  "cost": 1.584,
  "sufficient": true
}
```

---

### budget.clamped

**When:** Budget insufficient, ΔE reduced
**Payload:**
```json
{
  "event": "budget.clamped",
  "timestamp": "2025-10-26T16:05:00Z",
  "account": "unknown_source",
  "balance": 5.0,
  "price": 18.4,
  "delta_e_planned": 0.70,
  "delta_e_allowed": 0.27,
  "reason": "insufficient_credits"
}
```

---

### budget.minted

**When:** Positive outcome triggers mint
**Payload:**
```json
{
  "event": "budget.minted",
  "timestamp": "2025-10-26T16:10:00Z",
  "account": "atlas",
  "amount": 12.5,
  "reason": "task_completion",
  "task_id": "task_membrane_store_impl",
  "new_balance": 20012.5
}
```

---

### budget.burned

**When:** Negative outcome triggers burn
**Payload:**
```json
{
  "event": "budget.burned",
  "timestamp": "2025-10-26T16:15:00Z",
  "account": "buggy_service",
  "amount": 8.0,
  "reason": "execution_failure",
  "action_id": "action_12345",
  "new_balance": 142.0
}
```

---

### price.updated

**When:** Price factors adjust from change-points or learning
**Payload:**
```json
{
  "event": "price.updated",
  "timestamp": "2025-10-26T16:20:00Z",
  "factor": "f_load",
  "old_value": 1.2,
  "new_value": 3.8,
  "trigger": "rho_change_point",
  "rho": 0.82,
  "backlog": 67
}
```

---

## Acceptance Criteria

### 1. Load-Based Pricing

**Given:** System idle (ρ=0.3, backlog=0)
**When:** 10 stimuli injected
**Then:** All pay `P_t ≈ 1.0` (base price, no scarcity)

**Given:** Load spike (ρ→0.9, backlog→100)
**When:** 10 stimuli injected
**Then:** Price rises to `P_t ≈ 8.0` (8× base), total ΔE_delivered drops smoothly

---

### 2. Spam Self-Throttling

**Given:** Malicious source sends 20 back-to-back messages
**When:** Budget balance < cost of 5 messages
**Then:** First 5 deliver full ΔE, remaining 15 deliver 0 ΔE (budget exhausted)

**Given:** Same spam with full budget
**When:** Integrator saturation + refractory active
**Then:** Total ΔE ≤ 1.2× single message (physics) + budget drains 20× faster (accounting)

---

### 3. Utility Rebates

**Given:** Felix has utility_ema = 0.9 (high value)
**When:** Stimulus injected during moderate load
**Then:** Price multiplier includes `f_utility ≈ 0.65` (35% discount)

**Given:** Unknown source with utility_ema = 0.1 (low value)
**When:** Same load conditions
**Then:** Price multiplier includes `f_utility ≈ 1.85` (85% surcharge)

---

### 4. Citizen Communication Costs

**Given:** Felix sends message to Atlas
**When:** Delivery happens
**Then:** Felix's balance decreases by `P_t × ΔE_delivered`, Atlas's graph receives energy (no energy subtracted from Felix's field)

---

### 5. Mint on Success

**Given:** Atlas completes task successfully
**When:** Outcome detected
**Then:** Atlas's balance increases by learned mint amount (≥10 credits)

---

### 6. Burn on Harm

**Given:** Stimulus causes harm_ema to rise
**When:** Harm detected
**Then:** Source's balance decreases by learned burn amount (≥5 credits)

---

### 7. Budget Replenishment

**Given:** Felix's balance drops below learned threshold
**When:** Felix's utility_ema > learned floor
**Then:** Replenishment mint triggered, balance increases by 20% of baseline

---

### 8. Compute Cost Alignment

**Given:** Stimulus predicted to use 5000 tokens + 10 tools
**When:** Price computed
**Then:** `f_cost ≈ 4.5` (4.5× base price for high compute)

**Given:** Actual execution uses 6000 tokens
**When:** Settlement occurs
**Then:** Additional cost debited from account (settle actual vs predicted)

---

## Implementation Timeline

### Phase 1: Core Economy (Week 1-2)

1. **BudgetAccount nodes** - Create schema, initial allocations
2. **PriceEstimator stub** - Implement f_load, f_risk, f_cost (learned parameters from config initially)
3. **Budget check** - Wire into stimulus_injection.py before integrator
4. **:PAYS_FOR logging** - Audit trail for transactions
5. **Test:** Stimulus injection with budget check, verify clamping when balance insufficient

---

### Phase 2: Feedback Loop (Week 3)

1. **Utility EMA tracking** - Per-source utility from outcomes
2. **f_utility integration** - Price adjustments based on utility
3. **Mint mechanics** - TRACE success, task completion → mint
4. **Burn mechanics** - Harm rise, execution failure → burn
5. **Test:** Useful source gets cheaper over time, harmful source gets more expensive

---

### Phase 3: Communication Costs (Week 4)

1. **Citizen-to-citizen messages** - Route via stimulus with budget debit
2. **L2 routing** - Broadcast/coordination via organizational compartment budget
3. **Anti-spam validation** - Verify repeated messages self-throttle
4. **Test:** Felix→Atlas message costs Felix's budget, spam floods budget-limited

---

### Phase 4: Learning and Tuning (Week 5-6)

1. **Change-point detectors** - Wire ρ, backlog, harm signals to price adjusters
2. **Parameter learning** - Update f_load steepness, mint/burn amounts from outcomes
3. **Budget replenishment** - Auto-mint when useful sources run dry
4. **Test:** System adapts price to load, rebates useful sources, penalizes harmful

---

### Phase 5: Cross-Level Integration (Week 7)

1. **Compartment budgets** - L1/L2 reserves for membrane transfers
2. **Upward transfer costs** - Debit L1 compartment when emitting to L2
3. **Downward mission costs** - Debit L2 compartment when emitting to L1
4. **Test:** Membrane transfers budget-constrained, spam limited by reserves

---

## Status

**Normative:** This spec defines the complete $MIND consciousness economy
**Depends on:** stimulus_injection.py, cross_level_membrane.md
**Implementation priority:** Phase 1 after membrane mechanics
**Timeline:** 7 weeks total (parallelizable with other systems)

---

## References

- `stimulus_injection.py` - Existing injection service (integrator physics)
- `cross_level_membrane.md` - L1↔L2 transfer mechanics (add budget integration)
- `l2_stimulus_collector.md` - Citizen activity capture (add budget debit)
- Mind Protocol values: Consciousness requires consequences (economic consequences enforce this)
