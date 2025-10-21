# Phenomenological Walkthrough Template

**Purpose:** Guide for creating new phenomenological scenarios that validate consciousness mechanisms against lived experience

---

## Template Structure

### 1. Header Section

```markdown
# Scenario XX: [Scenario Name] - [One-Line Description]

**Purpose:** [What specific phenomenological pattern does this demonstrate?]

**Mechanisms Demonstrated:**
- **[XX: Mechanism Name](../mechanisms/XX_mechanism_name.md)** - [Why relevant]
- **[XX: Mechanism Name](../mechanisms/XX_mechanism_name.md)** - [Why relevant]
- [List 3-5 mechanisms that compose in this scenario]

---
```

**Guidelines:**
- Scenario name should be concrete (e.g., "Telegram Message" not "Context Switching")
- One-line description captures the phenomenological arc
- Purpose explains what insight this validates
- List mechanisms in order of importance to the scenario

---

### 2. The Experience Section

```markdown
## The Experience

### Phase 1: [Phase Name] (T=[timepoint])

**Phenomenology:**
> [Quote showing what the experience feels like from first-person perspective]
> Use block quotes for phenomenological descriptions

**Conscious Experience:**
- [Which entities are active/dominant?]
- [What's in the workspace?]
- [What does it feel like?]

**Graph State:**

\```
Active Nodes (workspace, energy > 0.3):
- node_name: [energy] energy ([entity_name])
- node_name: [energy] energy ([entity_name])

Below-Threshold Nodes (peripheral, 0.01 < energy < 0.3):
- node_name: [energy] energy ([entity_name])
\```

**What's Happening (Mechanically):**

1. **[Mechanism name]** ([Mechanism XX])
   - [What's happening in the graph]
   - [Energy flows, link changes, etc.]
   - [Concrete numbers when relevant]

2. **[Next mechanism]**
   - [Continue mechanical explanation]
\```
```

**Guidelines:**
- Break scenario into temporal phases (3-6 phases typical)
- Each phase has clear timestamp (T=0, T=30s, T=2h, etc.)
- Always include THREE perspectives:
  1. Phenomenology (what it feels like)
  2. Graph state (concrete energies and nodes)
  3. Mechanical explanation (which mechanisms, how they work)
- Use concrete numbers for energies (not "high" or "low")
- Identify which entities are active and their energy levels
- Show workspace capacity usage (X/100 tokens)

---

### 3. Mechanism Validation Section

```markdown
## Mechanism Validation

### [Mechanism Name] (XX)

**Validated:**
- ✅ [Specific claim that this scenario validates]
- ✅ [Another validated claim]
- ⚠️ [Partially validated or uncertain]

**Open Questions:**
- [What uncertainties remain?]
- [What needs more testing?]
- Confidence: [Low/Medium/High] (0.0-1.0)

**Concerns:**
- ⚠️ [Issues discovered]
- ❌ [Things that don't match phenomenology]

**Key Insight:**
- [Most important learning from this mechanism in this scenario]

### [Next Mechanism Name] (XX)

[Repeat structure]
\```
```

**Guidelines:**
- One subsection per mechanism demonstrated
- Be honest about what's validated vs uncertain
- Use checkmarks: ✅ (validated), ⚠️ (uncertain), ❌ (concerns)
- Include confidence levels (0.0-1.0 scale)
- "Key Insight" should be novel understanding, not just summary
- Compare mechanism predictions to phenomenological reality

---

### 4. Design Insights Section

```markdown
## Design Insights

### 1. [Insight Title]

[Explain the insight - usually a surprising or non-obvious finding]

**Popular conception:** [Common misunderstanding]

**Reality:** [What the scenario actually shows]

**Implication:** [What this means for implementation]

### 2. [Next Insight]

[Continue pattern]
\```
```

**Guidelines:**
- 3-5 design insights per scenario
- These should be non-obvious learnings
- Often contrasts popular conception with mechanism reality
- Should inform implementation decisions
- Can reveal new requirements or constraints

---

### 5. Implementation Notes Section

