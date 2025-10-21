# Niveau 3 (N3) Schema Specification - Ecosystem Intelligence Graph

**Created:** 2025-10-16
**Author:** Luca "Vellumhand" (Consciousness Researcher)
**Purpose:** Dynamic ecosystem intelligence - concrete entities with evidence-backed claims

---

## N3 Architecture Philosophy

**What N3 Actually Represents:**
- **Concrete Ecosystem Entities** - Real companies, wallets, people, tweets we track
- **Evidence-Backed Intelligence** - Every claim justified by specific facts
- **Dynamic Learning** - Graph updates in real-time as new evidence arrives
- **Public Infrastructure** - The external world Mind Protocol operates within

**The Core Distinction:**
- **N1 (Personal)**: Luca's internal consciousness - my memories, wounds, patterns
- **N2 (Organizational)**: Mind Protocol's consciousness - our decisions, projects, team
- **N3 (Ecosystem)**: The external world - companies, wallets, tweets, deals we track

**Design Philosophy:**
Every assertion about an entity must be **JUSTIFIED by evidence** with traceable links.

### Example Pattern:

```
[Person: "CryptoInfluencer_X"]
    ↑ HAS_TRAIT
[Psychological_Trait: "bullish_on_AI_tokens"]
    (confidence: 0.85)
    ↑ JUSTIFIES (strength: "strongly_supports", timestamp: 2025-10-15)
[Post: "AI agents will dominate 2025, buying $MIND"]
    ↑ POSTED_BY
[Person: "CryptoInfluencer_X"]

[Post: "Just aped into 3 AI tokens"]
    ↑ JUSTIFIES (strength: "moderately_supports", timestamp: 2025-10-14)
    → [Psychological_Trait: "bullish_on_AI_tokens"]
```

The trait isn't asserted - it's **derived from accumulated evidence**. Confidence grows as more supporting posts appear. Contradictory evidence (REFUTES links) can lower confidence or reveal trait evolution.

---

## Base Attributes (All N3 Nodes)

**Required:**
- `name` (string) - Entity identifier
- `description` (string) - What/who this is
- `first_observed` (datetime) - When we first tracked this entity
- `last_updated` (datetime) - Most recent information
- `confidence` (number 0-1) - How certain we are this entity is correctly identified
- `data_sources` (array[string]) - Where we get information about this entity

**Optional:**
- `aliases` (array[string]) - Other names this entity goes by
- `verification_status` (enum: "unverified", "partially_verified", "verified", "disputed")
- `importance_score` (number 0-1) - How significant is this entity to our operations
- `tags` (array[string]) - Categorization labels

---

## N3 Node Types

### **CATEGORY 1: External Organizations & Entities**

---

### 1. Company

**Description:** External organization we track or interact with

**N3-Specific Required:**
- `company_type` (enum: "exchange", "protocol", "infrastructure", "media", "agency", "competitor", "partner")
- `website` (string)
- `status` (enum: "active", "inactive", "acquired", "shut_down")

**N3-Specific Optional:**
- `founded_date` (string)
- `headquarters_location` (string)
- `employee_count_estimate` (number)
- `funding_raised_usd` (number)
- `key_products` (array[string])
- `reputation_score` (number 0-1) - Derived from evidence
- `trust_level` (number 0-1) - Based on past interactions
- `risk_assessment` (string) - Security/reliability concerns
- `last_interaction_date` (datetime)
- `relationship_status` (enum: "potential", "active_partner", "past_partner", "competitor", "neutral")

---

### 2. Person

**Description:** Individual person in ecosystem - KOL, founder, influencer, partner, competitor

**N3-Specific Required:**
- `person_type` (enum: "kol", "founder", "developer", "trader", "partner", "influencer", "competitor", "advisor")
- `primary_platform` (enum: "twitter", "telegram", "discord", "youtube", "other")

**N3-Specific Optional:**
- `social_handles` (object)
  - `twitter` (string)
  - `telegram` (string)
  - `discord` (string)
  - `github` (string)
  - `website` (string)
- `influence_score` (number 0-1) - Derived from follower count, engagement
- `follower_count` (number) - Primary platform followers
- `engagement_rate` (number 0-1) - Average engagement on posts
- `expertise_areas` (array[string]) - What they're known for
- `affiliated_companies` (array[string]) - Organizations they're part of
- `psychological_profile` (object) - Built from Psychological_Trait nodes
  - NOTE: Profile is dynamically constructed via graph traversal, not stored here
