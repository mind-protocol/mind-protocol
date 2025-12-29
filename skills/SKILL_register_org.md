# Skill: Register Org

```
MODULE: l4/registry
PROCEDURE: procedures/procedure_register_org.yaml
STATUS: IMPLEMENTED
```

---

## Purpose

Register a new organization in the L4 registry. Creates org node with all required properties (endpoint, wallet, JWT public key).

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | str | Yes | Organization display name |
| `wallet` | str | Yes | Solana wallet address |
| `endpoint_url` | str | Yes | WebSocket URL (must be wss://) |
| `jwt_public_key` | str | Yes | Public key for JWT signature verification |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `org_id` | str | Generated org ID (e.g., `org_a1b2c3d4e5f6`) |
| `success` | bool | Whether registration succeeded |
| `error` | str? | Error message if failed |

---

## Graph Result

```
[Space: org]
     │
     ├──LINK──► [Narrative: name]
     │            content="Acme Corp"
     │
     ├──LINK──► [Narrative: status]
     │            content="active"
     │
     ├──LINK──► [Narrative: registered_date]
     │            content="2024-12-29T..."
     │
     ├──LINK──► [Thing: wallet]
     │            content="So1ana..."
     │
     ├──LINK──► [Thing: endpoint]
     │            content="wss://acme.com/ws"
     │
     └──LINK──► [Thing: jwt_public_key]
                  content="-----BEGIN PUBLIC KEY-----..."
```

---

## Example

```yaml
# Input
name: "Acme Corp"
wallet: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
endpoint_url: "wss://api.acme.com/ws"
jwt_public_key: "-----BEGIN PUBLIC KEY-----\nMIIBIjAN..."

# Output
org_id: "org_a1b2c3d4e5f6"
success: true
error: null
```

---

## Validation

- `endpoint_url` must start with `wss://`
- `wallet` should be valid Solana address format
- `jwt_public_key` should be valid PEM format

---

## Errors

| Error | Cause |
|-------|-------|
| "Endpoint must be wss:// URL" | Invalid endpoint format |
| "Org ID already exists" | Duplicate registration |

---

## Related

- `SKILL_register_citizen.md` — Register citizen under org
- `SKILL_update_endpoint.md` — Change org endpoint
- `procedure_register_org.yaml` — Procedure definition
