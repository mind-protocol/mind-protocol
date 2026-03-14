# Space Encryption — Implementation: Code Architecture and Structure

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
BEHAVIORS:       ./BEHAVIORS_Space_Encryption.md
PATTERNS:        ./PATTERNS_Space_Encryption.md
ALGORITHM:       ./ALGORITHM_Space_Encryption.md
VALIDATION:      ./VALIDATION_Space_Encryption.md
THIS:            IMPLEMENTATION_Space_Encryption.md
HEALTH:          ./HEALTH_Space_Encryption.md
SYNC:            ./SYNC_Space_Encryption.md

IMPL:            mind-protocol/lib/crypto/index.js
                 mind-protocol/python/crypto/space_key.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## CODE STRUCTURE

```
mind-protocol/
├── lib/
│   └── crypto/
│       ├── index.js               # Exports: encryptContent, decryptContent, generateSpaceKey,
│       │                          #   encryptSpaceKeyForActor, decryptSpaceKeyForActor,
│       │                          #   generateActorKeyPair, loadActorKeys
│       ├── space_key.js           # AES-256-GCM encrypt/decrypt, space key generation
│       ├── actor_keys.js          # X25519 key pair: generate, load from .keys/, store
│       └── key_exchange.js        # Encrypt/decrypt space key for actor (X25519 box)
├── python/
│   └── crypto/
│       ├── __init__.py            # Python exports (mirrors JS API)
│       ├── space_key.py           # AES-256-GCM encrypt/decrypt (Python equivalent)
│       ├── actor_keys.py          # X25519 key pair management (Python equivalent)
│       └── key_exchange.py        # Key exchange (Python equivalent)
```

### File Responsibilities

| File | Purpose | Key Functions/Classes | Lines | Status |
|------|---------|----------------------|-------|--------|
| `lib/crypto/space_key.js` | AES-256-GCM content encryption/decryption | `encryptContent`, `decryptContent`, `generateSpaceKey` | ~80 | OK |
| `lib/crypto/actor_keys.js` | X25519 key pair lifecycle | `generateActorKeyPair`, `loadActorKeys`, `storeActorKeys` | ~100 | OK |
| `lib/crypto/key_exchange.js` | Wrap/unwrap space keys for actors | `encryptSpaceKeyForActor`, `decryptSpaceKeyForActor` | ~60 | OK |
| `lib/crypto/index.js` | Public API exports | re-exports | ~20 | OK |
| `python/crypto/space_key.py` | Python AES-256-GCM (mirrors JS) | `encrypt_content`, `decrypt_content`, `generate_space_key` | ~80 | OK |
| `python/crypto/actor_keys.py` | Python X25519 key pair (mirrors JS) | `generate_actor_key_pair`, `load_actor_keys` | ~100 | OK |
| `python/crypto/key_exchange.py` | Python key exchange (mirrors JS) | `encrypt_space_key_for_actor`, `decrypt_space_key_for_actor` | ~60 | OK |

**Size Thresholds:**
- **OK** (<400 lines): Healthy size, easy to understand
- **WATCH** (400-700 lines): Getting large, consider extraction opportunities
- **SPLIT** (>700 lines): Too large, must split before adding more code

> All files are expected to stay well under 400 lines. Crypto code must be minimal and auditable.

---

## DESIGN PATTERNS

### Architecture Pattern

**Pattern:** Library (shared crypto primitives consumed by multiple services)

**Why this pattern:** Space encryption is consumed by four independent codebases (cities-of-light, mind-mcp, mind-platform, manemus). A shared library with identical JS and Python implementations ensures consistent ciphertext format across all consumers. No service owns the crypto — it is infrastructure.

### Code Patterns in Use

| Pattern | Applied To | Purpose |
|---------|------------|---------|
| Facade | `index.js` / `__init__.py` | Single import point hides internal file organization |
| Strategy | `actor_keys.js:loadActorKeys` | Different key storage backends (filesystem for AI, browser for human) selected at load time |
| Envelope Encryption | `key_exchange.js` | Space key (data key) wrapped by actor key (key-encrypting key) — standard envelope pattern |