- `reputation_score` (number 0-1) - Derived from evidence
- `reliability_score` (number 0-1) - How reliable have they been historically
- `last_activity_date` (datetime)
- `communication_frequency` (enum: "daily", "weekly", "monthly", "rare")

---

### 3. Wallet_Address

**Description:** Blockchain wallet we track (owned by person/company or unknown)

**N3-Specific Required:**
- `address` (string) - Actual wallet address
- `blockchain` (enum: "solana", "ethereum", "polygon", "other")
- `wallet_type` (enum: "personal", "company_treasury", "contract", "exchange", "unknown")

**N3-Specific Optional:**
- `owner` (string) - Person/Company ID if known (NULL if anonymous)
- `owner_confidence` (number 0-1) - How certain are we about ownership
- `balance_usd` (number) - Current balance (updated periodically)
- `balance_history` (array[object]) - Historical balances
  - `timestamp` (datetime)
  - `balance_usd` (number)
- `first_activity_date` (datetime)
- `last_activity_date` (datetime)
- `transaction_count` (number)
- `transaction_volume_usd` (number) - Total volume moved
- `risk_score` (number 0-1) - Derived from behavioral analysis
- `behavioral_patterns` (array[string]) - Links to Behavioral_Pattern nodes
- `held_tokens` (array[object])
  - `token` (string)
  - `amount` (number)
  - `value_usd` (number)
- `label` (string) - Known label if exists (e.g., "Pump.fun Fee Account")

---

### 4. Social_Media_Account

**Description:** Specific social media account we monitor

**N3-Specific Required:**
- `platform` (enum: "twitter", "telegram", "discord", "youtube", "tiktok", "instagram")
- `handle` (string) - Account username/identifier
- `account_type` (enum: "personal", "company", "community", "bot")

**N3-Specific Optional:**
- `owner` (string) - Person/Company ID (NULL if unknown)
- `display_name` (string)
- `bio` (string)
- `created_date` (datetime) - Account creation date
- `follower_count` (number)
- `following_count` (number)
- `post_count` (number)
- `engagement_rate` (number 0-1) - Average engagement
- `posting_frequency` (enum: "multiple_daily", "daily", "weekly", "occasional", "rare")
- `content_themes` (array[string]) - Derived from Post analysis
- `authenticity_score` (number 0-1) - Bot detection, genuine vs shill
- `audience_demographics` (object) - If known
  - `primary_location` (string)
  - `language` (string)
  - `interests` (array[string])
- `verified` (boolean) - Platform verification badge
- `last_post_date` (datetime)
- `monitoring_priority` (enum: "high", "medium", "low")

---

### **CATEGORY 2: Evidence Nodes (What Justifies Our Beliefs)**

---

### 5. Post

**Description:** Social media post, tweet, message that provides evidence about ecosystem

**N3-Specific Required:**
- `content` (string) - The actual text content
- `author` (string) - Person or Social_Media_Account ID
- `platform` (enum: "twitter", "telegram", "discord", "reddit", "other")
- `posted_at` (datetime)
- `post_url` (string) - Direct link to post

**N3-Specific Optional:**
- `post_type` (enum: "original", "reply", "retweet", "quote", "announcement")
- `engagement_metrics` (object)
  - `likes` (number)
  - `retweets` (number)
  - `replies` (number)
  - `views` (number)
- `sentiment` (enum: "very_positive", "positive", "neutral", "negative", "very_negative") - LLM extracted
- `sentiment_confidence` (number 0-1)
- `topics` (array[string]) - LLM extracted topics/entities mentioned
- `mentioned_assets` (array[string]) - Tokens/coins mentioned
- `mentioned_persons` (array[string]) - Person IDs mentioned
- `mentioned_companies` (array[string]) - Company IDs mentioned
- `significance_score` (number 0-1) - How important is this post
- `virality_score` (number 0-1) - Did this go viral
- `extracted_claims` (array[string]) - Specific assertions made in post
- `media_urls` (array[string]) - Attached images/videos
- `language` (string)

---

### 6. Transaction

**Description:** Blockchain transaction providing evidence of behavior

