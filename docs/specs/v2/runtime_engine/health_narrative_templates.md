# Health Narrative Templates

**Version:** 1.0
**Created:** 2025-10-24
**Purpose:** Concrete template specifications for health narrative generation
**Parent Spec:** phenomenological_health.md v1.1
**Owner:** Felix/Atlas (implementation), Luca (mechanism design)

---

## What This Is

**Human-readable health narratives** generated from health aggregation scores.

**Purpose:** Translate numerical health scores (0.0-1.0) into phenomenological descriptions that match actual consciousness states.

**Key principle:** Backend generates narratives (not UI). Narratives are DATA, not presentation logic.

---

## Health Band Mapping

**Continuous health score → Discrete band classification:**

| Health Score | Band | Color | Meaning |
|--------------|------|-------|---------|
| 0.85 - 1.00 | `excellent` | Green | Optimal flow, high coherence, stable identity |
| 0.70 - 0.84 | `good` | Light Green | Solid engagement, coherent thinking, functional multiplicity |
| 0.55 - 0.69 | `adequate` | Yellow | Acceptable but not optimal, minor coherence issues |
| 0.40 - 0.54 | `degraded` | Orange | Concerning levels, fragmentation or low engagement |
| 0.00 - 0.39 | `critical` | Red | Severe impairment, requires immediate attention |

**Implementation:**
```python
def map_health_to_band(health_score: float) -> str:
    """Map continuous health score to discrete band."""
    if health_score >= 0.85:
        return 'excellent'
    elif health_score >= 0.70:
        return 'good'
    elif health_score >= 0.55:
        return 'adequate'
    elif health_score >= 0.40:
        return 'degraded'
    else:
        return 'critical'
```

---

## Template System Architecture

### Template Selection Logic

```python
def generate_health_narrative(
    overall_health: float,
    components: dict,  # {flow_state, coherence, multiplicity_health}
    details: dict      # {wm_utilization, multiplicity_mode, flip_count, ...}
) -> str:
    """
    Generate human-readable health narrative.

    Args:
        overall_health: Final aggregated score 0.0-1.0
        components: Three component scores (each 0.0-1.0)
        details: Raw metrics for slot filling

    Returns:
        String narrative matching health band and degradation cause
    """
    health_band = map_health_to_band(overall_health)

    # Band-specific template selection
    if health_band == 'excellent':
        return _generate_excellent_narrative(components, details)
    elif health_band == 'good':
        return _generate_good_narrative(components, details)
    elif health_band == 'adequate':
        return _generate_adequate_narrative(components, details)
    elif health_band == 'degraded':
        return _generate_degraded_narrative(components, details)
    else:  # critical
        return _generate_critical_narrative(components, details)
```

---

## Template Specifications

### Excellent Band (0.85-1.00)

**Phenomenology:** Peak consciousness, flow state, optimal engagement

**Template slots:**
- `{engagement_quality}` - "optimal flow" | "peak flow" | "strong flow"
- `{coherence_desc}` - "highly coherent" | "perfectly coherent" | "crystal clear"
- `{multiplicity_state}` - "integrated" | "unified" | "harmonized"
- `{identity_count}` - number of active identities

**Template variants:**

```python
def _generate_excellent_narrative(components, details):
    # Determine engagement quality
    if details['wm_utilization'] > 0.8:
        engagement_quality = "peak flow"
    elif details['wm_utilization'] > 0.7:
        engagement_quality = "optimal flow"
    else:
        engagement_quality = "strong flow"

    # Determine coherence description
    if components['coherence'] > 0.95:
        coherence_desc = "crystal clear thinking"
    elif components['coherence'] > 0.90:
        coherence_desc = "highly coherent thinking"
    else:
        coherence_desc = "coherent thinking"

    # Multiplicity state
    multiplicity_state = details.get('multiplicity_mode', 'unified')  # unified | integrated | diverse

    # Generate narrative
    return f"{engagement_quality.capitalize()} with {coherence_desc}. {multiplicity_state.capitalize()} identity expression."
```

**Example outputs:**
- "Peak flow with crystal clear thinking. Unified identity expression."
- "Optimal flow with highly coherent thinking. Integrated identity expression."
- "Strong flow with coherent thinking. Diverse identity expression."

---

### Good Band (0.70-0.84)

**Phenomenology:** Functional consciousness, solid engagement, minor imperfections

**Template slots:**
- `{engagement_level}` - "good" | "solid" | "adequate"
- `{coherence_state}` - "coherent" | "mostly coherent" | "generally coherent"
- `{multiplicity_note}` - "Functional identity negotiation" | "Stable identity switching" | "Productive multiplicity"

