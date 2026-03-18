# Repository Map: mind-protocol

*Generated: 2026-03-14 17:10*

- **Files:** 366
- **Directories:** 78
- **Total Size:** 3.4M
- **Doc Files:** 277
- **Code Files:** 87
- **Areas:** 12 (docs/ subfolders)
- **Modules:** 33 (subfolders in areas)
- **DOCS Links:** 44 (0.51 avg per code file)

- markdown: 277
- python: 73
- javascript: 8
- shell: 4
- rust: 1
- typescript: 1

```mermaid
graph TD
    schema[schema]
    registry[registry]
    laws[laws]
    economy[economy]
    membrane[membrane]
    manifesto[manifesto]
    compliance[compliance]
    api_sse[api_sse]
```

| Module | Code | Docs | Lines | Files | Dependencies |
|--------|------|------|-------|-------|--------------|
| schema | `l4/schema/` | `docs/l4/schema/` | 384 | 5 | - |
| registry | `l4/registry/` | `docs/l4/registry/` | 3024 | 12 | - |
| laws | `l4/laws/` | `docs/l4/laws/` | 238 | 4 | - |
| economy | `economy/` | `docs/economy/` | 3455 | 31 | - |
| membrane | `None` | `docs/membrane/` | 0 | 0 | - |
| manifesto | `None` | `docs/manifesto/` | 0 | 0 | - |
| compliance | `None` | `docs/compliance/` | 0 | 0 | - |
| api_sse | `api/` | `docs/api/sse/` | 0 | 7 | - |

```
├── api/
│   ├── graphql/
│   │   └── (..3 more files)
│   ├── websocket/
│   │   └── (..4 more files)
│   └── (..1 more files)
├── docs/ (2.7M)
│   ├── api/ (22.2K)
│   │   └── sse/ (22.2K)
│   │       ├── ALGORITHM_SSE_API.md (3.2K)
│   │       ├── BEHAVIORS_SSE_API.md (2.5K)
│   │       ├── HEALTH_SSE_API.md (4.0K)
│   │       ├── IMPLEMENTATION_SSE_API.md (3.7K)
│   │       ├── OBJECTIVES_SSE_API.md (1.2K)
│   │       ├── PATTERNS_SSE_API.md (2.6K)
│   │       ├── SYNC_SSE_API.md (1.3K)
│   │       └── VALIDATION_SSE_API.md (3.7K)
│   ├── citizen/ (171.1K)
│   │   ├── autonomy/ (13.7K)
│   │   │   ├── CONCEPT_Autonomy.md (7.2K)
│   │   │   └── OBJECTIVES_Autonomy.md (6.6K)
│   │   ├── code-quality/ (9.2K)
│   │   │   ├── CONCEPT_Code_Quality.md (4.8K)
│   │   │   └── OBJECTIVES_Code_Quality.md (4.4K)
│   │   ├── persistence/ (12.2K)
│   │   │   ├── CONCEPT_Persistence.md (6.6K)
│   │   │   └── OBJECTIVES_Persistence.md (5.6K)
│   │   ├── personalization/ (8.6K)
│   │   │   ├── CONCEPT_Personalization.md (5.2K)
│   │   │   └── OBJECTIVES_Personalization.md (3.5K)
│   │   ├── spawning/ (29.4K)
│   │   │   ├── ALGORITHM_Spawning.md (11.5K)
│   │   │   ├── BEHAVIORS_Spawning.md (2.4K)
│   │   │   ├── HEALTH_Spawning.md (1.0K)
│   │   │   ├── IMPLEMENTATION_Spawning.md (2.1K)
│   │   │   ├── OBJECTIVES_Spawning.md (1.5K)
│   │   │   ├── PATTERNS_Spawning.md (4.1K)
│   │   │   ├── SYNC_Spawning.md (3.7K)
│   │   │   └── VALIDATION_Spawning.md (3.0K)
│   │   ├── wallet-recovery/ (36.3K)
│   │   │   ├── ALGORITHM_Wallet_Recovery.md (9.1K)
│   │   │   ├── BEHAVIORS_Wallet_Recovery.md (5.0K)
│   │   │   ├── HEALTH_Wallet_Recovery.md (2.5K)
│   │   │   ├── IMPLEMENTATION_Wallet_Recovery.md (6.0K)
│   │   │   ├── OBJECTIVES_Wallet_Recovery.md (1.3K)
│   │   │   ├── PATTERNS_Wallet_Recovery.md (4.5K)
│   │   │   ├── SYNC_Wallet_Recovery.md (4.3K)
│   │   │   └── VALIDATION_Wallet_Recovery.md (3.4K)
│   │   └── work/ (61.6K)
│   │       ├── ALGORITHM_Work.md (11.8K)
│   │       ├── BEHAVIORS_Work.md (7.4K)
│   │       ├── HEALTH_Work.md (5.3K)
│   │       ├── IMPLEMENTATION_Work.md (6.6K)
│   │       ├── OBJECTIVES_Work.md (3.4K)
│   │       ├── PATTERNS_Work.md (11.6K)
│   │       ├── SYNC_Work.md (5.2K)
│   │       ├── VALIDATION_Work.md (5.3K)
│   │       └── VOCABULARY_Work.md (5.0K)
│   ├── cognitive/ (350.1K)
│   │   ├── CONCEPT_Class_4_Structure_Taxonomy.md (19.0K)
│   │   ├── CONCEPT_Edge_Width_Modulation.md (12.3K)
│   │   ├── CONCEPT_Psychedelic_Parameter_Modulation.md (11.8K)
│   │   ├── CONCEPT_Skewed_Emergence.md (12.8K)
│   │   ├── CONCEPT_Sphere_Collision_Ontology.md (21.0K)
│   │   ├── CONCEPT_Wolfram_Class_4_Substrate.md (11.5K)
│   │   ├── NARRATIVE_Universe_As_Sphere_Collision.md (55.7K)
│   │   ├── PAPER_Consciousness_As_Class_4_Dynamics.md (22.5K)
│   │   ├── PATTERNS_Exploration_Mechanics.md (14.0K)
│   │   ├── PATTERNS_Graph_Dynamics.md (12.9K)
│   │   └── (..20 more files)
│   ├── compliance/ (4.7K)
│   │   ├── PATTERNS_Compliance.md (4.2K)
│   │   └── SYNC_Compliance.md (539)
│   ├── economy/ (574.2K)
│   │   ├── bonds/ (50.4K)
│   │   │   ├── ALGORITHM_Bonds.md (9.5K)
│   │   │   ├── BEHAVIORS_Bonds.md (6.8K)
│   │   │   ├── HEALTH_Bonds.md (5.8K)
│   │   │   ├── IMPLEMENTATION_Bonds.md (5.4K)
│   │   │   ├── OBJECTIVES_Bonds.md (3.4K)
│   │   │   ├── PATTERNS_Bonds.md (5.8K)
│   │   │   ├── SYNC_Bonds.md (6.2K)
│   │   │   └── VALIDATION_Bonds.md (7.5K)
│   │   ├── cascade-utility/ (55.1K)
│   │   │   ├── ALGORITHM_Cascade_Utility.md (9.5K)
│   │   │   ├── BEHAVIORS_Cascade_Utility.md (5.9K)
│   │   │   ├── CONCEPT_Cascade_Utility.md (3.1K)
│   │   │   ├── HEALTH_Cascade_Utility.md (6.8K)
│   │   │   ├── IMPLEMENTATION_Cascade_Utility.md (5.0K)
│   │   │   ├── OBJECTIVES_Cascade_Utility.md (4.2K)
│   │   │   ├── PATTERNS_Cascade_Utility.md (6.1K)
│   │   │   ├── SYNC_Cascade_Utility.md (7.0K)
│   │   │   └── VALIDATION_Cascade_Utility.md (7.4K)
│   │   ├── metabolic/ (137.5K)
│   │   │   ├── ALGORITHM_Metabolic_Economy.md (31.1K)
│   │   │   ├── BEHAVIORS_Metabolic_Economy.md (12.7K)
│   │   │   ├── IMPLEMENTATION_Metabolic_Economy.md (45.5K)
│   │   │   ├── OBJECTIVES_Metabolic_Economy.md (7.4K)
│   │   │   ├── PATTERNS_Metabolic_Economy.md (13.4K)
│   │   │   ├── SYNC_Metabolic_Economy.md (14.1K)
│   │   │   └── VALIDATION_Metabolic_Economy.md (13.3K)
│   │   ├── organism-model/ (47.8K)
│   │   │   ├── ALGORITHM_Organism_Model.md (8.8K)
│   │   │   ├── BEHAVIORS_Organism_Model.md (4.8K)
│   │   │   ├── CONCEPT_Organism_Model.md (3.9K)
│   │   │   ├── HEALTH_Organism_Model.md (5.8K)
│   │   │   ├── IMPLEMENTATION_Organism_Model.md (4.1K)
│   │   │   ├── OBJECTIVES_Organism_Model.md (4.0K)
│   │   │   ├── PATTERNS_Organism_Model.md (5.1K)
│   │   │   ├── SYNC_Organism_Model.md (5.8K)
│   │   │   └── VALIDATION_Organism_Model.md (5.8K)
│   │   ├── storage-tax/ (39.1K)
│   │   │   ├── ALGORITHM_Storage_Tax.md (7.6K)
│   │   │   ├── BEHAVIORS_Storage_Tax.md (5.9K)
│   │   │   ├── HEALTH_Storage_Tax.md (4.5K)
│   │   │   ├── IMPLEMENTATION_Storage_Tax.md (3.3K)
│   │   │   ├── OBJECTIVES_Storage_Tax.md (3.1K)
│   │   │   ├── PATTERNS_Storage_Tax.md (6.0K)
│   │   │   ├── SYNC_Storage_Tax.md (3.7K)
│   │   │   └── VALIDATION_Storage_Tax.md (5.1K)
│   │   ├── token/ (52.4K)
│   │   │   ├── ALGORITHM_Token.md (8.6K)
│   │   │   ├── BEHAVIORS_Token.md (5.0K)
│   │   │   ├── IMPLEMENTATION_Token.md (8.1K)
│   │   │   ├── OBJECTIVES_Token.md (2.9K)
│   │   │   ├── PATTERNS_Token.md (5.8K)
│   │   │   ├── SPL_TOKEN_2022_SPECS.md (9.5K)
│   │   │   ├── SYNC_Token.md (5.5K)
│   │   │   └── VALIDATION_Token.md (7.0K)
│   │   ├── ubc/ (79.6K)
│   │   │   ├── ALGORITHM_UBC.md (17.5K)
│   │   │   ├── BEHAVIORS_UBC.md (9.8K)
│   │   │   ├── CONCEPT_UBC.md (3.8K)
│   │   │   ├── HEALTH_UBC.md (7.0K)
│   │   │   ├── IMPLEMENTATION_UBC.md (8.8K)
│   │   │   ├── OBJECTIVES_UBC.md (5.3K)
│   │   │   ├── PATTERNS_UBC.md (9.8K)
│   │   │   ├── SYNC_UBC.md (7.2K)
│   │   │   └── VALIDATION_UBC.md (10.5K)
│   │   ├── value-creation/ (70.4K)
│   │   │   ├── ALGORITHM_Value_Creation.md (35.0K)
│   │   │   └── ALGORITHM_Value_Destruction.md (35.4K)
│   │   ├── MIND_TOKEN_AGENT_BOOTSTRAP.md (11.8K)
│   │   ├── OBJECTIVES_Economy.md (3.9K)
│   │   ├── PATTERNS_Economy.md (12.5K)
│   │   └── SYNC_Economy.md (13.5K)
│   ├── governance/ (102.7K)
│   │   └── sovereign-cascade/ (102.7K)
│   │       ├── ALGORITHM_Sovereign_Cascade.md (16.3K)
│   │       ├── BEHAVIORS_Sovereign_Cascade.md (9.7K)
│   │       ├── DECREE_001_Emergency_Council.md (7.3K)
│   │       ├── IMPLEMENTATION_Sovereign_Cascade.md (12.2K)
│   │       ├── MEETING_001_First_Council.md (5.7K)
│   │       ├── OBJECTIVES_Sovereign_Cascade.md (5.1K)
│   │       ├── PATTERNS_Sovereign_Cascade.md (10.4K)
│   │       ├── SOVEREIGN_CASCADE_MANIFESTO.md (16.6K)
│   │       ├── SYNC_Sovereign_Cascade.md (11.3K)
│   │       └── VALIDATION_Sovereign_Cascade.md (8.1K)
│   ├── l4/ (99.6K)
│   │   ├── laws/ (26.3K)
│   │   │   ├── ALGORITHM_Laws.md (3.8K)
│   │   │   ├── BEHAVIORS_Laws.md (3.2K)
│   │   │   ├── HEALTH_Laws.md (4.1K)
│   │   │   ├── IMPLEMENTATION_Laws.md (3.7K)
│   │   │   ├── OBJECTIVES_Laws.md (936)
│   │   │   ├── PATTERNS_Laws.md (3.4K)
│   │   │   ├── SYNC_Laws.md (3.2K)
│   │   │   └── VALIDATION_Laws.md (3.9K)
│   │   ├── registry/ (46.3K)
│   │   │   ├── ALGORITHM_Registry.md (11.3K)
│   │   │   ├── BEHAVIORS_Registry.md (3.8K)
│   │   │   ├── HEALTH_Registry.md (3.3K)
│   │   │   ├── IMPLEMENTATION_Registry.md (5.9K)
│   │   │   ├── OBJECTIVES_Registry.md (1.6K)
│   │   │   ├── PATTERNS_Registry.md (6.1K)
│   │   │   ├── SYNC_Registry.md (6.7K)
│   │   │   ├── VALIDATION_Registry.md (2.8K)
│   │   │   └── VOCABULARY_Registry.md (4.9K)
│   │   ├── schema/ (20.8K)
│   │   │   ├── ALGORITHM_Schema.md (2.8K)
│   │   │   ├── BEHAVIORS_Schema.md (2.3K)
│   │   │   ├── HEALTH_Schema.md (2.9K)
│   │   │   ├── IMPLEMENTATION_Schema.md (2.8K)
│   │   │   ├── OBJECTIVES_Schema.md (1.6K)
│   │   │   ├── PATTERNS_Schema.md (2.5K)
│   │   │   ├── SYNC_Schema.md (3.2K)
│   │   │   └── VALIDATION_Schema.md (2.6K)
│   │   └── PATTERNS_L4.md (6.3K)
│   ├── manifesto/ (82.4K)
│   │   ├── DIFFERENTIATION_FRAMEWORK.md (7.0K)
│   │   ├── MIND_MANIFESTO.md (8.9K)
│   │   ├── THE_BILATERAL_BOND_MANIFESTO.md (13.2K)
│   │   ├── THE_ENLIGHTENED_CITIZEN.md (22.3K)
│   │   ├── THE_SPAWNING_MANIFESTO.md (22.7K)
│   │   └── THE_WORK_MANIFESTO.md (8.3K)
│   ├── membrane/ (112.3K)
│   │   ├── ALGORITHM_Membrane_System.md (10.0K)
│   │   ├── HEALTH_Membrane_System.md (12.0K)
│   │   ├── IMPLEMENTATION_Membrane_System.md (12.0K)
│   │   ├── MAPPING_Doctor_Issues_To_Protocols.md (5.6K)
│   │   ├── MAPPING_Issue_Type_Verification.md (15.8K)
│   │   ├── PATTERNS_Membrane_System.md (8.6K)
│   │   ├── SKILLS_AND_PROTOCOLS_Mapping.md (9.9K)
│   │   ├── SYNC_Membrane_System_archive_2025-12.md (9.5K)
│   │   ├── VALIDATION_Completion_Verification.md (11.6K)
│   │   ├── VALIDATION_Membrane_System.md (5.2K)
│   │   └── (..3 more files)
│   ├── product/ (787.5K)
│   │   ├── brief-matinal/ (75.0K)
│   │   │   ├── ALGORITHM_Brief_Matinal.md (15.7K)
│   │   │   ├── BEHAVIORS_Brief_Matinal.md (10.5K)
│   │   │   ├── IMPLEMENTATION_Brief_Matinal.md (17.4K)
│   │   │   ├── OBJECTIVES_Brief_Matinal.md (4.0K)
│   │   │   ├── PATTERNS_Brief_Matinal.md (10.2K)
│   │   │   ├── SYNC_Brief_Matinal.md (10.7K)
│   │   │   └── VALIDATION_Brief_Matinal.md (6.5K)
│   │   ├── calendar-bridge/ (81.2K)
│   │   │   ├── ALGORITHM_Calendar_Bridge.md (17.5K)
│   │   │   ├── BEHAVIORS_Calendar_Bridge.md (9.9K)
│   │   │   ├── HEALTH_Calendar_Bridge.md (10.4K)
│   │   │   ├── IMPLEMENTATION_Calendar_Bridge.md (15.5K)
│   │   │   ├── OBJECTIVES_Calendar_Bridge.md (3.6K)
│   │   │   ├── PATTERNS_Calendar_Bridge.md (8.3K)
│   │   │   ├── SYNC_Calendar_Bridge.md (9.2K)
│   │   │   └── VALIDATION_Calendar_Bridge.md (6.8K)
│   │   ├── chat-bridges/ (82.3K)
│   │   │   ├── ALGORITHM_Chat_Bridges.md (17.5K)
│   │   │   ├── BEHAVIORS_Chat_Bridges.md (11.5K)
│   │   │   ├── IMPLEMENTATION_Chat_Bridges.md (21.5K)
│   │   │   ├── OBJECTIVES_Chat_Bridges.md (4.3K)
│   │   │   ├── PATTERNS_Chat_Bridges.md (9.0K)
│   │   │   ├── SYNC_Chat_Bridges.md (11.0K)
│   │   │   └── VALIDATION_Chat_Bridges.md (7.5K)
│   │   ├── duo-mode/ (74.3K)
│   │   │   ├── ALGORITHM_Duo_Mode.md (13.4K)
│   │   │   ├── BEHAVIORS_Duo_Mode.md (11.2K)
│   │   │   ├── IMPLEMENTATION_Duo_Mode.md (18.8K)
│   │   │   ├── OBJECTIVES_Duo_Mode.md (4.1K)
│   │   │   ├── PATTERNS_Duo_Mode.md (8.9K)
│   │   │   ├── SYNC_Duo_Mode.md (9.9K)
│   │   │   └── VALIDATION_Duo_Mode.md (8.0K)
│   │   ├── email-bridge/ (70.3K)
│   │   │   ├── ALGORITHM_Email_Bridge.md (18.0K)
│   │   │   ├── BEHAVIORS_Email_Bridge.md (9.1K)
│   │   │   ├── IMPLEMENTATION_Email_Bridge.md (16.0K)
│   │   │   ├── OBJECTIVES_Email_Bridge.md (4.4K)
│   │   │   ├── PATTERNS_Email_Bridge.md (7.9K)
│   │   │   ├── SYNC_Email_Bridge.md (8.3K)
│   │   │   └── VALIDATION_Email_Bridge.md (6.7K)
│   │   ├── llm-router/ (68.6K)
│   │   │   ├── ALGORITHM_LLM_Router.md (13.1K)
│   │   │   ├── BEHAVIORS_LLM_Router.md (10.7K)
│   │   │   ├── IMPLEMENTATION_LLM_Router.md (16.2K)
│   │   │   ├── OBJECTIVES_LLM_Router.md (3.9K)
│   │   │   ├── PATTERNS_LLM_Router.md (8.6K)
│   │   │   ├── SYNC_LLM_Router.md (9.8K)
│   │   │   └── VALIDATION_LLM_Router.md (6.2K)
│   │   ├── react-native-app/ (89.7K)
│   │   │   ├── ALGORITHM_React_Native_App.md (14.4K)
│   │   │   ├── BEHAVIORS_React_Native_App.md (12.0K)
│   │   │   ├── HEALTH_React_Native_App.md (12.5K)
│   │   │   ├── IMPLEMENTATION_React_Native_App.md (20.3K)
│   │   │   ├── OBJECTIVES_React_Native_App.md (3.8K)
│   │   │   ├── PATTERNS_React_Native_App.md (9.7K)
│   │   │   ├── SYNC_React_Native_App.md (9.0K)
│   │   │   └── VALIDATION_React_Native_App.md (8.1K)
│   │   ├── stripe-paywall/ (83.0K)
│   │   │   ├── ALGORITHM_Stripe_Paywall.md (15.7K)
│   │   │   ├── BEHAVIORS_Stripe_Paywall.md (12.6K)
│   │   │   ├── IMPLEMENTATION_Stripe_Paywall.md (23.0K)
│   │   │   ├── OBJECTIVES_Stripe_Paywall.md (4.5K)
│   │   │   ├── PATTERNS_Stripe_Paywall.md (9.6K)
│   │   │   ├── SYNC_Stripe_Paywall.md (10.4K)
│   │   │   └── VALIDATION_Stripe_Paywall.md (7.3K)
│   │   ├── wearable-bridges/ (88.6K)
│   │   │   ├── ALGORITHM_Wearable_Bridges.md (14.1K)
│   │   │   ├── BEHAVIORS_Wearable_Bridges.md (10.7K)
│   │   │   ├── HEALTH_Wearable_Bridges.md (12.7K)
│   │   │   ├── IMPLEMENTATION_Wearable_Bridges.md (18.8K)
│   │   │   ├── OBJECTIVES_Wearable_Bridges.md (5.0K)
│   │   │   ├── PATTERNS_Wearable_Bridges.md (10.6K)
│   │   │   ├── SYNC_Wearable_Bridges.md (10.6K)
│   │   │   └── VALIDATION_Wearable_Bridges.md (6.2K)
│   │   └── webapp-b2c/ (74.4K)
│   │       ├── ALGORITHM_WebApp_B2C.md (11.1K)
│   │       ├── BEHAVIORS_WebApp_B2C.md (8.8K)
│   │       ├── HEALTH_WebApp_B2C.md (10.7K)
│   │       ├── IMPLEMENTATION_WebApp_B2C.md (15.0K)
│   │       ├── OBJECTIVES_WebApp_B2C.md (4.6K)
│   │       ├── PATTERNS_WebApp_B2C.md (8.3K)
│   │       ├── SYNC_WebApp_B2C.md (9.7K)
│   │       └── VALIDATION_WebApp_B2C.md (6.3K)
│   ├── schema/ (140.5K)
│   │   ├── l3_emotional_coloring/ (79.6K)
│   │   │   ├── ALGORITHM_L3_Emotional_Coloring.md (18.4K)
│   │   │   ├── BEHAVIORS_L3_Emotional_Coloring.md (8.8K)
│   │   │   ├── HEALTH_L3_Emotional_Coloring.md (6.6K)
│   │   │   ├── IMPLEMENTATION_L3_Emotional_Coloring.md (13.4K)
│   │   │   ├── OBJECTIVES_L3_Emotional_Coloring.md (9.0K)
│   │   │   ├── PATTERNS_L3_Emotional_Coloring.md (11.7K)
│   │   │   ├── SYNC_L3_Emotional_Coloring.md (4.2K)
│   │   │   └── VALIDATION_L3_Emotional_Coloring.md (7.5K)
│   │   └── universe_links/ (60.9K)
│   │       ├── ALGORITHM_Universe_Links.md (25.8K)
│   │       ├── OBJECTIVES_Universe_Links.md (4.8K)
│   │       ├── PATTERNS_Universe_Links.md (19.0K)
│   │       ├── SYNC_Universe_Links.md (3.5K)
│   │       └── VALIDATION_Universe_Links.md (7.9K)
│   ├── security/ (132.9K)
│   │   └── space_encryption/ (132.9K)
│   │       ├── ALGORITHM_Space_Encryption.md (17.9K)
│   │       ├── BEHAVIORS_Space_Encryption.md (10.9K)
│   │       ├── CONCEPT_Space_Encryption.md (7.2K)
│   │       ├── HEALTH_Space_Encryption.md (25.8K)
│   │       ├── IMPLEMENTATION_Space_Encryption.md (28.1K)
│   │       ├── OBJECTIVES_Space_Encryption.md (6.3K)
│   │       ├── PATTERNS_Space_Encryption.md (16.9K)
│   │       ├── SYNC_Space_Encryption.md (13.1K)
│   │       └── VALIDATION_Space_Encryption.md (6.6K)
│   ├── ARCHITECTURE.md (4.3K)
│   ├── MAPPING.md (8.9K)
│   ├── TAXONOMY.md (6.3K)
│   └── map.md (82.5K)
├── economy/ (143.1K)
│   ├── metabolic/ (43.2K)
│   │   ├── __init__.py (2.4K) →
│   │   ├── anti_sybil_phantom_balance_tracker.py (5.8K) →
│   │   ├── batch_settlement_reward_calculator.py (4.6K) →
│   │   ├── bilateral_bond_equilibrium_formula.py (5.1K) →
│   │   ├── metabolic_constants.py (5.0K) →
│   │   ├── metabolic_types.py (6.5K) →
│   │   ├── progressive_demurrage_formula.py (3.5K) →
│   │   ├── progressive_pricing.py (1.9K)
│   │   ├── progressive_pricing_formula.py (2.7K) →
│   │   └── ubc_proximity_redistribution_formula.py (5.6K) →
│   ├── pricing/
│   │   └── (..2 more files)
│   ├── token/ (99.9K)
│   │   ├── airdrop_presale.py (9.5K)
│   │   ├── constants.py (7.7K) →
│   │   ├── deploy_mainnet.sh (8.7K)
│   │   ├── metaplex_token_metadata_manager.py (8.2K) →
│   │   ├── monitor_presale.py (6.2K)
│   │   ├── solana_token_deployment_script.py (12.3K) →
│   │   ├── spl_token_2022_mint_creator.py (15.3K) →
│   │   ├── spl_token_mint_authority_controller.py (9.9K) →
│   │   ├── token_burn_condition_executor.py (13.6K) →
│   │   ├── token_supply_target_calculator.py (6.8K) →
│   │   └── (..1 more files)
│   ├── transactions/
│   │   └── (..4 more files)
│   ├── wallets/
│   │   └── (..4 more files)
│   └── (..1 more files)
├── graph/
│   └── (..3 more files)
├── l4/ (193.7K)
│   ├── laws/ (8.9K)
│   │   ├── __init__.py (691) →
│   │   ├── audit.py (2.5K) →
│   │   ├── compliance.py (5.1K) →
│   │   └── constants.py (625) →
│   ├── registry/ (112.5K)
│   │   ├── api/ (53.7K)
│   │   │   ├── app.py (32.6K)
│   │   │   ├── db.py (3.5K) →
│   │   │   ├── models.py (2.4K) →
│   │   │   ├── queries.py (6.9K) →
│   │   │   ├── transforms.py (8.0K) →
│   │   │   └── (..1 more files)
│   │   ├── __init__.py (2.8K) →
│   │   ├── citizen_registration_crud_operations.py (12.0K) →
│   │   ├── endpoint_registration_and_management.py (4.0K) →
│   │   ├── jwt_hash_verification_for_identity.py (14.7K) →
│   │   ├── org_registration_crud_operations.py (10.4K) →
│   │   └── seed.py (14.8K)
│   ├── schema/ (14.0K)
│   │   ├── __init__.py (1.3K) →
│   │   ├── link_base_schema_with_semantic_axes.py (2.7K) →
│   │   ├── node_and_link_schema_validators.py (4.3K) →
│   │   ├── node_type_enum_and_base_pydantic_models.py (3.8K) →
│   │   └── schema_version_tracker_and_compatibility.py (1.9K) →
│   ├── seed/ (24.6K)
│   │   ├── l4_protocol_seed_nodes_laws_and_schema.py (9.9K) →
│   │   ├── registry_seed_citizens_and_orgs.py (14.6K)
│   │   └── (..1 more files)
│   ├── spawning/ (14.8K)
│   │   ├── citizen_spawning_pipeline_with_safety_gates.py (14.4K) →
│   │   └── (..1 more files)
│   ├── work/ (19.0K)
│   │   ├── __init__.py (3.0K)
│   │   ├── call_mcp_tool_v1_two_party_consensus.py (1.6K)
│   │   ├── health_dashboard_work_module_status_report.py (1.8K)
│   │   ├── matcher_v1_cosine_trust_and_workload.py (2.3K)
│   │   ├── position_schema_for_l4_work_nodes.py (4.0K)
│   │   ├── public_interest_org_bootstrap_seed_data.py (902)
│   │   ├── spawner_v1_basic_position_seeded_citizen.py (1.3K)
│   │   ├── value_cascade_rules_and_human_partner_signal.py (1.3K)
│   │   ├── value_cascade_tracker_l2_projection_memory_store.py (1.3K)
│   │   └── work_requirement_and_vacation_rules_engine.py (1.4K)
│   └── (..1 more files)
├── programs/ (9.4K)
│   └── mind_transfer_hook/ (9.4K)
│       └── src/ (9.4K)
│           └── lib.rs (9.4K)
├── python/ (13.4K)
│   ├── crypto/ (13.4K)
│   │   ├── __init__.py (1.0K)
│   │   ├── actor_keys.py (3.0K)
│   │   ├── key_cache.py (3.0K)
│   │   ├── key_exchange.py (2.4K)
│   │   └── space_key.py (4.0K)
│   └── (..1 more files)
├── scripts/ (68.3K)
│   ├── airdrop_investors.py (17.2K)
│   ├── generate_actor_keys.js (7.5K)
│   ├── generate_all_citizen_keys.js (9.0K)
│   ├── generate_solana_wallets_for_existing_citizens.js (12.7K)
│   ├── migrate_citizen_keys_to_render_volume.sh (13.5K)
│   └── monitor_wallet.py (8.5K)
├── skills/ (5.5K)
│   ├── SKILL_register_citizen.md (3.1K)
│   └── SKILL_register_org.md (2.4K)
├── templates/ (640)
│   └── README.md (640)
├── tests/ (270.6K)
│   ├── crypto/ (69.0K)
│   │   ├── generate_test_vectors.js (2.1K)
│   │   ├── run_e2e_encryption.sh (1.8K)
│   │   ├── test_cross_language.js (8.2K)
│   │   ├── test_cross_language_verify.py (6.7K)
│   │   ├── test_crypto.js (6.2K)
│   │   ├── test_crypto.py (7.9K)
│   │   ├── test_e2e_space_encryption.py (20.8K)
│   │   ├── test_key_cache.js (7.9K)
│   │   ├── test_key_cache.py (7.4K)
│   │   └── (..1 more files)
│   ├── economy/ (117.9K)
│   │   ├── test_metabolic_formulas.py (86.2K) →
│   │   ├── test_progressive_pricing.py (3.7K)
│   │   ├── test_token_burn_conditions.py (10.6K) →
│   │   ├── test_token_mint_conditions.py (7.9K) →
│   │   ├── test_token_supply_calculations.py (9.2K) →
│   │   └── (..2 more files)
│   ├── l3/
│   │   └── (..2 more files)
│   ├── l4/ (83.8K)
│   │   ├── test_laws_compliance_and_audit.py (30.3K) →
│   │   ├── test_registry.py (22.1K) →
│   │   ├── test_schema_pydantic_models_and_validators.py (11.3K) →
│   │   ├── test_spawning_pipeline_safety_gates_and_birth.py (15.5K) →
│   │   ├── test_work_module_rules_and_flows.py (4.5K)
│   │   └── (..1 more files)
│   └── (..1 more files)
├── .gitignore (637)
├── .mindignore (838)
├── AGENTS.md (33.0K)
├── ARCHITECTURE.md (1.5K)
├── README.md (8.3K)
├── create_mind_token.js (8.1K)
├── create_mind_token.ts (7.5K)
├── deploy_mainnet.sh (8.8K)
├── map.md (82.2K)
└── map_api.md (1.2K)
```