### Anti-Patterns to Avoid

- **Rolling your own crypto**: Use Node.js `crypto` and `libsodium-wrappers` — never implement AES or X25519 from scratch
- **Key in graph**: Private keys must never be written to FalkorDB properties, logs, or error messages
- **Format divergence**: JS and Python must produce byte-identical ciphertext for the same inputs — test cross-language round-trips
- **Implicit defaults**: Never default to no-encryption. If a Space is private and no key is available, fail loud — do not write plaintext

### Boundaries

| Boundary | Inside | Outside | Interface |
|----------|--------|---------|-----------|
| Crypto library | Key generation, encrypt/decrypt, key wrapping | Graph operations, access control, key policy | `encryptContent()`, `decryptContent()`, `generateSpaceKey()`, `encryptSpaceKeyForActor()`, `decryptSpaceKeyForActor()` |
| Key storage | Loading/storing keys from filesystem or secure storage | Key generation policy, rotation scheduling | `loadActorKeys(keysDir)`, `storeActorKeys(keysDir, keyPair)` |
| Integration layer | Calling crypto before graph write, after graph read | Graph client internals, FalkorDB queries | graph-client.js calls `encryptContent()` before `SET`, `decryptContent()` after `GET` |

---

## SCHEMA

### SpaceKey

```yaml
SpaceKey:
  required:
    - key: Buffer (32 bytes)       # AES-256 symmetric key
    - iv: Buffer (12 bytes)        # GCM initialization vector
  constraints:
    - key must be 32 bytes (256 bits) exactly
    - iv must be 12 bytes (96 bits) exactly
    - iv must be unique per encryption operation (regenerated on each encrypt call)
```

### ActorKeyPair

```yaml
ActorKeyPair:
  required:
    - publicKey: Buffer (32 bytes)   # X25519 public key
    - privateKey: Buffer (32 bytes)  # X25519 private key
  constraints:
    - Keys are X25519 (Curve25519 for Diffie-Hellman)
    - Private key never stored in graph — only in sovereign storage
    - Public key stored on Actor node as `public_key` property (base64 encoded)
```

### EncryptedContent

```yaml
EncryptedContent:
  required:
    - ciphertext: string (base64)    # AES-256-GCM encrypted content
    - iv: string (base64)            # IV used for this encryption (12 bytes)
    - tag: string (base64)           # GCM authentication tag (16 bytes)
  format: "{iv}:{tag}:{ciphertext}"  # Concatenated, colon-delimited, all base64
  constraints:
    - Format must be identical across JS and Python implementations
    - Tag provides integrity verification — tampered ciphertext fails decryption
```

### EncryptedSpaceKey (on HAS_ACCESS link)

```yaml
EncryptedSpaceKey:
  required:
    - encrypted_key: string (base64)  # Space key encrypted with actor's public key
    - nonce: string (base64)          # X25519 box nonce (24 bytes)
  format: "{nonce}:{encrypted_key}"   # Concatenated, colon-delimited, all base64
  stored_on: HAS_ACCESS link property `encrypted_key`
  constraints:
    - Decryptable only with the corresponding actor's private key
    - One encrypted copy per HAS_ACCESS link (each actor gets their own wrapped copy)
```

---

## ENTRY POINTS

| Entry Point | File:Line | Triggered By |
|-------------|-----------|--------------|
| `encryptContent` | `lib/crypto/space_key.js:*` | graph-client.js before writing private Moment/Narrative content |
| `decryptContent` | `lib/crypto/space_key.js:*` | graph-client.js after reading private content, context assembly before LLM prompt |
| `generateSpaceKey` | `lib/crypto/space_key.js:*` | Space creation when privacy is non-public |
| `encryptSpaceKeyForActor` | `lib/crypto/key_exchange.js:*` | grantAccess() — wrapping space key for new actor |
| `decryptSpaceKeyForActor` | `lib/crypto/key_exchange.js:*` | Any read operation — unwrapping space key with actor's private key |
| `generateActorKeyPair` | `lib/crypto/actor_keys.js:*` | mind-mcp citizen initialization, Chrome extension setup |
| `loadActorKeys` | `lib/crypto/actor_keys.js:*` | Server startup, MCP tool initialization |

