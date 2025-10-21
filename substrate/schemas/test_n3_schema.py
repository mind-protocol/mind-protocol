"""
N3 Ecosystem Intelligence Schema Test

Tests the new N3 node and relation types for ecosystem intelligence tracking.

Run: python substrate/schemas/test_n3_schema.py
"""

from consciousness_schema import (
    # N3 Node Types
    Company, External_Person, Wallet_Address, Post, Transaction,
    Psychological_Trait, Market_Signal,
    # N3 Relation Types
    POSTED_BY, MENTIONED_IN, HAS_TRAIT, OWNS, N3_JUSTIFIES,
    # Enums
    FormationTrigger, CompanyType, PersonType, Platform, Blockchain, Sentiment
)
from datetime import datetime


def test_company_node():
    """Test N3 Company node"""
    print("\n1. Testing Company (N3 External Organization)...")

    company = Company(
        name="Pump.fun",
        description="Solana meme coin launchpad platform",
        formation_trigger=FormationTrigger.EXTERNAL_INPUT,
        confidence=0.95,
        company_type=CompanyType.PROTOCOL,
        website="https://pump.fun",
        status="active",
        founded_date="2024",
        reputation_score=0.7,
        trust_level=0.6,
        relationship_status="neutral",
        data_sources=["Twitter", "On-chain data"],
        verification_status="partially_verified",
        importance_score=0.8,
        tags=["solana", "meme_coins", "launchpad"]
    )

    print(f"   [OK] Created: {company.name}")
    print(f"   [OK] Type: {company.company_type}")
    print(f"   [OK] Reputation: {company.reputation_score}")
    print(f"   [OK] Data sources: {company.data_sources}")
    return company


def test_external_person_node():
    """Test N3 External_Person node (KOL tracking)"""
    print("\n2. Testing External_Person (N3 KOL Tracking)...")

    kol = External_Person(
        name="CryptoInfluencer_X",
        description="Major AI token influencer, 500K followers",
        formation_trigger=FormationTrigger.EXTERNAL_INPUT,
        confidence=0.9,
        person_type=PersonType.KOL,
        primary_platform=Platform.TWITTER,
        social_handles={"twitter": "@cryptoX", "telegram": "cryptoX"},
        influence_score=0.85,
        follower_count=500000,
        engagement_rate=0.05,
        expertise_areas=["AI_tokens", "Solana", "Trading"],
        reputation_score=0.75,
        reliability_score=0.65,
        data_sources=["Twitter API", "Manual tracking"],
        verification_status="verified",
        importance_score=0.9,
        tags=["kol", "ai_narrative", "high_influence"]
    )

    print(f"   [OK] Created: {kol.name}")
    print(f"   [OK] Type: {kol.person_type}")
    print(f"   [OK] Platform: {kol.primary_platform}")
    print(f"   [OK] Influence: {kol.influence_score}")
    print(f"   [OK] Followers: {kol.follower_count}")
    return kol


def test_post_evidence_node():
    """Test N3 Post node (evidence for JUSTIFIES links)"""
    print("\n3. Testing Post (N3 Evidence Node)...")

    post = Post(
        name="post_cryptoX_AI_bullish_20251016",
        description="CryptoInfluencer_X bullish on AI agents",
        formation_trigger=FormationTrigger.AUTOMATED_RECOGNITION,
        confidence=1.0,
        content="AI agents will dominate 2025, buying $MIND and $TAO heavily. This is the next narrative.",
        author="CryptoInfluencer_X",
        platform=Platform.TWITTER,
        posted_at=datetime.utcnow(),
        post_url="https://twitter.com/cryptoX/status/123456",
        post_type="original",
        engagement_metrics={"likes": 3500, "retweets": 850, "replies": 120, "views": 125000},
        sentiment=Sentiment.VERY_POSITIVE,
        sentiment_confidence=0.92,
        topics=["AI agents", "AI narrative", "$MIND", "$TAO"],
        mentioned_assets=["MIND", "TAO"],
        extracted_claims=["AI agents will dominate 2025", "Buying $MIND and $TAO"],
        significance_score=0.85,
        virality_score=0.72,
        data_sources=["Twitter API"],
        importance_score=0.9,
        tags=["AI_narrative", "bullish_signal"]
    )

    print(f"   [OK] Created: {post.name}")
    print(f"   [OK] Author: {post.author}")
    print(f"   [OK] Sentiment: {post.sentiment}")
    print(f"   [OK] Virality: {post.virality_score}")
    print(f"   [OK] Claims extracted: {len(post.extracted_claims)}")
    return post


