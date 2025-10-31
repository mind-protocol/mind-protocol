# =============================================================================
# Complete Schema Data - Single Source of Truth (REWRITTEN)
# =============================================================================
# Author: Felix "Ironhand" (edited for U3/U4 standardization)
# Date: 2025-10-31
# Source baseline: UNIFIED_SCHEMA_REFERENCE.md / previous complete_schema_data.py
#
# This file defines:
#   • UNIVERSAL_NODE_ATTRIBUTES
#   • UNIVERSAL_LINK_ATTRIBUTES
#   • LINK_FIELD_SPECS  (U4_* and U3_* only; reverse_name for all)
#   • NODE_TYPE_SCHEMAS (U4_* and U3_* canonical nodes + level-bound L1_/L2_/L3_/L4_)
#   • DEPRECATIONS      (old_name → new_name mapping; 1-release grace)
#
# Conventions:
#   • Primary label == type_name (e.g., :U4_Event → type_name="U4_Event")
#   • Universality: U4 = L1–L4; U3 = L1–L3
#   • Bitemporal fields: valid_from/valid_to + created_at/updated_at
#   • Visibility defaults: L1→private; L3/L4→public (unless policy says otherwise)
#   • commitments[]: same object on nodes AND links: {scheme, hash, subject_fields[], attestation_ids[], created_at}
#
# =============================================================================

FIELD_META_KEYS = [
    "required", "type", "enum_values", "range",
    "default", "set_by", "read_only", "computed", "persist",
    "description", "detailed_description"
]

VISIBILITY_DEFAULT_RULE = "L1→private; L2→partners; L3/L4→public"

# -------------------------------
# UNIVERSAL NODE ATTRIBUTE SETS
# -------------------------------
UNIVERSAL_NODE_ATTRIBUTES = {
    "core_identity": [
        {"name": "type_name", "type": "string", "required": True, "read_only": True,
         "description": "Canonical node class; equals primary graph label"},
        {"name": "name", "type": "string", "required": True,
         "description": "Display name"},
        {"name": "description", "type": "string", "required": False,
         "description": "Short summary"},
        {"name": "detailed_description", "type": "string", "required": False,
         "description": "Long-form explanation with examples"}
    ],
    "level_scope": [
        {"name": "level", "type": "enum", "required": True,
         "enum_values": ["L1", "L2", "L3", "L4"],
         "description": "Level this node belongs to"},
        {"name": "scope_ref", "type": "string", "required": False,
         "description": "Anchor for this node: Citizen (L1), Org (L2), Ecosystem (L3), or 'protocol' (L4)"}
    ],
    "bitemporal_tracking": [
        {"name": "valid_from", "type": "datetime", "required": True, "default": "now",
         "description": "When this fact became true"},
        {"name": "valid_to", "type": "datetime", "required": False, "default": None,
         "description": "When this fact ceased to be true (None = still valid)"},
        {"name": "created_at", "type": "datetime", "required": True, "default": "now", "set_by": "system",
         "description": "Record creation time"},
        {"name": "updated_at", "type": "datetime", "required": False, "set_by": "system",
         "description": "Last mutation time"}
    ],
    "privacy_governance": [
        {"name": "visibility", "type": "enum", "required": False,
         "enum_values": ["public", "partners", "governance", "private"],
         "default_rule": VISIBILITY_DEFAULT_RULE,
         "description": "Query visibility; default derived from level"},
        {"name": "commitments", "type": "array", "required": False,
         "description": "List of cryptographic commitments to private fields"},
        {"name": "proof_uri", "type": "string", "required": False,
         "description": "Pointer to proof bundle (ipfs://… or l4://…)"},
        {"name": "policy_ref", "type": "string", "required": False,
         "description": "Governing L4 policy document"}
    ],
    "provenance": [
        {"name": "created_by", "type": "string", "required": False,
         "description": "Agent/Service that created this node"},
        {"name": "substrate", "type": "enum", "required": False,
         "enum_values": ["personal", "organizational", "external_web", "external_system"],
         "description": "Where this was created"}
    ]
}

# -------------------------------
# UNIVERSAL LINK ATTRIBUTE SETS
# -------------------------------
UNIVERSAL_LINK_ATTRIBUTES = {
    "bitemporal_tracking": [
        {"name": "valid_from", "type": "datetime", "required": True, "default": "now",
         "description": "When this link became true"},
        {"name": "valid_to", "type": "datetime", "required": False, "default": None,
         "description": "When this link ceased to be true"},
        {"name": "created_at", "type": "datetime", "required": True, "default": "now", "set_by": "system",
         "description": "Record creation time"},
        {"name": "updated_at", "type": "datetime", "required": False, "set_by": "system",
         "description": "Last mutation time"}
    ],
    "privacy_governance": [
        {"name": "visibility", "type": "enum", "required": False,
         "enum_values": ["public", "partners", "governance", "private"],
         "default_rule": "inherit-from-nodes",
         "description": "Visibility; default = most restrictive of the two endpoints"},
        {"name": "commitments", "type": "array", "required": False,
         "description": "List of cryptographic commitments to link metadata"}
    ],
    "consciousness_metadata": [
        {"name": "goal", "type": "string", "required": False,
         "description": "Intent for forming this link"},
        {"name": "forming_mindstate", "type": "string", "required": False,
         "description": "Declarative state label at formation time",
         "detailed_description": "Declarative state label at formation time (e.g., 'deliberation','flow','alert','explore')"},
        {"name": "energy", "type": "float", "required": False, "set_by": "receiver", "read_only": True, "range": [0.0, 1.0],
         "description": "Receiver-computed urgency/valence at accept-time",
         "detailed_description": "Receiver-computed urgency/valence at accept-time; senders MUST NOT supply"},
        {"name": "confidence", "type": "float", "required": False, "range": [0.0, 1.0],
         "description": "Certainty in this connection at formation time"}
    ],
    "provenance": [
        {"name": "created_by", "type": "string", "required": False,
         "description": "Agent/Service that created this link"},
        {"name": "substrate", "type": "enum", "required": False,
         "enum_values": ["personal", "organizational", "external_web", "external_system"],
         "description": "Where this was created"}
    ]
}