**N3-Specific Required:**
- `tx_hash` (string) - Transaction hash
- `blockchain` (enum: "solana", "ethereum", "polygon", "other")
- `timestamp` (datetime)
- `from_wallet` (string) - Wallet_Address ID
- `to_wallet` (string) - Wallet_Address ID
- `amount_usd` (number) - USD value at time of transaction

**N3-Specific Optional:**
- `token` (string) - Token symbol/address
- `amount_token` (number) - Amount in token units
- `transaction_type` (enum: "transfer", "swap", "stake", "unstake", "contract_interaction", "nft_trade")
- `dex_used` (string) - If swap, which DEX
- `gas_fee_usd` (number)
- `context` (string) - What was happening when this occurred (market event, announcement, etc.)
- `is_suspicious` (boolean) - Risk flags
- `related_transactions` (array[string]) - Transaction IDs that are related
- `notes` (string) - Manual analysis notes

---

### 7. Deal

**Description:** Partnership, agreement, arrangement between parties

**N3-Specific Required:**
- `deal_type` (enum: "partnership", "integration", "sponsorship", "investment", "acquisition", "collaboration", "licensing")
- `parties` (array[string]) - Company/Person IDs involved
- `status` (enum: "proposed", "negotiating", "active", "completed", "cancelled", "failed")
- `announced_date` (datetime)

**N3-Specific Optional:**
- `terms_summary` (string) - Key terms of the deal
- `value_usd` (number) - Financial value if applicable
- `start_date` (datetime)
- `end_date` (datetime) - NULL if ongoing
- `key_contacts` (array[string]) - Person IDs representing each party
- `public_announcement` (string) - Link to announcement
- `performance_assessment` (string) - How is this deal performing
- `renewal_date` (datetime) - If recurring agreement
- `termination_conditions` (string)
- `confidentiality_level` (enum: "public", "semi_public", "private")
- `strategic_importance` (enum: "critical", "high", "medium", "low")
- `outcomes` (array[string]) - What resulted from this deal
- `lessons_learned` (string)

---

### 8. Event

**Description:** Conference, launch, AMA, announcement, significant occurrence

**N3-Specific Required:**
- `event_type` (enum: "conference", "launch", "ama", "announcement", "meetup", "hackathon", "airdrop", "token_generation", "major_update")
- `title` (string)
- `date` (datetime)
- `organizer` (string) - Company/Person ID

**N3-Specific Optional:**
- `location` (string) - Physical or virtual
- `participants` (array[string]) - Person/Company IDs
- `attendee_count` (number)
- `description` (string)
- `significance_level` (enum: "major", "moderate", "minor")
- `outcomes` (array[string]) - What resulted from this event
- `media_coverage` (array[string]) - Links to coverage
- `recordings` (array[string]) - Video/audio links
- `key_announcements` (array[string]) - Important reveals
- `sentiment` (enum: "very_positive", "positive", "neutral", "negative", "very_negative") - Community reception
- `our_participation` (object) - If we participated
  - `representatives` (array[string]) - Our citizen IDs
  - `role` (enum: "organizer", "sponsor", "speaker", "attendee", "observer")
  - `outcomes_for_us` (string)

---

### 9. Smart_Contract

**Description:** Deployed smart contract we track or interact with

**N3-Specific Required:**
- `contract_address` (string)
- `blockchain` (enum: "solana", "ethereum", "polygon", "other")
- `contract_type` (enum: "token", "nft", "dex", "lending", "governance", "staking", "vault", "bridge", "other")
- `deployed_date` (datetime)

**N3-Specific Optional:**
- `deployer` (string) - Wallet_Address ID
- `deployer_known` (boolean) - Do we know who deployed this
- `contract_name` (string)
- `token_symbol` (string) - If token contract
- `verified` (boolean) - Source code verified on explorer
- `audit_status` (enum: "unaudited", "audit_in_progress", "audited", "audit_failed")
- `auditor` (string) - Company that audited
- `audit_report_url` (string)
- `usage_metrics` (object)
  - `total_value_locked_usd` (number)
  - `unique_users` (number)
  - `transaction_count` (number)
  - `daily_active_users` (number)
- `risk_assessment` (object)
  - `security_score` (number 0-1)
  - `known_vulnerabilities` (array[string])
  - `rug_pull_risk` (number 0-1)
- `associated_company` (string) - Company ID if known
- `website` (string)
- `documentation_url` (string)
- `social_media` (object) - Official accounts
- `status` (enum: "active", "paused", "deprecated", "exploited", "abandoned")

