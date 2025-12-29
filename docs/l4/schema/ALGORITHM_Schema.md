# ALGORITHM: L4 Schema

```
STATUS: DESIGNING
PURPOSE: How schema validation and enforcement works
```

---

## Schema Validation Process

```
PROCEDURE validate_node(node):
    1. Check node_type in ALLOWED_TYPES
       - ALLOWED_TYPES = ["actor", "moment", "narrative", "space", "thing"]
       - If not → REJECT with "Invalid node_type"

    2. Check required fields present
       - Required: id, node_type, weight, energy
       - If missing → REJECT with "Missing required field: {field}"

    3. Check field ranges
       - weight >= 0
       - energy >= 0
       - If out of range → CLAMP or REJECT based on config

    4. Validate optional fields if present
       - type: string or null
       - synthesis: string or null
       - embedding: float[] or null

    5. ACCEPT node
```

```
PROCEDURE validate_link(link):
    1. Link type must be "link"
       - If not → REJECT with "Only 'link' type allowed"

    2. Check required fields
       - Required: source_id, target_id, polarity, hierarchy, permanence

    3. Check field ranges
       - polarity in [-1, 1]
       - hierarchy in [-1, 1]
       - permanence in [0, 1]
       - If out of range → CLAMP or REJECT

    4. Validate source and target exist
       - If not → REJECT with "Invalid reference"

    5. ACCEPT link
```

---

## Schema Loading

```
PROCEDURE load_schema(source):
    1. Determine source location
       - Local: .mind/schema.yaml
       - Protocol: l4/schema/schema.yaml
       - Remote: https://github.com/mind-protocol/mind-protocol (future)

    2. Parse YAML

    3. Validate schema version matches expected
       - Current: 1.8.1

    4. Build validators from schema definition
       - Node validators by type
       - Link validator
       - Range checkers

    5. Return SchemaValidator instance
```

---

## Pydantic Model Generation

```
PROCEDURE generate_pydantic_models(schema):
    1. For each node_type in schema.node_types:
       - Create Pydantic model class
       - Add required fields with types
       - Add optional fields with defaults
       - Add validators for ranges

    2. Create Link model
       - Single class for all links
       - Properties determine semantics

    3. Create SubEntity model (for Moments)

    4. Export models for import
```

---

## Version Checking

```
PROCEDURE check_version_compatibility(local_version, protocol_version):
    1. Parse semver: major.minor.patch

    2. If major differs → INCOMPATIBLE (breaking change)

    3. If minor differs → COMPATIBLE with warnings (new features)

    4. If only patch differs → COMPATIBLE (bug fixes)

    5. Return compatibility status
```

---

## Related

- `VALIDATION_Schema.md` — What must be true
- `IMPLEMENTATION_Schema.md` — Where code lives
- `l4/schema/models.py` — Pydantic models (future)
