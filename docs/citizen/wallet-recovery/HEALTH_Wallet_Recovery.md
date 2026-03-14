# Wallet Recovery — Health: Verification Mechanics

```
STATUS: DRAFT
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
PATTERNS:        ./PATTERNS_Wallet_Recovery.md
BEHAVIORS:       ./BEHAVIORS_Wallet_Recovery.md
ALGORITHM:       ./ALGORITHM_Wallet_Recovery.md
VALIDATION:      ./VALIDATION_Wallet_Recovery.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wallet_Recovery.md
THIS:            HEALTH_Wallet_Recovery.md (you are here)
SYNC:            ./SYNC_Wallet_Recovery.md

IMPL:            (no health checker yet)
```

---

## PURPOSE

This HEALTH file verifies that wallet recovery operates correctly in production: no funds left behind, registry stays consistent, audit trail exists for every change. These checks catch drift that unit tests cannot — e.g., a Solana transaction that succeeds but registry update that silently fails.

---

## WHY THIS PATTERN

Tests verify the algorithm in isolation. Health checks verify the system in production:
- Did the old wallet actually reach zero balance after the change?
- Does the registry actually point to the wallet that holds the funds?
- Do audit moments exist for every wallet change event?

---

## HEALTH INDICATORS SELECTED

```yaml
health_indicators:
  - name: old_wallet_drained
    flow_id: wallet_change
    priority: high
    rationale: If old wallet retains balance after change, citizen has lost funds (V1)
  - name: registry_wallet_consistency
    flow_id: wallet_change
    priority: high
    rationale: If registry wallet != wallet holding funds, economic identity is broken (V3)
  - name: audit_trail_completeness
    flow_id: wallet_change
    priority: med
    rationale: Missing audit moments mean we can't investigate disputed changes (V4)
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: wallet_change_funds_check
    purpose: Verify old wallets are drained after changes (V1)
    status: pending
    priority: high
  - name: registry_wallet_match
    purpose: Verify registry wallet matches actual token holder (V3)
    status: pending
    priority: high
  - name: wallet_change_audit_check
    purpose: Verify audit moments exist for all wallet changes (V4)
    status: pending
    priority: med
```

---

## KNOWN GAPS

<!-- @mind:todo Implement wallet_change_funds_check checker -->
<!-- @mind:todo Implement registry_wallet_match checker -->
<!-- @mind:todo Implement wallet_change_audit_check checker -->

---

## MARKERS

<!-- @mind:todo All three checkers are pending — implement after code exists -->