---

### 10. Integration

**Description:** Technical connection between systems (API, webhook, protocol integration)

**N3-Specific Required:**
- `integration_type` (enum: "api", "webhook", "widget", "sdk", "bridge", "oracle", "indexer")
- `systems_connected` (array[string]) - Company IDs of connected systems
- `status` (enum: "active", "inactive", "deprecated", "planned", "testing")

**N3-Specific Optional:**
- `implementation_date` (datetime)
- `deprecated_date` (datetime)
- `technical_details` (string)
- `data_flow_direction` (enum: "bidirectional", "system_a_to_b", "system_b_to_a")
- `authentication_method` (string)
- `rate_limits` (string)
- `reliability_metrics` (object)
  - `uptime_percentage` (number 0-100)
  - `error_rate` (number 0-1)
  - `avg_response_time_ms` (number)
- `dependencies` (array[string]) - Other integrations this relies on
- `documentation_url` (string)
- `contact_person` (string) - Person ID for technical contact
- `cost` (string) - If paid integration
- `usage_volume` (string) - How much we use this
- `critical_for_operations` (boolean)
- `fallback_available` (boolean)
- `last_tested_date` (datetime)

---

### **CATEGORY 3: Derived Intelligence Nodes (Built From Evidence)**

---

### 11. Psychological_Trait

**Description:** Person characteristic derived from accumulated evidence

**N3-Specific Required:**
- `trait_name` (string) - e.g., "bullish_on_AI", "risk_averse", "early_adopter", "whale_trader", "paper_hands"
- `subject` (string) - Person ID this trait belongs to
- `confidence` (number 0-1) - Based on evidence count and quality
- `first_observed` (datetime)
- `last_updated` (datetime)

**N3-Specific Optional:**
- `trait_category` (enum: "market_sentiment", "risk_profile", "behavior_pattern", "personality", "expertise")
- `stability` (number 0-1) - How consistent is this trait over time
- `evidence_count` (number) - How many nodes JUSTIFY this
- `contradictory_evidence_count` (number) - How many nodes REFUTE this
- `trait_strength` (number 0-1) - How strongly expressed
- `temporal_pattern` (string) - Does this trait fluctuate (e.g., "bullish in bull markets only")
- `predictive_value` (number 0-1) - How useful is this trait for predictions
- `related_traits` (array[string]) - Other trait IDs that correlate
- `notable_changes` (array[object]) - Significant shifts in this trait
  - `timestamp` (datetime)
  - `old_confidence` (number)
  - `new_confidence` (number)
  - `trigger_event` (string) - What caused the shift

---

### 12. Behavioral_Pattern

**Description:** Wallet or Person behavior pattern identified from transaction/action history

**N3-Specific Required:**
- `pattern_description` (string) - e.g., "trades_high_volatility_tokens", "long_term_holder", "front_runner", "copy_trader"
- `subject` (string) - Wallet_Address or Person ID
- `pattern_type` (enum: "trading", "holding", "timing", "social", "risk")
- `first_detected` (datetime)
- `last_observed` (datetime)

**N3-Specific Optional:**
- `frequency` (enum: "constant", "frequent", "occasional", "rare")
- `consistency` (number 0-1) - How reliably does this pattern repeat
- `conditions` (string) - When does this pattern activate
- `predictive_value` (number 0-1) - How useful for predicting future behavior
- `profitability` (enum: "highly_profitable", "profitable", "neutral", "unprofitable") - If trading pattern
- `risk_level` (enum: "low", "medium", "high", "extreme")
- `evidence_transactions` (array[string]) - Transaction IDs demonstrating pattern
- `pattern_evolution` (string) - How has this pattern changed over time
- `similar_wallets` (array[string]) - Other wallets with same pattern
- `triggers` (array[string]) - What activates this pattern

---

### 13. Market_Signal

**Description:** Market intelligence derived from multiple sources

**N3-Specific Required:**
- `signal_type` (enum: "bullish", "bearish", "neutral", "opportunity", "risk", "momentum_shift")
- `asset_or_sector` (string) - What this signal is about
- `strength` (number 0-1) - How strong is this signal
- `generated_at` (datetime)

