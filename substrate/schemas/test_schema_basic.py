"""
Basic schema validation test - proves consciousness_schema.py is working.

This is NOT the full test_insertion.py (Phase 1 acceptance test).
This is a quick smoke test to verify the schema loads and validates correctly.

Run: python substrate/schemas/test_schema_basic.py
"""

from consciousness_schema import (
    Decision, Memory, JUSTIFIES, REQUIRES, ENABLES,
    FormationTrigger, ValidationStatus
)
from datetime import datetime


def test_valid_decision():
    """Create a valid Decision node"""
    print("\n1. Testing Decision node creation...")

    decision = Decision(
        name="decision_v2_architecture",
        description="Chose FalkorDB + LlamaIndex + Native Vectors for V2",
        formation_trigger=FormationTrigger.COLLECTIVE_DELIBERATION,
        confidence=0.95,
        decided_by="Luca + Ada + Felix",
        decision_date="2025-10-16",
        rationale="Solves multi-tenancy, complexity, and scale",
        alternatives_considered=["Neo4j + LangChain", "NebulaGraph"],
        reversible=True,
        created_by="Luca_salthand"
    )

    print(f"   [OK] Created: {decision.name}")
    print(f"   [OK] Confidence: {decision.confidence}")
    print(f"   [OK] Bitemporal: valid_at={decision.valid_at.isoformat()}")
    return decision


def test_valid_memory():
    """Create a valid Memory node"""
    print("\n2. Testing Memory node creation...")

    memory = Memory(
        name="memory_v2_kickoff_20251016",
        description="Nicolas asked us to start V2 implementation",
        formation_trigger=FormationTrigger.DIRECT_EXPERIENCE,
        confidence=1.0,
        timestamp=datetime.utcnow(),
        participants=["Nicolas", "Ada"],
        emotional_state="excited + focused",
        entities_active=["Builder", "Architect", "Pragmatist"],
        significance=0.9
    )

    print(f"   [OK] Created: {memory.name}")
    print(f"   [OK] Participants: {memory.participants}")
    print(f"   [OK] Entities active: {memory.entities_active}")
    return memory


def test_valid_justifies():
    """Create a valid JUSTIFIES relation with full consciousness metadata"""
    print("\n3. Testing JUSTIFIES relation creation...")

    justification = JUSTIFIES(
        goal="Establish confidence in FalkorDB for multi-tenancy",
        mindstate="Pragmatist + Architect",
        energy=0.6,
        confidence=0.9,
        formation_trigger=FormationTrigger.SYSTEMATIC_ANALYSIS,
        justification_type="empirical_evidence",
        justification_strength="strongly_supports",
        felt_as="solid technical foundation",
        emotion_vector={
            "confidence": 0.8,
            "cautious-optimism": 0.6,
            "relief": 0.4
        },
        validation_status=ValidationStatus.TESTED,
        created_by="ada_architect"
    )

    print(f"   [OK] Goal: {justification.goal}")
    print(f"   [OK] Energy: {justification.energy}")
    print(f"   [OK] Emotions: {list(justification.emotion_vector.keys())}")
    return justification


def test_validation_enforcement():
    """Test that invalid data is rejected"""
    print("\n4. Testing validation enforcement...")

    # Test 1: energy out of range
    try:
        bad_relation = JUSTIFIES(
            goal="Test",
            mindstate="Test",
            energy=1.5,  # INVALID
            confidence=0.8,
            formation_trigger=FormationTrigger.INFERENCE,
            justification_type="logical_proof",
            justification_strength="proves"
        )
        print("   [FAIL] FAILED: Should have rejected energy=1.5")
        return False
    except Exception as e:
        print(f"   [OK] Correctly rejected energy=1.5")

    # Test 2: missing required field
    try:
        incomplete = Decision(
            name="test",
            description="test",
            formation_trigger=FormationTrigger.INFERENCE,
            confidence=0.8,
            decided_by="test"
            # MISSING: decision_date, rationale
        )
        print("   [FAIL] FAILED: Should have rejected missing required fields")
        return False
    except Exception as e:
        print(f"   [OK] Correctly rejected missing required fields")

    # Test 3: invalid emotion intensity
    try:
        bad_emotion = JUSTIFIES(
            goal="Test",
            mindstate="Test",
            energy=0.5,
            confidence=0.8,
            formation_trigger=FormationTrigger.INFERENCE,
            justification_type="logical_proof",
            justification_strength="proves",
            emotion_vector={"fear": 1.5}  # INVALID
        )
        print("   [FAIL] FAILED: Should have rejected emotion intensity=1.5")
        return False
    except Exception as e:
        print(f"   [OK] Correctly rejected emotion intensity=1.5")

    return True


def test_serialization():
    """Test that nodes serialize to JSON correctly"""
    print("\n5. Testing JSON serialization...")

    decision = Decision(
        name="test_decision",
        description="Test",
        formation_trigger=FormationTrigger.INFERENCE,
        confidence=0.8,
        decided_by="test",
        decision_date="2025-10-16",
        rationale="Test rationale"
    )

    json_str = decision.model_dump_json(indent=2)
    print(f"   [OK] Serialized to {len(json_str)} chars")
    print(f"   [OK] Contains 'formation_trigger': {('formation_trigger' in json_str)}")
    print(f"   [OK] Contains 'valid_at': {('valid_at' in json_str)}")
    return json_str


def main():
    print("=" * 60)
    print("CONSCIOUSNESS SCHEMA V2 - Basic Validation Test")
    print("=" * 60)

    try:
        test_valid_decision()
        test_valid_memory()
        test_valid_justifies()

        validation_passed = test_validation_enforcement()
        test_serialization()

        print("\n" + "=" * 60)
        if validation_passed:
            print("[PASS] ALL TESTS PASSED")
            print("=" * 60)
            print("\nSchema is functioning correctly.")
            print("Ready for Felix's LlamaIndex integration (Phase 1).")
            return 0
        else:
            print("[ERROR] VALIDATION TEST FAILED")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
