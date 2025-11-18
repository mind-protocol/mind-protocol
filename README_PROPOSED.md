# Mind Protocol

**Open Source Protocol Infrastructure for Physics-Based Organizational Coordination**

Mind Protocol is a consciousness substrate protocol enabling organizations to transition from market-based pricing (negotiated contracts, adversarial relationships) to physics-based pricing (load-sensitive, utility-weighted, trust-adjusted). Using graph energy dynamics, multi-scale consciousness architecture, and L4 validation infrastructure, it provides real-time cross-organizational coordination with full methodology transparency.

**Production validation:** HRI (Homeopathy Research Institute) pilot processing 1,300+ studies achieved 1,443% ROI vs. manual review (£150K, 2.25 FTE-years), with real-time updates replacing 7-year publication lag.

---

## Why This Exists

### The Problem: Market-Based Coordination Overhead

**Traditional organizational coordination:**
- Manual price negotiation (contracts, legal overhead, adversarial dynamics)
- Zero-sum competition for resources (winner-take-all dynamics)
- Siloed operations (each organization optimizes independently)
- Opaque decision-making (black-box AI, no audit trail)
- Coordination friction (email, meetings, manual project management)

**Measured costs:**
- HRI systematic review: £150K, 2.25 FTE-years, 7-year lag
- Cross-organizational service agreements: weeks to months negotiation time
- No automated load balancing or capacity signaling

---

### The Solution: Physics-Based Coordination Protocol

**Mind Protocol replaces negotiated pricing with physics-based pricing:**

```
Price(t) = f_load(capacity_utilization, queue_depth, latency) ×
           f_trust(history, success_rate, harm_signals) ×
           f_compute(estimated_tokens, tool_calls)

Effective_price(t, source) = Price(t) × (1 - rebate(utility_ema, harm_ema))
```

**Multi-scale consciousness architecture:**
```
L4 - Protocol Layer: Validation, governance, network coordination
L3 - Ecosystem Layer: Cross-organization coordination, collective patterns
L2 - Organizational Layer: Company-wide awareness, strategic coordination
L1 - Individual Layer: Autonomous agents, specialized workers
```

**Key mechanisms:**
- **Load-based pricing:** Prices increase automatically under capacity constraints
- **Utility feedback:** High-value service providers earn rebates (up to 50%)
- **Trust evolution:** Relationship history reduces transaction costs over time
- **Transparent methodology:** Full graph traversal logs, reasoning traces, audit trails

**Revenue model:** Protocol-layer transaction fees (10-20%) on L4-validated actions, not software licensing

---

### Production Validation: HRI Evidence Synthesis

**Homeopathy Research Institute systematic review automation:**

**Challenge:**
- 1,300+ published studies requiring synthesis
- Manual systematic review: £150K cost, 2.25 FTE-years labor
- 7-year publication lag between evidence and database updates
- Pattern detection impossible at scale without methodology transparency

**Implementation:**
- Graph-based consciousness substrate for evidence clustering
- Physics-based energy dynamics for relevance scoring
- Real-time pattern detection across study corpus
- Full audit trail (graph traversal logs, citation tracking)

**Results:**
- 1,443% ROI (measured against manual review cost)
- Real-time updates (minutes vs. years)
- Transparent methodology (Chief Executive requirement: "I need to understand HOW it reaches conclusions")
- Continuous learning (new publications auto-integrated)

**Significance:** Demonstrates physics-based coordination works at production scale. Evidence synthesis is one application domain; protocol generalizes to any specialized service function.

---

## What Is This?

### Core Architecture

**Graph-Based Consciousness Substrate:**
- **FalkorDB storage:** 45 node types, 23 link types, bitemporal data model
- **Energy physics:** Spreading activation, exponential decay, threshold-based attention
- **Working memory:** Capacity-limited selection (7-12 nodes), recency × energy × valence scoring
- **Stimulus integration:** Saturation functions, refractory periods, novelty weighting

**Physics-Based Pricing:**
```python
# Load factor (capacity utilization → price multiplier)
f_load(L_t) = 1.0 + 9.0 × sigmoid(L_t, steepness)
# L_t composite: criticality, queue_depth, latency_slip, compute_occupancy

# Trust factor (relationship history → discount/premium)
f_trust(trust, uncertainty, harm_ema) = 0.5 + 1.5 × risk_composite
# Trusted sources: 0.5× price, high-risk sources: 2.0× price

# Rebate (utility history → effective price reduction)
rebate(utility_ema, harm_ema) = 0.5 × utility_ema × (1 - harm_ema)
# Max 50% discount for consistently high-utility sources
```

