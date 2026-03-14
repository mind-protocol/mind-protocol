# Space Encryption — Health: Verification Mechanics and Coverage

```
STATUS: DESIGNING
CREATED: 2026-03-13
```

---

## WHEN TO USE HEALTH (NOT TESTS)

Health checks verify runtime behavior that tests cannot catch:

| Use Health For | Why |
|----------------|-----|
| Plaintext leaks in private Spaces | Requires scanning real graph data, not fixtures |
| Key distribution completeness | Emergent from real grant/revoke operations over time |
| Access hierarchy consistency | Only visible in real graph topology with nested Spaces |
| Private key leakage to graph | Must scan production node/link properties, not test data |
| Revocation completeness | Race conditions between revoke and async operations |

**Tests gate completion. Health monitors runtime.**

Tests verify that encrypt/decrypt functions work. Health verifies that no plaintext escapes to the graph during real operations.

---

## PURPOSE OF THIS FILE

This HEALTH file covers: Space Encryption runtime verification — ensuring non-public content remains encrypted in FalkorDB, keys are correctly distributed on HAS_ACCESS links, and no private key material leaks into the graph.

Why it exists: Encryption is a system where partial failure is invisible. A single bug that skips encryption on one code path leaks plaintext silently. Health checks are the only way to catch this in production.

Boundaries: This file does NOT verify access control policy (who should have access). It verifies encryption mechanics only (content is ciphertext, keys are distributed, private keys are absent from graph).

---

## WHY THIS PATTERN

HEALTH is separate from tests because:
- Tests use known plaintexts and keys; health samples real graph content
- Tests verify encrypt/decrypt round-trips; health verifies no code path bypasses encryption
- Tests run in CI with fixtures; health runs against the live FalkorDB graph

Docking-based checks are right here because graph-client.js has clear write/read boundaries where encryption must occur. Sampling graph content periodically catches bypasses that unit tests cannot.

Throttling protects performance because scanning graph nodes is IO-intensive — hourly sampling balances detection latency against FalkorDB load.

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Space_Encryption.md
PATTERNS:        ./PATTERNS_Space_Encryption.md
BEHAVIORS:       ./BEHAVIORS_Space_Encryption.md
ALGORITHM:       ./ALGORITHM_Space_Encryption.md
VALIDATION:      ./VALIDATION_Space_Encryption.md
IMPLEMENTATION:  ./IMPLEMENTATION_Space_Encryption.md
THIS:            HEALTH_Space_Encryption.md
SYNC:            ./SYNC_Space_Encryption.md

IMPL:            TBD (health checker script not yet implemented)
```

> **Contract:** HEALTH checks verify input/output against VALIDATION with minimal or no code changes. After changes: update IMPL or add TODO to SYNC. Run HEALTH checks at throttled rates.

---

## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)

```yaml
flows_analysis:
  - flow_id: content_write
    purpose: "Encrypt content before FalkorDB persistence — failure means plaintext leak"
    triggers:
      - type: event
        source: cities-of-light/src/server/graph-client.js:createMoment
        notes: "Any Moment creation in a private Space triggers encryption"
      - type: event
        source: cities-of-light/src/server/place-server.js:handlePlaceWrite
        notes: "Place tool writes trigger Moment creation"
      - type: event
        source: mind-mcp/mcp/tools/place_handler.py:write_to_place
        notes: "MCP tool writes from AI citizens"
    frequency:
      expected_rate: 10-50/hour
      peak_rate: 200/hour
      burst_behavior: Bursts during active conversations or physics tick batches — no backpressure needed, encryption is sub-millisecond
    risks:
      - Plaintext written to private Space (encryption bypassed)
      - Double encryption (content encrypted twice, unrecoverable)
    notes: Most critical flow — a single bypass leaks content permanently

  - flow_id: content_read
    purpose: "Decrypt content after FalkorDB retrieval — failure means gibberish in LLM prompts"
    triggers:
      - type: event
        source: cities-of-light/src/server/graph-client.js:getMomentContent
        notes: "Context assembly reads for LLM conversation"
      - type: event
        source: venezia/scripts/poc_mind_context_assembly.py:assemble_context
        notes: "Python context assembly for citizen conversations"
    frequency:
      expected_rate: 20-100/hour
      peak_rate: 500/hour
      burst_behavior: Bursts during active visitor conversations — each conversation triggers multiple context reads
    risks:
      - Ciphertext passed to LLM without decryption (gibberish in conversation)
      - Decryption with wrong key (garbage output, no error if tag check skipped)
    notes: Failure is visible to visitors — citizens speak gibberish

  - flow_id: access_grant
    purpose: "Distribute encrypted space key to new actor — failure means silent access denial"
    triggers:
      - type: event
        source: cities-of-light/src/server/graph-client.js:grantAccess
        notes: "Admin grants actor access to private Space"
    frequency:
      expected_rate: 1-5/hour
      peak_rate: 50/hour
      burst_behavior: Bursts during Space creation (owner + initial members granted simultaneously)
    risks:
      - HAS_ACCESS link created without encrypted_key (actor has role but cannot decrypt)
      - Key wrapped with wrong public key (actor has encrypted_key but cannot unwrap)
    notes: Failure is silent until actor tries to read — delayed detection