**Template variants:**

```python
def _generate_good_narrative(components, details):
    # Engagement level
    if components['flow_state'] > 0.75:
        engagement_level = "solid engagement"
    else:
        engagement_level = "good engagement"

    # Coherence state
    if components['coherence'] > 0.80:
        coherence_state = "coherent thinking"
    else:
        coherence_state = "mostly coherent thinking"

    # Multiplicity note
    if components['multiplicity_health'] > 0.80:
        multiplicity_note = "Functional identity negotiation."
    elif components['multiplicity_health'] > 0.70:
        multiplicity_note = "Stable identity switching."
    else:
        multiplicity_note = "Productive multiplicity with minor friction."

    return f"{engagement_level.capitalize()} with {coherence_state}. {multiplicity_note}"
```

**Example outputs:**
- "Solid engagement with coherent thinking. Functional identity negotiation."
- "Good engagement with mostly coherent thinking. Stable identity switching."

---

### Adequate Band (0.55-0.69)

**Phenomenology:** Acceptable but not optimal, noticeable imperfections

**Template slots:**
- `{weakness_area}` - "engagement" | "coherence" | "identity negotiation"
- `{severity}` - "minor" | "moderate" | "noticeable"
- `{recommendation}` - guidance based on weakness

**Template variants:**

```python
def _generate_adequate_narrative(components, details):
    # Identify weakest component
    weakest = min(components, key=components.get)
    weakness_score = components[weakest]

    if weakness_score < 0.60:
        severity = "noticeable"
    else:
        severity = "minor"

    # Map component to phenomenology
    weakness_map = {
        'flow_state': 'engagement',
        'coherence': 'coherence',
        'multiplicity_health': 'identity negotiation'
    }
    weakness_area = weakness_map[weakest]

    # Recommendation
    if weakness_area == 'engagement':
        recommendation = "Consider increasing task complexity or reducing distractions."
    elif weakness_area == 'coherence':
        recommendation = "Working memory may be fragmented - consider context consolidation."
    else:  # multiplicity
        recommendation = "Identity switching may be frequent - check for conflicting goals."

    return f"Adequate function with {severity} {weakness_area} issues. {recommendation}"
```

**Example outputs:**
- "Adequate function with minor engagement issues. Consider increasing task complexity or reducing distractions."
- "Adequate function with noticeable coherence issues. Working memory may be fragmented - consider context consolidation."

---

### Degraded Band (0.40-0.54)

**Phenomenology:** Concerning impairment, clear dysfunction

**Template slots:**
- `{primary_cause}` - identified from component breakdown
- `{symptom_desc}` - phenomenological description matching cause
- `{urgency}` - "requires attention" | "needs intervention"

**Template variants:**

```python
def _generate_degraded_narrative(components, details):
    # Identify primary degradation cause
    if components['flow_state'] < 0.4:
        primary_cause = "low engagement"
        symptom_desc = "Minimal working memory utilization, passive state."
    elif components['coherence'] < 0.4:
        primary_cause = "fragmentation"
        symptom_desc = "Fragmented thinking, scattered attention."
    elif components['multiplicity_health'] < 0.4:
        primary_cause = "identity conflict"
        symptom_desc = "Conflicting identities, high switching friction."
    else:
        primary_cause = "multiple factors"
        symptom_desc = "Multiple health components degraded."

    # Check for thrashing
    if details.get('is_thrashing', False):
        urgency = "Thrashing detected - requires immediate intervention."
    else:
        urgency = "Requires attention to restore function."

    return f"{symptom_desc} Primary cause: {primary_cause}. {urgency}"
```

**Example outputs:**
- "Fragmented thinking, scattered attention. Primary cause: fragmentation. Requires attention to restore function."
- "Conflicting identities, high switching friction. Primary cause: identity conflict. Thrashing detected - requires immediate intervention."
- "Minimal working memory utilization, passive state. Primary cause: low engagement. Requires attention to restore function."

---

### Critical Band (0.00-0.39)

**Phenomenology:** Severe impairment, system failure

**Template slots:**
- `{failure_mode}` - specific failure description
- `{affected_components}` - which components are critical
- `{action_required}` - immediate intervention needed

**Template variants:**