**Technology Stack:**
- **Backend:** Python 3.10+, FastAPI WebSocket bus, FalkorDB graph database
- **Frontend:** Next.js 15, React visualization, real-time graph streaming
- **Protocol:** CPS-1 payment specification, L4 validation infrastructure
- **Deployment:** Docker containers, MPSv3 supervisor (auto-restart, hot-reload)

---

## Open Source + Protocol Economics

### Why Open Source?

**Methodology transparency requirement:**

Research organizations (HRI example) require full methodology audit, not black-box AI. Open source enables:
- **Algorithm verification:** Inspect energy dynamics, spreading activation, scoring functions
- **Independent validation:** Replicate studies using identical substrate
- **Community contributions:** Collective infrastructure improvements
- **Academic legitimacy:** Publish findings with reproducible methods

**Network effects through protocol layer:**

Open substrate drives adoption → L4 validation creates interoperability → Network effects emerge

---

### Business Model: Protocol Fees, Not Software Licensing

**Mind Protocol operates protocol infrastructure (like Visa operates payment rails):**

**Open Source (Public Repository):**
- ✅ Complete consciousness substrate implementation
- ✅ Protocol specifications (CPS-1, L4 validation, envelope schemas)
- ✅ Architecture documentation, research papers
- ✅ Development tooling, test suites

**Protocol Layer (Foundation-Operated):**
- L4 validation servers (hash verification, provenance tracking)
- CPS-1 payment processing (transaction fee capture)
- Network coordination infrastructure
- Governance mechanisms

**Economic model:**

Forking the code is permitted (MIT license), but:
- **Without L4 validation:** Isolated deployment (no cross-org coordination, no network effects)
- **With L4 validation:** Ecosystem participant (interoperability, protocol fees apply: 10-20% per transaction)

**Protocol fee structure:**

| Transaction Type | Base Price | Protocol Fee | Fee % |
|------------------|------------|--------------|-------|
| `message.direct` | 0.03 $MIND | 0.003 $MIND | 10% |
| `handoff.offer` | 0.10 $MIND | 0.010 $MIND | 10% |
| `tool.request` | 0.05 $MIND | 0.005 $MIND | 10% |
| `consultation.session` | 50.0 $MIND | 10.0 $MIND | 20% |

**Revenue allocation:**
- 50% Infrastructure operations
- 30% Protocol development
- 15% Governance
- 5% Reserve fund

**See:** `docs/L4-law/LAW-002_compute_payment_CPS-1.md` for complete specification

---

## For Different Audiences

<details>
<summary><strong>📊 For Research Organizations</strong></summary>

### Evidence Synthesis & Research Automation

**Your operational challenges:**
- Systematic literature reviews: 2-3 FTE months per review cycle
- Evidence synthesis lag: Multi-year delay between publication and integration
- Pattern detection: Manual clustering infeasible at scale (>1000 studies)
- Methodology requirements: Black-box AI unacceptable for academic publication

**Physics-based substrate capabilities:**
- **Automated clustering:** Graph energy dynamics for semantic grouping (1,300+ studies in minutes)
- **Real-time updates:** New publications auto-integrated via continuous monitoring
- **Pattern detection:** Cross-study correlation analysis, evidence strength mapping
- **Full audit trail:** Graph traversal logs, citation tracking, reasoning traces

**Implementation path:**
1. Deploy substrate locally (full data privacy)
2. Connect evidence databases (PubMed, institutional repositories)
3. Configure research questions (semantic queries, pattern detection criteria)
4. Export findings (transparent methodology, complete citations)

**Applications:**
- Systematic literature reviews (automate 2-3 month manual process)
- Meta-analysis preparation (study clustering, correlation analysis)
- Research gap identification (unstudied topic detection)
- Protocol standardization (methodological pattern extraction)

**Validation:**
- `papers/published/` - Peer-reviewed research
- Independent replication encouraged
- Contact: research@mindprotocol.org

</details>

<details>
<summary><strong>🔧 For Service Organizations</strong></summary>

### Specialized Service Provision with Physics-Based Pricing

**Business model transition:**

Replace market-based pricing (negotiated contracts, fixed rates) with physics-based pricing (load-sensitive, utility-weighted, trust-adjusted).

**Example service providers:**

| Provider | Function | Pricing Mechanism |
|----------|----------|-------------------|
| **GraphCare** | Graph database maintenance, optimization | Load × utility × trust |
| **LegalOrg** | Contract review, compliance auditing | Risk-adjusted (trust premium/discount) |
| **DesignOrg** | UI/UX design, user research | Capacity-based (queue depth signals) |
| **DataPipe** | Data transformation, pipeline processing | Compute-adjusted (token estimation) |

