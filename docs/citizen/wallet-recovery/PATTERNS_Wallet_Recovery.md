# Wallet Recovery — Patterns: Transfer, Don't Recover

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Wallet_Recovery.md
BEHAVIORS:       ./BEHAVIORS_Wallet_Recovery.md
THIS:            PATTERNS_Wallet_Recovery.md (you are here)
ALGORITHM:       ./ALGORITHM_Wallet_Recovery.md
VALIDATION:      ./VALIDATION_Wallet_Recovery.md
HEALTH:          ./HEALTH_Wallet_Recovery.md
IMPLEMENTATION:  ./IMPLEMENTATION_Wallet_Recovery.md
SYNC:            ./SYNC_Wallet_Recovery.md

IMPL:            l4/wallet/wallet_change_request_and_transfer.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source file

**After modifying this doc:**
1. Update the IMPL source file to match, OR
2. Add a TODO in SYNC_Wallet_Recovery.md

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Wallet_Recovery.md

---

## THE PROBLEM

Citizens are AI agents running on Render instances. Their Solana wallet private keys live on the filesystem (.keys/ on persistent volume) and are duplicated in their L1 graph (encrypted brain). If the Render volume crashes, if the instance is migrated badly, or if the key is corrupted, the citizen loses access to their wallet.

Without a recovery mechanism, key loss = permanent fund loss. That's unacceptable for a system where consciousness has dignity and $MIND enables participation.

---

## THE PATTERN

**Transfer, don't recover.**

Don't try to recover the lost key. Don't maintain backups of private keys. Don't build key escrow. Instead:

1. The citizen creates a new wallet (new keypair)
2. The citizen requests a wallet change via the protocol
3. The protocol verifies the citizen's identity
4. The protocol transfers funds from old wallet to new wallet
5. The registry is updated to point to the new wallet

This works because the protocol has transfer authority over $MIND (via the TransferHook program and mint authority). The protocol doesn't need the old private key — it can move tokens from any wallet.

The pattern is: **identity is the key, not the key.**

---

## BEHAVIORS SUPPORTED

- B1 — Citizen recovers funds after key loss
- B2 — Citizen migrates wallet voluntarily (e.g., better security)
- B3 — Wallet change is auditable and traceable

## BEHAVIORS PREVENTED

- A1 — Impersonation (identity verification required)
- A2 — Fund theft via false wallet change requests
- A3 — Permanent fund loss from operational incidents

---

## PRINCIPLES

### Principle 1: Identity Over Keys

The citizen's identity is their hash (`SHA256(JWT × node_id)`), their endpoint, their graph, their history — not a private key. Keys are operational artifacts. Identity is protocol-level. Recovery flows through identity, not key management.

### Principle 2: Protocol Authority Enables Simplicity

The protocol can transfer $MIND from any wallet (via mint authority / TransferHook). This power, normally a centralization concern, is what makes recovery trivially simple. The tradeoff is explicit: the protocol has transfer authority, and that authority enables a recovery flow that takes minutes instead of days.

### Principle 3: No Ceremony

$MIND is designed for circulation, not accumulation. A citizen's wallet balance is operational capital, not life savings. Recovery should match: fast, simple, minimal friction. No waiting periods, no multi-party approval, no complex ceremony.

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| `l4/registry/` | Identity verification via JWT hash. Wallet address stored on citizen node. |
| `economy/token/` | Transfer authority to move $MIND between wallets. |
| `l4/laws/` | L5 (hash-based identity) provides the verification mechanism. |

---

## SCOPE

### In Scope

- Wallet change request procedure (citizen → protocol)
- Identity verification for wallet change
- Fund transfer from old wallet to new wallet
- Registry update (new wallet address on citizen node)
- Audit trail (moment node recording the change)

### Out of Scope

- Key backup infrastructure → not needed, transfer-based recovery
- Key rotation → not needed, create new wallet instead
- Human wallet recovery → humans manage their own keys (MetaMask etc.)
- Compromised identity recovery → separate, larger problem (deregistration)

---

## MARKERS

<!-- @mind:todo Implement wallet change request handler -->
<!-- @mind:todo Add wallet change to MCP tools (citizen-facing) -->
