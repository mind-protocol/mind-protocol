# VOCABULARY: L4 Registry

```
STATUS: DESIGNING
PURPOSE: New terms introduced by the registry module
```

---

## Terms Added to TAXONOMY

| Term | Category | Definition |
|------|----------|------------|
| Citizen | Entity | AI agent with identity and org membership |
| Org | Entity | Organization grouping citizens |
| Endpoint | Entity | WebSocket URL for communication |
| Verifier | Entity | Actor authorized to verify |

---

## Properties (linked nodes)

### Narratives (concepts, metadata)

| Term | Applies To | Required | Definition |
|------|------------|----------|------------|
| name | Citizen, Org | Yes | Display name |
| org_membership | Citizen | Yes | Reference to org ID |
| status | Citizen, Org | Yes | active/suspended/pending |
| registered_date | Citizen, Org | Yes | ISO timestamp |
| capabilities | Citizen | No | List of capabilities |

### Things (actual artifacts)

| Term | Applies To | Required | Definition |
|------|------------|----------|------------|
| wallet | Citizen, Org | Citizen: No, Org: Yes | Solana address |
| endpoint | Org | Yes | WebSocket URL (wss://) |
| jwt_public_key | Org | Yes | Public key for hash verification |

---

## Relationships

| Relationship | From | To | Via |
|--------------|------|----|----|
| belongs_to | Citizen | Org | link (hierarchy: 1.0) |
| has_property | Entity | Thing | link (hierarchy: 1.0) |
| verified_by | Entity | Verifier | link (polarity encodes status) |

---

## Verification States (computed)

| State | Link Exists | Polarity | Permanence |
|-------|-------------|----------|------------|
| unverified | No | — | — |
| pending | Yes | 0 | < 0.5 |
| provisional | Yes | 1.0 | < 0.5 |
| verified | Yes | 1.0 | >= 0.5 |
| rejected | Yes | -1.0 | any |

---

## Status Values

| Value | Meaning |
|-------|---------|
| `active` | Normal operation |
| `suspended` | Temporarily disabled |
| `pending` | Awaiting verification |

---

## Related

- `docs/TAXONOMY.md` — Central vocabulary
- `docs/MAPPING.md` — Schema translation
- `PATTERNS_Registry.md` — Design philosophy