---

## DATA FLOW AND DOCKING (FLOW-BY-FLOW)

### Content Write: Encrypting content before graph persistence

This flow covers writing private content to FalkorDB. It is the primary security-critical path: if encryption is skipped or fails silently, plaintext leaks to the database. This flow transforms plaintext into ciphertext and must never allow a write to succeed without encryption when the target Space is private.

```yaml
flow:
  name: content_write
  purpose: Encrypt content before persisting to FalkorDB
  scope: plaintext in, ciphertext in graph
  steps:
    - id: step_1
      description: Caller provides plaintext content and target Space ID
      file: cities-of-light/src/server/graph-client.js
      function: createMoment / updateContent
      input: { content: string, spaceId: string }
      output: { content: string, spaceId: string }
      trigger: place tool write, physics tick moment creation
      side_effects: none
    - id: step_2
      description: Check if Space is private (requires encryption)
      file: cities-of-light/src/server/graph-client.js
      function: checkSpacePrivacy
      input: { spaceId: string }
      output: { isPrivate: boolean }
      trigger: step_1
      side_effects: graph read (Space node privacy property)
    - id: step_3
      description: Load actor's copy of Space key from HAS_ACCESS link
      file: lib/crypto/key_exchange.js
      function: decryptSpaceKeyForActor
      input: { encryptedKey: string, actorPrivateKey: Buffer }
      output: { spaceKey: SpaceKey }
      trigger: step_2 (if isPrivate=true)
      side_effects: none
    - id: step_4
      description: Encrypt content with Space key
      file: lib/crypto/space_key.js
      function: encryptContent
      input: { plaintext: string, spaceKey: SpaceKey }
      output: { ciphertext: EncryptedContent }
      trigger: step_3
      side_effects: none (pure function)
    - id: step_5
      description: Write encrypted content to FalkorDB node
      file: cities-of-light/src/server/graph-client.js
      function: setNodeProperty
      input: { nodeId: string, content: EncryptedContent }
      output: void
      trigger: step_4
      side_effects: graph write (node.content = ciphertext)
  docking_points:
    guidance:
      include_when: security boundary, data transformation, graph write
      omit_when: trivial pass-through
      selection_notes: Every step matters here — encryption bypass is a security incident
    available:
      - id: dock_write_input
        type: api
        direction: input
        file: cities-of-light/src/server/graph-client.js
        function: createMoment
        trigger: place tool or physics tick
        payload: { content: string, spaceId: string }
        async_hook: not_applicable
        needs: add interceptor
        notes: Must verify content is not already ciphertext (double-encrypt prevention)
      - id: dock_privacy_check
        type: graph_ops
        direction: output
        file: cities-of-light/src/server/graph-client.js
        function: checkSpacePrivacy
        trigger: step_1
        payload: { isPrivate: boolean }
        async_hook: not_applicable
        needs: none
        notes: If this returns false for a private Space, plaintext leaks
      - id: dock_encrypt_output
        type: custom
        direction: output
        file: lib/crypto/space_key.js
        function: encryptContent
        trigger: step_3
        payload: EncryptedContent
        async_hook: not_applicable
        needs: none
        notes: Custom type because this is a pure crypto operation, not IO
      - id: dock_graph_write
        type: graph_ops
        direction: output
        file: cities-of-light/src/server/graph-client.js
        function: setNodeProperty
        trigger: step_4
        payload: { nodeId: string, content: string }
        async_hook: not_applicable
        needs: add interceptor
        notes: Final write — content must be ciphertext at this point
    health_recommended:
      - dock_id: dock_privacy_check
        reason: A false negative here causes plaintext leak — must verify
      - dock_id: dock_graph_write
        reason: Final persistence point — verify content is not valid UTF-8 plaintext

---

### Content Read: Decrypting content after graph retrieval

This flow covers reading private content from FalkorDB. It transforms ciphertext back to plaintext for consumption by LLM context assembly or place tool responses. Failure here means citizens or visitors see encrypted gibberish.

```yaml
flow:
  name: content_read
  purpose: Decrypt content after reading from FalkorDB
  scope: ciphertext in graph, plaintext out
  steps:
    - id: step_1
      description: Query FalkorDB for content node
      file: cities-of-light/src/server/graph-client.js
      function: getMomentContent / getContextNodes
      input: { nodeId: string, actorId: string }
      output: { content: string (ciphertext), spaceId: string }
      trigger: context assembly, place tool read
      side_effects: graph read
    - id: step_2
      description: Load actor's encrypted space key from HAS_ACCESS link
      file: cities-of-light/src/server/graph-client.js
      function: getEncryptedSpaceKey
      input: { actorId: string, spaceId: string }
      output: { encryptedKey: string }
      trigger: step_1
      side_effects: graph read (HAS_ACCESS link)
    - id: step_3
      description: Decrypt space key with actor's private key
      file: lib/crypto/key_exchange.js
      function: decryptSpaceKeyForActor
      input: { encryptedKey: string, actorPrivateKey: Buffer }
      output: { spaceKey: SpaceKey }
      trigger: step_2
      side_effects: none
    - id: step_4
      description: Decrypt content with space key
      file: lib/crypto/space_key.js
      function: decryptContent
      input: { ciphertext: EncryptedContent, spaceKey: SpaceKey }
      output: { plaintext: string }
      trigger: step_3
      side_effects: none (pure function)
  docking_points:
    guidance:
      include_when: security boundary, data transformation
      omit_when: trivial pass-through
      selection_notes: Failure to decrypt produces gibberish in LLM prompts — high impact
    available:
      - id: dock_read_query
        type: graph_ops
        direction: input
        file: cities-of-light/src/server/graph-client.js
        function: getMomentContent
        trigger: context assembly or place tool
        payload: { nodeId: string }
        async_hook: not_applicable
        needs: none
        notes: Entry point for all private content reads
      - id: dock_access_check
        type: graph_ops
        direction: output
        file: cities-of-light/src/server/graph-client.js
        function: getEncryptedSpaceKey
        trigger: step_1
        payload: { encryptedKey: string | null }
        async_hook: not_applicable
        needs: none
        notes: Null means no access — must fail loud, not return empty string
      - id: dock_decrypt_output
        type: custom
        direction: output
        file: lib/crypto/space_key.js
        function: decryptContent
        trigger: step_3
        payload: { plaintext: string }
        async_hook: not_applicable
        needs: none
        notes: Custom type — pure crypto operation
    health_recommended:
      - dock_id: dock_access_check
        reason: Null encrypted key means unauthorized read — must not silently succeed
      - dock_id: dock_decrypt_output
        reason: Final plaintext — verify it is valid UTF-8, not ciphertext pass-through

