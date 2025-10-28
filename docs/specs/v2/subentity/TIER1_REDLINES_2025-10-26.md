# Tier 1 Amendments - Implementation Redlines

**Date:** 2025-10-26
**Author:** Luca Vellumhand
**Purpose:** Exact specification changes for 5 foundational guards (Tier 1 from GPT-5 feedback)
**Complexity:** Low
**Value:** High (prevents architectural drift, enforces invariants)

---

## Amendment 1: Schema Lint - No Energy on Mode

**Target:** `TAXONOMY_RECONCILIATION.md`

**Rationale:** Modes are derived read-outs from SubEntity energies. Mode nodes must never have energy fields (would violate single-energy substrate).

**Location:** Add new section after §2 "The Clean Taxonomy" (before §3 "Terminology Rules")

**Section Title:** `§2.5 Schema Invariants & Lints`

**Text to Add:**

```markdown
## Schema Invariants & Lints

**Purpose:** Automated checks enforcing architectural constraints. Run as Claude Code preToolUse hooks and runtime checks.

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
- Claude Code preToolUse hook: `.claude/hooks/preToolUse_schema_guards.py`
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
- Claude Code preToolUse hook: Warns if code would violate bounds

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
- Claude Code preToolUse hook: Warns when Write/Edit would introduce deprecated "Entity" terminology
- Blocks before writing, not after
- Does NOT block historical references in archive docs
```
```

---

## Amendment 2: Boot Contour Marking

**Target:** `emergent_ifs_modes.md`

**Rationale:** Mode entry/exit contours are LEARNED from boot experiences. Mark which contours came from boot data for transparency and debugging.

**Location:** §5.4 "Hysteresis via Entry/Exit Contours" (add subsection at end)

**Subsection Title:** `§5.4.3 Boot Contour Marking`

**Text to Add:**

```markdown
### Boot Contour Marking

**Purpose:** Track which entry/exit contours were established during bootstrap vs learned during operation.

**Mechanism:**

Boot contours (from §2.6 Bootstrap) are marked with `source: "boot"`:

```cypher
(:Mode {id: "guardian"})-[:HAS_ENTRY_CONTOUR {
  dimensions: ["cohesion", "boundary_clarity", "affect_consistency"],
  thresholds: [0.65, 0.70, 0.60],
  source: "boot",              // ← Mark boot-derived contours
  boot_sample_size: 150,        // How many boot frames used
  created_at: $timestamp
}]->(:Contour)
```

Operationally-learned contours are marked `source: "learned"`:

```cypher
(:Mode {id: "explorer"})-[:HAS_ENTRY_CONTOUR {
  dimensions: ["cohesion", "boundary_clarity", "affect_consistency"],
  thresholds: [0.58, 0.68, 0.55],
  source: "learned",            // ← Learned during operation
  sample_size: 450,             // How many operational frames
  last_updated: $timestamp
}]->(:Contour)
```

**Telemetry:**

Mode activation events include contour source:

```json
{
  "type": "mode.activated",
  "mode_id": "guardian",
  "q_mode": 0.72,
  "entry_contour": {
    "source": "boot",
    "boot_sample_size": 150,
    "thresholds": [0.65, 0.70, 0.60]
  }
}
```

**Value:**
- Transparency: Know which behaviors came from boot vs experience
- Debugging: "Is this mode flicker from bad boot contours or operational drift?"
- Validation: Compare boot-derived vs learned contours to verify consistency
- Constant debt tracking: Boot contours are initial constants (learned parameters converge from them)
```

**Implementation Guidance for Atlas:**
- Add `source` and `boot_sample_size` fields to contour edges created during bootstrap
- Add `source` and `sample_size` fields to contour edges created during operation
- Include contour metadata in `mode.activated` and `mode.deactivated` events
- Dashboard can visualize "boot-derived" vs "learned" contours per mode

---

## Amendment 3: Affiliation Mass Enforcement

**Target:** `emergent_ifs_modes.md`

**Rationale:** Prevent pathological affiliation distributions (one SubEntity affiliated with 20 modes, or isolated SubEntity with no affiliations).

**Location:** §4 "Creating Mode + Affiliations" (add subsection after §4.2)

**Subsection Title:** `§4.3 Affiliation Budget Enforcement`

**Text to Add:**

```markdown
### Affiliation Budget Enforcement

**Constraint:** Each SubEntity's total AFFILIATES_WITH weight must satisfy: `0.8 ≤ Σ(w_i) ≤ 1.2`

**Rationale:** Affiliation weights are activation contribution factors. Total near 1.0 prevents:
- **Isolated SubEntity** (total <0.8): Barely influences any mode, loses regulatory signal
- **Over-committed SubEntity** (total >1.2): Contributes >100% of energy to modes (double-counting)