NODE_TYPE_SCHEMAS = {

# =========================
# U4 — UNIVERSAL NODES (L1–L4)
# =========================

  # ---- Events & Actors ----
  "U4_Event": {
    "universality": "U4",
    "description": "Universal event/happening; unifies L1 Memory & L3 Event.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string","description":"Citizen/Org/Ecosystem id or 'protocol'"},
      {"name":"event_kind","type":"enum",
       "enum_values":["percept","mission","market","incident","publish","trade","governance","healthcheck","decision_record"]},
      {"name":"actor_ref","type":"string"},
      {"name":"timestamp","type":"datetime","default":"now"}
    ],
    "optional": [
      {"name":"subject_refs","type":"array"},
      {"name":"severity","type":"enum","enum_values":["low","medium","high","critical"]},
      {"name":"attestation_ref","type":"string"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  "U4_Agent": {
    "universality": "U4",
    "description": "Universal actor: human, citizen, org, DAO, or external system.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"agent_type","type":"enum","enum_values":["human","citizen","org","dao","external_system"]}
    ],
    "optional": [
      {"name":"did","type":"string"},{"name":"keys","type":"array"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived","merged","dissolved"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  # ---- Composition atom ----
  "U4_Subentity": {
    "universality": "U4",
    "description": "Multi-scale neighborhood (functional role or semantic cluster). At L4 with kind='protocol-subsystem' it represents a protocol subsystem.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"kind","type":"enum","enum_values":["functional","semantic","protocol-subsystem"]},
      {"name":"role_or_topic","type":"string"}
    ],
    "optional": [
      {"name":"slug","type":"string"},
      {"name":"parent_ref","type":"string"},
      {"name":"member_count","type":"integer","default":0,"set_by":"receiver"},
      {"name":"centroid_embedding","type":"array"},
      {"name":"coherence_ema","type":"float","default":0.0},
      {"name":"quality_score","type":"float","default":0.0},
      {"name":"log_weight","type":"float","default":0.0},
      {"name":"stability_state","type":"enum","enum_values":["candidate","provisional","mature"],"default":"candidate"},
      {"name":"energy_runtime","type":"float","computed":True,"persist":False},
      {"name":"activation_level_runtime","type":"enum",
       "enum_values":["dominant","strong","moderate","weak","absent"],"computed":True,"persist":False},
      {"name":"created_from","type":"enum",
       "enum_values":["role_seed","semantic_clustering","co_activation","trace_formation","manual"],"default":"semantic_clustering"},
      {"name":"notes","type":"string"},
      # L4-only convenience (used when kind='protocol-subsystem')
      {"name":"policy_doc_uri","type":"string"},{"name":"version","type":"string"},
      {"name":"governance_model","type":"enum","enum_values":["foundation","dao","algorithmic","hybrid"],"default":"foundation"},
      {"name":"health","type":"enum","enum_values":["healthy","degraded","failing"],"default":"healthy"},
      {"name":"owners","type":"array"},{"name":"sla","type":"string"},
      {"name":"topic_coverage","type":"array"}
    ],
    "invariants": [
      "if kind=='protocol-subsystem' then level=='L4'",
      "member_count >= 0"
    ]
  },

  # ---- Goals, Decisions, Work ----
  "U4_Goal": {
    "universality": "U4",
    "description": "Universal goal; personal, project, ecosystem, or protocol roadmap item.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"horizon","type":"enum","enum_values":["daily","weekly","monthly","quarterly","annual","multi_year"]}
    ],
    "optional": [
      {"name":"okrs","type":"array"},{"name":"target_date","type":"datetime"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived","achieved","abandoned"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  "U4_Decision": {
    "universality": "U4",
    "description": "Universal decision record at any level.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"choice","type":"string"},{"name":"rationale","type":"string"},
      {"name":"decider_ref","type":"string"}
    ],
    "optional": [
      {"name":"proposal_ref","type":"string"},{"name":"outcome_ref","type":"string"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived","reversed"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  "U4_Work_Item": {
    "universality": "U4",
    "description": "Universal work item (task/milestone/bug/ticket/mission).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"work_type","type":"enum","enum_values":["task","milestone","bug","ticket","mission"]},
      {"name":"state","type":"enum","enum_values":["todo","doing","blocked","done","canceled"]},
      {"name":"priority","type":"enum","enum_values":["critical","high","medium","low"],"default":"medium"}
    ],
    "optional": [
      {"name":"assignee_ref","type":"string"},{"name":"due_date","type":"datetime"},
      {"name":"acceptance_criteria","type":"string"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  # ---- Metrics & Assessments ----
  "U4_Metric": {
    "universality": "U4",
    "description": "Metric definition (what/how to measure).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"unit","type":"string"},{"name":"definition","type":"string"}
    ],
    "optional": [
      {"name":"aggregation","type":"enum","enum_values":["sum","avg","p95","rate","custom"],"default":"avg"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ]
  },

  "U4_Measurement": {
    "universality": "U4",
    "description": "Concrete datapoint for a metric.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"metric_ref","type":"string"},
      {"name":"value","type":"float"},
      {"name":"timestamp","type":"datetime","default":"now","set_by":"system"}
    ],
    "optional": [{"name":"window","type":"string"},{"name":"status","type":"enum","enum_values":["active","archived"],"default":"active"}]
  },

  "U4_Assessment": {
    "universality": "U4",
    "description": "Evaluation record (reputation/psychology/performance/security/compliance).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"domain","type":"enum","enum_values":["reputation","psychology","performance","security","compliance"]},
      {"name":"score","type":"float"},
      {"name":"assessor_ref","type":"string"}
    ],
    "optional": [
      {"name":"scale","type":"string"},{"name":"method","type":"string"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived"],"default":"active"}
    ]
  },

  # ---- Knowledge & Documentation ----
  "U4_Knowledge_Object": {
    "universality": "U4",
    "description": "Spec/ADR/runbook/guide/reference—the canonical doc source.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"ko_id","type":"string"},
      {"name":"ko_type","type":"enum","enum_values":["adr","spec","runbook","guide","reference","policy_summary"]},
      {"name":"uri","type":"string"}
    ],
    "optional": [
      {"name":"hash","type":"string"},
      {"name":"status","type":"enum","enum_values":["draft","active","deprecated"],"default":"active"},
      {"name":"owner","type":"string"}
    ]
  },

  "U4_Doc_View": {
    "universality": "U4",
    "description": "Rendered documentation view/page.",
    "required": [
      {"name":"view_id","type":"string"},
      {"name":"route","type":"string"}
    ],
    "optional": [
      {"name":"renderer","type":"enum","enum_values":["next","static"],"default":"next"},
      {"name":"build_hash","type":"string","set_by":"system"}
    ]
  },

  # ---- Code & Attestations ----
  "U4_Code_Artifact": {
    "universality": "U4",
    "description": "Source artifact (file/module) tracked for traceability.",
    "required": [
      {"name":"repo","type":"string"},
      {"name":"path","type":"string"},
      {"name":"lang","type":"enum","enum_values":["py","ts","js","sql","bash","rust","go","other"]},
      {"name":"commit","type":"string"},
      {"name":"hash","type":"string","set_by":"system"}
    ],
    "optional": [{"name":"updated_at","type":"datetime","set_by":"system"}]
  },

  "U4_Attestation": {
    "universality": "U4",
    "description": "Cryptographic attestation (e.g., SEA identity snapshot, policy commitment).",
    "required": [
      {"name":"attestation_id","type":"string"},
      {"name":"issuer","type":"string"},{"name":"signature","type":"string"},
      {"name":"attestation_type","type":"enum","enum_values":["identity_snapshot","policy_commitment","contract_hash","capability_proof"]},
      {"name":"timestamp","type":"datetime","default":"now"}
    ],
    "optional": [
      {"name":"subject","type":"string"},{"name":"commitment","type":"string"},{"name":"fields","type":"array"},
      {"name":"valid_from","type":"datetime"},{"name":"valid_to","type":"datetime"},
      {"name":"revocation_ref","type":"string"},
      {"name":"payload_encrypted","type":"string"},{"name":"encryption_key_id","type":"string"}
    ]
  },

  # ---- Public presence & capability catalog ----
  "U4_Public_Presence": {
    "universality": "U4",
    "description": "Public listing/presence for an org/citizen in an ecosystem.",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3","L4"]},
      {"name":"scope_ref","type":"string"},
      {"name":"visibility","type":"enum","enum_values":["public","partners"],"default":"public"},
      {"name":"channels","type":"array","default":["web"]}
    ],
    "optional": [
      {"name":"capabilities","type":"array","description":"Advertised capability ids"},
      {"name":"route","type":"string"}
    ]
  },

  # NOTE: U4_Capability removed - duplicate of L4_Capability (line 707)
  # Capabilities are protocol-level law (L4), not universal across all levels
  # See DEPRECATIONS for migration path

  # ---- Cross-level assets ----
  "U4_Wallet_Address": {
    "universality": "U4",
    "description": "On-chain wallet address, usable at any level.",
    "required": [
      {"name":"address","type":"string"},
      {"name":"blockchain","type":"enum","enum_values":["ethereum","solana","bitcoin","other"]},
      {"name":"wallet_type","type":"enum","enum_values":["eoa","contract","multisig"]}
    ],
    "optional": []
  },

  "U4_Smart_Contract": {
    "universality": "U4",
    "description": "Smart contract reference across levels.",
    "required": [
      {"name":"contract_address","type":"string"},
      {"name":"blockchain","type":"enum","enum_values":["ethereum","solana","other"]},
      {"name":"contract_type","type":"enum","enum_values":["token","defi","nft","governance"]}
    ],
    "optional": []
  },

# =========================
# U3 — UNIVERSAL NODES (L1–L3)
# =========================

  # --------------------
  # Behavioral Pattern
  # --------------------
  "U3_Pattern": {
    "universality": "U3",
    "description": "Recurring behavior at L1–L3 (habits, best/anti patterns, market/process patterns).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"],
       "description":"Pattern applies at personal (L1), org (L2), or ecosystem (L3) scope"},
      {"name":"scope_ref","type":"string","description":"Citizen/Org/Ecosystem id"},
      {"name":"pattern_type","type":"enum",
       "enum_values":["habit","best_practice","anti_pattern","market_behavior","process_pattern"]},
      {"name":"valence","type":"enum","enum_values":["positive","negative","neutral"],"default":"neutral"}
    ],
    "optional": [
      {"name":"preconditions","type":"array","description":"Conditions that enable the pattern"},
      {"name":"postconditions","type":"array","description":"What tends to follow the pattern"},
      {"name":"activation_cues","type":"array","description":"Signals that trigger the pattern"},
      {"name":"decay_rate","type":"float","range":[0.0,1.0],"default":0.95,
       "description":"How quickly pattern salience decays without reinforcement"},
      {"name":"evidence_refs","type":"array","description":"Attestations or documents that support this pattern"},
      {"name":"status","type":"enum","enum_values":["active","suspended","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ],
    "invariants": ["level in {'L1','L2','L3'}"]
  },

  # --------------------
  # Risk (non-L4)
  # --------------------
  "U3_Risk": {
    "universality": "U3",
    "description": "Risk/threat to goals at L1–L3 (non-law).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"]},
      {"name":"scope_ref","type":"string"},
      {"name":"likelihood","type":"float","range":[0.0,1.0]},
      {"name":"impact","type":"float","range":[0.0,1.0]}
    ],
    "optional": [
      {"name":"risk_score","type":"float","computed":True,"description":"likelihood × impact"},
      {"name":"category","type":"enum","enum_values":["technical","market","operational","regulatory","reputational"]},
      {"name":"owner_ref","type":"string","description":"Agent/Team responsible for mitigation"},
      {"name":"mitigation_plan","type":"string"},
      {"name":"status","type":"enum",
       "enum_values":["active","mitigated","materialized","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ],
    "invariants": ["level in {'L1','L2','L3'}"]
  },

  # --------------------
  # Relationship (non-law)
  # --------------------
  "U3_Relationship": {
    "universality": "U3",
    "description": "Connection between agents at L1–L3 (personal/business/protocol partnerships).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"]},
      {"name":"scope_ref","type":"string"},
      {"name":"relationship_type","type":"enum",
       "enum_values":["personal","partnership","supplier","customer","counterparty","protocol_partnership"]}
    ],
    "optional": [
      {"name":"terms_ref","type":"string","description":"Agreement node id if formalized"},
      {"name":"start_date","type":"datetime","default":"now"},
      {"name":"end_date","type":"datetime","default":None},
      {"name":"trust_score","type":"float","range":[0.0,1.0],"default":0.5},
      {"name":"status","type":"enum","enum_values":["active","negotiating","suspended","terminated"],"default":"active"},
      {"name":"slug","type":"string"}
    ],
    "invariants": ["level in {'L1','L2','L3'}"]
  },

  # --------------------
  # Deal (generic non-regulatory agreement)
  # --------------------
  "U3_Deal": {
    "universality": "U3",
    "description": "Generic agreement/transaction intent at L1–L3 (pre-legal; distinct from L3_Deal if you keep that specialized).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"]},
      {"name":"scope_ref","type":"string"},
      {"name":"deal_kind","type":"enum","enum_values":["trade","service","licensing","collaboration"]},
      {"name":"state","type":"enum","enum_values":["Proposed","Confirmed","Settled","Rejected"],"default":"Proposed"}
    ],
    "optional": [
      {"name":"amount_ccy","type":"string","default":"USD"},
      {"name":"amount_value","type":"float"},
      {"name":"counterparties","type":"array","description":"Agent/Org ids involved"},
      {"name":"agreement_ref","type":"string"},
      {"name":"settlement_date","type":"datetime"},
      {"name":"notes","type":"string"},
      {"name":"status","type":"enum","enum_values":["active","archived"],"default":"active"}
    ],
    "invariants": ["level in {'L1','L2','L3'}"]
  },

  # --------------------
  # Community (social grouping not expressed as law)
  # --------------------
  "U3_Community": {
    "universality": "U3",
    "description": "Named group/community at L1–L3 (guild, working group, interest cluster).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"]},
      {"name":"scope_ref","type":"string"},
      {"name":"community_type","type":"enum","enum_values":["guild","working_group","interest","other"],"default":"other"},
      {"name":"name","type":"string"}
    ],
    "optional": [
      {"name":"purpose","type":"string"},
      {"name":"membership_policy","type":"enum","enum_values":["open","invite_only","vetted"],"default":"open"},
      {"name":"member_count","type":"integer","default":0,"set_by":"receiver"},
      {"name":"status","type":"enum","enum_values":["active","dormant","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ],
    "invariants": ["level in {'L1','L2','L3'}","member_count >= 0"]
  },

  # --------------------
  # Practice (implementation habit that is not L4 policy)
  # --------------------
  "U3_Practice": {
    "universality": "U3",
    "description": "Adopted practice/standard operating procedure at L1–L3 (non-law).",
    "required": [
      {"name":"level","type":"enum","enum_values":["L1","L2","L3"]},
      {"name":"scope_ref","type":"string"},
      {"name":"name","type":"string"}
    ],
    "optional": [
      {"name":"intent","type":"string","description":"Why this practice exists"},
      {"name":"steps","type":"array","description":"High-level steps/checklist"},
      {"name":"owner_ref","type":"string"},
      {"name":"maturity","type":"enum","enum_values":["incipient","defined","managed","optimized"],"default":"defined"},
      {"name":"status","type":"enum","enum_values":["active","deprecated","archived"],"default":"active"},
      {"name":"slug","type":"string"}
    ],
    "invariants": ["level in {'L1','L2','L3'}"]
  },



# =========================
# L4 — PROTOCOL / LAW NODES
# =========================

  # Anchor & structure
  "L4_Autonomy_Tier": {
    "universality": "L4",
    "description": "Capability gating tier at protocol level.",
    "required": [
      {"name":"tier_number","type":"integer","description":"1..5 scale"},
      {"name":"name","type":"string","default":"", "description":"Human label"}
    ],
    "optional": [
      {"name":"min_balance_mind","type":"float","default":0.0,
       "description":"Minimum wallet balance to qualify"},
      {"name":"min_reliability_score","type":"float","range":[0.0,100.0],"default":0.0},
      {"name":"notes","type":"string"}
    ]
  },

  # Registry core
  "L4_Schema_Bundle": {
    "universality": "L4",
    "description": "Logical release bundle of schemas/policies.",
    "required": [
      {"name":"semver","type":"string","description":"e.g., '1.0.0'"},
      {"name":"status","type":"enum","enum_values":["draft","active","deprecated","yanked"],"default":"draft"},
      {"name":"hash","type":"string","description":"Content address of manifest"}
    ],
    "optional": [
      {"name":"changelog_uri","type":"string"},
      {"name":"released_at","type":"datetime","default":"now","set_by":"system"}
    ]
  },

  "L4_Event_Schema": {
    "universality": "L4",
    "description": "JSON Schema descriptor for an event payload.",
    "required": [
      {"name":"schema_uri","type":"string","description":"l4://schemas/<name>/<ver>.json"},
      {"name":"version","type":"string"},
      {"name":"requires_sig_suite","type":"string","default":"SIG_ED25519_V1"},
      {"name":"sea_required","type":"boolean","default":False},
      {"name":"cps","type":"boolean","default":False}
    ],
    "optional": [
      {"name":"topic","type":"string","required":False,"description":"Concrete topic (e.g., 'presence.beacon')"},
      {"name":"topic_pattern","type":"string","required":False,"description":"Wildcard topic pattern (e.g., 'telemetry.state.*')"},
      {"name":"compat","type":"array","description":"Semver ranges compatible"},
      {"name":"bundle_id","type":"string","description":"Owning L4_Schema_Bundle"}
    ],
    "invariants": [
      "xor(topic, topic_pattern) = true"
    ]
  },

  "L4_Envelope_Schema": {
    "universality": "L4",
    "description": "Envelope shape & signing profile.",
    "required": [
      {"name":"name","type":"string","default":"ENV_STANDARD_V1"},
      {"name":"schema_uri","type":"string"},
      {"name":"version","type":"string"}
    ],
    "optional": [
      {"name":"required_headers","type":"array","default":
        ["id","ts","producer","schema_uri","version","signer","signature","sig_suite"]},
      {"name":"attestation_header","type":"string","default":"attestation_ref"},
      {"name":"sig_suite","type":"string","default":"SIG_ED25519_V1"}
    ]
  },

  "L4_Topic_Namespace": {
    "universality":"L4",
    "description":"Topic namespace (wildcards allowed).",
    "required":[
      {"name":"name","type":"string","description":"e.g., 'telemetry.state.*' or 'identity.snapshot.attest'"}
    ],
    "optional":[
      {"name":"notes","type":"string"}
    ]
  },

  "L4_Signature_Suite": {
    "universality":"L4",
    "description":"Signing algorithm/profile supported by validator.",
    "required":[
      {"name":"suite_id","type":"string","description":"e.g., 'SIG_ED25519_V1'"},
      {"name":"algo","type":"enum","enum_values":["ed25519","secp256k1","rsa"],"default":"ed25519"},
      {"name":"hash_algos","type":"array","default":["sha256","blake3"]}
    ],
    "optional":[
      {"name":"notes","type":"string"}
    ]
  },

  "L4_Governance_Policy": {
    "universality":"L4",
    "description":"Law/policy text with machine-enforceable expectations.",
    "required":[
      {"name":"policy_id","type":"string"},
      {"name":"hash","type":"string"},
      {"name":"uri","type":"string"}
    ],
    "optional":[
      {"name":"status","type":"enum","enum_values":["draft","active","deprecated"],"default":"active"},
      {"name":"summary","type":"string"}
    ]
  },

  "L4_Type_Index": {
    "universality":"L4",
    "description":"Catalog entry for a canonical type (U4_* / U3_* / Lx_*).",
    "required":[
      {"name":"type_name","type":"string"},
      {"name":"status","type":"enum","enum_values":["draft","active","deprecated"],"default":"active"},
      {"name":"schema_ref","type":"string","description":"l4://types/<type>@vN"}
    ],
    "optional":[
      {"name":"bundle_id","type":"string"},
      {"name":"notes","type":"string"}
    ]
  },

  "L4_Conformance_Suite": {
    "universality":"L4",
    "description":"Test suite for schemas/policies/topics/signature suites.",
    "required":[
      {"name":"suite_id","type":"string"},
      {"name":"semver","type":"string"},
      {"name":"cases","type":"array","description":"List of case descriptors"}
    ],
    "optional":[
      {"name":"pass_threshold","type":"float","range":[0.0,1.0],"default":0.95},
      {"name":"notes","type":"string"}
    ]
  },

  "L4_Conformance_Result": {
    "universality":"L4",
    "description":"Result of running a conformance suite.",
    "required":[
      {"name":"subject_ref","type":"string"},
      {"name":"suite_id","type":"string"},
      {"name":"pass_rate","type":"float","range":[0.0,1.0]},
      {"name":"ts","type":"datetime","default":"now","set_by":"system"}
    ],
    "optional":[
      {"name":"evidence_uri","type":"string"},
      {"name":"failures","type":"array"}
    ]
  },

  # Optional capability catalog (law names the capability)
  "L4_Capability": {
    "universality":"L4",
    "description":"Named capability that policies/tiers can unlock.",
    "required":[
      {"name":"capability_id","type":"string"},
      {"name":"description","type":"string"}
    ],
    "optional":[
      {"name":"risk_level","type":"enum","enum_values":["low","medium","high"],"default":"low"}
    ]
  }
}


# =============================================================================
# LINK FIELD SPECIFICATIONS (RICH)
# Canonical names prefixed U4_/U3_, with reverses, defaults, meta, invariants
# =============================================================================

LINK_FIELD_SPECS = {

  # =========================
  # Composition & Identity (U4)
  # =========================
  "U4_MEMBER_OF": {
    "universality": "U4",
    "reverse_name": "U4_HAS_MEMBER",
    "description": "Child → Parent composition.",
    "detailed_description": "Universal composition relation across L1–L4. "
                            "Must form a DAG; child.level ≤ parent.level. "
                            "Used for citizen→org, subentity→citizen, protocol-subsystem→protocol, etc.",
    "required": [
      {"name": "membership_type", "type": "enum",
       "enum_values": ["structural","functional","temporary","honorary"],
       "description": "Nature of membership"},
      {"name": "role", "type": "string",
       "description": "Role within the parent (e.g., 'frontend_team','governance_committee')"}
    ],
    "optional": [
      {"name": "since", "type": "datetime", "default": "now", "set_by": "sender",
       "description": "When membership began"},
      {"name": "until", "type": "datetime", "default": None, "set_by": "sender",
       "description": "When membership ends (if temporary)"},
      {"name": "forming_mindstate", "type": "string",
       "description": "Declarative state at formation",
       "detailed_description": "Declarative state at formation (e.g., 'deliberation','flow')"}
    ],
    "invariants": [
      "acyclic",                           # no cycles over repeated U4_MEMBER_OF
      "child.level <= parent.level"
    ],
    "cardinality": {"min": 0, "max": None}  # a node can have many parents in functional graphs (DAG)
  },

  "U4_ALIASES": {
    "universality": "U4",
    "reverse_name": "U4_ALIASES",  # symmetric
    "description": "Equivalence/alias relation.",
    "detailed_description": "A↔B indicate the same logical entity under different names or contexts.",
    "required": [
      {"name": "alias_type", "type": "enum",
       "enum_values": ["synonym","translation","historical_name","context_specific"]}
    ],
    "optional": [
      {"name": "context", "type": "string",
       "description": "Where this alias is used (e.g., 'community','technical_docs')"}
    ],
    "invariants": ["symmetric"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_MERGED_INTO": {
    "universality": "U4",
    "reverse_name": "U4_ABSORBED",
    "description": "Old → New merge; lineage preservation.",
    "detailed_description": "Sets old.status='merged'. New inherits selected fields from old.",
    "required": [
      {"name": "merge_timestamp", "type": "datetime", "default": "now", "set_by": "system"},
      {"name": "merge_reason", "type": "string"}
    ],
    "optional": [
      {"name": "absorbed_fields", "type": "array",
       "description": "Which fields on old were absorbed into new"}
    ],
    "invariants": ["origin.status = 'merged'"],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Governance & Capability (U4)
  # =========================
  "U4_GOVERNS": {
    "universality": "U4",
    "reverse_name": "U4_GOVERNED_BY",
    "description": "L4 subsystem governs a resource/domain.",
    "detailed_description": "Connects a protocol subsystem (SEA/CPS/UBC/RGS/AGL/…) to schemas, topics, policies, or capabilities it governs.",
    "required": [
      {"name": "governance_scope", "type": "string"},
      {"name": "authority_type", "type": "enum",
       "enum_values": ["policy_enforcement","resource_allocation","permission_granting","arbitration"]}
    ],
    "optional": [
      {"name": "policy_ref", "type": "string",
       "description": "URI to controlling document (e.g., 'l4://law/LAW-001')"}
    ],
    "invariants": ["source.level = L4"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_UNLOCKS": {
    "universality": "U4",
    "reverse_name": "U4_UNLOCKED_BY",
    "description": "Tier/Policy grants a capability.",
    "required": [
      {"name": "capability", "type": "string"},
      {"name": "unlock_condition", "type": "string"}
    ],
    "optional": [
      {"name": "expiration", "type": "datetime", "default": None}
    ],
    "invariants": [
      "origin.type_name IN {'L4_Autonomy_Tier','L4_Governance_Policy'}",
      "target.type_name = 'L4_Capability'"
    ],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Workflow & Assignment (U4)
  # =========================
  "U4_BLOCKED_BY": {
    "universality": "U4",
    "reverse_name": "U4_BLOCKS",
    "description": "Work_Item is blocked by a dependency/issue.",
    "required": [
      {"name": "blocking_reason", "type": "string"},
      {"name": "severity", "type": "enum",
       "enum_values": ["absolute","strong","partial"]}
    ],
    "optional": [
      {"name": "resolution_condition", "type": "string"}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_ASSIGNED_TO": {
    "universality": "U4",
    "reverse_name": "U4_ASSIGNEE_OF",
    "description": "Work_Item → Agent ownership.",
    "required": [],
    "optional": [
      {"name": "assignment_date", "type": "datetime", "default": "now"},
      {"name": "effort_estimate", "type": "string"}
    ],
    "invariants": ["max_one_assignee"],     # if you keep single ownership; else relax
    "cardinality": {"min": 0, "max": 1}
  },

  # =========================
  # Goals & Metrics (U4)
  # =========================
  "U4_DRIVES": {
    "universality": "U4",
    "reverse_name": "U4_DRIVEN_BY",
    "description": "Value/Motivation drives a Goal.",
    "required": [
      {"name": "drive_type", "type": "enum",
       "enum_values": ["intrinsic","extrinsic","strategic","ethical","pragmatic"]},
      {"name": "drive_strength", "type": "float", "range": [0.0,1.0], "default": 0.5}
    ],
    "optional": [],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_TARGETS": {
    "universality": "U4",
    "reverse_name": "U4_TARGET_OF",
    "description": "Goal targets a Metric/Outcome.",
    "required": [
      {"name": "target_type", "type": "enum",
       "enum_values": ["state_change","metric_threshold","deliverable","capability"]},
      {"name": "success_criteria", "type": "string"}
    ],
    "optional": [
      {"name": "target_date", "type": "datetime"}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_MEASURES": {
    "universality": "U4",
    "reverse_name": "U4_MEASURED_BY",
    "description": "Measurement measures a Metric.",
    "required": [],
    "optional": [
      {"name": "measurement_unit", "type": "string"}
    ],
    "invariants": ["origin.type_name = 'U4_Measurement'", "target.type_name = 'U4_Metric'"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_CONTROLS": {
    "universality": "U4",
    "reverse_name": "U4_CONTROLLED_BY",
    "description": "Mechanism controls/regulates a Metric.",
    "required": [
      {"name": "control_type", "type": "enum",
       "enum_values": ["regulates","optimizes","constrains","monitors"]}
    ],
    "optional": [],
    "invariants": ["target.type_name = 'U4_Metric'"],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Evidence & Docs (U4)
  # =========================
  "U4_EVIDENCED_BY": {
    "universality": "U4",
    "reverse_name": "U4_JUSTIFIES",
    "description": "Claim is supported by Proof/Attestation/Document.",
    "required": [
      {"name": "evidence_type", "type": "enum",
       "enum_values": ["attestation","measurement","document","witness","cryptographic_proof"]},
      {"name": "confidence", "type": "float", "range": [0.0,1.0], "default": 0.7}
    ],
    "optional": [],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_DOCUMENTS": {
    "universality": "U4",
    "reverse_name": "U4_DOCUMENTED_BY",
    "description": "Knowledge object documents a policy/schema/capability.",
    "required": [],
    "optional": [
      {"name": "doc_role", "type": "enum",
       "enum_values": ["adr","spec","runbook","guide","reference","policy_summary"],
       "default": "spec"}
    ],
    "invariants": ["origin.type_name = 'U4_Knowledge_Object'"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_REFERENCES": {
    "universality": "U4",
    "reverse_name": "U4_REFERENCED_BY",
    "description": "Doc/Code references an external resource.",
    "required": [
      {"name": "reference_type", "type": "enum",
       "enum_values": ["citation","dependency","inspiration","comparison"]}
    ],
    "optional": [
      {"name": "uri", "type": "string"}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_ABOUT": {
    "universality": "U4",
    "reverse_name": "U4_SUBJECT_OF",
    "description": "Content is about the subject node.",
    "required": [],
    "optional": [
      {"name": "focus_type", "type": "enum",
       "enum_values": ["primary_subject","secondary_mention","contextual_reference"],
       "default": "primary_subject"}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Dependencies & Causality (U4)
  # =========================
  "U4_DEPENDS_ON": {
    "universality": "U4",
    "reverse_name": "U4_REQUIRED_FOR",
    "description": "A depends on B (cannot function without).",
    "required": [
      {"name": "dependency_type", "type": "enum",
       "enum_values": ["runtime","build_time","data","infrastructure","logical"]},
      {"name": "criticality", "type": "enum",
       "enum_values": ["blocking","important","optional"], "default": "important"}
    ],
    "optional": [],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_ACTIVATES": {
    "universality": "U4",
    "reverse_name": "U4_ACTIVATED_BY",
    "description": "Stimulus activates Response/Subentity.",
    "required": [],
    "optional": [
      {"name": "activation_threshold", "type": "float", "range": [0.0,1.0], "default": 0.5}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_TRIGGERED_BY": {
    "universality": "U4",
    "reverse_name": "U4_TRIGGERS",
    "description": "Event was triggered by a cause.",
    "required": [],
    "optional": [
      {"name": "trigger_strength", "type": "float", "range": [0.0,1.0], "default": 0.5}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_SUPPRESSES": {
    "universality": "U4",
    "reverse_name": "U4_SUPPRESSED_BY",
    "description": "Inhibitor suppresses target.",
    "required": [],
    "optional": [
      {"name": "suppression_mechanism", "type": "string"}
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_RELATES_TO": {
    "universality": "U4",
    "reverse_name": "U4_RELATES_TO",   # symmetric
    "description": "Generic association; use sparingly.",
    "required": [
      {"name": "relationship_strength", "type": "enum",
       "enum_values": ["strong","moderate","weak","exploratory"], "default": "exploratory"},
      {"name": "needs_refinement", "type": "boolean", "default": True}
    ],
    "optional": [
      {"name": "refinement_candidates", "type": "array",
       "description": "Potential more specific link types (e.g., 'U4_DEPENDS_ON','U4_DOCUMENTS')"}
    ],
    "invariants": ["symmetric"],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Membrane traceability (U4)
  # =========================
  "U4_EMITS": {
    "universality": "U4",
    "reverse_name": "U4_EMITTED_BY",
    "description": "Code artifact emits events to a topic namespace.",
    "required": [],
    "optional": [
      {"name": "example_topics", "type": "array"},
      {"name": "last_seen", "type": "datetime", "set_by": "system"}
    ],
    "invariants": ["origin = U4_Code_Artifact", "target = L4_Topic_Namespace"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_CONSUMES": {
    "universality": "U4",
    "reverse_name": "U4_CONSUMED_BY",
    "description": "Code artifact consumes (subscribes to) a topic namespace.",
    "required": [],
    "optional": [
      {"name": "example_topics", "type": "array"},
      {"name": "last_seen", "type": "datetime", "set_by": "system"}
    ],
    "invariants": ["origin = U4_Code_Artifact", "target = L4_Topic_Namespace"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_IMPLEMENTS": {
    "universality": "U4",
    "reverse_name": "U4_IMPLEMENTED_BY",
    "description": "Code artifact implements a policy/schema/capability.",
    "required": [],
    "optional": [
      {"name": "evidence_rules_passed", "type": "array",
       "description": "mp-lint rule codes (e.g., ['R-001','R-002'])"},
      {"name": "last_lint_ts", "type": "datetime", "set_by": "system"}
    ],
    "invariants": ["origin = U4_Code_Artifact", "target ∈ {U4_Governance_Policy,U4_Event_Schema,U4_Capability}"],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_TESTS": {
    "universality": "U4",
    "reverse_name": "U4_TESTED_BY",
    "description": "Test artifact covers a policy/schema/capability.",
    "required": [],
    "optional": [
      {"name": "pass_rate", "type": "float", "range": [0.0,1.0]},
      {"name": "run_id", "type": "string"},
      {"name": "last_run_ts", "type": "datetime", "set_by": "system"}
    ],
    "invariants": ["origin = U4_Code_Artifact (test)"],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Risk & Econ & Participation (U3 — excludes L4)
  # =========================
  "U3_IMPACTS": {
    "universality": "U3",
    "reverse_name": "U3_IMPACTED_BY",
    "description": "Cause → Effect causal impact.",
    "required": [
      {"name": "impact_type", "type": "enum",
       "enum_values": ["positive","negative","neutral","mixed"]},
      {"name": "impact_magnitude", "type": "float", "range": [0.0,1.0]}
    ],
    "optional": [
      {"name": "impact_domain", "type": "string"}
    ],
    "invariants": ["levels ∈ {L1,L2,L3}"],
    "cardinality": {"min": 0, "max": None}
  },

  "U3_MITIGATED_BY": {
    "universality": "U3",
    "reverse_name": "U3_MITIGATES",
    "description": "Risk mitigated by Control.",
    "required": [
      {"name": "mitigation_effectiveness", "type": "float", "range": [0.0,1.0], "default": 0.5},
      {"name": "mitigation_type", "type": "enum",
       "enum_values": ["prevents","reduces","transfers","accepts"]}
    ],
    "optional": [],
    "invariants": ["levels ∈ {L1,L2,L3}"],
    "cardinality": {"min": 0, "max": None}
  },

  "U3_PARTICIPATES_IN": {
    "universality": "U3",
    "reverse_name": "U3_HAS_PARTICIPANT",
    "description": "Agent participates in Event/Community.",
    "required": [
      {"name": "participation_type", "type": "enum",
       "enum_values": ["organizer","active_participant","observer","contributor"]}
    ],
    "optional": [
      {"name": "participation_frequency", "type": "string", "default": "occasional"}
    ],
    "invariants": ["levels ∈ {L1,L2,L3}"],
    "cardinality": {"min": 0, "max": None}
  },

  "U3_SETTLED_BY": {
    "universality": "U3",
    "reverse_name": "U3_SETS",
    "description": "Dispute settled by Outcome.",
    "required": [
      {"name": "settlement_type", "type": "enum",
       "enum_values": ["consensus","arbitration","voting","mediation","ruling"]},
      {"name": "settlement_timestamp", "type": "datetime", "default": "now"}
    ],
    "optional": [
      {"name": "settlement_terms", "type": "string"}
    ],
    "invariants": ["levels ∈ {L1,L2,L3}"],
    "cardinality": {"min": 0, "max": None}
  },

  # =========================
  # Registry & Schema Management (U4)
  # =========================
  "U4_PUBLISHES_SCHEMA": {
    "universality": "U4",
    "reverse_name": "U4_PUBLISHED_IN",
    "description": "Bundle publishes a schema/type record.",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name = 'L4_Schema_Bundle'",
      "target.type_name IN {'L4_Event_Schema','L4_Envelope_Schema','L4_Type_Index'}"
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_MAPS_TO_TOPIC": {
    "universality": "U4",
    "reverse_name": "U4_TOPIC_HAS_SCHEMA",
    "description": "Event schema belongs to a topic namespace.",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name = 'L4_Event_Schema'",
      "target.type_name = 'L4_Topic_Namespace'"
    ],
    "cardinality": {"min": 1, "max": 1}
  },

  "U4_REQUIRES_SIG": {
    "universality": "U4",
    "reverse_name": "U4_REQUIRED_BY",
    "description": "Envelope/schema requires a signature suite.",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name IN {'L4_Envelope_Schema','L4_Event_Schema'}",
      "target.type_name = 'L4_Signature_Suite'"
    ],
    "cardinality": {"min": 1, "max": None}
  },

  "U4_CERTIFIES_CONFORMANCE": {
    "universality": "U4",
    "reverse_name": "U4_CONFORMANCE_CERTIFIED_BY",
    "description": "Suite certifies conformance for a target.",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name = 'L4_Conformance_Suite'",
      "target.type_name IN {'L4_Signature_Suite','L4_Schema_Bundle','L4_Topic_Namespace','L4_Type_Index'}"
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_SUPERSEDES": {
    "universality": "U4",
    "reverse_name": "U4_SUPERSEDED_BY",
    "description": "New bundle supersedes old bundle.",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name = 'L4_Schema_Bundle'",
      "target.type_name = 'L4_Schema_Bundle'",
      "origin.hash <> target.hash"
    ],
    "cardinality": {"min": 0, "max": None}
  },

  "U4_DEPRECATES": {
    "universality": "U4",
    "reverse_name": "U4_DEPRECATED_BY",
    "description": "Bundle deprecates an older bundle (non-linear).",
    "required": [],
    "optional": [],
    "invariants": [
      "origin.type_name = 'L4_Schema_Bundle'",
      "target.type_name = 'L4_Schema_Bundle'"
    ],
    "cardinality": {"min": 0, "max": None}
  }
}

# =============================================================================
# DEPRECATIONS (old_name → new_name mapping; 1-release grace)
# =============================================================================
DEPRECATIONS = {
  # Capability unification: U4_Capability and L4_Capability were duplicates
  # Keep L4_Capability as canonical (capabilities are protocol-level law)
  # Rationale: Capabilities are defined by L4 policy/law, not emergent at each level
  "U4_Capability": "L4_Capability",

  # Add other deprecated type/link names here as they emerge
}

# =============================================================================
# QUALITY GATES (for CI/lints)
# =============================================================================
CI_LINTS = {
  "label_equals_type_name": True,
  "universality_bounds": True,      # U3 only at L1–L3
  "single_universal_label": True,   # exactly one of U3_/U4_/Lx_
  "no_unprefixed_links": True,      # relations must start with U3_ or U4_
  "no_deprecated_links": list(DEPRECATIONS.keys()),
  "auto_fields_meta": {
      "nodes": ["created_at","updated_at","valid_from","valid_to","visibility","commitments","proof_uri"],
      "links": ["created_at","updated_at","valid_from","valid_to","commitments"],
      "require": ["default","set_by","read_only","computed"]   # present when applicable
  }
}

# =============================================================================
# END OF FILE
# =============================================================================