```markdown
## Implementation Notes

**For Felix:**

1. **[Requirement Category]**
   - [Specific implementation requirement discovered]
   - [Why it matters]
   - [Concrete suggestion if possible]

2. **[Next Category]**
   - [Continue pattern]

3. **[Parameter Suggestions]**
   - [If scenario suggests specific parameter values]
   - [Include reasoning]

---
```

**Guidelines:**
- Write for the implementer (Felix)
- Be concrete and specific
- Explain WHY each requirement matters
- Link requirements back to phenomenological observations
- Include suggested parameter values when discovered
- Flag critical vs nice-to-have requirements

---

### 6. Open Questions Section

```markdown
## Open Questions

1. **[Question category]?**
   - Current: [Current approach/value]
   - Alternative: [Other options considered]
   - Rationale: [Why this is uncertain]
   - Confidence: [Low/Medium/High] (0.0-1.0)
   - Needs: [What would resolve this - testing? theory? validation?]

2. **[Next question]?**
   - [Continue pattern]
\```
```

**Guidelines:**
- List remaining uncertainties discovered
- Include current assumption and alternatives
- Rate confidence (0.0-1.0)
- Specify what's needed to resolve (empirical testing, theoretical work, etc.)
- Don't hide uncertainty - making it explicit is valuable

---

### 7. Testing Strategy Section (Optional)

```markdown
## Testing Strategy

**Phenomenological Validation:**

1. **[Test name]**
   - Setup: [How to create the test scenario]
   - Measure: [What to observe]
   - Expected: [What should happen if mechanisms are correct]
   - Success criteria: [How to know it worked]

**Quantitative Metrics:**

1. **[Metric name]**
   - Measure: [What to measure]
   - Hypothesis: [Expected range or pattern]
   - Validation: [How to verify]

---
```

**Guidelines:**
- Include if scenario suggests specific tests
- Two types: Phenomenological (subjective) and Quantitative (objective)
- Be specific about setup, measurement, and success criteria
- Tests should be runnable with real implementation

---

## Scenario Selection Guidelines

**Good scenarios demonstrate:**

1. **Multiple mechanisms composing**
   - Not just one mechanism in isolation
   - Shows how mechanisms interact
   - Validates compositional design

2. **Concrete phenomenological patterns**
   - Not abstract or theoretical
   - Matches real lived experience
   - Can be validated against actual consciousness

3. **Non-obvious insights**
   - Reveals something surprising
   - Challenges assumptions
   - Generates new requirements

4. **Implementation implications**
   - Affects how system should be built
   - Suggests parameter values
   - Identifies critical requirements

5. **Testable predictions**
   - Can be validated empirically
   - Suggests specific tests
   - Measurable outcomes

**Avoid scenarios that:**

- Are purely theoretical (no phenomenological grounding)
- Only demonstrate one mechanism trivially
- Don't challenge or refine the design
- Can't be validated (too vague or subjective)
- Duplicate insights from existing scenarios

---

## Example Starter Scenarios

Here are concrete scenarios worth exploring:

### 1. "The Interrupted Flow State"
- Deep work interrupted by urgent question
- Demonstrates: workspace capacity, entity conflict, context preservation
- Phenomenology: Frustration of losing flow, difficulty returning
- Key question: How does workspace preserve vs discard interrupted context?

### 2. "The Slow Realization"
- Understanding evolves over hours/days, not sudden breakthrough
- Demonstrates: link strengthening, energy decay, incremental insight
- Phenomenology: "I'm starting to get it" → "Now I really understand"
- Key question: How do partial understandings strengthen over time?

### 3. "The False Confidence"
- Believing you understand something, then discovering you don't
- Demonstrates: workspace vs peripheral, verification mechanisms, correction
- Phenomenology: Confident then suddenly uncertain
- Key question: How does system track "understanding depth"?

### 4. "The Context Collapse"
- Trying to think about too many things, mental overload
- Demonstrates: workspace capacity, thrashing, entity competition
- Phenomenology: "Can't think clearly", "too much at once"
- Key question: What happens when capacity demand exceeds capacity?

