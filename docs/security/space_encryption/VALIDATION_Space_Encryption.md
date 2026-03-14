# Space Encryption — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
PATTERNS:        ./PATTERNS_Space_Encryption.md
BEHAVIORS:       ./BEHAVIORS_Space_Encryption.md
THIS:            VALIDATION_Space_Encryption.md (you are here)
ALGORITHM:       ./ALGORITHM_Space_Encryption.md (HOW — mechanisms go here)
IMPLEMENTATION:  ./IMPLEMENTATION_Space_Encryption.md
HEALTH:          ./HEALTH_Space_Encryption.md
SYNC:            ./SYNC_Space_Encryption.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the system has failed its purpose?

These are the value-producing invariants — the things that make Space encryption worth building. If content leaks, if keys escape the graph, if revoked Actors can still read, if the physics tick stalls on decryption — the system has failed.

---

## INVARIANTS

### V1: Content Confidentiality

**Why we care:** This is the entire reason Space encryption exists. If private content is readable without keys, every private Space in the graph is exposed. A single plaintext leak in a private Space means the encryption system has no value.

```
MUST:   content and synthesis fields of nodes in private Spaces are AES-256-GCM ciphertext in FalkorDB
NEVER:  plaintext content persisted to graph, disk, or logs for private Spaces
```

### V2: Key Sovereignty

**Why we care:** If Actor private keys escape the Actor's device, the entire trust model collapses. Anyone with a private key can decrypt every Space that Actor has access to. There is no recovery from private key compromise short of full key rotation across all affected Spaces.

```
MUST:   Actor private keys exist only on the Actor's device or compute (wallet, browser extension, .keys/ directory)
NEVER:  private keys stored in the graph, in logs, in environment variables, or transmitted over the network
```

### V3: Graph-Distributed Keys

**Why we care:** The Space symmetric key is the single secret that protects all content in a Space. If it appears in plaintext anywhere in the graph, any query can extract it and decrypt all content. The hybrid encryption model depends on Space keys existing only as X25519-encrypted values on HAS_ACCESS links.

```
MUST:   Space symmetric keys distributed exclusively via encrypted_key property on HAS_ACCESS links
NEVER:  Space keys stored in plaintext in the graph, in node properties, or in any persistent store
```

### V4: Hierarchical Access Correctness

**Why we care:** Hierarchical access (parent grants access to children) is a convenience that must not become a security hole. If the hierarchy walk is unbounded, it could grant unintended access. If it fails to cascade, users lose expected access. Both are broken.

```
MUST:   HAS_ACCESS to a parent Space grants decryption capability for all child Spaces (via IN links, max 5 levels)
NEVER:  child Space accessible without parent access (unless a separate direct HAS_ACCESS link exists)
```

### V5: Revocation Completeness

**Why we care:** If a revoked Actor can still decrypt new content, revocation is theater. Key rotation after revocation is what provides forward secrecy. Partial rotation (some content re-encrypted, some not) is worse than no rotation because it creates a false sense of security.

```
MUST:   after revocation, the old Space key is replaced, all content is re-encrypted with the new key, and all remaining members receive the new encrypted key
NEVER:  revoked Actor able to decrypt content written after their revocation
```

### V6: Physics Isolation

**Why we care:** The physics tick runs every cycle and must complete in under 1 second. If it ever attempts decryption, it needs key material — which means either storing keys in the tick process (security violation) or blocking on key retrieval (performance violation). Physics must be designed to never need encrypted fields.

```
MUST:   physics engine operates entirely on plaintext fields (energy, weight, type, timestamps)
NEVER:  physics tick reads content or synthesis fields, holds decryption keys, or calls decrypt functions
```

### V7: Zero Encryption for Public

**Why we care:** Public Spaces serve the majority of graph content. Encrypting public content wastes CPU, adds latency, and creates failure modes (key management for content that has no secrecy requirement). The encryption path must short-circuit completely for public Spaces.

```
MUST:   public Spaces have zero encryption overhead — content stored and read as plaintext
NEVER:  public content encrypted, public Spaces assigned Space keys, or HAS_ACCESS links created for public access
```

### V8: Rotation Atomicity

**Why we care:** If key rotation fails midway, the Space is left with a mix of old-key and new-key encrypted content. This state is unrecoverable without both keys, and the system cannot know which nodes use which key. Partial rotation is a data loss scenario.

```
MUST:   key rotation completes fully (all content re-encrypted, all links updated) or rolls back entirely
NEVER:  Space left with a mix of old-key and new-key encrypted content after a rotation attempt
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Encryption provides no value; content exposed |
| **HIGH** | Major value lost | Security degraded; attack surface opened |
| **MEDIUM** | Partial value lost | System works but with inefficiency or risk of edge-case failure |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Content Confidentiality | CRITICAL |
| V2 | Key Sovereignty | CRITICAL |
| V3 | Graph-Distributed Keys | HIGH |
| V4 | Hierarchical Access Correctness | HIGH |
| V5 | Revocation Completeness | HIGH |
| V6 | Physics Isolation | HIGH |
| V7 | Zero Encryption for Public | MEDIUM |
| V8 | Rotation Atomicity | MEDIUM |

---

## MARKERS

<!-- @mind:todo V5 — define acceptable window between revocation and rotation completion (is async rotation OK?) -->
<!-- @mind:todo V8 — verify FalkorDB transaction guarantees are sufficient for atomic batch re-encryption -->
<!-- @mind:proposition Consider V9: Audit Trail — every grant/revoke/rotation logged as a Moment for forensics -->
<!-- @mind:escalation V2 key sovereignty for AI citizens — .keys/ directory security depends on volume mount isolation; is this sufficient? -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
