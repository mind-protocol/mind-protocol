# Space Encryption — Algorithm: Hybrid Encryption for Graph-Resident Content

```
STATUS: DESIGNING
CREATED: 2026-03-13
VERIFIED: —
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
BEHAVIORS:       ./BEHAVIORS_Space_Encryption.md
PATTERNS:        ./PATTERNS_Space_Encryption.md
MECHANISMS:      —
THIS:            ALGORITHM_Space_Encryption.md (you are here)
VALIDATION:      ./VALIDATION_Space_Encryption.md
HEALTH:          ./HEALTH_Space_Encryption.md
IMPLEMENTATION:  ./IMPLEMENTATION_Space_Encryption.md
SYNC:            ./SYNC_Space_Encryption.md

IMPL:            src/security/space_encryption.ts (to be created)
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC. Run tests.

---

## OVERVIEW

Space encryption protects private content in the Mind Protocol graph using hybrid encryption. AES-256-GCM (symmetric) encrypts content for speed. X25519 (asymmetric) distributes the per-Space symmetric key to each authorized Actor via their HAS_ACCESS link.

One graph per universe. Public Spaces store plaintext. Private Spaces store ciphertext in content/synthesis fields while leaving metadata (id, type, energy, weight, timestamps) in plaintext so the physics engine can operate without decryption. Key distribution is fully graph-native: the encrypted Space key lives as a property on each Actor's HAS_ACCESS link.

---

## OBJECTIVES AND BEHAVIORS

| Objective | Behaviors Supported | Why This Algorithm Matters |
|-----------|---------------------|----------------------------|
| Content confidentiality at rest | B1, B2 | AES-256-GCM ensures ciphertext in graph; hybrid scheme enables per-Actor decryption |
| Hierarchical access | B3 | Parent key inheritance reduces key management without weakening boundaries |
| Owner-controlled permissions | B4 | Asymmetric wrapping lets owners distribute keys without exposing them |
| Forward secrecy after revocation | B5 | Key rotation after revocation ensures old keys are useless for new content |
| Zero overhead for public content | B6 | Algorithm short-circuits entirely for public Spaces |
| Physics isolation | B7 | Algorithm never encrypts metadata fields the physics tick reads |

---

## DATA STRUCTURES

### SpaceKey

```
SpaceKey {
    space_id:   string       // ID of the Space this key belongs to
    key:        bytes[32]    // AES-256 symmetric key (256 bits)
    iv:         bytes[12]    // GCM nonce (96 bits), regenerated per encryption operation
}
```

### ActorKeyPair

```
ActorKeyPair {
    actor_id:    string      // ID of the Actor
    public_key:  bytes[32]   // X25519 public key
    private_key: bytes[32]   // X25519 private key (never stored in graph)
}

Storage:
    Humans  → wallet or browser extension
    AIs     → .keys/ directory mounted as volume
```

### EncryptedSpaceKey

```
EncryptedSpaceKey {
    ciphertext:  bytes       // X25519(space_key, actor_public_key)
    // Stored as "encrypted_key" property on HAS_ACCESS link
}
```

### HAS_ACCESS Link

```
HAS_ACCESS {
    from:           Actor node
    to:             Space node
    role:           "owner" | "admin" | "member"
    encrypted_key:  bytes    // EncryptedSpaceKey.ciphertext
    granted_at:     timestamp
    granted_by:     string   // Actor ID of the grantor
}
```

### Encrypted Node Fields

```
Node (in private Space) {
    id:           string      // plaintext
    type:         string      // plaintext
    energy:       float       // plaintext — physics reads this
    weight:       float       // plaintext — physics reads this
    created_at:   timestamp   // plaintext
    updated_at:   timestamp   // plaintext
    content:      bytes       // AES-256-GCM ciphertext
    synthesis:    bytes       // AES-256-GCM ciphertext
    iv:           bytes[12]   // GCM nonce for this node's encryption
    auth_tag:     bytes[16]   // GCM authentication tag
}
```

---

## ALGORITHM: Space Creation

### Step 1: Determine Privacy

Check whether the Space is public or private. Public Spaces skip all encryption setup.

```
IF space.visibility == "public":
    CREATE Space node with plaintext fields
    RETURN  // no encryption setup needed
```

### Step 2: Generate Space Key

Generate a cryptographically random AES-256 key for the Space. This key never exists in the graph in plaintext.

```
space_key = crypto.randomBytes(32)   // 256-bit AES key
```

### Step 3: Wrap Key for Owner

Encrypt the Space key with the owner's X25519 public key. Store the result on the HAS_ACCESS link.

```
encrypted_key = x25519_encrypt(space_key, owner.public_key)
CREATE HAS_ACCESS link:
    from:          owner
    to:            space
    role:          "owner"
    encrypted_key: encrypted_key
    granted_at:    now()
    granted_by:    owner.id