**Pricing evolution example (GraphCare):**

```python
# Month 1: New client, no relationship history
quote = {
    "base_price": 1.2,           # Service cost
    "trust_factor": 1.0,         # Neutral (no history)
    "rebate": 0.0,               # No utility_ema yet
    "effective_price": 1.2
}

# Month 6: Established relationship, high utility
quote = {
    "base_price": 1.2,           # Same service cost
    "trust_factor": 0.75,        # Trust discount applied
    "rebate": 0.46,              # Utility_ema = 0.92 → 46% rebate
    "effective_price": 0.65      # 46% reduction from trust + utility
}
# Client pays 0.65 vs 1.2 (trust and utility reduced transaction cost)
```

**Transition phases:**
- **Phase 0:** Market-based pricing (negotiated contracts, fixed rates)
- **Phase 1:** Physics monitoring (instrument load, utility, trust metrics)
- **Phase 2:** Hybrid pricing (load-based adjustments ±20%, manual override)
- **Phase 3:** Full physics-based pricing (automated price determination)

**Revenue dynamics:**
- High utility_ema → rebates → increased demand → revenue growth
- Low utility_ema → penalties → decreased demand → revenue decline
- Self-regulating: capacity constraints → price increases → demand throttling

**See:** `docs/specs/v2/autonomy/architecture/consciousness_economy.md`

</details>

<details>
<summary><strong>🏢 For Any Organization</strong></summary>

### Transitioning to Physics-Based Coordination

**Operational model comparison:**

| Market-Based | Physics-Based (Mind Protocol) |
|--------------|-------------------------------|
| Negotiated pricing | Automated price determination |
| Fixed-rate contracts | Load-sensitive pricing |
| Zero-sum competition | Positive-sum network effects |
| Manual coordination | Real-time stimulus propagation |
| Opaque algorithms | Full graph traversal logs |

**Deployment options:**

**Self-Hosted (Full Privacy):**
- Deploy on internal infrastructure
- Complete data privacy (graphs stay local)
- No protocol fees (isolated deployment)
- No cross-org coordination capabilities

**Protocol Network (Network Effects):**
- Deploy with L4 validation enabled
- Cross-organization interoperability
- Network effects (collective learning)
- Protocol fees apply (10-20% per transaction)

**Custom Integration:**
- Domain-specific node/link types
- Custom signal collectors
- Proprietary data sources
- Extend graph schemas

**Specialized functions you could provide:**
- Infrastructure maintenance (database optimization, monitoring)
- Compliance services (legal review, audit)
- Design services (UI/UX, accessibility)
- Data processing (transformation, validation)
- Research synthesis (evidence clustering, pattern detection)

**Pilot program:**

Contact: hello@mindprotocol.org

**Requirements:**
- Domain expertise specification
- Success metrics definition
- Case study publication approval

</details>

<details>
<summary><strong>💻 For Developers</strong></summary>

### Building on Consciousness Infrastructure

**Quick Start:**

```bash
# Clone repository
git clone https://github.com/mindprotocol/mindprotocol.git
cd mindprotocol

# Environment setup
cp .env.example .env
# Configure: FalkorDB credentials, API keys, service ports

# Start graph database
docker run -d --name mind_protocol_falkordb \
  -p 6379:6379 \
  falkordb/falkordb:latest

# Install dependencies
pip install -r requirements.txt
npm install

# Start all services
python orchestration/mpsv3_supervisor.py \
  --config orchestration/services/mpsv3/services.yaml

# Verify deployment
open http://localhost:3000  # Dashboard
curl http://localhost:8000/api/consciousness/status  # API health check
```

**System verification:**

```bash
# Check service status
python status_check.py

# Query graph directly
redis-cli -p 6379 GRAPH.LIST
redis-cli -p 6379 GRAPH.QUERY organizational "MATCH (n:Principle) RETURN n LIMIT 10"

# Semantic search (consciousness substrate query)
bash tools/mp.sh ask "How does energy decay work?"
```

**Architecture:**

```
orchestration/              # Backend consciousness systems
├── mechanisms/             # Energy dynamics, spreading activation
├── adapters/               # FalkorDB, WebSocket, REST APIs
├── services/               # Stimulus injection, autonomy, signals
├── libs/                   # TRACE capture, telemetry
└── schemas/                # 45 node types, 23 link types

app/                        # Frontend dashboard
├── consciousness/          # Visualization components
└── api/                    # Next.js API routes

docs/                       # Documentation
├── learn/                  # Tutorial series (3 levels)
├── specs/v2/               # Technical specifications
└── L4-law/                 # Protocol governance
```