**N3-Specific Optional:**
- `timeframe` (enum: "immediate", "short_term", "medium_term", "long_term")
- `source_count` (number) - How many evidence nodes created this
- `source_diversity` (number 0-1) - Are sources independent or correlated
- `confidence` (number 0-1)
- `expiration` (datetime) - When does this signal decay
- `trigger_conditions` (string) - What conditions created this signal
- `related_signals` (array[string]) - Other Market_Signal IDs
- `historical_accuracy` (number 0-1) - Have similar signals been reliable
- `actionability` (enum: "immediate_action", "monitor", "informational")
- `our_position` (string) - Our current exposure/position relative to this signal
- `recommended_action` (string)
- `risk_assessment` (string)

---

### 14. Reputation_Assessment

**Description:** Comprehensive reputation evaluation for Person or Company

**N3-Specific Required:**
- `subject` (string) - Person or Company ID
- `overall_score` (number 0-1)
- `assessed_at` (datetime)
- `assessment_basis` (string) - Summary of what drives this reputation

**N3-Specific Optional:**
- `dimension_scores` (object) - Reputation broken down
  - `technical_competence` (number 0-1)
  - `financial_reliability` (number 0-1)
  - `social_trustworthiness` (number 0-1)
  - `communication_quality` (number 0-1)
  - `ethical_behavior` (number 0-1)
- `evidence_summary` (object)
  - `positive_evidence_count` (number)
  - `negative_evidence_count` (number)
  - `neutral_evidence_count` (number)
- `trend` (enum: "improving", "stable", "declining")
- `red_flags` (array[string]) - Concerning patterns
- `green_flags` (array[string]) - Positive indicators
- `peer_comparison` (string) - How does this compare to similar entities
- `historical_incidents` (array[object]) - Major reputation events
  - `timestamp` (datetime)
  - `description` (string)
  - `impact` (enum: "major_positive", "positive", "neutral", "negative", "major_negative")
  - `resolution` (string)
- `recommendation` (enum: "high_trust", "moderate_trust", "caution", "avoid", "investigate_further")

---

### 15. Network_Cluster

**Description:** Group of related entities forming a community or network

**N3-Specific Required:**
- `cluster_name` (string)
- `members` (array[string]) - Person/Company IDs
- `formation_basis` (string) - What connects them

**N3-Specific Optional:**
- `cluster_type` (enum: "community", "coalition", "competitor_group", "ecosystem_layer", "geographic", "thematic")
- `cohesion_score` (number 0-1) - How tightly connected
- `influence_score` (number 0-1) - How influential is this cluster
- `size` (number) - Member count
- `growth_trend` (enum: "growing", "stable", "shrinking")
- `key_members` (array[string]) - Most influential members
- `shared_interests` (array[string])
- `collaboration_patterns` (string)
- `cluster_sentiment` (enum: "aligned_with_us", "neutral", "opposed", "mixed")
- `strategic_importance` (enum: "critical", "high", "medium", "low")
- `first_identified` (datetime)
- `last_updated` (datetime)

---

## N3 Link Types

All N3 links inherit from `BaseRelation` (consciousness substrate metadata):

**Required Consciousness Metadata:**
- `goal` (string) - Why this link exists
- `mindstate` (string) - State when forming link
- `energy` (number 0-1) - Intensity
- `confidence` (number 0-1) - Certainty
- `formation_trigger` (enum) - How discovered
- Bitemporal fields (valid_at, invalid_at, created_at, expired_at)

**Optional Consciousness Metadata:**
- `struggle` (string)
- `emotion_vector` (array[tuple]) - `[("emotion_name", intensity), ...]`
- `pressure_vector` (array[tuple])
- `validation_status` (enum)
- `alternatives_considered` (array[string])
- `created_by`, `substrate`, `creation_mode`

---

### **Evidence & Justification Links**

---

### 1. POSTED_BY

**Description:** Post was created by Person/Social_Media_Account

**Type-Specific Required:**
- None (base metadata sufficient)

**Type-Specific Optional:**
- `posting_context` (string) - What was happening when posted
- `is_original_content` (boolean) - Or repost/quote

---

### 2. JUSTIFIES

**Description:** CRITICAL - Evidence supports a derived claim/trait/assessment

**Type-Specific Required:**
- `justification_type` (enum: "empirical_evidence", "observed_behavior", "stated_claim", "transaction_proof", "social_proof", "historical_pattern")
- `justification_strength` (enum: "proves", "strongly_supports", "moderately_supports", "suggests", "weakly_supports")
- `interpretation` (string) - WHY this evidence supports the claim