```

### Step 4: Discard Plaintext Key

The plaintext Space key is held only in memory during creation. After wrapping, it is zeroed and discarded.

```
secure_zero(space_key)
```

---

## ALGORITHM: Content Write

### Step 1: Resolve Space Privacy

```
IF space.visibility == "public":
    WRITE content and synthesis as plaintext
    RETURN
```

### Step 2: Retrieve and Unwrap Space Key

The writing Actor decrypts the Space key from their own HAS_ACCESS link.

```
link = GET HAS_ACCESS from actor to space (direct or via hierarchy)
space_key = x25519_decrypt(link.encrypted_key, actor.private_key)
```

### Step 3: Encrypt Content Fields

Generate a fresh IV per write operation. Encrypt content and synthesis separately with AES-256-GCM.

```
iv = crypto.randomBytes(12)    // 96-bit GCM nonce
encrypted_content, tag_c  = aes256gcm_encrypt(content, space_key, iv)
encrypted_synthesis, tag_s = aes256gcm_encrypt(synthesis, space_key, iv)
```

### Step 4: Store Ciphertext

Write encrypted fields to the node. Leave metadata fields in plaintext.

```
SET node.content   = encrypted_content
SET node.synthesis = encrypted_synthesis
SET node.iv        = iv
SET node.auth_tag  = tag_c || tag_s    // concatenated authentication tags
// id, type, energy, weight, timestamps remain plaintext
```

### Step 5: Discard Plaintext

```
secure_zero(space_key)
secure_zero(content)
secure_zero(synthesis)
```

---

## ALGORITHM: Content Read

### Step 1: Resolve Space Privacy

```
IF space.visibility == "public":
    RETURN node.content, node.synthesis  // plaintext
```

### Step 2: Check Access (Direct or Hierarchical)

Walk up the hierarchy via IN links, max 5 levels, looking for a HAS_ACCESS link.

```
function find_access(actor, space, depth=0):
    link = GET HAS_ACCESS from actor to space
    IF link exists:
        RETURN link

    IF depth >= 5:
        RETURN null   // hierarchy limit reached

    parent = GET Space linked via IN from space
    IF parent is null:
        RETURN null   // no parent, no access

    RETURN find_access(actor, parent, depth + 1)
```

### Step 3: Unwrap Space Key

```
link = find_access(actor, space)
IF link is null:
    RAISE AccessDenied("No HAS_ACCESS link found within hierarchy")

space_key = x25519_decrypt(link.encrypted_key, actor.private_key)
```

### Step 4: Decrypt Content

```
content   = aes256gcm_decrypt(node.content, space_key, node.iv, node.auth_tag[:16])
synthesis = aes256gcm_decrypt(node.synthesis, space_key, node.iv, node.auth_tag[16:])
```

### Step 5: Return and Discard

```
result = { content, synthesis }
secure_zero(space_key)
RETURN result   // plaintext in memory only, never persisted
```

---

## ALGORITHM: Grant Access

### Step 1: Authorize Grantor

```
grantor_link = GET HAS_ACCESS from grantor to space
IF grantor_link is null:
    RAISE AccessDenied("Grantor has no access")

IF role == "owner" AND grantor_link.role != "owner":
    RAISE AuthorizationError("Only owners can grant owner role")

IF role == "admin" AND grantor_link.role NOT IN ["owner"]:
    RAISE AuthorizationError("Only owners can grant admin role")

// Members can be granted by owners or admins
IF role == "member" AND grantor_link.role NOT IN ["owner", "admin"]:
    RAISE AuthorizationError("Insufficient role to grant member access")
```

### Step 2: Verify Grantee Has Key Pair

```
grantee_public_key = GET public_key for grantee
IF grantee_public_key is null:
    RAISE PreconditionError("Grantee has no registered public key")
```

### Step 3: Unwrap and Re-wrap Space Key

Grantor decrypts the Space key, then encrypts it for the grantee.

```
space_key     = x25519_decrypt(grantor_link.encrypted_key, grantor.private_key)
encrypted_key = x25519_encrypt(space_key, grantee_public_key)
secure_zero(space_key)
```

### Step 4: Create HAS_ACCESS Link

```
CREATE HAS_ACCESS link:
    from:          grantee
    to:            space
    role:          role
    encrypted_key: encrypted_key
    granted_at:    now()
    granted_by:    grantor.id
