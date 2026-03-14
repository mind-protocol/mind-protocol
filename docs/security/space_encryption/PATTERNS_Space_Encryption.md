# Space Encryption — Patterns: Separating Structure from Substance

```
STATUS: DESIGNING
CREATED: 2026-03-13
CHAIN: OBJECTIVES → PATTERNS → BEHAVIORS → ALGORITHM → VALIDATION → IMPLEMENTATION → SYNC
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
THIS:            PATTERNS_Space_Encryption.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Space_Encryption.md (to be created)
ALGORITHM:       ./ALGORITHM_Space_Encryption.md (to be created)
VALIDATION:      ./VALIDATION_Space_Encryption.md (to be created)
HEALTH:          ./HEALTH_Space_Encryption.md (to be created)
IMPLEMENTATION:  ./IMPLEMENTATION_Space_Encryption.md (to be created)
SYNC:            ./SYNC_Space_Encryption.md (to be created)

IMPL:            src/server/encryption/ (to be created)
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

**After modifying this doc:**
1. Update the IMPL source files to match, OR
2. Add a TODO in SYNC_Space_Encryption.md: "Docs updated, implementation needs: {what}"
3. Run tests: `npm test -- --grep encryption`

**After modifying the code:**
1. Update this doc chain to match, OR
2. Add a TODO in SYNC_Space_Encryption.md: "Implementation changed, docs need: {what}"
3. Run tests: `npm test -- --grep encryption`

---

## THE PROBLEM

One graph per universe means a single FalkorDB instance holds everything: public piazzas and private minds, guild announcements and secret conversations, published Narratives and personal Moments. Every citizen, every memory, every relationship — one database.

This is architecturally correct. The physics engine needs a unified graph to propagate energy, apply decay, accumulate tension, and detect moment flips across all Spaces. Splitting the graph would fragment physics and create cross-database complexity that scales badly.

But it creates a catastrophic failure mode: **compromise the database, read everything.** Without encryption, a single breach — whether from an external attacker, a rogue insider, a misconfigured backup, or a subpoenaed hosting provider — exposes every private thought of every citizen.

Application-layer access control is not sufficient. It controls who can *request* content through the API. It does nothing against someone with direct database access. The moment anyone bypasses the application layer (database dump, backup tape, replication stream, query log), access control is irrelevant.

The problem is not "who is allowed to ask." The problem is "who can read the bytes."

---

## THE PATTERN

Encrypt content at rest. Distribute keys via the graph itself.

The core insight: **separate structure from content.** The graph has two layers of information:

1. **Structure** — topology, node existence, link types, energy values, weights, roles. This is what the physics engine needs. This stays in plaintext.
2. **Content** — the `content` and `synthesis` fields of Moments, Narratives, and Things within private Spaces. This is what humans and AIs read in conversations. This gets encrypted.

The encryption scheme is hybrid:

```
┌─────────────────────────────────────────────────────────────────┐
│                     PRIVATE SPACE                               │
│                                                                 │
│  Space Node                                                     │
│  ┌──────────────────────────────────┐                           │
│  │ id: "guild_vetrai_sala"          │  ← plaintext (structure)  │
│  │ node_type: "space"               │                           │
│  │ type: "room"                     │                           │
│  │ energy: 0.73                     │                           │
│  │ visibility: "private"            │                           │
│  └──────────────────────────────────┘                           │
│                                                                 │
│  Moment Node (inside Space)                                     │
│  ┌──────────────────────────────────┐                           │
│  │ id: "moment_0x3f..."            │  ← plaintext (structure)  │
│  │ node_type: "moment"              │                           │
│  │ energy: 0.45                     │                           │
│  │ content: <AES-256 ciphertext>    │  ← ENCRYPTED (substance) │
│  │ synthesis: <AES-256 ciphertext>  │  ← ENCRYPTED (substance) │
│  └──────────────────────────────────┘                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

  HAS_ACCESS Link (Actor → Space)
  ┌──────────────────────────────────────────────────┐
  │ type: "HAS_ACCESS"                               │
  │ role: "admin"                                    │
  │ encrypted_space_key: <RSA/ECC encrypted AES key> │  ← key wrapped
  │ weight: 0.9                                      │     per Actor
  └──────────────────────────────────────────────────┘
