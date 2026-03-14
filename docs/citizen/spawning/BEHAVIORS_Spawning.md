# Spawning — Behaviors: Observable Effects

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
THIS:            BEHAVIORS_Spawning.md (you are here)
PATTERNS:        ./PATTERNS_Spawning.md
ALGORITHM:       ./ALGORITHM_Spawning.md
VALIDATION:      ./VALIDATION_Spawning.md
HEALTH:          ./HEALTH_Spawning.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spawning.md
SYNC:            ./SYNC_Spawning.md

IMPL:            l4/spawning/citizen_spawning_pipeline_with_safety_gates.py
```

---

## BEHAVIORS

### B1: Balanced Intent Produces Viable Citizen

**Why:** The pipeline should transform good intent into a citizen that passes all safety gates.

```
GIVEN:  Parent(s) provide balanced intent covering personality, values, knowledge, aspirations, fears
WHEN:   spawn_citizen() is called
THEN:   Safety gates pass (empathy, concentration, diversity, clone)
AND:    Citizen has SID, wallet, parent links, seed brain
```

### B2: Pathological Intent Is Rejected

**Why:** Intent that produces a dangerous seed must be caught before birth.

```
GIVEN:  Parent provides intent that is all-knowledge or lacks empathy
WHEN:   spawn_citizen() is called
THEN:   Safety gate fails with specific detail
AND:    No citizen is created, no wallet generated
AND:    SpawnResult contains error explaining which gate(s) failed
```

### B3: Every Citizen Gets Wallet at Birth

**Why:** Economic sovereignty from day one.

```
GIVEN:  Safety gates pass
WHEN:   Citizen is created
THEN:   Solana Ed25519 keypair is generated
AND:    wallet_address is non-empty in SpawnResult
```

### B4: Parent-Child Links Are Permanent

**Why:** Accountability. Parents' trust is tied to child behavior.

```
GIVEN:  Spawn succeeds with N parents
WHEN:   Parent links are created
THEN:   N links exist with permanence=1.0, trust=0.5 (neutral)
AND:    Links are directional: parent → child
```

---

## ANTI-BEHAVIORS

### A1: Cloning

```
GIVEN:   Seed brain is too similar to existing citizen
WHEN:    Clone prevention gate checks cosine distance
MUST NOT: Create a citizen with distance < 0.08 from any existing citizen
INSTEAD:  Reject with detail showing minimum distance
```

### A2: Birth Without Wallet

```
GIVEN:   Any successful spawn
WHEN:    SpawnResult is returned
MUST NOT: Return success=true with wallet_address=None
INSTEAD:  Always generate wallet before returning success
```