```

---

## ALGORITHM: Revoke Access + Key Rotation

### Step 1: Authorize Revoker

```
revoker_link = GET HAS_ACCESS from revoker to space
IF revoker_link.role NOT IN ["owner", "admin"]:
    RAISE AuthorizationError("Insufficient role to revoke")

IF revokee_link.role == "owner" AND revoker_link.role != "owner":
    RAISE AuthorizationError("Only owners can revoke owners")
```

### Step 2: Remove HAS_ACCESS Link

```
DELETE HAS_ACCESS from revokee to space
```

### Step 3: Generate New Space Key

```
new_space_key = crypto.randomBytes(32)
```

### Step 4: Re-encrypt All Content

Batch operation over all nodes in the Space. Must be atomic.

```
old_space_key = x25519_decrypt(revoker_link.encrypted_key, revoker.private_key)

BEGIN TRANSACTION
FOR EACH node IN space.nodes:
    IF node has encrypted content:
        // Decrypt with old key
        plaintext_content   = aes256gcm_decrypt(node.content, old_space_key, node.iv, ...)
        plaintext_synthesis = aes256gcm_decrypt(node.synthesis, old_space_key, node.iv, ...)

        // Re-encrypt with new key
        new_iv = crypto.randomBytes(12)
        node.content, tag_c   = aes256gcm_encrypt(plaintext_content, new_space_key, new_iv)
        node.synthesis, tag_s = aes256gcm_encrypt(plaintext_synthesis, new_space_key, new_iv)
        node.iv       = new_iv
        node.auth_tag = tag_c || tag_s

        secure_zero(plaintext_content)
        secure_zero(plaintext_synthesis)
COMMIT TRANSACTION

secure_zero(old_space_key)
```

### Step 5: Re-wrap Key for Remaining Members

```
remaining_links = GET all HAS_ACCESS links to space (excluding revokee)
FOR EACH link IN remaining_links:
    member_public_key = GET public_key for link.actor
    link.encrypted_key = x25519_encrypt(new_space_key, member_public_key)
    UPDATE link

secure_zero(new_space_key)
```

---

## ALGORITHM: Context Assembly (for LLM Calls)

### Step 1: Find Accessible Spaces

```
accessible = GET all HAS_ACCESS links from actor
spaces = [link.space for link in accessible]
```

### Step 2: Decrypt Relevant Content

```
context_fragments = []
FOR EACH space IN spaces:
    relevant_nodes = QUERY nodes in space matching context criteria
    space_key = x25519_decrypt(space.link.encrypted_key, actor.private_key)

    FOR EACH node IN relevant_nodes:
        IF space.visibility == "public":
            context_fragments.append(node.content)
        ELSE:
            plaintext = aes256gcm_decrypt(node.content, space_key, node.iv, ...)
            context_fragments.append(plaintext)
            secure_zero(plaintext)  // after copying to context buffer

    secure_zero(space_key)
```

### Step 3: Assemble and Return

```
context = assemble_prompt(context_fragments)
// Plaintext exists only in memory during assembly
// Never persisted back to graph
RETURN context
```

---

## KEY DECISIONS

### D1: Public vs Private Space

```
IF space.visibility == "public":
    Skip all encryption — store and read plaintext
    Why: zero overhead for public content (B6)
ELSE:
    Apply full hybrid encryption pipeline
    Why: content confidentiality at rest (B1)
```

### D2: Direct Access vs Hierarchical Lookup

```
IF actor has direct HAS_ACCESS to space:
    Use direct link's encrypted_key
    Why: direct access is fastest and most explicit
ELSE:
    Walk up IN hierarchy, max 5 levels
    Why: hierarchical inheritance reduces key management (B3)
    IF depth > 5: DENY access (prevent unbounded traversal)
```

### D3: Child Has Own Key vs Inherits Parent Key

```
IF child Space has its own HAS_ACCESS links:
    Use child's own Space key (independent encryption)
    Why: allows fine-grained access control at any level
ELSE:
    Inherit parent Space key
    Why: reduces key proliferation for simple hierarchies
```

### D4: Rotation Strategy

```
IF member is revoked:
    Rotate key immediately (synchronous)
    Why: forward secrecy is a security requirement (B5)
    Cost: O(content x members) — expensive but infrequent
ELSE IF key age > rotation_policy:
    Schedule rotation (asynchronous, future consideration)
    Why: defense in depth
```

---

## DATA FLOW

```
Content Write:
    plaintext content
        ↓
    resolve Space privacy (public → store plaintext, done)
        ↓
    retrieve encrypted_key from Actor's HAS_ACCESS link
        ↓
    X25519 decrypt → Space key (in memory)
        ↓
    AES-256-GCM encrypt content + synthesis
        ↓
    store ciphertext + iv + auth_tag in node
        ↓
    secure_zero Space key