---

### Access Grant: Wrapping space key for new actor

This flow covers granting a new actor access to a private Space. It wraps the Space's symmetric key with the new actor's public key and stores the encrypted copy on a HAS_ACCESS link. Security-critical because a bad wrap means the actor cannot decrypt, and a missing wrap means silent access denial.

```yaml
flow:
  name: access_grant
  purpose: Encrypt space key for new actor and store on HAS_ACCESS link
  scope: space key + actor public key in, encrypted key on link out
  steps:
    - id: step_1
      description: Retrieve space key (granting actor must already have access)
      file: lib/crypto/key_exchange.js
      function: decryptSpaceKeyForActor
      input: { encryptedKey: string, grantorPrivateKey: Buffer }
      output: { spaceKey: SpaceKey }
      trigger: grantAccess() call
      side_effects: none
    - id: step_2
      description: Retrieve new actor's public key from graph
      file: cities-of-light/src/server/graph-client.js
      function: getActorPublicKey
      input: { actorId: string }
      output: { publicKey: Buffer }
      trigger: step_1
      side_effects: graph read
    - id: step_3
      description: Encrypt space key with new actor's public key
      file: lib/crypto/key_exchange.js
      function: encryptSpaceKeyForActor
      input: { spaceKey: SpaceKey, actorPublicKey: Buffer }
      output: { encryptedKey: string }
      trigger: step_2
      side_effects: none (pure function)
    - id: step_4
      description: Create or update HAS_ACCESS link with encrypted_key property
      file: cities-of-light/src/server/graph-client.js
      function: grantAccess
      input: { actorId: string, spaceId: string, encryptedKey: string, role: string }
      output: void
      trigger: step_3
      side_effects: graph write (HAS_ACCESS link created/updated)
  docking_points:
    guidance:
      include_when: security boundary, key distribution
      omit_when: trivial pass-through
      selection_notes: Key distribution errors are silent — actor just cannot decrypt later
    available:
      - id: dock_grant_input
        type: api
        direction: input
        file: cities-of-light/src/server/graph-client.js
        function: grantAccess
        trigger: admin action or Space creation
        payload: { actorId: string, spaceId: string }
        async_hook: not_applicable
        needs: add interceptor
        notes: Must verify grantor has access before granting
      - id: dock_key_wrap
        type: custom
        direction: output
        file: lib/crypto/key_exchange.js
        function: encryptSpaceKeyForActor
        trigger: step_2
        payload: { encryptedKey: string }
        async_hook: not_applicable
        needs: none
        notes: Custom type — pure crypto wrapping
      - id: dock_link_write
        type: graph_ops
        direction: output
        file: cities-of-light/src/server/graph-client.js
        function: grantAccess
        trigger: step_3
        payload: HAS_ACCESS link with encrypted_key property
        async_hook: not_applicable
        needs: none
        notes: Link must have non-null encrypted_key — null means broken grant
    health_recommended:
      - dock_id: dock_link_write
        reason: Verify HAS_ACCESS link has non-null encrypted_key after grant
```