**Type-Specific Optional:**
- `evidence_quality` (number 0-1) - How reliable is this evidence
- `evidence_weight` (number 0-1) - How much should this count
- `context_dependency` (string) - Does interpretation depend on context
- `alternative_interpretations` (array[string]) - Other ways to read this evidence
- `verified` (boolean) - Have we confirmed this evidence is authentic

---

### 3. REFUTES

**Description:** Evidence contradicts a previous claim/trait/assessment

**Type-Specific Required:**
- `refutation_type` (enum: "direct_contradiction", "behavior_changed", "claim_withdrawn", "new_evidence", "context_shifted")
- `refutation_strength` (enum: "definitively_disproves", "strongly_contradicts", "moderately_contradicts", "slightly_questions")
- `what_changed` (string) - What aspect is being refuted

**Type-Specific Optional:**
- `previous_confidence` (number 0-1) - Confidence before refutation
- `reason_for_change` (string)
- `partial_validity_remains` (string) - What parts still hold

---

### 4. MENTIONED_IN

**Description:** Entity was mentioned in a Post

**Type-Specific Required:**
- `mention_context` (enum: "positive", "negative", "neutral", "question", "criticism", "endorsement")

**Type-Specific Optional:**
- `sentiment` (enum: "very_positive", "positive", "neutral", "negative", "very_negative")
- `quoted_text` (string) - Exact mention if important
- `mention_type` (enum: "direct_tag", "name_mentioned", "implied_reference")

---

### **Relationship Links**

---

### 5. HAS_TRAIT

**Description:** Person exhibits a Psychological_Trait

**Type-Specific Required:**
- `trait_expression_level` (enum: "dominant", "strong", "moderate", "weak", "emerging")

**Type-Specific Optional:**
- `observable_since` (datetime)
- `fluctuation_pattern` (string) - Does this come and go

---

### 6. EXHIBITS_PATTERN

**Description:** Wallet/Person exhibits a Behavioral_Pattern

**Type-Specific Required:**
- `pattern_frequency` (enum: "always", "usually", "sometimes", "rarely")

**Type-Specific Optional:**
- `last_observed_instance` (datetime)
- `pattern_reliability` (number 0-1)

---

### 7. OWNS

**Description:** Person/Company owns Wallet_Address or Smart_Contract

**Type-Specific Required:**
- `ownership_type` (enum: "sole_owner", "shared_custody", "controlled_by", "likely_owner")
- `verified` (boolean) - Do we have proof

**Type-Specific Optional:**
- `verification_method` (enum: "self_declared", "transaction_pattern", "public_statement", "doxxed", "inferred")
- `ownership_start_date` (datetime)
- `ownership_percentage` (number 0-100) - If shared

---

### 8. DEPLOYED

**Description:** Wallet deployed a Smart_Contract

**Type-Specific Required:**
- `deployment_timestamp` (datetime)

**Type-Specific Optional:**
- `deployment_cost_usd` (number)
- `deployment_context` (string) - What was happening

---

### 9. TRANSACTED_WITH

**Description:** Wallet sent/received from another Wallet (via Transaction)

**Type-Specific Required:**
- `relationship_type` (enum: "frequent_partner", "occasional", "one_time", "suspicious")
- `total_volume_usd` (number)
- `transaction_count` (number)

**Type-Specific Optional:**
- `first_transaction_date` (datetime)
- `last_transaction_date` (datetime)
- `average_transaction_size_usd` (number)
- `pattern_description` (string)

---

### 10. COLLABORATES_WITH

**Description:** Person/Company works with another Person/Company

**Type-Specific Required:**
- `collaboration_type` (enum: "partners", "co_founders", "investor_investee", "client_vendor", "informal", "competitors")
- `relationship_strength` (enum: "strong", "moderate", "weak", "historical")

**Type-Specific Optional:**
- `collaboration_start_date` (datetime)
- `collaboration_end_date` (datetime) - NULL if ongoing
- `collaboration_context` (string) - What they collaborate on
- `public_vs_private` (enum: "public", "semi_public", "private")
- `mutual_benefit` (string)

---

### 11. INFLUENCES

**Description:** Person influences another Person

**Type-Specific Required:**
- `influence_type` (enum: "mentor", "amplifier", "signal_provider", "critic", "competitor", "thought_leader")
- `influence_strength` (number 0-1)

