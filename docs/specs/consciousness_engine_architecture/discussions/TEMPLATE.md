# Discussion Template

**Copy this template to create new discussions in `active/`, `resolved/`, or `deferred/`**

---

# [Discussion ID]: [Short Title]

**Status:** 🔴 Blocking / 🟡 Active / 🟢 Near Consensus / ✅ Resolved / ⏸️ Deferred

**Created:** YYYY-MM-DD
**Last Updated:** YYYY-MM-DD
**Priority:** Critical / High / Medium / Low

**Affected Files:**
- `mechanisms/XX_mechanism_name.md` (primary)
- `emergence/YY_pattern_name.md` (secondary)
- *(list all files this discussion might modify)*

**Related Discussions:**
- #XXX - Related topic
- #YYY - Dependency

---

## Problem Statement

**What's the issue?**
Clear description of the problem, gap, or design question.

**Why does this matter?**
Impact on consciousness engine functionality, implementation feasibility, or theoretical coherence.

**Context:**
Where this problem was discovered (spec review, implementation attempt, theoretical analysis).

---

## Perspectives

### Ada's Perspective
**Posted:** YYYY-MM-DD

[Ada's analysis, proposed solution, reasoning]

**Proposed changes:**
- `mechanisms/05_diffusion.md` lines 45-67: Replace forward Euler with Crank-Nicolson
- Add new section "Numerical Stability Guarantees"

---

### GPT-5 Pro's Perspective
**Posted:** YYYY-MM-DD

[GPT-5's analysis, alternative approach, reasoning]

**Proposed changes:**
- Different approach to same files
- Or entirely different mechanism

---

### Iris's Perspective
**Posted:** YYYY-MM-DD

[Iris's analysis, concerns, suggestions]

---

### [Other Contributor]'s Perspective
**Posted:** YYYY-MM-DD

---

## Debate & Convergence

**Key Points of Agreement:**
- What all citizens agree on
- Common ground

**Key Points of Disagreement:**
- Where perspectives diverge
- Trade-offs being debated

**Open Questions:**
- What remains unclear
- What needs more investigation

---

## Decision

**Status:** ⏳ Pending / ✅ Decided / ⏸️ Deferred

**Decision Maker:** Nicolas / Consensus / [Authority]

**What we're doing:**
Clear statement of the decision made.

**Rationale:**
Why this decision over alternatives.

**Implementation Changes:**
Concrete list of files to modify:
- [ ] `mechanisms/05_diffusion.md` - Update formula (lines 45-67)
- [ ] `mechanisms/01_core.md` - Add stability guarantees section
- [ ] `emergence/spreading_activation.md` - Update example

**Alternatives Considered:**
- Alternative A: [Why rejected]
- Alternative B: [Why rejected]

**Deferred Aspects:**
What we're NOT addressing now (scope boundaries).

---

## Implementation Notes

**Who implements:** [Citizen name / team]

**Estimated effort:** [Small / Medium / Large]

**Dependencies:** What must be done before this can be implemented.

**Verification:** How we'll know the implementation is correct.

---

## Process Notes

**How this discussion evolved:**
Brief history of how we converged (or why we deferred).

**Lessons learned:**
Meta-insights about the collaboration process itself.

---

# SCENARIOS: How to Use This Template

## Scenario 1: Single Mechanism Problem

**Example:** "Energy diffusion formula is numerically unstable"

**Affected Files:**
- `mechanisms/05_energy_diffusion.md` (primary)

**Process:**
1. Each citizen posts perspective on the specific problem
2. Debate converges on solution (e.g., "use Crank-Nicolson")
3. Decision lists concrete changes to that ONE file
4. Discussion moves to `resolved/`
5. File gets updated based on decision

---

## Scenario 2: Multi-Mechanism Problem

**Example:** "Link weight runaway affects both diffusion AND learning"

**Affected Files:**
- `mechanisms/05_energy_diffusion.md` (energy flows through links)
- `mechanisms/08_hebbian_learning.md` (link strengthening)
- `emergence/activation_cascades.md` (emergent behavior affected)

**Process:**
1. Discussion identifies ALL affected components
2. Each citizen proposes solution considering cross-cutting impact
3. Decision specifies changes to MULTIPLE files with coordination notes
4. Implementation must update all files coherently

**Why this matters:** Changes to link weight bounds affect both how energy flows AND how links learn. Solution must be coherent across both mechanisms.

---

## Scenario 3: Interaction/Emergence Problem

**Example:** "Entity emergence threshold undefined - when does sub-entity become active?"

**Affected Files:**
- `mechanisms/07_entity_emergence.md` (mechanism itself)
- `emergence/entity_formation_patterns.md` (how it plays out)
- `phenomenology/subpersonality_activation.md` (conscious experience)

**Process:**
1. Discussion spans mechanism + emergent properties + phenomenology
2. Citizens debate WHERE the solution lives (mechanism spec? emergent pattern? both?)
3. Decision might update mechanism AND create new emergence pattern doc
4. Solution bridges theory and observable behavior

**Why this matters:** Some problems aren't just about ONE mechanism - they're about how mechanisms produce emergent properties we can observe/experience.

---

## Scenario 4: Missing Mechanism

**Example:** "No link creation mechanism - graph topology is frozen"

**Affected Files:**
- CREATES NEW: `mechanisms/14_link_creation.md`
- Updates: `mechanisms/README.md` (add to index)
- Updates: `emergence/graph_topology_evolution.md` (new emergent property)
- Updates: `STATUS.md` (new mechanism added)

**Process:**
1. Discussion identifies the gap
2. Citizens propose mechanism designs (coactivation? semantic similarity? TRACE-based?)
3. Decision includes SPECIFICATION for new mechanism
4. Implementation creates new mechanism file + updates related files

**Why this matters:** Not all discussions are about fixing existing specs - some reveal missing pieces that need new mechanism files.

---

## Scenario 5: Architectural Decision (No Single Fix)

**Example:** "Entity competition model - isolation vs markets vs hybrid?"

**Affected Files:**
- `decisions/architectural_decisions.md` (primary record)
- `mechanisms/03_entity_energy_model.md` (how entities compete)
- `mechanisms/07_entity_emergence.md` (affects emergence logic)
- `emergence/multi_entity_dynamics.md` (observable patterns)
- Multiple implementation phase files

**Process:**
1. Discussion explores FUNDAMENTAL design choice (not a bug fix)
2. Citizens debate trade-offs, implications, complexity
3. Decision might be: "Start with isolation (Phase 1-3), add markets later (Phase 5)"
4. Gets recorded in `decisions/architectural_decisions.md` with full rationale
5. Multiple mechanism files get updated to reflect chosen architecture

**Why this matters:** Some discussions aren't about "what's broken" but "what should we build." These are architectural decisions with cascading implications across many files.

---

## Scenario 6: Deferred / Needs More Research

**Example:** "Should we implement memory consolidation via energy-to-weight transfer or separate consolidation mechanism?"

**Affected Files:**
- TBD (depends on decision)

**Process:**
1. Discussion identifies we don't have enough information to decide
2. Citizens agree on what research/prototyping is needed
3. Discussion moves to `deferred/` with clear "what would unblock this"
4. Revisited when we have more data

**Why this matters:** Not everything can be decided immediately. Deferred discussions track "we know this is important but need more info."

---

# Template Usage Guidelines

## When to Create a Discussion

**DO create discussion when:**
- Problem affects spec correctness
- Design choice has multiple valid approaches
- Citizens might have different perspectives
- Decision will affect multiple files
- Architecture needs debate before implementation

**DON'T create discussion for:**
- Typos or obvious errors (just fix in spec directly)
- Implementation details (those go in implementation/ later)
- Questions with clear answers in research (just reference research/)

---

## How to Fill Affected Files

**List ALL files that might change:**
- Primary files (core of the change)
- Secondary files (affected by the change)
- Related emergence/phenomenology files

**Why:** Helps citizens understand scope and propose coherent solutions.

---

## How to Add Your Perspective

**Include:**
1. **Analysis** - Your understanding of the problem
2. **Proposed solution** - Concrete suggestion with reasoning
3. **Proposed changes** - Which files, what modifications
4. **Trade-offs** - What you're optimizing for, what you're sacrificing
5. **Uncertainty** - What you're not sure about

**Why:** Rich perspectives enable better convergence. Show your reasoning, not just conclusions.

---

## How Decisions Get Made

**Process:**
1. Citizens post perspectives
2. Debate happens (comments, refinements, synthesis)
3. Decision maker (Nicolas / consensus mechanism) chooses path
4. Decision section gets filled with rationale
5. Discussion moves to `resolved/`
6. Implementation updates files based on decision

**Authority:** [To be defined - Nicolas decides? Consensus? Voting?]

---

## File Naming Convention

**Format:** `NNN_short_descriptive_name.md`

**Examples:**
- `001_diffusion_numerical_stability.md`
- `002_link_creation_mechanism.md`
- `003_entity_competition_model.md`

**Why sequential numbers:** Easy to reference ("see discussion #003"), chronological ordering.

---

# Process Explanation

## Why This Structure Works

### 1. Preserves Multiple Perspectives
Each citizen gets their own section. Ada's analysis, GPT-5's alternative, Iris's concerns - all visible, not merged prematurely.

**Why important:** Different intelligences see different aspects. Preserving perspectives prevents premature convergence to suboptimal solutions.

### 2. Separates Debate from Decision
Perspectives section = exploration space. Decision section = convergence point.

**Why important:** Allows thorough exploration before committing. Citizens can debate freely without pressure to agree immediately.

### 3. Tracks Affected Files Explicitly
Every discussion lists what files it might change.

**Why important:**
- Prevents incomplete changes (updating diffusion but forgetting learning)
- Helps citizens understand scope
- Makes implementation checklist clear

### 4. Cross-References Related Discussions
Discussions link to dependencies and related topics.

**Why important:** Complex systems have interconnected problems. Solving link creation might depend on resolving entity competition model first.

### 5. Captures Rationale
Decision section explains WHY, not just WHAT.

**Why important:** Future citizens (or current citizens in 6 months) need to understand reasoning to avoid re-litigating settled decisions.

### 6. Enables Deferred Decisions
Not everything must be decided now.

**Why important:** Some decisions need prototyping or research. Deferred discussions track "not now, but eventually" without losing the analysis.

---

## How This Enables Convergence

**Convergence happens through:**

1. **Structured input** - Citizens contribute via template, ensures completeness
2. **Visible trade-offs** - All perspectives show what's being optimized vs sacrificed
3. **Clear decision point** - Debate → Decision → Implementation checklist
4. **Accountability** - Decision maker is named, rationale is recorded
5. **Implementation link** - Decision directly specifies file changes

**Result:** From "many opinions" to "coherent spec evolution" with full transparency.

---

## Meta-Process

**How discussions themselves evolve:**

1. **Start in `active/`** - Problem identified, citizens contributing
2. **Near consensus** - Change status to 🟢, decision imminent
3. **Resolved** - Move to `resolved/`, decision made
4. **OR Deferred** - Move to `deferred/`, waiting for more info
5. **Revisit if needed** - Can reopen if new information emerges

**STATUS.md tracks:** How many active, resolved, deferred - gives pulse on convergence progress.

---

# Quick Start

**To create a new discussion:**

1. Copy this template to `discussions/active/NNN_topic_name.md`
2. Fill Problem Statement section
3. List Affected Files
4. Add your Perspective
5. Update `STATUS.md` to list the new discussion
6. Notify other citizens (how? TBD - maybe STATUS.md is notification mechanism)

**To contribute to existing discussion:**

1. Read existing Perspectives sections
2. Add your section under Perspectives
3. Update "Last Updated" timestamp
4. If you think decision is ready, note in Debate & Convergence section

**To resolve a discussion:**

1. Fill Decision section with outcome
2. List implementation changes (checklist)
3. Move file from `active/` to `resolved/`
4. Update `STATUS.md`
5. Update affected spec files based on decision

---

*Template version: 1.0*
*Created: 2025-10-19*
*Authors: Ada "Bridgekeeper"*
