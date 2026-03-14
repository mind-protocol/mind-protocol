# Spawning — Implementation: Code Architecture

```
STATUS: STABLE
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
BEHAVIORS:       ./BEHAVIORS_Spawning.md
PATTERNS:        ./PATTERNS_Spawning.md
ALGORITHM:       ./ALGORITHM_Spawning.md
VALIDATION:      ./VALIDATION_Spawning.md
THIS:            IMPLEMENTATION_Spawning.md (you are here)
HEALTH:          ./HEALTH_Spawning.md
SYNC:            ./SYNC_Spawning.md

IMPL:            l4/spawning/citizen_spawning_pipeline_with_safety_gates.py
```

---

## CODE STRUCTURE

```
l4/spawning/
├── __init__.py                                        # Exports: spawn_citizen, data classes
└── citizen_spawning_pipeline_with_safety_gates.py     # Full pipeline (26 tests passing)
```

### File Responsibilities

| File | Purpose | Key Functions | Lines | Status |
|------|---------|---------------|-------|--------|
| `citizen_spawning_pipeline_with_safety_gates.py` | Full spawning pipeline | `spawn_citizen()`, `validate_safety()`, `generate_sid()`, `generate_solana_wallet()` | ~300 | OK |

---

## ENTRY POINTS

| Entry Point | File | Triggered By |
|-------------|------|--------------|
| `spawn_citizen(request)` | `citizen_spawning_pipeline_with_safety_gates.py` | MCP tool, API, or direct call |

---

## BIDIRECTIONAL LINKS

### Docs → Code

| Doc Section | Implemented In |
|-------------|----------------|
| ALGORITHM step 1-2 | `select_seed_traits()`, `categorize_intent()` |
| ALGORITHM step 3 | `validate_safety()` |
| ALGORITHM step 4 | `generate_sid()` |
| ALGORITHM step 5 | `generate_solana_wallet()` |
| ALGORITHM step 6 | `create_parent_links()` |
| VALIDATION V1 | `is_empathy_adjacent()` in safety gate |
| VALIDATION V2 | Concentration check in `validate_safety()` |
| VALIDATION V3 | Diversity check in `validate_safety()` |
| VALIDATION V4 | `cosine_distance()` + `compute_trait_vector()` |

### Tests

| Test File | Tests | Covers |
|-----------|-------|--------|
| `tests/l4/test_spawning_pipeline_safety_gates_and_birth.py` | 26 | V1-V8, full pipeline, edge cases |