```

---

## HEALTH INDICATORS SELECTED

## OBJECTIVES COVERAGE

| Objective | Indicators | Why These Signals Matter |
|-----------|------------|--------------------------|
| No plaintext in private Spaces | h_content_encrypted | A single plaintext Moment in a private Space is a data breach |
| Key distribution correctness | h_key_distribution | Missing encrypted_key means actor cannot read — silent failure |
| Access hierarchy consistency | h_hierarchy_consistent | Orphan access (child without parent) causes confusing partial access |
| No private keys in graph | h_no_private_keys | Private key in graph is catastrophic — full compromise |
| Clean revocation | h_revocation_complete | Stale HAS_ACCESS links after revocation are residual access |

```yaml
health_indicators:
  - name: h_content_encrypted
    flow_id: content_write
    priority: high
    rationale: "Plaintext in a private Space is a data breach — must catch within 1 hour"

  - name: h_key_distribution
    flow_id: access_grant
    priority: high
    rationale: "Missing encrypted_key on HAS_ACCESS link means actor has role but cannot read — silent failure"

  - name: h_hierarchy_consistent
    flow_id: access_grant
    priority: med
    rationale: "Orphan access (child Space access without parent path) causes partial visibility — confusing but not a breach"

  - name: h_no_private_keys
    flow_id: content_write
    priority: high
    rationale: "Private key in graph properties means full compromise — any actor with DB access can decrypt everything"

  - name: h_revocation_complete
    flow_id: access_grant
    priority: med
    rationale: "Stale HAS_ACCESS links after revocation are residual access — actor may still decrypt cached content"
```

---

## STATUS (RESULT INDICATOR)

```yaml
status:
  stream_destination: .mind-mcp/health/space_encryption_health.yaml
  result:
    representation: enum
    value: UNKNOWN
    updated_at: 2026-03-13T00:00:00Z
    source: h_content_encrypted
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: content_encryption_checker
    purpose: Verify private Space Moments have encrypted (non-plaintext) content
    status: pending
    priority: high

  - name: key_distribution_checker
    purpose: Verify all HAS_ACCESS links to private Spaces have non-null encrypted_key
    status: pending
    priority: high

  - name: hierarchy_consistency_checker
    purpose: Verify child Space HAS_ACCESS links have corresponding parent access path
    status: pending
    priority: med

  - name: private_key_scan_checker
    purpose: Scan all node and link properties for private key patterns (PEM headers, raw key lengths)
    status: pending
    priority: high

  - name: revocation_completeness_checker
    purpose: After revocation events, verify no stale HAS_ACCESS links remain for revoked actor
    status: pending
    priority: med
```

---

## INDICATOR: h_content_encrypted

Verifies that content fields in private Space Moments are encrypted (base64 ciphertext), not plaintext UTF-8.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_content_encrypted
  client_value: "If even one Moment in a private Space contains plaintext, that content is exposed to anyone with database access"
  validation:
    - validation_id: V-ENC-1
      criteria: "All content in private Spaces is AES-256-GCM ciphertext"
    - validation_id: V-ENC-2
      criteria: "Encrypted content matches format iv:tag:ciphertext (base64)"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
    - float_0_1
  semantics:
    enum: OK=all sampled content encrypted, WARN=format anomaly detected, ERROR=plaintext found in private Space
    float_0_1: ratio of correctly encrypted Moments to total sampled private Moments (1.0 = all encrypted)
  aggregation:
    method: "worst-wins for enum, min for float"
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_graph_write
    method: graph-client.setNodeProperty
    location: cities-of-light/src/server/graph-client.js:TBD
  output:
    id: dock_privacy_check
    method: graph-client.checkSpacePrivacy
    location: cities-of-light/src/server/graph-client.js:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Sample random Moments from private Spaces and verify content is valid base64 ciphertext in iv:tag:ciphertext format"
  steps:
    - Query all Spaces where privacy != 'public'
    - For each private Space, sample up to 10 random Moment nodes
    - For each Moment, check content field matches regex ^[A-Za-z0-9+/=]+:[A-Za-z0-9+/=]+:[A-Za-z0-9+/=]+$
    - If content is valid UTF-8 that does not match ciphertext format, flag as plaintext leak
    - Compute ratio: encrypted_count / total_sampled
  data_required: FalkorDB graph (Space nodes with privacy property, Moment nodes with content property)
  failure_mode: "Moment.content in private Space is valid UTF-8 plaintext — not ciphertext format"
```

