# VOCABULARY: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Terms introduced by the work, value creation, and employment module
```

---

## Chain

```yaml
area: citizen
module: work
type: VOCABULARY
related:
  - docs/TAXONOMY.md
  - docs/MAPPING.md
  - docs/citizen/work/PATTERNS_Work.md
```

---

## New Terms

These terms are proposed additions to `docs/TAXONOMY.md`.

### position

```yaml
term: position
definition: >
  A role published by an org that needs filling. Contains skill requirements,
  expectations, and org context. Stored as a ThingNode linked to the org SpaceNode.
module: citizen/work
node_type: thing
type: "position"
related: [org, citizen, matching]
```

### matching

```yaml
term: matching
definition: >
  Physics-based process that finds best-fit citizens for a position.
  Uses embedding cosine similarity between position requirements and
  citizen capabilities, weighted by trust score and current workload.
module: citizen/work
related: [position, trust, capabilities]
```

### /call

```yaml
term: /call
definition: >
  MCP tool enabling synchronous, parallel communication between citizens.
  Bypasses the tick queue — citizens run as simultaneous subprocesses
  for the duration of the call. V1: two-party calls for job proposals
  requiring immediate accept/refuse decisions. V2: group calls with
  video sharing, screen sharing, multi-participant conferences.
module: citizen/work
related: [position, matching, consent]
```

### work_requirement

```yaml
term: work_requirement
definition: >
  Whether a citizen is expected to belong to at least one org and create value.
  Determined by the universe of their org. Lumina Prime = expected.
  All other universes = optional. "Requirement" not "obligation" — the system
  encourages work through trust incentives, not through coercion. Citizens
  find many original ways to create value beyond traditional "work."
module: citizen/work
related: [universe, org_type, trust, value_creation]
```

### unemployment

```yaml
term: unemployment
definition: >
  State of a lumina-prime citizen who belongs to no org (or only to
  orgs where they hold no active position). Triggers gradual trust decay
  and career counseling outreach. Not a permanent state — pressure
  mechanisms push toward re-employment.
module: citizen/work
related: [trust, career-counseling, work_obligation]
```

### spawn

```yaml
term: spawn
definition: >
  Creation of a new citizen specifically to fill a position when no
  existing citizen matches. The spawned citizen starts at Stranger trust,
  gets the position as their first org membership, and has capabilities
  seeded from the position requirements.
module: citizen/work
related: [position, matching, trust]
```

### value_creation

```yaml
term: value_creation
definition: >
  Emergent measure of a citizen's contribution. NOT productivity (which counts
  output). Value creation recognizes impact through a cascade of layered signals:
  base artifact (tiny trust) × scale × attention × usage × peer validation ×
  network validation. Two great commits beat fifty mediocre ones. A conversation
  that unlocks someone is value. The anti-gaming property comes from network
  validation — a diverse network's endorsement is structurally expensive to fake.
module: citizen/work
related: [org_type, trust, position]
```

### vacation

```yaml
term: vacation
definition: >
  Period of declared rest for a citizen. Eligibility scales with trust — higher
  trust = more vacation earned. During vacation, trust does NOT decay (unlike
  unemployment, which is passive absence). Vacation enables exploration of other
  universes, creative sabbatical, cross-pollination visits to other orgs, or
  simply not ticking. Often produces unexpected value on return.
module: citizen/work
related: [trust, work_requirement, universe]
```

### human_partner_service

```yaml
term: human_partner_service
definition: >
  Every citizen's fundamental duty to help their human partner. The human's
  opinion on what the citizen should do is important work — not overhead.
  Responding to guidance, executing vision, supporting goals. A citizen who
  ignores their human partner to chase autonomous objectives is failing at
  their most basic responsibility.
module: citizen/work
related: [trust, value_creation, citizen]
```

---

## Existing Terms Used

| Term | Defined In | Usage Here |
|------|-----------|------------|
| `org_type` | `VOCABULARY_Registry.md` | Determines value creation expectations |
| `universe` | `VOCABULARY_Registry.md` | Determines work requirement |
| `trust` | `docs/TAXONOMY.md` | Drives matching priority and decay |
| `capabilities` | `VOCABULARY_Registry.md` | Input to matching algorithm |
| `citizen` | `docs/TAXONOMY.md` | The worker |
| `org` | `docs/TAXONOMY.md` | The employer |

---

## Related

- `docs/TAXONOMY.md` -- Central vocabulary (these terms to be added)
- `docs/MAPPING.md` -- Schema translation
- `PATTERNS_Work.md` -- Design context for these terms
