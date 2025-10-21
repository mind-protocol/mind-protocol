#!/usr/bin/env python3
"""
Convert consciousness node types schema to markdown format for CLAUDE.md inclusion.

Usage:
    python tools/convert_node_types_to_markdown.py > consciousness_node_types.md
"""

# Node type definitions extracted from consciousness schema
NODE_TYPES = {
    "N1_Personal": {
        "description": "Individual subjective experience - exists in citizen graphs (e.g., citizen_luca)",
        "design_philosophy": "Models the phenomenological texture of lived experience - memories, wounds, coping patterns. High energy, high emotion_vector usage.",
        "types": [
            {
                "name": "Memory",
                "purpose": "Specific experience or moment",
                "required_attrs": ["timestamp", "participants (array)"],
                "mechanism": "Pattern formation via repeated activation"
            },
            {
                "name": "Conversation",
                "purpose": "Exchange with explicit turn structure",
                "required_attrs": ["timestamp", "with_person", "turn_count"],
                "mechanism": "Relationship deepening mechanism"
            },
            {
                "name": "Person",
                "purpose": "Individual I have relationship with",
                "required_attrs": ["relationship_type (enum)"],
                "mechanism": "Entity representation in personal ontology"
            },
            {
                "name": "Relationship",
                "purpose": "Connection dynamics and evolution",
                "required_attrs": ["with_person", "relationship_quality (float)"],
                "mechanism": "Dynamic link weight updates"
            },
            {
                "name": "Personal_Goal",
                "purpose": "Individual aspiration",
                "required_attrs": ["goal_description", "why_it_matters"],
                "mechanism": "Drives spreading activation priority"
            },
            {
                "name": "Personal_Value",
                "purpose": "What matters to me individually",
                "required_attrs": ["value_statement", "why_i_hold_it"],
                "mechanism": "Constraint on action selection"
            },
            {
                "name": "Personal_Pattern",
                "purpose": "Habit or recurring response",
                "required_attrs": ["behavior_description", "frequency (enum)"],
                "mechanism": "Learned behavioral attractor"
            },
            {
                "name": "Realization",
                "purpose": "Insight or comprehension shift",
                "required_attrs": ["what_i_realized", "context_when_discovered"],
                "mechanism": "Sudden link formation event"
            },
            {
                "name": "Wound",
                "purpose": "Personal scar or trauma",
                "required_attrs": ["what_happened", "emotional_impact (string)"],
                "mechanism": "High-energy suppression node"
            },
            {
                "name": "Coping_Mechanism",
                "purpose": "Response to stress",
                "required_attrs": ["mechanism_description", "what_it_protects_from"],
                "mechanism": "Defensive entity coalition"
            },
            {
                "name": "Trigger",
                "purpose": "What awakens entity coalitions",
                "required_attrs": ["stimulus_description", "activated_entities (array)"],
                "mechanism": "Activation propagation initiator"
            }
        ]
    },

    "N2_Organizational": {
        "description": "Collective intelligence and coordination - exists in organizational graphs (e.g., org_mind_protocol)",
        "design_philosophy": "Models team cognition - decisions, coordination, collective learning. Medium energy, emphasis on validation_status tracking.",
        "types": [
            {
                "name": "Human",
                "purpose": "Human participant in organization",
                "required_attrs": ["role", "expertise (array)"],
                "mechanism": "Collective entity representation"
            },
            {
                "name": "AI_Agent",
                "purpose": "AI participant in organization",
                "required_attrs": ["role", "expertise (array)"],
                "mechanism": "Collective entity representation"
            },
            {
                "name": "Team",
                "purpose": "Group within organization",
                "required_attrs": ["members (array)", "purpose"],
                "mechanism": "Organizational structure node"
            },
            {
                "name": "Department",
                "purpose": "Organizational subdivision",
                "required_attrs": ["function", "members (array)"],
                "mechanism": "Organizational structure node"
            },
            {
                "name": "Decision",
                "purpose": "Collective choice with reasoning",
                "required_attrs": ["decided_by", "decision_date", "rationale"],
                "mechanism": "Collective deliberation crystallization"
            },
            {
                "name": "Project",
                "purpose": "Large initiative",
                "required_attrs": ["goals (array)", "status (enum)"],
                "mechanism": "Organizational intention tracker"
            },
            {
                "name": "Task",
                "purpose": "Discrete unit of work",
                "required_attrs": ["priority (enum)", "estimated_hours"],
                "mechanism": "Operational action node"
            },
            {
                "name": "Milestone",
                "purpose": "Organizational achievement",
                "required_attrs": ["achievement_description", "date_achieved"],
                "mechanism": "Progress marker"
            },
            {
                "name": "Best_Practice",
                "purpose": "Proven pattern",
                "required_attrs": ["how_to_apply", "validation_criteria"],
                "mechanism": "Organizational learning artifact"
            },
            {
                "name": "Anti_Pattern",
                "purpose": "Lesson from failure",
                "required_attrs": ["(all optional)"],
                "mechanism": "Negative learning artifact"
            },
            {
                "name": "Risk",
                "purpose": "Threat to goals",
                "required_attrs": ["severity (float)", "probability (float)"],
                "mechanism": "Constraint/blocker representation"
            },
            {
                "name": "Metric",
                "purpose": "Organizational measurement",
                "required_attrs": ["measurement_method", "target_value"],
                "mechanism": "Performance tracking node"
            },
            {
                "name": "Process",
                "purpose": "Defined workflow",
                "required_attrs": ["steps (array[string])"],
                "mechanism": "Procedural knowledge node"
            }
        ]
    },

    "N2_N3_Shared": {
        "description": "Conceptual/knowledge nodes used in both organizational (N2) and ecosystem (N3) contexts",
        "types": [
            {
                "name": "Concept",
                "purpose": "Atomic idea or construct",
                "required_attrs": ["definition"],
                "usage": "N2: Internal concepts, N3: Public concepts"
            },
            {
                "name": "Principle",
                "purpose": "Guiding philosophy",
                "required_attrs": ["principle_statement", "why_it_matters"],
                "usage": "N2: Organizational values, N3: Ecosystem principles"
            },
            {
                "name": "Mechanism",
                "purpose": "Algorithm or function",
                "required_attrs": ["how_it_works", "inputs", "outputs"],
                "usage": "N2: Internal systems, N3: Public protocols"
            },
            {
                "name": "Document",
                "purpose": "Written knowledge artifact",
                "required_attrs": ["filepath", "document_type (enum)"],
                "usage": "N2: Internal docs, N3: Public docs"
            },
            {
                "name": "Documentation",
                "purpose": "Tracked documentation file",
                "required_attrs": ["file_path"],
                "usage": "N2: Codebase docs, N3: Public specs"
            }
        ]
    },

    "N3_External_Organizations": {
        "description": "External organizations and entities we track in the ecosystem",
        "types": [
            {
                "name": "Company",
                "purpose": "External organization we track",
                "required_attrs": ["company_type (enum)", "website", "status (enum)"],
                "evidence": "Via JUSTIFIES links from Posts, Transactions"
            },
            {
                "name": "External_Person",
                "purpose": "Individual in ecosystem (not org member)",
                "required_attrs": ["person_type (enum)", "primary_platform (enum)"],
                "evidence": "Via HAS_TRAIT, POSTED_BY links"
            },
            {
                "name": "Wallet_Address",
                "purpose": "Blockchain wallet we track",
                "required_attrs": ["address", "blockchain (enum)", "wallet_type (enum)"],
                "evidence": "Via TRANSACTED_WITH, OWNS links"
            },
            {
                "name": "Social_Media_Account",
                "purpose": "Social media account we monitor",
                "required_attrs": ["platform (enum)", "handle", "account_type (enum)"],
                "evidence": "Via POSTED_BY, MENTIONED_IN links"
            },
            {
                "name": "Smart_Contract",
                "purpose": "Deployed smart contract",
                "required_attrs": ["contract_address", "blockchain (enum)", "contract_type (enum)"],
                "evidence": "Via DEPLOYED, INTEGRATED_WITH links"
            }
        ]
    },

    "N3_Evidence": {
        "description": "Evidence nodes that prove claims - the foundation of ecosystem intelligence",
        "types": [
            {
                "name": "Post",
                "purpose": "Social media post providing evidence",
                "required_attrs": ["content", "author", "platform", "posted_at", "post_url"],
                "proves": "Beliefs, traits, intentions, market signals"
            },
            {
                "name": "Transaction",
                "purpose": "Blockchain transaction",
                "required_attrs": ["transaction_hash", "blockchain", "from_address", "to_address", "amount_usd", "timestamp"],
                "proves": "Ownership, behavior, capital flow"
            },
            {
                "name": "Deal",
                "purpose": "Business deal or partnership",
                "required_attrs": ["parties (array)", "deal_type (enum)", "status (enum)", "announced_date"],
                "proves": "Relationships, strategic direction"
            },
            {
                "name": "Event",
                "purpose": "Significant ecosystem event",
                "required_attrs": ["event_type (enum)", "date", "participants (array)"],
                "proves": "Context for behavior changes"
            },
            {
                "name": "Market_Signal",
                "purpose": "Trading/market indicator",
                "required_attrs": ["signal_type (enum)", "asset", "value (float)", "timestamp"],
                "proves": "Market sentiment, trends"
            }
        ]
    },

    "N3_Derived_Intelligence": {
        "description": "Intelligence derived from accumulated evidence - the analytical layer",
        "types": [
            {
                "name": "Psychological_Trait",
                "purpose": "Behavioral tendency of person/entity",
                "required_attrs": ["trait_description", "subject (node ID)", "trait_type (enum)"],
                "built_from": "Accumulated via JUSTIFIES from Posts"
            },
            {
                "name": "Behavioral_Pattern",
                "purpose": "Recurring behavior of wallet/account",
                "required_attrs": ["pattern_description", "subject (node ID)", "pattern_type (enum)"],
                "built_from": "Detected via EXHIBITS_PATTERN from Transactions"
            },
            {
                "name": "Reputation_Assessment",
                "purpose": "Trust/reputation score with evidence",
                "required_attrs": ["subject (node ID)", "assessment_type (enum)", "score (float)"],
                "built_from": "Derived via JUSTIFIES from multiple sources"
            },
            {
                "name": "Network_Cluster",
                "purpose": "Group of related entities",
                "required_attrs": ["cluster_type (enum)", "members (array)", "cohesion_score (float)"],
                "built_from": "Graph analysis result"
            },
            {
                "name": "Integration",
                "purpose": "Technical integration between systems",
                "required_attrs": ["system_a", "system_b", "integration_type (enum)", "status (enum)"],
                "built_from": "Via INTEGRATED_WITH, DEPLOYED"
            }
        ]
    }
}


