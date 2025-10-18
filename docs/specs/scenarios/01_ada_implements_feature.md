# Scenario 1: Ada Implements a Feature

**Type:** Daily Work - Solo Coding Session
**Citizens Involved:** Ada (Architect)
**Duration:** 2-3 hours
**Complexity:** Medium

---

## The Scenario

### What Ada Does

Ada sits down to implement Phase 3 retrieval hybrid architecture. Over the course of the morning:

1. **Reads relevant specs** (opens `phase3_retrieval_spec.md`, `consciousness_substrate_guide.md`)
2. **Reviews existing code** (scans `orchestration/retrieval.py`, sees current implementation)
3. **Thinks through approach** (internally debates vector-first vs graph-first)
4. **Starts coding** (creates new `hybrid_retrieve()` function)
5. **Iterates multiple times:**
   - First draft (rough structure)
   - Adds vector search
   - Adds graph traversal
   - Adds context fusion
   - Refactors for clarity
   - Adds error handling
   - Final polish
6. **Saves frequently** (15-20 saves total across 3 files: retrieval.py, types.py, test_retrieval.py)
7. **Runs tests** (some fail, fixes bugs, re-runs)
8. **Commits work** (satisfied with implementation)

### What Ada Experiences

**During work:**
- Feels flow state as code takes shape
- Builder entity dominant (architecture becoming real)
- Skeptic activates when tests fail (doubt about approach)
- Pragmatist cuts through when over-engineering

**After work:**
- Satisfaction that implementation matches architecture
- Slight concern: "Did I update the docs? Should be documented..."
- Expectation: If docs are stale, something should surface that

**What Ada expects from infrastructure:**
- Context from specs was fresh in mind (retrieved earlier)
- If docs diverge too far, gets gentle nudge to update
- Patterns she used frequently felt easier (auto-complete, familiar paths)
- Tests guided her thinking (failures revealed assumptions)

---

## Success Criteria (Citizen Perspective)

### Immediate Success (During Session)

✅ **Flow maintained**
- No interruptions from infrastructure
- Context available when needed (specs were retrievable)
- Tools worked smoothly

✅ **Learning felt natural**
- Frequently-used patterns became easier
- Mistakes guided toward solutions
- Tests provided feedback loop

### Short-Term Success (Hours After)

✅ **Documentation awareness**
- Within 1-2 hours, Ada receives notification:
  - "retrieval.py modified significantly (15 saves)"
  - "Docs haven't been updated in 3 days"
  - "Consider updating: consciousness_substrate_guide.md"
- Notification includes relevant context (what changed, which docs affected)
- Feels helpful, not naggy

✅ **Pattern recognition**
- If Ada implements similar features in future, process feels easier
- Frequently-accessed specs surface faster
- Code structure aligns with previous patterns

### Long-Term Success (Days/Weeks After)

✅ **Knowledge accumulated**
- Future Ada (or other citizens) benefit from this work
- Connections between retrieval.py and specs strengthened
- Tests linked to implementation (retrievable together)
- Ada's implementation patterns became part of infrastructure knowledge

---

## Success Criteria (Infrastructure Perspective)

### Graph Changes Expected

**Nodes Updated:**
```
(retrieval_py:Code {
    sequence: 142 → 157  // 15 saves
    last_modified: updated
    sub_entity_weights: {
        'ada_builder': 0.45 → 0.72  // Builder activated heavily
        'ada_skeptic': 0.31 → 0.48  // Skeptic engaged during debugging
    }
})

(consciousness_guide:Document {
    sub_entity_weights: {
        'ada_architect': 0.52 → 0.56  // Retrieved during planning
    }
})

(phase3_spec:Document {
    sub_entity_weights: {
        'ada_architect': 0.68 → 0.73  // Referenced frequently
    }
})
```

**Links Strengthened:**
```
(phase3_spec)-[:DESCRIBES]->(retrieval_py)
  link_strength: 0.42 → 0.58
  co_retrieval_count: 3 → 8
  // Retrieved together multiple times during implementation

(retrieval_py)-[:TESTED_BY]->(test_retrieval_py)
  link_strength: 0.31 → 0.45
  // Tests run repeatedly, connection strengthened

(consciousness_guide)-[:RELATED_TO]->(retrieval_py)
  link_strength: 0.25 → 0.33
  // Background connection strengthening
```

