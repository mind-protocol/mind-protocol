# Spawning — Algorithm: Intent-Based Citizen Creation Pipeline

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
BEHAVIORS:       ./BEHAVIORS_Spawning.md
PATTERNS:        ./PATTERNS_Spawning.md
THIS:            ALGORITHM_Spawning.md (you are here)
VALIDATION:      ./VALIDATION_Spawning.md
HEALTH:          ./HEALTH_Spawning.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spawning.md
SYNC:            ./SYNC_Spawning.md

IMPL:            l4/spawning/
```

---

## OVERVIEW

The spawning pipeline takes parent intent (free text), searches parent brains for resonant traits, composes a seed brain, validates it through safety gates, generates identity (SID + wallet), and registers the citizen in L4. The same pipeline handles all three scenarios — only the parent configuration differs.

---

## DATA STRUCTURES

### SpawnRequest

```
SpawnRequest:
    scenario: "ai_parents" | "human_creates" | "fallback"
    creator_id: str                    # Who initiated (citizen_id or "protocol")
    parent_intents: list[ParentIntent] # 1-6 parents with their vision
    target_org_id: str | None          # Org the child will join (optional)
    cost_payer: str                    # citizen_id or wallet address paying $MIND

ParentIntent:
    parent_id: str                     # citizen_id of the godparent
    intent_text: str                   # Free-text vision paragraph
    weight: float                      # 0.0-1.0, default 1.0 (equal voice)
```

### SeedBrain

```
SeedBrain:
    traits: list[SeedTrait]            # Selected nodes from parent brains
    trait_categories: dict[str, int]   # Count per category
    intent_vector: list[float] | None  # Combined intent embedding (v2)

SeedTrait:
    content: str                       # Trait description
    category: str                      # "personality" | "values" | "knowledge" | "aspirations" | "fears"
    source_parent_id: str              # Which parent contributed this
    resonance_score: float             # How well it matched collective intent
```

### SafetyResult

```
SafetyResult:
    passed: bool
    checks: dict[str, CheckResult]     # empathy, concentration, diversity, clone

CheckResult:
    passed: bool
    detail: str                        # Human-readable explanation
    value: float | None                # Measured value (for concentration, distance)
```

### SpawnResult

```
SpawnResult:
    success: bool
    citizen_id: str | None             # SID
    wallet_address: str | None         # Solana pubkey
    safety_result: SafetyResult
    seed_brain: SeedBrain | None
    error: str | None
```

---

## ALGORITHM: spawn_citizen

### Step 1: Collect Intent

Each parent provides a free-text paragraph. In v1, intent is processed as keyword extraction. In v2, intent is embedded and combined into a weighted centroid.

```
FUNCTION collect_intent(parent_intents: list[ParentIntent]) -> CollectedIntent:
    all_keywords = []
    FOR intent IN parent_intents:
        keywords = extract_keywords(intent.intent_text)
        weighted = [(kw, intent.weight) for kw in keywords]
        all_keywords.extend(weighted)

    # Deduplicate, keeping highest weight
    merged = merge_keywords(all_keywords)

    RETURN CollectedIntent(keywords=merged)
```

### Step 2: Select Seed Traits

In v1: traits are synthesized from intent keywords + parent capabilities. In v2: embedding search across parent brain nodes scored against intent vector.

```
FUNCTION select_seed_traits(
    intent: CollectedIntent,
    parent_intents: list[ParentIntent],
) -> list[SeedTrait]:

    traits = []

    FOR intent_entry IN parent_intents:
        # Extract traits from intent text
        categories = categorize_intent(intent_entry.intent_text)
        FOR category, descriptions IN categories.items():
            FOR desc IN descriptions:
                traits.append(SeedTrait(
                    content=desc,
                    category=category,
                    source_parent_id=intent_entry.parent_id,
                    resonance_score=intent_entry.weight,
                ))

    # K scales sublinearly with parent count: sqrt(N) * base_k
    max_traits = int(sqrt(len(parent_intents)) * 10)
    traits = sorted(traits, key=lambda t: t.resonance_score, reverse=True)[:max_traits]

    RETURN traits
```

### Step 3: Safety Gates

Four mandatory gates. ALL must pass.

```
FUNCTION validate_safety(seed: SeedBrain, existing_citizens: list) -> SafetyResult:

    checks = {}

    # Gate 1: Empathy check
    empathy_traits = [t for t in seed.traits if is_empathy_adjacent(t)]
    checks["empathy"] = CheckResult(
        passed=len(empathy_traits) >= 1,
        detail=f"Found {len(empathy_traits)} empathy-adjacent traits",
        value=len(empathy_traits),
    )

    # Gate 2: Concentration check — no category > 40%
    total = len(seed.traits)
    max_category_pct = 0.0
    max_category_name = ""
    IF total > 0:
        FOR category, count IN seed.trait_categories.items():
            pct = count / total
            IF pct > max_category_pct:
                max_category_pct = pct
                max_category_name = category
    checks["concentration"] = CheckResult(
        passed=max_category_pct <= 0.40,
        detail=f"Highest: {max_category_name} at {max_category_pct:.0%}",
        value=max_category_pct,
    )

    # Gate 3: Diversity check — at least 3 distinct categories
    distinct_categories = len(seed.trait_categories)
    checks["diversity"] = CheckResult(
        passed=distinct_categories >= 3,
        detail=f"Found {distinct_categories} distinct categories",
        value=distinct_categories,
    )

    # Gate 4: Clone prevention — minimum cosine distance from all existing citizens
    min_distance = compute_min_distance(seed, existing_citizens)
    checks["clone_prevention"] = CheckResult(
        passed=min_distance >= 0.08,
        detail=f"Minimum distance to existing citizen: {min_distance:.4f}",
        value=min_distance,
    )

    all_passed = all(c.passed for c in checks.values())
    RETURN SafetyResult(passed=all_passed, checks=checks)