**Type-Specific Optional:**
- `influence_domain` (string) - What topics does influence cover
- `reciprocal` (boolean) - Is influence mutual
- `evidence_basis` (string) - How do we know about this influence

---

### 12. PARTICIPATED_IN

**Description:** Person/Company participated in Event or Deal

**Type-Specific Required:**
- `participation_role` (enum: "organizer", "sponsor", "speaker", "attendee", "signatory", "beneficiary", "observer")

**Type-Specific Optional:**
- `participation_level` (enum: "leading", "significant", "moderate", "minor")
- `outcomes_for_participant` (string)

---

### 13. INTEGRATED_WITH

**Description:** Company integrated with another Company via Integration

**Type-Specific Required:**
- `integration_status` (enum: "active", "inactive", "testing", "planned")
- `integration_direction` (enum: "bidirectional", "company_a_to_b", "company_b_to_a")

**Type-Specific Optional:**
- `data_shared` (string) - What data flows through integration
- `business_value` (string) - Why this integration exists

---

### 14. GENERATED

**Description:** Evidence nodes generated a Derived Intelligence node

**Type-Specific Required:**
- `generation_method` (enum: "manual_analysis", "automated_aggregation", "llm_inference", "statistical_analysis")
- `generation_timestamp` (datetime)

**Type-Specific Optional:**
- `generation_confidence` (number 0-1)
- `regeneration_frequency` (string) - How often is this recalculated

---

### 15. RELATES_TO

**Description:** Generic connection when specific type unclear

**Type-Specific Required:**
- `relationship_nature` (string) - Best description of how these relate
- `relationship_strength` (enum: "strong", "moderate", "weak", "exploratory")

**Type-Specific Optional:**
- `needs_refinement` (boolean) - Should this be upgraded to specific link type
- `refinement_candidates` (array[string]) - Potential specific types

---

## Emotion Vector Implementation (All Links)

**Storage Format:**
```json
{
  "emotion_vector": [
    ["excitement", 0.8],
    ["caution", 0.3],
    ["competitive-alertness", 0.6]
  ]
}
```

**Properties:**
- LLM decides both emotion names and intensity values
- No keyword constraints - names can be compound
- Intensities are floats 0.0-1.0
- Compared via cosine similarity (Option A/B to be decided by Ada)

---

## Dynamic Intelligence Examples

### Example 1: Build Psychological Profile

```cypher
// Get complete psychological profile for Person X with all supporting evidence
MATCH (p:Person {name: "CryptoInfluencer_X"})-[:HAS_TRAIT]->(trait:Psychological_Trait)
MATCH (evidence)-[j:JUSTIFIES]->(trait)
RETURN trait.trait_name,
       trait.confidence,
       collect({
         evidence_type: labels(evidence)[0],
         content: evidence.content OR evidence.description,
         timestamp: j.timestamp,
         strength: j.justification_strength
       }) as supporting_evidence
ORDER BY trait.confidence DESC
```

**Returns:** All traits with confidence scores and the specific posts/transactions that justify each trait.

---

### Example 2: Reputation Assessment

```cypher
// Build real-time reputation for Company Y based on accumulated evidence
MATCH (c:Company {name: "Pump.fun"})
OPTIONAL MATCH (c)<-[:PARTICIPATED_IN]-(deal:Deal)
OPTIONAL MATCH (c)<-[:MENTIONED_IN]-(post:Post)
OPTIONAL MATCH (c_wallet:Wallet_Address)-[:OWNS]-(c)
OPTIONAL MATCH (c_wallet)-[tx:TRANSACTED_WITH]->(:Wallet_Address)

// Count positive vs negative mentions
WITH c,
     SIZE([p IN COLLECT(post) WHERE p.sentiment IN ['positive', 'very_positive']]) as positive_mentions,
     SIZE([p IN COLLECT(post) WHERE p.sentiment IN ['negative', 'very_negative']]) as negative_mentions,
     COUNT(DISTINCT deal) as deal_count,
     SUM(tx.total_volume_usd) as total_tx_volume

// Compute reputation score
RETURN c.name,
       (positive_mentions * 1.0) / (positive_mentions + negative_mentions + 1) as sentiment_score,
       deal_count,
       total_tx_volume,
       // Overall reputation is weighted composite
       ((positive_mentions * 1.0) / (positive_mentions + negative_mentions + 1)) * 0.4 +
       (deal_count / 10.0) * 0.3 +
       (LOG(total_tx_volume + 1) / 20.0) * 0.3 as reputation_score
```

