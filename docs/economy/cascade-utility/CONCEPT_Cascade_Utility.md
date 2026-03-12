# CONCEPT: Cascade d'Utilite

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | cascade-utility                            |
| TYPE          | Cross-cutting concept                      |

## Core Insight

Value is measured by topological footprint, not self-declaration.

A contribution has zero value until the downstream graph proves it was useful. Stars, likes, downloads, and other vanity metrics are semantically cheap to generate and therefore carry no weight. The only metric that matters is the shape of the dependency graph: who used this contribution, how diverse are those users, and what provable value did they themselves produce?

> "Building a fake topology is like building Paris in Lego -- the cost exceeds the reward."

The Cascade d'Utilite is a biological immune system for value measurement. The cycle is:

```
Stimulus --> Action --> Usage Verification --> Diversity Check --> Value Production
```

A stimulus enters the system. An actor responds with an action. The system then verifies whether that action was actually used downstream. It checks whether the usage is diverse (not self-referential or Sybil-generated). Only then does the action produce recognized value.

This cycle is continuous and append-only. The `.cascade` root never erases -- neither successes nor failures are removed from the record.

## Why This Matters

Traditional value measurement systems (GitHub stars, npm downloads, social media engagement) are trivially gameable because they measure declaration, not topology. A bot can star a repository. A script can inflate download counts. But constructing a genuine, diverse, multi-organizational dependency graph that produces real downstream value is computationally prohibitive to fake.

The cascade transforms "how popular is this?" into "what shape does the usage graph have?" -- a question that is structurally resistant to manipulation.

## Relationships

| Related Module        | Relationship                                                              |
|-----------------------|---------------------------------------------------------------------------|
| UBC                   | Cascade utility scores serve as a vesting condition for compute credits   |
| storage-tax           | Cascade revenue funds the redistribution pool for storage-tax             |
| bonds                 | Trust scores from the bond system feed into the cascade's f_risk factor   |
| organism-model        | Organ pricing within the organism model is derived from cascade dynamics  |

## Open Questions

- @mind:TODO Determine the exact boundary between cascade-utility and the bond trust system. Where does trust scoring end and utility measurement begin?
- @mind:TODO Define the interaction protocol between cascade utility scores and UBC vesting schedules.
- @mind:TODO Specify how storage-tax redistribution is weighted by cascade utility output.