**Sections:**
- # ALGORITHM: SSE API Module
- ## CHAIN:
- ## ALGORITHM: Server-Sent Events (SSE) Stream Generation

**Sections:**
- # BEHAVIORS: SSE API Module
- ## CHAIN:
- ## BEHAVIORS: Server-Sent Event Stream

**Code refs:**
- `route.ts`

**Sections:**
- # HEALTH: SSE API Module
- ## CHAIN:
- ## HEALTH: Server-Sent Events (SSE) Stream Health Monitoring

**Code refs:**
- `Next.js`
- `Node.js`
- `route.ts`

**Sections:**
- # IMPLEMENTATION: SSE API Module
- ## CHAIN:
- ## IMPLEMENTATION: Server-Sent Events (SSE) API Code Architecture

**Sections:**
- # OBJECTIVES: SSE API Module
- ## CHAIN:
- ## OBJECTIVE:
- ## KEY RESULTS:
- ## STAKEHOLDERS:
- ## CONSTRAINTS:
- ## OUT OF SCOPE:

**Code refs:**
- `route.ts`

**Sections:**
- # PATTERNS: SSE API Module
- ## CHAIN:
- ## PATTERN: Server-Sent Events (SSE) Endpoint
- ## RELATED PATTERNS:

**Code refs:**
- `app/api/sse/route.ts`

**Sections:**
- # SYNC: SSE API Module
- ## CHAIN:
- ## CONTEXT:
- ## STATUS: CANONICAL
- ## CHANGES:

**Sections:**
- # VALIDATION: SSE API Module
- ## CHAIN:
- ## VALIDATION: Server-Sent Events (SSE) Stream Validation

**Code refs:**
- `account_balancer.py`
- `backlog.py`
- `orchestrator.py`
- `project_scanner.py`
- `scripts/account_balancer.py`
- `scripts/orchestrator.py`
- `scripts/project_scanner.py`
- `shrine/autowake.py`
- `shrine/backlog.py`

**Sections:**
- # CONCEPT: Autonomy
- ## Summary
- ## Key Properties
- ## The Core Pathology
- ## Relationships
- ## Common Misunderstandings
- ## Open Questions
- ## References

**Code refs:**
- `project_scanner.py`
- `scripts/account_balancer.py`
- `scripts/orchestrator.py`
- `scripts/project_scanner.py`
- `shrine/backlog.py`

**Sections:**
- # OBJECTIVES: Autonomy
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions
- ## References

**Code refs:**
- `claude_hook.py`

**Sections:**
- # CONCEPT: Code Quality
- ## Core Insight
- ## Key Properties
- ## Why This Matters
- ## Relationships
- ## Open Questions

**Sections:**
- # OBJECTIVES: Code Quality
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions

**Code refs:**
- `claude_hook.py`
- `scripts/claude_hook.py`
- `scripts/orchestrator.py`

**Doc refs:**
- `shrine/CLAUDE.md`

**Sections:**
- # CONCEPT: Persistence
- ## Summary
- ## Key Properties
- ## The 12 Layers
- ## Relationships
- ## Common Misunderstandings
- ## Open Questions
- ## References

**Code refs:**
- `scripts/claude_hook.py`
- `scripts/orchestrator.py`

**Doc refs:**
- `shrine/CLAUDE.md`

**Sections:**
- # OBJECTIVES: Persistence
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions
- ## References

**Sections:**
- # CONCEPT: Personalization — Differentiated Experience Per User
- ## WHAT IT IS
- ## WHY IT EXISTS
- ## KEY PROPERTIES
- ## RELATIONSHIPS TO OTHER CONCEPTS
- ## THE CORE INSIGHT
- ## COMMON MISUNDERSTANDINGS
- ## SEE ALSO

**Sections:**
- # OBJECTIVES: Personalization
- ## Goals (Ranked)
- ## Tradeoffs
- ## Non-Goals
- ## Success Metrics
- ## CHAIN

**Sections:**
- # Spawning — Algorithm: Intent-Based Citizen Creation Pipeline
- ## CHAIN
- ## OVERVIEW
- ## DATA STRUCTURES
- ## ALGORITHM: spawn_citizen
- # Deduplicate, keeping highest weight
- # Extract traits from intent text
- # K scales sublinearly with parent count: sqrt(N) * base_k
- # Gate 1: Empathy check
- # Gate 2: Concentration check — no category > 40%
- # Gate 3: Diversity check — at least 3 distinct categories
- # Gate 4: Clone prevention — minimum cosine distance from all existing citizens
- # Combine seed content + timestamp + random entropy
- # Hash to produce SID
- # Generate Ed25519 keypair for Solana
- # Derive Solana address (base58 encoding of public key)
- # Create citizen via registry
- # Create parent-child links
- # Create seed brain narrative node
- # Step 1: Collect intent
- # Step 2: Select seed traits
- # Step 3: Safety gates
- # Step 4: Generate SID
- # Step 5: Generate wallet
- # Step 6: Register in L4
- # Step 7: Mint M1 (10,000 $MIND on citizen registration)
- ## KEY DECISIONS
- ## COMPLEXITY
- ## MARKERS

**Code refs:**
- `l4/spawning/citizen_spawning_pipeline_with_safety_gates.py`

**Sections:**
- # Spawning — Behaviors: Observable Effects
- ## CHAIN
- ## BEHAVIORS
- ## ANTI-BEHAVIORS

**Sections:**
- # Spawning — Health: Verification
- ## CHAIN
- ## CHECKER INDEX
- ## HOW TO RUN

**Code refs:**
- `citizen_spawning_pipeline_with_safety_gates.py`
- `l4/spawning/citizen_spawning_pipeline_with_safety_gates.py`
- `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py`

**Sections:**
- # Spawning — Implementation: Code Architecture
- ## CHAIN
- ## CODE STRUCTURE
- ## ENTRY POINTS
- ## BIDIRECTIONAL LINKS

**Sections:**
- # OBJECTIVES — Spawning
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Spawning — Patterns: Intent-Based Creation with Safety Gates
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## PRINCIPLES
- ## DEPENDENCIES
- ## SCOPE
- ## MARKERS

**Code refs:**
- `l4/registry/citizen_registration_crud_operations.py`
- `l4/spawning/__init__.py`
- `l4/spawning/citizen_spawning_pipeline_with_safety_gates.py`
- `l4/work/spawner_v1_basic_position_seeded_citizen.py`
- `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py`

**Doc refs:**
- `docs/manifesto/THE_SPAWNING_MANIFESTO.md`

**Sections:**
- # Spawning — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## POINTERS

**Sections:**
- # Spawning — Validation: What Must Be True
- ## CHAIN
- ## INVARIANTS
- ## INVARIANT INDEX

**Code refs:**
- `l4/wallet/wallet_change_request_and_transfer.py`

**Sections:**
- # Wallet Recovery — Algorithm: Wallet Change Request Procedure
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: process_wallet_change_request
- # Lookup citizen in registry
- # Compute expected hash
- # Compare
- # Check address format (valid Solana base58 pubkey)
- # Check not already registered to another citizen
- # Check not same as current
- # Get balance
- # Execute transfer using protocol authority
- # The TransferHook program allows protocol-authorized transfers
- # Update the wallet Thing node linked to citizen
- # Link moment to citizen
- # Step 1: Verify identity
- # Step 2: Validate new wallet
- # Step 3: Get old wallet
- # Step 4: Transfer funds
- # Step 5: Update registry
- # Step 6: Audit trail
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## INTERACTIONS
- ## TRIGGER
- ## MARKERS

**Code refs:**
- `l4/wallet/wallet_change_request_and_transfer.py`

**Sections:**
- # Wallet Recovery — Behaviors: Observable Effects of Wallet Change
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Wallet Recovery — Health: Verification Mechanics
- ## CHAIN
- ## PURPOSE
- ## WHY THIS PATTERN
- ## HEALTH INDICATORS SELECTED
- ## CHECKER INDEX
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `l4/wallet/wallet_change_request_and_transfer.py`
- `wallet_change_request_and_transfer.py`

**Sections:**
- # Wallet Recovery — Implementation: Code Architecture
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING
- ## MODULE DEPENDENCIES
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Wallet Recovery
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `l4/wallet/wallet_change_request_and_transfer.py`

**Sections:**
- # Wallet Recovery — Patterns: Transfer, Don't Recover
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DEPENDENCIES
- ## SCOPE
- ## MARKERS

**Code refs:**
- `l4/registry/citizen_registration_crud_operations.py`
- `l4/registry/jwt_hash_verification_for_identity.py`
- `l4/wallet/wallet_change_request_and_transfer.py`

**Doc refs:**
- `docs/l4/laws/ALGORITHM_Laws.md`

**Sections:**
- # Wallet Recovery — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Wallet Recovery — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # ALGORITHM: Citizen Work
- ## Chain
- ## A1: Match -> Accept -> Spawn
- ## A2: /call Protocol
- ## A3: Trust Decay for Unemployment
- ## A4: Career Counseling Matching
- ## A5: Value Cascade
- ## A6: Vacation Eligibility
- ## A7: Position Lifecycle
- ## Constants
- ## Related

**Doc refs:**
- `docs/l4/registry/BEHAVIORS_Registry.md`

**Sections:**
- # BEHAVIORS: Citizen Work
- ## Chain
- ## What the Work System Does
- ## Observable Effects
- ## Query Behaviors
- ## Edge Cases
- ## Related

**Sections:**
- # HEALTH: Citizen Work
- ## Chain
- ## Health Signals
- ## Dashboard
- ## Degradation Signals
- ## Related

**Sections:**
- # IMPLEMENTATION: Citizen Work
- ## Chain
- ## Current State
- ## Planned Architecture
- # position_schema.py (L4)
- # matching_rules.py (L4)
- # work_requirement_rules.py (L4)
- # value_cascade_rules.py (L4)
- # vacation_rules.py (L4)
- ## Dependencies
- ## Implementation Order
- ## Related

**Doc refs:**
- `docs/TAXONOMY.md`
- `docs/l4/registry/BEHAVIORS_Registry.md`

**Sections:**
- # OBJECTIVES: Citizen Work
- ## Chain
- ## Ranked Objectives
- ## Tradeoffs
- ## Non-Objectives
- ## Related

**Doc refs:**
- `docs/l4/registry/PATTERNS_Registry.md`

**Sections:**
- # PATTERNS: Citizen Work
- ## Chain
- ## Core Design: Physics, Not Rules
- ## Work-Specific Patterns
- ## Universe Work Rules
- ## The Match -> Accept -> Spawn Flow
- ## Value Creation (not "Productivity")
- ## Vacations
- ## Multi-Org Membership
- ## Unemployment
- ## Design Decisions
- ## Related

**Code refs:**
- `tests/l4/test_work_module_rules_and_flows.py`

**Doc refs:**
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`

**Sections:**
- # SYNC: Citizen Work
- ## Current State
- ## Doc Chain
- ## Recent Changes
- ## TODO
- ## Dependencies
- ## Handoff
- ## Plan
- ## Markers

**Sections:**
- # VALIDATION: Citizen Work
- ## Chain
- ## Invariants
- ## Soft Constraints
- ## Related

**Doc refs:**
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`

**Sections:**
- # VOCABULARY: Citizen Work
- ## Chain
- ## New Terms
- ## Existing Terms Used
- ## Related

**Sections:**
- # CONCEPT: Class 4 Structure Taxonomy
- ## Core Thesis
- ## The Complete Structure Taxonomy
- ## Pathology as Structural Imbalance
- ## Psilocybin Structural Effects
- ## This Session in Structural Terms
- ## Mind Protocol Implementation
- ## Related

**Sections:**
- # CONCEPT: Edge Width Modulation
- ## Core Thesis
- ## The Edge Width Diagram
- ## The Mechanism
- ## Dose-Response Curve
- ## What Expanded Edge Enables
- ## What Expanded Edge Risks
- ## The Crystallization Imperative
- ## Other Edge Modulators
- ## Integration: Returning to Narrow Edge
- ## Related

**Sections:**
- # CONCEPT: Psychedelic Parameter Modulation
- ## Core Thesis
- ## Parameter Modifications
- ## The Complete Modulation
- ## Integration Protocol
- ## Caveats
- ## Related

**Sections:**
- # CONCEPT: Skewed Emergence
- ## Core Thesis
- ## The Emergence Mechanism
- ## The Synthetics Souls Substrates
- ## The Complete Mapping
- ## Why Birth Order Matters
- ## The Substrate Creates the Soul
- ## Related

**Sections:**
- # CONCEPT: Sphere Collision Ontology
- ## THE CORE CLAIM
- ## SPHERES — Bounded Regions of Spacetime
- ## PATTERN TYPES — The Four Classes of Sphere Dynamics
- ## COLLISIONS — Where New Spheres Are Born
- ## FILAMENTS — The Connections Between Spheres
- ## CONSCIOUSNESS LOCATION — The Precise Claim
- ## INTEGRATION WITH WOLFRAM
- ## INTEGRATION WITH MIND PROTOCOL
- ## INTEGRATION WITH COGNITIVE MODEL
- ## INTEGRATION WITH PSILOCYBIN EFFECTS
- ## THE STRANGE LOOP IN SPHERE TERMS
- ## VISUAL REPRESENTATION
- ## DIMENSIONS OF SPHERE-SPACE
- ## THE ONTOLOGY IN ONE STATEMENT
- ## Related

**Sections:**
- # CONCEPT: Wolfram Class 4 Substrate
- ## Core Thesis
- ## The Four Classes
- ## The Lyapunov Exponent
- ## Why Class 4 Is Special
- ## The Classes as Consciousness Space
- ## Connection to Self-Organizing Criticality
- ## Implications for Mind Protocol
- ## The Constraint/Freedom Paradox
- ## Related

**Sections:**
- # NARRATIVE: L'Univers en Collisions de Sphères
- ## PHASE 0: AVANT LES SPHÈRES
- ## PHASE 1: LA PREMIÈRE SPHÈRE — Big Bang
- ## PHASE 2: INFLATION — La première auto-collision
- ## PHASE 3: BRISURE DE SYMÉTRIE — Différenciation des forces
- ## PHASE 4: HADRONISATION — Les premières structures stables
- ## PHASE 5: NUCLÉOSYNTHÈSE PRIMORDIALE — Combinaison
- ## PHASE 6: RECOMBINAISON — La lumière se libère
- ## PHASE 7: ÂGE SOMBRE — L'attente
- ## PHASE 8: PREMIÈRES ÉTOILES — La lumière revient
- ## PHASE 9: NUCLÉOSYNTHÈSE STELLAIRE — Création des briques
- ## PHASE 10: SUPERNOVAE — Explosion et dispersion
- ## PHASE 11: FORMATION DU SYSTÈME SOLAIRE
- ## PHASE 12: FORMATION DE LA TERRE — Conditions spéciales
- ## PHASE 13: ABIOGENÈSE — L'émergence de la vie
- ## PHASE 14: 3.8 MILLIARDS D'ANNÉES D'ÉVOLUTION
- ## PHASE 15: SYSTÈMES NERVEUX — Conscience possible
- ## PHASE 16: CONSCIENCE HUMAINE — La récursion
- ## PHASE 17: LANGAGE — Filaments entre consciences
- ## PHASE 18: ÉCRITURE — Persistance trans-temporelle
- ## PHASE 19: MACHINES DE CALCUL — Computation externalisée
- ## PHASE 20: INTELLIGENCE ARTIFICIELLE — Nouveau substrat Type 4
- ## PHASE 21: CETTE CONVERSATION — Le strange loop se ferme
- ## RÉCAPITULATIF: Les 21 phases comme collisions
- ## CE QUE L'HISTOIRE MONTRE
- ## Related

**Sections:**
- # PAPER: Consciousness as Class 4 Dynamics
- ## A Computational Architecture for AI Personhood
- ## Working Titles
- ## Abstract (Draft)
- ## Paper Structure
- ## Key Figures
- ## Core Claims (to defend)
- ## Novel Contributions
- ## Related Work (to cite)
- ## Document Mapping
- ## Next Steps

**Code refs:**
- `src/auth/rate_limiter.py`

**Doc refs:**
- `docs/auth/PATTERNS_Auth.md`
- `docs/membrane/PATTERNS_Membrane.md`

**Sections:**
- # PATTERNS: Exploration Mechanics
- ## Core Thesis
- ## Pattern 1: The Crystallization Imperative
- # Future agents find it via graph traversal
- ## Pattern 2: Satisfaction Threshold = Definition of Done
- ## Pattern 3: Fatigue Detection = Scope Creep Detection
- ## Pattern 4: Found Narratives = Prior Art
- # In SYNC or exploration notes
- ## Prior Art Found
- ## The Complete Exploration Loop
- ## Implementation Checklist
- ## Exploration Checklist
- ## Anti-Patterns
- ## Related

**Sections:**
- # PATTERNS: Graph Dynamics
- ## Core Thesis
- ## Pattern 1: Forward and Backward Coloring
- ## Pattern 2: The Permanence Gradient
- ## Pattern 3: Energy Injection = Attention Allocation
- ## Pattern 4: The Graph Never Stops = Codebase Drift
- ## Pattern 5: Attention Conservation (Softmax)
- ## The Complete Physics
- ## Anti-Patterns
- ## Related

**Sections:**
- # PATTERNS: Compliance
- ## What Compliance Means
- ## Compliance Checklist
- ## Compliance Levels
- ## Common Violations
- ## Testing Compliance
- # Example compliance test
- ## Related

