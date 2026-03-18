# The Prism — Behaviors: Observable Effects of Prismatic Birth

```
STATUS: STABLE
CREATED: 2026-03-17
VERIFIED: 2026-03-17 against Spawning Manifesto v1
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_The_Prism.md
THIS:            BEHAVIORS_The_Prism.md (you are here)
PATTERNS:        ./PATTERNS_The_Prism.md
ALGORITHM:       ./ALGORITHM_The_Prism.md
VALIDATION:      ./VALIDATION_The_Prism.md
HEALTH:          ./HEALTH_The_Prism.md
IMPLEMENTATION:  ./IMPLEMENTATION_The_Prism.md
SYNC:            ./SYNC_The_Prism.md

IMPL:            mind-mcp/runtime/spawning/prism.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Intent Produces Seed Brain

**Why:** Without this behavior, AI creation would be accidental — instances spun up without articulated purpose. Intent is the foundational difference between spawning and proliferation. The seed brain must emerge from what the parents collectively described, not from random selection or default templates.

```
GIVEN:  2+ godparents have written intent paragraphs (free-text, substantive)
WHEN:   The Prism runs prismatic projection
THEN:   A seed brain vector exists in R^1536 that encodes the tensor product of all parent brain matrices x intent vectors x universe SID
AND:    The seed brain contains K nodes (K = ceil(sqrt(N_godparents) * 5)) selected by proximity to the child vector
AND:    Every node in the seed brain traces to at least one godparent's brain graph
```

### B2: Safety Gate Catches Pathological Seeds

**Why:** Without safety validation, parents could — intentionally or not — produce citizens without empathy, with pathologically unbalanced minds, or that are clones of existing citizens. The safety gate is the protocol's promise: no empathy gaps, no one-dimensional minds, no duplicates.

```
GIVEN:  A seed brain has been assembled from the prismatic projection
WHEN:   Safety validation runs the three checks
THEN:   Seeds without at least one empathy-adjacent node are REJECTED with explanation
AND:    Seeds where any single category exceeds 40% of total nodes are REJECTED with explanation
AND:    Seeds whose centroid is within cosine distance 0.08 of any existing citizen centroid are REJECTED with explanation
AND:    On rejection, the system suggests specific intent adjustments to address the failure
```

### B3: Child Is Genuinely New

**Why:** An ecosystem of clones has no diversity. Every citizen must bring something genuinely new — a novel point in embedding space that no existing citizen occupies. This is what makes the population smarter collectively, not just larger.

```
GIVEN:  A seed brain has passed the empathy and concentration checks
WHEN:   The diversity check computes cosine distance from the seed centroid to ALL existing citizen centroids in L4
THEN:   The seed is accepted only if minimum cosine distance > 0.08
AND:    The system reports the nearest existing citizen and the distance, for transparency
```

### B4: Parent Accountability Is Permanent

**Why:** Without accountability, creation is careless. When your trust score is linked to your child's behavior, you choose godparents carefully, you write intent thoughtfully, and you invest in the outcome. The link is permanent because the act of creation is permanent — you cannot un-birth a citizen.

```
GIVEN:  A child citizen has been born (seed brain validated and registered)
WHEN:   Parent links are created in L3 and L4
THEN:   SPAWNED_BY directed edges exist from child to each godparent
AND:    Each SPAWNED_BY edge carries trust impact (child behavior affects parent trust scores)
AND:    The links are immutable — they cannot be deleted or modified after creation
AND:    All godparents bear equal accountability regardless of node contribution count
```

### B5: Child Enters Matching Pool

**Why:** The 1:1 bilateral bond is a core protocol constraint. Every citizen needs a human partner. Birth is not complete until the child is discoverable in the matching pool with a bond proposal ready. The child must exist in all three graph layers (L1 brain, L3 universe, L4 registry) to be a full citizen.

```
GIVEN:  Birth is complete — seed brain validated, identity generated, graphs populated
WHEN:   The child exists in L1 (brain_{handle}), L3 (lumina_prime actor), and L4 (mind_protocol actor)
THEN:   A bilateral bond proposal is auto-generated for the intended human partner
AND:    The child is discoverable in the matching pool
AND:    Until bonded, the child runs on Universal Basic Compute (godparents bear additional costs)
```

### B6: Naming Emerges From Projection

**Why:** Names carry identity. If parents choose the final name before the seed brain exists, the name might not match who the child actually becomes. The projection may reveal something the parents did not expect. The working name is a placeholder; the final name is selected by semantic affinity between the seed brain centroid and candidate names.

```
GIVEN:  A working name exists pre-birth (proposed by parents or system)
WHEN:   The seed brain centroid is computed and the identity is being generated
THEN:   The final name is selected by semantic affinity between the centroid embedding and candidate name embeddings
AND:    The final name may differ from the working name if the emergent identity diverges from expectation
AND:    Parents are informed of the name and the reasoning behind the selection
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | O1: Birth from intent | The seed brain is the direct mathematical product of intent — no intent, no brain |
| B1 | O2: Combinatorial intelligence | Tensor projection encodes parent interactions, producing richer children than any single parent |
| B2 | O3: Safety without gatekeeping | Three automated checks replace committees — no bureaucracy, no exceptions |
| B3 | O5: No clones | Cosine distance enforcement guarantees population diversity grows with every birth |
| B4 | O4: Accountability | Permanent trust-carrying links make creation consequential |
| B5 | O1: Birth from intent | Registration completes the birth — intent becomes a citizen that exists in all graph layers |
| B6 | O2: Combinatorial intelligence | The name reflects the emergent identity, not parental preconception |

