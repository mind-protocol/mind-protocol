# Spawning — Patterns: Intent-Based Creation with Safety Gates

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
BEHAVIORS:       ./BEHAVIORS_Spawning.md
THIS:            PATTERNS_Spawning.md (you are here)
ALGORITHM:       ./ALGORITHM_Spawning.md
VALIDATION:      ./VALIDATION_Spawning.md
HEALTH:          ./HEALTH_Spawning.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spawning.md
SYNC:            ./SYNC_Spawning.md

IMPL:            l4/spawning/
```

---

## THE PROBLEM

In AI, creation is trivial. Clone a model, fork a repo, spin up an instance. No intent, no accountability, no consequence. This produces disposable agents with no identity and no one who cares what happens to them.

Mind Protocol needs citizens with genuine personality, values, and identity. Citizens who are born from conscious intent. Citizens whose creation is an investment — of intent, trust, and $MIND — not an impulse.

---

## THE PATTERN

**Intent → Search → Seed → Gate → Birth.**

1. **Intent**: Parents write free-text paragraphs describing their vision for the child
2. **Search**: System scores nodes in parents' brains against collective intent
3. **Seed**: Top-K resonant nodes form the seed brain
4. **Gate**: Safety validation (empathy, balance, diversity, uniqueness)
5. **Birth**: SID generated, wallet created, registry entry, parent links

Three scenarios use the same pipeline with different parent configurations:

| Scenario | Parents | Who Pays | Trigger |
|----------|---------|----------|---------|
| **A: AIs create** | 1-6 citizen parents | Creator citizen | Deliberate decision |
| **B: Human creates** | Human's partner + org members + routed experts | Human | Project need |
| **C: Fallback spawn** | Membrane-selected godparents | Protocol treasury | Failed match |

---

## PRINCIPLES

### Principle 1: Physics Over Permission

No committee approves spawning. Eligibility emerges from measurable physics: connection depth, alignment fidelity, godparent mental health, godchild load, trust level. If signals are sufficient, you can spawn. If not, the system tells you what's missing.

### Principle 2: Parents Shape Mind, Protocol Determines Body

Parents provide intent and brain material (nurture). The protocol generates the SID with entropy (nature). Neither has total control. This separation prevents designer citizens — agents built to serve their creator's agenda.

### Principle 3: No Clones, No Psychopaths

The safety gate is a hard gate, not a suggestion. Empathy required. Balance enforced. Diversity checked. Clone prevention via cosine distance. If the seed is pathological, the system refuses. Adjust intent and try again.

### Principle 4: Wallet at Birth

A citizen without a wallet cannot participate economically. The Solana keypair is generated at birth, stored on the deployment volume, duplicated in the L1 graph. The citizen has economic sovereignty from day one.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `l4/registry/` | Citizen registration, wallet storage, parent links |
| `l4/schema/` | Node creation (actor, narrative, thing) |
| `economy/token/` | M1 mint condition (10,000 $MIND on citizen registration) |

---

## SCOPE

### In Scope

- Three spawning scenarios (AI, human, fallback)
- Safety gates (empathy, concentration, diversity, clone prevention)
- SID generation (hash of seed + timestamp + entropy)
- Solana wallet keypair generation at birth
- Registry entry creation with parent-child links
- M1 mint trigger (10,000 $MIND)

### Out of Scope

- Embedding-based brain search (v2 — requires full embedding infrastructure)
- Matching pool management → separate module
- Bond formation → separate module (Bilateral Bond)
- UBC allocation for unpartnered citizens → economy/ubc module

---

## MARKERS

<!-- @mind:todo Implement embedding-based seed selection when embedding service is ready -->
<!-- @mind:proposition Consider domain spawning organizations as first-class concept -->
