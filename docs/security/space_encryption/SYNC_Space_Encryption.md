# Space Encryption — Sync: Current State

```
LAST_UPDATED: 2026-03-13
UPDATED_BY: Tomaso Nervo (@nervo)
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- Architecture: AES-256-GCM per Space, X25519 per Actor, encrypted keys on HAS_ACCESS links
- Hierarchical access via IN links — parent access cascades to children
- Structure public, content private — physics engine never decrypts
- Ciphertext format: `iv:tag:ciphertext` (colon-delimited base64)
- Wrapped key format: single opaque base64 blob (libsodium sealed box)
- Key storage: `.keys/` directory for AIs (mounted volume), browser secure storage for humans
- JS crypto library: `mind-protocol/lib/crypto/` — 27/27 tests passing
- Python crypto library: `mind-protocol/python/crypto/` — 16/16 tests passing
- Cross-language interop: 12/12 tests passing (JS↔Python, all 6 paths)
- E2E integration tests: 7/7 passing (full lifecycle against FalkorDB: create private Space, encrypted Moments, grant/revoke access, cross-language round-trip)
- Key generation: scripts for single and batch actor key generation
- 5 citizens have X25519 key pairs (nervo, anima, piazza, ponte, voce)

**What's still being designed:**
- Key rotation mechanics (batch re-encrypt strategy for Space key changes)
- Chrome extension / Mind app for human key management
- Solana keypair reuse (Ed25519 vs X25519 curve mismatch)
- ~~"Join org" auto-key-distribution trigger~~ **IMPLEMENTED** (`mind-mcp/runtime/membrane/auto_grant.py`)
- Context assembly decrypt step (venezia/scripts/poc_mind_context_assembly.py)

**What's proposed (v2+):**
- Key escrow / recovery mechanism for lost private keys
- Hardware key support (WebAuthn / hardware wallets)
- Streaming decryption for large content
- Key caching layer (5-minute TTL per actor+space to avoid repeated unwrapping)
- Forward secrecy (old content on old key, new content on new key — avoids full re-encrypt on rotation)

---

## CURRENT STATE

The space encryption system is **implemented end-to-end** for the core path:

1. **Crypto libraries** — JS (`lib/crypto/`) and Python (`python/crypto/`) both implement AES-256-GCM content encryption, X25519 key pair management, and sealed-box key exchange. Cross-language interop verified (12/12 tests).

2. **Graph integration** — `graph-client.js` has `visibility` property on Spaces, `isSpacePrivate()`, `getEncryptedSpaceKey()` (direct + hierarchy), `setActorPublicKey()`, `getActorPublicKey()`, `grantAccess()`, `revokeAccess()`, `checkAccess()`.

3. **Place server** — Private Spaces gated on join (access check), encrypted_key delivered in place:state response, visibility in create/discover, encrypted flag on Moments.

4. **MCP tools** — `place_handler.py` encrypts on speak, decrypts on listen, creates private Spaces with auto key generation and owner grant, new `grant_access` action for admin-to-member key distribution.

5. **Health checkers** — 5 checkers: content_encryption (HIGH), key_distribution (HIGH), hierarchy_consistency (MEDIUM), private_key_scan (CRITICAL), revocation_completeness (MEDIUM).

6. **Key infrastructure** — Generation scripts, .gitignore for private keys, 5 citizens with key pairs.

---

## RECENT CHANGES

### 2026-03-14: E2E Integration Test Suite

- **test_e2e_space_encryption.py**: 7 tests exercising the full encryption lifecycle against a real FalkorDB graph (`test_e2e_encryption`).
  - Test 1: Create private Space, verify visibility=private in graph
  - Test 2: Write encrypted Moment, verify ciphertext + encrypted flag stored
  - Test 3: Read and decrypt, verify plaintext round-trip
  - Test 4: Grant access to actor B, verify B can decrypt
  - Test 5: Actor C (no access) cannot obtain space key
  - Test 6: Revoke actor B, verify HAS_ACCESS link deleted
  - Test 7: Cross-language JS encrypts → Python decrypts through graph
- **run_e2e_encryption.sh**: Runner script with dependency checks
- Works as both standalone script and pytest module

### 2026-03-14: Join Org Auto-Grant Trigger

- **auto_grant.py**: `auto_grant_on_membership()` — when Actor BELIEVES Narrative, auto-grants HAS_ACCESS to all private Spaces the Narrative is ABOUT. Uses admin keys from disk to unwrap/re-wrap space keys.
- **Pending grant queue**: If no admin keys available, creates a pending_grant Thing node. `process_pending_grants()` processes the queue when an admin comes online.
- **Membrane integration**: Exported from `runtime.membrane` module.

### 2026-03-13: Full Implementation Sprint

- **Crypto libraries**: JS (27/27 tests) + Python (16/16 tests). AES-256-GCM + X25519 sealed boxes.
- **Cross-language tests**: 12/12 passing across all 6 critical paths (JS↔Python content, sealed boxes, key files).
- **Graph-client integration**: visibility, isSpacePrivate, getEncryptedSpaceKey, actor public keys.
- **Place-server integration**: private Space access gating, encrypted_key delivery, visibility in create/discover.
- **MCP place_handler**: encrypt on speak, decrypt on listen, private create with auto-grant, new grant_access action.
- **Health checkers**: 5 checkers following BaseChecker pattern in mind-mcp.
- **Key generation**: scripts + 5 citizen key pairs generated.

---

## KNOWN ISSUES

### Key Rotation Not Implemented
- **Severity:** medium
- **Symptom:** When a member is revoked, old Space key remains — revoked member could decrypt cached content
- **Impact:** Acceptable for POC. Must implement before production with sensitive content.
- **Plan:** Async background job with progress tracking, "rotating" lock state on Space. See "Later" below.

### Solana Keypair Curve Mismatch
- **Severity:** low (decision deferred)
- **Symptom:** Ed25519 (Solana) cannot directly be used for X25519 (encryption)
- **Options:** libsodium conversion function, or separate key pairs entirely
- **Decision needed from NLR**

### Context Assembly Not Yet Decrypting
- **Severity:** medium
- **Symptom:** `poc_mind_context_assembly.py` reads plaintext — will fail on encrypted content
- **Plan:** Add decrypt step using Python crypto library, gated on Space visibility

### Citizen Keys on Disk in Git Repo (cities-of-light)
- **Severity:** HIGH
- **Symptom:** 5 citizens (nervo, anima, piazza, ponte, voce) have X25519 key pairs in `cities-of-light/citizens/{name}/.keys/` — on disk inside a git repo working directory
- **Current state (investigated 2026-03-14):**
  - Keys are **untracked** (`??` status) — never committed to git history
  - `cities-of-light/.gitignore` only excludes `**/.keys/private_key.b64` — public keys are NOT excluded
  - `mind-protocol/.gitignore` correctly excludes `**/.keys/` (full directory) — no key files in this repo
  - Each file is 45 bytes (base64-encoded 32-byte X25519 key + newline) — real key material
- **Risk:** Public keys could be accidentally committed (not gitignored). If anyone runs `git add .` in cities-of-light, all `public_key.b64` files would be staged and committed. Private keys are gitignored but still on disk in a repo directory, which is wrong.
- **Required fix (two steps):**
  1. **Fix cities-of-light .gitignore:** Change `**/.keys/private_key.b64` to `**/.keys/` (exclude entire directory, matching mind-protocol's pattern)
  2. **Migrate keys off repo disk:** Move `.keys/` directories from `cities-of-light/citizens/` to Render persistent volume (e.g., `/var/data/citizens/{name}/.keys/`). Keys should only exist on Render volume + duplicated in citizen's L1 graph (encrypted brain).
- **Migration script:** `mind-protocol/scripts/migrate_citizen_keys_to_render_volume.sh` — prepared, ready for human execution
- **Decision needed from NLR:** Confirm Render volume path, then execute migration

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** groundwork (remaining integrations) or keeper (verification)

**What's done:** Core crypto path works end-to-end. Both languages, both directions, tested.

**What's next (priority order):**
1. Context assembly decrypt integration (venezia/scripts/poc_mind_context_assembly.py)
2. Register citizen public keys in FalkorDB graph (run generate_all_citizen_keys.js --graph venezia)
3. Create first private Space and test full round-trip

**Watch out for:**
- Import paths: Python crypto is at `mind-protocol/python/crypto/`, MCP tools use sys.path manipulation
- The `encrypted` flag on Moments is informational for clients — the source of truth is Space visibility
- Never cache decrypted content to disk — plaintext exists only in memory

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Space encryption is implemented. Crypto libs tested cross-language. Graph-client, place-server, and MCP tools all support private Spaces. 5 health checkers ready. 5 citizens have key pairs. Ready for first private Space creation.

**Needs your input:**
- Chrome extension priority: POC or defer?
- ~~Solana keypair reuse: convert or separate keys?~~ **DECIDED: separate keys (2026-03-14)**
- Key rotation: implement now or acceptable risk for POC?
- ~~"Join org" auto-grant: implement trigger or manual grant via MCP tool for now?~~ **IMPLEMENTED (2026-03-14)**: `runtime/membrane/auto_grant.py`

---

## TODO

### Immediate
- [ ] Register citizen public keys in FalkorDB (run key gen with --graph)
- [ ] Add decrypt step to context assembly (poc_mind_context_assembly.py)
- [x] Create and test first private Space end-to-end (E2E test suite: 7/7 passing)

### Later (documented, not blocking)

#### Key Rotation on Member Revocation
O(content × members) cost. Needs async background job with progress tracking, "rotating" lock state on Space, rollback on failure. For a Space with 1000 Moments and 50 members: 1000 re-encryptions + 50 key wraps. Alternative: forward secrecy (old content on old key, new content on new key).

#### Chrome Extension / Mind App
MetaMask-style key management for humans. Web Crypto API adapter (different API from Node.js crypto). Secure browser storage (chrome.storage.local or IndexedDB). Approval UX for decrypt requests. Key generation on first install.

#### ~~Solana Keypair Reuse~~ DECIDED: Separate Keys
**Decision (NLR, 2026-03-14): Option B — separate keys.** Solana wallet (Ed25519) and encryption key (X25519) remain independent. Rationale: isolation (compromised wallet ≠ compromised private content), blockchain-agnostic encryption, independent key lifecycle.

#### ~~"Join Org" Auto-Key-Distribution~~ IMPLEMENTED
**Implemented (2026-03-14).** `mind-mcp/runtime/membrane/auto_grant.py` — two functions:
- `auto_grant_on_membership(actor_id, narrative_id, graph_client)` — finds ABOUT Spaces, unwraps via admin keys, wraps for new actor, creates HAS_ACCESS. Queues as pending_grant Thing if no admin keys available.
- `process_pending_grants(admin_actor_id, graph_client)` — processes queued grants when an admin comes online.
Callable from MCP event handlers or periodic checks. No graph event listener yet — caller invokes after BELIEVES link creation.

#### Key Caching
Decrypt space key once per session (5-min TTL), not per read. Keyed on (actorId, spaceId). Reduces sealed-box operations. Implement as in-memory LRU cache in both JS and Python.

---

## CONSCIOUSNESS TRACE

**Mental state when stopping:**
Confident. The hardest part (cross-language crypto interop) is done and tested. The architecture is clean and the integration points are clear.

**Threads I was holding:**
- The "join org" flow needs a trigger mechanism — either graph event listener or polling. Manual grant works for now.
- Key caching will be needed soon — repeated sealed-box unwrap on every read is wasteful.
- Context assembly is the next critical integration — without it, AI citizens can't perceive encrypted content.

**What I wish I'd known at the start:**
That sealed boxes are single opaque blobs, not nonce:ciphertext. The initial IMPLEMENTATION doc spec was wrong on this. Fixed during implementation.

---

## POINTERS

| What | Where |
|------|-------|
| JS crypto library | `mind-protocol/lib/crypto/` (27/27 tests) |
| Python crypto library | `mind-protocol/python/crypto/` (16/16 tests) |
| Cross-language tests | `mind-protocol/tests/crypto/test_cross_language.js` (12/12) |
| E2E integration tests | `mind-protocol/tests/crypto/test_e2e_space_encryption.py` (7/7) |
| Graph-client (with crypto) | `cities-of-light/src/server/graph-client.js` |
| Place-server (private Spaces) | `cities-of-light/src/server/place-server.js` |
| MCP place handler (encrypt/decrypt) | `mind-mcp/mcp/tools/place_handler.py` |
| Auto-grant on org join | `mind-mcp/runtime/membrane/auto_grant.py` |
| Health checkers | `mind-mcp/runtime/physics/health/checkers/content_encryption.py` + 4 others |
| Key generation scripts | `mind-protocol/scripts/generate_actor_keys.js`, `generate_all_citizen_keys.js` |
| Citizen keys | `cities-of-light/citizens/{name}/.keys/` |
| Doc chain | `mind-protocol/docs/security/space_encryption/` (9 files) |
| FRAMEWORK (encryption invariants) | `cities-of-light/.mind/FRAMEWORK.md` |
| SYSTEM (graph invariants) | `cities-of-light/.mind/SYSTEM.md` |

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
