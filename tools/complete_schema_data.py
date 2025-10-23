"""
Complete Schema Data - Single Source of Truth

Extracted from UNIFIED_SCHEMA_REFERENCE.md
This file contains ALL schema definitions for the Mind Protocol consciousness infrastructure.

Author: Felix "Ironhand"
Date: 2025-01-19
Source: UNIFIED_SCHEMA_REFERENCE.md
"""

# ============================================================================
# UNIVERSAL NODE ATTRIBUTES (BaseNode - inherited by ALL 44 node types)
# ============================================================================

UNIVERSAL_NODE_ATTRIBUTES = {
    "core_idsubentity": [
        {"name": "name", "type": "string", "required": True,
         "description": "Unique identifier for this node"},
        {"name": "description", "type": "string", "required": True,
         "description": "Human-readable explanation"},
        {"name": "node_type", "type": "string", "required": True,
         "description": "The specific node class name (auto-set)"}
    ],

    "bitemporal_tracking": [
        {"name": "valid_at", "type": "datetime", "required": True,
         "description": "When this fact became true in reality"},
        {"name": "invalid_at", "type": "datetime", "required": False,
         "description": "When this fact ceased being true (None = still valid)"},
        {"name": "created_at", "type": "datetime", "required": True,
         "description": "When we learned about this fact"},
        {"name": "expired_at", "type": "datetime", "required": False,
         "description": "When this knowledge was superseded (None = current)"}
    ],

    "consciousness_metadata": [
        {"name": "formation_trigger", "type": "enum", "required": True,
         "enum_values": ["direct_experience", "inference", "external_input",
                        "traversal_discovery", "systematic_analysis",
                        "spontaneous_insight", "automated_recognition",
                        "collective_deliberation"],
         "description": "How this node was discovered"},
        {"name": "confidence", "type": "float", "required": True, "range": [0.0, 1.0],
         "description": "Certainty this node is accurate"}
    ],

    "provenance": [
        {"name": "created_by", "type": "string", "required": False,
         "description": "Who/what created this node"},
        {"name": "substrate", "type": "enum", "required": False,
         "enum_values": ["personal", "organizational", "gemini_web", "external"],
         "description": "Where created"}
    ],

    "activation_energy": [
        {"name": "base_weight", "type": "float", "required": False, "range": [0.0, 1.0],
         "description": "Base importance from creation context"},
        {"name": "reinforcement_weight", "type": "float", "required": False, "range": [0.0, 1.0],
         "description": "Weight learned from usefulness evaluations"},
        {"name": "decay_rate", "type": "float", "required": False, "range": [0.9, 0.99],
         "description": "Energy decay per cycle (default: 0.95)"}
    ]
}

# ============================================================================
# UNIVERSAL LINK ATTRIBUTES (BaseRelation - inherited by ALL 38 link types)
# ============================================================================

UNIVERSAL_LINK_ATTRIBUTES = {
    "consciousness_metadata": [
        {"name": "goal", "type": "string", "required": True,
         "description": "Why this link exists"},
        {"name": "mindstate", "type": "string", "required": True,
         "description": "Internal state when forming this link"},
        {"name": "energy", "type": "float", "required": True, "range": [0.0, 1.0],
         "description": "Emotional intensity/urgency"},
        {"name": "confidence", "type": "float", "required": True, "range": [0.0, 1.0],
         "description": "Logical certainty in this connection"},
        {"name": "formation_trigger", "type": "enum", "required": True,
         "enum_values": ["direct_experience", "inference", "external_input",
                        "traversal_discovery", "systematic_analysis",
                        "spontaneous_insight", "automated_recognition",
                        "collective_deliberation"],
         "description": "How this link was discovered"}
    ],

    "bitemporal_tracking": [
        {"name": "valid_at", "type": "datetime", "required": True,
         "description": "When this link became true"},
        {"name": "invalid_at", "type": "datetime", "required": False,
         "description": "When link ceased being true"},
        {"name": "created_at", "type": "datetime", "required": True,
         "description": "When we learned about this link"},
        {"name": "expired_at", "type": "datetime", "required": False,
         "description": "When this link knowledge was superseded"}
    ],

    "optional_rich_metadata": [
        {"name": "struggle", "type": "string", "required": False,
         "description": "Tension this link creates/resolves"},
        {"name": "validation_status", "type": "enum", "required": False,
         "enum_values": ["theoretical", "experiential", "tested", "proven"],
         "description": "Quality progression"},
        {"name": "alternatives_considered", "type": "array", "required": False,
         "description": "Other interpretations evaluated"},
        {"name": "created_by", "type": "string", "required": False,
         "description": "Who/what created this link"},
        {"name": "substrate", "type": "enum", "required": False,
         "enum_values": ["personal", "organizational", "gemini_web", "external"],
         "description": "Where created"}
    ]
}