def test_psychological_trait_node():
    """Test N3 Psychological_Trait node (derived intelligence)"""
    print("\n4. Testing Psychological_Trait (N3 Derived Intelligence)...")

    trait = Psychological_Trait(
        name="trait_cryptoX_bullish_on_AI",
        description="CryptoInfluencer_X consistently bullish on AI tokens",
        formation_trigger=FormationTrigger.AUTOMATED_RECOGNITION,
        confidence=0.87,
        trait_name="bullish_on_AI_agents",
        subject="CryptoInfluencer_X",
        trait_category="market_sentiment",
        stability=0.85,
        evidence_count=15,
        contradictory_evidence_count=2,
        trait_strength=0.9,
        predictive_value=0.75,
        data_sources=["Post analysis"],
        importance_score=0.8,
        tags=["AI_narrative", "sentiment_analysis"]
    )

    print(f"   [OK] Created: {trait.name}")
    print(f"   [OK] Subject: {trait.subject}")
    print(f"   [OK] Trait: {trait.trait_name}")
    print(f"   [OK] Evidence count: {trait.evidence_count} supporting, {trait.contradictory_evidence_count} refuting")
    print(f"   [OK] Confidence: {trait.confidence}")
    return trait


def test_n3_justifies_relation():
    """Test N3_JUSTIFIES relation (evidence-backed claim)"""
    print("\n5. Testing N3_JUSTIFIES (Evidence -> Trait)...")

    justifies = N3_JUSTIFIES(
        goal="Establish that CryptoInfluencer_X is bullish on AI based on post evidence",
        mindstate="Automated pattern recognition + Analyst verification",
        energy=0.7,
        confidence=0.87,
        formation_trigger=FormationTrigger.AUTOMATED_RECOGNITION,
        justification_type="observed_behavior",
        justification_strength="strongly_supports",
        felt_as="Clear pattern across multiple posts",
        evidence_quality=0.9,
        evidence_weight=0.85,
        context_dependency="High engagement suggests genuine conviction vs performative",
        verified=True,
        emotion_vector={
            "analytical-confidence": 0.8,
            "pattern-recognition-satisfaction": 0.7
        }
    )

    print(f"   [OK] Goal: {justifies.goal}")
    print(f"   [OK] Justification strength: {justifies.justification_strength}")
    print(f"   [OK] Evidence quality: {justifies.evidence_quality}")
    print(f"   [OK] Evidence weight: {justifies.evidence_weight}")
    print(f"   [OK] Verified: {justifies.verified}")
    return justifies


