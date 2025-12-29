# IMPLEMENTATION: L4 Registry

```
STATUS: IMPLEMENTED
PURPOSE: Code architecture for registry module
UPDATED: 2024-12-29
```

---

## Architecture

**L4 Registry = Nodes in Neo4j. No API. All graph queries.**

```
Membrane (mind-ops)                    Neo4j
     │                                   │
     │  graph query: find citizen        │
     ├──────────────────────────────────►│
     │                                   │
     │◄──────────────────────────────────┤
     │  returns: ActorNode + linked      │
     │                                   │
     │  graph query: verify hash         │
     ├──────────────────────────────────►│
     │                                   │
     │◄──────────────────────────────────┤
     │  returns: match true/false        │
```

**Key insight:** There is no L4 API. The registry IS nodes in Neo4j. Membrane queries the graph directly via `mind.graph.ops`.

---

## Directory Structure

```
l4/registry/
├── __init__.py                              # Exports all registry functions
├── citizen_registration_crud_operations.py  # Citizen models + node creation
├── org_registration_crud_operations.py      # Org models + node creation
├── endpoint_registration_and_management.py  # Endpoint validation
└── jwt_hash_verification_for_identity.py    # Hash computation + verification
```

---

## Key Files

### citizen_registration_crud_operations.py

```python
@dataclass
class CitizenRegistration:
    """Input for creating citizen nodes."""
    name: str
    org_id: str
    jwt_hash: str  # SHA256(JWT), never raw
    wallet: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)

@dataclass
class CitizenRecord:
    """Output when querying citizen."""
    id: str
    name: str
    org_id: str
    status: str  # "active" | "pending" | "suspended"
    registered_at: str
    wallet: Optional[str]
    capabilities: List[str]
    verification_status: str  # computed from links

def create_citizen_nodes(registration: CitizenRegistration) -> tuple:
    """
    Create graph nodes for a citizen.
    Returns: (citizen_node, property_nodes, links)
    Caller persists to graph via mind.graph.ops
    """
```

### org_registration_crud_operations.py

```python
@dataclass
class OrgRegistration:
    """Input for creating org nodes."""
    name: str
    wallet: str           # Solana address - required
    endpoint_url: str     # wss:// URL - required
    jwt_public_key: str   # For hash verification

def create_org_nodes(registration: OrgRegistration) -> tuple:
    """
    Create graph nodes for an org.
    Returns: (org_node, property_nodes, links)
    """
```

### jwt_hash_verification_for_identity.py

```python
def compute_hash(jwt: str, node_id: str) -> str:
    """
    Hash formula: SHA256(JWT + node_id)
    Used by membrane to verify cross-org stimuli.
    """
    return hashlib.sha256(f"{jwt}{node_id}".encode()).hexdigest()

def verify_hash(expected_hash: str, node_id: str, graph_lookup: callable) -> VerificationResult:
    """
    Verify hash against registry.
    graph_lookup queries Neo4j for stored hash.
    """
```

---

## Data Flow: Registration

```
1. Membrane receives register_org() call
         │
         ▼
2. Membrane calls create_org_nodes() from l4/registry
         │
         ▼
3. create_org_nodes() returns (SpaceNode, property_nodes, links)
         │
         ▼
4. Membrane persists to Neo4j via mind.graph.ops.create_node()
         │
         ▼
5. The org now EXISTS in the registry (it's a node in Neo4j)
         │
         ▼
6. Membrane emits event "registered"
```

**No API call.** The registry is the graph. Creating nodes = registering.

---

## Data Flow: Hash Verification

```
1. Stimulus arrives with hash = SHA256(JWT + node_id)
         │
         ▼
2. Membrane queries Neo4j: find citizen node by node_id
         │
         ▼
3. Traverse to linked thing node (type="jwt_hash")
         │
         ▼
4. Compare stored hash with stimulus hash
         │
         ▼
5. Return VerificationResult(valid=True/False)
```

**No API call.** Just graph traversal.

---

## Storage

The registry stores in Neo4j as regular nodes:

| Entity | Node Type | Subtype |
|--------|-----------|---------|
| Citizen | `actor` | `type: "citizen"` |
| Org | `space` | `type: "org"` |
| Endpoint | `thing` | `type: "endpoint"` |
| Wallet | `thing` | `type: "wallet"` |
| JWT Key | `thing` | `type: "jwt_public_key"` |
| Name | `narrative` | `type: "name"` |
| Status | `narrative` | `type: "status"` |

Links:
- Citizen → Org: `link` with `hierarchy: 1` (belongs to)
- Org → Endpoint: `link` with `hierarchy: 1` (has)
- Entity → Property: `link` with `hierarchy: 1` (has)

---

## Integration

| Consumer | What They Do | How |
|----------|--------------|-----|
| Membrane (spaces.py) | Register org | `create_org_nodes()` + `mind.graph.ops.create_node()` |
| Membrane (spaces.py) | Register citizen | `create_citizen_nodes()` + `mind.graph.ops.create_node()` |
| Membrane (hash_check.py) | Verify hash | `compute_hash()` + graph query |
| Membrane (routing) | Get endpoint | Graph traversal: org → endpoint thing |

**All via graph queries. No HTTP API.**

---

## Dependencies

| Package | Purpose |
|---------|---------|
| pydantic | Model validation (NodeBase, LinkBase) |
| hashlib | SHA256 hashing |
| mind.graph.ops | Graph CRUD (used by membrane) |

---

## Related

- `l4/schema/` — Base node/link models
- `ALGORITHM_Registry.md` — Registration procedures
- `PATTERNS_Registry.md` — Design philosophy