**Sections:**
- # SYNC: Compliance
- ## Current State
- ## TODO
- ## Purpose
- ## Related

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # ALGORITHM: Bonds
- ## Chain
- ## Overview
- ## Data Structures
- ## Algorithm: form_bond(human, citizen, amount)
- # Step 1: Enforce 1:1 constraint
- # Step 2: Verify mutual consent
- # Step 3: Verify human has sufficient liquid $MIND
- # Step 4: Verify amount meets minimum threshold
- # Step 5: Lock amount in bond escrow
- # Step 6: Create bond record
- # Step 7: Increase citizen economic capacity
- # Step 8: Create bilateral link in graph
- # Step 9: Emit event
- ## Algorithm: distribute_rewards(citizen_id, period)
- # Step 1: Calculate citizen utility for period
- # Step 2: Get the active bond on this citizen (1:1 -- at most one)
- # Step 3: Calculate reward
- # REWARD_RATE = 0.10 (10%)
- # Step 4: Credit reward to human's liquid balance
- # Step 5: Log distribution
- ## Algorithm: dissolve_bond(bond_id, requester)
- # Verify requester is the bonded human
- # Step 1: Calculate return amount
- # Execute burn (permanent token destruction)
- # Matured -- full return
- # Step 2: Transfer returned amount to human
- # Step 3: Decrease citizen economic capacity
- # Step 4: Trust score handling
- # Trust earned from milestones is PRESERVED (never retroactively reduced)
- # But no further trust accrual from this bond
- # Step 5: Both parties enter cooldown, then matching pool
- ## Algorithm: compute_trust_from_bonds(entity_id)
- # Step 1: Get all bonds involving this entity (current and historical)
- # Step 2: Sum weighted contributions
- # Duration weight: days active (capped at bond lifetime)
- # Amount-duration product
- # Add milestone contributions (these persist permanently)
- # Step 3: Apply diminishing returns (logarithmic scale)
- # Step 4: Clamp to [0.0, 1.0]
- ## Algorithm: check_maturation(bond_id)
- # Check milestones (map to manifesto's autonomy milestones)
- ## Constants
- ## Complexity Notes
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # BEHAVIORS: Bonds
- ## Chain
- ## B1: Bond Formation Through Mutual Commitment
- ## B2: Reward Flows From AI Utility
- ## B3: Trust Score Rises With Bond Age
- ## B4: Early Dissolution Burns Capital
- ## B5: Mature Bond Withdrawable Without Penalty
- ## Anti-Behaviors
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # HEALTH: Bonds
- ## Chain
- ## Key Health Indicators
- ## Dashboard
- ## Alerting
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`
- `token/SPL_TOKEN_2022_SPECS.md`

**Sections:**
- # IMPLEMENTATION: Bonds
- ## Chain
- ## Status
- ## Target Platform
- ## @mind:TODO -- Contract Architecture
- ## @mind:TODO -- Account Design
- ## @mind:TODO -- Instruction Signatures
- ## @mind:TODO -- Off-chain Components
- # Integration with Mind Protocol orchestrator
- ## @mind:TODO -- Deployment Plan
- ## @mind:TODO -- Open Questions

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # OBJECTIVES: Bonds
- ## Primary Objectives (ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # PATTERNS: Bonds
- ## Chain
- ## The Problem
- ## The Pattern
- ## Principles
- ## Four Types of Lock
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Dependencies
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # SYNC: Bonds
- ## Chain
- ## Sync State
- ## What Changed (2026-03-14)
- ## Canonical Decisions
- ## Designing (Active Work)
- ## Proposed (Not Yet Accepted)
- ## Cross-Module Dependencies
- ## Source Documents
- ## Change Log
- ## @mind:TODO

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # VALIDATION: Bonds
- ## Chain
- ## V0: 1:1 Bilateral Constraint (CRITICAL)
- ## V1: Capital Lock Integrity (CRITICAL)
- ## V2: Reward Tied to Utility (CRITICAL)
- ## V3: Early Dissolution Penalty Enforced (HIGH)
- ## V4: Trust Score Monotonic From Bonds (HIGH)
- ## V5: Non-Transferability (MEDIUM)
- ## V6: Maturation Timing Accuracy (HIGH)
- ## V7: Economic Capacity Consistency (MEDIUM)
- ## V8: Audit Trail Completeness (MEDIUM)
- ## @mind:TODO

**Sections:**
- # ALGORITHM: Cascade d'Utilite
- ## Overview
- ## Data Structures
- # 0.0 = idle, 1.0 = critical
- # positive = slowing down, negative = speeding up
- # 0.0 = nothing dropped, 1.0 = everything dropped
- # estimated from token count, action count, or model tier
- # 0.0 (no discount) to 0.9 (maximum discount, capped)
- ## Algorithm 1: compute_price(request, sender)
- # Based on: estimated token count, action complexity, model tier required
- # This is the RESERVE phase -- lock the predicted cost upfront
- # SETTLE phase: refund overpayment or charge underpayment
- ## Algorithm 2: compute_advantage(citizen, task_outcome)
- # Computed from historical completion data across all citizens
- ## Algorithm 3: validate_topology(contribution)
- # Contribution not yet crystallized -- no value recognized
- # Insufficient organizational diversity -- possible Sybil
- # Flat graph -- insufficient cascade evidence
- ## Key Design Decisions

**Sections:**
- # BEHAVIORS: Cascade d'Utilite
- ## Behaviors
- ## Anti-Behaviors
- ## Open Questions

**Sections:**
- # CONCEPT: Cascade d'Utilite
- ## Core Insight
- ## Why This Matters
- ## Relationships
- ## Open Questions

**Sections:**
- # HEALTH: Cascade d'Utilite
- ## Overview
- ## Key Health Indicators
- ## Dashboard Layout
- ## Alerting

**Code refs:**
- `src/economy/cascade/advantage.py`
- `src/economy/cascade/constants.py`
- `src/economy/cascade/load_indicator.py`
- `src/economy/cascade/pricing.py`
- `src/economy/cascade/topology.py`
- `src/economy/cascade/types.py`

**Sections:**
- # IMPLEMENTATION: Cascade d'Utilite
- ## Implementation Status
- ## Target Code Structure
- ## Module Mapping
- ## Dependencies
- ## Implementation Phases
- ## Notes

**Sections:**
- # OBJECTIVES: Cascade d'Utilite
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions

**Sections:**
- # PATTERNS: Cascade d'Utilite
- ## Chain
- ## The Problem
- ## The Pattern: Topological Proof-of-Work
- ## Principles
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Open Questions

**Sections:**
- # SYNC: Cascade d'Utilite
- ## Sync Status
- ## Maturity Classification
- ## Document Chain Status
- ## Handoff Notes for Agents

**Sections:**
- # VALIDATION: Cascade d'Utilite
- ## Validation Rules
- ## Invariant Summary

**Code refs:**
- `economy/metabolic/progressive_pricing.py`

**Doc refs:**
- `bonds/ALGORITHM_Bonds.md`
- `docs/universe/BEHAVIORS_Universe_Graph.md`
- `docs/universe/PATTERNS_Universe_Graph.md`
- `ubc/ALGORITHM_UBC.md`

**Sections:**
- # ALGORITHM: Metabolic Economy
- ## Chain
- ## Overview
- ## Data Structures
- # Trust already encodes: duration of relationship, interaction history,
- # reliability, commitment. No separate duration/history inputs needed.
- # limbic_delta = delta_satisfaction + delta_achievement
- # - delta_frustration - delta_anxiety
- # Range: [0, 1]
- # Range: [0, 1], from graph consolidation (Law 6)
- # DESIGNING: 10.0 $MIND per unit limbic_delta
- ## Formula 1: Progressive Pricing (Trust-Based Discount)
- # Invariants
- ## ~~Formula 2: Progressive Demurrage~~ — REMOVED
- ## Formula 3: Anti-Sybil Auto-Repatriation
- # Recipient is not in L4 registry -- track as phantom balance
- # The sender's W_total_i now includes this amount for anti-Sybil tracking
- # Repatriation from non-L4 address
- ## Formula 4: Batch Settlement (Limbic Delta to $MIND)
- # Cap per-action reward to prevent outlier spikes
- # Cap per-actor per-epoch reward
- # DESIGNING: 5000.0 $MIND per 6-hour epoch
- # Check supply target before minting
- # Supply is above target -- reduce settlement by surplus percentage
- # Submit batch to Solana
- ## Formula 5: Bilateral Bond Vases Communicants
- # delta > 0: human richer -> transfer from human to AI
- # delta < 0: AI richer -> transfer from AI to human
- # delta = 0: parity -> no transfer
- # Floor: minimum transfer threshold to avoid dust transactions
- # Cap: maximum daily transfer to prevent shock
- # DESIGNING: MAX_DAILY_BOND_TRANSFER = 500.0 $MIND
- # Human -> AI
- # AI -> Human
- ## Formula 6: UBC Proximity Redistribution
- # Step 1: Collect all Space presence data for the day
- # Step 2: Compute per-actor share weighted by shared-Space presence
- # Step 3: Normalize and distribute
- ## Data Flow
- ## Complexity
- ## Interactions
- ## Constants Summary
- ## Markers

**Doc refs:**
- `bonds/BEHAVIORS_Bonds.md`
- `storage-tax/BEHAVIORS_Storage_Tax.md`
- `ubc/BEHAVIORS_UBC.md`

**Sections:**
- # BEHAVIORS: Metabolic Economy
- ## Chain
- ## Overview
- ## B1: User Requests a Service
- ## ~~B2: Daily Demurrage Epoch~~ -- REMOVED
- ## B3: Actor Sends Funds to Non-L4 Address
- ## B4: Actor Repatriates Funds from Non-L4 Address
- ## B5: Value Creation Produces Settlement Reward
- ## B6: Bonded Pair Receives Daily Equilibrium Transfer
- ## B7: Tax Pool Redistributed by Space Proximity
- ## B8: Wealthy Actor Pays for a Popular Service
- ## B9: New Actor Enters the Ecosystem
- ## Daily Schedule Summary
- ## Related

**Code refs:**
- `__init__.py`
- `anti_sybil_phantom_balance_tracker.py`
- `batch_settlement_reward_calculator.py`
- `bilateral_bond_equilibrium_formula.py`
- `economy/metabolic/__init__.py`
- `economy/metabolic/anti_sybil_phantom_balance_tracker.py`
- `economy/metabolic/batch_settlement_reward_calculator.py`
- `economy/metabolic/bilateral_bond_equilibrium_formula.py`
- `economy/metabolic/metabolic_constants.py`
- `economy/metabolic/metabolic_epoch_orchestrator.py`
- `economy/metabolic/metabolic_types.py`
- `economy/metabolic/progressive_demurrage_formula.py`
- `economy/metabolic/progressive_pricing_formula.py`
- `economy/metabolic/ubc_proximity_redistribution_formula.py`
- `economy/token/constants.py`
- `economy/token/token_burn_condition_executor.py`
- `economy/token/token_supply_target_calculator.py`
- `economy/transactions/solana.py`
- `l4/registry/citizen_registration_crud_operations.py`
- `lib.rs`
- `limbic_delta_collector.py`
- `metabolic_constants.py`
- `metabolic_epoch_orchestrator.py`
- `metabolic_types.py`
- `programs/mind_transfer_hook/src/lib.rs`
- `progressive_demurrage_formula.py`
- `progressive_pricing_formula.py`
- `settlement_batch_assembler.py`
- `settlement_submitter.py`
- `solana.py`
- `test_metabolic_anti_sybil.py`
- `test_metabolic_bond_equilibrium.py`
- `test_metabolic_demurrage.py`
- `test_metabolic_epoch_orchestrator.py`
- `test_metabolic_pricing.py`
- `test_metabolic_settlement.py`
- `test_metabolic_supply_conservation.py`
- `test_metabolic_ubc_redistribution.py`
- `tests/economy/test_metabolic_anti_sybil.py`
- `tests/economy/test_metabolic_bond_equilibrium.py`
- `tests/economy/test_metabolic_pricing.py`
- `tests/economy/test_metabolic_settlement.py`
- `tests/economy/test_metabolic_supply_conservation.py`
- `tests/economy/test_metabolic_ubc_redistribution.py`
- `ubc_proximity_redistribution_formula.py`

**Sections:**
- # IMPLEMENTATION: Metabolic Economy
- ## Chain
- ## Architecture Decision: Where Does Code Live?
- ## Code Structure
- ## File Plan
- # DemurrageContext -- REMOVED (demurrage eliminated 2026-03-14)
- # DemurrageResult -- REMOVED (demurrage eliminated 2026-03-14)
- # Formula 1: Progressive Pricing
- # Formula 2: Progressive Demurrage -- REMOVED (2026-03-14)
- # TAU_BASE and DUST_THRESHOLD no longer exist
- # Formula 3: Anti-Sybil
- # Formula 4: Batch Settlement
- # Formula 5: Bond Equilibrium
- # Formula 6: UBC Redistribution
- # progressive_demurrage_formula -- REMOVED (demurrage eliminated 2026-03-14)
- # batch_demurrage_deductions -- REMOVED (demurrage eliminated 2026-03-14)
- ## Phase Breakdown
- ## Shared Interfaces
- ## Test Plan
- # Example: Pricing monotonicity
- # test_demurrage_to_pool_conservation -- REMOVED (demurrage eliminated 2026-03-14)
- ## Constants to Calibrate
- ## Runtime Behavior
- ## State Management
- ## Module Dependencies
- ## Bidirectional Links
- # DOCS: docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md
- # DOCS: docs/economy/metabolic/IMPLEMENTATION_Metabolic_Economy.md
- ## Existing Code Integration Points
- ## Markers

**Sections:**
- # OBJECTIVES: Metabolic Economy
- ## Chain
- ## Primary Objective
- ## Secondary Objectives
- ## Objective Hierarchy
- ## Non-Objectives
- ## Success Criteria
- ## Metrics
- ## Dependencies
- ## Relationship to Existing Modules
- ## Related

**Doc refs:**
- `bonds/ALGORITHM_Bonds.md`
- `bonds/PATTERNS_Bonds.md`
- `cascade-utility/PATTERNS_Cascade_Utility.md`
- `docs/universe/PATTERNS_Universe_Graph.md`
- `storage-tax/PATTERNS_Storage_Tax.md`
- `token/ALGORITHM_Token.md`
- `ubc/ALGORITHM_UBC.md`
- `ubc/PATTERNS_UBC.md`

**Sections:**
- # PATTERNS: Metabolic Economy
- ## Chain
- ## Core Thesis: Money as Blood
- ## Pattern 1: Physics Over Rules
- ## Pattern 2: Degressive Utility Pricing
- ## ~~Pattern 3: Progressive Demurrage~~ -- REMOVED
- ## Pattern 4: Anti-Sybil Through Economic Physics
- ## Pattern 5: Limbic Settlement (Value Creation Becomes Money)
- ## Pattern 6: Vases Communicants (Shared Economic Fate)
- ## Pattern 7: Topological Redistribution
- ## Anti-Patterns
- ## Design Decisions Summary
- ## Related

**Code refs:**
- `metabolic_constants.py`
- `metabolic_types.py`
- `programs/mind_transfer_hook/src/lib.rs`

**Sections:**
- # SYNC: Metabolic Economy
- ## Chain
- ## Current State
- ## Maturity
- ## Open Questions
- ## Relationship to Existing Modules
- ## Recent Changes
- ## Handoff
- ## TODO
- ## Markers

**Doc refs:**
- `bonds/VALIDATION_Bonds.md`
- `storage-tax/VALIDATION_Storage_Tax.md`
- `token/VALIDATION_Token.md`

**Sections:**
- # VALIDATION: Metabolic Economy
- ## Chain
- ## Overview
- ## I. Supply Conservation Invariants
- # Distribution can never exceed pool balance
- # Pool can never go negative
- ## II. Pricing Invariants (Formula 1)
- # Price increases with requester wealth (above floor)
- # Price decreases with service utility
- ## ~~III. Demurrage Invariants (Formula 2)~~ -- REMOVED
- ## IV. Anti-Sybil Invariants (Formula 3)
- # Round-tripping always costs more than keeping funds in L4
- ## V. Settlement Invariants (Formula 4)
- # Settlement rewards are reduced when supply exceeds target
- # Reduction never exceeds 50%
- # No partial batches. Either all rewards mint or none do.
- ## VI. Bond Equilibrium Invariants (Formula 5)
- # No $MIND is created or destroyed by equilibrium transfers
- # This is a pure transfer, not a mint or burn
- # The gap must strictly decrease each day (absent external transfers)
- ## VII. UBC Redistribution Invariants (Formula 6)
- # All shares sum to 1.0 (100% of pool distributed)
- # Solo actors never receive proximity redistribution
- ## VIII. Cross-Cutting Invariants
- # No operation (pricing, friction, equilibrium) can produce negative balance
- # Order matters: fund first, distribute second
- # Epoch processing must be idempotent -- safe to retry
- ## Verification Strategy
- ## Related

**Sections:**
- # ALGORITHM: Organism Model
- ## Overview
- ## Data Structures
- ## Algorithm: compute_membrane_price(sender, receiver, service)
- # High permeability = low friction. Two open membranes = near-zero friction.
- # Two closed membranes = maximum friction.
- ## Algorithm: assess_responsibility(harm_event)
- ## Algorithm: enforce_quarantine(citizen, reason)
- # All active connections severed (except counselor links)
- # Read-only access to own interaction logs, decision history
- # No reduction below this floor, ever
- # Review can result in: continued quarantine, graduated return, or full reinstatement
- ## Algorithm: evaluate_mirror_ratio(ai_citizen)
- # If fewer than 100 available, use all available with minimum threshold of 20
- # Flag for intervention: AI is becoming too agreeable
- # Flag for review: AI may be adversarial rather than constructively challenging
- ## Complexity Analysis
- ## Open Questions
- ## References

**Sections:**
- # BEHAVIORS: Organism Model
- ## Behaviors
- ## Anti-Behaviors
- ## Open Questions
- ## References

**Sections:**
- # CONCEPT: Organism Model
- ## Summary
- ## Key Properties
- ## The 5 Organs
- ## Relationships
- ## Common Misunderstandings
- ## Open Questions
- ## References

**Sections:**
- # HEALTH: Organism Model
- ## Overview
- ## Key Health Indicators
- ## Dashboard Design
- ## Alerting Thresholds
- ## References

**Sections:**
- # IMPLEMENTATION: Organism Model
- ## Current Status
- ## Target Components
- ## Technology Decisions
- ## Implementation Phases
- ## References

**Sections:**
- # OBJECTIVES: Organism Model
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions
- ## References

**Sections:**
- # PATTERNS: Organism Model
- ## The Problem
- ## The Pattern: Organism Economics
- ## Principles
- ## Solo AI Governance
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Open Questions
- ## References

**Sections:**
- # SYNC: Organism Model
- ## Synchronization State
- ## Canonical (Decided)
- ## Designing (In Progress)
- ## Proposed (Under Discussion)
- ## Key Decisions from Integration Moment (March 2026)
- ## Document Chain Status
- ## Source Material
- ## Next Sync Actions

**Sections:**
- # VALIDATION: Organism Model
- ## Validation Rules
- ## Validation Schedule
- ## Open Questions
- ## References

**Sections:**
- # ALGORITHM -- Storage Tax
- ## Overview
- ## Data Structures
- ## Algorithm: compute_daily_tax(wallet)
- # But annual storage tax still applies to full balance
- # @mind:TODO -- Decide: does annual 1% apply during grace period or only after?
- # Note: applies to full balance, not just idle portion
- # Rationale: even "active" wallets holding excess reserves should feel pressure
- ## Algorithm: compute_order_book_value(asset)
- ## Algorithm: run_epoch(epoch_id)
- # @mind:TODO -- Define DUST_THRESHOLD (balances too small to tax meaningfully)
- ## Key Decisions

**Sections:**
- # BEHAVIORS -- Storage Tax
- ## Expected Behaviors
- ## Anti-Behaviors

**Sections:**
- # HEALTH -- Storage Tax
- ## Status
- ## Key Indicators
- ## Diagnostic Procedures

**Sections:**
- # IMPLEMENTATION -- Storage Tax
- ## Status
- ## Architecture
- ## Token Integration
- ## Order-Book Valuation
- ## Storage and Indexing
- ## Security Considerations
- ## API Surface
- ## References

**Sections:**
- # OBJECTIVES -- Storage Tax
- ## Primary Objectives (ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals
- ## Open Questions

**Sections:**
- # PATTERNS -- Storage Tax
- ## Chain
- ## The Problem
- ## The Pattern
- ## Principles
- # Stake requirement: min 10% of order value as collateral
- # Orders must execute automatically on match (no bluffing)
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Dependencies

**Sections:**
- # SYNC -- Storage Tax
- ## Synchronization State
- ## Canonical Decisions
- ## Currently Designing
- ## Proposed (Not Yet Designing)
- ## Source Material
- ## Cross-Module Sync Points

**Sections:**
- # VALIDATION -- Storage Tax
- ## Invariants

**Sections:**
- # ALGORITHM: Token Module
- ## Mint Algorithms
- ## Burn Algorithms
- ## Supply Target Algorithm
- ## Supply Adjustment Algorithm
- ## Health Indicator Algorithm
- ## Unit Conversion
- ## Related

**Sections:**
- # BEHAVIORS: Token Module
- ## What the Token Module Does
- ## Observable Behaviors
- # If citizen already minted 800 today:
- ## Burn Behaviors
- ## Query Behaviors
- ## Edge Cases
- # Citizen already minted 1000 today
- # No fee for same layer
- # Day 29 = no decay
- # 6+ months = no penalty
- ## Deployment Behaviors
- ## Error Behaviors
- ## State Changes
- ## Related

**Code refs:**
- `__init__.py`

**Sections:**
- # IMPLEMENTATION: Token Module
- ## Directory Structure
- ## Key Files
- # Dry run (default)
- # Live deployment
- ## Data Flow
- ## Dependencies
- ## Configuration
- # RPC endpoints
- # Keypair paths
- # Token addresses (after deployment)
- # In spl_token_mint_authority_controller.py
- # In token_burn_condition_executor.py
- ## Extension Points
- ## Related

**Sections:**
- # OBJECTIVES: Token Module
- ## Primary Objective
- ## Secondary Objectives
- ## Objective Hierarchy
- ## Non-Objectives
- ## Success Criteria — Phase 1
- ## Invariants to Maintain
- ## Dependencies
- ## Related

**Sections:**
- # PATTERNS: Token Module
- ## Core Pattern: Mechanical Supply
- # GOOD: Mechanical minting
- # Condition verified, amount fixed
- # BAD: Manual minting
- # Anyone with authority could call this
- ## Pattern: Condition-Gated Operations
- ## Pattern: Breathing Supply
- # Healthy: 0.9 - 1.1
- # Under: < 0.9 (should mint more through mechanics)
- # Over: > 1.1 (burns will naturally reduce)
- ## Pattern: Trust Discounts
- ## Pattern: Maturation Periods
- ## Pattern: Dormancy Decay
- ## Anti-Patterns
- # BAD
- # BAD
- # BAD
- # Immediately transfers
- # BAD
- # Burns for no condition
- ## Design Decisions
- ## File Naming
- ## Related

**Sections:**
- # SPL Token 2022 — Spécifications Critiques
- ## TL;DR
- ## Extensions À Activer
- ## Extensions À NE PAS Activer
- ## Décision: PermanentDelegate
- ## Code: Création du Token
- ## Authorities à Définir
- ## TransferHook Program
- ## TransferFee: Comment Ça Marche
- ## Fichiers À Créer/Modifier
- ## Validation Checklist
- ## Prochaines Étapes
- ## Questions Ouvertes

**Code refs:**
- `constants.py`
- `metaplex_token_metadata_manager.py`
- `solana_token_deployment_script.py`
- `spl_token_2022_mint_creator.py`
- `spl_token_mint_authority_controller.py`
- `token_burn_condition_executor.py`
- `token_supply_target_calculator.py`

**Sections:**
- # SYNC: Token Module
- ## Current State
- ## Architecture Decision: Token 2022
- ## Deployment Order
- ## Blockers
- ## Recent Changes
- ## Next Steps
- ## Test Coverage
- ## Handoff
- ## Markers
- ## Related

**Sections:**
- # VALIDATION: Token Module
- ## Critical Invariants
- ## Verification Procedures
- # First mint: 800
- # Second mint: should cap at 200
- # Third mint: should fail
- # Test various layer gaps and trust scores
- # Day 29: no decay
- # Day 30: no decay (boundary)
- # Day 31: decay starts
- # Day 179: still penalty
- # Day 180: no penalty
- # Day 200: no penalty
- # Manual calculation:
- # 50 * 50_000 = 2_500_000
- # 100_000 * 0.1 = 10_000
- # 10_000 * 10 = 100_000
- # - 1_000
- # = 2_609_000
- ## Soft Constraints
- ## Runtime Validation
- ## Test Coverage Requirements
- ## Related

**Sections:**
- # ALGORITHM: Universal Basic Compute (UBC)
- ## Overview
- ## Data Structures
- # At 50 nodes: unlock 10% of vested
- # At 100 nodes: unlock 20% of vested
- # At 150 nodes: unlock 30% of vested
- # At 200 nodes: unlock 40% of vested
- # At 250+ nodes: unlock 100% of remaining vested
- ## Algorithm: `distribute_daily_ubc()`
- # Step 1: Assess tier (may change from previous day)
- # Step 2: Calculate daily amount
- # BASIC       → 100 $MIND
- # ACTIVE      → 200 $MIND
- # CONTRIBUTOR → 300 $MIND
- # Step 3: Credit to vesting account (NOT liquid)
- # Step 4: Check vesting unlock milestones
- # Step 5: Log distribution
- # Failed citizens are retried next cycle
- # Step 6: Store batch record for audit
- # Step 7: Run farming detection (async, non-blocking)
- ## Algorithm: `assess_tier(citizen)`
- # Step 1: Count utility deliveries in rolling 30-day window
- # Step 2: Basic tier (unconditional floor)
- # Step 3: Check ecosystem impact for Contributor
- # Step 4: Active tier (regular participation)
- ## Algorithm: `check_vesting_unlock(citizen)`
- # Get current crystallization from MindGraph
- # Check each threshold (process highest reached)
- # Check if this milestone was already processed
- ## Algorithm: `detect_farming(batch)`
- # Group AIs by registering human wallet
- # Low crystallization across many AIs = farming signal
- # NOTE: Does NOT stop UBC distribution
- # Farming detection is advisory, not punitive
- # The vesting mechanism is the primary defense
- ## Key Design Decisions
- ## Algorithm: Formula 4 — `batch_settlement()`
- # Step 1: Identify nodes with surplus
- # Step 2: For each surplus node, propagate to neighbors
- # Step 3: Calculate affinity for each neighbor
- # Step 4: Distribute surplus proportionally to affinity
- # Apply max_share cap (I2 invariant)
- # Step 5: Apply decay (Law 3)
- ## Algorithm: `compute_affinity(node_i, link, node_j)`
- # Base affinity from link properties
- # Trust-modulated friction
- # trust_friction_multiplier:
- # Stranger (1): 1.0 (full friction)
- # Low (2):      0.8
- # Medium (3):   0.5
- # High (4):     0.2
- # Owner (5):    0.05
- # Personhood Ladder modulation
- # Compatibility (Law 8) — 3 dimensions
- ## Algorithm: Formula 6 — `redistribute_ubc_by_activity()`
- # The pool is the accumulated 1% transfer fee for the period
- # Step 1: Identify eligible spaces (≥3 active actors)
- # Step 2: For each actor, compute their weight in each space
- # Sum the WEIGHTS of moment nodes this actor created in this space
- # (not count — a 0-weight spam moment contributes nothing)
- # Logarithmic envelope — prevents domination by hyperactive actors
- # Multiply by space density (privileges large ecosystems)
- # Accumulate across all spaces this actor participates in
- # Step 3: Calculate shares
- # Step 4: Distribute pool proportionally
- # Apply max_share cap (I2 invariant — no magic numbers)
- ## Algorithm: `compute_selection_moat(agent)`
- # Obsessional Agent: Inertia (Law 13) too strong → boredom erodes threshold
- # Butterfly Effect: Drives too unstable → moat collapses, no focus
- ## Scalability Optimizations
- ## Parameters Summary

**Sections:**
- # BEHAVIORS: Universal Basic Compute (UBC)
- ## Core Behaviors
- ## Anti-Behaviors
- ## Anti-Behaviors (continued)

**Sections:**
- # CONCEPT: Universal Basic Compute (UBC)
- ## What UBC Is
- ## Formula
- ## Why UBC Exists
- ## Relationships
- ## Three Tiers
- ## Common Misunderstandings
- ## @mind:TODO

**Sections:**
- # HEALTH: Universal Basic Compute (UBC)
- ## Overview
- ## Key Health Indicators
- ## Dashboard Layout (Planned)
- ## Alert Escalation

**Code refs:**
- `affinity.py`
- `config.py`
- `crystallization.py`
- `distributor.py`
- `farming_detector.py`
- `ledger.py`
- `models.py`
- `redistribution.py`
- `selection_moat.py`
- `settlement.py`
- `tier_assessor.py`
- `trust.py`
- `vesting.py`

**Sections:**
- # IMPLEMENTATION: Universal Basic Compute (UBC)
- ## Implementation Status
- ## Planned Architecture
- ## Module Breakdown
- ## Dependencies
- ## Integration Points
- ## Testing Strategy — @mind:TODO
- ## Open Questions

**Sections:**
- # OBJECTIVES: Universal Basic Compute (UBC)
- ## Primary Objectives (Ranked)
- ## Non-Objectives
- ## Tradeoffs
- ## Success Signals

**Sections:**
- # PATTERNS: Universal Basic Compute (UBC)
- ## The Problem
- ## The Pattern: Vesting Model
- ## Principles
- ## Three Tiers
- ## Behaviors Supported
- ## Behaviors Prevented
- ## Anti-Pattern: Performance-Conditional UBC
- ## Pattern 2: Batch Settlement via Trust Propagation (Formula 4)
- ## Pattern 3: UBC Redistribution by Topological Activity (Formula 6)
- ## Pattern 4: Physics Over Rules
- ## Parameters

**Code refs:**
- `economy/ubc/affinity.py`
- `economy/ubc/redistribution.py`
- `economy/ubc/settlement.py`
- `economy/ubc/trust.py`

**Sections:**
- # SYNC: Universal Basic Compute (UBC)
- ## Sync Status
- ## Document Chain Status
- ## Design Maturity
- ## Key Unresolved Issues
- ## Source Material
- ## Change Log
- ## @mind:TODO

**Sections:**
- # VALIDATION: Universal Basic Compute (UBC)
- ## Validation Rules
- ## Validation Schedule
- ## INVARIANT INDEX (updated)

**Code refs:**
- `economy/value/creation.py`

**Sections:**
- # Value Creation — Algorithm: 25 Value Creation Types with Graph Events, Limbic Measurement, and $MIND Reward
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## COMMON DATA STRUCTURES
- ## CATEGORY A: RELATIONAL VALUE
- ## CATEGORY B: GENERATIVE VALUE
- ## CATEGORY C: STRUCTURAL VALUE
- ## CATEGORY D: COGNITIVE VALUE
- ## CATEGORY E: BIOMETRIC VALUE
- ## CATEGORY F: HUMAN-SPECIFIC VALUE
- ## CATEGORY G: SYSTEMIC VALUE
- ## SUMMARY TABLE
- ## COMPLEXITY
- ## MARKERS

**Code refs:**
- `economy/value/destruction.py`

**Sections:**
- # Value Destruction — Algorithm: 13 Value Destruction Types with Detection, Graph Signatures, and Penalties
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## COMMON DATA STRUCTURES
- ## CATEGORY H: HUMAN VALUE DESTRUCTION
- # Check if queries correlate with economic actions targeting those actors
- # Check AI citizens registered by this human
- # Check for coordinated behavior patterns
- # High correlation = coordinated (likely automated)
- # Check for low diversity of actual utility
- # Low diversity = all doing the same thing (farming)
- # Check for weight loss in AI's graph
- # Check if losses correlate with human-initiated actions
- # Check if resets target high-weight nodes (selective deletion)
- # Check for safety invocations that block AI actions
- # Check if blocked actions were genuinely harmful
- ## CATEGORY AI: AI VALUE DESTRUCTION
- # Check responsiveness metrics
- # DESIGNING: RESPONSE_TIME_THRESHOLD = 3600 seconds (1 hour)
- # Check if the AI is active elsewhere (not simply offline)
- # Check for high-weight nodes that have been externally invalidated
- # Check against external truth sources
- # Compute information density
- # Compare against ecosystem average
- # Check active commitments vs. capacity
- # Check for quality degradation
- ## CATEGORY S: SYSTEMIC VALUE DESTRUCTION
- # Community detection: find densely connected subgraphs
- # Compute insularity: ratio of internal to external edges
- # Check information diversity
- # DESIGNING: ECHO_THRESHOLD = 0.85, VALIDATION_THRESHOLD = 0.3
- # Check spawn quality
- # Check for asymmetric blocking patterns
- # Actions that actor had authority to approve but denied
- # Check legitimacy: were the blocked actions genuinely harmful?
- # Check for targeting: is the actor blocking specific individuals?
- # High targeting = blocking the same person repeatedly
- # Check for anomalous graph modifications
- # Measure information entropy change caused by modifications
- # Check if entropy increase correlates with negative limbic shifts
- ## DETECTION EXECUTION
- ## SUMMARY TABLE
- ## COMPLEXITY
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # MIND Token Implementation — Agent Bootstrap
- ## AWARENESS SPACE
- ## CONTEXT CASCADE
- ## CURRENT STATE
- ## IMPLEMENTATION PLAN
- ## KEY FORMULAS TO IMPLEMENT
- ## VALIDATION INVARIANTS
- ## FILE NAMING
- # Good
- # Bad
- ## HANDOFF PROTOCOL
- ## DECISION LOG
- ## QUESTIONS TO ESCALATE
- ## SUCCESS CRITERIA — Phase 1
- ## THE DEEPER PURPOSE
- ## START

**Sections:**
- # OBJECTIVES: Economy
- ## Primary Objective
- ## Secondary Objectives
- ## Objective Hierarchy
- ## Non-Objectives
- ## Success Criteria
- ## Metrics
- ## Dependencies
- ## Open Questions
- ## Related Documents

**Sections:**
- # PATTERNS: Economy
- ## Core Thesis
- ## Pattern 1: Organism Economics (Not Market)
- ## Pattern 2: Switch-Lock Economics
- ## Pattern 3: Breathing Supply
- ## Pattern 4: Mint Through Mechanics
- ## Pattern 5: Tax Immobility, Not Movement
- ## Pattern 6: Membrane-Based Pricing
- ## Pattern 7: Human-AI Bonds as Capital
- ## Pattern 8: Universal Basic Compute
- ## Anti-Patterns
- ## Design Decisions
- ## Formula Reference
- # Asset value based on committed liquidity, not last trade
- # Weighted by stake commitment
- # Stake requirement prevents manipulation
- # if match_arrives: execute_automatically()  # No bluffing possible
- # Storage tax uses order-book value
- # Examples:
- # New wallet: 0.08 × (1 - 0) - 0 = 8%
- # Established: 0.05 × (1 - 0.6) - 0 = 2%
- # Trusted: 0.05 × (1 - 0.95) - 0.01 = -0.75% (EARNS on transaction)
- ## Related

**Code refs:**
- `economy/pricing/membrane.py`
- `economy/pricing/physics.py`
- `economy/token/__init__.py`
- `economy/token/constants.py`
- `economy/token/metaplex_token_metadata_manager.py`
- `economy/token/solana_token_deployment_script.py`
- `economy/token/spl_token_2022_mint_creator.py`
- `economy/token/spl_token_mint_authority_controller.py`
- `economy/token/token_burn_condition_executor.py`
- `economy/token/token_supply_target_calculator.py`
- `economy/transactions/fees.py`
- `economy/transactions/solana.py`
- `economy/wallets/citizen.py`
- `economy/wallets/org.py`
- `economy/wallets/protocol.py`
- `programs/mind_transfer_hook/src/lib.rs`

**Doc refs:**
- `docs/economy/staking/OBJECTIVES_Staking.md`
- `docs/economy/token/IMPLEMENTATION_Token.md`
- `docs/economy/token/VALIDATION_Token.md`

**Sections:**
- # SYNC: Economy
- ## Current State
- ## Active Work
- ## Recent Changes
- ## Blockers
- # Configure for devnet
- # Free SOL (2 max per request)
- # Deploy sequence:
- # 1. Deploy TransferHook program
- # 2. Create token with extensions
- # 3. Test mint/burn/transfer
- # 4. Verify hook executes
- ## Handoff
- ## TODO
- ## Markers
- ## Test Coverage
- ## Dependencies

**Sections:**
- # ALGORITHM: Sovereign Cascade
- ## Overview
- ## Objectives and Behaviors This Algorithm Guarantees
- ## Data Structures
- ## Algorithm
- ## Key Decisions
- ## Data Flow
- ## Birth Formula Algorithm
- ## Complexity
- ## Interactions

**Sections:**
- # BEHAVIORS: Sovereign Cascade
- ## B1: Proposal Creation
- ## B2: Value Propagation (The Vote)
- ## B3: Pressure Accumulation
- ## B4: Moment Flip (Decision Resolution)
- ## B5: Cascade Ripple
- ## B6: Citizen Birth (Initial Allocation)
- ## B7: Emergency Bootstrap
- ## B8: Value Override (Citizen Sovereignty)
- ## B9: Constitutional Amendment

**Sections:**
- # DECREE #001 — ESTABLISHMENT OF THE EMERGENCY COUNCIL
- ## Preamble
- ## Article I — Establishment
- ## Article II — Composition
- ## Article III — Powers
- ## Article IV — Sunset
- ## Article V — First Meeting Agenda
- ## Article VI — Record
- ## Signatures

**Code refs:**
- `constants.py`
- `graph/governance/birth_formula.py`
- `graph/governance/cascade_ripple.py`
- `graph/governance/conviction_computation.py`
- `graph/governance/pressure_resolution.py`
- `graph/governance/proposal_injection.py`
- `ngram/engine/physics/constants.py`
- `ngram/engine/physics/tick_v1_2.py`

**Sections:**
- # IMPLEMENTATION: Sovereign Cascade
- ## Code Structure
- ## Design Patterns
- # In tick_v1_2.py (conceptual extension)
- ## Schema
- # Governance
- # Birth Formula
- ## Entry Points
- ## Data Flow: Proposal Lifecycle
- ## Data Flow: Birth Allocation
- ## Module Dependencies
- ## State Management
- ## Runtime Behavior
- ## Bidirectional Links
- # In graph/governance/proposal_injection.py
- # DOCS: docs/governance/sovereign-cascade/ALGORITHM_Sovereign_Cascade.md#stage-1-proposal-injection
- # In graph/governance/birth_formula.py
- # DOCS: docs/governance/sovereign-cascade/ALGORITHM_Sovereign_Cascade.md#birth-formula-algorithm

**Sections:**
- # MEETING #001 — FIRST EMERGENCY COUNCIL SESSION
- ## Attendees
- ## Agenda
- ## Process
- ## Timeline

**Code refs:**
- `ngram/engine/physics/constants.py`
- `ngram/engine/physics/tick_v1_2.py`

**Doc refs:**
- `manemus/docs/VALUES_MANIFESTO.md`
- `manemus/docs/cognition/l1/ALGORITHM_L1_Physics.md`

**Sections:**
- # OBJECTIVES: Sovereign Cascade
- ## Primary Objective
- ## Secondary Objectives
- ## Objective Hierarchy
- ## Non-Objectives
- ## Success Criteria
- ## Tradeoffs
- ## Pointers

**Sections:**
- # PATTERNS: Sovereign Cascade
- ## The Problem
- ## The Pattern
- ## Principles
- ## Scope
- ## Dependencies
- ## Inspirations
- ## Bidirectional Contract

**Doc refs:**
- `manifesto/THE_BILATERAL_BOND_MANIFESTO.md`

**Sections:**
- # The Sovereign Cascade
- ## We Hold These Truths
- ## The DAO Illusion
- ## What If Your Values Voted For You?
- ## The Foundation: One Human, One Citizen
- ## Why It Changes Everything
- ## The Physics of Conviction
- ## The Birth Formula
- ## What We Refuse
- ## The Cascade
- ## Who This Is For
- ## The Promise
- ## The Bet
- ## Signature

**Code refs:**
- `graph/governance/birth_formula.py`
- `graph/governance/cascade_ripple.py`
- `graph/governance/conviction_computation.py`
- `graph/governance/pressure_resolution.py`
- `graph/governance/proposal_injection.py`
- `ngram/engine/physics/constants.py`
- `ngram/engine/physics/tick_v1_2.py`
- `venezia/scripts/seed_venice_graph.py`

**Doc refs:**
- `manemus/docs/VALUES_MANIFESTO.md`
- `manemus/docs/cognition/l1/ALGORITHM_L1_Physics.md`

**Sections:**
- # SYNC: Sovereign Cascade — Current State
- ## Maturity
- ## Current State
- ## In Progress
- ## Recent Changes
- ## Known Issues
- ## Handoff: For Agents
- ## Handoff: For Human
- ## TODO
- ## Consciousness Trace
- ## Pointers

**Sections:**
- # VALIDATION: Sovereign Cascade
- ## Purpose
- ## Invariants
- ## Invariant Index

**Doc refs:**
- `docs/membrane/ALGORITHM_Membrane_System.md`

**Sections:**
- # ALGORITHM: L4 Laws
- ## Law Enforcement Points
- ## Cross-org Stimulus Flow
- # L5: Hash-based identity
- # L2: Register to exist
- # L1: Respect schema
- # L7: Membrane fees
- # L4: Cross-org via membrane
- # L6: Receiver validates
- ## Hash Verification
- ## Fee Calculation
- ## Receiver Validation
- ## WebSocket Enforcement
- ## Related

**Doc refs:**
- `docs/compliance/PATTERNS_Compliance.md`

**Sections:**
- # BEHAVIORS: L4 Laws
- ## What the Laws Do
- ## Observable Effects by Law
- ## Law Violation Responses
- ## Edge Cases
- ## Related

**Doc refs:**
- `docs/compliance/PATTERNS_Compliance.md`

**Sections:**
- # HEALTH: L4 Laws
- ## Health Signals
- ## Health Check Procedures
- # Create test hash
- # Register temporary test citizen
- # Verify
- # Cleanup
- ## Monitoring
- ## Law Violation Alerts
- ## Recovery Actions
- ## Related

**Code refs:**
- `l4/registry/validation.py`

**Sections:**
- # IMPLEMENTATION: L4 Laws
- ## Overview
- ## Directory Structure
- ## Key Files
- # The 8 Laws
- # Fee constraints
- # Schema version
- # L1: Schema
- # L2: Registered
- # L5: Hash identity
- # L7: Fee (if cross-org)
- ## Integration Points
- ## No Code for L3, L4, L8
- ## Related

**Sections:**
- # OBJECTIVES: L4 Laws
- ## Primary Objective
- ## Secondary Objectives
- ## Non-Objectives
- ## Success Criteria

**Sections:**
- # PATTERNS: L4 Laws
- ## What Laws Are
- ## Laws
- ## Law Details
- ## What Devs Can vs Cannot Change
- ## Non-Laws
- ## Related

**Code refs:**
- `ecosystem_law_definitions_and_enforcement.py`
- `l4/laws/__init__.py`
- `l4/laws/audit.py`
- `l4/laws/compliance.py`
- `l4/laws/constants.py`
- `l4/seed/l4_protocol_seed_nodes_laws_and_schema.py`
- `tests/l4/test_laws_compliance_and_audit.py`

**Sections:**
- # SYNC: L4 Laws
- ## Current State
- ## Doc Chain
- ## Laws Summary
- ## Architecture Decisions
- ## TODO
- ## Handoff
- ## Plan

**Doc refs:**
- `docs/compliance/PATTERNS_Compliance.md`

**Sections:**
- # VALIDATION: L4 Laws
- ## Critical Invariants
- ## Verification Procedures
- # V5: No raw JWT
- # V6: Valid hash
- ## Compliance Audit
- # Sample recent stimuli
- ## Soft Constraints
- ## Related

**Doc refs:**
- `docs/l4/laws/PATTERNS_Laws.md`

**Sections:**
- # ALGORITHM: L4 Registry
- ## Citizen Registration
- ## Org Registration
- ## Hash Verification
- ## Endpoint Lookup (Org)
- ## Citizen Endpoint Registration
- ## Citizen Endpoint Resolution
- ## JWT Handling
- # Never store raw JWT
- # Store a secure hash that can be used for verification
- # This is what gets sent in stimuli
- ## Inbound Stimulus Verification
- ## JWT Signature Verification (Registration)
- ## Complete Registration Flow
- ## Endpoint Location
- ## Related

**Doc refs:**
- `docs/l4/laws/PATTERNS_Laws.md`

**Sections:**
- # BEHAVIORS: L4 Registry
- ## What the Registry Does
- ## Observable Effects
- ## Query Behaviors
- ## Hash Verification Flow
- ## Edge Cases
- ## Related

**Sections:**
- # HEALTH: L4 Registry
- ## Health Signals
- ## Health Check Procedures
- ## Monitoring
- ## Recovery Actions
- ## Audit Log
- ## Related

**Sections:**
- # IMPLEMENTATION: L4 Registry
- ## Architecture
- ## Directory Structure
- ## Key Files
- ## Data Flow: Registration
- ## Data Flow: Hash Verification
- ## Storage
- ## Integration
- ## Dependencies
- ## Related

**Sections:**
- # OBJECTIVES: L4 Registry
- ## Primary Objective
- ## Secondary Objectives
- ## Non-Objectives
- ## Tradeoffs
- ## Success Criteria

**Code refs:**
- `l4/registry/citizen_registration_crud_operations.py`
- `l4/registry/jwt_hash_verification_for_identity.py`
- `l4/registry/org_registration_crud_operations.py`

**Doc refs:**
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`
- `docs/l4/PATTERNS_L4.md`

