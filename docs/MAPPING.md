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
  {name} — organization with {citizen_count} citizens, status: {status}

content_includes:
  - Organization description
  - Service offerings

required_linked_things:
  - type: "name"
  - type: "wallet"
  - type: "endpoint"
  - type: "jwt_public_key"
  - type: "status"
  - type: "registered_date"
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

## Related

- `docs/TAXONOMY.md` — Term definitions
- `l4/schema/schema.yaml` — Schema constraints
