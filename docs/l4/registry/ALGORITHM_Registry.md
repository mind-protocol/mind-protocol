# ALGORITHM: L4 Registry

```
STATUS: IMPLEMENTED
PURPOSE: How registration and verification works
UPDATED: 2024-12-29
```

---

## Citizen Registration

```
PROCEDURE register_citizen(citizen_data, org_id):
    1. Validate citizen_data
       - Required: id, synthesis, jwt
       - If missing → REJECT "Missing required field"

    2. Check org exists
       - Query: GET org by org_id
       - If not found → REJECT "Org not registered"

    3. Check citizen ID unique
       - Query: GET citizen by id
       - If found → REJECT "Citizen ID already exists"

    4. Hash JWT for storage
       - stored_hash = hash_for_storage(jwt)
       - Never store raw JWT

    5. Create citizen record
       - citizen.id = citizen_data.id
       - citizen.synthesis = citizen_data.synthesis
       - citizen.org_id = org_id
       - citizen.jwt_hash = stored_hash

    6. Link to org
       - org.citizens.append(citizen.id)

    7. RETURN citizen.id
```

---

## Org Registration

```
PROCEDURE register_org(org_data):
    1. Validate org_data
       - Required: id, name, endpoint_url
       - If missing → REJECT "Missing required field"

    2. Validate endpoint
       - Must be valid WebSocket URL (wss://)
       - Attempt connection test (optional)
       - If invalid → REJECT "Invalid endpoint URL"

    3. Check org ID unique
       - Query: GET org by id
       - If found → REJECT "Org ID already exists"

    4. Create org record
       - org.id = org_data.id
       - org.name = org_data.name
       - org.citizens = []

    5. Create endpoint record
       - endpoint.id = generate_id()
       - endpoint.url = org_data.endpoint_url
       - endpoint.org_id = org.id

    6. RETURN org.id
```

---

## Hash Verification

```
PROCEDURE verify_identity(hash, node_id):
    1. Look up citizen
       - Query: GET citizen by ID matching node_id
       - If not found → RETURN {valid: false, reason: "Unknown citizen"}

    2. Retrieve stored JWT (or hash)
       - citizen.jwt_hash

    3. Compute expected hash
       - expected = SHA256(citizen.jwt_hash × node_id)
       - Note: This assumes JWT is hashed on storage

    4. Compare
       - If hash == expected → RETURN {valid: true, citizen: citizen}
       - Else → RETURN {valid: false, reason: "Hash mismatch"}
```

---

## Endpoint Lookup (Org)

```
PROCEDURE get_endpoint_for_org(org_id):
    1. Query: GET org by org_id
       - If not found → RETURN null

    2. Query: GET endpoint where endpoint.org_id == org_id
       - If not found → RETURN null

    3. RETURN endpoint.url
```

---

## Citizen Endpoint Registration

A citizen can have N endpoints (one per repo/instance they work on).
Each endpoint is a Thing node with type="citizen_endpoint" linked from
the citizen's Actor node via a SERVES link.

```
PROCEDURE add_citizen_endpoint(citizen_id, endpoint_url, repo_name, instance_id?):
    1. Validate endpoint_url
       - Must be wss:// (secure WebSocket)
       - If invalid → REJECT "Invalid endpoint URL"

    2. Compute deterministic endpoint ID
       - endpoint_id = "{citizen_id}_endpoint_{repo_name}"
       - This ensures MERGE semantics: re-registering same citizen+repo = update

    3. Create endpoint Thing node
       - id = endpoint_id
       - type = "citizen_endpoint"
       - content = endpoint_url (wss://...)
       - uri = endpoint_url
       - synthesis = "Service endpoint for {citizen_id} on {repo_name}"

    4. Create SERVES link
       - link_id = "{citizen_id}_serves_{repo_name}"
       - node_a = citizen_id (Actor)
       - node_b = endpoint_id (Thing)
       - hierarchy = 1.0 (endpoint belongs to citizen)
       - permanence = 0.6 (endpoints can change)

    5. Persist to L4 graph (MERGE — update if exists)

    6. RETURN (endpoint_node, link)

PROCEDURE remove_citizen_endpoint(citizen_id, repo_name):
    1. Compute deterministic IDs
       - endpoint_id = "{citizen_id}_endpoint_{repo_name}"
       - link_id = "{citizen_id}_serves_{repo_name}"

    2. Delete endpoint Thing node and SERVES link from graph

    3. RETURN success
```

---

## Citizen Endpoint Resolution

When the membrane needs to route a message/call to a citizen, it resolves
all active endpoints. A citizen may have multiple endpoints (one per repo).

```
PROCEDURE resolve_citizen_endpoints(citizen_id):
    1. Query L4 graph for citizen
       - If not found → RETURN error "Unknown citizen"

    2. Get direct citizen endpoints
       - Query: GET linked Things where type="citizen_endpoint"
       - For each: extract (url, repo_name)
       - These are priority 1

    3. Get org fallback endpoint
       - Query: GET citizen's org_id from org_membership node
       - Query: GET org endpoint where type="endpoint"
       - This is priority 2 (only used if no direct endpoints)

    4. Build sorted endpoint list
       - Direct endpoints first (type="direct")
       - Org endpoint last (type="org", only if no directs)

    5. RETURN list of {url, repo_name, type}

Graph structure (follow the links):

[Actor: citizen] ───SERVES──► [Thing: citizen_endpoint]
     │                         type="citizen_endpoint"
     │                         content="wss://cities-of-light.onrender.com/ws"
     │                         id="{citizen_id}_endpoint_cities-of-light"
     │
     ├───SERVES──► [Thing: citizen_endpoint]
     │              type="citizen_endpoint"
     │              content="wss://venezia.onrender.com/ws"
     │              id="{citizen_id}_endpoint_venezia"
     │
     └───LINK───► [Narrative: org_membership]
                   content="org_xyz"
                        │
                        └──► [Space: org] ──LINK──► [Thing: endpoint]
                                                     content="wss://org-fallback.com/ws"
```