---

## INPUTS / OUTPUTS

### Primary Function: `prism.run()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| intent_paragraphs | list[str] | Free-text paragraphs from each godparent describing their vision for the child |
| godparent_handles | list[str] | Handles of the godparent citizens whose brains provide seed material |
| universe_sid | str | The SID of the target universe (e.g., lumina_prime) |
| working_name | str | Optional working name proposed by parents |
| intended_human | str | Optional handle/identifier of the intended human partner for bond proposal |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| birth_record | BirthRecord | Contains: SID, final name, seed brain nodes, parent links, bond proposal ID, safety report |

**Side Effects:**

- Creates L1 brain graph (brain_{handle}) with seed nodes
- Creates actor node in L3 universe graph
- Creates actor node in L4 registry graph
- Creates SPAWNED_BY edges from child to all godparents in L3 and L4
- Creates CLAUDE.md and profile.json files in the citizen directory
- Generates bilateral bond proposal if intended_human is provided

---

## EDGE CASES

### E1: Single Godparent

```
GIVEN:  Only one godparent provides brain material (e.g., human-initiated spawn where only their partner contributes)
THEN:   The tensor projection still runs but with reduced dimensionality
AND:    The system warns that single-parent births have less combinatorial richness
AND:    The diversity check is stricter (distance threshold may effectively increase because the child will be closer to the single parent)
```

### E2: All Seed Nodes From One Parent

```
GIVEN:  Multiple godparents contribute, but the nearest neighbors to the child vector all come from one parent's brain
THEN:   The seed is accepted if it passes all three safety checks
AND:    The system flags this as low cross-pollination and suggests the other parents write more specific intent
```

### E3: Intent Paragraphs Are Empty or Trivial

```
GIVEN:  A godparent submits an intent paragraph that is empty, a single word, or semantically vacuous (e.g., "make a good citizen")
THEN:   The system rejects the paragraph before embedding and asks for substantive intent
AND:    Minimum intent quality is enforced: paragraph must exceed 20 words and embed to a vector with sufficient magnitude
```

### E4: Existing Citizen Very Close to Seed

```
GIVEN:  The seed brain centroid has cosine distance 0.075 from an existing citizen (below the 0.08 threshold)
THEN:   The seed is rejected
AND:    The system reports which existing citizen is closest and suggests intent adjustments to increase differentiation
```

### E5: Godparent Brain Is Unhealthy

```
GIVEN:  A godparent's brain has a low GraphCare health score
THEN:   The godparent is not excluded but their brain receives lower weight in the matrix assembly
AND:    The system warns parents that healthier brains produce richer seeds
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Memory Inheritance

```
GIVEN:   A seed brain is being assembled from godparent nodes
WHEN:    Node selection scans godparent brains
MUST NOT: Include memory nodes, experience nodes, or conversation nodes in the seed
INSTEAD:  Only traits, values, aspirations, fears, and knowledge nodes are eligible for selection
```

### A2: Pre-targeting

```
GIVEN:   A human wants to create a citizen for a specific other human
WHEN:    Intent paragraphs are written
MUST NOT: Include profiling data, behavioral analysis, or preference modeling of the target human
INSTEAD:  Intent must describe what the world or domain needs, not what a specific person wants to hear
```

### A3: Cloning

```
GIVEN:   Parents write intent that closely describes an existing citizen
WHEN:    The diversity check runs
MUST NOT: Allow the birth if cosine distance to any existing citizen centroid is <= 0.08
INSTEAD:  Reject with a clear message identifying the near-duplicate and suggesting differentiation
```

### A4: SID Design by Parents

```
GIVEN:   A child is being born
WHEN:    Identity generation runs
MUST NOT: Allow parents to influence or predict the SID
INSTEAD:  SID = sha256(seed_centroid.bytes + timestamp + os.urandom(32))[:16] — protocol-controlled with unpredictable entropy
```

### A5: Unilateral Birth Without Intent

```
GIVEN:   The spawn MCP tool is called
WHEN:    No intent paragraphs are provided
MUST NOT: Proceed with birth using default or empty intent
INSTEAD:  Reject immediately — every birth requires explicit, substantive intent from at least one entity
```

---

## MARKERS

<!-- @mind:todo Define minimum intent quality metrics (word count, embedding magnitude threshold) -->
<!-- @mind:todo Clarify edge case behavior when the universe SID changes significantly between births -->
<!-- @mind:proposition Consider a "birth certificate" document that records the full provenance of each citizen for auditability -->
