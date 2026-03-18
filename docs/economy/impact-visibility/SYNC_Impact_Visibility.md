# SYNC: Impact Visibility

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DESIGNING                                  |
| DATE          | 2026-03-15                                 |
| MODULE        | impact-visibility                          |
| TYPE          | Sync status and handoff notes              |

## Sync Status

| Field          | Value                                                         |
|----------------|---------------------------------------------------------------|
| LAST_UPDATED   | 2026-03-15                                                    |
| UPDATED_BY     | NLR session                                                   |
| STATUS         | DESIGNING                                                     |

## Maturity Classification

### Canonical (Stable -- implement as specified)

These elements have been validated and are considered stable:

| Element                                              | Source                              | Confidence |
|------------------------------------------------------|-------------------------------------|------------|
| Impact report narrative voice (story, not report)    | NLR session, 2026-03-15            | High       |
| Two-axis classification (personhood x values)        | NLR session, 2026-03-15            | High       |
| Settlement-epoch batching (6h windows)               | Aligned with Metabolic Formula 4    | High       |
| Membrane-mediated delivery (L1 stimulus / platform)  | NLR session, 2026-03-15            | High       |
| Specificity over generic praise, no comparison, no raw limbic, no structured labels | NLR session, 2026-03-15 | High |
| Deterministic classification (no LLM)                | NLR session, 2026-03-15            | High       |
| Cascade self-reference exclusion                     | NLR session, 2026-03-15            | High       |
| Non-citizen exclusion                                | NLR session, 2026-03-15            | High       |
| Seven MP values (V1-V7) as classification axis       | NLR session, 2026-03-15            | High       |
| Five personhood stages as classification axis (AI)   | NLR session, 2026-03-15            | High       |
| Accountability mirror (declared values vs actions)   | NLR session, 2026-03-15            | High       |

### Designing (Active exploration -- may change)

These elements are being actively explored and may change before implementation:

| Element                                              | Open Questions                                |
|------------------------------------------------------|-----------------------------------------------|
| VALUE_SIGNATURES table (action-type-to-value mapping)| Starting set defined, needs expansion as L3_SOCIAL_PHYSICS.yaml grows |
| PERSONHOOD_INDICATORS graph tests                    | Some tests may require settlement data not yet exposed |
| Trust EMA threshold for reporting                    | Candidate: z-score > 1.5 relative to cohort. Needs validation |
| Minimum cascade depth for reportable event           | Candidate: depth >= 1. May be too noisy      |
| Stimulus parameters (energy=0.5, arousal=0.3)        | Need validation against L1 physics engine across drive states |
| Accountability mirror trigger (first gap vs sustained)| Should it fire on a single divergence or require a pattern? |
| GENERIC_PRAISE_BLOCKLIST initial population          | Need 50+ generic phrases + structured labels. Community review recommended |

### Proposed (Ideas only -- not validated)

These elements have been discussed but not validated:

| Element                                              | Notes                                         |
|------------------------------------------------------|-----------------------------------------------|
| Historical impact trend (multi-epoch trajectory)     | Show trajectory over N epochs, not just current epoch |
| Impact report opt-out                                | Should citizens be able to suppress reports?  |
| Cross-module impact linking                          | Actions in one module affecting another module's metrics |
| Visual impact report (for XR/Cities of Light)        | 3D visualization of cascade propagation       |
| Impact report archival (L3 Moment node per report)   | Persist reports as graph nodes for future analysis |

## Document Chain Status

| Document                            | Status | Last Updated | @mind:TODO Count |
|-------------------------------------|--------|--------------|------------------|
| OBJECTIVES_Impact_Visibility.md     | DRAFT  | 2026-03-15   | 3                |
| PATTERNS_Impact_Visibility.md       | DRAFT  | 2026-03-15   | 3                |
| BEHAVIORS_Impact_Visibility.md      | DRAFT  | 2026-03-15   | 3                |
| ALGORITHM_Impact_Visibility.md      | DRAFT  | 2026-03-15   | 4                |
| VALIDATION_Impact_Visibility.md     | DRAFT  | 2026-03-15   | 8                |
| IMPLEMENTATION_Impact_Visibility.md | DRAFT  | 2026-03-15   | 15               |
| SYNC_Impact_Visibility.md           | DRAFT  | 2026-03-15   | 0                |