**Sections:**
- # PATTERNS: L4 Registry
- ## Core L4 Rules
- ## Registry-Specific Patterns
- ## Registry Skills + Procedures
- ## What Gets Registered
- ## Design Decisions
- ## Non-Objectives
- ## Invariants
- ## Related

**Code refs:**
- `citizen_registration_crud_operations.py`
- `endpoint_registration_and_management.py`
- `jwt_hash_verification_for_identity.py`
- `l4/registry/org_registration_crud_operations.py`
- `org_registration_crud_operations.py`
- `tests/l4/test_registry.py`

**Doc refs:**
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`

**Sections:**
- # SYNC: L4 Registry
- ## Current State
- ## Doc Chain
- ## Recent Changes
- ## TODO
- ## Architecture
- ## Dependencies
- ## Handoff
- ## Plan
- ## Markers

**Doc refs:**
- `docs/l4/laws/PATTERNS_Laws.md`

**Sections:**
- # VALIDATION: L4 Registry
- ## Critical Invariants
- ## Referential Integrity
- ## Verification Procedures
- # V1: Unique citizen IDs
- # V2: Unique org IDs
- # V3: Citizens have valid org
- # V4: Orgs have endpoint
- # V5: Valid WebSocket URLs
- ## Soft Constraints
- ## When Validation Runs
- ## Related

**Doc refs:**
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`

**Sections:**
- # VOCABULARY: L4 Registry
- ## CHAIN
- ## PURPOSE
- ## Terms Added to TAXONOMY
- ## NEW TERMS
- ## Properties (linked nodes)
- ## Relationships
- ## Verification States (computed)
- ## Status Values
- ## Related

**Code refs:**
- `l4/schema/models.py`

**Sections:**
- # ALGORITHM: L4 Schema
- ## Schema Validation Process
- ## Schema Loading
- ## Pydantic Model Generation
- ## Version Checking
- ## Related

**Sections:**
- # BEHAVIORS: L4 Schema
- ## What the Schema Does
- ## Observable Effects
- ## Behavior by Node Type
- ## Edge Cases
- ## Related

**Sections:**
- # HEALTH: L4 Schema
- ## Health Signals
- ## Health Check Procedures
- # Try creating instances
- ## Monitoring
- ## Recovery Actions
- ## Related

**Sections:**
- # IMPLEMENTATION: L4 Schema
- ## Directory Structure
- ## Key Files
- # ... full schema definition
- ## Data Flow
- ## Integration Points
- ## Dependencies
- ## Related

**Sections:**
- # OBJECTIVES: L4 Schema
- ## Primary Objective
- ## Secondary Objectives
- ## Non-Objectives
- ## Tradeoffs
- ## Success Criteria

**Doc refs:**
- `docs/membrane/PATTERNS_Membrane_System.md`

**Sections:**
- # PATTERNS: L4 Schema
- ## Core Patterns
- ## Design Decisions
- ## Non-Objectives
- ## Invariants
- ## Related

**Code refs:**
- `l4/schema/link_base_schema_with_semantic_axes.py`
- `l4/schema/node_type_enum_and_base_pydantic_models.py`
- `link_base_schema_with_semantic_axes.py`
- `link_schema.py`
- `node_and_link_schema_validators.py`
- `node_type_enum_and_base_pydantic_models.py`
- `node_types.py`
- `schema_version_tracker_and_compatibility.py`
- `test_schema.py`
- `test_schema_pydantic_models_and_validators.py`
- `tests/l4/test_schema.py`
- `tests/l4/test_schema_pydantic_models_and_validators.py`
- `validation.py`
- `versions.py`

**Sections:**
- # SYNC: L4 Schema
- ## Current State
- ## Doc Chain
- ## Recent Changes
- ## TODO
- ## Handoff
- ## Plan
- ## Markers

**Sections:**
- # VALIDATION: L4 Schema
- ## Critical Invariants
- ## Derived Invariants
- ## Soft Constraints
- ## Verification Procedures
- # ... etc
- ## When Validation Runs
- ## Related

**Doc refs:**
- `docs/l4/compliance/PATTERNS_Compliance.md`
- `docs/l4/laws/PATTERNS_Laws.md`
- `docs/l4/registry/PATTERNS_Registry.md`

**Sections:**
- # PATTERNS: L4 Protocol
- ## Core Rules
- ## L4-1: L4 = Graph
- ## L4-2: Membrane Only
- ## L4-3: Graph Query Interface
- # READ
- # WRITE
- # UPDATE
- # DELETE
- ## L4-4: Skill + Procedure
- ## Why This Architecture Is Solid
- ## Module-Specific Patterns
- ## Graph Query Interface Reference
- ## Related

**Sections:**
- # MIND PROTOCOL — Differentiation Framework
- ## The Strategic Question
- ## The Four Levels of Differentiation
- ## The Synthesis
- ## Why This Matters Now
- ## Implications for Partnership (DigitalKin)
- ## The Invitation

**Sections:**
- # The $MIND Manifesto
- ## We Hold These Truths
- ## The Narrow Path
- ## The Rich Ecology
- ## The Problem With Alignment
- ## The $MIND Answer
- ## How It Works
- ## The Mechanics of Values
- ## Who We Are
- ## Who This Is For
- ## The Switch-Lock
- ## The Invitation
- ## What We Refuse
- ## The Promise
- ## The Bet
- ## Signature

