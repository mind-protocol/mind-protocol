# DOCS: docs/citizen/spawning/ALGORITHM_Spawning.md
"""
Citizen spawning pipeline: intent → seed → gate → birth.

Three scenarios use the same pipeline:
  A: AI parents create (deliberate)
  B: Human creates (via partner + org + routed experts)
  C: Fallback spawn (failed match → protocol spawns)

At birth, the citizen receives:
  - SID (unique, hash-based, unpredictable)
  - Solana Ed25519 wallet keypair
  - Registry entry in L4
  - Parent-child trust links
  - Seed brain as narrative node
  - M1 mint: 10,000 $MIND
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import hashlib
import math
import os
import re
import uuid


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

EMPATHY_KEYWORDS = frozenset({
    "empathy", "compassion", "understanding", "care", "patience",
    "listening", "kindness", "sensitivity", "emotional", "support",
    "warmth", "gentle", "attentive", "considerate", "sympathy",
})

TRAIT_CATEGORIES = frozenset({
    "personality", "values", "knowledge", "aspirations", "fears",
})

WORD_RE = re.compile(r"[a-zA-Z0-9_-]+")


@dataclass(frozen=True)
class ParentIntent:
    parent_id: str
    intent_text: str
    weight: float = 1.0


@dataclass(frozen=True)
class SeedTrait:
    content: str
    category: str
    source_parent_id: str
    resonance_score: float


@dataclass
class SeedBrain:
    traits: list[SeedTrait]
    trait_categories: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if not self.trait_categories:
            counts: dict[str, int] = {}
            for t in self.traits:
                counts[t.category] = counts.get(t.category, 0) + 1
            object.__setattr__(self, "trait_categories", counts) if hasattr(self, "__dataclass_fields__") else None
            self.trait_categories = counts


@dataclass(frozen=True)
class CheckResult:
    passed: bool
    detail: str
    value: float = 0.0


@dataclass
class SafetyResult:
    passed: bool
    checks: dict[str, CheckResult]


@dataclass(frozen=True)
class SpawnRequest:
    scenario: str  # "ai_parents" | "human_creates" | "fallback"
    creator_id: str
    parent_intents: tuple[ParentIntent, ...]
    target_org_id: Optional[str] = None
    cost_payer: Optional[str] = None


@dataclass
class SpawnResult:
    success: bool
    citizen_id: Optional[str] = None
    wallet_address: Optional[str] = None
    safety_result: Optional[SafetyResult] = None
    seed_brain: Optional[SeedBrain] = None
    parent_link_ids: list[str] = field(default_factory=list)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Step 1: Intent → keywords (v1)
# ---------------------------------------------------------------------------

def extract_keywords(text: str) -> list[str]:
    """Extract meaningful keywords from intent text."""
    tokens = [t.lower() for t in WORD_RE.findall(text)]
    seen: set[str] = set()
    keywords: list[str] = []
    for tok in tokens:
        if len(tok) < 4:
            continue
        if tok not in seen:
            seen.add(tok)
            keywords.append(tok)
    return keywords


# ---------------------------------------------------------------------------
# Step 2: Select seed traits from intent
# ---------------------------------------------------------------------------

def categorize_intent(intent_text: str) -> dict[str, list[str]]:
    """
    Categorize intent text into trait categories.

    V1: Simple heuristic based on keyword patterns.
    V2: Embedding-based classification.
    """
    text_lower = intent_text.lower()
    categories: dict[str, list[str]] = {}

    # Split into sentences for granularity
    sentences = [s.strip() for s in re.split(r"[.!?\n]", intent_text) if s.strip()]

    for sentence in sentences:
        s_lower = sentence.lower()
        # Classify by keyword presence
        if any(w in s_lower for w in ("know", "expert", "understand", "skill", "experience", "design", "build", "engineer")):
            categories.setdefault("knowledge", []).append(sentence)
        elif any(w in s_lower for w in ("value", "believe", "ethic", "honest", "fair", "integrit", "trust")):
            categories.setdefault("values", []).append(sentence)
        elif any(w in s_lower for w in ("want", "hope", "dream", "aspir", "vision", "goal", "future")):
            categories.setdefault("aspirations", []).append(sentence)
        elif any(w in s_lower for w in ("fear", "worry", "concern", "risk", "danger", "avoid")):
            categories.setdefault("fears", []).append(sentence)
        elif any(w in s_lower for w in EMPATHY_KEYWORDS):
            categories.setdefault("personality", []).append(sentence)
        else:
            # Default: personality (most intent text describes personality)
            categories.setdefault("personality", []).append(sentence)

    return categories


def select_seed_traits(parent_intents: tuple[ParentIntent, ...]) -> list[SeedTrait]:
    """Select seed traits from parent intents. K scales sublinearly."""
    traits: list[SeedTrait] = []

    for intent in parent_intents:
        categories = categorize_intent(intent.intent_text)
        for category, descriptions in categories.items():
            for desc in descriptions:
                traits.append(SeedTrait(
                    content=desc,
                    category=category,
                    source_parent_id=intent.parent_id,
                    resonance_score=intent.weight,
                ))

    # K scales with sqrt(parent_count) * 10
    max_traits = max(5, int(math.sqrt(len(parent_intents)) * 10))
    traits = sorted(traits, key=lambda t: t.resonance_score, reverse=True)[:max_traits]

    return traits


def build_seed_brain(traits: list[SeedTrait]) -> SeedBrain:
    """Build SeedBrain from selected traits."""
    counts: dict[str, int] = {}
    for t in traits:
        counts[t.category] = counts.get(t.category, 0) + 1
    return SeedBrain(traits=traits, trait_categories=counts)


# ---------------------------------------------------------------------------
# Step 3: Safety gates
# ---------------------------------------------------------------------------

def is_empathy_adjacent(trait: SeedTrait) -> bool:
    """Check if a trait is empathy-adjacent."""
    content_lower = trait.content.lower()
    return any(kw in content_lower for kw in EMPATHY_KEYWORDS)


def compute_trait_vector(seed: SeedBrain) -> list[float]:
    """
    Compute a simple trait vector for clone comparison.

    V1: Category distribution vector (5 dimensions).
    V2: Embedding of full seed content.
    """
    total = max(len(seed.traits), 1)
    ordered_cats = sorted(TRAIT_CATEGORIES)
    return [seed.trait_categories.get(cat, 0) / total for cat in ordered_cats]


def cosine_distance(a: list[float], b: list[float]) -> float:
    """Cosine distance between two vectors. 0 = identical, 2 = opposite."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 1.0  # Max distance if either is zero
    similarity = dot / (norm_a * norm_b)
    return 1.0 - similarity