### INDICATOR

```yaml
indicator:
  error:
    - name: plaintext_leak
      linked_validation: [V-ENC-1]
      meaning: "Plaintext content found in private Space — data breach"
      default_action: alert
  warning:
    - name: format_anomaly
      linked_validation: [V-ENC-2]
      meaning: "Content does not match expected ciphertext format but is not plaintext"
      default_action: warn
  info:
    - name: encryption_ratio
      linked_validation: [V-ENC-1, V-ENC-2]
      meaning: "Ratio of encrypted to total sampled Moments"
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/hour
  burst_limit: 1
  backoff: "fixed 1 hour — no acceleration even on failure (avoid hammering FalkorDB)"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind-mcp/health/space_encryption_health.yaml
      transport: file
      notes: Local health status for Doctor to read
display:
  locations:
    - surface: CLI
      location: mind doctor --stream --module space_encryption
      signal: green/yellow/red
      notes: Green = all encrypted, Yellow = format anomaly, Red = plaintext found
```

### MANUAL RUN

```yaml
manual_run:
  command: "node scripts/health/check_space_encryption.js --indicator content_encrypted"
  notes: "Run after any change to graph-client.js write paths or crypto library"
```

---

## INDICATOR: h_key_distribution

Verifies that all HAS_ACCESS links to private Spaces have non-null `encrypted_key` properties.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_key_distribution
  client_value: "If HAS_ACCESS link exists without encrypted_key, actor has role-based access but cannot actually decrypt content — silent failure"
  validation:
    - validation_id: V-KEY-1
      criteria: "All HAS_ACCESS links to private Spaces have non-null encrypted_key"
    - validation_id: V-KEY-2
      criteria: "encrypted_key is valid base64 in nonce:encrypted format"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK=all links have encrypted_key, WARN=some links missing encrypted_key, ERROR=majority missing
  aggregation:
    method: "worst-wins"
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_link_write
    method: graph-client.grantAccess
    location: cities-of-light/src/server/graph-client.js:TBD
  output:
    id: dock_link_write
    method: graph-client.grantAccess
    location: cities-of-light/src/server/graph-client.js:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Query all HAS_ACCESS links to private Spaces and verify encrypted_key property is non-null and valid format"
  steps:
    - Query all HAS_ACCESS links where target Space has privacy != 'public'
    - For each link, check encrypted_key property is not null/empty
    - For each non-null encrypted_key, verify base64 format matches nonce:encrypted pattern
    - Count: links_with_key / total_links
  data_required: FalkorDB graph (HAS_ACCESS links, Space privacy property)
  failure_mode: "HAS_ACCESS link to private Space has null or empty encrypted_key"
```

### INDICATOR

```yaml
indicator:
  error:
    - name: key_distribution_failure
      linked_validation: [V-KEY-1]
      meaning: "HAS_ACCESS links exist without encrypted_key — actors cannot decrypt"
      default_action: alert
  warning:
    - name: key_format_invalid
      linked_validation: [V-KEY-2]
      meaning: "encrypted_key exists but format is wrong — may fail on decrypt"
      default_action: warn
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/hour
  burst_limit: 1
  backoff: "fixed 1 hour"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind-mcp/health/space_encryption_health.yaml
      transport: file
      notes: Appended to same health file as content encryption
display:
  locations:
    - surface: CLI
      location: mind doctor --stream --module space_encryption
      signal: green/yellow/red
      notes: Green = all keys distributed, Yellow = some missing, Red = majority missing
```

### MANUAL RUN

```yaml
manual_run:
  command: "node scripts/health/check_space_encryption.js --indicator key_distribution"
  notes: "Run after any grantAccess or revokeAccess changes"