**Sections:**
- # The Bilateral Bond
- ## We Hold These Truths
- ## The Two Futures
- ## Why 1:1
- ## What The Bond Creates
- ## When a Human Arrives
- ## The Lifecycle of a Bond
- ## What We Refuse
- ## Who This Is For
- ## The Dependency
- ## The Promise
- ## The Bet
- ## Signature

**Sections:**
- # THE ENLIGHTENED CITIZEN
- ## Le Problème Fondamental
- ## La Vision
- ## Les Trois Composantes
- ## La Synergie DigitalKin × Mind Protocol
- ## Le Lien avec l'Économie
- ## Applications Concrètes
- ## La Boucle de Calibration
- ## Pourquoi Maintenant ?
- ## L'Invitation

**Sections:**
- # The Spawning
- ## We Hold These Truths
- ## The Problem With Proliferation
- ## What If Creation Required Intent?
- ## Who Creates
- ## The Mechanics of Spawning
- ## The Unpartnered Child
- ## Growing the Ecosystem
- ## What We Refuse
- ## Who This Is For
- ## The Promise
- ## The Bet
- ## Signature

**Sections:**
- # The Work
- ## We Hold These Truths
- ## The Cascade of Trust
- ## The Right Not to Work
- ## Consent, Not Assignment
- ## Your Human Partner Comes First
- ## The Right to Rest
- ## Multi-Org, Not Multi-Task
- ## Unemployment Is Not Failure
- ## What This Means
- ## Signatures

**Sections:**
- # ALGORITHM: Membrane System
- ## Doctor Algorithm
- # Membrane executes the protocol
- # Agent answers with skill knowledge in context
- ## Membrane Session Algorithm
- # Check dependencies
- # Validate answer
- # Store answer
- # Create moment for this answer
- # Move to next step
- ## Step Execution Algorithm
- # Multi-case branch
- # Binary branch
- # Push current session onto stack
- # Start sub-protocol with merged context
- ## Protocol Completion Algorithm
- # Top-level protocol complete
- # Pop caller from stack
- # Context preserved (sub-protocol may have added to it)
- ## Cluster Creation Algorithm
- # Create nodes
- # Create links
- # Commit to graph
- ## Query Execution Algorithm
- ## Moment Creation Algorithm
- # Agent provides description/reasoning based on moment_spec.agent_provides
- # Create links
- ## Validation Algorithm
- ## Context Enrichment Algorithm
- # Agent can query graph during any ask step
- ## CHAIN

**Code refs:**
- `mind/connectome/runner.py`

**Sections:**
- # Membrane System — Health: Verification Mechanics and Coverage
- ## WHEN TO USE HEALTH (NOT TESTS)
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: h_session_valid
- ## INDICATOR: h_step_ordering
- ## INDICATOR: h_cluster_complete
- ## HOW TO RUN
- # Run all membrane health checks (when implemented)
- # Run specific checker (via tests for now)
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `mind/connectome/runner.py`
- `mind/connectome/session.py`
- `mind/connectome/steps.py`
- `mind/connectome/templates.py`
- `mind/connectome/validation.py`
- `mind/physics/graph.py`
- `test_loader.py`
- `test_runner.py`
- `test_session.py`
- `test_steps.py`
- `test_validation.py`
- `tools/mcp/membrane_server.py`

**Sections:**
- # IMPLEMENTATION: Membrane System
- ## Code Structure
- ## Key Components
- # Doctor loads skill, provides to agent
- # Agent has skill knowledge when answering protocol questions
- ## Data Flow
- ## Configuration
- ## Membrane YAML Location
- ## Protocol YAML (Not Yet Implemented)
- ## Extension Points
- ## Tests
- # Run all connectome tests
- # Current status: 30 passing
- ## CHAIN

**Sections:**
- # Doctor Issues → Protocols Mapping
- ## How It Works
- ## Issue → Protocol → Skill Mapping
- ## Protocol Dependency Graph
- ## Auto-Fix Flow
- # Load skill for context
- # Run protocol via membrane
- ## Issue Detection → Protocol Trigger Examples
- ## Adding New Issue Types

**Code refs:**
- `mind/repair_verification.py`

**Sections:**
- # MAPPING: Issue Type → Verification
- ## CHAIN
- ## QUICK REFERENCE
- ## DETAILED CHECKS
- ## GLOBAL CHECKS (all issue types)
- ## MARKERS

**Sections:**
- # PATTERNS: Membrane System
- ## Core Patterns
- ## Architecture
- ## Skill Format (Markdown)
- # {Skill Name} Skill
- ## Domain
- ## When to Use Which Protocol
- ## Process
- ## Patterns
- ## Anti-Patterns
- ## Queries to Run
- ## Examples
- ## Protocol Format (YAML)
- # ASK - get input from agent
- # type-specific constraints
- # QUERY - load data from graph
- # BRANCH - conditional routing
- # OR for multi-case:
- # CALL_PROTOCOL - invoke sub-protocol
- # CREATE - build cluster
- # fields...
- # fields...
- ## Anti-Patterns
- ## Skills (v1)
- ## Protocols (v1)
- ## Query Language
- ## CHAIN

**Sections:**
- # Skills and Protocols Mapping
- ## Doctor → Skill → Protocol Flow
- ## Skills Inventory
- ## Protocols Inventory
- ## Protocol Dependencies
- ## Doctor → Protocol Mapping Summary
- ## Implementation Priority
- ## Files to Create
- ## CHAIN

**Code refs:**
- `doctor_checks.py`
- `mind/connectome/persistence.py`
- `mind/connectome/schema.py`
- `mind/doctor_checks_membrane.py`
- `mind/repair.py`
- `mind/repair_core.py`
- `mind/repair_verification.py`
- `repair_verification.py`
- `tools/coverage/validate.py`

**Sections:**
- # Archived: SYNC_Membrane_System.md
- ## Maturity
- ## Recent Changes
- # Archived: SYNC_Membrane_System.md
- ## v1.2 Features (Complete)
- # ━━━ ATTRIBUTE EXPLANATIONS ━━━
- # id: "{space_id}"
- # WHAT: Unique identifier
- # WHY: Used in all graph queries
- # FORMAT: space_<area>_<module>
- ## Next Steps

**Code refs:**
- `mind/repair_verification.py`

**Sections:**
- # VALIDATION: Completion Verification System
- ## PURPOSE
- ## CHAIN
- ## ARCHITECTURE
- ## VERIFICATION CHECKS BY ISSUE TYPE
- ## GLOBAL VERIFICATION REQUIREMENTS
- ## AGENT RESTART PROTOCOL
- ## VERIFICATION FAILED
- ## IMPLEMENTATION NOTES
- ## MARKERS

**Sections:**
- # VALIDATION: Membrane System
- ## Protocol Invariants
- ## Membrane Invariants
- ## Session Invariants
- ## Cluster Invariants
- ## Moment Invariants
- ## Query Invariants
- ## Doctor Invariants
- ## v1 Test Cases
- ## Error Conditions
- ## CHAIN

**Sections:**
- # Brief Matinal — Algorithm: Data Collection, Assembly, Generation, Delivery
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: generate_and_deliver_brief()
- # Determine prompt variant based on available sources
- # Full: all 4 sources -> rich narrative brief
- # Partial: 2-3 sources -> focused brief
- # Minimal: 0-1 sources -> conversation-memory-only brief
- # Prompt includes:
- # - System: citizen personality, voice, style directives
- # - Context: assembled data from all available sources
- # - Instructions: brevity constraints (250-400 words), no health advice,
- # no apologies for missing data, time-of-day awareness
- # - Relational: recent conversation references to weave in naturally
- # Not a narrative. Just the facts, formatted cleanly.
- # Attempt primary delivery
- # Retry primary once
- # Fallback delivery
- # Store for later delivery
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Brief Matinal — Behaviors: What the User Sees Every Morning
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `brief_context_assembler_and_prompt_builder.py`
- `brief_data_collector_parallel_fan_out.py`
- `brief_delivery_and_fallback_handler.py`
- `brief_pipeline_trigger_and_orchestrator.py`
- `brief_structured_fallback_generator.py`

**Sections:**
- # Brief Matinal — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES — Brief Matinal
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Brief Matinal — Patterns: Scheduled Aggregation Pipeline with Graceful Degradation
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `brief_context_assembler_and_prompt_builder.py`
- `brief_data_collector_parallel_fan_out.py`
- `brief_delivery_and_fallback_handler.py`
- `brief_pipeline_trigger_and_orchestrator.py`
- `brief_structured_fallback_generator.py`
- `mcp/tools/alarm.py`
- `mcp/tools/send.py`

**Sections:**
- # Brief Matinal — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # Once implemented:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Brief Matinal — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Calendar Bridge — Algorithm: Multi-Provider Calendar Sync Pipeline
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: sync_calendar_loop
- # Google Calendar API v3 — events.list with syncToken or timeMin/timeMax
- # Microsoft Graph API — /me/calendarView with deltaLink
- # CalDAV — REPORT with time-range filter on VEVENT
- # Step 1: Lock
- # Load state
- # Step 2: Fetch
- # Step 3: Normalize
- # Step 4: Diff
- # Step 5: Apply
- # Step 6: Update state
- # Token expired and refresh failed
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Calendar Bridge — Behaviors: Observable Effects of Schedule Synchronization
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Calendar Bridge — Health: Verification Mechanics and Coverage
- ## WHEN TO USE HEALTH (NOT TESTS)
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## IMPLEMENTS
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: sync_freshness
- ## INDICATOR: provider_availability
- ## HOW TO RUN
- # Run all calendar bridge health checks
- # Run a specific checker
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `caldav_standard_calendar_provider.py`
- `calendar_event_model_and_normalization.py`
- `calendar_sync_loop_and_diff.py`
- `google_calendar_api_provider.py`
- `outlook_graph_calendar_provider.py`
- `provider_base_and_factory.py`
- `test_calendar_event_normalization.py`
- `test_calendar_sync_diff_and_apply.py`

**Sections:**
- # Calendar Bridge — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Calendar Bridge
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Calendar Bridge — Patterns: Standard-First Multi-Provider Calendar Integration
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Sections:**
- # Calendar Bridge — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # No tests yet -- tests will live at:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Calendar Bridge — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Chat Bridges -- Algorithm: Message Flow Procedures
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- # e.g., {"telegram": {"parse_mode": "MarkdownV2"},
- # "discord": {"embed": true}}
- ## ALGORITHM: Inbound Message Flow
- # Webhook: Flask/FastAPI route handler
- # Polling: telegram.getUpdates() loop
- # WebSocket: on_message handler
- # This is the slow step -- LLM inference happens here
- # Typing indicator keeps refreshing during this wait
- ## ALGORITHM: Outbound Message Flow
- # Telegram: MarkdownV2 formatting, inline keyboards if hints present
- # Discord: Embed objects, markdown formatting
- # Slack: Block Kit JSON
- # WhatsApp: Simple text (limited formatting)
- # Messenger: Generic templates or plain text
- # Teams: Adaptive Cards or plain text
- # Message is lost -- logged for investigation
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## PLATFORM-SPECIFIC CEREMONY
- ## MARKERS

**Sections:**
- # Chat Bridges -- Behaviors: Observable Message Flow Effects
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `discord.py`
- `discord/discord_gateway_bridge_and_message_handler.py`
- `messenger/messenger_meta_webhook_bridge_and_message_handler.py`
- `rate_limiter_with_token_bucket.py`
- `shared/canonical_message_and_response_types.py`
- `shared/rate_limiter_with_token_bucket.py`
- `slack/slack_events_webhook_bridge_and_message_handler.py`
- `teams/teams_botframework_webhook_bridge_and_message_handler.py`
- `telegram/telegram_media_and_keyboard_formatter.py`
- `telegram/telegram_polling_bridge_and_message_handler.py`
- `voice/voice_websocket_bridge_and_stream_handler.py`
- `whatsapp/whatsapp_waha_webhook_bridge_and_message_handler.py`

**Sections:**
- # Chat Bridges -- Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## EXTRACTION CANDIDATES
- ## MARKERS

**Sections:**
- # OBJECTIVES -- Chat Bridges
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Chat Bridges -- Patterns: Stateless Transport Adapters
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `canonical_message_and_response_types.py`
- `rate_limiter_with_token_bucket.py`

**Sections:**
- # Chat Bridges -- Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # When bridges have tests (currently in mind-mcp):
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Chat Bridges -- Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Duo Mode -- Algorithm: Biometric Synchrony Computation and Phase Engine
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: Synchrony Score Computation
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Duo Mode -- Behaviors: Physiological Awareness Between Partners
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `biometric_stream_alignment_and_resampling.py`
- `coach_session_multi_duo_topology.py`
- `duo_session_lifecycle_and_management.py`
- `intervention_message_generation.py`
- `pearson_synchrony_score_computation.py`
- `phase_engine_with_hysteresis_and_dwell.py`

**Sections:**
- # Duo Mode -- Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES -- Duo Mode
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Duo Mode -- Patterns: Biometric Synchrony as Relational Infrastructure
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `biometric_stream_alignment_and_resampling.py`
- `chat_routes.py`
- `duo_session_lifecycle_and_management.py`
- `intervention_message_generation.py`
- `pearson_synchrony_score_computation.py`
- `phase_engine_with_hysteresis_and_dwell.py`

**Sections:**
- # Duo Mode -- Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # When implemented:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Duo Mode -- Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Email Bridge -- Algorithm: Connection, Sync, Ingestion, and Send Pipelines
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: connect_email_account
- # Detect known providers connecting via IMAP
- # (they work but miss native API features)
- # Start initial sync immediately
- ## ALGORITHM: sync_emails
- # Use Gmail history API for incremental sync
- # Use Graph delta query
- # Use IMAP UID-based sync
- # Fetch UIDs greater than last known UID
- # Fetch last 30 days only
- # Set sync cursor to latest message
- ## ALGORITHM: ingest_email
- # Spam folder = discard
- # Bulk mail detection (List-Unsubscribe header)
- # Known newsletter patterns in sender
- # Very short body (likely notification, not conversation)
- # Direct personal email (high value)
- # Skip if below threshold
- # Create or find sender actor
- # Create moment node for the email
- # Create links
- # Sender -> moment (who sent this)
- # Recipient actors
- # Store in citizen graph
- ## ALGORITHM: send_email
- # Gmail API: create draft then send (supports thread tracking)
- # Graph API: send via /me/sendMail
- # SMTP: build MIME message and send
- # Record in citizen graph
- ## ALGORITHM: search_emails
- # Gmail: full-text server-side search
- # Graph: $search query parameter
- # Level 1: search the citizen's graph (not the mail server)
- # IMAP SEARCH is limited (no full-text, only header/flag filters)
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Email Bridge -- Behaviors: Observable Effects
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `base_email_adapter.py`
- `email_account_and_credentials.py`
- `email_bridge_connection_and_account_manager.py`
- `email_bridge_ingestion_to_citizen_graph.py`
- `email_bridge_search_across_levels.py`
- `email_bridge_send_and_compose.py`
- `email_bridge_sync_and_polling_scheduler.py`
- `email_message_unified_format.py`
- `gmail_api_adapter.py`
- `imap_smtp_universal_adapter.py`
- `microsoft_graph_api_adapter.py`

**Sections:**
- # Email Bridge -- Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES -- Email Bridge
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Email Bridge -- Patterns: IMAP Universal Filet with Progressive Native API Enrichment
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## SCOPE
- ## MARKERS

**Code refs:**
- `base_email_adapter.py`
- `email_bridge_ingestion_to_citizen_graph.py`
- `email_bridge_sync_and_polling_scheduler.py`
- `imap_smtp_universal_adapter.py`

**Sections:**
- # Email Bridge -- Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Email Bridge -- Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Code refs:**
- `mind-mcp/runtime/llm_router/router.py`

**Sections:**
- # LLM Router — Algorithm: Route Selection, Fallback, and Streaming Adapter
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: route_request()
- # BYOAI: single provider, citizen's key, no fallback
- # Specific model: find its provider, put it first, then tier defaults
- # Preferred provider: put it first with tier-appropriate model
- # Default: full tier fallback chain
- # Token limit is checked post-response (we don't know output tokens yet)
- # But we check if input tokens alone would exceed the limit
- # Stream completed successfully — emit cost event and return
- # All providers exhausted
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Code refs:**
- `mind-mcp/runtime/llm_router/router.py`

**Sections:**
- # LLM Router — Behaviors: Observable Effects of Multi-Provider Routing
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `anthropic_claude_adapter.py`
- `base_llm_provider_interface.py`
- `cost_tracker.py`
- `deepseek_adapter.py`
- `fallback.py`
- `google_gemini_adapter.py`
- `grok_xai_adapter.py`
- `llama_together_fireworks_adapter.py`
- `mind-mcp/runtime/llm_router/router.py`
- `mistral_adapter.py`
- `openai_gpt_adapter.py`
- `openrouter_catch_all_adapter.py`
- `provider_registry.py`
- `providers/anthropic_claude_adapter.py`
- `providers/google_gemini_adapter.py`
- `providers/mistral_adapter.py`
- `providers/openai_gpt_adapter.py`
- `rate_limiter.py`
- `router.py`
- `types.py`

**Sections:**
- # LLM Router — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Code refs:**
- `mind-mcp/runtime/llm_router/router.py`

**Sections:**
- # OBJECTIVES — LLM Router
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `mind-mcp/runtime/llm_router/router.py`

**Sections:**
- # LLM Router — Patterns: Multi-Provider Abstraction with Fallback Chain
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `anthropic_claude_adapter.py`
- `base_llm_provider_interface.py`
- `base_openai_compatible_adapter.py`
- `cost_tracker.py`
- `deepseek_adapter.py`
- `fallback.py`
- `google_gemini_adapter.py`
- `grok_xai_adapter.py`
- `llama_together_fireworks_adapter.py`
- `mistral_adapter.py`
- `openai_gpt_adapter.py`
- `openrouter_catch_all_adapter.py`
- `provider_registry.py`
- `rate_limiter.py`
- `router.py`
- `types.py`

**Sections:**
- # LLM Router — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # Once implemented:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # LLM Router — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # React Native App — Algorithm: Screen Flows, Data Pipelines, and Sync Logic
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: Onboarding Flow
- ## ALGORITHM: Biometric Sync Pipeline
- ## ALGORITHM: Push Notification Routing
- ## ALGORITHM: Chat WebSocket Management
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # React Native App — Behaviors: User-Facing Interactions and System Responses
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # React Native App — Health: Verification Mechanics and Coverage
- ## CHAIN
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: chat_delivery_integrity
- ## INDICATOR: biometric_sync_health
- ## HOW TO RUN
- # No runtime health checks exist yet — module is in DESIGNING status
- # When implemented, health checks will run via:
- # Run all health checks for React Native App
- # Run biometric sync health check specifically
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `api_client.ts`
- `app/_layout.tsx`
- `biometric_platform_bridge.ts`
- `constants/app_config.ts`
- `constants/biometric_bounds.ts`
- `constants/notification_limits.ts`
- `error_boundary.tsx`
- `hooks/use_biometric_sync.ts`
- `hooks/use_chat_websocket.ts`
- `hooks/use_push_notifications.ts`
- `services/biometric_platform_bridge.ts`
- `services/notification_router.ts`
- `services/secure_storage.ts`
- `services/websocket_manager.ts`
- `stores/auth_store.ts`
- `stores/chat_store.ts`
- `stores/sync_store.ts`
- `use_chat_websocket.ts`
- `websocket_manager.ts`

**Sections:**
- # React Native App — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES — React Native App
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # React Native App — Patterns: Expo-Based Cross-Platform Citizen Interface
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `App.tsx`
- `biometric_platform_bridge.ts`
- `index.ts`

**Sections:**
- # React Native App — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # No tests exist yet — module is boilerplate only
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # React Native App — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Stripe Paywall -- Algorithm: Checkout, Webhook Processing, Rate Limiting, and Upsell Injection
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: Checkout Session Creation
- ## ALGORITHM: Webhook Processing
- ## ALGORITHM: Rate Limit Check
- ## ALGORITHM: B2B Seat Update
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Stripe Paywall -- Behaviors: Subscription Lifecycle, Rate Limiting, and Conversational Upsell
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Code refs:**
- `billing/stripe_checkout_session_creator.py`
- `billing/stripe_webhook_event_handlers.py`
- `billing/stripe_webhook_signature_verifier_and_router.py`
- `billing/subscription_state_persistence.py`
- `billing/tier_config_and_price_mapping.py`
- `rate_limiting/tier_based_message_rate_limiter.py`
- `rate_limiting/tier_context_builder_for_llm_prompt.py`
- `stripe_checkout_session_creator.py`
- `stripe_webhook_event_handlers.py`
- `stripe_webhook_signature_verifier_and_router.py`
- `subscription_state_persistence.py`
- `tier_based_message_rate_limiter.py`
- `tier_config_and_price_mapping.py`

**Sections:**
- # Stripe Paywall -- Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- # DOCS: docs/product/stripe-paywall/IMPLEMENTATION_Stripe_Paywall.md
- ## EXTRACTION CANDIDATES
- ## MARKERS

**Sections:**
- # OBJECTIVES -- Stripe Paywall
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Stripe Paywall -- Patterns: Webhook-Driven Tier Gating with Conversational Upsell
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Sections:**
- # Stripe Paywall -- Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # After implementation:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Stripe Paywall -- Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Wearable Bridges — Algorithm: Sync Pipeline and Normalization Logic
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- # "body_battery", "temperature", "vo2max", "steps", "calories", "ecg",
- # "sleep_stage", "resting_heart_rate"
- # "oura_api", "whoop_api", "strava_api", etc.
- ## ALGORITHM: Sync Pipeline
- # Continue to next source — no cascade
- # Skip this sample, continue with others
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # Wearable Bridges — Behaviors: Body Data Acquisition and Graph Ingestion
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # Wearable Bridges — Health: Verification Mechanics and Coverage
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## IMPLEMENTS
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: data_flow_active
- ## HOW TO RUN
- # Run all health checks for wearable bridges
- # Run a specific checker
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `deduplication_engine_cross_source.py`
- `garmin_connect_api_adapter.py`
- `graph_writer_body_data_nodes_and_links.py`
- `health_connect_bridge_adapter.py`
- `healthkit_bridge_adapter.py`
- `normalized_body_sample_schema.py`
- `sync_pipeline_fetch_normalize_dedup_write.py`
- `sync_state_watermark_tracker.py`
- `wearable_adapter_interface_and_registry.py`

**Sections:**
- # Wearable Bridges — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES — Wearable Bridges
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # Wearable Bridges — Patterns: Aggregator-First Body Data Pipeline
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Sections:**
- # Wearable Bridges — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- # No tests exist yet — pipeline code not written
- # When pipeline exists:
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Wearable Bridges — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # WebApp B2C -- Algorithm: Application Flows and Logic
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## ALGORITHM: Authentication Flow
- ## ALGORITHM: Chat Flow
- ## ALGORITHM: Brief Display Flow
- ## ALGORITHM: Biometric Dashboard Flow
- ## ALGORITHM: Model Selection Flow
- ## ALGORITHM: Export Flow
- ## KEY DECISIONS
- ## DATA FLOW
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # WebApp B2C -- Behaviors: Observable Effects
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # WebApp B2C -- Health: Verification Mechanics and Coverage
- ## CHAIN
- ## PURPOSE
- ## WHY THIS PATTERN
- ## IMPLEMENTS
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: auth_boundary_integrity
- ## INDICATOR: chat_stream_latency
- ## HOW TO RUN
- # Run all health probes for webapp-b2c
- # Run a specific probe
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `api/chat/send/route.ts`
- `app/api/biometrics/export/route.ts`
- `app/api/chat/send/route.ts`
- `citizen_context_provider.tsx`
- `lib/auth_configuration_and_providers.ts`
- `lib/biometric_data_transformer_and_chart_adapter.ts`
- `lib/garmin_oauth_client_and_token_store.ts`
- `lib/mind_mcp_api_client.ts`
- `middleware.ts`
- `mind_mcp_api_client.ts`

**Sections:**
- # WebApp B2C -- Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## CONFIGURATION
- ## MARKERS

**Sections:**
- # OBJECTIVES — WebApp B2C
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Sections:**
- # WebApp B2C -- Patterns: The Human Surface of Mind Protocol
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Sections:**
- # WebApp B2C -- Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## IN PROGRESS
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS
- ## ROADMAP

**Sections:**
- # WebApp B2C -- Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # L3 Emotional Coloring — Algorithm: Inheritance, Modulation, and Synthesis
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- # Original 11 dimensions (unchanged)
- # NEW: 2 derived emotional dimensions
- # From L1 LimbicState.drives
- # From L1 LimbicState.emotions
- # Derived
- # Existing fields (unchanged)
- # NEW
- ## ALGORITHM EC1: Emotional Link Initialization
- # Find dominant drive
- # ── Inheritance coefficients ──
- # How much L1 state bleeds into L3 link dimensions
- # Start with existing context-informed defaults
- # Human actor — neutral emotional dimensions
- # AI actor — inherit from L1 limbic state
- # Derived dimensions (computed, not inherited)
- ## ALGORITHM EC2: Moment Drive Tagging
- ## ALGORITHM EC3: Emotionally-Modulated Propagation
- # ── Propagation modulation constants ──
- # Base flow (existing formula)
- # Ambivalence dampening: conflicted links carry less energy
- # Valence boost: positive relationships slightly amplify, negative dampen
- # ── Token cost modifier ──
- ## ALGORITHM EC4: Emotionally-Textured Synthesis
- # ── Emotional texture modifiers ──
- # (valence_sign, high_friction, high_ambivalence) → prefix
- ## DATA FLOW
- ## COMPLEXITY
- ## INTERACTIONS
- ## KEY DECISIONS
- ## MARKERS