# ============================================================================
# LINK TYPE FIELD SPECIFICATIONS
# ============================================================================

LINK_FIELD_SPECS = {
    # Structural Relationships
    "BLOCKS": {
        "level": "shared", "category": "structural",
        "description": "Prevents progress or blocks execution",
        "required": [
            {"name": "severity", "type": "enum",
             "enum_values": ["absolute", "strong", "partial"],
             "description": "How completely this blocks progress"},
            {"name": "blocking_condition", "type": "string",
             "description": "What condition must change to unblock"},
            {"name": "felt_as", "type": "string",
             "description": "Emotional/phenomenological experience of being blocked"},
            {"name": "consciousness_impact", "type": "string",
             "description": "How this affects consciousness state"}
        ],
        "optional": []
    },

    "ENABLES": {
        "level": "shared", "category": "structural",
        "description": "Makes something possible or facilitates it",
        "required": [
            {"name": "enabling_type", "type": "enum",
             "enum_values": ["prerequisite", "facilitator", "amplifier", "catalyst", "permission"],
             "description": "How this enables the target"},
            {"name": "degree_of_necessity", "type": "enum",
             "enum_values": ["required", "helpful", "optional"],
             "description": "How necessary is this enabler"},
            {"name": "felt_as", "type": "string",
             "description": "Phenomenological experience of enablement"},
            {"name": "without_this", "type": "string",
             "description": "What happens if this enabler is removed"}
        ],
        "optional": []
    },

    "EXTENDS": {
        "level": "shared", "category": "structural",
        "description": "Builds upon foundation or extends functionality",
        "required": [
            {"name": "extension_type", "type": "enum",
             "enum_values": ["specialization", "generalization", "elaboration", "application"],
             "description": "How extension relates to base"},
            {"name": "what_is_added", "type": "string",
             "description": "What the extension adds to the base"},
            {"name": "maintains_compatibility", "type": "boolean",
             "description": "Whether extension remains compatible with base"},
            {"name": "composition_ratio", "type": "float", "range": [0.0, 1.0],
             "description": "How much is new vs inherited (0=all base, 1=all new)"}
        ],
        "optional": []
    },

    "RELATES_TO": {
        "level": "shared", "category": "structural",
        "description": "Generic connection when specific type unclear",
        "required": [
            {"name": "relationship_strength", "type": "enum",
             "enum_values": ["strong", "moderate", "weak", "exploratory"],
             "description": "Strength of relationship"},
            {"name": "needs_refinement", "type": "boolean",
             "description": "Should this be replaced with more specific link type?"},
            {"name": "refinement_candidates", "type": "array",
             "description": "Potential more specific link types to use"}
        ],
        "optional": []
    },

    # Dependency & Requirements
    "REQUIRES": {
        "level": "shared", "category": "dependency",
        "description": "Necessary conditions or prerequisites",
        "required": [
            {"name": "requirement_criticality", "type": "enum",
             "enum_values": ["blocking", "important", "optional"],
             "description": "How critical is this requirement"},
            {"name": "temporal_relationship", "type": "enum",
             "enum_values": ["must_precede", "should_precede", "concurrent_ok"],
             "description": "Temporal ordering constraint"},
            {"name": "failure_mode", "type": "string",
             "description": "What happens if requirement not met"},
            {"name": "verification_method", "type": "string",
             "description": "How to verify requirement is satisfied"}
        ],
        "optional": []
    },

    # Evidence & Justification
    "JUSTIFIES": {
        "level": "shared", "category": "evidence",
        "description": "Evidence supporting practice/decision/claim",
        "required": [
            {"name": "justification_type", "type": "enum",
             "enum_values": ["empirical_evidence", "lived_experience", "logical_proof",
                           "ethical_reasoning", "pragmatic_value"],
             "description": "Type of justification"},
            {"name": "justification_strength", "type": "enum",
             "enum_values": ["proves", "strongly_supports", "moderately_supports",
                           "suggests", "weakly_supports"],
             "description": "Strength of justification"},
            {"name": "felt_as", "type": "string",
             "description": "Phenomenological experience of justification"},
            {"name": "counter_arguments_exist", "type": "boolean",
             "description": "Are there known counter-arguments?"}
        ],
        "optional": []
    },

    "REFUTES": {
        "level": "shared", "category": "evidence",
        "description": "Disproves or invalidates claim",
        "required": [],
        "optional": []
    },

    # Documentation & Implementation (5 types)
    "DOCUMENTS": {
        "level": "shared", "category": "documentation",
        "description": "Written record of implementation or decision",
        "required": [],
        "optional": [
            {"name": "documentation_type", "type": "string",
             "description": "Type of documentation (spec, guide, reference, etc.)"}
        ]
    },

    "DOCUMENTED_BY": {
        "level": "shared", "category": "documentation",
        "description": "Implementation documented by this artifact",
        "required": [],
        "optional": []
    },

    "SUPERSEDES": {
        "level": "shared", "category": "documentation",
        "description": "This replaces older version",
        "required": [],
        "optional": []
    },

    "IMPLEMENTS": {
        "level": "shared", "category": "documentation",
        "description": "Putting pattern or best practice into reality",
        "required": [],
        "optional": []
    },

    "CREATES": {
        "level": "shared", "category": "documentation",
        "description": "Task will produce this artifact when completed",
        "required": [],
        "optional": []
    },

    # Organizational Coordination (5 types)
    "ASSIGNED_TO": {
        "level": "shared", "category": "organizational",
        "description": "Task ownership or responsibility",
        "required": [],
        "optional": []
    },

    "COLLABORATES_WITH": {
        "level": "shared", "category": "organizational",
        "description": "Working partnership between subentities",
        "required": [],
        "optional": []
    },

    "CONTRIBUTES_TO": {
        "level": "shared", "category": "organizational",
        "description": "Work supporting larger initiative",
        "required": [],
        "optional": []
    },

    "MEASURES": {
        "level": "shared", "category": "organizational",
        "description": "Quantifies performance or progress",
        "required": [],
        "optional": []
    },

    "THREATENS": {
        "level": "shared", "category": "organizational",
        "description": "Danger or risk to goal/project",
        "required": [],
        "optional": []
    },

    # Activation & Triggering (3 types)
    "ACTIVATES": {
        "level": "n1", "category": "activation",
        "description": "Trigger awakens subentity coalition",
        "required": [],
        "optional": []
    },

    "TRIGGERED_BY": {
        "level": "n1", "category": "activation",
        "description": "What caused memory/pattern to activate",
        "required": [],
        "optional": []
    },

    "SUPPRESSES": {
        "level": "n1", "category": "activation",
        "description": "What blocks subentity activation",
        "required": [],
        "optional": []
    },

    # Learning & Growth (2 types)
    "LEARNED_FROM": {
        "level": "n1", "category": "learning",
        "description": "Personal pattern extracted from experience",
        "required": [],
        "optional": []
    },

    "DEEPENED_WITH": {
        "level": "n1", "category": "learning",
        "description": "Relationship growth through experience",
        "required": [],
        "optional": []
    },

    # Value & Direction (1 type)
    "DRIVES_TOWARD": {
        "level": "n1", "category": "value",
        "description": "Value pushing toward goal",
        "required": [],
        "optional": []
    },
}