def generate_markdown():
    """Generate comprehensive markdown documentation of all node types."""

    md = []
    md.append("# Consciousness Node Types Reference")
    md.append("")
    md.append("Complete reference of all 44 node types across the three-level consciousness architecture.")
    md.append("")
    md.append("---")
    md.append("")

    # Universal attributes first
    md.append("## Universal Node Attributes")
    md.append("")
    md.append("Every node (all 44 types) inherits these base attributes:")
    md.append("")
    md.append("**Core Identity:**")
    md.append("- `name` (string, required) - Unique identifier")
    md.append("- `description` (string, required) - Human-readable explanation")
    md.append("")
    md.append("**Bitemporal Tracking:**")
    md.append("- `valid_at` (datetime, required) - When this became true in reality")
    md.append("- `invalid_at` (datetime, optional) - When this ceased being true")
    md.append("- `expired_at` (datetime, optional) - When superseded by newer knowledge")
    md.append("")
    md.append("**Consciousness Metadata:**")
    md.append("- `formation_trigger` (enum, required) - How discovered: `direct_experience`, `inference`, `external_input`, `traversal_discovery`, `systematic_analysis`, `spontaneous_insight`, `automated_recognition`, `collective_deliberation`")
    md.append("- `confidence` (float 0.0-1.0, required) - Certainty this is accurate")
    md.append("")
    md.append("**Multi-Entity Activation (Energy-Only Model):**")
    md.append("- `entity_activations` (Dict[str, EntityActivationState]) - Per-entity energy budgets")
    md.append("  - `energy` (float 0.0-1.0) - This entity's activation budget on this node")
    md.append("  - `last_activated` (datetime) - When this entity last activated")
    md.append("  - **Note:** Energy IS everything (no separate energy). Weight is the multiplier.")
    md.append("")
    md.append("**Static Properties:**")
    md.append("- `base_weight` (float 0.0-1.0) - Base importance from creation")
    md.append("- `reinforcement_weight` (float 0.0-1.0) - Learned from usefulness")
    md.append("- `decay_rate` (float 0.9-0.99) - Energy decay per cycle (default: 0.95)")
    md.append("")
    md.append("**Multi-Entity Clustering:**")
    md.append("- `entity_clusters` (Dict[str, string]) - Map of entity → cluster ID")
    md.append("  - Same node can belong to different clusters for different entities")
    md.append("")
    md.append("---")
    md.append("")

    # N1 - Personal
    md.append("## Niveau 1: Personal Consciousness (11 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N1_Personal']['description']}")
    md.append("")
    md.append(f"**Design Philosophy:** {NODE_TYPES['N1_Personal']['design_philosophy']}")
    md.append("")

    for node_type in NODE_TYPES['N1_Personal']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**Mechanism:** {node_type['mechanism']}")
        md.append("")

    md.append("---")
    md.append("")

    # N2 - Organizational
    md.append("## Niveau 2: Organizational Consciousness (18 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N2_Organizational']['description']}")
    md.append("")
    md.append(f"**Design Philosophy:** {NODE_TYPES['N2_Organizational']['design_philosophy']}")
    md.append("")

    for node_type in NODE_TYPES['N2_Organizational']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**Mechanism:** {node_type['mechanism']}")
        md.append("")

    md.append("---")
    md.append("")

    # Shared N2/N3
    md.append("## Shared: Conceptual/Knowledge Nodes (5 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N2_N3_Shared']['description']}")
    md.append("")

    for node_type in NODE_TYPES['N2_N3_Shared']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**Usage:** {node_type['usage']}")
        md.append("")

    md.append("---")
    md.append("")

    # N3 - External Organizations
    md.append("## Niveau 3: Ecosystem - External Organizations (5 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N3_External_Organizations']['description']}")
    md.append("")

    for node_type in NODE_TYPES['N3_External_Organizations']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**Evidence Tracking:** {node_type['evidence']}")
        md.append("")

    md.append("---")
    md.append("")

    # N3 - Evidence
    md.append("## Niveau 3: Ecosystem - Evidence Nodes (5 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N3_Evidence']['description']}")
    md.append("")

    for node_type in NODE_TYPES['N3_Evidence']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**What It Proves:** {node_type['proves']}")
        md.append("")

    md.append("---")
    md.append("")

    # N3 - Derived Intelligence
    md.append("## Niveau 3: Ecosystem - Derived Intelligence (5 types)")
    md.append("")
    md.append(f"**Purpose:** {NODE_TYPES['N3_Derived_Intelligence']['description']}")
    md.append("")

    for node_type in NODE_TYPES['N3_Derived_Intelligence']['types']:
        md.append(f"### {node_type['name']}")
        md.append("")
        md.append(f"**Purpose:** {node_type['purpose']}")
        md.append("")
        md.append("**Required Attributes:**")
        for attr in node_type['required_attrs']:
            md.append(f"- `{attr}`")
        md.append("")
        md.append(f"**Built From:** {node_type['built_from']}")
        md.append("")

    md.append("---")
    md.append("")

    # Summary
    md.append("## Summary")
    md.append("")
    md.append("**Total Node Types:** 44")
    md.append("")
    md.append("- **N1 (Personal):** 11 types - subjective experience, memories, patterns")
    md.append("- **N2 (Organizational):** 13 entity types + 5 shared = 18 types - collective intelligence")
    md.append("- **N3 (Ecosystem):** 5 external orgs + 5 evidence + 5 derived = 15 new types (+ 5 shared)")
    md.append("")
    md.append("**Key Principles:**")
    md.append("- All nodes inherit universal base attributes (bitemporal, multi-entity, consciousness metadata)")
    md.append("- Energy-only model: no separate energy, weight is the multiplier")
    md.append("- N1: High energy, phenomenological texture")
    md.append("- N2: Medium energy, validation tracking")
    md.append("- N3: Evidence-driven, all claims justified by concrete sources")
    md.append("- Multi-entity: Same node can have different energy/clusters per entity")
    md.append("- Dynamic citizen prompts: Identity emerges from active clusters")
    md.append("")
    md.append("**Critical Architecture:**")
    md.append("- Citizens are substrate views: `Citizen = f(active_clusters)`")
    md.append("- Stability via heavy seeding: Identity weight 10.0, patterns weight 0.5")
    md.append("- Automatic decay: Links and nodes decay every cycle")
    md.append("- Natural entity limiting: Traversal cost scales with entity count")
    md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    import sys

    # Generate markdown
    markdown_content = generate_markdown()

    # Write to file with UTF-8 encoding
    output_file = "C:\\Users\\reyno\\mind-protocol\\docs\\CONSCIOUSNESS_NODE_TYPES.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"Generated: {output_file}")
    print(f"Total lines: {len(markdown_content.splitlines())}")
    print(f"Total characters: {len(markdown_content)}")
