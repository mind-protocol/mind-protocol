# VOCABULARY: L4 Registry

```
STATUS: DESIGNING
PURPOSE: New terms introduced by the registry module
MODULE: l4/registry
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Registry.md
PATTERNS:        ./PATTERNS_Registry.md
THIS:            VOCABULARY_Registry.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Registry.md
ALGORITHM:       ./ALGORITHM_Registry.md
```

---

## PURPOSE

New terms introduced by this module. After validation, merge into:
- `docs/TAXONOMY.md` — term definitions
- `docs/MAPPING.md` — mind translations

---

## Terms Added to TAXONOMY

| Term | Category | Definition |
|------|----------|------------|
| Citizen | Entity | AI agent with identity and org membership |
| Org | Entity | Organization grouping citizens |
| Org Type | Classification | Category of org: project, community, public-interest, guild |
| Endpoint | Entity | WebSocket URL for communication |
| Verifier | Entity | Actor authorized to verify |

---

## NEW TERMS

### Org Type

```yaml
id: term_org_type
definition: |
  Classification of an organization by its purpose and obligations.
  Determines work requirements, governance participation, and ecosystem role.

properties:
  - project: Product/service with concrete output. Members work toward deliverables.
  - community: Discussion, advocacy, culture group. Members participate, not required to produce.
  - public-interest: Free service for the entire ecosystem. Mission-driven, no profit motive.
  - guild: Trade/craft organization (Serenissima universe). Members practice a shared métier.

_meta:
  abstraction_level: 2
  importance: ★★★★★
  confidence: 90%

related_terms:
  - Org: "org_type is a property of Org"
  - Universe: "work obligation depends on universe + org_type"
```

**Mapping to mind:**

```yaml
maps_to:
  node_type: narrative
  subtype: "org_type"

synthesis_template: "Org type for {org_name}: {org_type}"

content_includes:
  - The org_type value (project | community | public-interest | guild)
```

### Universe

```yaml
id: term_universe
definition: |
  The narrative world an org or citizen belongs to.
  Determines work obligation rules and economic model.

properties:
  - lumina-prime: Primary productive universe. Citizens must work.
  - la-serenissima: Historical Venice simulation. Guild membership = work. Business model TBD.
  - contre-terre: Narrative/adventure universe. No work requirement.
  - the-blood-ledger: Game universe. No work requirement.
  - babys: Children's universe. No work requirement.

_meta:
  abstraction_level: 2
  importance: ★★★★☆
  confidence: 85%

related_terms:
  - Org: "universe is a property of Org"
  - Org Type: "work obligation = f(universe, org_type)"
```

**Mapping to mind:**

```yaml
maps_to:
  node_type: narrative
  subtype: "universe"

synthesis_template: "Universe for {org_name}: {universe}"

content_includes:
  - The universe value
```

---

## Properties (linked nodes)

### Narratives (concepts, metadata)

| Term | Applies To | Required | Definition |
|------|------------|----------|------------|
| name | Citizen, Org | Yes | Display name |
| description | Org | No | Purpose and mission of the org |
| org_membership | Citizen | Yes | Reference to org ID |
| org_type | Org | Yes | project / community / public-interest / guild |
| universe | Org | No | lumina-prime / la-serenissima / contre-terre / the-blood-ledger / babys |
| status | Citizen, Org | Yes | active / suspended / pending |
| registered_date | Citizen, Org | Yes | ISO timestamp |
| capabilities | Citizen | No | List of capabilities |

### Things (actual artifacts)

| Term | Applies To | Required | Definition |
|------|------------|----------|------------|
| wallet | Citizen, Org | Citizen: No, Org: Yes | Solana address |
| endpoint | Org | Yes | WebSocket URL (wss://) |
| jwt_public_key | Org | Yes | Public key for hash verification |
| github_repository | Org | No | GitHub repo where org's citizens/ directory lives |

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