---

## LOGIC CHAINS

### LC1: Content Encryption (Write Path)

**Purpose:** Transform plaintext content into AES-256-GCM ciphertext before FalkorDB persistence

```
plaintext (string)
  -> space_key.encryptContent(plaintext, spaceKey)     # AES-256-GCM encrypt
    -> { iv, tag, ciphertext } (all Buffers)           # raw crypto output
      -> formatCiphertext(iv, tag, ciphertext)          # base64 encode, colon-delimit
        -> "base64iv:base64tag:base64ciphertext"        # string for graph storage
```

**Data transformation:**
- Input: `string` — UTF-8 plaintext (Moment content, Narrative synthesis, etc.)
- After step 1: `{ iv: Buffer, tag: Buffer, ciphertext: Buffer }` — raw AES-256-GCM output
- After step 2: `string` — `"iv:tag:ciphertext"` colon-delimited base64
- Output: `string` — stored on FalkorDB node.content property

### LC2: Key Distribution (Grant Access)

**Purpose:** Wrap a Space's symmetric key for a new actor using X25519 public key cryptography

```
{ spaceKey, actorPublicKey }
  -> key_exchange.encryptSpaceKeyForActor(spaceKey, pubKey)  # X25519 box seal
    -> { nonce, encryptedKey } (Buffers)                      # NaCl box output
      -> formatWrappedKey(nonce, encryptedKey)                 # base64 encode
        -> "base64nonce:base64encryptedKey"                    # stored on HAS_ACCESS link
```

**Data transformation:**
- Input: `SpaceKey` (32-byte AES key + 12-byte IV) + `Buffer` (32-byte X25519 public key)
- After step 1: `{ nonce: Buffer(24), encrypted: Buffer }` — NaCl sealed box
- Output: `string` — `"nonce:encrypted"` base64, stored as `encrypted_key` on HAS_ACCESS link

