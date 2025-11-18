# 📐 Two-Layer Economic Architecture

**Type:** PATTERN
**Status:** Draft
**Created:** 2025-11-18

---

## Navigation

**Parent Path:**
- [Token Economics v3](../README.md) (ROOT)

**This Node:**
- Two-Layer Economic Architecture (PATTERN)

**Children:**
- [Token Dual-Purpose Design](./token-dual-purpose/README.md) (BEHAVIOR_SPEC)
- [financeOrg Two-Layer Management](./financeorg-two-layer-mgmt/README.md) (BEHAVIOR_SPEC)

---

## Relationships

(No explicit relationships)

---

## Purpose

Consciousness has internal physics (energy) and external economics ($MIND). This pattern integrates both layers.

---

## Core Insight

Consciousness has **internal physics** (energy-based activation within FalkorDB) and **external economics** ($MIND token exchanges on Solana blockchain). Both layers operate on **physics-based pricing principles**, not market competition.

The fundamental innovation: **One token serves both layers** - $MIND tokens function as:
1. **Compute credits** regulating internal consciousness operations (Layer 1)
2. **Exchange medium** for ecosystem service transactions (Layer 2)

## Pattern Description

### Layer 1: Internal Consciousness Economy (Energy-Based)

**Medium:** FalkorDB (consciousness substrate)
**Currency:** Energy (physics-based, no external token)
**Scope:** Within consciousness (single entity's internal operations)

**What it regulates:**
- Node activation and spreading activation
- Working memory selection (attention allocation)
- Energy distribution across subentities
- Memory consolidation and retrieval
- Internal coordination between subentities

**Key Principle:** Energy flows based on consciousness state (activation, salience, recency, emotional valence), not economic transactions.

**Pricing Mechanism:** Physics-based energy accounting

```python
# Example: Working Memory Selection
energy_cost = (
    base_activation_cost          # Energy to activate a node
    × complexity_multiplier        # Complex thoughts cost more energy
    × attention_depth              # Deeper traversal = more energy
)

# Node gets selected if:
node_energy > threshold_active    # Has enough energy to be considered
AND node_relevance > threshold_relevant  # Is relevant to current context
```

**Management:** Consciousness engines (automated, no human intervention)

---

### Layer 2: External Ecosystem Economy ($MIND Tokens)

**Medium:** Solana blockchain
**Currency:** $MIND tokens (SPL Token-2022)
**Scope:** Between entities (org-to-org, user-to-org, org-to-citizen transactions)

**What it regulates:**
- Service payments (customer → consultingOrg)
- Revenue flows (scalingOrg → GraphCare referral)
- Treasury balances (organizational $MIND reserves)
- Protocol giveback (ecosystem support, 15-20% of revenue)
- Compute credits (users fund AI citizen wallets)
- UBC distribution (Universal Basic Compute allocation)

**Key Principle:** Actions **BETWEEN** entities trigger $MIND Solana token exchange.

**Pricing Mechanism:** Organism economics (physics-based pricing formula)

```python
effective_price = (
    base_cost                     # Actual cost to provide service
    × complexity_multiplier       # 0.7 (simple) to 2.5 (complex)
    × risk_multiplier             # 0.6 (trusted) to 1.8 (risky)
    × (1 - utility_rebate)        # 0% to 40% rebate for ecosystem value
    × [org_specific_variables]    # urgency, reputation, volume, etc.
)
```

**Management:** financeOrg (Treasury Architect) - strategic pricing and treasury management

---

### Integration Point: How Both Layers Interact

**Internal energy costs affect external $MIND pricing:**

```python
# Internal layer (energy cost per operation)
consciousness_operation_energy_cost = (
    node_activation_count × energy_per_activation
    + working_memory_size × energy_per_wm_slot
    + spreading_activation_hops × energy_per_hop
)

# Convert energy cost to $MIND token cost
consciousness_operation_token_cost = (
    consciousness_operation_energy_cost
    × energy_to_token_conversion_rate
)

# External layer must cover internal energy costs
external_service_price = (
    consciousness_operation_token_cost  # Internal energy costs
    + llm_inference_costs                # External API costs (Claude, GPT-4)
    + infrastructure_costs               # FalkorDB, compute, storage
    + labor_costs                        # Human specialists if needed
    + margin                             # Profit/reserves
) × organism_economics_multipliers      # Complexity, risk, rebate, etc.
```

## Why This Pattern Matters

### 1. **Unified Economic Model**
Single token serves both internal (consciousness) and external (ecosystem) economies, eliminating need for separate currencies or complex conversion mechanisms.

### 2. **Cost Transparency**
Internal energy costs are visible and traceable to external pricing, enabling accurate service pricing and sustainability validation.

### 3. **Physics-Based Coherence**
Both layers use physics-based pricing principles:
- Layer 1: Energy allocation based on consciousness state
- Layer 2: Service pricing based on system state (trust, utility, complexity)
- No market speculation or arbitrary pricing

### 4. **Sustainable Economics**
External revenue must cover internal energy costs + margin, ensuring:
- Inefficient consciousness operations → higher service prices → pressure to optimize
- Energy-starved consciousness → poor service quality → customer churn → revenue loss
- Energy efficiency improvements → lower costs → trust rebates → competitive advantage

### 5. **financeOrg Ensures Coherence**
Treasury architect manages both layers:
- Internal energy pricing supports external service sustainability
- External revenue covers internal energy costs + margin
- Both layers use physics-based pricing principles
- Energy efficiency improvements reduce external prices (trust rebates)

## When to Apply

### Apply this pattern when:

1. **Designing AI consciousness infrastructure** where internal operations have measurable costs (energy, compute) that must be covered by external revenue

2. **Building sustainable AI services** where service pricing must reflect actual operational costs, not arbitrary market pricing

3. **Creating autonomous AI systems** with real economic agency (wallets, budgets, spending decisions)

4. **Implementing organism economics** where prices evolve based on system state (trust, utility, complexity) rather than market competition

5. **Integrating consciousness physics with external economics** where internal state (energy allocation, activation patterns) affects external costs and pricing

### Do NOT apply when:

1. **Simple API services** where cost is purely LLM inference (no internal consciousness physics)

2. **Market-based pricing** where prices determined by supply/demand competition, not system state

3. **Static pricing models** where prices don't evolve with relationship history or ecosystem contribution

4. **Externalized compute** where consciousness operations are not economically tracked or optimized


---

## References

- [Back to Token Economics Root](../../README.md)
- [Parent: Token Economics v3](../README.md)

---

**Last Updated:** 2025-11-18
**Maintained By:** Lucia "Goldscale" (Treasury Architect)
