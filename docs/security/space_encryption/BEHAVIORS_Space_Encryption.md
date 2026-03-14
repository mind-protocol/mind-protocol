# Space Encryption — Behaviors: Observable Effects of Graph-Level Content Protection

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
THIS:            BEHAVIORS_Space_Encryption.md (you are here)
PATTERNS:        ./PATTERNS_Space_Encryption.md
MECHANISMS:      —
ALGORITHM:       ./ALGORITHM_Space_Encryption.md
VALIDATION:      ./VALIDATION_Space_Encryption.md
HEALTH:          ./HEALTH_Space_Encryption.md
IMPLEMENTATION:  ./IMPLEMENTATION_Space_Encryption.md
SYNC:            ./SYNC_Space_Encryption.md

IMPL:            src/security/space_encryption.ts (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## BEHAVIORS

### B1: Private Content Is Unreadable Without Keys

**Why:** The entire encryption system exists to guarantee that a graph breach does not leak private content. If ciphertext is not stored, there is no confidentiality.

```
GIVEN:  a Moment node in a private Space
WHEN:   anyone reads the node from FalkorDB directly (including after a breach)
THEN:   the content and synthesis fields contain AES-256-GCM ciphertext, not plaintext
AND:    all other fields (id, type, energy, weight, created_at) remain in plaintext
```

### B2: Authorized Actors Can Decrypt Content

**Why:** Encryption is useless if legitimate users cannot recover plaintext. The hybrid key scheme (symmetric Space key wrapped per-Actor) must complete the round trip cleanly.

```
GIVEN:  an Actor with a HAS_ACCESS link to a Space
WHEN:   they request content from that Space
THEN:   the system retrieves their encrypted_key from the HAS_ACCESS link
AND:    decrypts the Space key with the Actor's private key
AND:    decrypts the content and synthesis fields with the Space key
AND:    returns plaintext to the caller
```

### B3: Access Cascades Through Hierarchy

**Why:** Spaces nest (parent/child via IN links). An Actor authorized on a parent Space should not need separate keys for every child. Hierarchy reduces key management overhead while preserving the security boundary.

```
GIVEN:  an Actor with HAS_ACCESS to a parent Space
WHEN:   they request content from a child Space (linked via IN, max 5 levels deep)
THEN:   the parent's Space key decrypts the child's content (child inherits parent key unless overridden)
AND:    the hierarchy walk stops at 5 levels to prevent unbounded traversal
```

### B4: Owner Can Grant and Revoke Access

**Why:** Access control must be owner-driven. Granting access means encrypting the Space key for the new Actor so they can decrypt independently without ever seeing anyone else's private key.

```
GIVEN:  an Actor with role "owner" on a Space
WHEN:   they grant access to another Actor with a specified role
THEN:   the Space key is encrypted with the new Actor's public key
AND:    a new HAS_ACCESS link is created with the role and encrypted_key properties
```

### B5: Revocation Triggers Key Rotation

**Why:** Removing a member's link is not enough — they may have cached the old Space key. Key rotation ensures forward secrecy: revoked Actors cannot decrypt any content written after revocation.

```
GIVEN:  a member is revoked from a Space
WHEN:   their HAS_ACCESS link is removed
THEN:   a new AES-256 Space key is generated
AND:    all content in the Space is re-encrypted with the new key
AND:    remaining members' HAS_ACCESS links are updated with the new encrypted_key
```

### B6: Public Spaces Have No Encryption Overhead

**Why:** Encrypting public content wastes CPU and adds latency for zero security benefit. Public Spaces must remain fast and simple.

```
GIVEN:  a Space with no HAS_ACCESS links (public)
WHEN:   content is written or read
THEN:   content is stored and retrieved in plaintext
AND:    no encryption or decryption step is performed
```

### B7: Physics Engine Never Needs Decryption

**Why:** The physics tick must complete in under 1 second. If it needed to decrypt content, it would be both slow and a security risk (requiring key material in the tick process). Plaintext metadata fields are sufficient for energy propagation.

```
GIVEN:  the physics tick running
WHEN:   it reads node properties for energy propagation and decay
THEN:   it only reads plaintext fields (energy, weight, type, timestamps)
AND:    it never accesses content or synthesis fields
AND:    it never holds or requests any decryption keys
```

---

## OBJECTIVES SERVED

| Behavior ID | Objective | Why It Matters |
|-------------|-----------|----------------|
| B1 | Content confidentiality at rest | Prevents data exposure from graph breach or unauthorized access |
| B2 | Usable encryption | Encryption that blocks legitimate users is worse than no encryption |
| B3 | Hierarchical access model | Reduces key management complexity for nested Space structures |
| B4 | Owner-controlled access | Enables self-sovereign permission management without a central authority |
| B5 | Forward secrecy after revocation | Prevents ex-members from reading future content |
| B6 | Zero overhead for public content | Keeps public Spaces performant and simple |
| B7 | Physics isolation from secrets | Ensures the physics tick stays fast and never touches key material |

---

## INPUTS / OUTPUTS

### Primary Function: `encrypt_content()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| space_id | string | ID of the target Space |
| content | string | Plaintext content to encrypt |
| synthesis | string | Plaintext synthesis to encrypt |
| actor_id | string | ID of the Actor performing the write |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| encrypted_content | bytes | AES-256-GCM ciphertext of content field |
| encrypted_synthesis | bytes | AES-256-GCM ciphertext of synthesis field |
| iv | bytes (12) | GCM nonce used for this encryption |

**Side Effects:**

- Encrypted fields written to FalkorDB node properties
- No plaintext persisted to disk or graph for private Spaces

### Primary Function: `decrypt_content()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| space_id | string | ID of the source Space |
| actor_id | string | ID of the Actor requesting decryption |
| node_id | string | ID of the node whose content to decrypt |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| content | string | Decrypted plaintext content |
| synthesis | string | Decrypted plaintext synthesis |

**Side Effects:**

- Plaintext exists only in memory, never persisted
- HAS_ACCESS link traversal logged for audit

### Primary Function: `grant_access()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| space_id | string | ID of the Space to grant access to |
| grantor_id | string | ID of the Actor granting access (must be owner or admin) |
| grantee_id | string | ID of the Actor receiving access |
| role | string | Role to assign: "owner", "admin", or "member" |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| has_access_link | HAS_ACCESS | The created link with role and encrypted_key |

**Side Effects:**

- New HAS_ACCESS link created in graph
- Space key encrypted with grantee's public key

### Primary Function: `revoke_access()`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| space_id | string | ID of the Space to revoke access from |
| revoker_id | string | ID of the Actor revoking access (must be owner or admin) |
| revokee_id | string | ID of the Actor being revoked |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| rotation_result | RotationResult | Summary: nodes re-encrypted, members updated, success/failure |

**Side Effects:**

- HAS_ACCESS link removed for revoked Actor
- New Space key generated
- All content in Space re-encrypted
- All remaining HAS_ACCESS links updated with new encrypted_key

---

## EDGE CASES

### E1: Actor Has Access via Multiple Paths

```
GIVEN:  an Actor has direct HAS_ACCESS to a child Space AND access via parent hierarchy
THEN:   direct access takes precedence (use the child Space's own key if it has one)
```

### E2: Space Key Rotation During Active Read

```
GIVEN:  an Actor begins decrypting content with the current key
         AND key rotation starts before they finish
THEN:   the read completes with the old key (rotation does not invalidate in-flight reads)
AND:    subsequent reads use the new key
```

### E3: Child Space Overrides Parent Key

```
GIVEN:  a child Space has its own HAS_ACCESS links (separate from parent)
THEN:   the child uses its own Space key, not the parent's
AND:    parent access does NOT cascade into this child
```

### E4: Actor's Key Pair Not Yet Generated

```
GIVEN:  an Actor is granted access but has no key pair registered
THEN:   the grant fails with an error indicating the Actor needs to generate keys first
AND:    no HAS_ACCESS link is created
```

### E5: Hierarchy Depth Exceeds 5 Levels

```
GIVEN:  a Space is nested more than 5 levels deep via IN links
THEN:   access does not cascade beyond 5 levels
AND:    deeper Spaces require explicit HAS_ACCESS links
```

---

## ANTI-BEHAVIORS

What should NOT happen:

### A1: Private Keys Never Appear in Graph

```
GIVEN:   any operation involving Actor private keys
WHEN:    the operation writes to FalkorDB
MUST NOT: store private keys as node properties, link properties, or Moment content
INSTEAD:  private keys remain exclusively on Actor's device (.keys/ directory or wallet)
```

### A2: Plaintext Content Never Persists for Private Spaces

```
GIVEN:   a write operation to a private Space
WHEN:    content is stored in FalkorDB
MUST NOT: write unencrypted content or synthesis fields to any node property
INSTEAD:  encrypt with AES-256-GCM before writing; plaintext exists only in memory
```

### A3: Physics Tick Never Touches Encrypted Fields

```
GIVEN:   the physics tick iterating over graph nodes
WHEN:    it reads node properties
MUST NOT: read content or synthesis fields, or request decryption keys
INSTEAD:  read only energy, weight, type, and timestamp fields
```

### A4: Admins Cannot Escalate to Owner

```
GIVEN:   an Actor with role "admin" on a Space
WHEN:    they attempt to grant "owner" role to any Actor
MUST NOT: succeed — only owners can grant owner role
INSTEAD:  return authorization error
```

---

## MARKERS

<!-- @mind:todo B5 key rotation performance — benchmark re-encryption cost for Spaces with >1000 nodes -->
<!-- @mind:proposition Consider async key rotation with a "rotating" state flag on the Space -->
<!-- @mind:escalation E2 concurrent read during rotation — need to decide on locking strategy vs eventual consistency -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