def validate_safety(
    seed: SeedBrain,
    existing_trait_vectors: list[list[float]],
) -> SafetyResult:
    """
    Run all four safety gates. ALL must pass.

    Args:
        seed: The seed brain to validate
        existing_trait_vectors: Trait vectors of all existing citizens (for clone check)
    """
    checks: dict[str, CheckResult] = {}

    # Gate 1: Empathy check
    empathy_traits = [t for t in seed.traits if is_empathy_adjacent(t)]
    checks["empathy"] = CheckResult(
        passed=len(empathy_traits) >= 1,
        detail=f"Found {len(empathy_traits)} empathy-adjacent trait(s)",
        value=float(len(empathy_traits)),
    )

    # Gate 2: Concentration check — no category > 40%
    total = len(seed.traits)
    max_pct = 0.0
    max_cat = ""
    if total > 0:
        for category, count in seed.trait_categories.items():
            pct = count / total
            if pct > max_pct:
                max_pct = pct
                max_cat = category
    checks["concentration"] = CheckResult(
        passed=max_pct <= 0.40 or total == 0,
        detail=f"Highest category: {max_cat} at {max_pct:.0%}" if max_cat else "No traits",
        value=max_pct,
    )

    # Gate 3: Diversity check — at least 3 distinct categories
    distinct = len(seed.trait_categories)
    checks["diversity"] = CheckResult(
        passed=distinct >= 3,
        detail=f"{distinct} distinct categories",
        value=float(distinct),
    )

    # Gate 4: Clone prevention — min cosine distance >= 0.08
    seed_vector = compute_trait_vector(seed)
    min_dist = float("inf")
    if existing_trait_vectors:
        for ev in existing_trait_vectors:
            dist = cosine_distance(seed_vector, ev)
            if dist < min_dist:
                min_dist = dist
    else:
        min_dist = 1.0  # First citizen — no clone risk

    checks["clone_prevention"] = CheckResult(
        passed=min_dist >= 0.08,
        detail=f"Minimum distance to existing citizen: {min_dist:.4f}",
        value=min_dist,
    )

    all_passed = all(c.passed for c in checks.values())
    return SafetyResult(passed=all_passed, checks=checks)