# ============================================================================
# NODE TYPE SCHEMAS
# ============================================================================

NODE_TYPE_SCHEMAS = {
    # N1 (Personal Consciousness) - 11 Types
    "Memory": {
        "level": "n1", "category": "personal",
        "description": "Specific experience or moment",
        "required": [
            {"name": "timestamp", "type": "datetime",
             "description": "When this memory occurred"},
            {"name": "participants", "type": "array",
             "description": "Who was involved"}
        ],
        "optional": []
    },

    "Conversation": {
        "level": "n1", "category": "personal",
        "description": "Exchange with explicit turn structure",
        "required": [
            {"name": "timestamp", "type": "datetime",
             "description": "When conversation occurred"},
            {"name": "with_person", "type": "string",
             "description": "Who I conversed with"},
            {"name": "turn_count", "type": "integer",
             "description": "Number of turns in conversation"}
        ],
        "optional": []
    },

    "Person": {
        "level": "n1", "category": "personal",
        "description": "Individual I have relationship with",
        "required": [
            {"name": "relationship_type", "type": "enum",
             "enum_values": ["friend", "colleague", "mentor", "family", "acquaintance"],
             "description": "Type of relationship"}
        ],
        "optional": []
    },

    "Relationship": {
        "level": "n1", "category": "personal",
        "description": "Connection dynamics and evolution",
        "required": [
            {"name": "with_person", "type": "string",
             "description": "Who this relationship is with"},
            {"name": "relationship_quality", "type": "float", "range": [0.0, 1.0],
             "description": "Quality of relationship"}
        ],
        "optional": []
    },

    "Personal_Goal": {
        "level": "n1", "category": "personal",
        "description": "Individual aspiration",
        "required": [
            {"name": "goal_description", "type": "string",
             "description": "What the goal is"},
            {"name": "why_it_matters", "type": "string",
             "description": "Why this goal is important to me"}
        ],
        "optional": []
    },

    "Personal_Value": {
        "level": "n1", "category": "personal",
        "description": "What matters to me individually",
        "required": [
            {"name": "value_statement", "type": "string",
             "description": "The value itself"},
            {"name": "why_i_hold_it", "type": "string",
             "description": "Why I hold this value"}
        ],
        "optional": []
    },

    "Personal_Pattern": {
        "level": "n1", "category": "personal",
        "description": "Habit or recurring response",
        "required": [
            {"name": "behavior_description", "type": "string",
             "description": "Description of the pattern"},
            {"name": "frequency", "type": "enum",
             "enum_values": ["constant", "frequent", "occasional", "rare"],
             "description": "How often this pattern occurs"}
        ],
        "optional": []
    },

    "Realization": {
        "level": "n1", "category": "personal",
        "description": "Insight or comprehension shift",
        "required": [
            {"name": "what_i_realized", "type": "string",
             "description": "The insight itself"},
            {"name": "context_when_discovered", "type": "string",
             "description": "Context when this realization occurred"}
        ],
        "optional": []
    },

    "Wound": {
        "level": "n1", "category": "personal",
        "description": "Personal scar or trauma",
        "required": [
            {"name": "what_happened", "type": "string",
             "description": "What caused the wound"},
            {"name": "emotional_impact", "type": "string",
             "description": "How this affects me emotionally"}
        ],
        "optional": []
    },

    "Coping_Mechanism": {
        "level": "n1", "category": "personal",
        "description": "Response to stress",
        "required": [
            {"name": "mechanism_description", "type": "string",
             "description": "How I cope"},
            {"name": "what_it_protects_from", "type": "string",
             "description": "What this mechanism defends against"}
        ],
        "optional": []
    },

    "Trigger": {
        "level": "n1", "category": "personal",
        "description": "What awakens subentity coalitions",
        "required": [
            {"name": "stimulus_description", "type": "string",
             "description": "What triggers activation"},
            {"name": "activated_entities", "type": "array",
             "description": "Which subentities this triggers"}
        ],
        "optional": []
    },

    # N2 (Organizational) - 18 Types
    "Human": {
        "level": "n2", "category": "organizational",
        "description": "Human participant in organization",
        "required": [
            {"name": "role", "type": "string",
             "description": "Role in organization"},
            {"name": "expertise", "type": "array",
             "description": "Areas of expertise"}
        ],
        "optional": []
    },

    "AI_Agent": {
        "level": "n2", "category": "organizational",
        "description": "AI participant in organization",
        "required": [
            {"name": "role", "type": "string",
             "description": "Role in organization"},
            {"name": "expertise", "type": "array",
             "description": "Areas of expertise"}
        ],
        "optional": []
    },

    "Team": {
        "level": "n2", "category": "organizational",
        "description": "Group within organization",
        "required": [
            {"name": "members", "type": "array",
             "description": "Team members"},
            {"name": "purpose", "type": "string",
             "description": "Team purpose"}
        ],
        "optional": []
    },

    "Department": {
        "level": "n2", "category": "organizational",
        "description": "Organizational subdivision",
        "required": [
            {"name": "function", "type": "string",
             "description": "Department function"},
            {"name": "members", "type": "array",
             "description": "Department members"}
        ],
        "optional": []
    },

    "Decision": {
        "level": "n2", "category": "organizational",
        "description": "Collective choice with reasoning",
        "required": [
            {"name": "decided_by", "type": "string",
             "description": "Who made the decision"},
            {"name": "decision_date", "type": "datetime",
             "description": "When decision was made"},
            {"name": "rationale", "type": "string",
             "description": "Why this decision was made"}
        ],
        "optional": []
    },

    "Project": {
        "level": "n2", "category": "organizational",
        "description": "Large initiative",
        "required": [
            {"name": "goals", "type": "array",
             "description": "Project goals"},
            {"name": "status", "type": "enum",
             "enum_values": ["planning", "active", "completed", "cancelled"],
             "description": "Current status"}
        ],
        "optional": []
    },

    "Task": {
        "level": "n2", "category": "organizational",
        "description": "Discrete unit of work",
        "required": [
            {"name": "priority", "type": "enum",
             "enum_values": ["critical", "high", "medium", "low"],
             "description": "Task priority"},
            {"name": "estimated_hours", "type": "float",
             "description": "Estimated time to complete"}
        ],
        "optional": []
    },

    "Milestone": {
        "level": "n2", "category": "organizational",
        "description": "Organizational achievement",
        "required": [
            {"name": "achievement_description", "type": "string",
             "description": "What was achieved"},
            {"name": "date_achieved", "type": "datetime",
             "description": "When it was achieved"}
        ],
        "optional": []
    },

    "Best_Practice": {
        "level": "n2", "category": "organizational",
        "description": "Proven pattern",
        "required": [
            {"name": "how_to_apply", "type": "array",
             "description": "How to apply this practice (list of steps)"},
            {"name": "validation_criteria", "type": "string",
             "description": "How to verify it works"}
        ],
        "optional": []
    },

    "Anti_Pattern": {
        "level": "n2", "category": "organizational",
        "description": "Lesson from failure",
        "required": [],
        "optional": []
    },

    "Risk": {
        "level": "n2", "category": "organizational",
        "description": "Threat to goals",
        "required": [
            {"name": "severity", "type": "float", "range": [0.0, 1.0],
             "description": "How severe is this risk"},
            {"name": "probability", "type": "float", "range": [0.0, 1.0],
             "description": "Likelihood of occurrence"}
        ],
        "optional": []
    },

    "Metric": {
        "level": "n2", "category": "organizational",
        "description": "Organizational measurement",
        "required": [
            {"name": "measurement_method", "type": "string",
             "description": "How to measure this"},
            {"name": "target_value", "type": "string",
             "description": "Target value"}
        ],
        "optional": []
    },

    "Process": {
        "level": "n2", "category": "organizational",
        "description": "Defined workflow",
        "required": [
            {"name": "steps", "type": "array",
             "description": "Process steps"}
        ],
        "optional": []
    },

    "Code": {
        "level": "n2", "category": "organizational",
        "description": "Code file tracked in consciousness",
        "required": [
            {"name": "file_path", "type": "string",
             "description": "Path to the code file"},
            {"name": "language", "type": "enum",
             "enum_values": ["python", "typescript", "javascript", "sql", "bash", "rust", "go", "other"],
             "description": "Programming language"},
            {"name": "purpose", "type": "string",
             "description": "What this code does"}
        ],
        "optional": [
            {"name": "status", "type": "enum",
             "enum_values": ["active", "deprecated", "experimental"],
             "description": "Current status of the code"},
            {"name": "complexity", "type": "enum",
             "enum_values": ["simple", "moderate", "complex"],
             "description": "Code complexity level"},
            {"name": "dependencies", "type": "array",
             "description": "What this code depends on"}
        ]
    },

    # Conceptual/Knowledge (5 types - Shared N2/N3)
    "Concept": {
        "level": "shared", "category": "knowledge",
        "description": "Atomic idea or construct",
        "required": [
            {"name": "definition", "type": "string",
             "description": "Definition of the concept"}
        ],
        "optional": []
    },

    "Principle": {
        "level": "shared", "category": "knowledge",
        "description": "Guiding philosophy",
        "required": [
            {"name": "principle_statement", "type": "string",
             "description": "The principle itself"},
            {"name": "why_it_matters", "type": "string",
             "description": "Why this principle is important"}
        ],
        "optional": []
    },

    "Mechanism": {
        "level": "shared", "category": "knowledge",
        "description": "Algorithm or function",
        "required": [
            {"name": "how_it_works", "type": "string",
             "description": "How the mechanism operates"},
            {"name": "inputs", "type": "string",
             "description": "What inputs it takes"},
            {"name": "outputs", "type": "string",
             "description": "What outputs it produces"}
        ],
        "optional": []
    },

    "Document": {
        "level": "shared", "category": "knowledge",
        "description": "Written knowledge artifact",
        "required": [
            {"name": "filepath", "type": "string",
             "description": "Path to document"},
            {"name": "document_type", "type": "enum",
             "enum_values": ["spec", "guide", "reference", "plan", "report"],
             "description": "Type of document"}
        ],
        "optional": []
    },

    "Documentation": {
        "level": "shared", "category": "knowledge",
        "description": "Tracked documentation file",
        "required": [
            {"name": "file_path", "type": "string",
             "description": "Path to documentation file"}
        ],
        "optional": []
    },

    # N3 (Ecosystem Intelligence) - 15 Types
    # Category 1: External Organizations & Subentities
    "Company": {
        "level": "n3", "category": "ecosystem",
        "description": "External organization we track",
        "required": [
            {"name": "company_type", "type": "enum",
             "enum_values": ["startup", "enterprise", "dao", "protocol"],
             "description": "Type of company"},
            {"name": "website", "type": "string",
             "description": "Company website"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "acquired", "defunct"],
             "description": "Current status"}
        ],
        "optional": []
    },

    "External_Person": {
        "level": "n3", "category": "ecosystem",
        "description": "Individual in ecosystem (not org member)",
        "required": [
            {"name": "person_type", "type": "enum",
             "enum_values": ["founder", "investor", "influencer", "developer"],
             "description": "Type of person"},
            {"name": "primary_platform", "type": "enum",
             "enum_values": ["twitter", "linkedin", "github"],
             "description": "Primary social platform"}
        ],
        "optional": []
    },

    "Wallet_Address": {
        "level": "n3", "category": "ecosystem",
        "description": "Blockchain wallet we track",
        "required": [
            {"name": "address", "type": "string",
             "description": "Wallet address"},
            {"name": "blockchain", "type": "enum",
             "enum_values": ["ethereum", "solana", "bitcoin"],
             "description": "Which blockchain"},
            {"name": "wallet_type", "type": "enum",
             "enum_values": ["eoa", "contract", "multisig"],
             "description": "Type of wallet"}
        ],
        "optional": []
    },

    "Social_Media_Account": {
        "level": "n3", "category": "ecosystem",
        "description": "Social media account we monitor",
        "required": [
            {"name": "platform", "type": "enum",
             "enum_values": ["twitter", "linkedin", "github", "farcaster"],
             "description": "Platform"},
            {"name": "handle", "type": "string",
             "description": "Account handle"},
            {"name": "account_type", "type": "enum",
             "enum_values": ["personal", "company", "project"],
             "description": "Type of account"}
        ],
        "optional": []
    },

    "Smart_Contract": {
        "level": "n3", "category": "ecosystem",
        "description": "Deployed smart contract",
        "required": [
            {"name": "contract_address", "type": "string",
             "description": "Contract address"},
            {"name": "blockchain", "type": "enum",
             "enum_values": ["ethereum", "solana"],
             "description": "Which blockchain"},
            {"name": "contract_type", "type": "enum",
             "enum_values": ["token", "defi", "nft", "governance"],
             "description": "Type of contract"}
        ],
        "optional": []
    },

    # Category 2: Evidence Nodes
    "Post": {
        "level": "n3", "category": "evidence",
        "description": "Social media post providing evidence",
        "required": [
            {"name": "content", "type": "string",
             "description": "Post content"},
            {"name": "author", "type": "string",
             "description": "Who posted it"},
            {"name": "platform", "type": "enum",
             "enum_values": ["twitter", "linkedin", "farcaster"],
             "description": "Which platform"},
            {"name": "posted_at", "type": "datetime",
             "description": "When it was posted"},
            {"name": "post_url", "type": "string",
             "description": "URL to post"}
        ],
        "optional": []
    },

    "Transaction": {
        "level": "n3", "category": "evidence",
        "description": "Blockchain transaction",
        "required": [
            {"name": "transaction_hash", "type": "string",
             "description": "Transaction hash"},
            {"name": "blockchain", "type": "enum",
             "enum_values": ["ethereum", "solana", "bitcoin"],
             "description": "Which blockchain"},
            {"name": "from_address", "type": "string",
             "description": "Source address"},
            {"name": "to_address", "type": "string",
             "description": "Destination address"},
            {"name": "amount_usd", "type": "float",
             "description": "Transaction value in USD"},
            {"name": "timestamp", "type": "datetime",
             "description": "When transaction occurred"}
        ],
        "optional": []
    },

    "Deal": {
        "level": "n3", "category": "evidence",
        "description": "Business deal or partnership",
        "required": [
            {"name": "parties", "type": "array",
             "description": "Parties involved"},
            {"name": "deal_type", "type": "enum",
             "enum_values": ["investment", "partnership", "acquisition"],
             "description": "Type of deal"},
            {"name": "status", "type": "enum",
             "enum_values": ["announced", "completed", "cancelled"],
             "description": "Deal status"},
            {"name": "announced_date", "type": "datetime",
             "description": "When announced"}
        ],
        "optional": []
    },

    "Event": {
        "level": "n3", "category": "evidence",
        "description": "Significant ecosystem event",
        "required": [
            {"name": "event_type", "type": "enum",
             "enum_values": ["launch", "hack", "upgrade", "governance"],
             "description": "Type of event"},
            {"name": "date", "type": "datetime",
             "description": "When it occurred"},
            {"name": "participants", "type": "array",
             "description": "Who was involved"}
        ],
        "optional": []
    },

    "Market_Signal": {
        "level": "n3", "category": "evidence",
        "description": "Trading/market indicator",
        "required": [
            {"name": "signal_type", "type": "enum",
             "enum_values": ["price", "volume", "sentiment"],
             "description": "Type of signal"},
            {"name": "asset", "type": "string",
             "description": "Which asset"},
            {"name": "value", "type": "float",
             "description": "Signal value"},
            {"name": "timestamp", "type": "datetime",
             "description": "When measured"}
        ],
        "optional": []
    },

    # Category 3: Derived Intelligence
    "Psychological_Trait": {
        "level": "n3", "category": "derived",
        "description": "Behavioral tendency of person/subentity",
        "required": [
            {"name": "trait_description", "type": "string",
             "description": "Description of the trait"},
            {"name": "subject", "type": "string",
             "description": "Who has this trait (node ID)"},
            {"name": "trait_type", "type": "enum",
             "enum_values": ["bullish", "bearish", "risk-averse", "aggressive"],
             "description": "Type of trait"}
        ],
        "optional": []
    },

    "Behavioral_Pattern": {
        "level": "n3", "category": "derived",
        "description": "Recurring behavior of wallet/account",
        "required": [
            {"name": "pattern_description", "type": "string",
             "description": "Description of the pattern"},
            {"name": "subject", "type": "string",
             "description": "Who exhibits this (node ID)"},
            {"name": "pattern_type", "type": "enum",
             "enum_values": ["trading", "social", "technical"],
             "description": "Type of pattern"}
        ],
        "optional": []
    },

    "Reputation_Assessment": {
        "level": "n3", "category": "derived",
        "description": "Trust/reputation score with evidence",
        "required": [
            {"name": "subject", "type": "string",
             "description": "Who is being assessed (node ID)"},
            {"name": "assessment_type", "type": "enum",
             "enum_values": ["credibility", "expertise", "trustworthiness"],
             "description": "Type of assessment"},
            {"name": "score", "type": "float", "range": [0.0, 1.0],
             "description": "Assessment score"}
        ],
        "optional": []
    },

    "Network_Cluster": {
        "level": "n3", "category": "derived",
        "description": "Group of related subentities",
        "required": [
            {"name": "cluster_type", "type": "enum",
             "enum_values": ["social", "financial", "technical"],
             "description": "Type of cluster"},
            {"name": "members", "type": "array",
             "description": "Cluster members"},
            {"name": "cohesion_score", "type": "float", "range": [0.0, 1.0],
             "description": "How cohesive the cluster is"}
        ],
        "optional": []
    },

    "Integration": {
        "level": "n3", "category": "derived",
        "description": "Technical integration between systems",
        "required": [
            {"name": "system_a", "type": "string",
             "description": "First system"},
            {"name": "system_b", "type": "string",
             "description": "Second system"},
            {"name": "integration_type", "type": "enum",
             "enum_values": ["api", "bridge", "protocol"],
             "description": "Type of integration"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "deprecated", "planned"],
             "description": "Integration status"}
        ],
        "optional": []
    },
}
