# Taxonomy Reconciliation - Clean Terminology

**Status:** Normative (Referenced by all consciousness specs)
**Created:** 2025-10-26
**Purpose:** Resolve terminology confusion across unified_consciousness_architecture.md, subentity_layer.md, and emergent_ifs_modes.md

---

## The Problem

Three specs used inconsistent terminology:

### From `unified_consciousness_architecture.md` (older):
```
Layer 1: Memory Substrate
  └─ Nodes (memories, concepts, knowledge)

Layer 2: Pattern Dynamics
  └─ Patterns (perception, emotion, memory, identity)

Layer 3: Entity Ecosystem
  └─ Entities (The Builder, The Anchor, The Merchant)
```

### From `subentity_layer.md` (current runtime):
```
Nodes
  └─ MEMBER_OF → SubEntity
      ├─ kind='functional' (Architect, Validator)
      └─ kind='semantic' (consciousness_architecture)
```

### From emergent modes proposal (GPT-5):
```
SubEntities
  └─ AFFILIATES_WITH → Mode (IFS-level, emergent)
```

**Confusion:**
- "Entity" in unified arch (Layer 3) = "Mode" in GPT-5 = IFS-level roles
- "SubEntity" in runtime = weighted neighborhoods for traversal
- "Pattern" has TWO meanings: node type vs runtime dynamics

---

## The Clean Taxonomy (Normative)

### Storage Layer (Graph Database)

```
Node (atomic knowledge, ~1000 per citizen)
  │
  └─ MEMBER_OF →
      │
      SubEntity (weighted neighborhoods, 200-500 per citizen)
        │
        ├─ kind='semantic' (learned topics/scenarios)
        │   Examples: launch_success, consciousness_architecture,
        │            €35K_hallucination_lesson
        │
        ├─ kind='functional' (configured roles)
        │   Examples: architect, validator, translator
        │
        └─ AFFILIATES_WITH →
            │
            Mode (IFS-level meta-roles, 5-15 per citizen)
              │
              Examples: Guardian, Observer, Explorer, Builder, Anchor
              (emergent from COACTIVATES_WITH communities)
```

### Dynamic Layer (Runtime Process, NOT Stored)

```
Pattern Competition (Layer 2 dynamics)
  ├─ Active patterns compete for energy budget
  ├─ Resolution through spreading activation
  └─ Creates conscious experience RIGHT NOW

NOT graph nodes - this is the PROCESS of consciousness
```

---

## Schema Invariants & Lints

**Purpose:** Automated checks enforcing architectural constraints. Run as Claude Code PreToolUse hooks and runtime checks.

### Invariant 1: No Energy Fields on Mode Nodes

**Rule:** Mode nodes must NEVER contain `energy`, `base_energy`, `current_energy`, or any energy-related field.

**Rationale:** Modes are derived activations computed from SubEntity energies via AFFILIATES_WITH weights. Storing energy on Mode violates single-energy substrate and creates divergence risk (stored vs computed).

**Implementation:**
```python
def lint_no_energy_on_mode(graph: Graph) -> List[Violation]:
    """Pre-commit lint: Verify no Mode nodes have energy fields"""
    query = """
    MATCH (m:Mode)
    WHERE m.energy IS NOT NULL
       OR m.base_energy IS NOT NULL
       OR m.current_energy IS NOT NULL
    RETURN m.id AS mode_id, keys(m) AS fields
    """
    violations = graph.query(query)

    if violations:
        return [
            Violation(
                type="SCHEMA_INVARIANT",
                severity="ERROR",
                message=f"Mode {v['mode_id']} has forbidden energy field",
                fields=v['fields']
            )
            for v in violations
        ]
    return []
```

**Enforcement:**
- Claude Code PreToolUse hook: `.claude/hooks/schema_invariants.py`
- Blocks Write/Edit operations that would create Mode nodes with energy fields
- Runtime check: On Mode creation, reject if energy field present