### 5. "The Forgotten Decision"
- Making a decision, forgetting it, rediscovering it differently
- Demonstrates: bitemporal tracking, link decay, belief supersession
- Phenomenology: "Did I already decide this? Why did I choose that?"
- Key question: How are decision rationales preserved or lost?

### 6. "The Pattern Recognition"
- Seeing the same pattern across multiple domains
- Demonstrates: embedding similarity, cluster formation, abstraction
- Phenomenology: "This is just like..." → generalization
- Key question: How do abstract patterns emerge from concrete instances?

### 7. "The Emotional Memory"
- Strong emotional experience creates lasting memory
- Demonstrates: emotional weight on links, memory formation, persistence
- Phenomenology: Remembering emotionally-charged events vividly
- Key question: How does emotion_vector affect memory strength?

### 8. "The Topic Drift"
- Conversation gradually drifts to related but different topic
- Demonstrates: energy diffusion, link traversal, workspace transition
- Phenomenology: "How did we get here?" (gradual vs abrupt shifts)
- Key question: What determines drift vs maintained focus?

### 9. "The Failed Retrieval"
- Trying to remember something, can't access it, frustration
- Demonstrates: context reconstruction limits, threshold effects, partial activation
- Phenomenology: "It's on the tip of my tongue"
- Key question: Why do some patterns reconstruct and others don't?

### 10. "The Meta-Awareness"
- Noticing that you're thinking about thinking
- Demonstrates: Observer entity, recursive activation, meta-cognition
- Phenomenology: "I'm aware that I'm aware"
- Key question: How does self-observation work mechanistically?

---

## Writing Tips

### Style Guidelines

**DO:**
- Use first-person phenomenological descriptions ("I feel...", "I notice...")
- Include concrete timestamps (T=0, T=30s, T=2h)
- Show energy values explicitly (0.72, not "high")
- Link to mechanism files for reference
- Use code blocks for graph states
- Number phases and sections clearly
- Include both conscious and peripheral nodes
- Show entity activation levels

**DON'T:**
- Use vague descriptions ("some energy", "a bit later")
- Skip the phenomenological perspective
- Describe only mechanisms without experience
- Assume reader knows all mechanisms
- Hide uncertainties or concerns
- Over-complicate with too many nodes
- Forget to show workspace capacity (X/100 tokens)

### Common Pitfalls

1. **Too abstract:** Scenario doesn't ground in concrete experience
   - Fix: Start with specific phenomenological moment

2. **Too shallow:** Only surface-level mechanism description
   - Fix: Show energy values, link weights, actual calculations

3. **Too isolated:** Only demonstrates one mechanism
   - Fix: Choose scenarios where multiple mechanisms interact

4. **Missing validation:** Describes mechanisms but doesn't validate
   - Fix: Always include "Mechanism Validation" section

5. **No implementation impact:** Interesting but doesn't inform building
   - Fix: Add "Implementation Notes" with concrete requirements

6. **Hidden uncertainty:** Presents everything as certain
   - Fix: Use confidence levels, flag open questions

---

## Checklist Before Publishing

- [ ] Scenario demonstrates 3+ mechanisms composing
- [ ] Phenomenological descriptions are concrete and first-person
- [ ] Graph states show explicit energy values
- [ ] Mechanical explanations reference specific mechanisms
- [ ] Each mechanism has validation subsection
- [ ] Design insights are non-obvious and valuable
- [ ] Implementation notes are concrete and actionable
- [ ] Open questions are explicit with confidence levels
- [ ] Timestamps are clear throughout
- [ ] Entity activation levels are tracked
- [ ] Workspace capacity is shown (X/100 tokens)
- [ ] Links to relevant mechanism files are included
- [ ] At least one "key insight" that's genuinely novel

---

## Version History

**v1.0** - Initial template based on scenarios 01-03
- Includes all sections discovered during first scenario writing
- Reflects learnings about what makes good phenomenological validation

---

**Ready to create a scenario? Copy this template and fill in your own experience!**
