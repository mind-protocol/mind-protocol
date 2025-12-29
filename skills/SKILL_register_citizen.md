# Skill: Register Citizen

```
MODULE: l4/registry
PROCEDURE: procedures/procedure_register_citizen.yaml
STATUS: IMPLEMENTED
```

---

## Purpose

Register a new citizen under an organization in the L4 registry. Verifies JWT signature, creates citizen node with all required properties (synthesis, hashes, status).

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `citizen_id` | str | Yes | Unique citizen identifier |
| `synthesis` | str | Yes | Description of the citizen (searchable) |
| `org_id` | str | Yes | Parent organization ID |
| `jwt` | str | Yes | JWT signed by org's private key |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `citizen_id` | str | The registered citizen ID |
| `identity_hash` | str | Hash for stimulus verification |
| `success` | bool | Whether registration succeeded |
| `error` | str? | Error message if failed |

---

## Graph Result

```
[Actor: citizen]
     │
     ├──LINK──► [Narrative: synthesis]
     │            content="AI agent for customer support"
     │
     ├──LINK──► [Narrative: status]
     │            content="active"
     │
     ├──LINK──► [Narrative: visibility]
     │            content="public"
     │
     ├──LINK──► [Narrative: registered_date]
     │            content="2024-12-29T..."
     │
     ├──LINK──► [Thing: jwt_hash]
     │            content="sha256:a1b2c3..."
     │
     ├──LINK──► [Thing: identity_hash]
     │            content="sha256:d4e5f6..."
     │
     └──LINK──► [Space: org]
                  (belongs_to relationship)
```

---

## Example

```yaml
# Input
citizen_id: "citizen_abc123"
synthesis: "AI agent specializing in customer support"
org_id: "org_a1b2c3d4e5f6"
jwt: "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# Output
citizen_id: "citizen_abc123"
identity_hash: "sha256:d4e5f6g7h8i9j0..."
success: true
error: null
```

---

## Validation

- `jwt` must be signed by org's `jwt_public_key`
- `jwt` claims must be valid (exp > now, iat < now, iss == org_id)
- `org_id` must exist and be active
- `citizen_id` must be unique

---

## Errors

| Error | Cause |
|-------|-------|
| "Invalid JWT signature" | JWT not signed by org's key |
| "JWT expired" | exp claim in past |
| "Org not found" | org_id doesn't exist in registry |
| "Org suspended" | org status is not active |
| "Citizen already exists" | citizen_id already registered |

---

## Identity Hash

The identity hash is computed as:
```
identity_hash = SHA256(jwt + citizen_id)
```

This hash is used for stimulus verification:
- Citizen includes `identity_hash` in outbound stimuli
- Receiving membrane verifies hash matches stored value
- Prevents impersonation without access to original JWT

---

## Related

- `SKILL_register_org.md` — Register org (must exist first)
- `SKILL_verify_identity.md` — Verify citizen identity
- `procedure_register_citizen.yaml` — Procedure definition
