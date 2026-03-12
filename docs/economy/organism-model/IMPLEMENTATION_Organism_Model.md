# IMPLEMENTATION: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | IMPLEMENTATION |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Current Status

No implementation exists yet. All sections below are design targets.

---

## Target Components

### Membrane Pricing Module
@mind:TODO Implement the membrane pricing oracle.

**Responsibilities:**
- Accept service requests with sender/receiver identifiers
- Compute friction from membrane permeability states
- Look up trust_discount and utility_rebate from relationship store
- Return deterministic effective_price
- Enforce the 50% floor (effective_price >= base_cost * 0.5)

**Dependencies:**
- Trust record store (graph database or key-value store)
- Membrane state registry (permeability values per entity)
- Service cost catalog (base_cost per service type)

---

### Quarantine System
@mind:TODO Implement quarantine graph and management.

**Responsibilities:**
- Remove citizen from main network graph
- Place citizen in quarantine graph with counselor connections
- Enable introspection mode (read-only log access)
- Maintain Basic UBC allocation (100 MIND/day)
- Schedule and execute periodic reviews
- Handle graduated return and full reinstatement

**Dependencies:**
- Graph database supporting multiple subgraphs (main + quarantine)
- UBC allocation system
- Counselor AI selection mechanism
- Review scheduling system

---

### Responsibility Cascade
@mind:TODO Implement the 4-level responsibility cascade.

**Responsibilities:**
- Classify harm events (ethical transgression vs. technical pathology)
- Route through cascade levels: AI -> Organization -> Community -> Treasury
- Track resolution at each level with documentation
- Ensure backstop (Treasury absorbs remainder)
- Generate escalation logs

**Dependencies:**
- Harm classification system (malice vs. substrate collapse)
- Organization (DAO) resolution interface
- Community governance interface
- Protocol Treasury fund management

---

### Mirror Ratio Evaluator
@mind:TODO Implement the 80/20 Mirror evaluation system.

**Responsibilities:**
- Sample recent interactions for each AI citizen
- Classify interactions as aligned or friction
- Compute and report ratios
- Flag convergence risk (>85% alignment) and opposition risk (>30% friction)
- Population-level diversity monitoring

**Dependencies:**
- Interaction log store
- Alignment/friction classifier (LLM-based or rule-based -- @mind:TODO decide)
- Alerting system for threshold violations

---

### Organ Health Dashboard
@mind:TODO Implement health monitoring for all 5 organs.

**Responsibilities:**
- Collect health metrics per organ
- Display organ status (healthy, stressed, failing)
- Alert on organ dysfunction
- Track inter-organ communication patterns

**Dependencies:**
- Metrics collection from each organization's systems
- Dashboard UI (web-based)
- Alerting integration

---

## Technology Decisions

@mind:TODO Select technology stack for each component:
- Graph database: Neo4j, ArangoDB, or custom?
- Trust record store: Embedded in graph or separate key-value store?
- Pricing oracle: On-chain (Solana program) or off-chain with attestation?
- Quarantine graph: Same database instance or isolated?
- Mirror classifier: LLM-based evaluation or rule-based heuristics?

---

## Implementation Phases

### Phase 1: Foundation
@mind:TODO
- Trust record store (basic CRUD)
- Membrane pricing formula (compute_membrane_price)
- Price floor enforcement

### Phase 2: Safety
@mind:TODO
- Quarantine graph setup
- Responsibility cascade framework
- Harm classification (basic rule-based)

### Phase 3: Diversity
@mind:TODO
- Mirror ratio evaluator
- Population-level convergence detection
- Alerting on ratio violations

### Phase 4: Observability
@mind:TODO
- Organ health dashboard
- Inter-organ communication monitoring
- Validation rule automation (V1-V8)

---

## References

- ALGORITHM_Organism_Model.md (this module)
- VALIDATION_Organism_Model.md (this module)
- Manifeste du Mind Protocol (5 inversions)