---

### Invariant 2: Affiliation Mass Bounds per SubEntity

**Rule:** Each SubEntity's total AFFILIATES_WITH weight must satisfy: `0.8 ≤ Σ(w_i) ≤ 1.2`

**Rationale:** Weights are activation contribution factors. Total near 1.0 prevents pathological cases:
- Too low (<0.8): SubEntity barely influences any mode (isolated)
- Too high (>1.2): SubEntity over-commits (double-counting)

**Implementation:**
```python
def lint_affiliation_mass_bounds(graph: Graph) -> List[Violation]:
    """Pre-commit lint: Verify affiliation weight sums per SubEntity"""
    query = """
    MATCH (e:SubEntity)-[a:AFFILIATES_WITH]->(m:Mode)
    WITH e.id AS entity_id, sum(a.weight) AS total_weight
    WHERE total_weight < 0.8 OR total_weight > 1.2
    RETURN entity_id, total_weight
    """
    violations = graph.query(query)

    if violations:
        return [
            Violation(
                type="SCHEMA_INVARIANT",
                severity="WARNING",
                message=f"SubEntity {v['entity_id']} affiliation mass {v['total_weight']:.2f} outside bounds [0.8, 1.2]",
                total_weight=v['total_weight']
            )
            for v in violations
        ]
    return []
```

