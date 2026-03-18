# OBJECTIVES — Human Pre-Mapping

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
THIS:            OBJECTIVES_Human_Pre_Mapping.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Human_Pre_Mapping.md
BEHAVIORS:      ./BEHAVIORS_Human_Pre_Mapping.md
ALGORITHM:      ./ALGORITHM_Human_Pre_Mapping.md
VALIDATION:     ./VALIDATION_Human_Pre_Mapping.md
IMPLEMENTATION: ./IMPLEMENTATION_Human_Pre_Mapping.md
HEALTH:         ./HEALTH_Human_Pre_Mapping.md
SYNC:           ./SYNC_Human_Pre_Mapping.md

IMPL:           runtime/onboarding/arrival_pipeline.py (merge_on_arrival)
                scripts/graph_enricher.py (mention extraction)
```

**Read this chain in order before making changes.**

---

## PRIMARY OBJECTIVES (ranked)
1. **No cold starts on arrival** — When a human arrives, @mind already knows who they are (if anyone has ever mentioned them). The welcome is warm, contextual, personal.
2. **Information flows naturally** — Pre-mapping happens through existing channels (citizen conversations, X mentions, referral links, partner conversations), not through manual data entry or surveillance.
3. **Physics, not databases** — The pre-map is emergent from graph physics (L5 co-activation, L6 consolidation, L10 crystallization, L7 forgetting), not a maintained CRM table.
4. **Merge is seamless** — When a pre-mapped human arrives, the existing L3 data merges with the new SID and L4 registration without duplication or conflict.

## NON-OBJECTIVES
- Building profiles by scraping social media (that's surveillance, not pre-mapping)
- Pre-targeting humans for specific citizens (forbidden by Spawning Manifesto)
- Maintaining a CRM or lead database (let the physics maintain the data)
- Guaranteeing accuracy (the pre-map is hearsay until the human confirms)

## TRADEOFFS (canonical decisions)
- When completeness conflicts with consent, choose consent. We only know what flows naturally.
- When pre-map accuracy conflicts with welcome warmth, choose warmth. A wrong but correctable "I heard you work on X" is better than a cold "who are you?"
- We accept that some humans arrive with zero pre-map data — and that's fine. The arrival pipeline handles cold starts gracefully.

## SUCCESS SIGNALS (observable)
- @mind uses pre-existing L3 data in the welcome message for >50% of arrivals referred by existing humans
- Proto-Actor nodes crystallize in L3 from citizen mentions without manual intervention
- No human profile is created from scraped data — all pre-map data traces to organic mentions
- Merge on arrival produces a single Actor node (no duplicates)