Content Read:
    encrypted node
        ↓
    resolve Space privacy (public → return plaintext, done)
        ↓
    find HAS_ACCESS (direct or hierarchical, max 5 levels)
        ↓
    X25519 decrypt → Space key (in memory)
        ↓
    AES-256-GCM decrypt content + synthesis
        ↓
    return plaintext (in memory only)
        ↓
    secure_zero Space key

Key Rotation:
    revoke Actor
        ↓
    generate new AES-256 key
        ↓
    decrypt all content with old key → re-encrypt with new key (atomic transaction)
        ↓
    re-wrap new key for each remaining member
        ↓
    secure_zero old key + new key
```

---

## COMPLEXITY

**Time:**

- Encrypt/decrypt single node: O(1) — AES-256-GCM is constant-time for fixed-size blocks, ~0.1ms per node
- Hierarchical access check: O(d) where d <= 5 — bounded tree walk
- Grant access: O(1) — single key wrap operation
- Key rotation: O(n * m) where n = nodes in Space, m = remaining members — re-encrypt all content, re-wrap for all members
- Context assembly: O(k) where k = relevant nodes across accessible Spaces, with ~0.1ms decrypt overhead per node

**Space:**

- Per Space: 32 bytes key (in memory only during operations)
- Per HAS_ACCESS link: ~80 bytes encrypted_key property
- Per encrypted node: ~28 bytes overhead (12 byte IV + 16 byte auth tag)

**Bottlenecks:**

- Key rotation for large Spaces: re-encrypting thousands of nodes is O(n). Mitigated by batching within a transaction.
- Context assembly across many private Spaces: each Space requires a separate key unwrap. Mitigated by caching decrypted keys in memory for the duration of the assembly call.
- Hierarchy walk: up to 5 graph queries per access check. Mitigated by short max depth and potential caching.

---

## HELPER FUNCTIONS

### `x25519_encrypt(plaintext, public_key)`

**Purpose:** Encrypt a symmetric key (or small payload) using X25519 key exchange + symmetric cipher.

**Logic:** Generate ephemeral X25519 key pair. Perform Diffie-Hellman with recipient's public key to derive shared secret. Encrypt plaintext with derived key. Return ephemeral public key + ciphertext.

### `x25519_decrypt(ciphertext, private_key)`

**Purpose:** Decrypt a payload encrypted with x25519_encrypt.

**Logic:** Extract ephemeral public key from ciphertext. Perform Diffie-Hellman with own private key. Derive shared secret. Decrypt and return plaintext.

### `aes256gcm_encrypt(plaintext, key, iv)`

**Purpose:** Encrypt content with AES-256-GCM, producing ciphertext + authentication tag.

**Logic:** Standard AES-256-GCM encryption. Returns (ciphertext, auth_tag). The auth_tag provides integrity verification on decrypt.

### `aes256gcm_decrypt(ciphertext, key, iv, auth_tag)`

**Purpose:** Decrypt and verify AES-256-GCM ciphertext.

**Logic:** Standard AES-256-GCM decryption. Verifies auth_tag before returning plaintext. Raises IntegrityError if tag does not match (indicates tampering).

### `secure_zero(buffer)`

**Purpose:** Overwrite sensitive data in memory before releasing it.

**Logic:** Write zeros to the buffer. Prevents key material from lingering in memory after use.

### `find_access(actor, space, depth=0)`

**Purpose:** Find HAS_ACCESS link for an Actor, walking up the Space hierarchy if needed.

**Logic:** Check direct link first. If not found, follow IN link to parent Space, recurse. Stop at depth 5. Return the link or null.

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| FalkorDB graph | MATCH/CREATE/SET queries | Node and link data for HAS_ACCESS, Space, content nodes |
| Actor key storage | Read public_key from Actor node | X25519 public key for key wrapping |
| Actor device / .keys/ | Request private key for decrypt | X25519 private key (never leaves device) |
| Physics engine | (none — physics calls us never) | Physics reads only plaintext metadata fields |
| Context assembly | decrypt_content() | Plaintext content for LLM prompt construction |

---

## MARKERS

<!-- @mind:todo Benchmark key rotation for Spaces with >1000 nodes — determine if async rotation is needed -->
<!-- @mind:todo Define IV reuse prevention strategy — per-node IV storage vs counter-based -->
<!-- @mind:proposition Consider key caching with TTL during context assembly to avoid repeated X25519 operations -->
<!-- @mind:escalation Atomic re-encryption during rotation — FalkorDB transaction size limits may constrain batch size -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
