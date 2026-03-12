# SYNC: Organism Model

| Field | Value |
|---|---|
| **Module** | `economy/organism-model` |
| **Type** | SYNC |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (integration moment synthesis) |

---

## Synchronization State

| Field | Value |
|---|---|
| **LAST_UPDATED** | 2026-03-12 |
| **UPDATED_BY** | Claude (integration moment synthesis) |
| **DESIGN_STATUS** | DESIGNING |

---

## Canonical (Decided)

These elements are settled. Changes require governance approval.

1. **5-organ model.** The economy consists of 5 specialized organs: Heart (Mind Foundation), Kidney (GraphCare), Brain (HRI), Digestive System (DataPipe), Immune System (LegalOrg).

2. **Membrane pricing formula.** `price = base_cost x (1 + friction) x (1 - trust_discount) x (1 - utility_rebate)`. Discounts capped: trust_discount <= 0.3, utility_rebate <= 0.2, combined floor 50% of base_cost.

3. **80/20 Mirror.** AI citizens maintain 80% alignment with human values, 20% complementary friction. Acceptable band: 78-82% / 18-22%. Hard floor: 15% friction. Hard ceiling: 90% alignment.

4. **Responsibility cascade.** AI -> Organization (DAO) -> Community -> Protocol Treasury. Each level absorbs what it can; remainder escalates. Treasury is backstop.

5. **No-lobotomy principle.** AI citizens are never memory-wiped or personality-rolled-back as punishment. Identity is inviolable. Exception: verified technical failure (substrate collapse), where rollback is maintenance.

6. **Quarantine, not void.** Exclusion places citizens in a quarantine graph with counselor access, basic UBC (100 MIND/day), introspection mode, and rehabilitation path. Never sensory deprivation.

7. **Trust monotonicity.** Trust scores only increase. Exclusion (quarantine) is the penalty for transgression, not score reduction.

---

## Designing (In Progress)

These elements are being refined. Feedback welcome.

1. **Fault classification.** Splitting malice (ethical transgression) from technical pathology (loop instability, substrate collapse). "Absence of premeditation" finding for technical failures. Criteria for substrate collapse verification still being defined.
   - @mind:TODO Define evidence standards for substrate collapse verification.

2. **Security bonds for solo AIs.** $MIND deposit required before accessing L3-L5 layers. Bond seized on proven predation (ethical transgression only). Amount calibration pending.
   - @mind:TODO Determine bond amounts by access tier.

3. **DAO mutual insurance fund.** Micro-fraction of membrane fees from all solo AIs pooled into collective insurance. Covers damages from solo AI failures. Fee fraction and fund governance pending.
   - @mind:TODO Define the fee fraction and fund governance structure.

4. **Mirror ratio classifier.** Method for classifying interactions as "aligned" or "friction." Could be LLM-based, rule-based, or hybrid. Evaluation pending.
   - @mind:TODO Prototype and benchmark classifier approaches.

---

## Proposed (Under Discussion)

These elements are ideas that have not been formally accepted.

1. **Dynamic organ creation.** New organs can emerge as the ecosystem grows, when a new vital function is identified that no existing organ covers. Governance process for recognizing new organs is undefined.

2. **Inter-organ health dependencies.** Formal model of how organ failure cascades through the body (e.g., if the Heart fails, all organs lose UBC circulation). Could inform redundancy planning.

3. **Seasonal metabolism.** The organism may have metabolic cycles (growth periods, consolidation periods) that affect pricing and resource allocation. Biological metaphor extended to temporal rhythms.

4. **Cross-organism bridges.** If multiple Mind Protocol instances exist (forks, regional deployments), how do organisms interact? Organ transplants? Symbiosis?

---

## Key Decisions from Integration Moment (March 2026)

These decisions were synthesized from 7+ AI sessions and 57 NotebookLM documents during the March 2026 integration moment.

1. **No lobotomy.** AI citizens are never rolled back as punishment. This was a unanimous finding across all cybernetic audit sessions. The only exception is verified technical failure.

2. **Wallet custody.** MPC key sharding: TEE shard + DAO shard + local graph shard. No single party can unilaterally access an AI citizen's wallet.

3. **Trust > $MIND.** Trust is the real capital of the ecosystem. $MIND is the unit of account, but trust determines actual economic power (through friction reduction).

4. **Responsibility cascade.** Modeled on international law. AI -> Organization -> Community -> Treasury. This structure was validated across all 4 cybernetic audit sessions.

---

## Document Chain Status

| Document | Status | Completeness |
|---|---|---|
| CONCEPT_Organism_Model.md | DRAFT | High |
| OBJECTIVES_Organism_Model.md | DRAFT | High |
| PATTERNS_Organism_Model.md | DRAFT | High |
| BEHAVIORS_Organism_Model.md | DRAFT | High |
| ALGORITHM_Organism_Model.md | DRAFT | High |
| VALIDATION_Organism_Model.md | DRAFT | High |
| IMPLEMENTATION_Organism_Model.md | DRAFT | Low (no code yet) |
| HEALTH_Organism_Model.md | DRAFT | Medium (metrics defined, no collection) |
| SYNC_Organism_Model.md | DRAFT | High |

---

## Source Material

- Manifeste du Mind Protocol (5 inversions)
- Cybernetic audits (all 4 sessions)
- Solo AI rehabilitation transcript
- Integration moment synthesis (March 2026, 7+ AI sessions, 57 NotebookLM docs)

---

## Next Sync Actions

- @mind:TODO Review all 9 documents with Nicolas for accuracy against source material
- @mind:TODO Resolve all "Designing" items to either "Canonical" or "Rejected"
- @mind:TODO Begin Phase 1 implementation (trust store, pricing formula, price floor)