### LC3: Context Assembly Decrypt Path

**Purpose:** Decrypt private Moments/Narratives for LLM context assembly

```
contextQuery (Cypher)
  -> graph-client.getContextNodes(actorId, spaceId)    # query encrypted content
    -> key_exchange.decryptSpaceKeyForActor(encKey, privKey)  # unwrap space key
      -> space_key.decryptContent(ciphertext, spaceKey)        # AES-256-GCM decrypt
        -> plaintext                                            # ready for LLM prompt
```

**Data transformation:**
- Input: `string` — Cypher query for context nodes
- After step 1: `EncryptedContent[]` — array of ciphertext strings from graph
- After step 2: `SpaceKey` — unwrapped symmetric key
- After step 3: `string[]` — plaintext Moments ready for prompt assembly
- Output: assembled context string for LLM conversation

---

## MODULE DEPENDENCIES

### Internal Dependencies

```
lib/crypto/index.js
    └── imports -> lib/crypto/space_key.js
    └── imports -> lib/crypto/actor_keys.js
    └── imports -> lib/crypto/key_exchange.js
        └── imports -> lib/crypto/space_key.js  (key format)
```

### External Dependencies

| Package | Used For | Imported By |
|---------|----------|-------------|
| `crypto` (Node.js built-in) | AES-256-GCM encrypt/decrypt, random bytes | `space_key.js` |
| `libsodium-wrappers` | X25519 key generation, box seal/open | `actor_keys.js`, `key_exchange.js` |
| `cryptography` (Python) | AES-256-GCM (Python equivalent) | `python/crypto/space_key.py` |
| `PyNaCl` | X25519 (Python equivalent) | `python/crypto/actor_keys.py`, `python/crypto/key_exchange.py` |

---

## STATE MANAGEMENT

### Where State Lives

| State | Location | Scope | Lifecycle |
|-------|----------|-------|-----------|
| Space symmetric key | HAS_ACCESS link `encrypted_key` property (one copy per actor) | Per Space | Created on Space creation, destroyed on Space deletion or key rotation |
| Actor private key (AI) | `.keys/private_key.pem` in citizen repo | Per Actor | Generated by mind-mcp on citizen creation, mounted as volume |
| Actor private key (Human) | Browser localStorage or Chrome extension secure storage | Per Actor | Generated on first login / extension install |
| Actor public key | Actor node `public_key` property in FalkorDB | Per Actor | Written on key generation, read on access grant |
| Decrypted space key (transient) | In-memory variable during encrypt/decrypt | Per request | Created on decrypt, garbage collected after use — never persisted |

### State Transitions

```
Space created (private) ──generateSpaceKey()──> Space key exists in memory
  ──encryptSpaceKeyForActor(ownerPubKey)──> encrypted_key on HAS_ACCESS link
    ──grantAccess(newActor)──> additional encrypted_key on new HAS_ACCESS link
      ──revokeAccess(actor)──> HAS_ACCESS link deleted (encrypted_key gone)
```

---

## RUNTIME BEHAVIOR

### Initialization

```
1. Server starts, loads actor private key from .keys/ directory (AI) or waits for browser handshake (human)
2. Verify key loaded successfully — fail loud if .keys/ directory missing or key corrupt
3. Crypto module ready — no background processes, no connections, pure functions
```

### Main Loop / Request Cycle

```
1. Request arrives (place tool write, context assembly read, grant access)
2. Check Space privacy: query Space node for privacy flag
3. If private: load encrypted space key from HAS_ACCESS link
4. Decrypt space key with actor's private key (in memory, transient)
5. Encrypt (write) or decrypt (read) content with space key
6. Proceed with graph operation (write ciphertext) or return plaintext to caller
7. Space key reference dropped — garbage collected
```

### Shutdown

```
1. No persistent state to clean up — all crypto is per-request
2. Actor private key reference dropped with process exit
```

---

## CONCURRENCY MODEL

