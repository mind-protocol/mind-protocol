# ALGORITHM: L4 Laws

```
STATUS: DESIGNING
PURPOSE: How law enforcement works at protocol boundaries
```

---

## Law Enforcement Points

Laws are enforced at:
1. **Membrane** — Cross-org stimulus routing
2. **Registry** — Identity verification
3. **Graph** — Schema compliance (via Pydantic)
4. **API** — WebSocket enforcement

---

## Cross-org Stimulus Flow

```
PROCEDURE process_cross_org_stimulus(stimulus):
    # L5: Hash-based identity
    1. Extract hash from stimulus
       - If raw JWT detected → REJECT "Token exposure forbidden"

    2. Verify hash against registry
       - expected = SHA256(citizen.jwt × stimulus.node_id)
       - If hash != expected → REJECT "Invalid identity"

    # L2: Register to exist
    3. Lookup sender in registry
       - If not found → REJECT "Unknown sender"

    4. Lookup target org in registry
       - If not found → REJECT "Unknown target"

    # L1: Respect schema
    5. Validate stimulus payload against schema
       - If invalid → REJECT with validation errors

    # L7: Membrane fees
    6. Calculate fee
       - fee = stimulus.value * fee_rate  # 1-5%
       - If sender.balance < fee → REJECT "Insufficient funds"

    7. Deduct fee
       - sender.balance -= fee
       - protocol.balance += fee

    # L4: Cross-org via membrane
    8. Route through membrane
       - Get target endpoint from registry
       - Forward stimulus to target

    # L6: Receiver validates
    9. Target org receives stimulus
       - Target applies own acceptance logic
       - Target filters response by trust mode

    10. RETURN response (or acknowledgment)
```

---

## Hash Verification

```
PROCEDURE verify_stimulus_identity(stimulus):
    1. Extract claimed identity
       - sender_id = stimulus.sender_id
       - hash = stimulus.identity_hash

    2. Lookup in registry
       - citizen = registry.get_citizen(sender_id)
       - If not found → RETURN {valid: false}

    3. Compute expected hash
       - expected = SHA256(citizen.jwt × stimulus.node_id)

    4. Compare
       - If hash == expected → RETURN {valid: true, citizen: citizen}
       - Else → RETURN {valid: false, reason: "Hash mismatch"}
```

---

## Fee Calculation

```
PROCEDURE calculate_membrane_fee(stimulus):
    1. Determine fee rate
       - base_rate = 0.01  # 1%
       - load_factor = get_current_load()  # 0.0 - 1.0
       - trust_factor = get_trust_level(sender, target)  # 0.0 - 1.0

    2. Calculate final rate
       - rate = base_rate + (0.04 * load_factor) - (0.02 * trust_factor)
       - rate = clamp(rate, 0.01, 0.05)  # 1-5%

    3. RETURN stimulus.value * rate
```

---

## Receiver Validation

```
PROCEDURE receiver_validate(stimulus, receiver_config):
    1. Check acceptance rules
       - If sender in receiver.blocklist → REJECT
       - If sender not in receiver.allowlist AND mode == "trust" → REJECT

    2. Apply trust mode filter
       - mode = receiver_config.trust_mode_for(sender)
       - If mode == "public" → filter to public fields only
       - If mode == "sanitized" → filter sensitive content
       - If mode == "trust" → full response

    3. Process stimulus
       - Apply to local graph
       - Generate response

    4. RETURN filtered response
```

---

## WebSocket Enforcement

```
PROCEDURE handle_connection(request):
    1. Check protocol
       - If request.protocol != "websocket" → RETURN 404

    2. Upgrade connection
       - Establish WebSocket

    3. Authenticate
       - Receive auth message with hash
       - Verify via registry

    4. Begin push session
       - Subscribe to relevant events
       - Push on change
```

---

## Related

- `VALIDATION_Laws.md` — What must be true
- `IMPLEMENTATION_Laws.md` — Where code lives
- `docs/membrane/ALGORITHM_Membrane_System.md` — Membrane routing details
