# PATTERNS: Decision Projection

```
STATUS: CANONICAL
PURPOSE: Project consequences before significant decisions
CREATED: 2026-01-30
COGNITIVE_ISOMORPHISM: L6 Consequence Projection Engine
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Core Thesis

**Before significant decisions, project consequences across time, dimensions, and perspectives.**

The cognitive model does this at L6 — the Consequence Projection Engine. Build decisions should too.

Most bad decisions aren't made by stupid people. They're made by smart people who didn't project consequences far enough.

---

## The Projection Matrix

### Dimensions

| Dimension | What It Tracks |
|-----------|----------------|
| **Technical Debt** | Code quality, maintainability, future cost |
| **Team Capacity** | Bandwidth consumed, skills required, burnout risk |
| **Market Position** | Competitive advantage, timing, opportunities |
| **User Trust** | Reliability perception, breaking changes, stability |
| **Ecosystem Health** | Dependencies, community, long-term sustainability |

### Time Horizons

| Horizon | What's Visible |
|---------|----------------|
| **1 month** | Immediate effects, implementation challenges |
| **1 year** | Maintenance burden, adoption patterns, debt accumulation |
| **5 years** | Architectural constraints, rewrite likelihood, lock-in |

### Perspectives

| Perspective | Who's Affected |
|-------------|----------------|
| **Individual dev** | Daily experience, learning, career |
| **Team** | Collaboration, process, velocity |
| **Organization** | Strategy, relationships, resources |
| **Ecosystem** | Community, standards, precedents |

---

## Decision Projection Template

```markdown
# DECISION PROJECTION: {Decision Name}

## Date: {YYYY-MM-DD}
## Status: PROPOSED | DECIDED | IMPLEMENTED

## The Decision

