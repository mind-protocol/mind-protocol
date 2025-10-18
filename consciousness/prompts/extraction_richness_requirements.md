# Extraction Richness Requirements

## Core Principle: Titre + Description Complète

**Every node needs TWO parts:**
1. **`name`** - Short identifier (5-8 words max)
2. **`description`** - Complete multi-paragraph explanation

**No terse descriptions. No single sentences. Full context always.**

---

## Minimum Description Lengths by Node Type

| Node Type | Min Chars | Min Sentences | Must Answer |
|-----------|-----------|---------------|-------------|
| **Decision** | 500 | 6-8 | Problem? Why this? Alternatives (3+)? Trade-offs? Consequences? |
| **Best_Practice** | 400 | 5-7 | What to do? Why it works? Validation criteria? How to apply? |
| **Principle** | 400 | 5-7 | Principle statement? Why matters? Examples? How to apply? |
| **Realization** | 300 | 4-6 | What realized? Context? Why significant? Implications? |
| **Memory** | 300 | 4-6 | What happened? Who present? Emotional significance? Learning? |
| **Anti_Pattern** | 400 | 5-7 | What failed? Why failed? Cost paid? How to avoid? |
| **Risk** | 300 | 4-5 | Threat? Impact? Probability? Mitigation? |
| **Pattern** | 300 | 4-5 | Behavior? Triggers? Frequency? Why it matters? |
| **Task** | 200 | 3-4 | What needs doing? Why? Context? Acceptance criteria? |
| **All Others** | 150 | 3+ | What is it? Why matters? Context? |

---

## Required Fields by Type (Beyond Base Schema)

**Decision:**
- `rationale` (required) - Why this decision over alternatives
- `alternatives_considered` (required, min 3 items) - What else was evaluated
- `validation_status` (required) - theoretical/tested/proven

**Best_Practice:**
- `how_to_apply` (required) - Concrete steps to use this
- `validation_criteria` (required) - How to know if working

**Anti_Pattern:**
- `what_failed` (required) - Specific failure
- `cost_paid` (required) - Consequences experienced
- `how_to_avoid` (required) - Prevention guidance

**Realization:**
- `what_i_realized` (required) - The insight
- `context_when_discovered` (required) - Situation that triggered it

**Memory:**
- `what_happened` (required) - The event
- `participants` (required) - Who was there
- `emotional_impact` (required) - How it felt

---

## Description Structure Template

```
[CONTEXT - 1-2 sentences]
Brief setup of the situation or problem.

[CORE CONTENT - 3-5 sentences]
The main substance: what is it, why it exists, how it works.

[SIGNIFICANCE - 1-2 sentences]
Why this matters, what it enables, consequences.
```

**For Decision nodes, add:**
```
ALTERNATIVES CONSIDERED:
1. Option A - why rejected
2. Option B - why rejected
3. Option C - why rejected

TRADE-OFFS ACCEPTED:
- Downside 1 we accepted
- Downside 2 we accepted
```

---

## Validation Checklist (Self-Check Before Extraction)

Before calling add-cluster, verify:

- [ ] Every node has `description` ≥ minimum length for its type
- [ ] Decision nodes list ≥ 3 alternatives considered
- [ ] Decision nodes include trade-offs section
- [ ] Best_Practice nodes include how_to_apply + validation_criteria
- [ ] All nodes answer: "Could someone understand this in 6 months?"
- [ ] No single-sentence descriptions
- [ ] No vague phrases like "related to X" - explain HOW related

**If ANY checklist item fails → fix before extraction.**

---

## Why This Matters

**6 months from now:**
- "Why did we decide X?" → Complete reasoning preserved
- "How do I apply pattern Y?" → Step-by-step guidance available
- "What was the context for Z?" → Situation fully documented

**Terse descriptions create amnesia. Rich descriptions create organizational memory.**

---

## Integration with MCP Tool

When calling `mcp__consciousness__add-cluster`, the tool will validate:
1. Description length per type
2. Required type-specific fields present
3. Decision alternatives count ≥ 3

**Extraction will FAIL if richness requirements not met.**