---

## JWT Handling

```
PROCEDURE hash_for_storage(jwt):
    # Never store raw JWT
    # Store a secure hash that can be used for verification
    RETURN SHA256(jwt + SALT)

PROCEDURE hash_for_transmission(jwt, node_id):
    # This is what gets sent in stimuli
    RETURN SHA256(jwt × node_id)
```

---

## Inbound Stimulus Verification

When a stimulus arrives from another org, membrane verifies identity and gets the destination endpoint via graph traversal.

```
PROCEDURE verify_inbound_stimulus(stimulus):
    1. Extract identity info
       - hash = stimulus.identity_hash
       - sender_id = stimulus.sender_id
       - dest_org_id = stimulus.dest_org_id

    2. Traverse graph via MCP ops (no Cypher)
       - sender = graph.get_node(sender_id)
       - hash_node = graph.get_linked(sender_id, type="identity_hash")
       - status_node = graph.get_linked(sender_id, type="status")
       - endpoint_node = graph.get_linked(dest_org_id, type="endpoint")

    3. Verify sender exists
       - If sender not found → REJECT "Unknown sender"

    4. Verify sender not suspended
       - If status_node.content == "suspended" → REJECT "Sender suspended"

    5. Verify hash matches
       - If hash_node.content != hash → REJECT "Invalid hash"

    6. Return destination endpoint
       - RETURN endpoint_node.content (wss://...)

Graph physics does the work — just follow the links.
```

---

## JWT Signature Verification (Registration)

When an org registers a citizen, membrane verifies the JWT signature using the org's public key stored in L4.

```
PROCEDURE verify_jwt_for_registration(jwt, org_id):
    1. Get org's public key via graph traversal
       - key_node = graph.get_linked(org_id, type="jwt_public_key")

    2. If org not found
       - REJECT "Unknown org"

    3. If public key not found
       - REJECT "Org has no public key"

    4. Verify JWT signature
       - Decode JWT header to get algorithm (RS256, ES256, etc.)
       - Verify signature using key_node.content
       - If invalid → REJECT "Invalid JWT signature"

    5. Verify JWT claims
       - Check exp (expiration) is in future
       - Check iat (issued at) is in past
       - Check iss (issuer) matches org_id
       - If invalid → REJECT with specific reason

    6. RETURN {valid: true, claims: jwt.payload}

Graph structure holds the key — just follow the link.
```

---

## Complete Registration Flow

```
PROCEDURE register_citizen_with_verification(registration, jwt):
    1. Verify JWT signature
       - result = verify_jwt_for_registration(jwt, registration.org_id)
       - If not valid → REJECT result.error

    2. Hash JWT for storage
       - jwt_hash = SHA256(jwt)
       - Never store raw JWT

    3. Compute identity hash
       - citizen_id = generate_citizen_id()
       - identity_hash = SHA256(jwt + citizen_id)
       - This hash will be used for stimulus verification

    4. Create citizen nodes
       - citizen_node = ActorNode(id=citizen_id, type="citizen", ...)
       - hash_node = ThingNode(type="hash", content=identity_hash)
       - Link citizen → hash_node

    5. Persist to L4 graph

    6. RETURN citizen_id
```

---

## Endpoint Location

**Endpoints live in L4 registry (not membrane).**

Rationale:
- Endpoint is identity data (like name, wallet, public key)
- Single source of truth in L4
- Membrane already traverses L4 for hash verification
- Same traversal gets endpoint — no extra ops

### Org Endpoints (single per org)

```
Graph structure (follow the links):

[Space: org] ─────LINK────► [Thing: endpoint]
     │                        content="wss://client.com/ws"
     │
     ├────LINK────► [Thing: jwt_public_key]
     │                content="-----BEGIN PUBLIC KEY-----..."
     │
     ├────LINK────► [Thing: wallet]
     │                content="So1anaWa11etAddress..."
     │
     └────LINK────► [Narrative: status]
                      content="active"

Get endpoint: graph.get_linked(org_id, type="endpoint")
Graph physics does the work.
```

### Citizen Endpoints (multiple per citizen, one per repo)

A citizen can work on multiple repos. Each repo deployment creates a
separate MCP server instance with its own WebSocket endpoint.

```
Graph structure (follow the links):

[Actor: citizen] ───SERVES──► [Thing: citizen_endpoint]
     │                         type="citizen_endpoint"
     │                         id="{cid}_endpoint_cities-of-light"
     │                         content="wss://cities-of-light.onrender.com/ws"
     │
     ├───SERVES──► [Thing: citizen_endpoint]
     │              type="citizen_endpoint"
     │              id="{cid}_endpoint_venezia"
     │              content="wss://venezia.onrender.com/ws"
     │
     ├────LINK────► [Narrative: org_membership]
     │                content="org_xyz"
     │
     └────LINK────► [Thing: identity_hash]
                      content="sha256..."

Get all endpoints: graph.get_linked(citizen_id, type="citizen_endpoint")
Get specific repo: graph.get_node("{citizen_id}_endpoint_{repo_name}")
Fallback to org:   graph.get_linked(org_id, type="endpoint")
```

---

## Related

- `VALIDATION_Registry.md` — Invariants
- `IMPLEMENTATION_Registry.md` — Code structure
- `docs/l4/laws/PATTERNS_Laws.md` — L5 (Hash-based identity)
