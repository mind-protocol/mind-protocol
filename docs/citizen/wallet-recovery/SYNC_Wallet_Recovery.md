# Wallet Recovery — Sync: Current State

```
LAST_UPDATED: 2026-03-14
UPDATED_BY: Claude Opus (groundwork)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Pattern: Transfer, don't recover (identity is the key, not the key)
- Procedure: verify identity → validate wallet → transfer funds → update registry → audit
- 6 invariants defined (V1-V6)
- Full doc chain created

**What's still being designed:**
- Implementation (code not yet written)
- MCP tool for citizen-facing wallet change
- Rate limiting strategy
- Atomicity across Solana + FalkorDB (no shared transaction — need compensation strategy)

**What's proposed (v2+):**
- Batch wallet migration (many citizens at once, e.g., instance migration)
- Human wallet recovery (different flow, lower priority)

---

## CURRENT STATE

Full documentation chain created. No code yet. The module is ready for implementation — the algorithm, validation invariants, and data structures are defined. Implementation depends on existing registry and token modules.

---

## RECENT CHANGES

### 2026-03-14: Module Created

- **What:** Created wallet-recovery doc chain (8 files)
- **Why:** Nicolas identified that wallet change is a protocol-level procedure. Key loss recovery = protocol transfers funds to new wallet. Simple, no ceremony.
- **Key decisions:**
  - Transfer, don't recover (no key backup infrastructure)
  - Identity verification via L5 hash (same as all protocol identity)
  - No waiting period ($MIND is for circulation)
  - Full balance transfer only (no partial)
  - Audit trail mandatory (moment nodes for every attempt)

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (implementation)

**What's done:** Complete doc chain. Algorithm is precise pseudocode — translate to Python.

**What you need to understand:**
- This module calls into `l4/registry/` for identity verification and wallet updates
- It calls into `economy/token/` for the actual Solana transfer
- The protocol has transfer authority (via mint authority / TransferHook)
- Audit moments are standard L4 graph operations

**Watch out for:**
- Atomicity: Solana transfer and FalkorDB registry update are separate transactions. If one fails after the other succeeds, you need a compensation strategy (log the inconsistency, retry the failed part).
- The `execute_protocol_transfer` function may not exist yet — check economy/token/ for what's available.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Wallet recovery module fully documented. Pattern: citizen creates new wallet → protocol verifies identity → transfers all funds → updates registry. No key backup needed, no ceremony, no waiting period. Ready for implementation.

**Decisions made:**
- Transfer-based recovery (not key recovery)
- L5 hash verification (same as protocol identity)
- Full balance, no partial transfers
- No waiting period
- Audit trail for every attempt (success or failure)

**Decisions resolved:**
- No rate limiting — wallet changes are rare operational events
- Trigger: citizen DMs @nlr_ai on Telegram. Nicolas verifies and executes. KISS.

---

## TODO

### Immediate

- [ ] Implement `l4/wallet/wallet_change_request_and_transfer.py`
- [ ] Write tests for 6 validation invariants

### Later

- [ ] Batch wallet migration for instance moves
- [ ] Health checkers (after code exists)

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Clear. The design is simple by intention — $MIND isn't for hoarding, so recovery can be fast and unceremonious. The tricky part will be atomicity across Solana and FalkorDB, but that's an implementation detail, not a design problem.

**Threads I was holding:**
- The `execute_protocol_transfer` function needs to exist in economy/token/ — might need to be created
- Rate limiting should probably be physics-based (trust-based cooldown?) rather than a hardcoded constant

---

## POINTERS

| What | Where |
|------|-------|
| Doc chain | `docs/citizen/wallet-recovery/` (8 files) |
| Implementation target | `l4/wallet/wallet_change_request_and_transfer.py` |
| Registry (identity) | `l4/registry/jwt_hash_verification_for_identity.py` |
| Registry (wallet) | `l4/registry/citizen_registration_crud_operations.py` |
| Token transfer | `economy/token/` |
| L5 Law (hash identity) | `docs/l4/laws/ALGORITHM_Laws.md` |