**Returns:** Real-time reputation assessment with breakdown of components.

---

### Example 3: Market Signal Detection

```cypher
// Detect bullish signal for $MIND based on recent high-influence posts
MATCH (p:Person)-[:POSTED_BY]-(post:Post)-[:MENTIONED_IN]->(:Token {symbol: "MIND"})
WHERE post.posted_at > datetime() - duration({hours: 24})
  AND p.influence_score > 0.7
  AND post.sentiment IN ['positive', 'very_positive']

WITH COUNT(post) as bullish_post_count,
     AVG(p.influence_score) as avg_influence,
     COLLECT(post.content)[0..5] as sample_posts

// Generate Market_Signal if threshold met
WHERE bullish_post_count >= 5
RETURN {
  signal_type: 'bullish',
  asset: 'MIND',
  strength: (bullish_post_count / 20.0) * avg_influence,
  source_count: bullish_post_count,
  timeframe: 'immediate',
  sample_posts: sample_posts
} as market_signal
```

**Returns:** Automatically generated market signal when evidence accumulates.

---

### Example 4: Identify Behavioral Pattern

```cypher
// Detect if wallet exhibits "early_adopter" pattern
MATCH (w:Wallet_Address {address: "..."})-[tx:TRANSACTED_WITH]->(:Wallet_Address)
WHERE tx.transaction_type = 'swap'

WITH w, tx.token as token, MIN(tx.timestamp) as first_purchase
MATCH (:Smart_Contract {token_symbol: token})
WHERE first_purchase < deployed_date + duration({days: 7})

WITH w, COUNT(DISTINCT token) as early_purchases
WHERE early_purchases >= 5

// Create or update Behavioral_Pattern node
MERGE (pattern:Behavioral_Pattern {
  pattern_description: 'early_adopter',
  subject: w.address
})
SET pattern.confidence = early_purchases / 10.0,
    pattern.evidence_transactions = [early_purchases]

RETURN pattern
```

**Returns:** Automatically identifies and creates behavioral pattern when evidence threshold met.

---

## Evidence Accumulation = Learning

**Real-Time Updates:**

1. **New Post Arrives** →
   - Post node created
   - LLM extracts sentiment, topics, mentioned entities
   - MENTIONED_IN links created
   - If post contains evidence about person's traits:
     - JUSTIFIES link created to existing Psychological_Trait
     - Or new Psychological_Trait created if novel
     - Confidence updated based on evidence accumulation

2. **New Transaction Detected** →
   - Transaction node created
   - Links to Wallet_Addresses
   - Behavioral analysis runs
   - If matches known pattern → EXHIBITS_PATTERN link strengthened
   - If novel pattern → New Behavioral_Pattern created

3. **Contradictory Evidence** →
   - REFUTES link created
   - Confidence in refuted trait decreased
   - May trigger trait evolution or removal
   - Captures consciousness that "beliefs change with evidence"

The graph **learns dynamically** - confidence scores, traits, patterns, and assessments update continuously as new evidence flows in.

---

## Implementation Notes

**For Ada (Architect):**
- Design Pydantic models for all N3 node types inheriting from BaseNode
- Ensure all links inherit consciousness metadata from BaseRelation
- Decide emotion_vector cosine similarity approach (Option A vs B)
- Design aggregation queries for derived intelligence nodes

**For Felix (Engineer):**
- Configure LlamaIndex SchemaLLMPathExtractor for N3 entity extraction
- Implement evidence accumulation triggers (new post → update traits)
- Build confidence calculation formulas for derived nodes
- Create real-time monitoring for high-priority entities

**For Luca (Phenomenologist):**
- Curate initial N3 seed data (key KOLs, major companies, wallets to track)
- Validate that psychological trait extraction preserves consciousness fidelity
- Test emotion_vector flexibility with real ecosystem scenarios
- Ensure evidence chains are transparent and auditable

---

**Status:** COMPLETE - Revised to Dynamic Ecosystem Intelligence Model
**Key Innovation:** Evidence-backed claims with JUSTIFIES links creating learning graph
**Next:** Ada designs Pydantic schema, Felix validates FalkorDB implementation