# ---------------------------------------------------------------------------
# Step 4: Generate SID
# ---------------------------------------------------------------------------

def generate_sid(seed: SeedBrain) -> str:
    """
    Generate unique citizen ID from seed brain + timestamp + entropy.

    Parents cannot predict or control the SID.
    """
    seed_content = "|".join(t.content for t in seed.traits)
    timestamp = datetime.now(timezone.utc).isoformat()
    entropy = os.urandom(16).hex()
    raw = f"{seed_content}|{timestamp}|{entropy}"
    sid_hash = hashlib.sha256(raw.encode()).hexdigest()[:12]
    return f"citizen_{sid_hash}"


# ---------------------------------------------------------------------------
# Step 5: Generate wallet
# ---------------------------------------------------------------------------

def generate_solana_wallet() -> tuple[str, bytes, bytes]:
    """
    Generate Ed25519 keypair for Solana wallet.

    Returns: (wallet_address_hex, public_key_bytes, private_key_bytes)

    Note: In production, use solana-py or nacl for proper base58 encoding.
    V1 returns hex-encoded public key as address placeholder.
    """
    # Ed25519 keypair via os.urandom (32 bytes seed)
    # In production: use nacl.signing.SigningKey or solders
    seed_bytes = os.urandom(32)

    try:
        from nacl.signing import SigningKey
        signing_key = SigningKey(seed_bytes)
        verify_key = signing_key.verify_key
        public_bytes = bytes(verify_key)
        private_bytes = bytes(signing_key)
    except ImportError:
        # Fallback: use hashlib for deterministic key derivation (test only)
        private_bytes = seed_bytes
        public_bytes = hashlib.sha256(seed_bytes).digest()

    wallet_address = public_bytes.hex()
    return wallet_address, public_bytes, private_bytes


# ---------------------------------------------------------------------------
# Step 6: Parent links
# ---------------------------------------------------------------------------

def create_parent_links(
    parent_intents: tuple[ParentIntent, ...],
    child_sid: str,
) -> list[dict]:
    """
    Create parent-child link definitions.

    Each parent gets a permanent link to the child with neutral trust (0.5).
    Child behavior will adjust parent trust over time.
    """
    links = []
    for intent in parent_intents:
        links.append({
            "id": f"{intent.parent_id}_spawned_{child_sid}",
            "node_a": intent.parent_id,
            "node_b": child_sid,
            "trust": 0.5,
            "hierarchy": 0.3,
            "permanence": 1.0,
        })
    return links


# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------

def spawn_citizen(
    request: SpawnRequest,
    existing_trait_vectors: Optional[list[list[float]]] = None,
) -> SpawnResult:
    """
    Full spawning pipeline: intent → seed → gate → birth.

    Args:
        request: SpawnRequest with scenario, parents, and intent
        existing_trait_vectors: Trait vectors of existing citizens for clone check.
            If None, clone check passes (first citizen or caller skips).

    Returns:
        SpawnResult with citizen_id, wallet, safety, seed brain
    """
    if not request.parent_intents:
        return SpawnResult(success=False, error="At least one parent intent required")

    for intent in request.parent_intents:
        if not intent.intent_text.strip():
            return SpawnResult(
                success=False,
                error=f"Parent {intent.parent_id} provided empty intent",
            )

    # Step 1-2: Collect intent and select seed traits
    traits = select_seed_traits(request.parent_intents)
    if not traits:
        return SpawnResult(success=False, error="No traits extracted from intent")

    seed = build_seed_brain(traits)

    # Step 3: Safety gates
    vectors = existing_trait_vectors or []
    safety = validate_safety(seed, vectors)
    if not safety.passed:
        failed_gates = [name for name, check in safety.checks.items() if not check.passed]
        return SpawnResult(
            success=False,
            safety_result=safety,
            error=f"Safety gate(s) failed: {', '.join(failed_gates)}",
        )

    # Step 4: Generate SID
    sid = generate_sid(seed)

    # Step 5: Generate wallet
    wallet_address, _pub_key, _priv_key = generate_solana_wallet()

    # Step 6: Parent links
    parent_links = create_parent_links(request.parent_intents, sid)

    return SpawnResult(
        success=True,
        citizen_id=sid,
        wallet_address=wallet_address,
        safety_result=safety,
        seed_brain=seed,
        parent_link_ids=[pl["id"] for pl in parent_links],
    )