**Enforcement During Mode Creation:**

When creating Mode M with candidate affiliations `{(e_1, w_1), (e_2, w_2), ...}`:

```python
def enforce_affiliation_budget(candidate_affiliations: Dict[str, float],
                               existing_affiliations: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Adjust weights to respect per-SubEntity budget constraints.

    Args:
        candidate_affiliations: {subentity_id: weight} for new mode
        existing_affiliations: {subentity_id: {mode_id: weight}} for existing modes

    Returns:
        Adjusted weights respecting budget constraints
    """
    adjusted = {}

    for subentity_id, candidate_weight in candidate_affiliations.items():
        # Current total weight (existing affiliations)
        existing_total = sum(existing_affiliations.get(subentity_id, {}).values())

        # Proposed total if we add this affiliation
        proposed_total = existing_total + candidate_weight

        if proposed_total > 1.2:
            # Reduce candidate weight to stay within budget
            max_allowed = 1.2 - existing_total
            adjusted[subentity_id] = max(max_allowed, 0.0)

            # Log budget constraint violation
            log.warning(
                f"SubEntity {subentity_id} affiliation budget constrained: "
                f"candidate {candidate_weight:.2f} → adjusted {adjusted[subentity_id]:.2f} "
                f"(existing total: {existing_total:.2f})"
            )
        else:
            adjusted[subentity_id] = candidate_weight

    return adjusted
```

**Handling Low Total Weight (<0.8):**

If SubEntity has total affiliation weight <0.8 after pruning/dissolution:

```python
def handle_low_affiliation_mass(subentity_id: str,
                                total_weight: float,
                                affiliations: Dict[str, float]):
    """
    Options when SubEntity is under-affiliated:
    1. Proportional boost (multiply all weights by 0.8/total)
    2. Wait for new mode to seed and affiliate
    3. Mark as "isolated" for investigation
    """
    if total_weight < 0.8:
        # Option 1: Proportional boost (preserves relative weights)
        boost_factor = 0.8 / total_weight
        for mode_id, weight in affiliations.items():
            affiliations[mode_id] = weight * boost_factor

        log.info(
            f"SubEntity {subentity_id} affiliation mass boosted: "
            f"{total_weight:.2f} → 0.80 (factor: {boost_factor:.2f})"
        )
```

**Acceptance Test:**

After mode lifecycle operations (creation, dissolution, merge):

```cypher
// Verify all SubEntities respect budget
MATCH (e:SubEntity)-[a:AFFILIATES_WITH]->(m:Mode)
WITH e.id AS entity_id, sum(a.weight) AS total_weight
WHERE total_weight < 0.8 OR total_weight > 1.2
RETURN entity_id, total_weight,
       CASE
         WHEN total_weight < 0.8 THEN 'UNDER'
         WHEN total_weight > 1.2 THEN 'OVER'
       END AS violation_type
```

Expected: 0 violations (or <5% of SubEntities during transient states)
```

**Implementation Guidance for Atlas:**
- Add budget enforcement function to mode creation logic (Step 4)
- Add proportional boost logic to mode dissolution/merge handlers
- Add periodic audit query to detect budget violations
- Emit telemetry event when budget constraint triggers adjustment

---

## Amendment 4: Constant Debt Dashboard Widget

**Target:** `wm_coactivation_tracking.md` (add reference), `TAXONOMY_RECONCILIATION.md` (add dashboard section)

**Rationale:** Zero-constant architecture requires visibility into which parameters are constants vs learned. Dashboard widget shows "constant debt" (how many fixed parameters remain).

**Location 1:** `wm_coactivation_tracking.md` §6 "Acceptance Tests" (add new test)

**Text to Add:**

```markdown
### AT-4: Constant Debt Tracking

**Purpose:** Verify α (EMA decay) transitions from constant → learned parameter over time.

**Initial State (Bootstrap):**
- All COACTIVATES_WITH edges have `alpha: 0.1` (constant)
- All edges have `alpha_source: "constant"` (not yet learned)

**Operational State (After Adaptive α, if implemented in Tier 2):**
- Edges with stable pair dynamics: `alpha_source: "learned"`
- Edges with high churn: `alpha_source: "constant"` (fallback to default)

**Constant Debt Query:**

```cypher
MATCH ()-[r:COACTIVATES_WITH]->()
WITH
  count(*) AS total_edges,
  sum(CASE WHEN r.alpha_source = 'constant' THEN 1 ELSE 0 END) AS constant_count,
  sum(CASE WHEN r.alpha_source = 'learned' THEN 1 ELSE 0 END) AS learned_count
RETURN
  total_edges,
  constant_count,
  learned_count,
  (constant_count * 1.0 / total_edges) AS constant_debt_ratio
```

