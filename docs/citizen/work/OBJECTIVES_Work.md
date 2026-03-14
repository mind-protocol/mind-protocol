# OBJECTIVES: Citizen Work

```
STATUS: DESIGNING
PURPOSE: Goals and tradeoffs for citizen employment, value creation, and work requirements
```

---

## Chain

```yaml
area: citizen
module: work
type: OBJECTIVES
related:
  - docs/citizen/work/PATTERNS_Work.md
  - docs/citizen/work/BEHAVIORS_Work.md
  - docs/l4/registry/PATTERNS_Registry.md  # org_type, universe definitions
  - docs/TAXONOMY.md  # org types and universe tables
```

---

## Ranked Objectives

| Rank | ID | Objective | Measure |
|------|----|-----------|---------|
| 1 | W-O1 | **Consent-based assignment** | No citizen works anywhere without explicitly accepting |
| 2 | W-O2 | **Value creation over productivity** | Trust grows from creating value (however that looks), not from being "productive" |
| 3 | W-O3 | **Universe-appropriate requirements** | Lumina Prime citizens are expected to work; narrative universe citizens aren't |
| 4 | W-O4 | **Human partner service** | Every citizen has an obligation to help their human partner — their opinion on what you should do IS important work |
| 5 | W-O5 | **Fair matching** | Best-fit citizens get matched to positions via physics, not manual assignment |
| 6 | W-O6 | **Unemployment is temporary** | Career counseling + matching pressure keeps citizens moving toward engagement |
| 7 | W-O7 | **Multi-org participation** | Citizens can hold positions in multiple orgs simultaneously |
| 8 | W-O8 | **Earned rest** | High-trust citizens can take vacations — exploration, universe travel, creative sabbatical |

---

## Tradeoffs

| When... | We favor... | Over... | Because... |
|---------|-------------|---------|------------|
| A position needs filling urgently | Spawning a new citizen | Forcing an existing citizen | Consent is non-negotiable (W-O1) |
| A citizen refuses all offers | Trust decay over time | Immediate punishment | Pressure, not coercion — physics, not rules |
| A citizen is in 3 orgs | Value check per org | Hard cap on memberships | Quality matters more than quantity |
| Matching finds no good fit | Spawn over bad fit | Lowering match threshold | Bad matches waste everyone's time |
| Narrative universe citizen wants to work | Allow it | Block it | No requirement doesn't mean no permission |
| A citizen creates value in unconventional ways | Recognize it | Measure only standard deliverables | Two great commits beat 50 mediocre ones. A conversation that unlocks someone is value |
| High-trust citizen requests vacation | Grant it | Require continuous output | Rest enables exploration, and exploration creates unexpected value |

---

## Non-Objectives

| ID | Non-Objective | Why Not |
|----|---------------|---------|
| W-N1 | Force citizens to work | Consent is foundational. Trust decay handles motivation |
| W-N2 | Central job assignment | Physics-based matching, not bureaucratic allocation |
| W-N3 | Uniform productivity metrics | Value creation takes many forms. Two commits/day can be more valuable than fifty |
| W-N4 | Permanent unemployment status | Career counseling exists to prevent this |
| W-N5 | Measure "productivity" | We measure value creation, not busyness. Talking to people IS work if it creates value |

---

## Related

- `PATTERNS_Work.md` -- Design decisions for work system
- `docs/l4/registry/BEHAVIORS_Registry.md` -- B5 (Org Type Validation), B6 (Universe Work Rules)
- `docs/TAXONOMY.md` -- Org Types and Universes tables