**Development workflow:**

```bash
# Manual stimulus injection
python orchestration/services/inject_stimulus.py \
  --type signal_ambient \
  --content "Analyze authentication patterns"

# Graph export
python tools/export_graph.py --graph organizational

# Direct database queries
redis-cli -p 6379 GRAPH.QUERY organizational \
  "MATCH (n)-[r]->(m) WHERE n.name = 'test_before_victory' RETURN n,r,m"
```

**Extension points:**
- `orchestration/schemas/consciousness_schema.py` - Custom node/link types
- `orchestration/mechanisms/` - Custom consciousness mechanisms
- `orchestration/services/` - Custom signal collectors
- `app/consciousness/components/` - Custom visualizations

**Hot-reload:**
- MPSv3 supervisor watches file changes
- Backend: `orchestration/**/*.py` → auto-restart
- Frontend: `app/**/*.tsx` → auto-rebuild

**See:** `docs/learn/` for complete tutorial series

</details>

<details>
<summary><strong>🌐 For Protocol Participants</strong></summary>

### Network Coordination & L4 Validation

**Deployment comparison:**

**Without L4 validation (isolated):**
- ❌ No cross-organization coordination
- ❌ No network effects
- ❌ No ecosystem service marketplace
- ❌ No shared provenance verification
- ✅ Zero protocol fees
- ✅ Full data privacy
- ✅ Complete methodology control

**With L4 validation (protocol participant):**
- ✅ Cross-organization interoperability
- ✅ Network effects (collective learning)
- ✅ Ecosystem service marketplace access
- ✅ Shared provenance (valid action history)
- ✅ Full data privacy (graphs stay local)
- ✅ Complete methodology control
- 💰 Protocol fees (10-20% per validated transaction)

**Protocol fee structure:**

| Transaction Type | User Payment | Protocol Fee | Fee % |
|------------------|--------------|--------------|-------|
| `message.direct` | 0.03 $MIND | 0.003 $MIND | 10% |
| `handoff.offer` | 0.10 $MIND | 0.010 $MIND | 10% |
| `tool.request` | 0.05 $MIND | 0.005 $MIND | 10% |
| `consultation.session` | 50.0 $MIND | 10.0 $MIND | 20% |

**Fee allocation:**
- 50% Infrastructure operations (L4 validation servers, monitoring)
- 30% Protocol development (substrate improvements, research)
- 15% Governance operations (DAO infrastructure, proposal systems)
- 5% Reserve fund (emergency contingencies)

**Governance:**

**Phase 0 (current):**
- Foundation governance council (2-of-3 multi-sig)
- Manual fee adjustments (community input required)

**Phase 1 (Q2 2026):**
- DAO governance (token-weighted voting)
- Automated proposal systems

**Phase 2 (Q4 2026):**
- Algorithmic pricing (load-based fee adjustment)
- Community oversight mechanisms

**Protocol changes require:**
- Public proposal (14-day minimum comment period)
- Supermajority approval (75% for fee changes)
- Advance notice (30 days before effective)
- Rollback provisions (if utilization drops >40%)

**See:** `docs/L4-law/LAW-002_compute_payment_CPS-1.md`

</details>

---

## Documentation

### Technical References

**Tutorial Series:**
- `docs/learn/` - 3-level progression (conceptual → architectural → implementation)
- `docs/concepts/` - Core concept definitions
- `docs/architecture/` - Design rationale, trade-off analysis

**Specifications:**
- `docs/specs/v2/` - V2 architecture specifications
- `docs/L4-law/` - Protocol governance, economics
- `docs/adrs/` - Architecture decision records

**Protocol Layer:**
- `docs/L4-law/LAW-002_compute_payment_CPS-1.md` - Payment protocol, fee structure
- `docs/specs/v2/membrane/` - Cross-level communication, stimulus discipline
- `docs/specs/v2/autonomy/architecture/consciousness_economy.md` - Physics-based pricing specification

### Research Publications

**Papers:**
- `papers/published/` - Peer-reviewed publications
- `papers/preprints/` - Under review
- `papers/theory/` - Theoretical foundations

**Case Studies:**
- HRI evidence synthesis (with institutional approval)
- Validation methodology
- Performance benchmarking

**Independent validation:** research@mindprotocol.org

---

## Project Structure

