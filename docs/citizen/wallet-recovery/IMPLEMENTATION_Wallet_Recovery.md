# Wallet Recovery — Implementation: Code Architecture

```
STATUS: DRAFT
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
BEHAVIORS:       ./BEHAVIORS_Wallet_Recovery.md
PATTERNS:        ./PATTERNS_Wallet_Recovery.md
ALGORITHM:       ./ALGORITHM_Wallet_Recovery.md
VALIDATION:      ./VALIDATION_Wallet_Recovery.md
THIS:            IMPLEMENTATION_Wallet_Recovery.md (you are here)
HEALTH:          ./HEALTH_Wallet_Recovery.md
SYNC:            ./SYNC_Wallet_Recovery.md

IMPL:            l4/wallet/wallet_change_request_and_transfer.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
l4/wallet/
├── __init__.py                                    # Exports: process_wallet_change_request
└── wallet_change_request_and_transfer.py          # Full wallet change flow
```

### File Responsibilities

| File | Purpose | Key Functions | Status |
|------|---------|---------------|--------|
| `wallet_change_request_and_transfer.py` | Wallet change procedure | `process_wallet_change_request()`, `verify_citizen_identity()`, `transfer_funds()` | PENDING |

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Pipeline — sequential steps with early exit on failure.

**Why this pattern:** Each step has a clear precondition (previous step passed). Failure at any point produces a clear, auditable result. No branching complexity.

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Wallet module | Change request logic, audit trail | Registry CRUD, token transfers | `process_wallet_change_request()` |

---

## SCHEMA

### WalletChangeRequest

```yaml
WalletChangeRequest:
  required:
    - citizen_id: str           # Registry citizen ID
    - new_wallet_address: str   # Solana base58 pubkey
    - identity_proof: str       # SHA256(JWT × node_id)
  optional:
    - reason: str               # "key_loss" | "migration" | "security"
  constraints:
    - new_wallet_address must be valid Solana base58
    - new_wallet_address must not belong to another citizen
```

### WalletChangeResult

```yaml
WalletChangeResult:
  required:
    - success: bool
    - citizen_id: str
  conditional:
    - old_wallet: str           # Present on success
    - new_wallet: str           # Present on success
    - amount_transferred: float # Present on success
    - moment_id: str            # Present always (audit)
    - error: str                # Present on failure
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `process_wallet_change_request` | `l4/wallet/wallet_change_request_and_transfer.py` | MCP tool call or API request |

---

## DATA FLOW AND DOCKING

### Wallet Change Flow: Identity → Validate → Transfer → Registry → Audit

This is the only flow. It transforms a wallet change request into a completed transfer with audit trail.

```yaml
flow:
  name: wallet_change
  purpose: Transfer citizen funds to new wallet and update registry
  scope: Single citizen, single wallet change
  steps:
    - id: verify_identity
      description: Verify citizen identity via L5 hash
      file: l4/wallet/wallet_change_request_and_transfer.py
      function: verify_citizen_identity
      input: citizen_id + identity_proof
      output: verified citizen or rejection
      trigger: process_wallet_change_request call
      side_effects: none
    - id: validate_wallet
      description: Check new wallet is valid and unregistered
      file: l4/wallet/wallet_change_request_and_transfer.py
      function: validate_new_wallet
      input: new_wallet_address
      output: validation result
      trigger: identity verified
      side_effects: none
    - id: transfer_funds
      description: Move all $MIND from old to new wallet
      file: l4/wallet/wallet_change_request_and_transfer.py
      function: transfer_funds
      input: old_wallet + new_wallet
      output: transfer result with tx signature
      trigger: wallet validated
      side_effects: Solana transaction
    - id: update_registry
      description: Point citizen record to new wallet
      file: l4/wallet/wallet_change_request_and_transfer.py
      function: update_registry
      input: citizen_id + new_wallet_address
      output: success
      trigger: funds transferred
      side_effects: FalkorDB write
    - id: create_audit
      description: Record wallet change as moment node
      file: l4/wallet/wallet_change_request_and_transfer.py
      function: create_audit_moment
      input: request + result
      output: moment_id
      trigger: registry updated (or on failure)
      side_effects: FalkorDB write
```

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
l4/wallet/
    └── imports → l4/registry/ (identity verification, wallet lookup/update)
    └── imports → economy/token/ (protocol transfer authority)
    └── imports → l4/schema/ (moment creation for audit)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `solana` | Transaction execution | `wallet_change_request_and_transfer.py` |

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1 | `l4/wallet/wallet_change_request_and_transfer.py:verify_citizen_identity` |
| ALGORITHM step 2 | `l4/wallet/wallet_change_request_and_transfer.py:validate_new_wallet` |
| ALGORITHM step 3 | `l4/wallet/wallet_change_request_and_transfer.py:transfer_funds` |
| ALGORITHM step 4 | `l4/wallet/wallet_change_request_and_transfer.py:update_registry` |
| ALGORITHM step 5 | `l4/wallet/wallet_change_request_and_transfer.py:create_audit_moment` |

---

## MARKERS

<!-- @mind:todo Implement wallet_change_request_and_transfer.py -->
<!-- @mind:todo Add MCP tool for citizen-facing wallet change -->
<!-- @mind:todo Write tests for all 6 validation invariants -->