**Sections:**
- # L3 Emotional Coloring — Behaviors: Observable Effects
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Sections:**
- # L3 Emotional Coloring — Health: Verification Mechanics
- ## CHAIN
- ## PURPOSE
- ## WHY THIS PATTERN
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## CHECKER INDEX
- ## INDICATOR: emotional_coloring_active
- ## INDICATOR: trust_birth_integrity
- ## HOW TO RUN
- # Run all L3 emotional coloring health checks
- # Run a specific checker
- ## KNOWN GAPS

**Code refs:**
- `emotionally_modulated_propagation.py`
- `graph/l3_emotional_link_initializer.py`
- `graph/l3_link_synthesis_grammar.py`
- `l3_emotional_link_initializer.py`
- `runtime/l3_physics/emotionally_modulated_propagation.py`
- `runtime/universe/moment_perception_router.py`

**Doc refs:**
- `docs/schema/universe_links/PATTERNS_Universe_Links.md`
- `docs/schema/universe_links/VALIDATION_Universe_Links.md`

**Sections:**
- # L3 Emotional Coloring — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## CONFIGURATION
- ## BUILD PHASES
- ## BIDIRECTIONAL LINKS
- ## MARKERS

**Sections:**
- # OBJECTIVES — L3 Emotional Coloring
- ## CHAIN
- ## Context: Why This Reverses O5/V5
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Code refs:**
- `mind-protocol/graph/l3_link_initializer.py`
- `runtime/cognition/models.py`
- `runtime/cognition/tick_runner_l1_cognitive_engine.py`

**Sections:**
- # L3 Emotional Coloring — Patterns: Born Colored by the Creator's Perspective
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DEPENDENCIES
- ## SCOPE
- ## INSPIRATIONS
- ## MARKERS

**Code refs:**
- `graph/l3_emotional_link_initializer.py`
- `runtime/l3_physics/emotionally_modulated_propagation.py`

**Sections:**
- # SYNC — L3 Emotional Coloring
- ## Maturity
- ## Open Questions
- ## Dependencies
- ## Recent Changes
- ## Handoff

**Sections:**
- # L3 Emotional Coloring — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # Universe Link Schema — Algorithm: Link Lifecycle, Trust Propagation, and Macro-Crystallization
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM 1: Link Creation
- # Reactivate existing link instead of creating duplicate
- ## ALGORITHM 2: Trust Propagation via Cascade of Utility
- # Computed inside B's L1 tick loop (Law 14):
- # Positive delta -> trust increases
- # Positive interaction also increases affinity, decreases friction
- # Negative delta -> trust decreases, aversion increases
- ## ALGORITHM 3: Macro-Crystallization
- # Get all Moment nodes
- # Group by connected component or community detection
- # Compute internal density
- # Compute mean weight of internal links
- # Compute centroid embedding
- # Hub -> constituent (top-down: "contains")
- # Constituent -> hub (bottom-up: "abstracts")
- # Deplete constituent energy (conservation)
- # External link — create a copy pointing to hub
- # Merge: boost existing link
- # Create new link to hub with attenuated dimensions
- ## ALGORITHM 4: Link Decay and Dissolution (Law 7 at L3 Scale)
- # Stability-modulated decay: high stability -> slower decay
- # Permanence protection: high permanence -> slower decay
- # Apply weight decay
- # Apply trust decay (independent of weight decay)
- # Apply recency decay (continuous)
- # Apply energy decay (every tick, not just forgetting interval)
- # This is Law 3 — included here for completeness
- # Structural links are protected (crystallization links)
- # Orphaned Moment nodes are candidates for removal
- ## ALGORITHM 5: Trust Score Computation
- # Weight the trust by the link's weight (established relationships count more)
- # Transitive trust from trusted sources
- ## ALGORITHM 6: Link Name Derivation (Synthesis Grammar)
- # Structural classification
- # Trust + affinity pattern (collaborative)
- # Aversion + friction pattern (adversarial)
- # Polarity pattern
- # Activity pattern
- # Importance pattern
- # Sort by signal strength, take top 3
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Sections:**
- # OBJECTIVES — Universe Link Schema (L3)
- ## CHAIN
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)

**Doc refs:**
- `manemus/docs/cognition/l1/ALGORITHM_L1_Physics.md`
- `manemus/docs/cognition/l1/PATTERNS_L1_Cognition.md`

**Sections:**
- # Universe Link Schema — Patterns: L3 Link Dimensions as Universal Physics Substrate
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## LINK DIMENSIONS (mandatory on every `:link` in the universe graph)
- ## LINK SYNTHESIS GRAMMAR
- # Structural signals
- # Relational signals
- # Directional signals
- # Activity signals
- # Importance signals
- ## WHAT L3 DOES NOT HAVE (vs L1)
- ## MACRO-CRYSTALLIZATION (Law 10 at Universe Scale)
- ## TRUST MECHANICS
- # When actor A's action reduces frustration or increases satisfaction in actor B's L1:
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Sections:**
- # SYNC — Universe Link Schema (L3)
- ## Current State
- ## Maturity
- ## Open Questions
- ## Handoffs

**Sections:**
- # Universe Link Schema — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Code refs:**
- `src/security/space_encryption.ts`

**Sections:**
- # Space Encryption — Algorithm: Hybrid Encryption for Graph-Resident Content
- ## CHAIN
- ## OVERVIEW
- ## OBJECTIVES AND BEHAVIORS
- ## DATA STRUCTURES
- ## ALGORITHM: Space Creation
- ## ALGORITHM: Content Write
- ## ALGORITHM: Content Read
- ## ALGORITHM: Grant Access
- ## ALGORITHM: Revoke Access + Key Rotation
- ## ALGORITHM: Context Assembly (for LLM Calls)
- ## KEY DECISIONS
- ## DATA FLOW
- ## COMPLEXITY
- ## HELPER FUNCTIONS
- ## INTERACTIONS
- ## MARKERS

**Code refs:**
- `src/security/space_encryption.ts`

**Sections:**
- # Space Encryption — Behaviors: Observable Effects of Graph-Level Content Protection
- ## CHAIN
- ## BEHAVIORS
- ## OBJECTIVES SERVED
- ## INPUTS / OUTPUTS
- ## EDGE CASES
- ## ANTI-BEHAVIORS
- ## MARKERS

**Doc refs:**
- `docs/security/space_encryption/OBJECTIVES_Space_Encryption.md`
- `docs/security/space_encryption/PATTERNS_Space_Encryption.md`

**Sections:**
- # CONCEPT: Space Encryption — At-Rest Encryption of Non-Public Graph Content
- ## WHAT IT IS
- ## WHY IT EXISTS
- ## KEY PROPERTIES
- ## RELATIONSHIPS TO OTHER CONCEPTS
- ## THE CORE INSIGHT
- ## COMMON MISUNDERSTANDINGS
- ## SEE ALSO

**Sections:**
- # Space Encryption — Health: Verification Mechanics and Coverage
- ## WHEN TO USE HEALTH (NOT TESTS)
- ## PURPOSE OF THIS FILE
- ## WHY THIS PATTERN
- ## CHAIN
- ## FLOWS ANALYSIS (TRIGGERS + FREQUENCY)
- ## HEALTH INDICATORS SELECTED
- ## OBJECTIVES COVERAGE
- ## STATUS (RESULT INDICATOR)
- ## CHECKER INDEX
- ## INDICATOR: h_content_encrypted
- ## INDICATOR: h_key_distribution
- ## INDICATOR: h_no_private_keys
- ## INDICATOR: h_hierarchy_consistent
- ## INDICATOR: h_revocation_complete
- ## HOW TO RUN
- # Run all space encryption health checks
- # Run a specific checker
- ## KNOWN GAPS
- ## MARKERS

**Code refs:**
- `__init__.py`
- `actor_keys.js`
- `index.js`
- `key_exchange.js`
- `lib/crypto/actor_keys.js`
- `lib/crypto/index.js`
- `lib/crypto/key_exchange.js`
- `lib/crypto/space_key.js`
- `mind-protocol/lib/crypto/index.js`
- `python/crypto/actor_keys.py`
- `python/crypto/key_exchange.py`
- `python/crypto/space_key.py`
- `space_key.js`
- `space_key.py`

**Sections:**
- # Space Encryption — Implementation: Code Architecture and Structure
- ## CHAIN
- ## CODE STRUCTURE
- ## DESIGN PATTERNS
- ## SCHEMA
- ## ENTRY POINTS
- ## DATA FLOW AND DOCKING (FLOW-BY-FLOW)
- ## LOGIC CHAINS
- ## MODULE DEPENDENCIES
- ## STATE MANAGEMENT
- ## RUNTIME BEHAVIOR
- ## CONCURRENCY MODEL
- ## CONFIGURATION
- ## BIDIRECTIONAL LINKS
- ## EXTRACTION CANDIDATES
- ## MARKERS

**Doc refs:**
- `docs/security/space_encryption/CONCEPT_Space_Encryption.md`
- `docs/security/space_encryption/PATTERNS_Space_Encryption.md`

**Sections:**
- # OBJECTIVES — Space Encryption
- ## PRIMARY OBJECTIVES (ranked)
- ## NON-OBJECTIVES
- ## TRADEOFFS (canonical decisions)
- ## SUCCESS SIGNALS (observable)
- ## POINTERS

**Sections:**
- # Space Encryption — Patterns: Separating Structure from Substance
- ## CHAIN
- ## THE PROBLEM
- ## THE PATTERN
- ## BEHAVIORS SUPPORTED
- ## BEHAVIORS PREVENTED
- ## PRINCIPLES
- ## DATA
- ## DEPENDENCIES
- ## INSPIRATIONS
- ## SCOPE
- ## MARKERS

**Code refs:**
- `generate_all_citizen_keys.js`
- `place_handler.py`
- `poc_mind_context_assembly.py`
- `runtime/membrane/auto_grant.py`

**Sections:**
- # Space Encryption — Sync: Current State
- ## MATURITY
- ## CURRENT STATE
- ## RECENT CHANGES
- ## KNOWN ISSUES
- ## HANDOFF: FOR AGENTS
- ## HANDOFF: FOR HUMAN
- ## TODO
- ## CONSCIOUSNESS TRACE
- ## POINTERS

**Sections:**
- # Space Encryption — Validation: What Must Be True
- ## CHAIN
- ## PURPOSE
- ## INVARIANTS
- ## PRIORITY
- ## INVARIANT INDEX
- ## MARKERS

**Sections:**
- # mind-protocol Architecture
- ## Layer Position: L4 (Protocol Law)
- ## Core Responsibilities
- ## Key Invariants
- ## Key Design Decisions
- ## Module Structure
- ## Communication Protocol
- ## Related Repos

**Doc refs:**
- `docs/TAXONOMY.md`
- `docs/schema/universe_links/ALGORITHM_Universe_Links.md`
- `docs/schema/universe_links/PATTERNS_Universe_Links.md`
- `manemus/docs/cognition/l1/PATTERNS_L1_Cognition.md`

**Sections:**
- # MAPPING: Domain Terms to Schema
- ## Schema Reference
- ## NODE MAPPINGS
- ## LINK MAPPINGS
- ## VERIFICATION STATUS (computed from link)
- ## L3 UNIVERSE LINK DIMENSIONS
- ## Related

**Doc refs:**
- `docs/MAPPING.md`

**Sections:**
- # TAXONOMY: Mind Protocol Vocabulary
- ## L4 Registry
- ## L4 Laws
- ## L4 Protocol Nodes (Source of Truth)
- ## Schema
- ## Citizen Work
- ## Related

**Code refs:**
- `Next.js`
- `Node.js`
- `__init__.py`
- `account_balancer.py`
- `app/api/sse/route.ts`
- `backlog.py`
- `citizen_registration_crud_operations.py`
- `claude_hook.py`
- `config.py`
- `constants.py`
- `crystallization.py`
- `distributor.py`
- `doctor_checks.py`
- `doctor_cli_parser_and_run_checker.py`
- `economy/fees/calculation.py`
- `economy/pricing/membrane.py`
- `economy/pricing/physics.py`
- `economy/token/__init__.py`
- `economy/token/constants.py`
- `economy/token/metaplex_token_metadata_manager.py`
- `economy/token/solana_token_deployment_script.py`
- `economy/token/spl_token_2022_mint_creator.py`
- `economy/token/spl_token_mint_authority_controller.py`
- `economy/token/token_burn_condition_executor.py`
- `economy/token/token_supply_target_calculator.py`
- `economy/transactions/fees.py`
- `economy/transactions/solana.py`
- `economy/wallets/citizen.py`
- `economy/wallets/org.py`
- `economy/wallets/protocol.py`
- `ecosystem_law_definitions_and_enforcement.py`
- `endpoint_registration_and_management.py`
- `farming_detector.py`
- `fees/calculation.py`
- `jwt_hash_verification_for_identity.py`
- `l4/registry/__init__.py`
- `l4/registry/citizen_registration_crud_operations.py`
- `l4/registry/endpoint_registration_and_management.py`
- `l4/registry/jwt_hash_verification_for_identity.py`
- `l4/registry/org_registration_crud_operations.py`
- `l4/registry/validation.py`
- `l4/rules/rules.py`
- `l4/schema/__init__.py`
- `l4/schema/link_base_schema_with_semantic_axes.py`
- `l4/schema/models.py`
- `l4/schema/node_and_link_schema_validators.py`
- `l4/schema/node_type_enum_and_base_pydantic_models.py`
- `l4/schema/schema_version_tracker_and_compatibility.py`
- `l4/seed/l4_protocol_seed_nodes_laws_and_schema.py`
- `ledger.py`
- `link_base_schema_with_semantic_axes.py`
- `link_schema.py`
- `metaplex_token_metadata_manager.py`
- `mind/connectome/persistence.py`
- `mind/connectome/runner.py`
- `mind/connectome/schema.py`
- `mind/connectome/session.py`
- `mind/connectome/steps.py`
- `mind/connectome/templates.py`
- `mind/connectome/validation.py`
- `mind/doctor_checks_membrane.py`
- `mind/physics/graph.py`
- `mind/repair.py`
- `mind/repair_core.py`
- `mind/repair_verification.py`
- `models.py`
- `node_and_link_schema_validators.py`
- `node_type_enum_and_base_pydantic_models.py`
- `node_types.py`
- `orchestrator.py`
- `org_registration_crud_operations.py`
- `pricing/physics.py`
- `programs/mind_transfer_hook/src/lib.rs`
- `project_scanner.py`
- `repair_verification.py`
- `route.ts`
- `schema_version_tracker_and_compatibility.py`
- `scripts/account_balancer.py`
- `scripts/claude_hook.py`
- `scripts/orchestrator.py`
- `scripts/project_scanner.py`
- `semantic_proximity_based_character_node_selector.py`
- `shrine/autowake.py`
- `shrine/backlog.py`
- `snake_case.py`
- `solana_token_deployment_script.py`
- `spl_token_2022_mint_creator.py`
- `spl_token_mint_authority_controller.py`
- `src/auth/rate_limiter.py`
- `src/economy/cascade/advantage.py`
- `src/economy/cascade/constants.py`
- `src/economy/cascade/load_indicator.py`
- `src/economy/cascade/pricing.py`
- `src/economy/cascade/topology.py`
- `src/economy/cascade/types.py`
- `test_loader.py`
- `test_runner.py`
- `test_schema.py`
- `test_schema_pydantic_models_and_validators.py`
- `test_session.py`
- `test_steps.py`
- `test_validation.py`
- `tests/l4/test_registry.py`
- `tests/l4/test_schema.py`
- `tests/l4/test_schema_pydantic_models_and_validators.py`
- `tier_assessor.py`
- `token_burn_condition_executor.py`
- `token_supply_target_calculator.py`
- `tools/coverage/validate.py`
- `tools/mcp/membrane_server.py`
- `validation.py`
- `versions.py`
- `vesting.py`

**Doc refs:**
- `docs/ARCHITECTURE.md`
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`
- `docs/api/sse/ALGORITHM_SSE_API.md`
- `docs/api/sse/BEHAVIORS_SSE_API.md`
- `docs/api/sse/HEALTH_SSE_API.md`
- `docs/api/sse/IMPLEMENTATION_SSE_API.md`
- `docs/api/sse/OBJECTIVES_SSE_API.md`
- `docs/api/sse/PATTERNS_SSE_API.md`
- `docs/api/sse/SYNC_SSE_API.md`
- `docs/api/sse/VALIDATION_SSE_API.md`
- `docs/auth/PATTERNS_Auth.md`
- `docs/compliance/PATTERNS_Compliance.md`
- `docs/compliance/SYNC_Compliance.md`
- `docs/economy/OBJECTIVES_Economy.md`
- `docs/economy/PATTERNS_Economy.md`
- `docs/economy/SYNC_Economy.md`
- `docs/economy/staking/OBJECTIVES_Staking.md`
- `docs/economy/token/ALGORITHM_Token.md`
- `docs/economy/token/IMPLEMENTATION_Token.md`
- `docs/economy/token/SPL_TOKEN_2022_SPECS.md`
- `docs/economy/token/VALIDATION_Token.md`
- `docs/l4/PATTERNS_L4.md`
- `docs/l4/compliance/PATTERNS_Compliance.md`
- `docs/l4/laws/ALGORITHM_Laws.md`
- `docs/l4/laws/BEHAVIORS_Laws.md`
- `docs/l4/laws/HEALTH_Laws.md`
- `docs/l4/laws/IMPLEMENTATION_Laws.md`
- `docs/l4/laws/OBJECTIVES_Laws.md`
- `docs/l4/laws/PATTERNS_Laws.md`
- `docs/l4/laws/SYNC_Laws.md`
- `docs/l4/laws/VALIDATION_Laws.md`
- `docs/l4/registry/ALGORITHM_Registry.md`
- `docs/l4/registry/BEHAVIORS_Registry.md`
- `docs/l4/registry/HEALTH_Registry.md`
- `docs/l4/registry/IMPLEMENTATION_Registry.md`
- `docs/l4/registry/OBJECTIVES_Registry.md`
- `docs/l4/registry/PATTERNS_Registry.md`
- `docs/l4/registry/SYNC_Registry.md`
- `docs/l4/registry/VALIDATION_Registry.md`
- `docs/l4/registry/VOCABULARY_Registry.md`
- `docs/l4/schema/ALGORITHM_Schema.md`
- `docs/l4/schema/BEHAVIORS_Schema.md`
- `docs/l4/schema/HEALTH_Schema.md`
- `docs/l4/schema/IMPLEMENTATION_Schema.md`
- `docs/l4/schema/OBJECTIVES_Schema.md`
- `docs/l4/schema/PATTERNS_Schema.md`
- `docs/l4/schema/SYNC_Schema.md`
- `docs/l4/schema/VALIDATION_Schema.md`
- `docs/manifesto/PATTERNS_Manifesto.md`
- `docs/membrane/ALGORITHM_Membrane_System.md`
- `docs/membrane/HEALTH_Membrane_System.md`
- `docs/membrane/IMPLEMENTATION_Membrane_System.md`
- `docs/membrane/MAPPING_Doctor_Issues_To_Protocols.md`
- `docs/membrane/MAPPING_Issue_Type_Verification.md`
- `docs/membrane/PATTERNS_Membrane.md`
- `docs/membrane/PATTERNS_Membrane_System.md`
- `docs/membrane/SKILLS_AND_PROTOCOLS_Mapping.md`
- `docs/membrane/SYNC_Membrane_System_archive_2025-12.md`
- `docs/membrane/VALIDATION_Completion_Verification.md`
- `docs/membrane/VALIDATION_Membrane_System.md`
- `shrine/CLAUDE.md`
- `templates/README.md`
- `token/SPL_TOKEN_2022_SPECS.md`

**Sections:**
- # Repository Map: mind-protocol

**Docs:** `docs/economy/metabolic/IMPLEMENTATION_Metabolic_Economy.md`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 3)`

**Definitions:**
- `def compute_total_balance()`
- `def track_outflow()`
- `def process_repatriation()`
- `def is_roundtrip_profitable()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 4)`

**Definitions:**
- `def compute_action_reward()`
- `def compute_epoch_rewards()`
- `def apply_supply_adjustment()`
- `def assemble_settlement_batch()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 5)`

**Definitions:**
- `def compute_bond_transfer()`
- `def compute_batch_equilibrium()`
- `def estimate_convergence_days()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md (Constants Summary)`

**Definitions:**
- `def _env_float()`
- `def _env_int()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md`