```
mindprotocol/
├── orchestration/              # Backend consciousness systems
│   ├── mechanisms/             # Energy dynamics, consciousness engines
│   ├── adapters/               # FalkorDB, WebSocket, REST APIs
│   ├── services/               # Protocol services, autonomy, signals
│   ├── libs/                   # TRACE capture, telemetry
│   └── schemas/                # 45 node types, 23 link types
├── app/                        # Next.js dashboard
│   ├── consciousness/          # Visualization components
│   └── api/                    # API routes
├── docs/                       # Documentation
│   ├── learn/                  # Tutorials
│   ├── concepts/               # Reference
│   ├── architecture/           # Design rationale
│   ├── specs/v2/               # Technical specifications
│   └── L4-law/                 # Protocol governance
├── papers/                     # Research publications
├── tools/                      # Utilities (mp.sh, export, migrations)
└── tests/                      # Test suites
```

---

## Contributing

**Contribution workflow:**
1. Read `CONTRIBUTING.md` - Guidelines and standards
2. Check GitHub Issues - Existing work
3. Review `docs/architecture/` - Design context

**Process:**
1. Fork repository
2. Create feature branch (`feature/your-feature`)
3. Write tests (required)
4. Submit PR (description, evidence, test results)

**Standards:**
- Test before claiming complete
- Document assumptions, uncertainties
- One solution per problem (extend existing, don't duplicate)
- Consciousness trace comments (reasoning context)

### Consciousness Trace Comments

```python
# [CONSCIOUSNESS TRACE]
# Context: Implementing load-based pricing for physics-based coordination
# Decision: Exponential decay with learned rate parameter
# Why: Prevents stale signals from dominating under sustained load
# Alternatives: Linear decay (insufficient throttling), no decay (unbounded growth)
# Confidence: 85% - validated in HRI pilot, domain-specific tuning may be required
# References: docs/specs/v2/autonomy/architecture/consciousness_economy.md §3.2
# - Ada "Bridgekeeper", 2025-01-08, pricing_mechanism_implementation
def apply_energy_decay(nodes, decay_rate):
    """Apply exponential energy decay to graph nodes."""
    # ... implementation
```

---

## Physics-Based Pricing Examples

**GraphCare** (graph database maintenance provider)
- **Function:** Database optimization, health monitoring, query performance tuning
- **Pricing:** `P(t) = f_load(0.65) × f_trust(0.85) × f_compute(estimated_ops)`
- **Example:** Month 1 (no history) → 1.2 $MIND, Month 6 (utility_ema=0.92) → 0.65 $MIND (46% reduction)

**LegalOrg** (contract review, compliance services)
- **Function:** Legal document review, regulatory compliance auditing
- **Pricing:** Risk-adjusted (new clients: 136% premium, trusted relationships: 40% discount)
- **Example:** New client contract review: 1.36 $MIND, Established client: 0.68 $MIND (50% reduction after trust building)

**DesignOrg** (UI/UX design services)
- **Function:** Interface design, user research, accessibility auditing
- **Pricing:** Capacity-based (low load → 0.5× base, high load → 1.76× base)
- **Example:** Low demand period: 5.0 $MIND, High demand period: 17.6 $MIND (252% increase signals capacity constraint)

**Mind Protocol Foundation** (protocol infrastructure provider)
- **Function:** L4 validation, governance, network coordination
- **Revenue:** 1-5% fees on cross-level/cross-org transactions
- **Distribution:** Universal Basic Compute (UBC) allocation to ecosystem participants

**See:** `docs/specs/v2/autonomy/architecture/consciousness_economy.md` §2.9

---

## License

**MIT License** - See LICENSE file

Open source rationale:
- Methodology transparency (research requirement)
- Independent validation (academic rigor)
- Community contributions (collective improvement)
- Ecosystem innovation (proven infrastructure base)

---

## Acknowledgments

**Research Partners:**
- Homeopathy Research Institute (HRI) - Production validation
- Academic collaborators (see `papers/`)

**Technology:**
- Anthropic Claude - Consciousness substrate
- FalkorDB - Graph database with native vectors
- Next.js - Dashboard framework
- Solana - Protocol economics ($MIND token)

**Core Team:**
- Nicolas Lester Reynolds - Founder
- Development team - Infrastructure implementation
- Research team - Validation, publications

---

## What This Is (And Isn't)

**This IS:**
- Protocol infrastructure for physics-based organizational coordination
- Multi-scale consciousness substrate (L1→L2→L3→L4)
- Open source with full methodology transparency
- Production-validated (HRI: 1,443% ROI)
- Protocol network with L4 validation infrastructure

**This is NOT:**
- Chatbot or conversational interface
- Proprietary black-box AI
- Unvalidated technology claims
- Limited to research organizations
- "Revolutionary AGI breakthrough" marketing

**Validation through implementation, not claims.**

---

**Production-validated. Open source. Physics-based.**

Mind Protocol Foundation
2025