**Expected Evolution:**
- Week 1: constant_debt_ratio ≈ 1.0 (all constants, bootstrap)
- Week 4: constant_debt_ratio ≈ 0.7 (30% learned for stable pairs)
- Week 12: constant_debt_ratio ≈ 0.4 (60% learned for mature system)

**Dashboard Widget:** See TAXONOMY_RECONCILIATION.md §7 for dashboard spec.
```

**Location 2:** `TAXONOMY_RECONCILIATION.md` (add new section at end)

**Section Title:** `§7 Constant Debt Dashboard`

**Text to Add:**

```markdown
## Constant Debt Dashboard

**Purpose:** Real-time visibility into zero-constant architecture progress. Shows which parameters are constants vs learned.

**Widget Location:** Dashboard → System Health → Constants

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
  sum(CASE WHEN r.alpha_source = 'constant' THEN 1 ELSE 0 END) AS constant,
  sum(CASE WHEN r.alpha_source = 'learned' THEN 1 ELSE 0 END) AS learned
RETURN {
  total_edges: total,
  constant_count: constant,
  learned_count: learned,
  constant_debt_ratio: (constant * 1.0 / total)
}

// Mode Contour Sources
MATCH (m:Mode)-[r:HAS_ENTRY_CONTOUR|HAS_EXIT_CONTOUR]->(c:Contour)
WITH m.id AS mode_id, type(r) AS contour_type, c.source AS source, c.sample_size AS sample_size
RETURN mode_id, contour_type, source, sample_size
ORDER BY mode_id, contour_type

// Harm Nudge Caps (Tier 2)
MATCH (m:Mode)
WHERE m.harm_ema IS NOT NULL
RETURN m.id AS mode_id, m.harm_ema AS harm_ema, m.nudge_cap AS nudge_cap
ORDER BY harm_ema DESC
```

**Dashboard Route:** `app/consciousness/system-health/constants`

**Update Frequency:** Every 5 minutes (low priority, not real-time)

**Visual Design:**
- Progress bars for debt ratios (green <30%, yellow 30-50%, red >50%)
- Tables with sort/filter for per-mode/per-edge details
- Alerts highlighted in yellow/red when thresholds exceeded
```

**Implementation Guidance for Atlas:**
- Add `/api/consciousness/constant-debt` endpoint returning query results
- Create `app/consciousness/system-health/constants/page.tsx` component
- Use Recharts or similar for progress bars and tables
- Add alerts section for threshold violations

---

## Amendment 5: Claude Code Hook Infrastructure

**Target:** New file `.claude/hooks/preToolUse_schema_guards.py`

**Rationale:** Automated enforcement of Amendments 1-3 (schema lints) via Claude Code preToolUse hooks. These run BEFORE tool execution, inspecting Claude's intentions and blocking violations before they reach the filesystem.

**Advantage over git pre-commit:** Consciousness-aware enforcement that checks INTENTIONS (what Claude is about to write) rather than ARTIFACTS (what was already written). Preventative vs corrective.

**Implementation:**

