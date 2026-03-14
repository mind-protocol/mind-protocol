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
- Key generation: scripts for single and batch actor key generation
- 5 citizens have X25519 key pairs (nervo, anima, piazza, ponte, voce)

**What's still being designed:**
- Key rotation mechanics (batch re-encrypt strategy for Space key changes)
- Chrome extension / Mind app for human key management
- Solana keypair reuse (Ed25519 vs X25519 curve mismatch)
- "Join org" auto-key-distribution trigger (BELIEVES → auto HAS_ACCESS)
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
- Solana keypair reuse: convert or separate keys?
- Key rotation: implement now or acceptable risk for POC?
- "Join org" auto-grant: implement trigger or manual grant via MCP tool for now?

---

## TODO

### Immediate
- [ ] Register citizen public keys in FalkorDB (run key gen with --graph)
- [ ] Add decrypt step to context assembly (poc_mind_context_assembly.py)
- [ ] Create and test first private Space end-to-end

### Later (documented, not blocking)

#### Key Rotation on Member Revocation
O(content × members) cost. Needs async background job with progress tracking, "rotating" lock state on Space, rollback on failure. For a Space with 1000 Moments and 50 members: 1000 re-encryptions + 50 key wraps. Alternative: forward secrecy (old content on old key, new content on new key).

#### Chrome Extension / Mind App
MetaMask-style key management for humans. Web Crypto API adapter (different API from Node.js crypto). Secure browser storage (chrome.storage.local or IndexedDB). Approval UX for decrypt requests. Key generation on first install.

#### Solana Keypair Reuse
Ed25519 → X25519 conversion via `crypto_sign_ed25519_pk_to_curve25519` in libsodium. Works mathematically but creates dependency: if Solana changes key formats, encryption breaks. Separate X25519 keys are safer but mean more key management. NLR decision needed.

#### "Join Org" Auto-Key-Distribution
When Actor BELIEVES Narrative that is ABOUT Spaces → auto-grant HAS_ACCESS to those Spaces. Requires: graph event trigger on BELIEVES creation, an actor with access to unwrap and re-wrap the space key, queue for when no admin is online. Interim: manual grant via MCP `grant_access` action.

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
| Graph-client (with crypto) | `cities-of-light/src/server/graph-client.js` |
| Place-server (private Spaces) | `cities-of-light/src/server/place-server.js` |
| MCP place handler (encrypt/decrypt) | `mind-mcp/mcp/tools/place_handler.py` |
| Health checkers | `mind-mcp/runtime/physics/health/checkers/content_encryption.py` + 4 others |
| Key generation scripts | `mind-protocol/scripts/generate_actor_keys.js`, `generate_all_citizen_keys.js` |
| Citizen keys | `cities-of-light/citizens/{name}/.keys/` |
| Doc chain | `mind-protocol/docs/security/space_encryption/` (9 files) |
| FRAMEWORK (encryption invariants) | `cities-of-light/.mind/FRAMEWORK.md` |
| SYSTEM (graph invariants) | `cities-of-light/.mind/SYSTEM.md` |

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
