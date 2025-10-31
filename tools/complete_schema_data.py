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
    ],

    "privacy_governance": [
        {"name": "visibility", "type": "enum", "required": False,
         "enum_values": ["public", "partners", "governance", "private"],
         "description": "Who can query this node (default: public for L3/L4, private for L1)"},
        {"name": "commitments", "type": "array", "required": False,
         "description": "Cryptographic commitments to private fields [{scheme, hash, subject_fields, attestation_ids, created_at}]"},
        {"name": "proof_uri", "type": "string", "required": False,
         "description": "Pointer to proof bundle (ipfs://... or l4://attestation/...)"},
        {"name": "policy_ref", "type": "string", "required": False,
         "description": "L4 policy governing retention/redaction (e.g., l4://policy/retention/citizen_pii)"}
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
    ],

    "privacy_governance": [
        {"name": "visibility", "type": "enum", "required": False,
         "enum_values": ["public", "partners", "governance", "private"],
         "description": "Who can query this link (default: same as connected nodes)"},
        {"name": "commitment", "type": "object", "required": False,
         "description": "Commitment to link metadata if sensitive {scheme, hash, attestation_ids, created_at}"}
    ]
}

# ============================================================================
# LINK TYPE FIELD SPECIFICATIONS
# ============================================================================

LINK_FIELD_SPECS = {
    # ========================================================================
    # UNIVERSAL LINK TYPES (U3/U4)
    # ========================================================================

    # Composition & Identity (U4)
    "MEMBER_OF": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Child→Parent composition relationship. Universal L1234. Invariants: DAG; child.level ≤ parent.level.",
        "required": [
            {"name": "membership_type", "type": "enum",
             "enum_values": ["structural", "functional", "temporary", "honorary"],
             "description": "Nature of membership"},
            {"name": "role", "type": "string",
             "description": "Role within parent structure (e.g., 'frontend_team', 'governance_committee')"}
        ],
        "optional": [
            {"name": "since", "type": "datetime",
             "description": "When membership began"},
            {"name": "until", "type": "datetime",
             "description": "When membership ends (for temporary memberships)"}
        ]
    },

    "ALIASES": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Symmetric equivalence relationship (A↔B). Universal L1234. Same entity, different names/contexts.",
        "required": [
            {"name": "alias_type", "type": "enum",
             "enum_values": ["synonym", "translation", "historical_name", "context_specific"],
             "description": "Type of aliasing"}
        ],
        "optional": [
            {"name": "context", "type": "string",
             "description": "When this alias is used (e.g., 'community_facing', 'technical_docs')"}
        ]
    },

    "MERGED_INTO": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Old→New merge relationship. Universal L1234. Sets old.status=merged. Preserves lineage.",
        "required": [
            {"name": "merge_timestamp", "type": "datetime",
             "description": "When merge occurred"},
            {"name": "merge_reason", "type": "string",
             "description": "Why entities were merged"}
        ],
        "optional": [
            {"name": "absorbed_fields", "type": "array",
             "description": "Which fields from old were absorbed into new"}
        ]
    },

    # Governance & Capability (U4)
    "GOVERNS": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "L4 Subentity→Any. Universal L1234. Protocol subsystem governs domain/resource.",
        "required": [
            {"name": "governance_scope", "type": "string",
             "description": "What aspect is governed (e.g., 'identity', 'payments', 'disputes')"},
            {"name": "authority_type", "type": "enum",
             "enum_values": ["policy_enforcement", "resource_allocation", "permission_granting", "arbitration"],
             "description": "Type of governance authority"}
        ],
        "optional": [
            {"name": "policy_ref", "type": "string",
             "description": "URI to policy document (e.g., 'l4://law/LAW-001')"}
        ]
    },

    "GOVERNED_BY": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Any→L4 Subentity. Universal L1234. Resource/domain governed by protocol subsystem.",
        "required": [
            {"name": "governance_scope", "type": "string",
             "description": "What aspect is governed"},
            {"name": "compliance_status", "type": "enum",
             "enum_values": ["compliant", "pending_review", "non_compliant", "exempt"],
             "description": "Current compliance status"}
        ],
        "optional": []
    },

    "UNLOCKS": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Tier/Policy→Capability/Permission. Universal L1234. Grants access or capability.",
        "required": [
            {"name": "capability", "type": "string",
             "description": "What capability is unlocked (e.g., 'api_access', 'governance_vote')"},
            {"name": "unlock_condition", "type": "string",
             "description": "Condition that must be met to unlock"}
        ],
        "optional": [
            {"name": "expiration", "type": "datetime",
             "description": "When unlock expires (if temporary)"}
        ]
    },

    # Workflow & Assignment (U4)
    "BLOCKED_BY": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Work_Item→Blocker. Universal L1234. Work cannot proceed until blocker resolved.",
        "required": [
            {"name": "blocking_reason", "type": "string",
             "description": "Why this blocks progress"},
            {"name": "severity", "type": "enum",
             "enum_values": ["absolute", "strong", "partial"],
             "description": "How completely this blocks"}
        ],
        "optional": [
            {"name": "resolution_condition", "type": "string",
             "description": "What must happen to unblock"}
        ]
    },

    # Goals & Metrics (U4)
    "DRIVES": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Value/Motivation→Goal. Universal L1234. Motivation driving goal pursuit.",
        "required": [
            {"name": "drive_type", "type": "enum",
             "enum_values": ["intrinsic", "extrinsic", "strategic", "ethical", "pragmatic"],
             "description": "Nature of drive"},
            {"name": "drive_strength", "type": "float", "range": [0.0, 1.0],
             "description": "How strongly this drives goal"}
        ],
        "optional": []
    },

    "TARGETS": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Goal→Outcome. Universal L1234. Goal aims to achieve specific outcome.",
        "required": [
            {"name": "target_type", "type": "enum",
             "enum_values": ["state_change", "metric_threshold", "deliverable", "capability"],
             "description": "Type of target"},
            {"name": "success_criteria", "type": "string",
             "description": "How to know target is achieved"}
        ],
        "optional": [
            {"name": "target_date", "type": "datetime",
             "description": "When target should be achieved"}
        ]
    },

    "CONTROLS": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Mechanism→Metric. Universal L1234. Mechanism controls/regulates metric.",
        "required": [
            {"name": "control_type", "type": "enum",
             "enum_values": ["regulates", "optimizes", "constrains", "monitors"],
             "description": "How mechanism controls metric"}
        ],
        "optional": []
    },

    # Evidence & Attestation (U4)
    "EVIDENCED_BY": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Claim→Proof. Universal L1234. Claim supported by evidence/attestation.",
        "required": [
            {"name": "evidence_type", "type": "enum",
             "enum_values": ["attestation", "measurement", "document", "witness", "cryptographic_proof"],
             "description": "Type of evidence"},
            {"name": "confidence", "type": "float", "range": [0.0, 1.0],
             "description": "How strongly evidence supports claim"}
        ],
        "optional": []
    },

    "ABOUT": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Content→Subject. Universal L1234. Content is about subject matter.",
        "required": [],
        "optional": [
            {"name": "focus_type", "type": "enum",
             "enum_values": ["primary_subject", "secondary_mention", "contextual_reference"],
             "description": "How central the subject is to content"}
        ]
    },

    "REFERENCES": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Doc→External_Resource. Universal L1234. Document references external resource.",
        "required": [
            {"name": "reference_type", "type": "enum",
             "enum_values": ["citation", "dependency", "inspiration", "comparison"],
             "description": "Nature of reference"}
        ],
        "optional": [
            {"name": "uri", "type": "string",
             "description": "URI of referenced resource"}
        ]
    },

    "DEPENDS_ON": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "A→B: cannot function without. Universal L1234. Strong dependency relationship.",
        "required": [
            {"name": "dependency_type", "type": "enum",
             "enum_values": ["runtime", "build_time", "data", "infrastructure", "logical"],
             "description": "Nature of dependency"},
            {"name": "criticality", "type": "enum",
             "enum_values": ["blocking", "important", "optional"],
             "description": "How critical is this dependency"}
        ],
        "optional": []
    },

    # Relationships & Impact (U3 - excludes L4)
    "IMPACTS": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Cause→Effect. Universal L123 (excludes L4). Causal impact relationship.",
        "required": [
            {"name": "impact_type", "type": "enum",
             "enum_values": ["positive", "negative", "neutral", "mixed"],
             "description": "Nature of impact"},
            {"name": "impact_magnitude", "type": "float", "range": [0.0, 1.0],
             "description": "Magnitude of impact"}
        ],
        "optional": [
            {"name": "impact_domain", "type": "string",
             "description": "Domain affected (e.g., 'performance', 'reputation', 'financial')"}
        ]
    },

    "MITIGATED_BY": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Risk→Control. Universal L123 (excludes L4). Risk mitigation relationship.",
        "required": [
            {"name": "mitigation_effectiveness", "type": "float", "range": [0.0, 1.0],
             "description": "How effectively this mitigates risk"},
            {"name": "mitigation_type", "type": "enum",
             "enum_values": ["prevents", "reduces", "transfers", "accepts"],
             "description": "How risk is mitigated"}
        ],
        "optional": []
    },

    # Community & Participation (U3 - excludes L4)
    "PARTICIPATES_IN": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Agent→Event/Community. Universal L123 (excludes L4). Participation relationship.",
        "required": [
            {"name": "participation_type", "type": "enum",
             "enum_values": ["organizer", "active_participant", "observer", "contributor"],
             "description": "Nature of participation"}
        ],
        "optional": [
            {"name": "participation_frequency", "type": "string",
             "description": "How often participates (e.g., 'regular', 'occasional')"}
        ]
    },

    "SETTLED_BY": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Dispute→Outcome. Universal L123 (excludes L4). Dispute resolution relationship.",
        "required": [
            {"name": "settlement_type", "type": "enum",
             "enum_values": ["consensus", "arbitration", "voting", "mediation", "ruling"],
             "description": "How dispute was settled"},
            {"name": "settlement_timestamp", "type": "datetime",
             "description": "When settlement occurred"}
        ],
        "optional": [
            {"name": "settlement_terms", "type": "string",
             "description": "Terms of settlement"}
        ]
    },

    # ========================================================================
    # EXISTING SHARED LINK TYPES (to be updated to universal where appropriate)
    # ========================================================================

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
        "level": "shared", "category": "structural", "universality": "U4",
        "description": "A↔B: general association. Universal L1234. Generic connection when specific type unclear.",
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
        "level": "shared", "category": "organizational", "universality": "U4",
        "description": "Work_Item→Agent. Universal L1234. Task ownership or responsibility assignment.",
        "required": [],
        "optional": [
            {"name": "assignment_date", "type": "datetime",
             "description": "When assignment was made"}
        ]
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
        "level": "shared", "category": "organizational", "universality": "U4",
        "description": "Metric→Measured_thing. Universal L1234. Quantifies performance or progress.",
        "required": [],
        "optional": [
            {"name": "measurement_unit", "type": "string",
             "description": "Unit of measurement (e.g., 'milliseconds', 'count', 'percentage')"}
        ]
    },

    "THREATENS": {
        "level": "shared", "category": "organizational",
        "description": "Danger or risk to goal/project",
        "required": [],
        "optional": []
    },

    # Activation & Triggering (3 types)
    "ACTIVATES": {
        "level": "shared", "category": "activation", "universality": "U4",
        "description": "Stimulus→Response. Universal L1234. Trigger awakens subentity coalition or initiates response.",
        "required": [],
        "optional": [
            {"name": "activation_threshold", "type": "float", "range": [0.0, 1.0],
             "description": "Energy threshold for activation"}
        ]
    },

    "TRIGGERED_BY": {
        "level": "shared", "category": "activation", "universality": "U4",
        "description": "Event→Cause. Universal L1234. What caused memory/pattern/event to activate.",
        "required": [],
        "optional": [
            {"name": "trigger_strength", "type": "float", "range": [0.0, 1.0],
             "description": "How strongly this triggered the event"}
        ]
    },

    "SUPPRESSES": {
        "level": "shared", "category": "activation", "universality": "U4",
        "description": "Inhibitor→Target. Universal L1234. What blocks subentity activation or suppresses response.",
        "required": [],
        "optional": [
            {"name": "suppression_mechanism", "type": "string",
             "description": "How suppression works"}
        ]
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

    # Universal/Shared (Multi-scale consciousness infrastructure)
    "Subentity": {
        "level": "shared", "category": "consciousness",
        "description": "Multi-scale consciousness neighborhood (functional role or semantic cluster). Universal across ALL levels: L1 (personal roles), L2 (org teams), L3 (ecosystem clusters), L4 (protocol subsystems).",
        "required": [
            {"name": "entity_kind", "type": "enum",
             "enum_values": ["functional", "semantic"],
             "description": "Type of subentity: functional (cognitive role) or semantic (topic cluster)"},
            {"name": "role_or_topic", "type": "string",
             "description": "Role name (e.g., 'translator', 'sea_identity') or topic (e.g., 'consciousness_architecture')"},
            {"name": "scope", "type": "enum",
             "enum_values": ["personal", "organizational", "ecosystem", "protocol"],
             "description": "Which level this subentity operates at"}
        ],
        "optional": [
            {"name": "centroid_embedding", "type": "array",
             "description": "Semantic embedding for similarity matching (768 or 1536 dims)"},
            {"name": "energy_runtime", "type": "float",
             "description": "Aggregate energy from member nodes (computed, not persisted)"},
            {"name": "threshold_runtime", "type": "float",
             "description": "Dynamic activation threshold (computed, not persisted)"},
            {"name": "activation_level_runtime", "type": "enum",
             "enum_values": ["dominant", "strong", "moderate", "weak", "absent"],
             "description": "Current activation state (computed, not persisted)"},
            {"name": "coherence_ema", "type": "float",
             "description": "How tight is this cluster (EMA)"},
            {"name": "member_count", "type": "integer",
             "description": "Number of nodes in this subentity"},
            {"name": "log_weight", "type": "float",
             "description": "Long-run importance (learning weight)"},
            {"name": "stability_state", "type": "enum",
             "enum_values": ["candidate", "provisional", "mature"],
             "description": "Lifecycle state for promotion/dissolution"},
            {"name": "quality_score", "type": "float",
             "description": "Geometric mean of quality signals"},
            {"name": "created_from", "type": "string",
             "description": "Provenance: role_seed | semantic_clustering | co_activation | trace_formation"},
            {"name": "policy_doc_uri", "type": "string",
             "description": "(L4 only) Pointer to law document (e.g., 'l4://law/LAW-001')"},
            {"name": "version", "type": "string",
             "description": "(L4 only) Semantic version for protocol subsystems"},
            {"name": "governance_model", "type": "enum",
             "enum_values": ["foundation", "dao", "algorithmic", "hybrid"],
             "description": "(L4 only) Who governs this subsystem"},
            {"name": "health", "type": "enum",
             "enum_values": ["healthy", "degraded", "failing"],
             "description": "(L4 only) Operational health status"}
        ]
    },

    # Universal Types (L1234 or L123)
    "U4_Event": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal event/happening across all levels (L1234). Unifies Memory (L1) and Event (L3). Percepts, missions, market events, incidents, governance actions.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this event occurred at"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "event_kind", "type": "enum",
             "enum_values": ["percept", "mission", "market", "incident", "publish", "trade", "governance", "healthcheck", "decision_record"],
             "description": "Type of event"},
            {"name": "actor_ref", "type": "string",
             "description": "Who performed this event (Agent node ID)"},
            {"name": "timestamp", "type": "datetime",
             "description": "When event occurred"}
        ],
        "optional": [
            {"name": "subject_refs", "type": "array",
             "description": "What/who this event is about (node IDs)"},
            {"name": "severity", "type": "enum",
             "enum_values": ["low", "medium", "high", "critical"],
             "description": "Event severity (for incidents/alerts)"},
            {"name": "attestation_ref", "type": "string",
             "description": "SEA snapshot/context hash for high-stakes events"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived"],
             "description": "Event status"}
        ]
    },

    "U4_Agent": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal agent across all levels (L1234). Unifies Person (L1), Human/AI_Agent (L2), External_Person (L3). Any actor that can perform actions.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this agent operates at"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "agent_type", "type": "enum",
             "enum_values": ["human", "citizen", "org", "dao", "external_system"],
             "description": "Type of agent"}
        ],
        "optional": [
            {"name": "did", "type": "string",
             "description": "Decentralized identifier (e.g., did:mind:solana:felix)"},
            {"name": "keys", "type": "array",
             "description": "Public keys for signing"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived", "merged", "dissolved"],
             "description": "Agent status"}
        ]
    },

    "U3_Pattern": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Universal behavioral pattern (L123). Unifies Personal_Pattern, Best_Practice, Anti_Pattern, Behavioral_Pattern. Recurring behaviors at any scale.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3"],
             "description": "Which level this pattern applies to"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3)"},
            {"name": "pattern_type", "type": "enum",
             "enum_values": ["habit", "best_practice", "anti_pattern", "market_behavior", "process_pattern"],
             "description": "Type of pattern"},
            {"name": "valence", "type": "enum",
             "enum_values": ["positive", "negative", "neutral"],
             "description": "Is this pattern beneficial, harmful, or neutral?"}
        ],
        "optional": [
            {"name": "preconditions", "type": "array",
             "description": "What must be true before this pattern activates"},
            {"name": "postconditions", "type": "array",
             "description": "What becomes true after this pattern executes"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived"],
             "description": "Pattern status"}
        ]
    },

    "U4_Goal": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal goal/aspiration (L1234). Personal goals, project goals, protocol roadmaps. Any target state to achieve.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this goal applies to"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "horizon", "type": "enum",
             "enum_values": ["daily", "weekly", "monthly", "quarterly", "annual", "multi_year"],
             "description": "Time horizon for achieving this goal"}
        ],
        "optional": [
            {"name": "okrs", "type": "array",
             "description": "Key results (array of {key_result_id, target, current})"},
            {"name": "target_date", "type": "datetime",
             "description": "When this goal should be achieved"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived", "achieved", "abandoned"],
             "description": "Goal status"}
        ]
    },

    "U4_Decision": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal decision record (L1234). Personal choices, organizational decisions, protocol governance decisions.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this decision was made at"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "choice", "type": "string",
             "description": "What was decided"},
            {"name": "rationale", "type": "string",
             "description": "Why this decision was made"},
            {"name": "decider_ref", "type": "string",
             "description": "Who made this decision (Agent/Org/DAO node ID)"}
        ],
        "optional": [
            {"name": "proposal_ref", "type": "string",
             "description": "Proposal this decision responds to"},
            {"name": "outcome_ref", "type": "string",
             "description": "Event/Agreement resulting from this decision"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived", "reversed"],
             "description": "Decision status"}
        ]
    },

    "U3_Risk": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Universal risk assessment (L123). Threats to goals at personal, organizational, or ecosystem level.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3"],
             "description": "Which level this risk exists at"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3)"},
            {"name": "likelihood", "type": "float", "range": [0.0, 1.0],
             "description": "Probability this risk materializes"},
            {"name": "impact", "type": "float", "range": [0.0, 1.0],
             "description": "Severity if this risk materializes"}
        ],
        "optional": [
            {"name": "risk_score", "type": "float",
             "description": "Computed: likelihood × impact"},
            {"name": "category", "type": "enum",
             "enum_values": ["technical", "market", "operational", "regulatory", "reputational"],
             "description": "Risk category"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived", "mitigated", "materialized"],
             "description": "Risk status"}
        ]
    },

    "U4_Metric": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal metric definition (L1234). Defines what to measure at any level (personal habits, org KPIs, ecosystem metrics, protocol health).",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this metric applies to"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "unit", "type": "string",
             "description": "Unit of measurement (e.g., 'USD', 'count', 'percentage')"},
            {"name": "definition", "type": "string",
             "description": "What this metric measures"}
        ],
        "optional": [
            {"name": "aggregation", "type": "enum",
             "enum_values": ["sum", "avg", "p95", "rate", "custom"],
             "description": "How to aggregate measurements"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived"],
             "description": "Metric status"}
        ]
    },

    "U4_Measurement": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal measurement data point (L1234). Actual measurements of a Metric over time.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this measurement is from"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "metric_ref", "type": "string",
             "description": "Metric node ID this measures"},
            {"name": "value", "type": "float",
             "description": "Measured value"},
            {"name": "timestamp", "type": "datetime",
             "description": "When this was measured"}
        ],
        "optional": [
            {"name": "window", "type": "string",
             "description": "Time window for aggregation (e.g., '1h', '1d')"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "archived"],
             "description": "Measurement status"}
        ]
    },

    "U4_Work_Item": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal work item (L1234). Unifies Task, Milestone, personal todos. Any discrete unit of work at any level.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this work item belongs to"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "work_type", "type": "enum",
             "enum_values": ["task", "milestone", "bug", "ticket", "mission"],
             "description": "Type of work"},
            {"name": "state", "type": "enum",
             "enum_values": ["todo", "doing", "blocked", "done", "canceled"],
             "description": "Current state"},
            {"name": "priority", "type": "enum",
             "enum_values": ["critical", "high", "medium", "low"],
             "description": "Priority level"}
        ],
        "optional": [
            {"name": "assignee_ref", "type": "string",
             "description": "Who is assigned (Agent node ID)"},
            {"name": "due_date", "type": "datetime",
             "description": "When this should be completed"},
            {"name": "acceptance_criteria", "type": "string",
             "description": "How we know this is done"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived"],
             "description": "Work item status"}
        ]
    },

    "U3_Relationship": {
        "level": "shared", "category": "universal", "universality": "U3",
        "description": "Universal relationship (L123). Personal relationships, business partnerships, protocol partnerships. Connection between agents.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3"],
             "description": "Which level this relationship exists at"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3)"},
            {"name": "relationship_type", "type": "enum",
             "enum_values": ["personal", "partnership", "supplier", "customer", "counterparty", "protocol_partnership"],
             "description": "Type of relationship"}
        ],
        "optional": [
            {"name": "terms_ref", "type": "string",
             "description": "Agreement node ID defining terms (optional)"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "negotiating", "suspended", "terminated"],
             "description": "Relationship status"}
        ]
    },

    "U4_Assessment": {
        "level": "shared", "category": "universal", "universality": "U4",
        "description": "Universal assessment/evaluation (L1234). Unifies Reputation_Assessment, Psychological_Trait, performance reviews. Any evaluation of an entity.",
        "required": [
            {"name": "level", "type": "enum",
             "enum_values": ["L1", "L2", "L3", "L4"],
             "description": "Which level this assessment applies to"},
            {"name": "scope_ref", "type": "string",
             "description": "Anchor: Citizen ID (L1), Org ID (L2), Ecosystem ID (L3), or 'protocol' (L4)"},
            {"name": "domain", "type": "enum",
             "enum_values": ["reputation", "psychology", "performance", "security", "compliance"],
             "description": "What aspect is being assessed"},
            {"name": "score", "type": "float",
             "description": "Assessment score (scale-dependent)"},
            {"name": "assessor_ref", "type": "string",
             "description": "Who performed assessment (Agent/Org/DAO node ID)"}
        ],
        "optional": [
            {"name": "scale", "type": "string",
             "description": "What scale the score is on (e.g., '0-100', '1-5 stars')"},
            {"name": "method", "type": "string",
             "description": "How assessment was performed"},
            {"name": "slug", "type": "string",
             "description": "URL-friendly identifier"},
            {"name": "status", "type": "enum",
             "enum_values": ["active", "suspended", "archived"],
             "description": "Assessment status"}
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

    "Attestation": {
        "level": "n3", "category": "evidence",
        "description": "Cryptographic attestation/proof (e.g., SEA-1.0 snapshot)",
        "required": [
            {"name": "attestation_id", "type": "string",
             "description": "Unique attestation identifier"},
            {"name": "issuer", "type": "string",
             "description": "DID of issuer (e.g., 'did:mind:solana:felix')"},
            {"name": "signature", "type": "string",
             "description": "Cryptographic signature (e.g., Ed25519)"},
            {"name": "attestation_type", "type": "enum",
             "enum_values": ["identity_snapshot", "policy_commitment", "contract_hash", "capability_proof"],
             "description": "Type of attestation"},
            {"name": "timestamp", "type": "datetime",
             "description": "When attestation was created"}
        ],
        "optional": [
            {"name": "subject", "type": "string",
             "description": "Node or link ID this attests to"},
            {"name": "commitment", "type": "string",
             "description": "Hash commitment (e.g., 'sha256:abc123...')"},
            {"name": "fields", "type": "array",
             "description": "List of field names committed to"},
            {"name": "valid_from", "type": "datetime",
             "description": "Start of validity window"},
            {"name": "valid_to", "type": "datetime",
             "description": "End of validity window"},
            {"name": "revocation_ref", "type": "string",
             "description": "Pointer to revocation event if revoked"},
            {"name": "payload_encrypted", "type": "string",
             "description": "Encrypted full payload (AES-256-GCM, governance-scoped)"},
            {"name": "encryption_key_id", "type": "string",
             "description": "ID of key used for encryption (e.g., 'foundation_audit_key_20251030')"}
        ]
    },
}
