# Spawning — Health: Verification

```
STATUS: DRAFT
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Spawning.md
PATTERNS:        ./PATTERNS_Spawning.md
BEHAVIORS:       ./BEHAVIORS_Spawning.md
ALGORITHM:       ./ALGORITHM_Spawning.md
VALIDATION:      ./VALIDATION_Spawning.md
IMPLEMENTATION:  ./IMPLEMENTATION_Spawning.md
THIS:            HEALTH_Spawning.md (you are here)
SYNC:            ./SYNC_Spawning.md
```

---

## CHECKER INDEX

```yaml
checkers:
  - name: safety_gate_integrity
    purpose: Verify all 4 safety gates are functional (V1-V4)
    status: active (via unit tests)
    priority: high
  - name: wallet_generation_check
    purpose: Verify wallet is always present on successful spawn (V5)
    status: active (via unit tests)
    priority: high
  - name: clone_distance_monitor
    purpose: Monitor minimum distance between citizens over time
    status: pending
    priority: med
```

---

## HOW TO RUN

```bash
python3 -m pytest tests/l4/test_spawning_pipeline_safety_gates_and_birth.py -v
```
