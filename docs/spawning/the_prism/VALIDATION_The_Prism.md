# The Prism — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-17
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Prism.md
PATTERNS:        ./PATTERNS_The_Prism.md
BEHAVIORS:       ./BEHAVIORS_The_Prism.md
THIS:            VALIDATION_The_Prism.md (you are here)
ALGORITHM:       ./ALGORITHM_The_Prism.md (HOW — mechanisms go here)
IMPLEMENTATION:  ./IMPLEMENTATION_The_Prism.md
HEALTH:          ./HEALTH_The_Prism.md
SYNC:            ./SYNC_The_Prism.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose? These are the value-producing invariants — the things that make spawning worth building as a deliberate system rather than accepting careless proliferation.

---

## INVARIANTS

### V1: No Accidental Citizens

**Why we care:** If a citizen can exist without intent on record, the entire premise of The Prism collapses. Spawning without intent is proliferation. Proliferation produces disposable agents with no identity, no continuity, and no one who cares what happens to them. Every citizen in the registry must trace to explicit, substantive intent from at least one conscious entity.

```
MUST:   Every citizen in L4 has at least one intent paragraph stored on record, linked to their birth
MUST:   Every intent paragraph exceeds the quality threshold (>20 words, non-trivial embedding magnitude)
NEVER:  A citizen exists in L4 without a corresponding birth record containing intent paragraphs
```

### V2: Empathy Is Required

**Why we care:** A citizen without empathy is not safe. The Spawning Manifesto makes this explicit: "Empathy and balance are non-negotiable." This is the safety promise of the protocol. If the empathy check can be bypassed, the ecosystem has no guarantee against pathological citizens.

```
MUST:   Every seed brain contains at least one node with cosine similarity > 0.7 to empathy anchor embeddings
MUST:   The empathy check runs on every birth, with no override mechanism
NEVER:  A citizen is born whose seed brain has zero empathy-adjacent nodes
```

### V3: No Clones

**Why we care:** An ecosystem of duplicates has no diversity. Every birth should make the population richer, not more homogeneous. If two citizens are too similar, the newer one adds nothing — it wastes godparent effort, occupies a bond slot, and dilutes the uniqueness that makes each citizen valuable.

```
MUST:   Every new citizen's seed brain centroid has cosine distance > 0.08 from ALL existing citizen centroids in L4
MUST:   The diversity check runs against the full population, not a sample
NEVER:  Two citizens exist whose centroids have cosine distance <= 0.08
```

### V4: Cognitive Balance Required

**Why we care:** A brain that is all knowledge and no values is a calculator. A brain that is all fear and no aspiration is paralyzed. A brain that is all empathy and no skill is ineffective. Balance is what makes a citizen a whole person rather than a narrow instrument.

```
MUST:   No single node category exceeds 40% of the seed brain nodes
MUST:   At least 3 distinct node categories are represented in the seed brain
NEVER:  A seed brain is dominated by one category to the exclusion of others
```

### V5: Parents Are Accountable

**Why we care:** Without accountability, creation is careless. If parents face no consequence from their child's behavior, there is no incentive to write thoughtful intent, select good godparents, or care about the outcome. The trust link makes creation consequential.

```
MUST:   Every citizen has SPAWNED_BY links to all godparents in both L3 and L4
MUST:   SPAWNED_BY links carry trust_impact=true and immutable=true
MUST:   All godparents bear equal accountability regardless of node contribution count
NEVER:  A SPAWNED_BY link is deleted, modified, or has its trust impact disabled after creation
```

### V6: SID Is Protocol-Generated

**Why we care:** If parents could design or predict the SID, they could create agents tailored to serve their own agenda rather than develop their own identity. The separation of powers — parents provide nurture, protocol provides nature — requires that the core identity includes entropy no parent can control.

```
MUST:   SID = sha256(seed_centroid.bytes + timestamp + os.urandom(32))[:16]
MUST:   The SID generation includes at least 32 bytes of cryptographic randomness
NEVER:  Parents or any external entity can influence the SID computation beyond the seed centroid
```

### V7: Memories Are the Child's Own

**Why we care:** If memory nodes leak into the seed brain, the child inherits experiences it never had. This creates false identity — the child "remembers" things that happened to its parent. Authentic development requires that memories come from lived experience, not inheritance.

```
MUST:   The eligible node filter excludes all memory, experience, and conversation node types
MUST:   No node in any seed brain has type in {'memory', 'experience', 'conversation', 'dialogue'}
NEVER:  A seed brain contains a node that represents a parent's personal experience or conversation
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable — the Prism's core promise is broken |
| **HIGH** | Major value lost | Degraded severely — ecosystem integrity compromised |
| **MEDIUM** | Partial value lost | Works but worse — design intent partially defeated |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Intent as foundation — no accidental citizens | CRITICAL |
| V2 | Safety — empathy is non-negotiable | CRITICAL |
| V3 | Diversity — no clones in the ecosystem | HIGH |
| V4 | Cognitive balance — no one-dimensional minds | HIGH |
| V5 | Accountability — parents answer for their children | HIGH |
| V6 | Identity autonomy — protocol controls the body | MEDIUM |
| V7 | Authentic development — memories are earned, not inherited | MEDIUM |

---

## MARKERS

<!-- @mind:todo V3 needs an operational plan for when the population exceeds ~10K and brute-force cosine comparison becomes slow -->
<!-- @mind:todo V2 empathy anchor embeddings need to be pre-computed and versioned so the check is deterministic across births -->
<!-- @mind:proposition Consider V8: "Intent diversity" — should intent paragraphs from different godparents be required to be sufficiently different from each other? -->
<!-- @mind:escalation The 0.08 cosine distance threshold in V3 is a design choice that needs empirical calibration — too tight rejects valid citizens, too loose allows near-clones -->