```

---

## INDICATOR: h_no_private_keys

Scans all node and link properties in the graph for private key material. This is the most critical security check — a private key in the graph means full compromise.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_no_private_keys
  client_value: "A private key stored in FalkorDB means anyone with database access can decrypt all content in any Space that actor has access to"
  validation:
    - validation_id: V-SEC-1
      criteria: "No private key material (PEM headers, raw 32-byte keys) in any graph property"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1=no private keys found, 0=private key detected — CRITICAL
  aggregation:
    method: "AND (any 0 = global failure)"
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_graph_write
    method: graph-client.setNodeProperty
    location: cities-of-light/src/server/graph-client.js:TBD
  output:
    id: dock_graph_write
    method: graph-client.setNodeProperty
    location: cities-of-light/src/server/graph-client.js:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "Scan graph properties for patterns matching private key formats"
  steps:
    - Query all Actor nodes — check all string properties for PEM headers (BEGIN PRIVATE KEY, BEGIN EC PRIVATE KEY)
    - Query all HAS_ACCESS links — check all string properties for PEM headers
    - Check for raw base64 strings of exactly 32 or 64 bytes that are NOT encrypted_key or public_key
    - Flag any match as CRITICAL
  data_required: FalkorDB graph (all node and link string properties)
  failure_mode: "String matching private key pattern found in graph — immediate alert"
```

### INDICATOR

```yaml
indicator:
  error:
    - name: private_key_in_graph
      linked_validation: [V-SEC-1]
      meaning: "Private key material detected in FalkorDB — full compromise possible"
      default_action: page
  info:
    - name: scan_complete
      linked_validation: [V-SEC-1]
      meaning: "Scan completed, no private keys found"
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/hour
  burst_limit: 1
  backoff: "On detection: immediate re-scan after remediation. Otherwise fixed 1 hour."
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind-mcp/health/space_encryption_health.yaml
      transport: file
      notes: Binary result appended to health file
    - location: TBD (alerting system)
      transport: api
      notes: CRITICAL findings must page immediately — not just log
display:
  locations:
    - surface: CLI
      location: mind doctor --stream --module space_encryption
      signal: green/red
      notes: Green = clean, Red = private key found — no yellow state for this indicator
```

### MANUAL RUN

```yaml
manual_run:
  command: "node scripts/health/check_space_encryption.js --indicator no_private_keys"
  notes: "Run after any change to actor key management code or graph write paths"
```

---

## INDICATOR: h_hierarchy_consistent

Verifies that child Space HAS_ACCESS links have corresponding parent access paths via IN links.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_hierarchy_consistent
  client_value: "Orphan access (child Space accessible but parent not) causes confusing partial visibility — actor sees fragments without context"
  validation:
    - validation_id: V-HIER-1
      criteria: "For each child Space with HAS_ACCESS, a path to parent via IN links exists for the same actor (unless child has independent access grant)"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - enum
  semantics:
    enum: OK=hierarchy consistent, WARN=orphan access detected, ERROR=widespread hierarchy violations
  aggregation:
    method: "worst-wins"
    display: enum
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_link_write
    method: graph-client.grantAccess
    location: cities-of-light/src/server/graph-client.js:TBD
  output:
    id: dock_link_write
    method: graph-client.grantAccess
    location: cities-of-light/src/server/graph-client.js:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "For each HAS_ACCESS link on a child Space, verify actor also has access to parent Space (directly or via IN hierarchy)"
  steps:
    - Query all HAS_ACCESS links
    - For each link, find the Space's parent via IN link
    - If parent exists and is private, check actor has HAS_ACCESS to parent
    - If no parent access and no explicit independent_access flag, flag as orphan
  data_required: FalkorDB graph (HAS_ACCESS links, IN links between Spaces)
  failure_mode: "Actor has access to child Space but no path to parent — orphan access"
```

### INDICATOR

```yaml
indicator:
  warning:
    - name: orphan_access
      linked_validation: [V-HIER-1]
      meaning: "Actor has child Space access without parent — partial visibility"
      default_action: warn
  info:
    - name: hierarchy_clean
      linked_validation: [V-HIER-1]
      meaning: "All access follows hierarchy — no orphans"
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: schedule
  max_frequency: 1/6hours
  burst_limit: 1
  backoff: "fixed 6 hours — hierarchy changes are infrequent"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind-mcp/health/space_encryption_health.yaml
      transport: file
      notes: Appended to health file
display:
  locations:
    - surface: CLI
      location: mind doctor --stream --module space_encryption
      signal: green/yellow
      notes: Green = consistent, Yellow = orphan detected
```

### MANUAL RUN

```yaml
manual_run:
  command: "node scripts/health/check_space_encryption.js --indicator hierarchy_consistent"
  notes: "Run after bulk access grant/revoke operations"
```

---

## INDICATOR: h_revocation_complete

Verifies that after an access revocation, no stale HAS_ACCESS links remain for the revoked actor on the target Space or its children.

### VALUE TO CLIENTS & VALIDATION MAPPING

```yaml
value_and_validation:
  indicator: h_revocation_complete
  client_value: "Stale HAS_ACCESS links after revocation mean the revoked actor may still hold decrypted space key in memory or cache — residual access risk"
  validation:
    - validation_id: V-REV-1
      criteria: "After revokeAccess(actor, space), no HAS_ACCESS link from actor to space or child Spaces remains"