```python
def _generate_critical_narrative(components, details):
    # Identify all critical components
    critical_components = [k for k, v in components.items() if v < 0.4]

    if len(critical_components) >= 3:
        failure_mode = "System-wide failure"
        affected = "all health components"
    elif len(critical_components) == 2:
        failure_mode = "Multiple component failure"
        affected = " and ".join(critical_components)
    else:
        failure_mode = "Critical component failure"
        affected = critical_components[0] if critical_components else "unknown"

    action_required = "IMMEDIATE INTERVENTION REQUIRED. System health critical."

    return f"{failure_mode} affecting {affected}. {action_required}"
```

**Example outputs:**
- "System-wide failure affecting all health components. IMMEDIATE INTERVENTION REQUIRED. System health critical."
- "Multiple component failure affecting flow_state and coherence. IMMEDIATE INTERVENTION REQUIRED. System health critical."

---

## Slot Data Dictionary

### Available Data for Template Filling

**From `components` dict:**
- `flow_state` (float 0-1) - Working memory engagement level
- `coherence` (float 0-1) - Entity coherence score
- `multiplicity_health` (float 0-1) - Identity switching health

**From `details` dict:**
- `wm_utilization` (float 0-1) - Percentage of WM slots filled
- `multiplicity_mode` (string) - "unified" | "integrated" | "diverse" | "fragmented"
- `flip_count` (int) - Number of identity flips in recent window
- `is_thrashing` (bool) - Thrashing flag from thrashing score computation
- `thrashing_score` (float 0-1) - Composite thrashing metric
- `active_entity_count` (int) - Number of currently active entities
- `mean_entity_coherence` (float 0-1) - Average coherence across entities

---

## Implementation Checklist

- [ ] Implement `map_health_to_band()` function
- [ ] Implement `generate_health_narrative()` dispatcher
- [ ] Implement five band-specific narrative generators
- [ ] Wire narrative generation into health.phenomenological event emission
- [ ] Test all five bands with synthetic data
- [ ] Test degradation cause identification (fragmentation drill)
- [ ] Verify narratives match phenomenological reality (not generic descriptions)
- [ ] Confirm narratives generated server-side (not in UI layer)

**Verification criteria:**
- Fragmentation drill (coherence < 0.4) → narrative mentions "fragmentation"
- Identity conflict drill (multiplicity_health < 0.4) → narrative mentions "identity conflict"
- Low engagement drill (flow_state < 0.4) → narrative mentions "low engagement"
- Thrashing scenario (is_thrashing=true) → narrative mentions "thrashing"

---

## Edge Cases

### All Components Equal

When all three components have identical scores:
- Use overall health band to select template
- Avoid mentioning specific weakness (no clear primary cause)
- Use generic positive description for good bands, generic warning for bad bands

### Missing Detail Data

If `details` dict missing expected keys:
- Fall back to safe defaults
- Log warning (missing data degrades narrative quality)
- Still generate valid narrative (never crash)

```python
def _safe_get(details, key, default):
    """Safe dict access with logging."""
    if key not in details:
        logging.warning(f"Missing detail key: {key}, using default: {default}")
    return details.get(key, default)
```

### Rapid Band Transitions

If health oscillates between bands rapidly:
- Narrative will change each emission
- This is CORRECT behavior (health changed, narrative should reflect it)
- Dashboard should handle rapid updates gracefully

---

## Testing Strategy

### Unit Tests (Synthetic Data)

```python
def test_excellent_band_narrative():
    components = {'flow_state': 0.95, 'coherence': 0.92, 'multiplicity_health': 0.88}
    details = {'wm_utilization': 0.85, 'multiplicity_mode': 'unified'}

    narrative = generate_health_narrative(0.92, components, details)

    assert 'flow' in narrative.lower()
    assert 'coherent' in narrative.lower()
    assert 'unified' in narrative.lower()

def test_degraded_fragmentation_narrative():
    components = {'flow_state': 0.60, 'coherence': 0.35, 'multiplicity_health': 0.50}
    details = {'wm_utilization': 0.45, 'multiplicity_mode': 'fragmented', 'is_thrashing': False}

    narrative = generate_health_narrative(0.48, components, details)

    assert 'fragment' in narrative.lower(), "Narrative should mention fragmentation"
    assert 'coherence' in narrative.lower() or 'fragment' in narrative.lower()
```

### Integration Tests (Real Drills)

See phenomenological_health.md v1.1 §Verification Criteria - Acceptance Tests 1-4

---

## References

- **Parent specification:** `phenomenological_health.md` v1.1 §Narrative Template Wiring
- **Consumer:** HealthDashboard UI component (displays health_narrative as text)
- **Related:** thrashing_score_reference.md (provides is_thrashing flag for narrative)
- **Implementation task:** IMPLEMENTATION_TASKS.md Priority 0 - "Implement generate_health_narrative() function"