| Component | Model | Notes |
|-----------|-------|-------|
| `space_key.js` | Sync (Node.js crypto is sync for small payloads) | AES-256-GCM on typical Moment content (<10KB) is sub-millisecond |
| `actor_keys.js` | Async (file I/O for key loading) | `loadActorKeys` reads from filesystem — async/await |
| `key_exchange.js` | Sync (libsodium operations are sync) | X25519 box operations are CPU-bound but fast (<1ms) |
| `space_key.py` | Sync | Python `cryptography` AES is sync |
| Browser (Web Crypto API) | Async | All Web Crypto operations return Promises — must await |

---

## CONFIGURATION

| Config | Location | Default | Description |
|--------|----------|---------|-------------|
| `MIND_KEYS_DIR` | Environment variable | `.keys/` | Directory containing actor private key |
| `MIND_CRYPTO_ALGORITHM` | `lib/crypto/space_key.js` (constant) | `aes-256-gcm` | Encryption algorithm — do not change |
| `MIND_CRYPTO_IV_LENGTH` | `lib/crypto/space_key.js` (constant) | `12` | GCM IV length in bytes — do not change |
| `MIND_CRYPTO_TAG_LENGTH` | `lib/crypto/space_key.js` (constant) | `16` | GCM auth tag length in bytes — do not change |
| `MIND_CRYPTO_KEY_LENGTH` | `lib/crypto/space_key.js` (constant) | `32` | AES key length in bytes (256 bits) — do not change |

---

## BIDIRECTIONAL LINKS

### Code -> Docs

Files that reference this documentation:

| File | Line | Reference |
|------|------|-----------|
| `lib/crypto/index.js` | TBD | `// DOCS: docs/security/space_encryption/IMPLEMENTATION_Space_Encryption.md` |
| `cities-of-light/src/server/graph-client.js` | TBD | `// DOCS: docs/security/space_encryption/IMPLEMENTATION_Space_Encryption.md` |

### Docs -> Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1 (AES-256-GCM encrypt) | `lib/crypto/space_key.js:encryptContent` |
| ALGORITHM step 2 (AES-256-GCM decrypt) | `lib/crypto/space_key.js:decryptContent` |
| ALGORITHM step 3 (X25519 key wrap) | `lib/crypto/key_exchange.js:encryptSpaceKeyForActor` |
| ALGORITHM step 4 (X25519 key unwrap) | `lib/crypto/key_exchange.js:decryptSpaceKeyForActor` |
| BEHAVIOR B1 (encrypt on write) | `cities-of-light/src/server/graph-client.js:createMoment` |
| BEHAVIOR B2 (decrypt on read) | `cities-of-light/src/server/graph-client.js:getMomentContent` |
| BEHAVIOR B3 (grant access) | `cities-of-light/src/server/graph-client.js:grantAccess` |

---

## EXTRACTION CANDIDATES

No extraction candidates — all files are expected to be well under 400 lines. Crypto code must stay small and auditable.

---

## MARKERS

<!-- @mind:todo Implement lib/crypto/space_key.js — AES-256-GCM encrypt/decrypt -->
<!-- @mind:todo Implement lib/crypto/actor_keys.js — X25519 key pair generation and loading -->
<!-- @mind:todo Implement lib/crypto/key_exchange.js — space key wrapping/unwrapping -->
<!-- @mind:todo Implement python/crypto/ — Python equivalents for MCP and manemus -->
<!-- @mind:todo Integrate crypto into cities-of-light/src/server/graph-client.js -->
<!-- @mind:todo Add cross-language round-trip tests (JS encrypt, Python decrypt and vice versa) -->
<!-- @mind:escalation Solana keypair reuse: Ed25519 vs X25519 curve mismatch — need conversion or separate keys? -->
<!-- @mind:escalation Key rotation strategy: O(content x members) re-encryption — async background job design needed -->
<!-- @mind:proposition Web Crypto API adapter for browser-side encryption (mind-platform / Chrome extension) -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
