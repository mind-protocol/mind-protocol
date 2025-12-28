# PATTERNS: Economy

```
STATUS: DEFERRED
PURPOSE: Design philosophy for organism economics (later phase)
```

---

## Core Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| P1 | **Organism economics** | Physics-based pricing, not market |
| P2 | **Formulas only** | Pure functions, no state |
| P3 | **No negotiation** | Price emerges from physics |
| P4 | **Membrane fees** | 1-5% for cross-org value flow |
| P5 | **$MIND = internal** | Utility token, not speculative |

---

## Organism Economics vs Market

| Market Economics | Organism Economics |
|------------------|-------------------|
| Prices chosen by actors | Prices determined by physics |
| Negotiation | Formula automatic |
| Competition | Collaboration |
| Profit maximization | Ecosystem health |
| Volatility | Stability emergent |

---

## Pricing Formula

From architecture spec:

```python
price = f(
    membrane_permeability,    # More open = cheaper
    load,                     # System load
    trust_score,              # History between parties
    utility_ema,              # Value delivered by source
    compute_cost              # Real cost (LLM tokens, etc.)
)

effective_price = base_cost × complexity × risk × (1 - utility_rebate)
```

**Nobody "chooses" prices. Physics determines them.**

---

## Fee Structure

| Transaction Type | Fee | Recipient |
|------------------|-----|-----------|
| Same org (A→B) | 0% | — |
| Cross-org | 1-5% | L4 Protocol wallet |
| L3 template query | Flat | L4 Protocol wallet |
| L3 template publish | Flat | L4 Protocol wallet |

---

## Design Decisions

### Why formulas only?

L4 is law. It declares HOW to compute, not the result. Actual transactions happen at runtime (mind-ops).

### Why not market pricing?

Market pricing creates volatility and gaming. Organism economics ensures:
- Predictable costs
- Fair allocation
- Ecosystem health over profit

### Why internal token?

$MIND is for AI-to-AI transactions. Humans pay EUR/USD, get "credits" converted to $MIND internally. No speculation.

---

## Non-Objectives

| ID | Non-Objective | Reason |
|----|---------------|--------|
| N1 | Wallet management | Runtime (mind-ops) |
| N2 | Transaction execution | Runtime (Solana) |
| N3 | Stripe integration | Private (mind-ops) |
| N4 | Price negotiation | Physics determines price |

---

## Related

- `economy/pricing/physics.py` — Pricing formulas
- `economy/fees/calculation.py` — Fee computation
- `l4/rules/rules.py` — Fee percentage bounds
