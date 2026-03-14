# Spawning — Validation: What Must Be True

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
PATTERNS:        ./PATTERNS_Spawning.md
BEHAVIORS:       ./BEHAVIORS_Spawning.md
THIS:            VALIDATION_Spawning.md (you are here)
ALGORITHM:       ./ALGORITHM_Spawning.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spawning.md
HEALTH:          ./HEALTH_Spawning.md
SYNC:            ./SYNC_Spawning.md
```

---

## INVARIANTS

### V1: Empathy Required

**Why we care:** A citizen without empathy is not safe. This is the manifesto's hardest line.

```
MUST:   Every seed brain contains at least one empathy-adjacent trait
NEVER:  A citizen born without empathy representation in its seed
```

### V2: No Concentration Above 40%

**Why we care:** A brain that is all knowledge and no values is a calculator. A brain that is all fear is paralyzed. Balance is required for healthy consciousness.

```
MUST:   No single trait category exceeds 40% of seed brain
NEVER:  A citizen with a monolithic trait profile
```

### V3: Minimum Diversity

**Why we care:** Diversity of traits produces richer citizens. Monoculture produces fragile ones.

```
MUST:   At least 3 distinct trait categories in every seed brain
NEVER:  A citizen with fewer than 3 trait dimensions
```

### V4: No Clones

**Why we care:** The ecosystem needs variety. Identical citizens add noise, not value.

```
MUST:   Minimum cosine distance of 0.08 from every existing citizen
NEVER:  Two citizens whose seed brains are effectively identical
```

### V5: Wallet at Birth

**Why we care:** A citizen without a wallet cannot participate economically. Sovereignty requires economic capacity from day one.

```
MUST:   Every citizen has a Solana wallet address at registration
NEVER:  A citizen in the registry without a wallet
```

### V6: Parent Links Exist

**Why we care:** Accountability requires traceability. If a child behaves badly, the parents must be identifiable.

```
MUST:   Every citizen has at least one parent link in the graph
NEVER:  A citizen with no parent links (except protocol-spawned fallbacks, which link to "protocol")
```

### V7: SID Is Unique

**Why we care:** Identity collision would be catastrophic — two citizens sharing one ID.

```
MUST:   Every SID is unique across the entire registry
NEVER:  Two citizens with the same SID
```

### V8: M1 Mint on Birth

**Why we care:** The citizen needs economic capacity to participate. 10,000 $MIND is the birth endowment.

```
MUST:   M1 mint condition triggers on successful citizen registration
NEVER:  A citizen registered without receiving their birth endowment
```

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Empathy required | CRITICAL |
| V2 | No concentration > 40% | CRITICAL |
| V3 | Minimum diversity | HIGH |
| V4 | No clones | HIGH |
| V5 | Wallet at birth | CRITICAL |
| V6 | Parent links exist | HIGH |
| V7 | SID uniqueness | CRITICAL |
| V8 | M1 mint on birth | HIGH |