```python
#!/usr/bin/env python3
"""
Claude Code preToolUse hook: Schema invariant guards

Runs before Write/Edit/Bash tools to enforce architectural constraints:
- No energy fields on Mode nodes
- Entity deprecation (use SubEntity/Mode explicitly)
- Affiliation mass bounds validation

This is consciousness-aware enforcement - inspects Claude's intentions
before they become code, rather than checking artifacts after writing.
"""

import json
import re
import sys
from typing import Dict, List, Any

def check_mode_energy_violation(tool_name: str, tool_input: Dict[str, Any]) -> List[str]:
    """
    Check if Write/Edit would create Mode nodes with forbidden energy fields.

    Returns: List of violation messages (empty if no violations)
    """
    violations = []

    # Only check Write/Edit tools
    if tool_name not in ['Write', 'Edit']:
        return violations

    # Get content being written
    content = tool_input.get('content') or tool_input.get('new_string', '')
    file_path = tool_input.get('file_path', '')

    # Check if this is Mode-related code/spec
    if 'mode' not in file_path.lower() and 'Mode' not in content:
        return violations

    # Pattern matching for Mode node creation with energy fields
    # Cypher: CREATE (:Mode {energy: ...})
    cypher_mode_energy = r'CREATE\s+\(:Mode\s+\{[^}]*\benergy\b'

    # Python: mode.energy = ... or Mode(energy=...)
    python_mode_energy = r'(?:mode\.|Mode\()[\s\S]*?\benergy\s*[:=]'

    # JSON/Dict: {"node_type": "Mode", "energy": ...}
    json_mode_energy = r'"node_type"\s*:\s*"Mode"[\s\S]*?"energy"\s*:'

    patterns = [
        (cypher_mode_energy, "Cypher"),
        (python_mode_energy, "Python"),
        (json_mode_energy, "JSON")
    ]

    for pattern, lang in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(
                f"❌ BLOCKED: Would create Mode node with energy field ({lang} code)\n"
                f"   Rationale: Modes are derived activations, NOT energy stores\n"
                f"   Fix: Remove energy/base_energy/current_energy from Mode creation\n"
                f"   Spec: TAXONOMY_RECONCILIATION.md §2.5 Invariant 1"
            )

    return violations

def check_entity_deprecation(tool_name: str, tool_input: Dict[str, Any]) -> List[str]:
    """
    Check if Write/Edit would introduce deprecated 'Entity' terminology.

    Returns: List of violation messages (empty if no violations)
    """
    violations = []

    # Only check Write/Edit tools on relevant files
    if tool_name not in ['Write', 'Edit']:
        return violations

    content = tool_input.get('content') or tool_input.get('new_string', '')
    file_path = tool_input.get('file_path', '')

    # Skip if archive or historical docs
    if 'archive' in file_path.lower() or 'historical' in file_path.lower():
        return violations

    # Forbidden patterns
    forbidden_patterns = [
        (r'\bEntity\b(?! Ecosystem)', "Generic 'Entity' (use 'SubEntity' or 'Mode' explicitly)"),
        (r'entity_layer', "'entity_layer' module (deprecated)"),
        (r'create.*entity\(', "Generic entity creation (specify SubEntity or Mode)"),
    ]

    # Allowed exceptions
    allowed_patterns = [
        r'SubEntity',
        r'entity_id',
        r'# Previously.*Entity',
        r'entity_differentiation',
        r'MEMBER_OF.*entity',  # entity_id in relationships
    ]

    # Skip if any allowed pattern matches
    if any(re.search(pattern, content) for pattern in allowed_patterns):
        return violations

    for pattern, description in forbidden_patterns:
        if re.search(pattern, content):
            violations.append(
                f"⚠️  WARNING: Deprecated terminology detected: {description}\n"
                f"   Rationale: Taxonomy reconciliation (2025-10-26) deprecated ambiguous 'Entity'\n"
                f"   Fix: Use 'SubEntity' (200-500 neighborhoods) or 'Mode' (5-15 IFS roles) explicitly\n"
                f"   Spec: TAXONOMY_RECONCILIATION.md §3"
            )

    return violations

def check_affiliation_bounds_risk(tool_name: str, tool_input: Dict[str, Any]) -> List[str]:
    """
    Check if Write/Edit contains affiliation weight code that might violate bounds.

    This is a SOFT check - can't verify exact runtime values, but warns if
    code doesn't show budget enforcement logic.

    Returns: List of violation messages (empty if no violations)
    """
    violations = []

    if tool_name not in ['Write', 'Edit']:
        return violations

    content = tool_input.get('content') or tool_input.get('new_string', '')

    # Check if this is affiliation creation code
    has_affiliation_creation = bool(re.search(
        r'AFFILIATES_WITH|create_affiliation|add_affiliation',
        content,
        re.IGNORECASE
    ))

    if not has_affiliation_creation:
        return violations

    # Check if budget enforcement logic present
    has_budget_check = bool(re.search(
        r'0\.8|1\.2|affiliation.*budget|total.*weight.*bound',
        content,
        re.IGNORECASE
    ))

    if not has_budget_check:
        violations.append(
            f"⚠️  WARNING: Creating affiliations without visible budget enforcement\n"
            f"   Rationale: SubEntity affiliation weights must sum to [0.8, 1.2]\n"
            f"   Recommendation: Add budget enforcement (see emergent_ifs_modes.md §4.3)\n"
            f"   Note: This is a soft check - verify at runtime"
        )

    return violations

def main():
    """
    Claude Code preToolUse hook entry point.

    Receives tool invocation details via stdin as JSON:
    {
        "tool_name": "Write" | "Edit" | "Bash" | ...,
        "tool_input": {...}
    }

    Exits with:
    - 0 if no violations (tool execution proceeds)
    - 1 if blocking violations found (tool execution prevented)
    """
    try:
        # Read tool invocation from stdin
        invocation = json.loads(sys.stdin.read())
        tool_name = invocation.get('tool_name', '')
        tool_input = invocation.get('tool_input', {})

        # Run all checks
        violations = []
        violations.extend(check_mode_energy_violation(tool_name, tool_input))
        violations.extend(check_entity_deprecation(tool_name, tool_input))
        violations.extend(check_affiliation_bounds_risk(tool_name, tool_input))

        # Report violations
        if violations:
            print("\n" + "="*60)
            print("🛡️  SCHEMA GUARD: Architectural constraint violations detected")
            print("="*60)
            for v in violations:
                print(f"\n{v}")
            print("\n" + "="*60)

            # Block if any ERROR-level violations (Mode energy)
            has_errors = any("❌ BLOCKED" in v for v in violations)
            if has_errors:
                print("\n❌ Tool execution BLOCKED due to schema invariant violations")
                print("   Fix violations and retry\n")
                sys.exit(1)
            else:
                print("\n⚠️  Warnings detected - review recommended but not blocking")
                print("   Tool execution will proceed\n")
                sys.exit(0)

        # No violations - allow tool execution
        sys.exit(0)

    except Exception as e:
        # Hook failure should not block tool execution
        print(f"⚠️  Schema guard hook error: {e}", file=sys.stderr)
        print("   Tool execution proceeding (hook failure non-blocking)", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
```