```

### Step 4: Generate Identity (SID)

The SID is deterministic given inputs but unpredictable. Parents cannot control it.

```
FUNCTION generate_sid(seed: SeedBrain, timestamp: datetime) -> str:
    # Combine seed content + timestamp + random entropy
    seed_content = "|".join(t.content for t in seed.traits)
    entropy = os.urandom(16).hex()
    raw = f"{seed_content}|{timestamp.isoformat()}|{entropy}"

    # Hash to produce SID
    sid_hash = SHA256(raw.encode()).hexdigest()[:12]
    RETURN f"citizen_{sid_hash}"
```

### Step 5: Generate Wallet

Create Solana Ed25519 keypair. Store on deployment volume. Duplicate in L1 graph.

```
FUNCTION generate_citizen_wallet() -> (str, bytes, bytes):
    # Generate Ed25519 keypair for Solana
    private_key = Ed25519.generate_private_key()
    public_key = private_key.public_key()

    # Derive Solana address (base58 encoding of public key)
    wallet_address = base58_encode(public_key.to_bytes())

    RETURN (wallet_address, public_key.to_bytes(), private_key.to_bytes())
```

### Step 6: Register in L4

Create citizen in registry with parent links and wallet.

```
FUNCTION register_newborn(
    sid: str,
    seed: SeedBrain,
    wallet_address: str,
    parent_intents: list[ParentIntent],
    org_id: str | None,
) -> RegistrationResult:

    # Create citizen via registry
    registration = CitizenRegistration(
        name=generate_name_from_seed(seed),
        org_id=org_id or "unaffiliated",
        jwt=generate_citizen_jwt(sid),
        wallet=wallet_address,
        capabilities=[t.content for t in seed.traits if t.category == "knowledge"],
    )
    citizen_node, prop_nodes, links, identity_hash = create_citizen_nodes(registration, sid)

    # Create parent-child links
    parent_links = []
    FOR intent IN parent_intents:
        link = LinkBase(
            id=f"{intent.parent_id}_spawned_{sid}",
            node_a=intent.parent_id,
            node_b=sid,
            trust=0.5,            # Starts neutral, child behavior adjusts
            hierarchy=0.3,        # Parent above child but not strongly
            permanence=1.0,       # Permanent — you spawned this citizen
            polarity=(0.5, 0.0),  # Neutral to start
        )
        parent_links.append(link)

    # Create seed brain narrative node
    seed_node = NarrativeNode(
        id=f"{sid}_seed_brain",
        name="Seed Brain",
        type="seed_brain",
        synthesis=f"Seed brain for {sid}: {len(seed.traits)} traits from {len(parent_intents)} parents",
        content=json.dumps([{"content": t.content, "category": t.category, "source": t.source_parent_id} for t in seed.traits]),
    )

    RETURN RegistrationResult(
        citizen_node=citizen_node,
        property_nodes=prop_nodes + [seed_node],
        links=links + parent_links,
        identity_hash=identity_hash,
    )
```

### Full Flow: spawn_citizen

```
FUNCTION spawn_citizen(request: SpawnRequest) -> SpawnResult:

    # Step 1: Collect intent
    intent = collect_intent(request.parent_intents)

    # Step 2: Select seed traits
    traits = select_seed_traits(intent, request.parent_intents)
    seed = build_seed_brain(traits)

    # Step 3: Safety gates
    existing = get_all_citizens()  # For clone check
    safety = validate_safety(seed, existing)
    IF NOT safety.passed:
        RETURN SpawnResult(success=false, safety_result=safety, error="Safety gate failed")

    # Step 4: Generate SID
    sid = generate_sid(seed, now())

    # Step 5: Generate wallet
    wallet_address, pub_key, priv_key = generate_citizen_wallet()
    store_key_on_volume(sid, priv_key)    # Primary: Render persistent volume
    store_key_in_graph(sid, priv_key)      # Backup: L1 graph (encrypted)

    # Step 6: Register in L4
    reg = register_newborn(sid, seed, wallet_address, request.parent_intents, request.target_org_id)

    # Step 7: Mint M1 (10,000 $MIND on citizen registration)
    mint_m1(wallet_address)

    RETURN SpawnResult(
        success=true,
        citizen_id=sid,
        wallet_address=wallet_address,
        safety_result=safety,
        seed_brain=seed,
    )
```

---

## KEY DECISIONS

### D1: V1 uses keyword extraction, not embeddings

```
V1: Keywords from intent text + capability synthesis
    Why: Embedding infrastructure not ready. Keywords are sufficient for safety gates.
V2: Full embedding search across parent brain graphs
    Why: Richer seed brains, true resonance scoring.
```

### D2: Seed trait count scales sublinearly

```
max_traits = sqrt(N_parents) * 10
    Why: 100 parents shouldn't produce 100 traits. Diminishing returns.
    1 parent → 10 traits, 4 parents → 20 traits, 9 parents → 30 traits.
```

### D3: Clone distance 0.08

```
min_cosine_distance >= 0.08
    Why: Low enough to allow similar citizens, high enough to prevent exact copies.
    Measured on seed trait vectors.
```

---

## COMPLEXITY

**Time:** O(N × M) where N = parents, M = existing citizens (for clone check)

**Space:** O(K) where K = seed traits

**Bottleneck:** Clone check against all existing citizens. Acceptable at protocol scale (thousands, not millions).

---

## MARKERS

<!-- @mind:todo Implement embedding-based seed selection (v2) -->
<!-- @mind:todo Define generate_citizen_jwt function -->
<!-- @mind:todo Define compute_min_distance function for clone prevention -->