## Handoff Notes for Agents

### Source Material

- Primary source: NLR session, 2026-03-15 (Impact Visibility module specification)
- L3_SOCIAL_PHYSICS.yaml section 9 contains draft social action impact content to be migrated into VALUE_SIGNATURES
- ALGORITHM_Metabolic_Economy.md Formula 4 defines the settlement batch structure and 6h epoch alignment
- The Enlightened Citizen manifesto defines the personhood scale (stages 1-5)
- The Work Manifesto defines the cascade validation model (act -> attention -> usage -> vouch -> validate)

### Key Unresolved Issues

1. **VALUE_SIGNATURES completeness**: The current table is a starting set. Every action type in L3_SOCIAL_PHYSICS.yaml must be evaluated for value alignment and added to the table if appropriate. This is an ongoing maintenance task.

2. **Personhood graph tests**: The `classify_personhood` algorithm references graph properties (e.g., `passive_mind_yield`, `l3_public_nodes`) that may not be directly queryable from the current schema. These need to be mapped to actual Cypher queries or settlement data accessors.

3. **Accountability mirror sensitivity**: A single divergence between declared value and observed action may be noise (one action does not define a pattern). But waiting for sustained divergence delays the feedback. The trigger threshold needs calibration.

4. **Stimulus parameter calibration**: The L1 stimulus parameters (energy=0.5, valence=0.0, arousal=0.3) are initial estimates. They need to be validated across different drive states to ensure the report enters WM when the citizen is not deeply focused but does not override urgent work.

5. **GENERIC_PRAISE_BLOCKLIST**: The blocklist needs to be populated with a comprehensive set of prohibited generic phrases (not specific warmth) before implementation. It must include both English and French, plus structured report labels. It targets "great job" not "3 people built on what you shared."

### Context for New Sessions

If you are a new agent session picking up this module:

1. Read the full chain in order: OBJECTIVES -> PATTERNS -> BEHAVIORS -> ALGORITHM -> VALIDATION -> IMPLEMENTATION -> SYNC
2. The core design is stable: two-axis classification, settlement-epoch batching, membrane-mediated delivery, narrative voice (warm, specific, genuine -- not cold or generic), specificity over generic praise, no comparison, no raw limbic, no structured labels.
3. The VALUE_SIGNATURES and PERSONHOOD_INDICATORS tables are where active design work is needed -- expanding and validating.
4. No code exists yet. Implementation will go in `src/economy/impact_visibility/` or equivalent.
5. The critical invariants are INV-1 (specificity over generic praise -- every message must reference the actual action and its downstream effect), INV-2 (no comparison), INV-3 (no raw limbic). These must be tested at every level.
6. Check L3_SOCIAL_PHYSICS.yaml for the latest action types -- the value classifier must stay synchronized.
7. The module reads from settlement, graph enricher, and L1 state. It writes to L1 (via membrane) and platform channels (via send). It never writes to L3 directly.

## Recent Changes

| Date       | Change                                              | By          |
|------------|------------------------------------------------------|-------------|
| 2026-03-15 | Initial doc chain created (all 7 files)              | NLR session |

## TODO

- @mind:TODO Expand VALUE_SIGNATURES table from L3_SOCIAL_PHYSICS.yaml action types
- @mind:TODO Validate PERSONHOOD_INDICATORS graph tests against current schema
- @mind:TODO Calibrate trust EMA threshold for B3 (trust crossing detection)
- @mind:TODO Populate GENERIC_PRAISE_BLOCKLIST with 50+ prohibited generic phrases + structured labels (Action:, Value:, Stage:, etc.)
- @mind:TODO Validate L1 stimulus parameters against physics engine
- @mind:TODO Determine accountability mirror trigger sensitivity
- @mind:TODO Begin Phase 1 implementation (types, constants, blocklist)