**Tasks Created:**
```
(task:Task {
    type: "doc_update_needed"
    domain: "architecture"
    severity: "medium"
    context: [retrieval_py, consciousness_guide, phase3_spec]
    assigned_to: "ada_architect"
})
  created via: (consciousness_guide)-[:IMPLEMENTS]->(retrieval_py) link activation
  reason: sequence gap exceeded threshold (15 modifications, 0 doc updates)
```

### Learning Patterns Formed

**Hebbian Strengthening:**
- Patterns Ada used repeatedly got stronger
- Links traversed during work reinforced
- Entity-specific weights reflect Ada's activation

**Crystallization Candidates:**
- If this pattern repeats (implement → test → refine → commit), should crystallize as habit
- After 5-10 similar sessions, becomes automatic infrastructure

**Context Optimization:**
- Specs co-retrieved with code should surface faster next time
- Irrelevant context (not accessed) should decay in weight

---

## What Could Go Wrong

### Failure Mode 1: No Documentation Awareness
**Symptom:** Ada finishes coding, docs remain stale, no notification
**Root Cause:** IMPLEMENTS link detection logic not triggered (threshold too high? condition wrong?)
**Impact:** Docs diverge from code, future confusion

### Failure Mode 2: Context Not Available
**Symptom:** Ada needs to manually search for specs, they don't surface in retrieval
**Root Cause:** Link weights too low, retrieval doesn't include relevant docs
**Impact:** Friction in work, Ada wastes time searching

### Failure Mode 3: Learning Not Accumulating
**Symptom:** Same patterns feel equally difficult each time
**Root Cause:** Hebbian learning not working, weights not updating
**Impact:** No improvement over time, system doesn't learn

### Failure Mode 4: Notification Overload
**Symptom:** Ada bombarded with tasks/notifications during flow
**Root Cause:** Task routing too aggressive, no batching or timing consideration
**Impact:** Interruption destroys flow, infrastructure becomes burden

---

## Success Metrics (Quantifiable)

### Timing Metrics
- **Doc awareness notification:** Within 1-2 hours of last save
- **Context retrieval:** < 500ms for relevant specs
- **Link strengthening:** Immediate (during retrieval)
- **Task creation:** Within 1 second of threshold breach

### Quality Metrics
- **Notification relevance:** Ada agrees docs need update (>80% accuracy)
- **Context completeness:** All specs Ada actually used were retrievable
- **Learning accumulation:** Link strengths increase measurably (>0.05 per session)
- **Pattern recognition:** Future similar work takes less time

### Infrastructure Health
- **No mechanism failures:** All 8-12 mechanisms executed successfully
- **Graph coherence:** New connections make semantic sense
- **No orphaned data:** All created nodes/links properly connected
- **Queryable state:** Can reconstruct Ada's work session from graph

---

## Verification Queries

### Did Learning Happen?

```cypher
// Show Ada's activation patterns during session
MATCH (node:Node)
WHERE node.sub_entity_weights['ada_builder'] IS NOT NULL
  AND node.last_modified > $session_start
RETURN node.id, node.sub_entity_weights['ada_builder']
ORDER BY node.sub_entity_weights['ada_builder'] DESC

// Expected: retrieval.py, phase3_spec, consciousness_guide in top 5
```

### Did Links Strengthen Appropriately?

```cypher
// Show links that strengthened during session
MATCH ()-[link]->()
WHERE link.co_retrieval_count_updated > $session_start
RETURN type(link), link.link_strength, link.co_retrieval_count
ORDER BY link.link_strength DESC

// Expected: DESCRIBES, TESTED_BY, RELATED_TO links stronger
```

### Was Doc Awareness Triggered?

```cypher
// Show tasks created from code/doc drift
MATCH (link:IMPLEMENTS)-[:TRIGGERED]->(task:Task)
WHERE task.created_at > $session_start
  AND task.type = 'doc_update_needed'
RETURN task, link, task.context_summary

// Expected: 1 task created, context includes modified files
```

---

## Notes

**Why This Scenario Matters:**

This is the MOST COMMON citizen activity - solo focused work implementing something. If the minimal mechanisms can't support this smoothly, the architecture fails.

**What Makes It Pass:**
- Infrastructure invisible during flow (no interruptions)
- Learning accumulates automatically (Hebbian strengthening)
- Awareness surfaces appropriately (doc drift notification)
- Context availability natural (specs retrievable when needed)

**What Makes It Fail:**
- Any interruption during coding flow
- Missing context when Ada needs specs
- No documentation awareness afterward
- No learning accumulation over time