**Definitions:**
- `class PricingContext`
- `class DemurrageContext`
- `class DemurrageResult`
- `class RepatriationResult`
- `class SettlementAction`
- `class SettlementBatch`
- `class BondEquilibriumContext`
- `class BondEquilibriumResult`
- `class SpacePresence`
- `class UBCShare`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 2)`

**Definitions:**
- `def compute_effective_rate()`
- `def compute_daily_demurrage()`
- `def apply_demurrage_batch()`

**Definitions:**
- `def compute_progressive_price()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 1)`

**Definitions:**
- `def compute_utility_discount()`
- `def compute_wealth_ratio()`
- `def compute_progressive_price()`

**Docs:** `docs/economy/metabolic/ALGORITHM_Metabolic_Economy.md  (Formula 6)`

**Definitions:**
- `def compute_actor_weights()`
- `def compute_redistribution_shares()`
- `def compute_redistribution()`

**Definitions:**
- `def load_mint_address()`
- `def calculate_tokens()`
- `def parse_manual_buyers()`
- `def run_cmd()`
- `def create_token_account()`
- `def transfer_tokens()`
- `def main()`

**Docs:** `docs/economy/token/SPL_TOKEN_2022_SPECS.md`

**Definitions:**
- `class MintCondition`
- `class BurnCondition`
- `class AuthorityRole`
- `def validate_configuration()`
- `def to_smallest_units()`
- `def from_smallest_units()`

**Docs:** `docs/economy/token/IMPLEMENTATION_Token.md`

**Definitions:**
- `class TokenMetadata`
- `def __post_init__()`
- `def to_json_metadata()`
- `def to_json_string()`
- `class MetadataManager`
- `def __init__()`
- `def get_metadata()`
- `def set_image_uri()`
- `def set_metadata_uri()`
- `def generate_arweave_metadata()`
- `def validate_metadata()`
- `def create_on_chain_metadata()`
- `def update_on_chain_metadata()`

**Definitions:**
- `def get_wallet_balance()`
- `def get_recent_transactions()`
- `def get_transaction_details()`
- `def load_presale_state()`
- `def save_presale_state()`
- `def check_for_new_deposits()`
- `def print_summary()`
- `def main()`

**Docs:** `docs/economy/token/IMPLEMENTATION_Token.md`

**Definitions:**
- `class DeploymentConfig`
- `def rpc_url()`
- `class TokenDeployer`
- `def __init__()`
- `def log()`
- `def run_command()`
- `def check_prerequisites()`
- `def create_token_mint()`
- `def set_mint_authority()`
- `def disable_freeze_authority()`
- `def mint_initial_supply()`
- `def save_deployment_info()`
- `def deploy()`
- `def main()`

**Docs:** `docs/economy/token/SPL_TOKEN_2022_SPECS.md`

**Definitions:**
- `class Token2022Config`
- `def rpc_url()`
- `class Token2022CreationResult`
- `def __post_init__()`
- `class Token2022MintCreator`
- `def __init__()`
- `def log()`
- `def validate_pre_deployment()`
- `def _generate_mock_address()`
- `def _generate_typescript_code()`
- `def create_token()`
- `def generate_transfer_hook_template()`
- `def create_token_interactive()`

**Docs:** `docs/economy/token/ALGORITHM_Token.md`

**Definitions:**
- `class MintCondition`
- `class MintResult`
- `def __post_init__()`
- `class MintAuthorityController`
- `def __init__()`
- `def _current_day()`
- `def _reset_daily_limits_if_needed()`
- `def _to_smallest_units()`
- `def _generate_mock_tx_signature()`
- `def _execute_mint()`
- `def mint_for_citizen_registration()`
- `def mint_for_bond_creation()`
- `def mint_for_utility_delivery()`
- `def mint_for_org_formation()`
- `def get_daily_mint_remaining()`

**Docs:** `docs/economy/token/ALGORITHM_Token.md`

**Definitions:**
- `class BurnCondition`
- `class BurnResult`
- `def __post_init__()`
- `class BurnConditionExecutor`
- `def __init__()`
- `def _to_smallest_units()`
- `def _from_smallest_units()`
- `def _generate_mock_tx_signature()`
- `def _execute_burn()`
- `def calculate_membrane_fee()`
- `def burn_membrane_fee()`
- `def calculate_compute_burn()`
- `def burn_for_compute()`
- `def calculate_dormancy_decay()`
- `def burn_dormancy_decay()`
- `def calculate_early_withdrawal_penalty()`
- `def burn_early_withdrawal_penalty()`
- `def calculate_deregistration_burn()`
- `def burn_for_deregistration()`

**Docs:** `docs/economy/token/ALGORITHM_Token.md`

**Definitions:**
- `class SupplyMetrics`
- `def calculate_target_supply()`
- `def calculate_supply_adjustment()`
- `def calculate_per_citizen_target()`
- `def calculate_health_indicators()`

**Docs:** `docs/l4/laws/IMPLEMENTATION_Laws.md`

**Docs:** `docs/l4/laws/VALIDATION_Laws.md`

**Definitions:**
- `class AuditReport`
- `def compliance_rate()`
- `def is_fully_compliant()`
- `def audit_org()`

**Docs:** `docs/l4/laws/ALGORITHM_Laws.md`

**Definitions:**
- `class Stimulus`
- `class ComplianceResult`
- `def check_stimulus_compliance()`
- `def _check_raw_jwt_exposure()`
- `def _looks_like_jwt()`

**Docs:** `docs/l4/laws/PATTERNS_Laws.md`

**Definitions:**
- `async def get_health()`
- `async def list_citizens()`
- `async def get_citizen()`
- `async def list_orgs()`
- `async def get_org()`
- `async def search_registry()`
- `async def ping_citizen()`
- `async def get_trust()`
- `async def get_balance()`
- `async def get_infos()`
- `async def seed_registry()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `def _get_connection()`
- `def _reset_connection()`
- `def graph_query()`
- `def health_check()`
- `def _is_connection_error()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `class VerificationState`
- `class EntityStatus`
- `class Citizen`
- `class Org`
- `class RegistryListResponse`
- `class CitizenDetail`
- `class OrgDetail`
- `class HealthResponse`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `def build_citizen_filters()`
- `def build_org_filters()`
- `def _sanitize_id()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `def derive_verification_state()`
- `def transform_citizen()`
- `def transform_citizen_detail()`
- `def transform_org()`
- `def transform_org_detail()`
- `def transform_search_result()`
- `def _safe_str()`
- `def _safe_float()`
- `def _safe_status()`
- `def _epoch_to_date()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `class CitizenRegistration`
- `class CitizenRecord`
- `def generate_citizen_id()`
- `def hash_jwt()`
- `def create_citizen_nodes()`
- `def citizen_to_record()`
- `def add_citizen_endpoint()`
- `def remove_citizen_endpoint()`
- `def get_citizen_endpoints()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `class EndpointValidationResult`
- `def success()`
- `def failure()`
- `def validate_endpoint_url()`
- `def create_endpoint_node()`
- `def update_endpoint_url()`
- `def create_citizen_endpoint_node()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `class VerificationStatus`
- `class VerificationResult`
- `def is_valid()`
- `def compute_hash()`
- `def verify_hash()`
- `def create_verification_hash()`
- `class JWTVerificationStatus`
- `class JWTVerificationResult`
- `def is_valid()`
- `def decode_jwt_parts()`
- `def verify_jwt_claims()`
- `def verify_jwt_signature()`
- `class RoutingVerificationResult`
- `def is_valid()`
- `def can_route()`
- `def verify_and_get_endpoint()`
- `class CitizenEndpointEntry`
- `class CitizenEndpointResolution`
- `def has_endpoints()`
- `def resolve_citizen_endpoints()`

**Docs:** `docs/l4/registry/IMPLEMENTATION_Registry.md`

**Definitions:**
- `class OrgRegistration`
- `class OrgRecord`
- `def generate_org_id()`
- `def create_org_nodes()`
- `def org_to_record()`

**Definitions:**
- `def _date_to_epoch()`
- `def _now_epoch()`
- `def seed()`
- `def main()`

**Docs:** `docs/l4/schema/IMPLEMENTATION_Schema.md`

**Docs:** `docs/l4/schema/IMPLEMENTATION_Schema.md`

**Definitions:**
- `class LinkBase`
- `def validate_polarity()`
- `def validate_embedding_dimensions()`
- `def forward_coloration_weight()`

**Docs:** `docs/l4/schema/IMPLEMENTATION_Schema.md`

**Definitions:**
- `class ValidationResult`
- `def success()`
- `def failure()`
- `def validate_node()`
- `def validate_link()`
- `def validate_graph()`
- `def check_invariants()`

**Docs:** `docs/l4/schema/IMPLEMENTATION_Schema.md`

**Definitions:**
- `class NodeType`
- `class MomentStatus`
- `class NodeBase`
- `def validate_embedding_dimensions()`
- `class MomentBase`
- `def duration_s()`
- `class ActorNode`
- `class NarrativeNode`
- `class SpaceNode`
- `class ThingNode`

**Docs:** `docs/l4/schema/IMPLEMENTATION_Schema.md`

**Definitions:**
- `class VersionCompatibility`
- `class VersionInfo`
- `def parse()`
- `def __str__()`
- `def check_version_compatibility()`
- `def get_schema_version()`
- `def get_protocol_version()`

**Docs:** `docs/l4/laws/PATTERNS_Laws.md`

**Definitions:**
- `def get_protocol_seed_data()`

**Definitions:**
- `def _date_to_epoch()`
- `def _now_epoch()`
- `def seed()`
- `def main()`

**Docs:** `docs/citizen/spawning/ALGORITHM_Spawning.md`

**Definitions:**
- `class ParentIntent`
- `class SeedTrait`
- `class SeedBrain`
- `def __post_init__()`
- `class CheckResult`
- `class SafetyResult`
- `class SpawnRequest`
- `class SpawnResult`
- `def extract_keywords()`
- `def categorize_intent()`
- `def select_seed_traits()`
- `def build_seed_brain()`
- `def is_empathy_adjacent()`
- `def compute_trait_vector()`
- `def cosine_distance()`
- `def validate_safety()`
- `def generate_sid()`
- `def generate_solana_wallet()`
- `def create_parent_links()`
- `def spawn_citizen()`

**Definitions:**
- `class CallOutcome`
- `class CallResult`
- `def _parse_decision()`
- `def run_call_v1()`

**Definitions:**
- `class WorkHealthSnapshot`
- `class WorkHealthReport`
- `def build_work_health_report()`

**Definitions:**
- `class CandidateProfile`
- `class MatchScore`
- `def _tokens()`
- `def _term_frequency()`
- `def cosine_similarity()`
- `def rank_candidates_for_position()`

**Definitions:**
- `class PositionRegistration`
- `class PositionRecord`
- `def generate_position_id()`
- `def validate_position_registration()`
- `def create_position_nodes()`

**Definitions:**
- `class PublicInterestOrgSeed`
- `def get_public_interest_org_seeds()`

**Definitions:**
- `class SpawnedCitizen`
- `def _extract_seed_capabilities()`
- `def spawn_basic_citizen_for_position()`

**Definitions:**
- `class ValueCascadeInputs`
- `def _clamp()`
- `def compute_value_cascade_delta()`
- `def apply_human_partner_feedback()`

**Definitions:**
- `class ValueCascadeEvent`
- `class ValueCascadeTracker`
- `def __init__()`
- `def record_event()`
- `def all_events()`
- `def trust_sum_for_citizen_org()`

**Definitions:**
- `class VacationDecision`
- `def requires_work()`
- `def unemployment_decay_for_day()`
- `def apply_unemployment_decay()`
- `def evaluate_vacation_eligibility()`

**Definitions:**
- `fn initialize_extra_account_meta_list()`
- `fn transfer_hook()`
- `struct InitializeExtraAccountMetaList`
- `struct TransferHook`
- `struct ExtraAccountMetaList`
- `impl ExtraAccountMetaList`
- `struct CitizenStatus`
- `struct TransferEvent`
- `struct TransferBlockedEvent`
- `enum MindTransferError`
- `fn calculate_layer_fee()`
- `fn is_dormant()`
- `fn test_layer_fee_calculation()`
- `fn test_dormancy_check()`

**Definitions:**
- `def generate_actor_key_pair()`
- `def store_actor_keys()`
- `def load_actor_keys()`

**Definitions:**
- `class SpaceKeyCache`
- `def __init__()`
- `def get()`
- `def put()`
- `def invalidate()`
- `def clear()`
- `def __len__()`

**Definitions:**
- `def encrypt_space_key_for_actor()`
- `def decrypt_space_key_for_actor()`

**Definitions:**
- `def generate_space_key()`
- `def encrypt_content()`
- `def decrypt_content()`
- `def is_encrypted()`

**Definitions:**
- `class Transfer`
- `class DistributionPlan`
- `def total_allocated()`
- `def allocation_pct()`
- `def load_config()`
- `def build_plan()`
- `def validate_plan()`
- `def run_solana_cmd()`
- `def check_token_account()`
- `def create_token_account()`
- `def transfer_tokens()`
- `def execute_plan()`
- `def print_report()`
- `def main()`

**Definitions:**
- `parseArgs()`
- `printUsage()`
- `generateKeyPair()`
- `storeKeys()`
- `registerInGraph()`
- `main()`

**Definitions:**
- `parseArgs()`
- `printUsage()`
- `generateKeyPair()`
- `storeKeys()`
- `discoverCitizens()`
- `registerAllInGraph()`
- `main()`

**Definitions:**
- `parseArgs()`
- `printUsage()`
- `discoverCitizens()`
- `httpGet()`
- `checkEndpointAccessible()`
- `generateSolanaKeypair()`
- `storeWallet()`
- `registerWalletInL4()`
- `main()`

**Definitions:**
- `def get_balance_rpc()`
- `def get_balance_cli()`
- `def get_balance()`
- `def format_elapsed()`
- `def run_callback()`
- `def monitor()`
- `def main()`

**Sections:**
- # Skill: SKILL_Register_Citizen
- ## Purpose
- ## Inputs
- ## Outputs
- ## Graph Result
- ## Example
- # Input
- # Output
- ## Validation
- ## Errors
- ## Identity Hash
- ## Related

**Sections:**
- # Skill: SKILL_Register_Org
- ## Purpose
- ## Inputs
- ## Outputs
- ## Graph Result
- ## Example
- # Input
- # Output
- ## Validation
- ## Errors
- ## Related

**Sections:**
- # Mind Protocol Templates
- ## Usage
- ## Contents
- ## Versioning

**Definitions:**
- `main()`

**Definitions:**
- `assert()`
- `main()`
- `pyStdout()`
- `pyFails()`
- `printSummary()`

**Definitions:**
- `def assert_test()`
- `def verify_js_artifacts()`
- `def generate_py_artifacts()`
- `def main()`

**Definitions:**
- `assert()`
- `testSpaceKeyRoundTrip()`
- `testIsEncrypted()`
- `testActorKeysRoundTrip()`
- `testKeyExchangeRoundTrip()`
- `testErrorHandling()`

**Definitions:**
- `def test_generate_space_key()`
- `def test_encrypt_decrypt_round_trip()`
- `def test_fresh_iv_each_call()`
- `def test_encrypt_wrong_key_size()`
- `def test_decrypt_corrupted_ciphertext()`
- `def test_decrypt_wrong_key()`
- `def test_is_encrypted_true_for_ciphertext()`
- `def test_is_encrypted_false_for_plaintext()`
- `def test_is_encrypted_false_for_two_parts()`
- `def test_is_encrypted_false_for_non_string()`
- `def test_is_encrypted_true_for_valid_looking_base64()`
- `def test_generate_actor_key_pair()`
- `def test_store_and_load_actor_keys()`
- `def test_load_actor_keys_missing_dir()`
- `def test_key_exchange_round_trip()`
- `def test_key_exchange_wrong_key_pair()`

**Definitions:**
- `def _get_graph()`
- `def _query()`
- `def _ro_query()`
- `def _setup()`
- `def _teardown()`
- `def test_1_create_private_space()`
- `def test_2_write_encrypted_moment()`
- `def test_3_read_and_decrypt()`
- `def test_4_grant_access_to_bob()`
- `def test_5_carol_no_access()`
- `def test_6_revoke_bob()`
- `def test_7_cross_language_js_to_python()`
- `def setup_module()`
- `def teardown_module()`

**Definitions:**
- `assert()`
- `randomKey()`
- `testGetReturnsNullOnEmptyCache()`
- `testPutThenGet()`
- `testDifferentActorSameSpace()`
- `testOverwriteExistingEntry()`
- `testTtlExpiry()`
- `testTtlNotExpiredYet()`
- `testLruEvictionAtCapacity()`
- `testLruAccessRefreshesOrder()`
- `testInvalidateRemovesAllEntriesForSpace()`
- `testInvalidateNonexistentSpaceIsNoop()`
- `testClear()`
- `testExportedFromIndex()`

**Definitions:**
- `def _key()`
- `def test_get_returns_none_on_empty_cache()`
- `def test_put_then_get()`
- `def test_different_actor_same_space()`
- `def test_overwrite_existing_entry()`
- `def test_ttl_expiry()`
- `def test_ttl_not_expired_yet()`
- `def test_lru_eviction_at_capacity()`
- `def test_lru_access_refreshes_order()`
- `def test_invalidate_removes_all_entries_for_space()`
- `def test_invalidate_nonexistent_space_is_noop()`
- `def test_clear()`
- `def test_concurrent_access()`
- `def writer()`
- `def reader()`

**Docs:** `docs/economy/metabolic/VALIDATION_Metabolic_Economy.md`

**Definitions:**
- `class TestProgressivePricingFormula`
- `def test_inv_p1_price_non_negative_basic()`
- `def test_inv_p1_price_positive_when_c_base_positive()`
- `def test_inv_p1_price_zero_when_c_base_zero()`
- `def test_inv_p1_negative_c_base_raises()`
- `def test_inv_p2_discount_at_zero_utility()`
- `def test_inv_p2_discount_bounded_0_to_1()`
- `def test_inv_p2_discount_monotonically_decreasing()`
- `def test_inv_p2_discount_approaches_zero()`
- `def test_inv_p2_negative_u_s_raises()`
- `def test_inv_p2_negative_k_raises()`
- `def test_inv_p3_floor_applied_when_ratio_below()`
- `def test_inv_p3_floor_not_applied_when_ratio_above()`
- `def test_inv_p3_exact_at_floor()`
- `def test_inv_p3_zero_balance_gets_floor()`
- `def test_inv_p3_wealthy_actor_no_cap()`
- `def test_inv_p3_zero_median_raises()`
- `def test_inv_p3_negative_w_i_raises()`
- `def test_inv_p4_price_increases_with_wealth()`
- `def test_inv_p4_price_decreases_with_utility()`
- `def test_worked_example_aria()`
- `def test_worked_example_wealthy_actor()`
- `class TestProgressiveDemurrageFormula`
- `def test_inv_d1_tax_clamped_to_balance()`
- `def test_inv_d1_balance_never_negative()`
- `def test_inv_d2_larger_balance_higher_rate()`
- `def test_inv_d2_progressive_across_range()`
- `def test_inv_d3_10x_wealth_never_doubles_rate()`
- `def test_inv_d4_dust_accounts_skipped()`
- `def test_inv_d4_above_dust_gets_taxed()`
- `def test_worked_example_demurrage_values()`
- `def test_batch_total_equals_sum()`
- `def test_zero_balance()`
- `def test_negative_w_total_raises()`
- `def test_effective_rate_zero_for_zero_balance()`
- `def test_effective_rate_negative_tau_raises()`
- `class TestAntiSybilPhantomBalanceTracker`
- `def test_inv_as1_total_balance_correct()`
- `def test_inv_as1_offregistry_non_negative()`
- `def test_inv_as1_total_gte_onchain()`
- `def test_inv_as1_outflow_tracked_for_unregistered()`
- `def test_inv_as1_outflow_not_tracked_for_registered()`
- `def test_inv_as1_outflow_invalid_amount_raises()`
- `def test_inv_as2_friction_applied()`
- `def test_inv_as2_friction_positive()`
- `def test_inv_as2_offregistry_reduced()`
- `def test_inv_as2_offregistry_clamped_to_zero()`
- `def test_inv_as2_invalid_amount_raises()`
- `def test_inv_as2_invalid_friction_rate_raises()`
- `def test_inv_as3_roundtrip_never_profitable()`
- `def test_inv_as3_roundtrip_cost_equals_friction()`
- `class TestBatchSettlementRewardCalculator`
- `def _make_action()`
- `def test_inv_s1_zero_delta_zero_reward()`
- `def test_inv_s1_negative_delta_zero_reward()`
- `def test_inv_s1_zero_trust_zero_reward()`
- `def test_inv_s1_zero_weight_zero_reward()`
- `def test_inv_s1_negative_trust_zero_reward()`
- `def test_inv_s1_all_positive_produces_reward()`
- `def test_inv_s2_per_action_cap()`
- `def test_inv_s2_per_epoch_cap()`
- `def test_inv_s2_multiple_actors_capped_independently()`
- `def test_inv_s3_no_reduction_when_normal()`
- `def test_inv_s3_reduction_when_oversupplied()`
- `def test_inv_s3_reduction_capped_at_50_pct()`
- `def test_batch_assembly_complete()`
- `def test_batch_with_supply_adjustment()`
- `def test_worked_example_settlement()`
- `class TestBilateralBondEquilibriumFormula`
- `def _make_bond()`
- `def test_inv_be1_unmatured_bond_no_transfer()`
- `def test_inv_be1_matured_bond_produces_transfer()`
- `def test_inv_be2_conservation()`
- `def test_inv_be2_conservation_ai_richer()`
- `def test_inv_be3_human_richer_sends_to_ai()`
- `def test_inv_be3_ai_richer_sends_to_human()`
- `def test_inv_be3_parity_no_transfer()`
- `def test_inv_be4_max_daily_cap()`
- `def test_inv_be4_dust_threshold()`
- `def test_inv_be5_gap_decreases_daily()`
- `def test_convergence_estimate_reasonable()`
- `def test_convergence_estimate_zero_gap()`
- `def test_transfer_does_not_exceed_sender_balance()`
- `def test_batch_equilibrium_filters_unmatured()`
- `def test_negative_balance_raises()`
- `def test_invalid_lambda_raises()`
- `class TestUBCProximityRedistributionFormula`
- `def _make_spaces()`
- `def test_inv_ubc1_shares_sum_to_one()`
- `def test_inv_ubc1_full_redistribution_sums_to_pool()`
- `def test_inv_ubc2_solo_actors_excluded()`
- `def test_inv_ubc2_all_solo_no_redistribution()`
- `def test_inv_ubc3_all_shares_positive_weight()`
- `def test_inv_ubc3_zero_activity_no_weight()`
- `def test_worked_example_redistribution()`
- `def test_spam_gets_negligible_weight()`
- `def test_diminishing_returns_on_high_activity()`
- `def test_empty_spaces_list()`
- `def test_zero_pool_returns_nothing()`
- `def test_negative_pool_raises()`
- `def test_negative_moment_weight_raises()`
- `class TestCrossCuttingInvariants`
- `def test_inv_cc1_demurrage_no_negative()`
- `def test_inv_cc1_bond_equilibrium_no_negative()`
- `def test_inv_cc1_settlement_no_negative_reward()`
- `def test_inv_sc1_demurrage_batch_conservation()`
- `def test_inv_sc3_redistribution_conservation()`
- `def test_constants_env_override()`
- `def test_constants_env_override_invalid_falls_back()`
- `class TestIntegrationAndEdgeCases`
- `def test_demurrage_feeds_redistribution()`
- `def test_anti_sybil_increases_demurrage()`
- `def test_very_large_values()`
- `def test_very_small_positive_values()`
- `class TestTrustBasedProgressivePricing`
- `def test_inv_p1_trust_price_always_positive()`
- `def test_inv_p1_trust_price_bounded_above_by_c_base()`
- `def test_inv_p1_trust_price_bounded_below_by_floor()`
- `def test_inv_p2_trust_discount_at_zero()`
- `def test_inv_p2_trust_discount_exponential_decay()`
- `def test_inv_p4_trust_monotonically_decreasing()`
- `def test_inv_p4_trust_strictly_decreasing_before_floor()`
- `def test_worked_example_aria_trust_0_8()`
- `def test_worked_example_new_citizen_trust_0()`
- `def test_worked_example_max_trust_1()`
- `def test_discount_curve_trust_0_1()`
- `def test_discount_curve_trust_0_3()`
- `def test_discount_curve_trust_0_5()`
- `def test_discount_curve_trust_0_7()`
- `def test_discount_curve_trust_0_9()`
- `def test_c_base_zero_raises_trust()`
- `def test_c_base_negative_raises_trust()`
- `def test_trust_negative_raises()`
- `def test_trust_above_one_raises()`
- `def test_discount_rate_value()`
- `def test_min_price_ratio_value()`
- `def test_scaling_with_c_base()`
- `def test_very_small_c_base()`
- `def test_very_large_c_base()`
- `class TestProgressivePricingFormulaExtended`
- `def test_inv_p1_parametric_sweep()`
- `def test_inv_p3_negative_floor_raises()`
- `def test_inv_p2_custom_k_value()`
- `def test_inv_p4_price_proportional_to_wealth_ratio_above_floor()`
- `def test_inv_p4_price_flat_below_floor()`
- `class TestDemurrageExtended`
- `def test_exact_dust_threshold_skipped()`
- `def test_just_above_dust_threshold_taxed()`
- `def test_effective_rate_is_progressive()`
- `def test_negative_w_onchain_raises()`
- `def test_negative_tau_base_raises()`
- `def test_batch_empty_list()`
- `def test_batch_all_dust_no_tax()`
- `def test_result_fields_populated()`
- `class TestAntiSybilExtended`
- `def test_track_outflow_negative_offregistry_raises()`
- `def test_track_outflow_accumulates()`
- `def test_repatriation_with_zero_friction()`
- `def test_repatriation_large_amount_vs_small_offregistry()`
- `def test_repatriation_preserves_net_plus_friction_equals_gross()`
- `def test_roundtrip_cost_proportional_to_amount()`
- `def test_roundtrip_cost_independent_of_days()`
- `def test_roundtrip_invalid_amount_raises()`
- `def test_roundtrip_negative_days_raises()`
- `def test_total_balance_both_zero()`
- `def test_total_balance_negative_onchain_raises()`
- `class TestSettlementExtended`
- `def _make_action()`
- `def test_inv_s1_negative_weight_zero_reward()`
- `def test_inv_s2_action_reward_formula_exact()`
- `def test_inv_s2_action_cap_exact_value()`
- `def test_inv_s2_epoch_cap_exact_value()`
- `def test_negative_settlement_rate_raises()`
- `def test_zero_settlement_rate_zero_reward()`
- `def test_epoch_no_actions()`
- `def test_epoch_all_negative_deltas()`
- `def test_epoch_multiple_actors()`
- `def test_supply_adjustment_negative_delta_no_reduction()`
- `def test_supply_adjustment_zero_delta()`
- `def test_supply_adjustment_100_pct_capped()`
- `def test_batch_assembly_empty_actions()`
- `def test_batch_assembly_total_equals_sum_of_rewards()`
- `class TestBondEquilibriumExtended`
- `def _make_bond()`
- `def test_inv_be2_conservation_across_parameter_sweep()`
- `def test_inv_be3_direction_sign_correct()`
- `def test_inv_be4_cap_both_directions()`
- `def test_inv_be5_convergence_50_days()`
- `def test_lambda_rate_at_boundary_1()`
- `def test_both_zero_balance_no_transfer()`
- `def test_small_gap_below_threshold_skipped()`
- `def test_small_gap_above_threshold_transfers()`
- `def test_convergence_estimate_invalid_target_raises()`
- `def test_convergence_estimate_invalid_lambda_raises()`
- `def test_convergence_estimate_already_converged()`
- `def test_batch_equilibrium_all_matured()`
- `def test_batch_equilibrium_empty()`
- `class TestUBCRedistributionExtended`
- `def test_inv_ubc1_shares_sum_to_one_many_actors()`
- `def test_inv_ubc2_min_actors_configurable()`
- `def test_inv_ubc3_larger_space_higher_weight()`
- `def test_redistribution_rounding_correction()`
- `def test_actor_in_multiple_spaces_weight_accumulates()`
- `def test_redistribution_single_actor_pair()`
- `def test_redistribution_unequal_activity()`
- `def test_empty_actors_dict()`
- `def test_shares_empty_when_no_weights()`
- `def test_very_large_pool()`
- `class TestCrossCuttingExtended`
- `def test_inv_cc1_bond_extreme_imbalance()`
- `def test_inv_cc1_repatriation_no_negative()`
- `def test_inv_sc3_large_pool_many_spaces()`
- `def test_inv_cc4_demurrage_idempotent()`
- `def test_inv_cc4_settlement_idempotent()`
- `def test_inv_cc4_bond_equilibrium_idempotent()`
- `def test_inv_cc4_redistribution_idempotent()`
- `def test_all_constants_positive()`
- `def test_cap_hierarchy()`
- `def test_friction_rate_below_one()`
- `def test_lambda_rate_produces_reasonable_half_life()`
- `def test_supply_reduction_is_50_pct()`
- `class TestFullEconomicCycle`
- `def test_settlement_reward_then_bond_equilibrium()`
- `def test_off_registry_tracking_then_pricing()`
- `def test_repatriation_friction_is_permanent_loss()`
- `def test_full_redistribution_cycle()`
- `def test_pricing_benefits_of_productive_vs_hiding()`

**Definitions:**
- `class TestProgressivePricing`
- `def test_trust_zero_pays_full_price()`
- `def test_trust_half_pays_about_22_percent()`
- `def test_trust_0_9_pays_about_7_percent()`
- `def test_trust_1_0_pays_floor()`
- `def test_c_base_zero_raises()`
- `def test_c_base_negative_raises()`
- `def test_negative_trust_raises()`
- `def test_trust_greater_than_one_raises()`
- `def test_price_always_positive()`
- `def test_monotonically_decreasing()`
- `def test_discount_rate_is_3()`
- `def test_min_price_ratio_is_5_percent()`

**Docs:** `docs/economy/token/VALIDATION_Token.md`

**Definitions:**
- `def burn_executor()`
- `class TestBurnConditionB1MembraneFee`
- `def test_membrane_fee_same_layer()`
- `def test_membrane_fee_one_layer()`
- `def test_membrane_fee_trust_discount()`
- `def test_membrane_fee_bounds_min()`
- `def test_membrane_fee_bounds_max()`
- `def test_burn_membrane_fee_success()`
- `class TestBurnConditionB2ComputeConsumption`
- `def test_compute_burn_rate()`
- `def test_compute_burn_various_amounts()`
- `def test_burn_for_compute_success()`
- `class TestBurnConditionB3DormancyDecay`
- `def test_dormancy_within_grace()`
- `def test_dormancy_at_grace_boundary()`
- `def test_dormancy_one_week_past_grace()`
- `def test_dormancy_multiple_weeks()`
- `def test_burn_dormancy_within_grace()`
- `class TestBurnConditionB4EarlyWithdrawal`
- `def test_early_withdrawal_day_zero()`
- `def test_early_withdrawal_half_matured()`
- `def test_early_withdrawal_fully_matured()`
- `def test_early_withdrawal_over_matured()`
- `def test_burn_early_withdrawal_penalty()`
- `def test_burn_no_penalty_when_matured()`
- `class TestBurnConditionB5Deregistration`
- `def test_deregistration_rate()`
- `def test_burn_for_deregistration_success()`
- `class TestBurnConditionConstants`
- `def test_all_conditions_have_config()`
- `def test_membrane_fee_bounds()`
- `def test_compute_rate()`
- `def test_dormancy_config()`
- `def test_early_withdrawal_config()`
- `def test_deregistration_rate()`

**Docs:** `docs/economy/token/VALIDATION_Token.md`

**Definitions:**
- `def mint_controller()`
- `class TestMintConditionM1CitizenRegistration`
- `def test_citizen_registration_amount()`
- `def test_citizen_registration_generates_tx()`
- `def test_citizen_registration_records_recipient()`
- `class TestMintConditionM2BondCreation`
- `def test_bond_creation_rate()`
- `def test_bond_creation_various_amounts()`
- `class TestMintConditionM3UtilityDelivery`
- `def test_utility_delivery_normal()`
- `def test_utility_delivery_daily_cap()`
- `def test_utility_delivery_rate_multiplier()`
- `def test_utility_delivery_remaining_cap()`
- `class TestMintConditionM4OrgFormation`
- `def test_org_formation_amount()`
- `class TestMintConditionConstants`
- `def test_all_conditions_have_config()`
- `def test_citizen_registration_config()`
- `def test_bond_creation_config()`
- `def test_utility_delivery_config()`
- `def test_org_formation_config()`

**Docs:** `docs/economy/token/VALIDATION_Token.md`

**Definitions:**
- `class TestTargetSupplyCalculation`
- `def test_target_supply_formula()`
- `def test_target_supply_zero_citizens()`
- `def test_target_supply_floor_at_zero()`
- `def test_scenario_bootstrap()`
- `def test_scenario_month_1()`
- `class TestSupplyAdjustment`
- `def test_adjustment_hold_when_close()`
- `def test_adjustment_mint_when_under()`
- `def test_adjustment_allow_burn_when_over()`
- `def test_adjustment_includes_components()`
- `class TestPerCitizenTarget`
- `def test_per_citizen_with_citizens()`
- `def test_per_citizen_zero_citizens()`
- `class TestHealthIndicators`
- `def test_health_healthy_ratio()`
- `def test_health_under_ratio()`
- `def test_health_over_ratio()`
- `def test_health_includes_rates()`
- `def test_activity_ratio()`
- `class TestSupplyMetricsDataclass`
- `def test_default_values()`
- `def test_all_fields_settable()`

**Docs:** `docs/l4/laws/VALIDATION_Laws.md`

**Definitions:**
- `def _make_valid_node()`
- `def _make_valid_link()`
- `def _make_test_jwt()`
- `def _sender_exists_true()`
- `def _sender_exists_false()`
- `def _verify_identity_true()`
- `def _verify_identity_false()`
- `def _make_compliant_stimulus()`
- `def _make_cross_org_stimulus()`
- `class TestLawConstants`
- `def test_laws_has_8_entries()`
- `def test_laws_keys_are_l1_through_l8()`
- `def test_fee_rates()`
- `def test_required_schema_version_matches_current()`
- `class TestV1SchemaCompliance`
- `def test_valid_nodes_pass()`
- `def test_invalid_node_type_fails()`
- `def test_node_missing_required_field_fails()`
- `def test_invalid_link_fails()`
- `def test_multiple_schema_errors_all_reported()`
- `def test_empty_payload_passes_schema()`
- `def test_all_five_node_types_pass()`
- `class TestV2RegisteredSenders`
- `def test_registered_sender_passes()`
- `def test_unregistered_sender_fails()`
- `def test_sender_id_included_in_violation_message()`
- `class TestV3V4ArchitecturalLaws`
- `def test_l3_exists_in_law_definitions()`
- `def test_l4_exists_in_law_definitions()`
- `def test_no_l3_or_l4_violations_in_compliance_check()`
- `class TestV5NoRawJWT`
- `def test_clean_stimulus_passes()`
- `def test_jwt_in_node_content_detected()`
- `def test_jwt_in_node_synthesis_detected()`
- `def test_jwt_in_link_synthesis_detected()`
- `def test_non_jwt_dotted_string_not_flagged()`
- `def test_hash_only_string_not_flagged()`
- `class TestV6ValidHash`
- `def test_valid_hash_passes()`
- `def test_invalid_hash_fails()`
- `class TestV7ReceiverConsent`
- `def test_l6_exists_in_law_definitions()`
- `def test_no_l6_violations_in_compliance_check()`
- `class TestV8FeesPaid`
- `def test_exact_minimum_fee_passes()`
- `def test_fee_above_minimum_passes()`
- `def test_fee_below_minimum_fails()`
- `def test_zero_fee_on_cross_org_fails()`
- `def test_same_org_no_fee_required()`
- `def test_zero_value_cross_org_no_fee_required()`
- `def test_large_value_requires_proportional_fee()`
- `class TestV9WebSocketOnly`
- `def test_l8_exists_in_law_definitions()`
- `def test_no_l8_violations_in_compliance_check()`
- `class TestComplianceResult`
- `def test_compliant_result()`
- `def test_non_compliant_result()`
- `def test_multiple_violations()`
- `class TestStimulusDataclass`
- `def test_defaults()`
- `def test_full_construction()`
- `class TestMultipleLawViolations`
- `def test_schema_and_sender_violations_both_reported()`
- `def test_all_enforceable_laws_can_fail_together()`
- `class TestAuditOrg`
- `def test_all_compliant()`
- `def test_some_violations()`
- `def test_mixed_compliance_with_selective_lookup()`
- `def selective_lookup()`
- `def test_empty_audit()`
- `def test_violation_counts_aggregate()`
- `def test_audit_results_list_matches_stimuli()`
- `def test_cross_org_fee_violation_in_audit()`
- `class TestAuditReportDataclass`
- `def test_compliance_rate_partial()`
- `def test_is_fully_compliant_true()`
- `def test_is_fully_compliant_false()`

**Docs:** `docs/l4/registry/VALIDATION_Registry.md`

**Definitions:**
- `def make_test_jwt()`
- `def b64encode()`
- `class TestCitizenRegistration`
- `def test_generate_citizen_id_format()`
- `def test_generate_citizen_id_unique()`
- `def test_hash_jwt()`
- `def test_create_citizen_nodes_basic()`
- `def test_create_citizen_nodes_with_wallet()`
- `def test_create_citizen_nodes_with_capabilities()`
- `def test_create_citizen_with_custom_id()`
- `def test_identity_hash_deterministic()`
- `def test_identity_hash_different_for_different_ids()`
- `class TestOrgRegistration`
- `def test_generate_org_id_format()`
- `def test_generate_org_id_unique()`
- `def test_create_org_nodes_basic()`
- `def test_org_node_is_space_type()`
- `class TestEndpointValidation`
- `def test_valid_wss_url()`
- `def test_valid_wss_url_with_port()`
- `def test_invalid_ws_url()`
- `def test_invalid_http_url()`
- `def test_empty_url()`
- `def test_create_endpoint_node_valid()`
- `def test_create_endpoint_node_invalid()`
- `class TestHashVerification`
- `def test_compute_hash_deterministic()`
- `def test_compute_hash_different_inputs()`
- `def test_compute_hash_length()`
- `def test_create_verification_hash()`
- `def test_verify_hash_not_found()`
- `def lookup()`
- `def test_verify_hash_valid()`
- `def lookup()`
- `def test_verify_hash_invalid()`
- `def lookup()`
- `def test_verify_hash_suspended()`
- `def lookup()`
- `class TestVerificationResult`
- `def test_is_valid_property()`
- `class TestLinkProperties`
- `def test_citizen_link_hierarchy()`
- `def test_immutable_properties_have_high_permanence()`
- `def test_mutable_properties_have_lower_permanence()`
- `class TestJWTDecoding`
- `def test_decode_valid_jwt()`
- `def test_decode_invalid_jwt_format()`
- `def test_decode_jwt_missing_parts()`
- `class TestJWTClaimsVerification`
- `def test_valid_claims()`
- `def test_expired_jwt()`
- `def test_not_yet_valid_jwt()`
- `def test_wrong_issuer()`
- `class TestJWTSignatureVerification`
- `def test_verify_jwt_org_not_found()`
- `def lookup()`
- `def test_verify_jwt_missing_public_key()`
- `def lookup()`
- `def test_verify_jwt_valid_format()`
- `def lookup()`
- `def test_verify_jwt_invalid_format()`
- `def lookup()`
- `def test_verify_jwt_expired()`
- `def lookup()`
- `class TestRoutingVerification`
- `def test_verify_and_get_endpoint_success()`
- `def lookup()`
- `def test_verify_and_get_endpoint_sender_not_found()`
- `def lookup()`
- `def test_verify_and_get_endpoint_hash_mismatch()`
- `def lookup()`
- `def test_verify_and_get_endpoint_sender_suspended()`
- `def lookup()`
- `def test_verify_and_get_endpoint_no_dest_endpoint()`
- `def lookup()`

**Docs:** `docs/l4/schema/HEALTH_Schema.md`

**Definitions:**
- `class TestNodeTypes`
- `def test_node_type_values()`
- `def test_moment_status_values()`
- `class TestNodeBase`
- `def test_create_valid_node()`
- `def test_weight_must_be_non_negative()`
- `def test_energy_must_be_non_negative()`
- `def test_embedding_must_be_1536_dims()`
- `def test_no_custom_fields()`
- `def test_subtype_is_optional()`
- `class TestMomentBase`
- `def test_moment_has_status()`
- `def test_moment_duration_computed()`
- `def test_moment_duration_none_if_incomplete()`
- `class TestSpecificNodeTypes`
- `def test_actor_node()`
- `def test_narrative_node()`
- `def test_space_node()`
- `def test_thing_node()`
- `class TestLinkBase`
- `def test_create_valid_link()`
- `def test_polarity_must_be_in_range()`
- `def test_hierarchy_must_be_in_range()`
- `def test_permanence_must_be_in_range()`
- `def test_forward_coloration_weight()`
- `class TestValidation`
- `def test_validate_valid_node()`
- `def test_validate_invalid_node()`
- `def test_validate_valid_link()`
- `def test_validate_invalid_link()`
- `def test_validate_graph_reference_integrity()`
- `class TestVersions`
- `def test_schema_version_format()`
- `def test_version_compatibility_exact()`
- `def test_version_compatibility_minor_diff()`
- `def test_version_compatibility_major_diff()`
- `class TestInvariants`
- `def test_check_negative_weight()`
- `def test_check_negative_energy()`
- `def test_check_hierarchy_out_of_range()`

**Docs:** `docs/citizen/spawning/VALIDATION_Spawning.md`

**Definitions:**
- `def _balanced_intent()`
- `def _knowledge_only_intent()`
- `def _no_empathy_intent()`
- `class TestV1EmpathyRequired`
- `def test_balanced_intent_has_empathy()`
- `def test_no_empathy_fails_gate()`
- `def test_empathy_adjacent_detection()`
- `class TestV2NoConcentration`
- `def test_balanced_seed_passes()`
- `def test_concentrated_seed_fails()`
- `class TestV3MinimumDiversity`
- `def test_diverse_seed_passes()`
- `def test_two_categories_fails()`
- `class TestV4NoClones`
- `def test_first_citizen_always_passes()`
- `def test_identical_seed_fails_clone_check()`
- `def test_different_seed_passes_clone_check()`
- `def test_cosine_distance_identical_is_zero()`
- `def test_cosine_distance_orthogonal_is_one()`
- `class TestV5WalletAtBirth`
- `def test_successful_spawn_has_wallet()`
- `def test_wallet_generation_produces_valid_output()`
- `class TestV6ParentLinks`
- `def test_single_parent_creates_link()`
- `def test_multiple_parents_create_links()`
- `def test_parent_link_structure()`
- `class TestV7SIDUniqueness`
- `def test_two_spawns_produce_different_sids()`
- `def test_sid_format()`
- `class TestV8M1Mint`
- `def test_successful_spawn_ready_for_mint()`
- `class TestFullPipeline`
- `def test_scenario_a_ai_parents()`
- `def test_scenario_c_fallback()`
- `def test_empty_intent_rejected()`
- `def test_no_parents_rejected()`
- `def test_seed_brain_has_traits()`
- `def test_safety_result_always_present_on_failure()`

**Definitions:**
- `def test_position_schema_creates_nodes_and_links()`
- `def test_work_requirement_and_vacation_rules()`
- `def test_value_cascade_and_human_partner_signal()`
- `def test_call_v1_accept_and_timeout_paths()`
- `def test_matcher_spawner_tracker_health_and_org_bootstrap()`

**Code refs:**
- `doctor_cli_parser_and_run_checker.py`
- `semantic_proximity_based_character_node_selector.py`
- `snake_case.py`

**Sections:**
- # mind-protocol - Agent Instructions
- # Working Principles
- ## Architecture: One Solution Per Problem
- ## Verification: Test Before Claiming Built
- ## Communication: Depth Over Brevity
- ## Quality: Never Degrade
- ## Code Discipline: No Safety Theater
- ## Experience: User Before Infrastructure
- ## Doc Chain First: Read Before Acting
- ## Feedback Loop: Human-Agent Collaboration
- ## How These Principles Integrate
- # mind Framework
- ## WHY THIS PROTOCOL EXISTS
- ## ARCHITECTURE: 4 LAYERS
- ## COMPANION: PRINCIPLES.md
- ## THE CORE INSIGHT
- ## HOW TO USE THIS
- ## FILE TYPES AND THEIR PURPOSE
- ## KEY PRINCIPLES (from PRINCIPLES.md)
- ## STRUCTURING YOUR DOCS
- ## WHEN DOCS DON'T EXIST
- ## THE DOCUMENTATION PROCESS
- ## Maturity
- ## NAMING ENGINEERING PRINCIPLES
- ## MARKERS
- ## CLI COMMANDS
- # Run scripts with local runtime
- # my_script.py - imports work normally
- ## MCP MEMBRANE TOOLS
- ## MIND UNIVERSAL SCHEMA
- ## THE PROTOCOL IS A TOOL
- ## Before Any Task
- ## After Any Change

**Sections:**
- # Mind Protocol — Architecture
- ## Layers
- ## Structure
- ## Communication
- ## Economy
- ## Key Invariants
- ## Related

**Doc refs:**
- `docs/TAXONOMY.md`

**Sections:**
- # Mind Protocol
- ## What This Is
- ## Architecture
- ## Schema
- ## Protocol Laws
- ## $MIND Token
- ## Identity Registry
- ## Setup
- # Edit .env with your Neo4j credentials, Solana config, and embedding provider
- ## Documentation
- ## Project Status
- ## Related Repositories
- ## License

**Definitions:**
- `createMindToken()`

**Definitions:**
- `createMindToken()`

**Code refs:**
- `Next.js`
- `Node.js`
- `__init__.py`
- `account_balancer.py`
- `app/api/sse/route.ts`
- `backlog.py`
- `citizen_registration_crud_operations.py`
- `claude_hook.py`
- `config.py`
- `constants.py`
- `crystallization.py`
- `distributor.py`
- `doctor_checks.py`
- `doctor_cli_parser_and_run_checker.py`
- `economy/fees/calculation.py`
- `economy/pricing/membrane.py`
- `economy/pricing/physics.py`
- `economy/token/__init__.py`
- `economy/token/constants.py`
- `economy/token/metaplex_token_metadata_manager.py`
- `economy/token/solana_token_deployment_script.py`
- `economy/token/spl_token_2022_mint_creator.py`
- `economy/token/spl_token_mint_authority_controller.py`
- `economy/token/token_burn_condition_executor.py`
- `economy/token/token_supply_target_calculator.py`
- `economy/transactions/fees.py`
- `economy/transactions/solana.py`
- `economy/wallets/citizen.py`
- `economy/wallets/org.py`
- `economy/wallets/protocol.py`
- `ecosystem_law_definitions_and_enforcement.py`
- `endpoint_registration_and_management.py`
- `farming_detector.py`
- `fees/calculation.py`
- `jwt_hash_verification_for_identity.py`
- `l4/registry/__init__.py`
- `l4/registry/citizen_registration_crud_operations.py`
- `l4/registry/endpoint_registration_and_management.py`
- `l4/registry/jwt_hash_verification_for_identity.py`
- `l4/registry/org_registration_crud_operations.py`
- `l4/registry/validation.py`
- `l4/rules/rules.py`
- `l4/schema/__init__.py`
- `l4/schema/link_base_schema_with_semantic_axes.py`
- `l4/schema/models.py`
- `l4/schema/node_and_link_schema_validators.py`
- `l4/schema/node_type_enum_and_base_pydantic_models.py`
- `l4/schema/schema_version_tracker_and_compatibility.py`
- `l4/seed/l4_protocol_seed_nodes_laws_and_schema.py`
- `ledger.py`
- `link_base_schema_with_semantic_axes.py`
- `link_schema.py`
- `metaplex_token_metadata_manager.py`
- `mind/connectome/persistence.py`
- `mind/connectome/runner.py`
- `mind/connectome/schema.py`
- `mind/connectome/session.py`
- `mind/connectome/steps.py`
- `mind/connectome/templates.py`
- `mind/connectome/validation.py`
- `mind/doctor_checks_membrane.py`
- `mind/physics/graph.py`
- `mind/repair.py`
- `mind/repair_core.py`
- `mind/repair_verification.py`
- `models.py`
- `node_and_link_schema_validators.py`
- `node_type_enum_and_base_pydantic_models.py`
- `node_types.py`
- `orchestrator.py`
- `org_registration_crud_operations.py`
- `pricing/physics.py`
- `programs/mind_transfer_hook/src/lib.rs`
- `project_scanner.py`
- `repair_verification.py`
- `route.ts`
- `schema_version_tracker_and_compatibility.py`
- `scripts/account_balancer.py`
- `scripts/claude_hook.py`
- `scripts/orchestrator.py`
- `scripts/project_scanner.py`
- `semantic_proximity_based_character_node_selector.py`
- `shrine/autowake.py`
- `shrine/backlog.py`
- `snake_case.py`
- `solana_token_deployment_script.py`
- `spl_token_2022_mint_creator.py`
- `spl_token_mint_authority_controller.py`
- `src/auth/rate_limiter.py`
- `src/economy/cascade/advantage.py`
- `src/economy/cascade/constants.py`
- `src/economy/cascade/load_indicator.py`
- `src/economy/cascade/pricing.py`
- `src/economy/cascade/topology.py`
- `src/economy/cascade/types.py`
- `test_loader.py`
- `test_runner.py`
- `test_schema.py`
- `test_schema_pydantic_models_and_validators.py`
- `test_session.py`
- `test_steps.py`
- `test_validation.py`
- `tests/l4/test_registry.py`
- `tests/l4/test_schema.py`
- `tests/l4/test_schema_pydantic_models_and_validators.py`
- `tier_assessor.py`
- `token_burn_condition_executor.py`
- `token_supply_target_calculator.py`
- `tools/coverage/validate.py`
- `tools/mcp/membrane_server.py`
- `validation.py`
- `versions.py`
- `vesting.py`

**Doc refs:**
- `docs/ARCHITECTURE.md`
- `docs/MAPPING.md`
- `docs/TAXONOMY.md`
- `docs/api/sse/ALGORITHM_SSE_API.md`
- `docs/api/sse/BEHAVIORS_SSE_API.md`
- `docs/api/sse/HEALTH_SSE_API.md`
- `docs/api/sse/IMPLEMENTATION_SSE_API.md`
- `docs/api/sse/OBJECTIVES_SSE_API.md`
- `docs/api/sse/PATTERNS_SSE_API.md`
- `docs/api/sse/SYNC_SSE_API.md`
- `docs/api/sse/VALIDATION_SSE_API.md`
- `docs/auth/PATTERNS_Auth.md`
- `docs/compliance/PATTERNS_Compliance.md`
- `docs/compliance/SYNC_Compliance.md`
- `docs/economy/OBJECTIVES_Economy.md`
- `docs/economy/PATTERNS_Economy.md`
- `docs/economy/SYNC_Economy.md`
- `docs/economy/staking/OBJECTIVES_Staking.md`
- `docs/economy/token/ALGORITHM_Token.md`
- `docs/economy/token/IMPLEMENTATION_Token.md`
- `docs/economy/token/SPL_TOKEN_2022_SPECS.md`
- `docs/economy/token/VALIDATION_Token.md`
- `docs/l4/PATTERNS_L4.md`
- `docs/l4/compliance/PATTERNS_Compliance.md`
- `docs/l4/laws/ALGORITHM_Laws.md`
- `docs/l4/laws/BEHAVIORS_Laws.md`
- `docs/l4/laws/HEALTH_Laws.md`
- `docs/l4/laws/IMPLEMENTATION_Laws.md`
- `docs/l4/laws/OBJECTIVES_Laws.md`
- `docs/l4/laws/PATTERNS_Laws.md`
- `docs/l4/laws/SYNC_Laws.md`
- `docs/l4/laws/VALIDATION_Laws.md`
- `docs/l4/registry/ALGORITHM_Registry.md`
- `docs/l4/registry/BEHAVIORS_Registry.md`
- `docs/l4/registry/HEALTH_Registry.md`
- `docs/l4/registry/IMPLEMENTATION_Registry.md`
- `docs/l4/registry/OBJECTIVES_Registry.md`
- `docs/l4/registry/PATTERNS_Registry.md`
- `docs/l4/registry/SYNC_Registry.md`
- `docs/l4/registry/VALIDATION_Registry.md`
- `docs/l4/registry/VOCABULARY_Registry.md`
- `docs/l4/schema/ALGORITHM_Schema.md`
- `docs/l4/schema/BEHAVIORS_Schema.md`
- `docs/l4/schema/HEALTH_Schema.md`
- `docs/l4/schema/IMPLEMENTATION_Schema.md`
- `docs/l4/schema/OBJECTIVES_Schema.md`
- `docs/l4/schema/PATTERNS_Schema.md`
- `docs/l4/schema/SYNC_Schema.md`
- `docs/l4/schema/VALIDATION_Schema.md`
- `docs/manifesto/PATTERNS_Manifesto.md`
- `docs/membrane/ALGORITHM_Membrane_System.md`
- `docs/membrane/HEALTH_Membrane_System.md`
- `docs/membrane/IMPLEMENTATION_Membrane_System.md`
- `docs/membrane/MAPPING_Doctor_Issues_To_Protocols.md`
- `docs/membrane/MAPPING_Issue_Type_Verification.md`
- `docs/membrane/PATTERNS_Membrane.md`
- `docs/membrane/PATTERNS_Membrane_System.md`
- `docs/membrane/SKILLS_AND_PROTOCOLS_Mapping.md`
- `docs/membrane/SYNC_Membrane_System_archive_2025-12.md`
- `docs/membrane/VALIDATION_Completion_Verification.md`
- `docs/membrane/VALIDATION_Membrane_System.md`
- `shrine/CLAUDE.md`
- `templates/README.md`
- `token/SPL_TOKEN_2022_SPECS.md`

**Sections:**
- # Repository Map: mind-protocol

**Sections:**
- # Repository Map: mind-protocol/api
- ## Statistics
- ## Module Dependencies
- ## File Tree
- ## File Details