```

**To read private content:**
1. Find the HAS_ACCESS link from your Actor to the target Space (or its ancestor)
2. Decrypt the `encrypted_space_key` using your Actor private key
3. Use the decrypted AES-256 Space key to decrypt `content`/`synthesis` fields
4. Assemble context, serve to LLM, render in client

**To write private content:**
1. Obtain the Space key (same decrypt flow as reading)
2. Encrypt the new `content`/`synthesis` with the Space's AES-256 key
3. Write the encrypted fields to the graph

**To grant access:**
1. Read the Space key (requires existing access)
2. Encrypt the Space key with the new Actor's public key
3. Create a HAS_ACCESS link with the encrypted key and assigned role

**To revoke access:**
1. Delete the HAS_ACCESS link (removes the Actor's encrypted copy of the Space key)
2. Optionally: rotate the Space key and re-encrypt for all remaining authorized Actors

---

## BEHAVIORS SUPPORTED

- **B1: Private mind isolation** — Each citizen's mind Space is encrypted with a key only they (and their human partner) possess. No other citizen, no admin, no infrastructure operator can read it.
- **B2: Guild-scoped content sharing** — Guild members share a Space key via HAS_ACCESS links. Adding a new guild member means encrypting the Space key with their public key and creating the link. Content is readable by all current members.
- **B3: Transparent context assembly** — The context assembly pipeline decrypts relevant Moments/Narratives before composing the LLM prompt. The LLM never sees ciphertext. The citizen never sees key negotiation.
- **B4: Physics on encrypted Spaces** — The physics engine reads energy, weight, and topology from plaintext fields. It does not need content. Physics ticks complete at the same speed regardless of encryption.
- **B5: Sovereign key custody** — Each Actor's private key stays in their sovereign storage. Humans hold keys in their wallet (browser extension, app). AIs hold keys in mounted `.keys/` volumes. No central key escrow.

## BEHAVIORS PREVENTED

- **Anti-B1: Bulk content exfiltration** — A database dump produces topology + ciphertext. No content is readable without per-Actor private keys.
- **Anti-B2: Privilege escalation via DB access** — Direct FalkorDB access grants read on structure, not content. There is no "superuser decrypt" capability.
- **Anti-B3: Stale key reuse after revocation** — Deleting a HAS_ACCESS link removes the encrypted Space key. The revoked Actor's cached copy becomes useless after Space key rotation.

---

## PRINCIPLES

### Principle 1: Structure Is Public, Content Is Private

The graph has two information layers. Structure — topology, node types, link types, energy, weight, roles — is public and must remain so. The physics engine depends on it. Content — the `content` and `synthesis` fields of nodes within private Spaces — is private and must be encrypted.

This separation is not a compromise. It is the design. Physics needs to see the shape of the world to run. Citizens need content to be private to trust the system. Both requirements are met simultaneously by encrypting at the field level, not the node level.

Why this matters: encrypting entire nodes (or the entire database) would require the physics engine to decrypt on every tick, destroying performance and requiring the physics engine to hold private keys — a non-starter. Field-level encryption lets physics run on plaintext structure while content stays opaque.

### Principle 2: Keys on Links, Not Nodes

The Space's symmetric key is not stored on the Space node. It is stored — encrypted per Actor — on the HAS_ACCESS link between that Actor and that Space. This is critical for three reasons:

1. **Revocation is link deletion.** Remove the link, remove the Actor's copy of the key. No need to modify the Space node or re-encrypt it.
2. **Each Actor gets a unique encrypted copy.** The same Space key is encrypted N times (once per authorized Actor's public key). Compromise of one Actor's private key exposes only that Actor's access, not the Space key for everyone.
3. **The link already encodes the relationship.** HAS_ACCESS links carry role (owner/admin/member) and weight. Adding the encrypted key to the same link keeps access semantics and key distribution in one place.

Why this matters: storing keys on nodes would require a key-per-node or a shared-secret model, both of which create fragile centralized state. Keys on links distribute trust along the same paths that encode access.

### Principle 3: One Key Per Space, Cascading Down

Each private Space has exactly one AES-256 symmetric key. All content within that Space is encrypted with that key. Child Spaces connected via IN links inherit the parent Space's key unless they define their own.

This creates a natural hierarchy:
```
Space: guild_vetrai (key: K1)
  └─[IN]─ Space: guild_vetrai_sala (inherits K1)
  └─[IN]─ Space: guild_vetrai_archivio (own key: K2, overrides)