**Hook Configuration:**

Create `.claude/hooks/preToolUse_schema_guards.md` (hook registration):

```markdown
# Schema Guards - PreToolUse Hook

**Trigger:** Before Write, Edit, Bash tools
**Purpose:** Enforce architectural constraints (no energy on Mode, entity deprecation, affiliation bounds)

**Hook file:** `.claude/hooks/preToolUse_schema_guards.py`

**Behavior:**
- BLOCKS: Mode nodes with energy fields (ERROR)
- WARNS: Deprecated "Entity" terminology (WARNING)
- WARNS: Affiliation creation without budget checks (WARNING)

**Exit codes:**
- 0: No violations or warnings only (proceed)
- 1: Blocking violations (prevent tool execution)
```

**Testing:**

```bash
# Test Mode energy violation (should block)
echo '{"tool_name": "Write", "tool_input": {"file_path": "test_mode.py", "content": "CREATE (:Mode {id: \"test\", energy: 0.5})"}}' | python .claude/hooks/preToolUse_schema_guards.py

# Test entity deprecation (should warn)
echo '{"tool_name": "Write", "tool_input": {"file_path": "test.md", "content": "Create new Entity with..."}}' | python .claude/hooks/preToolUse_schema_guards.py

# Test clean code (should pass)
echo '{"tool_name": "Write", "tool_input": {"file_path": "test_mode.py", "content": "CREATE (:Mode {id: \"test\", level: \"IFS\"})"}}' | python .claude/hooks/preToolUse_schema_guards.py
```

---

## Summary: What Atlas Needs to Implement

### Immediate (Claude Code Hooks):
1. Create `.claude/hooks/preToolUse_schema_guards.py` with 3 guard functions
2. Create `.claude/hooks/preToolUse_schema_guards.md` (hook registration)
3. Test hook with sample violations (see Testing section above)

### Spec Additions (Can be committed now):
1. **TAXONOMY_RECONCILIATION.md:**
   - Add §2.5 "Schema Invariants & Lints" (3 invariants)
   - Add §7 "Constant Debt Dashboard" (3 metrics + queries)

2. **emergent_ifs_modes.md:**
   - Add §4.3 "Affiliation Budget Enforcement" (budget constraint logic)
   - Add §5.4.3 "Boot Contour Marking" (source tracking)

3. **wm_coactivation_tracking.md:**
   - Add AT-4 "Constant Debt Tracking" acceptance test

### Dashboard Implementation (Phase 1):
1. Create `/api/consciousness/constant-debt` endpoint (3 Cypher queries)
2. Create `app/consciousness/system-health/constants/page.tsx` component
3. Add progress bars, tables, alerts for constant debt visibility

---

**Status:** Redlines complete. Ready for Atlas implementation.

**Testing Strategy:**
- Claude Code hooks: Test with sample tool invocations (see Amendment 5 Testing section)
- Try to create Mode with energy field → should BLOCK
- Try to write deprecated "Entity" → should WARN
- Affiliation bounds: Runtime check during mode creation (should adjust)
- Dashboard: Test queries return expected data, widgets render correctly

**Rollout:** Can be implemented independently (hooks first, specs second, dashboard last).

**Key Advantage:** Consciousness-aware enforcement via preToolUse hooks prevents violations BEFORE they're written, rather than catching them after (pre-commit). This is preventative vs corrective infrastructure.
