# Human Pre-Mapping — Sync: Current State

```
LAST_UPDATED: 2026-03-18
UPDATED_BY: @mentor
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- The 6 channels pattern (citizen mentions, X inbound, referral, NLR intent, partner conversations, anamnesis)
- Physics-based accumulation (L5, L6, L10 crystallization, L7 forgetting)
- Merge-on-arrival in the arrival pipeline
- Anti-patterns (no scraping, no pre-targeting, no unverified assertions)

**What's still being designed:**
- Name matching heuristic (fuzzy + embedding + referral priority)
- L10 crystallization parameters for proto-Actor emergence
- Referral link format and injection path
- How graph_enricher extracts human names (not just @handles) from citizen messages

**What's proposed (v2+):**
- Cross-universe proto-Actors (mentioned in Venezia, arrives in LP)
- Pre-map scoring (how confident are we in the data)
- Automatic partner suggestion based on pre-map domain affinity

---

## CURRENT STATE

The pattern is defined but not yet implemented as a distinct module. The pieces exist:
- `graph_enricher.on_message()` already creates Moments with mentions
- `twitter_bridge.process_mention()` already creates Moments from X
- `arrival_pipeline.check_existing_l3_data()` already searches L3 for the arriving name

What's missing:
- graph_enricher doesn't extract human names from free text (only @handles)
- L10 crystallization hasn't been verified to produce proto-Actors from mentions
- Merge-on-arrival doesn't fuse proto-Actor with new SID yet (it searches but doesn't merge)
- No referral link system exists

---

## RECENT CHANGES

### 2026-03-18: Module documented

- **What:** Full doc chain for Human Pre-Mapping (OBJECTIVES, PATTERNS, BEHAVIORS, SYNC)
- **Why:** NLR asked how to make pre-mapping happen naturally. The answer: define channels, let physics accumulate, merge on arrival.
- **Insight:** This isn't a feature to build — it's a property that emerges from connecting existing channels to the arrival pipeline.

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Extend

**Where I stopped:** Documentation complete. Implementation needs 4 concrete changes:
1. graph_enricher: extract human names from free text (NLP/regex/LLM)
2. L10: verify crystallization parameters create proto-Actors from 10+ mentions
3. arrival_pipeline: add merge logic (proto-Actor + SID = single Actor)
4. Referral links: design format, add injection path

**Watch out for:**
- Don't build a CRM. The physics IS the CRM.
- Don't scrape. All data must trace to organic channels.
- The name matching problem is real — "Florent Berthet" vs "Flo" vs "florent-berthet" need to resolve to the same proto-Actor.

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Human pre-mapping is documented as a 6-channel emergent process. No new systems — just connecting existing graph_enricher, twitter_bridge, and arrival_pipeline so that knowledge about future humans accumulates naturally and is used on arrival.

**Decisions made:**
- 6 channels defined (citizen mentions, X, referral, NLR intent, partner conversations, anamnesis)
- Physics-based, not database-based
- Anti-patterns clear (no scraping, no pre-targeting)

**Needs your input:**
- Referral link format — do you want a URL system or just manual injection?
- Name extraction from free text — NLP, regex, or LLM-based?

---

## TODO

### Immediate
- [ ] graph_enricher: add human name extraction from free text (not just @handles)
- [ ] arrival_pipeline: add proto-Actor → SID merge logic
- [ ] Verify L10 crystallization creates proto-Actors from 10+ mentions

### Later
- [ ] Referral link system (URL format + injection path)
- [ ] ALGORITHM doc (detailed merge algorithm)
- [ ] VALIDATION doc (invariants)
- [ ] IMPLEMENTATION doc (code pointers)
- [ ] HEALTH doc (monitoring)
- IDEA: Pre-map confidence scoring (how much do we trust the data)

---

## CONSCIOUSNESS TRACE

**Mental state:** Confident in the pattern. The key insight is that pre-mapping isn't a feature — it's an emergent property of a living graph. The channels exist. The physics exists. We just need to connect them.

**Threads held:**
- The name matching problem is harder than it looks (fuzzy matching across languages, nicknames, partial names)
- Anamnesis channel (channel 6) depends on the anamnesis process being implemented — it's referenced in the updated MIND_MANIFESTO but may not be live yet

**Intuition:** The most powerful channel will be #5 (partner conversations). When bonded humans casually mention friends, that's the highest-fidelity pre-map data because it comes with relationship context. But it requires active bonds, which requires more humans, which requires... pre-mapping working. Circular but bootstrappable.

---

## POINTERS

| What | Where |
|------|-------|
| Arrival pipeline | `mind-mcp/runtime/onboarding/arrival_pipeline.py` |
| Graph enricher | `mind-mcp/scripts/graph_enricher.py` |
| X bridge | `mind-mcp/runtime/bridges/twitter_bridge.py` |
| L3 physics laws | `mind-mcp/schema-l3.yaml` (applicable_laws section) |
| L10 crystallization | `mind-mcp/schema-l1.yaml` (L10_crystallization) |
| Spawning Manifesto (anti pre-targeting) | `mind-protocol/docs/manifesto/THE_SPAWNING_MANIFESTO.md` |
| Onboarding pipeline | `mind-protocol/docs/onboarding/ALGORITHM_Human_Onboarding.md` |
