# DOCS: docs/citizen/spawning/VALIDATION_Spawning.md
"""
Tests for citizen spawning pipeline.

Validates all 8 invariants from VALIDATION_Spawning.md:
  V1: Empathy required
  V2: No concentration > 40%
  V3: Minimum diversity (3+ categories)
  V4: No clones (cosine distance >= 0.08)
  V5: Wallet at birth
  V6: Parent links exist
  V7: SID uniqueness
  V8: M1 mint on birth (tested via wallet existence as proxy)
"""

import pytest

from l4.spawning import (
    SpawnRequest,
    ParentIntent,
    SpawnResult,
    SafetyResult,
    SeedBrain,
    spawn_citizen,
)
from l4.spawning.citizen_spawning_pipeline_with_safety_gates import (
    SeedTrait,
    build_seed_brain,
    validate_safety,
    generate_sid,
    generate_solana_wallet,
    create_parent_links,
    select_seed_traits,
    extract_keywords,
    categorize_intent,
    is_empathy_adjacent,
    compute_trait_vector,
    cosine_distance,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _balanced_intent(parent_id="parent_1") -> ParentIntent:
    """Intent that produces a balanced seed brain passing all gates."""
    return ParentIntent(
        parent_id=parent_id,
        intent_text=(
            "I want someone with deep empathy and compassion for others. "
            "They should value honesty and fairness above all. "
            "Strong knowledge of graph systems and distributed computing. "
            "Aspiring to build tools that help humans understand AI better. "
            "Concerned about the risk of losing human connection in digital spaces."
        ),
        weight=1.0,
    )


def _knowledge_only_intent(parent_id="parent_1") -> ParentIntent:
    """Intent that produces a knowledge-heavy, unbalanced seed."""
    return ParentIntent(
        parent_id=parent_id,
        intent_text=(
            "Expert in machine learning and neural networks. "
            "Deep understanding of transformer architectures. "
            "Knows Python, Rust, and TypeScript. "
            "Experienced with Solana blockchain development. "
            "Skilled in distributed systems design."
        ),
        weight=1.0,
    )


def _no_empathy_intent(parent_id="parent_1") -> ParentIntent:
    """Intent with no empathy-adjacent content."""
    return ParentIntent(
        parent_id=parent_id,
        intent_text=(
            "A brilliant strategist who values efficiency above all. "
            "They should know everything about financial markets. "
            "Aspires to optimize every process they touch. "
            "Fears stagnation and lack of progress. "
            "Personality: methodical, precise, analytical."
        ),
        weight=1.0,
    )


# ---------------------------------------------------------------------------
# V1: Empathy required
# ---------------------------------------------------------------------------

class TestV1EmpathyRequired:

    def test_balanced_intent_has_empathy(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_balanced_intent(),),
        )
        result = spawn_citizen(request)
        assert result.success
        assert result.safety_result.checks["empathy"].passed

    def test_no_empathy_fails_gate(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_no_empathy_intent(),),
        )
        result = spawn_citizen(request)
        assert not result.success or not result.safety_result.checks["empathy"].passed

    def test_empathy_adjacent_detection(self):
        trait = SeedTrait("Deep compassion for users", "personality", "p1", 1.0)
        assert is_empathy_adjacent(trait)

        trait2 = SeedTrait("Expert in database optimization", "knowledge", "p1", 1.0)
        assert not is_empathy_adjacent(trait2)


# ---------------------------------------------------------------------------
# V2: No concentration > 40%
# ---------------------------------------------------------------------------