def test_market_signal_node():
    """Test N3 Market_Signal node (actionable intelligence)"""
    print("\n6. Testing Market_Signal (N3 Actionable Intelligence)...")

    signal = Market_Signal(
        name="signal_AI_narrative_bullish_20251016",
        description="Strong bullish signal for AI tokens from multiple high-influence KOLs",
        formation_trigger=FormationTrigger.AUTOMATED_RECOGNITION,
        confidence=0.82,
        signal_type="bullish",
        asset_or_sector="AI_tokens",
        strength=0.85,
        generated_at=datetime.utcnow(),
        timeframe="short_term",
        source_count=12,
        source_diversity=0.7,
        trigger_conditions="3+ high-influence KOLs posting bullish within 24h",
        historical_accuracy=0.65,
        actionability="monitor",
        recommended_action="Watch for confirmation, consider position sizing",
        risk_assessment="Moderate - narrative-driven, could reverse quickly",
        data_sources=["Twitter analysis", "Engagement metrics"],
        importance_score=0.85,
        tags=["AI_narrative", "bullish_signal", "KOL_driven"]
    )

    print(f"   [OK] Created: {signal.name}")
    print(f"   [OK] Signal type: {signal.signal_type}")
    print(f"   [OK] Strength: {signal.strength}")
    print(f"   [OK] Source count: {signal.source_count}")
    print(f"   [OK] Actionability: {signal.actionability}")
    return signal


def test_validation():
    """Test N3 validation enforcement"""
    print("\n7. Testing N3 Validation Enforcement...")

    # Test 1: Invalid blockchain enum
    try:
        bad_wallet = Wallet_Address(
            name="test_wallet",
            description="test",
            formation_trigger=FormationTrigger.EXTERNAL_INPUT,
            confidence=0.8,
            address="0x123...",
            blockchain="bitcoin",  # INVALID - not in Blockchain enum
            wallet_type="personal"
        )
        print("   [FAIL] Should have rejected invalid blockchain")
        return False
    except Exception:
        print("   [OK] Correctly rejected invalid blockchain enum")

    # Test 2: Missing required N3 field
    try:
        bad_post = Post(
            name="test_post",
            description="test",
            formation_trigger=FormationTrigger.EXTERNAL_INPUT,
            confidence=0.8,
            content="Test content",
            author="test",
            platform=Platform.TWITTER,
            # MISSING: posted_at, post_url (required)
        )
        print("   [FAIL] Should have rejected missing required fields")
        return False
    except Exception:
        print("   [OK] Correctly rejected missing required N3 fields")

    # Test 3: Invalid evidence_quality range
    try:
        bad_justifies = N3_JUSTIFIES(
            goal="test",
            mindstate="test",
            energy=0.5,
            confidence=0.8,
            formation_trigger=FormationTrigger.INFERENCE,
            justification_type="empirical_evidence",
            justification_strength="strongly_supports",
            evidence_quality=1.5  # INVALID - must be 0.0-1.0
        )
        print("   [FAIL] Should have rejected invalid evidence_quality")
        return False
    except Exception:
        print("   [OK] Correctly rejected invalid evidence_quality range")

    return True


def main():
    print("=" * 70)
    print("N3 ECOSYSTEM INTELLIGENCE SCHEMA - Validation Test")
    print("=" * 70)

    try:
        # Test N3 node types
        company = test_company_node()
        kol = test_external_person_node()
        post = test_post_evidence_node()
        trait = test_psychological_trait_node()
        signal = test_market_signal_node()

        # Test N3 relation types
        justifies = test_n3_justifies_relation()

        # Test validation
        validation_passed = test_validation()

        print("\n" + "=" * 70)
        if validation_passed:
            print("[PASS] ALL N3 TESTS PASSED")
            print("=" * 70)
            print("\nN3 Ecosystem Intelligence schema is functioning correctly.")
            print(f"\nTotal schema capacity:")
            print(f"  - 44 node types (11 N1 + 13 N2 + 15 N3 + 5 shared)")
            print(f"  - 38 relation types (23 N1/N2 + 15 N3)")
            print(f"\nN3 enables evidence-backed ecosystem intelligence:")
            print(f"  - External entity tracking (companies, KOLs, wallets)")
            print(f"  - Evidence capture (posts, transactions, events)")
            print(f"  - Derived intelligence (traits, patterns, signals)")
            print(f"  - Real-time learning via JUSTIFIES/REFUTES links")
            return 0
        else:
            print("[ERROR] VALIDATION TEST FAILED")
            print("=" * 70)
            return 1

    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