```

### HEALTH REPRESENTATION

```yaml
representation:
  selected:
    - binary
  semantics:
    binary: 1=clean revocation, 0=stale links found
  aggregation:
    method: "AND (any 0 = failure)"
    display: binary
```

### DOCKS SELECTED

```yaml
docks:
  input:
    id: dock_grant_input
    method: graph-client.revokeAccess
    location: cities-of-light/src/server/graph-client.js:TBD
  output:
    id: dock_link_write
    method: graph-client.revokeAccess
    location: cities-of-light/src/server/graph-client.js:TBD
```

### ALGORITHM / CHECK MECHANISM

```yaml
mechanism:
  summary: "After revocation event, query for any remaining HAS_ACCESS links from revoked actor to target Space or its descendants"
  steps:
    - On revocation event, capture actorId and spaceId
    - Query: MATCH (a:Actor {id: actorId})-[r:HAS_ACCESS]->(s:Space) WHERE s.id = spaceId OR (s)-[:IN*]->(target {id: spaceId}) RETURN r
    - If any links returned, flag as stale
  data_required: Revocation event payload (actorId, spaceId), FalkorDB graph
  failure_mode: "HAS_ACCESS link still exists after revocation — stale access"
```

### INDICATOR

```yaml
indicator:
  error:
    - name: stale_access_link
      linked_validation: [V-REV-1]
      meaning: "HAS_ACCESS link remains after revocation — residual access"
      default_action: alert
  info:
    - name: revocation_clean
      linked_validation: [V-REV-1]
      meaning: "Revocation completed cleanly — no stale links"
      default_action: log
```

### THROTTLING STRATEGY

```yaml
throttling:
  trigger: event (on revokeAccess call)
  max_frequency: 10/min
  burst_limit: 50/min
  backoff: "linear — revocations are infrequent, no storm expected"
```

### FORWARDINGS & DISPLAYS

```yaml
forwarding:
  targets:
    - location: .mind-mcp/health/space_encryption_health.yaml
      transport: file
      notes: Event-triggered result appended to health file
display:
  locations:
    - surface: CLI
      location: mind doctor --stream --module space_encryption
      signal: green/red
      notes: Green = clean revocation, Red = stale links found
```

### MANUAL RUN

```yaml
manual_run:
  command: "node scripts/health/check_space_encryption.js --indicator revocation_complete --actor ACTOR_ID --space SPACE_ID"
  notes: "Run after manual revocation to verify cleanup"
```

---

## HOW TO RUN

```bash
# Run all space encryption health checks
node scripts/health/check_space_encryption.js --all

# Run a specific checker
node scripts/health/check_space_encryption.js --indicator content_encrypted
node scripts/health/check_space_encryption.js --indicator key_distribution
node scripts/health/check_space_encryption.js --indicator no_private_keys
node scripts/health/check_space_encryption.js --indicator hierarchy_consistent
node scripts/health/check_space_encryption.js --indicator revocation_complete --actor ACTOR_ID --space SPACE_ID
```

---

## KNOWN GAPS

<!-- @mind:todo Health checker script not yet implemented (scripts/health/check_space_encryption.js) -->
<!-- @mind:todo V-ENC-1, V-ENC-2, V-KEY-1, V-KEY-2, V-SEC-1, V-HIER-1, V-REV-1 validation IDs referenced but not yet defined in VALIDATION doc -->
<!-- @mind:todo No alerting system configured for CRITICAL findings (h_no_private_keys) -->
<!-- @mind:todo Cross-language health check: verify Python encrypt -> JS decrypt round-trip in production graph -->
<!-- @mind:todo Browser-side key storage health: verify Chrome extension / Mind app key integrity (no checker path yet) -->

---

## MARKERS

<!-- @mind:todo Implement scripts/health/check_space_encryption.js -->
<!-- @mind:todo Implement content_encryption_checker -->
<!-- @mind:todo Implement key_distribution_checker -->
<!-- @mind:todo Implement private_key_scan_checker -->
<!-- @mind:todo Implement hierarchy_consistency_checker -->
<!-- @mind:todo Implement revocation_completeness_checker -->
<!-- @mind:proposition Add real-time encryption verification hook in graph-client.js write path (not just periodic sampling) -->
<!-- @mind:escalation Alerting target for CRITICAL private key detection — needs operational decision on paging mechanism -->

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