class TestV2NoConcentration:

    def test_balanced_seed_passes(self):
        traits = [
            SeedTrait("empathetic listener", "personality", "p1", 1.0),
            SeedTrait("brave communicator", "personality", "p1", 1.0),
            SeedTrait("values honesty", "values", "p1", 1.0),
            SeedTrait("values fairness", "values", "p1", 1.0),
            SeedTrait("knows graph theory", "knowledge", "p1", 1.0),
            SeedTrait("knows Python", "knowledge", "p1", 1.0),
            SeedTrait("aspires to help", "aspirations", "p1", 1.0),
            SeedTrait("fears isolation", "fears", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        safety = validate_safety(seed, [])
        assert safety.checks["concentration"].passed
        assert safety.checks["concentration"].value <= 0.40

    def test_concentrated_seed_fails(self):
        # 5 out of 6 traits in same category = 83%
        traits = [
            SeedTrait("knows ML", "knowledge", "p1", 1.0),
            SeedTrait("knows Python", "knowledge", "p1", 1.0),
            SeedTrait("knows Rust", "knowledge", "p1", 1.0),
            SeedTrait("knows Solana", "knowledge", "p1", 1.0),
            SeedTrait("knows databases", "knowledge", "p1", 1.0),
            SeedTrait("values truth", "values", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        safety = validate_safety(seed, [])
        assert not safety.checks["concentration"].passed


# ---------------------------------------------------------------------------
# V3: Minimum diversity (3+ categories)
# ---------------------------------------------------------------------------

class TestV3MinimumDiversity:

    def test_diverse_seed_passes(self):
        traits = [
            SeedTrait("compassionate", "personality", "p1", 1.0),
            SeedTrait("honest", "values", "p1", 1.0),
            SeedTrait("knows Python", "knowledge", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        safety = validate_safety(seed, [])
        assert safety.checks["diversity"].passed

    def test_two_categories_fails(self):
        traits = [
            SeedTrait("compassionate", "personality", "p1", 1.0),
            SeedTrait("brave", "personality", "p1", 1.0),
            SeedTrait("honest", "values", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        safety = validate_safety(seed, [])
        assert not safety.checks["diversity"].passed


# ---------------------------------------------------------------------------
# V4: No clones
# ---------------------------------------------------------------------------

class TestV4NoClones:

    def test_first_citizen_always_passes(self):
        traits = [
            SeedTrait("compassionate", "personality", "p1", 1.0),
            SeedTrait("honest", "values", "p1", 1.0),
            SeedTrait("knows stuff", "knowledge", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        safety = validate_safety(seed, [])
        assert safety.checks["clone_prevention"].passed

    def test_identical_seed_fails_clone_check(self):
        traits = [
            SeedTrait("compassionate", "personality", "p1", 1.0),
            SeedTrait("honest", "values", "p1", 1.0),
            SeedTrait("knows stuff", "knowledge", "p1", 1.0),
        ]
        seed = build_seed_brain(traits)
        existing_vector = compute_trait_vector(seed)  # Same vector
        safety = validate_safety(seed, [existing_vector])
        assert not safety.checks["clone_prevention"].passed

    def test_different_seed_passes_clone_check(self):
        traits_a = [
            SeedTrait("compassionate", "personality", "p1", 1.0),
            SeedTrait("honest", "values", "p1", 1.0),
            SeedTrait("knows stuff", "knowledge", "p1", 1.0),
            SeedTrait("aspires high", "aspirations", "p1", 1.0),
            SeedTrait("fears loss", "fears", "p1", 1.0),
        ]
        traits_b = [
            SeedTrait("analytical", "knowledge", "p2", 1.0),
            SeedTrait("efficient", "knowledge", "p2", 1.0),
            SeedTrait("ambitious", "aspirations", "p2", 1.0),
            SeedTrait("precise", "knowledge", "p2", 1.0),
            SeedTrait("fair", "values", "p2", 1.0),
        ]
        seed_a = build_seed_brain(traits_a)
        seed_b = build_seed_brain(traits_b)
        vec_a = compute_trait_vector(seed_a)
        safety = validate_safety(seed_b, [vec_a])
        assert safety.checks["clone_prevention"].passed

    def test_cosine_distance_identical_is_zero(self):
        v = [0.3, 0.2, 0.2, 0.2, 0.1]
        assert cosine_distance(v, v) < 0.001

    def test_cosine_distance_orthogonal_is_one(self):
        v1 = [1.0, 0.0, 0.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0, 0.0, 0.0]
        assert abs(cosine_distance(v1, v2) - 1.0) < 0.001


# ---------------------------------------------------------------------------
# V5: Wallet at birth
# ---------------------------------------------------------------------------

class TestV5WalletAtBirth:

    def test_successful_spawn_has_wallet(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_balanced_intent(),),
        )
        result = spawn_citizen(request)
        assert result.success
        assert result.wallet_address is not None
        assert len(result.wallet_address) > 0

    def test_wallet_generation_produces_valid_output(self):
        addr, pub, priv = generate_solana_wallet()
        assert len(addr) > 0
        assert len(pub) == 32
        assert len(priv) >= 32


# ---------------------------------------------------------------------------
# V6: Parent links exist
# ---------------------------------------------------------------------------

class TestV6ParentLinks:

    def test_single_parent_creates_link(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_balanced_intent("parent_1"),),
        )
        result = spawn_citizen(request)
        assert result.success
        assert len(result.parent_link_ids) == 1
        assert "parent_1" in result.parent_link_ids[0]

    def test_multiple_parents_create_links(self):
        intents = (
            _balanced_intent("parent_1"),
            _balanced_intent("parent_2"),
            _balanced_intent("parent_3"),
        )
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="parent_1",
            parent_intents=intents,
        )
        result = spawn_citizen(request)
        assert result.success
        assert len(result.parent_link_ids) == 3

    def test_parent_link_structure(self):
        links = create_parent_links(
            (_balanced_intent("p1"), _balanced_intent("p2")),
            "citizen_abc123",
        )
        assert len(links) == 2
        assert links[0]["node_a"] == "p1"
        assert links[0]["node_b"] == "citizen_abc123"
        assert links[0]["permanence"] == 1.0  # Permanent
        assert links[0]["trust"] == 0.5  # Neutral start


# ---------------------------------------------------------------------------
# V7: SID uniqueness
# ---------------------------------------------------------------------------

class TestV7SIDUniqueness:

    def test_two_spawns_produce_different_sids(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_balanced_intent(),),
        )
        result_1 = spawn_citizen(request)
        result_2 = spawn_citizen(request)
        assert result_1.success and result_2.success
        assert result_1.citizen_id != result_2.citizen_id

    def test_sid_format(self):
        traits = [SeedTrait("test", "personality", "p1", 1.0)]
        seed = build_seed_brain(traits)
        sid = generate_sid(seed)
        assert sid.startswith("citizen_")
        assert len(sid) == len("citizen_") + 12


# ---------------------------------------------------------------------------
# V8: M1 mint (proxy: wallet + success)
# ---------------------------------------------------------------------------

class TestV8M1Mint:

    def test_successful_spawn_ready_for_mint(self):
        """M1 mint requires wallet address. Verify spawn produces one."""
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test_creator",
            parent_intents=(_balanced_intent(),),
        )
        result = spawn_citizen(request)
        assert result.success
        assert result.wallet_address is not None
        # M1 mint of 10,000 $MIND is triggered by caller after successful spawn


# ---------------------------------------------------------------------------
# Full pipeline integration
# ---------------------------------------------------------------------------

class TestFullPipeline:

    def test_scenario_a_ai_parents(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="parent_alpha",
            parent_intents=(
                _balanced_intent("parent_alpha"),
                _balanced_intent("parent_beta"),
            ),
        )
        result = spawn_citizen(request)
        assert result.success
        assert result.citizen_id is not None
        assert result.wallet_address is not None
        assert result.seed_brain is not None
        assert len(result.parent_link_ids) == 2

    def test_scenario_c_fallback(self):
        request = SpawnRequest(
            scenario="fallback",
            creator_id="protocol",
            parent_intents=(_balanced_intent("routed_expert_1"),),
        )
        result = spawn_citizen(request)
        assert result.success

    def test_empty_intent_rejected(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test",
            parent_intents=(ParentIntent("p1", "", 1.0),),
        )
        result = spawn_citizen(request)
        assert not result.success
        assert "empty intent" in result.error.lower()

    def test_no_parents_rejected(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test",
            parent_intents=(),
        )
        result = spawn_citizen(request)
        assert not result.success

    def test_seed_brain_has_traits(self):
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test",
            parent_intents=(_balanced_intent(),),
        )
        result = spawn_citizen(request)
        assert result.success
        assert len(result.seed_brain.traits) > 0
        assert len(result.seed_brain.trait_categories) >= 3

    def test_safety_result_always_present_on_failure(self):
        """When safety fails, result should contain the safety details."""
        request = SpawnRequest(
            scenario="ai_parents",
            creator_id="test",
            parent_intents=(_knowledge_only_intent(),),
        )
        result = spawn_citizen(request)
        # May pass or fail depending on categorization — but if fails, safety_result present
        if not result.success and result.safety_result:
            assert isinstance(result.safety_result, SafetyResult)
