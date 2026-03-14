# Wallet Recovery — Validation: What Must Be True

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
PATTERNS:        ./PATTERNS_Wallet_Recovery.md
BEHAVIORS:       ./BEHAVIORS_Wallet_Recovery.md
THIS:            VALIDATION_Wallet_Recovery.md (you are here)
ALGORITHM:       ./ALGORITHM_Wallet_Recovery.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wallet_Recovery.md
HEALTH:          ./HEALTH_Wallet_Recovery.md
SYNC:            ./SYNC_Wallet_Recovery.md
```

---

## PURPOSE

**Validation = what we care about being true.**

A citizen must never permanently lose funds due to key loss. The wallet change procedure must be secure against impersonation but fast for legitimate requests. Every change must be traceable.

---

## INVARIANTS

### V1: No Funds Left Behind

**Why we care:** If any $MIND remains in the old wallet after a change, the citizen has effectively lost those funds (they can't access the old wallet).

```
MUST:   After successful wallet change, old wallet balance == 0
NEVER:  Partial transfer that leaves funds stranded
```

### V2: Identity Verification Is Mandatory

**Why we care:** Without verification, anyone could claim to be a citizen and redirect their funds to a wallet they control.

```
MUST:   Every wallet change verifies SHA256(JWT × node_id) against registry
NEVER:  A wallet change proceeds without identity verification passing
```

### V3: Registry Consistency

**Why we care:** If the registry points to the old wallet after a change, the citizen's economic identity is broken — membrane fees, UBC, rewards all go to the wrong address.

```
MUST:   After successful wallet change, registry wallet == new wallet address
NEVER:  Registry pointing to old wallet after successful change
```

### V4: Audit Trail Exists

**Why we care:** Without audit trails, there's no way to investigate disputed changes or detect attack patterns.

```
MUST:   Every wallet change attempt (success or failure) creates a moment node
NEVER:  A wallet change that leaves no trace in the graph
```

### V5: No Duplicate Wallet Addresses

**Why we care:** Two citizens sharing the same wallet would create economic chaos — whose funds are whose?

```
MUST:   Each wallet address maps to at most one citizen in the registry
NEVER:  Two different citizens with the same wallet address
```

### V6: Atomicity

**Why we care:** If the transfer succeeds but the registry update fails (or vice versa), the citizen is in a broken state.

```
MUST:   Transfer + registry update either both succeed or both fail
NEVER:  Transfer without registry update, or registry update without transfer
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | No funds left behind | CRITICAL |
| V2 | Identity verification mandatory | CRITICAL |
| V3 | Registry consistency | CRITICAL |
| V4 | Audit trail exists | HIGH |
| V5 | No duplicate wallet addresses | HIGH |
| V6 | Atomicity of transfer + registry | CRITICAL |

---

## MARKERS

<!-- @mind:todo Define what "atomicity" means in practice across Solana + FalkorDB (no shared transaction) -->
