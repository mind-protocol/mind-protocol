# IMPLEMENTATION: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Code architecture for schema module
```

---

## Directory Structure

```
l4/schema/
├── __init__.py          # Exports: Schema, validate_node, validate_link
├── schema.yaml          # Canonical schema definition (source of truth)
├── models.py            # Pydantic models generated from schema
├── validators.py        # Validation functions
└── loader.py            # Schema loading and version checking
```

---

## Key Files

### schema.yaml

The canonical schema definition. All other files derive from this.

```yaml
version: "1.8.1"
node_types:
  - actor
  - moment
  - narrative
  - space
  - thing
link_type: link
# ... full schema definition
```

### models.py

Pydantic models for type-safe node and link creation.

```python
from pydantic import BaseModel, Field, validator

class NodeBase(BaseModel):
    id: str
    node_type: Literal["actor", "moment", "narrative", "space", "thing"]
    weight: float = Field(ge=0)
    energy: float = Field(ge=0)
    type: Optional[str] = None  # subtype
    content: Optional[str] = None
    synthesis: Optional[str] = None
    embedding: Optional[List[float]] = None

class Link(BaseModel):
    source_id: str
    target_id: str
    polarity: float = Field(ge=-1, le=1)
    hierarchy: float = Field(ge=-1, le=1)
    permanence: float = Field(ge=0, le=1)
```

### validators.py

```python
def validate_node(node: dict) -> ValidationResult:
    """Validate node against schema invariants."""
    ...

def validate_link(link: dict) -> ValidationResult:
    """Validate link against schema invariants."""
    ...

def validate_graph(graph: dict) -> List[ValidationResult]:
    """Validate entire graph."""
    ...
```

### loader.py

```python
def load_schema(path: str = None) -> Schema:
    """Load and parse schema.yaml."""
    ...

def check_version(local: str, protocol: str) -> VersionCompatibility:
    """Check version compatibility."""
    ...
```

---

## Data Flow

```
schema.yaml
    ↓ (parsed by)
loader.py
    ↓ (generates)
models.py (Pydantic classes)
    ↓ (used by)
validators.py
    ↓ (exported via)
__init__.py → External consumers
```

---

## Integration Points

| Consumer | What They Use | How |
|----------|---------------|-----|
| mind-mcp | Schema version, models | Import from l4.schema |
| mind-ops | Validators | Import validate_* functions |
| Client repos | .mind/schema.yaml | Copy from templates/ |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| pydantic | Model validation |
| pyyaml | Schema parsing |

---

## Related

- `templates/mind/schema.yaml` — Template for client repos
- `ALGORITHM_Schema.md` — Validation procedures
- `HEALTH_Schema.md` — Runtime checks