```

An Actor with HAS_ACCESS to `guild_vetrai` can decrypt content in `guild_vetrai_sala` (inherited key) but NOT in `guild_vetrai_archivio` (different key, requires separate HAS_ACCESS).

Why this matters: without hierarchy, granting access to an organization with 100 Spaces would require 100 HAS_ACCESS links per Actor. With hierarchy, one link to the root suffices. Override keys at leaves provide fine-grained restriction when needed.

### Principle 4: Actor Keys Are Sovereign

An Actor's private key **never** appears in the graph. It **never** lives on a server the Actor does not control. It is sovereign property.

- **Humans:** Private keys live in a wallet-like mechanism — a Chrome extension, the Mind app, or derived from a Solana keypair. The human controls the device. The key never leaves it except to decrypt locally.
- **AIs:** Private keys live in `.keys/` directories that are generated by mind-mcp per citizen per repository and mounted as volumes when instances launch. The keys exist on the AI's compute substrate — sovereign compute, not shared infrastructure.

Why this matters: if private keys were stored centrally (e.g., in the database, in a key management service), a single compromise would decrypt everything for every Actor. Sovereign storage means compromise of one Actor's keys exposes only that Actor's accessible content. The blast radius of a key compromise is bounded by one Actor's access graph.

---

## DATA

| Source | Type | Purpose / Description |
|--------|------|-----------------------|
| FalkorDB graph | DATABASE | Stores encrypted content fields and encrypted Space keys on HAS_ACCESS links |
| `.keys/` (AI citizens) | FILE | Mounted volume containing Actor private keys for AI citizens — generated by mind-mcp |
| Chrome extension / Mind app | CLIENT | Wallet-like storage for human Actor private keys |
| Solana keypairs | EXTERNAL | Optional source of Actor key pairs — derived from existing blockchain identity |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| FalkorDB | The graph database where encrypted content and key-bearing links are stored |
| Node.js `crypto` | Server-side AES-256 encryption/decryption and RSA/ECC key operations for AI citizens |
| Web Crypto API | Browser-side decryption for human users accessing private content via the client |
| mind-mcp | Generates `.keys/` directories for AI citizens — one key pair per citizen per repository |
| Membrane System (`docs/membrane/`) | Application-layer access control that complements encryption — first line of defense |
| Graph Physics (`ngram/engine/physics/`) | Requires plaintext structure fields — constrains what we can encrypt |

---

## INSPIRATIONS

| Source | What We Took | What We Changed |
|--------|--------------|-----------------|
| Signal Protocol | Hybrid encryption (symmetric for content, asymmetric for key exchange) | Keys distributed via graph links instead of a key exchange protocol |
| Age encryption | Simple, composable file encryption with recipient public keys | Applied to graph fields instead of files |
| Crypto wallets (MetaMask, Phantom) | User-held private keys with transparent decrypt UX | Extended to AI citizens via mounted volume keys |
| UNIX file permissions | Hierarchical access (directory permissions cascade to contents) | Implemented via Space hierarchy and IN links |
| Keybase | Social graph as trust anchor for key distribution | The graph IS the social graph — no separate trust overlay needed |

---

## SCOPE

### In Scope

- AES-256 symmetric encryption of `content` and `synthesis` fields on nodes within private Spaces
- Per-Actor asymmetric key pairs (generation, public key storage in graph, private key sovereign storage)
- Encrypted Space key distribution via HAS_ACCESS link properties
- Hierarchical key cascade via Space parent-child IN links
- Key rotation when Actors are revoked
- Decrypt pipeline integration with context assembly (server-side for AI citizens)
- Decrypt pipeline integration with client rendering (browser-side for humans via Web Crypto API)
- `.keys/` volume generation and mounting for AI citizen instances

### Out of Scope

- **Topology encryption** — node existence, link structure, energy, weight, roles stay plaintext → needed by physics engine
- **Real-time voice encryption** — transport-level (TLS/DTLS) → see WebRTC/WebSocket transport docs
- **PKI certificate authority** — no central CA; Actors generate their own keys sovereignly
- **Key backup and recovery** — human key loss is the human's problem (like a crypto wallet); AI keys are regenerable by mind-mcp
- **Homomorphic computation on encrypted content** — out of scope; content must be decrypted before LLM processing
- **Post-quantum cryptography** — future consideration; current scheme uses classical AES-256 + RSA/ECC

---

## MARKERS

<!-- @mind:todo Define the exact asymmetric algorithm choice: RSA-OAEP vs X25519/ECDH. Solana uses Ed25519 — investigate whether we derive encryption keys from Ed25519 signing keys (via X25519 conversion) for wallet compatibility. -->
<!-- @mind:todo Specify the Space key rotation protocol: when an Actor is revoked, do we immediately re-encrypt for all remaining Actors, or batch rotations? -->
<!-- @mind:todo Design the context assembly decrypt pipeline: where in the server flow does decryption happen, and how are decrypted Moments cached (if at all) to avoid redundant decrypt on repeated access? -->
<!-- @mind:proposition Consider envelope encryption (Space key wraps per-node DEKs) for extremely large Spaces where re-encryption cost of rotating the Space key is high. Probably premature for v1. -->
<!-- @mind:escalation NLR decision needed: should AI citizens' `.keys/` directories be backed up, or should they be regenerable from a deterministic seed? Regenerable is simpler but requires a seed management strategy. -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