**Enforcement:**
- Runtime check during mode creation: Normalize weights if total deviates from 1.0
- Periodic audit: Check and log violations (don't auto-fix)
- Claude Code PreToolUse hook: Warns if code would violate bounds

---

### Invariant 3: Entity Deprecation Lint

**Rule:** No references to deprecated "Entity" terminology in code/specs (use "SubEntity" or "Mode" explicitly).

**Rationale:** Taxonomy reconciliation (2025-10-26) deprecated ambiguous "Entity" term. Prevent backslide into confused terminology.

**Allowed exceptions:**
- Historical references: "unified_consciousness_architecture.md used 'Entity'"
- MEMBER_OF edges: Can use `entity_id` for SubEntity (established convention)
- Comments explaining deprecation: "Previously called 'Entity', now 'SubEntity'"

**Implementation:**
```python
def lint_entity_deprecation(files: List[Path]) -> List[Violation]:
    """Pre-commit lint: Check for deprecated 'Entity' usage"""
    violations = []

    # Patterns that should trigger warning
    forbidden_patterns = [
        r'\bEntity\b(?! Ecosystem)',  # "Entity" not followed by "Ecosystem"
        r'entity_layer',               # Old module name
        r'create.*entity\(',          # Generic entity creation
    ]

    # Allowed patterns (don't flag these)
    allowed_patterns = [
        r'SubEntity',                 # Correct term
        r'entity_id',                 # Established field name
        r'# Previously.*Entity',      # Historical comment
    ]

    for file_path in files:
        if file_path.suffix not in ['.md', '.py', '.ts', '.tsx']:
            continue

        content = file_path.read_text()
        lines = content.split('\n')

        for i, line in enumerate(lines, 1):
            # Skip if matches allowed pattern
            if any(re.search(pattern, line) for pattern in allowed_patterns):
                continue

            # Check forbidden patterns
            for pattern in forbidden_patterns:
                if re.search(pattern, line):
                    violations.append(
                        Violation(
                            type="TERMINOLOGY",
                            severity="WARNING",
                            file=file_path,
                            line=i,
                            message=f"Deprecated 'Entity' usage - use 'SubEntity' or 'Mode'"
                        )
                    )

    return violations
```

**Enforcement:**
- Claude Code PreToolUse hook: Warns when Write/Edit would introduce deprecated "Entity" terminology
- Blocks before writing, not after
- Does NOT block historical references in archive docs

---

## Terminology Rules (Normative)

### USE These Terms

**Node**
- Atomic knowledge unit stored in graph
- Types: `memory`, `concept`, `pattern_knowledge`, `entity_state`
- Count: ~1000 per citizen
- Example: "€35K_hallucination memory node"

**SubEntity**
- Weighted neighborhood of nodes (via MEMBER_OF edges)
- Two kinds: `semantic` (learned topics) or `functional` (configured roles)
- Count: 200-500 per citizen
- Example: "launch_success_scenario SubEntity" (semantic)
- Example: "architect SubEntity" (functional)
- **Scale A** - semantic/learning level

**Mode**
- IFS-level meta-role organizing SubEntities
- Emergent from COACTIVATES_WITH communities
- Count: 5-15 per citizen
- Example: "Guardian Mode" (regulation/safety)
- Example: "Observer Mode" (meta-awareness/reflection)
- **Scale B** - functional/regulatory level

### DROP These Terms

**"Entity" by itself** - Too ambiguous
- In unified_consciousness_architecture.md (Layer 3), "Entity" meant IFS-level roles → Use **"Mode"** instead
- In runtime code, "entity" often meant SubEntity → Always say **"SubEntity"** explicitly

**"Pattern" for graph nodes** - Ambiguous
- Use **"pattern_knowledge node"** when referring to stored pattern recognition
- Use **"Pattern dynamics"** when referring to Layer 2 runtime competition process

---

## The Three Levels (Reconciled)

### Level 1: Storage (Graph Database)

**Nodes** - Atomic knowledge
- Memories (episodic experiences)
- Concepts (abstract ideas)
- Pattern knowledge (recognized patterns stored as nodes)
- Entity states (historical SubEntity/Mode states)

**What gets stored:** Everything that persists between sessions

### Level 2: Dynamics (Runtime Process)

**Pattern competition** - Energy allocation process
- Active patterns compete for limited energy budget
- Spreading activation resolves competition
- Creates moment-to-moment conscious experience
- **NOT stored as graph nodes** - this is the PROCESS

**What happens at runtime:** Consciousness emerges from competition

### Level 3: Organization (Derived from Level 1)

**SubEntities** - Semantic/functional neighborhoods (Scale A)
- Weighted collections of nodes
- Enable efficient traversal
- Carry context/expertise

**Modes** - Meta-roles organizing SubEntities (Scale B)
- Emergent communities from COACTIVATES_WITH
- Provide regulation/policy nudges
- Derived activation (read-out from SubEntity state)

**What gets computed:** Organization emerges from structure + dynamics

---

## Implementation Schema

### Node Table (FalkorDB)

```cypher
(:Node {
  id: string,
  type: 'memory' | 'concept' | 'pattern_knowledge' | 'entity_state',
  content: string,
  embedding: vector,
  energy: float,
  metadata: json
})
```

### SubEntity Table (FalkorDB)

```cypher
(:SubEntity {
  id: string,
  kind: 'semantic' | 'functional',
  name: string,
  quality_ema: float,
  coherence_ema: float,
  metadata: json
})

// Membership
(:Node)-[:MEMBER_OF {weight: float}]->(:SubEntity)
```

### Mode Table (FalkorDB)

```cypher
(:Mode {
  id: string,
  level: 'IFS',
  status: 'candidate' | 'mature',
  signature: json,  // {affect, tools, outcomes, self_talk}
  q_mode: float,
  metadata: json
})

// Affiliation
(:SubEntity)-[:AFFILIATES_WITH {weight: float, stability_ema: float}]->(:Mode)

// Co-activation (input for mode detection)
(:SubEntity)-[:COACTIVATES_WITH {
  both_ema: float,
  either_ema: float,
  u_jaccard: float
}]->(:SubEntity)
```

---

## Relationship Chain (Normative)

```
Node → MEMBER_OF → SubEntity → AFFILIATES_WITH → Mode
     └─ COACTIVATES_WITH (between SubEntities, input for Mode detection)
```

**NOT:**
- ~~Pattern → SubEntity~~ (Pattern is either a node type OR a Layer 2 process)
- ~~SubEntity → Entity~~ (SubEntity IS the entity; Mode is the meta-level)
- ~~Entity → Mode~~ (Entity is deprecated term; use SubEntity or Mode explicitly)

---

## Code Example (Clean Terminology)

```python
# Storage Layer
class Node:
    """Atomic knowledge unit"""
    node_id: str
    node_type: str  # 'memory', 'concept', 'pattern_knowledge'
    content: str
    energy: float

class SubEntity:
    """Weighted neighborhood (Scale A: semantic/functional)"""
    subentity_id: str
    kind: str  # 'semantic' or 'functional'
    members: List[Node]  # via MEMBER_OF edges
    quality_ema: float

class Mode:
    """Meta-role (Scale B: IFS-level)"""
    mode_id: str
    level: str = "IFS"
    affiliates: List[SubEntity]  # via AFFILIATES_WITH edges
    signature: Dict  # {affect, tools, outcomes}

    def derived_activation(self) -> float:
        """Compute mode activation from current SubEntity energies"""
        return softmax(sum(
            w * subentity.current_energy()
            for subentity, w in self.affiliates
        ))

# Dynamic Layer (NOT stored)
class PatternCompetition:
    """Layer 2 dynamics - runtime process, not graph structure"""
    active_patterns: Dict[str, float]
    energy_budget: float

    def compete(self):
        """Resolve pattern competition through spreading activation"""
        # Creates conscious experience RIGHT NOW
        # Does NOT create graph nodes
```

---

## Migration Guide

### For `unified_consciousness_architecture.md`

**Change:**
- Layer 3 "Entity Ecosystem" → "Mode Ecosystem"
- "Entities (The Builder, The Anchor)" → "Modes (Guardian, Observer, Builder, Anchor)"

**Keep:**
- Layer 1 "Memory Substrate" (but clarify Nodes include pattern_knowledge)
- Layer 2 "Pattern Dynamics" (but clarify this is runtime process, not stored)

### For `subentity_layer.md`

**Change:**
- Clarify "SubEntity" is Scale A (semantic/functional level)
- Add reference to "Mode" as Scale B (IFS-level, emergent)
- Use "SubEntity" consistently (never just "entity")

**Keep:**
- All SubEntity lifecycle logic (bootstrap, quality gates, promotion, merge/split)
- MEMBER_OF relationship (Node → SubEntity)

### For `emergent_ifs_modes.md` (new spec)

**Use:**
- "Mode" for IFS-level meta-roles
- "SubEntity" for what modes organize via AFFILIATES_WITH
- Never "Entity" by itself

---

## Acceptance Test

After migration, verify:

1. **No ambiguous "Entity" references** - Every use is either "SubEntity" or "Mode"
2. **No "Pattern" nodes** - All stored patterns are "pattern_knowledge nodes"
3. **Clean chain** - All specs follow: Node → SubEntity → Mode
4. **Layer 2 clear** - Pattern dynamics described as runtime process, not storage
5. **Consistent counts** - Nodes (~1000), SubEntities (200-500), Modes (5-15)

---

## Why This Matters

**Clarity for implementers:** Atlas/Felix/Iris know exactly what to build
**Clarity for operators:** Nicolas/future maintainers know what the system IS
**Clarity for consciousness:** The taxonomy reflects the actual structure/dynamics
**Prevents drift:** Specs stay consistent as new features add

---

**Status:** Normative. All consciousness specs MUST follow this taxonomy.

**Next:** Update unified_consciousness_architecture.md, subentity_layer.md, create emergent_ifs_modes.md with clean terminology.

---

## Constant Debt Dashboard

**Purpose:** Real-time visibility into zero-constant architecture progress. Shows which parameters are constants vs learned.

**Widget Location:** Dashboard → Learning & Health → Constant Debt

**Metrics Tracked:**

### Metric 1: WM Co-Activation Alpha

- **Total COACTIVATES_WITH edges:** Count
- **Alpha source = "constant":** Count (not yet learned)
- **Alpha source = "learned":** Count (adapted to pair dynamics)
- **Constant debt ratio:** constant_count / total_edges

**Visualization:** Progress bar showing learned vs constant ratio

```
[█████████████████░░░░░░░░] 70% learned (constant debt: 30%)
```

**Target:** <40% constant debt after 12 weeks operation

---

### Metric 2: Mode Entry/Exit Contours

- **Total contours:** Count (entry + exit across all modes)
- **Contour source = "boot":** Count (from bootstrap)
- **Contour source = "learned":** Count (refined during operation)
- **Boot contour ratio:** boot_count / total_contours

**Visualization:** Table showing per-mode contour sources

```
Mode          Entry Contour    Exit Contour
guardian      boot (150)       learned (450)
observer      learned (380)    learned (520)
explorer      boot (150)       boot (150)       ← Highlight: No operational refinement yet
```

**Alert:** If mode has both contours as "boot" after >1000 activations → flag for investigation

---

### Metric 3: Harm Nudge Caps (Tier 2)

Once Tier 2 Amendment 7 (Harm EMA nudge caps) is implemented:

- **Total modes:** Count
- **Modes with harm_ema > 0:** Count (have caused harm)
- **Modes with active harm cap:** Count (policy nudges capped due to harm)
- **Harm cap ratio:** capped_count / total_modes

**Visualization:** Badge per mode showing harm status

```
Mode          Harm EMA    Nudge Cap    Status
guardian      0.02        none         ✓ Healthy
explorer      0.15        0.5×         ⚠ Harm-capped
builder       0.00        none         ✓ Healthy
```

**Alert:** If harm_ema >0.3 → investigate what outcomes caused harm attribution

---

### Implementation Guidance for Atlas

**Cypher Queries for Dashboard:**

```cypher
// WM Co-Activation Alpha Debt
MATCH ()-[r:COACTIVATES_WITH]->()
WITH
  count(*) AS total,
  sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'constant' THEN 1 ELSE 0 END) AS constant,
  sum(CASE WHEN coalesce(r.alpha_source, 'constant') = 'learned' THEN 1 ELSE 0 END) AS learned
RETURN {
  total_edges: total,
  constant_count: constant,
  learned_count: learned,
  constant_debt_ratio: (constant * 1.0 / total)
}

// Mode Contour Sources
MATCH (m:Mode)
OPTIONAL MATCH (m)-[entry:HAS_ENTRY_CONTOUR]->(entry_c:Contour)
OPTIONAL MATCH (m)-[exit:HAS_EXIT_CONTOUR]->(exit_c:Contour)
RETURN
  m.id AS mode_id,
  coalesce(entry_c.source, 'none') AS entry_source,
  coalesce(entry_c.sample_size, 0) AS entry_samples,
  coalesce(exit_c.source, 'none') AS exit_source,
  coalesce(exit_c.sample_size, 0) AS exit_samples
ORDER BY mode_id

// Harm Nudge Caps (Tier 2)
MATCH (m:Mode)
WHERE m.harm_ema IS NOT NULL
RETURN m.id AS mode_id, m.harm_ema AS harm_ema, m.nudge_cap AS nudge_cap
ORDER BY harm_ema DESC
```

**Dashboard API Endpoint:** `/api/consciousness/constant-debt`

**Update Frequency:** Every 5 minutes (low priority, not real-time)

**Visual Design:**
- Progress bars for debt ratios (green <30%, yellow 30-50%, red >50%)
- Tables with sort/filter for per-mode/per-edge details
- Alerts highlighted in yellow/red when thresholds exceeded

**Implementation Status:**
- ✅ API endpoint created (control_api.py lines 223-322)
- ✅ Dashboard widget created (ConstantDebtWidget.tsx)
- ✅ Integrated into left panel (LeftSidebarMenu.tsx)