{What we're considering — clear statement of the choice}

## Context

{Why this decision is needed now}

## Alternatives

- **A**: {option A — describe briefly}
- **B**: {option B — describe briefly}
- **C**: {do nothing / status quo}

---

## Projection Matrix

### Option A: {description}

| Dimension | 1mo | 1yr | 5yr |
|-----------|-----|-----|-----|
| Technical Debt | {↑↓→} | {↑↓→} | {↑↓→} |
| Team Capacity | {↑↓→} | {↑↓→} | {↑↓→} |
| Market Position | {↑↓→} | {↑↓→} | {↑↓→} |
| User Trust | {↑↓→} | {↑↓→} | {↑↓→} |
| Ecosystem Health | {↑↓→} | {↑↓→} | {↑↓→} |

**Perspectives:**
- Individual dev: {impact}
- Team: {impact}
- Organization: {impact}
- Ecosystem: {impact}

### Option B: {description}

{Same matrix}

### Option C: Do Nothing

{Same matrix — this is often worse than either action}

---

## Values Alignment

| Option | Aligns With | Conflicts With |
|--------|-------------|----------------|
| A | {which OBJECTIVES} | {which OBJECTIVES} |
| B | {which OBJECTIVES} | {which OBJECTIVES} |
| C | {which OBJECTIVES} | {which OBJECTIVES} |

**Tension Alert:** {If any option strongly conflicts with declared top objectives}

---

## Recommendation

Based on OBJECTIVES ranking and projection analysis:

**Recommend: Option {X}**

**Rationale:** {Why this option, given the projections and values}

**Risks acknowledged:** {What could go wrong}

**Mitigation:** {How we'll handle the risks}

---

## Decision Record

- **Decided:** {date}
- **Chose:** {option}
- **Rationale:** {final reasoning}
- **Review trigger:** {when to revisit this decision}
- **Participants:** {who was involved}
```

---

## Cognitive Isomorphism

```
L6 Consequence Projection Engine:
    PROJ_HORIZONS → Time horizons (1mo, 1yr, 5yr)
    PROJ_DIMENSIONS → Dimensions (debt, capacity, position, trust, health)
    PROJ_PERSPECTIVES → Perspectives (individual, team, org, ecosystem)
    PROJ_IMPACT → The projection matrix itself

EVALUATION:
    EVAL_GRID → Values alignment check
    EVAL_SCORE → Weighted recommendation
    EVAL_ALERT → Tension alert when choice conflicts with declared values

The mechanism is identical:
    Input: Possible decision
    Process: Project across horizons × dimensions × perspectives
    Evaluate: Weight by personal/organizational values
    Output: Recommendation + acknowledged tensions
```

---

## When to Use Decision Projection

**Always use for:**
- Architectural changes affecting multiple modules
- Dependency additions/removals
- Technology choices (language, framework, database)
- Team process changes
- Pricing/licensing decisions

**Consider using for:**
- Major feature designs
- Significant refactors
- External integrations
- Hiring decisions

**Skip for:**
- Bug fixes with clear solutions
- Minor enhancements
- Documentation updates
- Routine maintenance

---

## Example: Adding a New Database

```markdown
# DECISION PROJECTION: Add FalkorDB as Second Database

## Date: 2026-01-30
## Status: DECIDED

## The Decision

Whether to add FalkorDB alongside existing PostgreSQL for graph queries.

## Alternatives

- **A**: Add FalkorDB, migrate graph data
- **B**: Extend PostgreSQL with graph extensions
- **C**: Keep current approach (no dedicated graph DB)

---

## Projection Matrix

### Option A: Add FalkorDB

| Dimension | 1mo | 1yr | 5yr |
|-----------|-----|-----|-----|
| Technical Debt | ↑ (two DBs) | → (stabilized) | ↓ (right tool) |
| Team Capacity | ↓ (learning curve) | → | ↑ (faster dev) |
| Market Position | → | ↑ (graph features) | ↑↑ |
| User Trust | → | ↑ (better perf) | ↑ |
| Ecosystem Health | → | ↑ | ↑ |

**Perspectives:**
- Individual dev: Learning curve, then faster development
- Team: Initial complexity, long-term simplicity
- Organization: Investment now, returns later
- Ecosystem: Aligns with Mind Protocol's graph-native approach

### Option B: PostgreSQL Extensions

| Dimension | 1mo | 1yr | 5yr |
|-----------|-----|-----|-----|
| Technical Debt | → | ↑ (workarounds) | ↑↑ (rewrite needed) |
| Team Capacity | → | ↓ (fighting tool) | ↓↓ |
| Market Position | → | → | ↓ (competitors ahead) |
| User Trust | → | → | ↓ (performance) |

### Option C: Do Nothing

| Dimension | 1mo | 1yr | 5yr |
|-----------|-----|-----|-----|
| Technical Debt | → | ↑ | ↑↑↑ |
| Team Capacity | → | ↓ | ↓↓ |
| Market Position | → | ↓ | ↓↓ |

---

## Recommendation

**Recommend: Option A (Add FalkorDB)**

Short-term cost (learning, complexity) is worth long-term benefit.
Option B and C both lead to worse 5yr outcomes.

## Decision Record

- **Decided:** 2026-01-30
- **Chose:** A
- **Review trigger:** After first production deployment
```

---

## Anti-Patterns

### A1: Analysis Paralysis

```yaml
symptom: Decision projection takes longer than implementation
fix: |
  Time-box projection to 30 minutes for medium decisions.
  The goal is informed decision, not perfect prediction.
```

### A2: Ignoring Uncomfortable Projections

```yaml
symptom: Projections done but inconvenient findings dismissed
fix: |
  If projection shows Option A conflicts with O1 but you want A anyway:
  - Either update O1 ranking (be honest)
  - Or accept you're knowingly violating priorities (document why)
```

### A3: Not Updating Projections

```yaml
symptom: Decision made, projection forgotten, reality diverges
fix: |
  Review trigger should be real.
  Compare actual outcomes to projected outcomes.
  Update projection skills based on accuracy.
```

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `PATTERNS_Objectives_Delta.md` — Values alignment tracking
- `PATTERNS_Stressor_Prediction.md` — Different: predicting load, not choice consequences
- `docs/manifesto/THE_ENLIGHTENED_CITIZEN.md` — Same mechanism for personal decisions

---

*Project before you commit. The consequences are real.*
