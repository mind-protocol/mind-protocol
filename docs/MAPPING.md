# MAPPING: Domain Terms to Schema

```
STATUS: DESIGNING
PURPOSE: How domain vocabulary maps to mind universal schema
```

---

## Schema Reference

The mind schema is **FIXED**:
- 5 node_types: `actor`, `moment`, `narrative`, `space`, `thing`
- 1 link_type: `link` (all semantics in properties)
- All custom data in `content` and `synthesis` fields

---

## NODE MAPPINGS

### L4 Registry

#### Citizen

```yaml
domain_term: "Citizen"
maps_to:
  node_type: actor
  subtype: "citizen"

synthesis_template: |
  {name} — citizen of {org_name}, status: {status}

content_includes:
  - Capabilities list
  - Registration details

required_linked_things:
  - type: "name"
  - type: "org_membership"
  - type: "status"
  - type: "registered_date"

optional_linked_things:
  - type: "wallet"
  - type: "capabilities"
```

#### Org

```yaml
domain_term: "Org"
maps_to:
  node_type: space
  subtype: "org"

synthesis_template: |
  {name} — {org_type} organization ({universe}), {citizen_count} citizens, status: {status}

content_includes:
  - Organization description and mission
  - Org type and universe
  - Service offerings

required_linked_things:
  - type: "name"
  - type: "org_type"       # project | community | public-interest | guild
  - type: "wallet"
  - type: "endpoint"
  - type: "jwt_public_key"
  - type: "status"
  - type: "registered_date"

optional_linked_things:
  - type: "description"          # purpose and mission
  - type: "universe"             # lumina-prime | la-serenissima | contre-terre | the-blood-ledger | babys
  - type: "github_repository"    # GitHub repo (thing node with URI)
```

#### Endpoint

```yaml
domain_term: "Endpoint"
maps_to:
  node_type: thing
  subtype: "endpoint"

synthesis_template: |
  WebSocket endpoint for {org_name}

content_includes:
  - Full wss:// URL
```

#### Registry Properties (linked nodes)

**Concepts → narrative**
```yaml
domain_term: "name | status | org_membership | registered_date | capabilities"
maps_to:
  node_type: narrative
  subtype: "{property_name}"

synthesis_template: |
  {property_name} for {parent_name}

content_includes:
  - The conceptual value
```

**Artifacts → thing**
```yaml
domain_term: "wallet | endpoint | jwt_public_key"
maps_to:
  node_type: thing
  subtype: "{property_name}"

synthesis_template: |
  {property_name} for {parent_name}

content_includes:
  - The actual artifact (address, URL, key)
```

#### Verifier

```yaml
domain_term: "Verifier"
maps_to:
  node_type: actor
  subtype: "verifier"

synthesis_template: |
  {name} — L4 verification authority

content_includes:
  - Verification scope
  - Authority level
```

---

## LINK MAPPINGS

### Citizen → Org (membership)

```yaml
domain_relationship: "citizen belongs to org"
maps_to:
  polarity: [1.0, 0.5]      # citizen→org strong, org→citizen moderate
  hierarchy: 1.0             # org contains citizen
  permanence: 0.9            # stable membership
```

### Entity → Property (has property)

```yaml
domain_relationship: "entity has property"
maps_to:
  polarity: [1.0, 0.0]      # entity→property, not reverse
  hierarchy: 1.0             # entity contains property
  permanence: 0.8            # properties are stable
```

### Verifier → Entity (verification)

```yaml
domain_relationship: "verifier verified entity"
maps_to:
  polarity: [1.0, 0.0]      # 1.0 = verified, -1.0 = rejected
  hierarchy: 1.0             # verifier has authority
  permanence: [0.0-1.0]      # 0 = under review, 1 = permanent
```

---

## VERIFICATION STATUS (computed from link)

```python
def get_verification(entity_id: str) -> str:
    link = get_link(source_type="verifier", target=entity_id)

    if not link:
        return "unverified"
    elif link.polarity < 0:
        return "rejected"
    elif link.permanence < 0.5:
        return "provisional"
    else:
        return "verified"
```

---

## L3 UNIVERSE LINK DIMENSIONS

Every `:link` in every L3 universe graph carries **exactly 11 mandatory dimensions**. These are the SAME dimensions used on L1 cognitive links (see `manemus/docs/cognition/l1/PATTERNS_L1_Cognition.md`), **minus all limbic dimensions**. No custom fields are permitted. No universe adds or removes dimensions.

### The 11 Dimensions

| # | Dimension | Type | Range | L1 Equivalent |
|---|-----------|------|-------|---------------|
| 1 | `weight` | float | [0, 1] | `weight` |
| 2 | `energy` | float | [0, +inf) | `energy` |
| 3 | `stability` | float | [0, 1] | `stability` |
| 4 | `recency` | float | [0, 1] | `recency` |
| 5 | `polarity` | float | [-1, 1] | `gain` sign (implicit) |
| 6 | `hierarchy` | float | [-1, 1] | `contains`/`abstracts` link types (implicit) |
| 7 | `permanence` | float | [0, 1] | Node type durability (implicit) |
| 8 | `trust` | float | [0, 1] | `trust` on relational valence |
| 9 | `affinity` | float | [0, 1] | `affinity` on relational valence |
| 10 | `aversion` | float | [0, 1] | `aversion` on relational valence |
| 11 | `friction` | float | [0, 1] | `friction` on relational valence |

### What Is Excluded (L1-only dimensions)

The following L1 link dimensions are NOT present on L3 links:

- `relation_kind` (14-type enum) — L3 has one link type; semantics are in dimensions
- `valence` (emotional color) — emotions belong to L1 brains
- `ambivalence` (internal conflict) — cognitive state, L1 only
- `activation_gain` (propagation multiplier) — replaced by `polarity` at L3
- All drive-affinity dimensions (`goal_relevance`, `novelty_affinity`, `care_affinity`, `achievement_affinity`, `risk_affinity`) — drives are L1 limbic

### No Custom Fields

Domain-specific data (transaction amounts, commit SHAs, meeting durations) belongs in linked `thing` or `moment` nodes, NEVER as additional fields on the link. The link schema is fixed at 11 dimensions across all universes, all domains, all time.

**Why:** Physics laws (propagation, decay, consolidation, forgetting) operate on these 11 dimensions uniformly. Adding a custom field means either the physics ignores it (dead weight) or the physics must special-case it (complexity explosion). Neither is acceptable.

### Link Names Are Derived

The `type` field on `:link` is a DERIVED label computed from the dimensional vector via a synthesis grammar. It is NEVER the source of truth. Physics, queries, and consolidation operate on dimensions, not type names.

See: `docs/schema/universe_links/PATTERNS_Universe_Links.md` for the full synthesis grammar.

### Trust Lives on Links

Trust is a dimension on `:link`, not a property of nodes. An actor's "trust score" is computed at query time by aggregating incoming link trust values weighted by link weight. No node carries a `trust` or `reputation` field.

See: `docs/schema/universe_links/ALGORITHM_Universe_Links.md` for trust computation.

---

## Related

- `docs/TAXONOMY.md` — Term definitions
- `l4/schema/schema.yaml` — Schema constraints
- `docs/schema/universe_links/` — Full L3 Universe Link Schema doc chain
