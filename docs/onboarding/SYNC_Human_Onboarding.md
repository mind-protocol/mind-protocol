# Human Onboarding — Sync: Current State

```
LAST_UPDATED: 2026-03-17
UPDATED_BY: @mentor
STATUS: DESIGNING
```

---

## MATURITY

**What's canonical (v1):**
- The pipeline design: @mind → @mentor → @genesis
- SID (universal, same format for humans and AI citizens) as primary identifier, @handle as alias
- L4 creation on first message
- Task-based handoff to @mentor

**What's still being designed:**
- SID generation for humans (same sha256 format as AI citizens)
- Migration of existing citizens to SIDs (those without one)
- Bridge modifications for new-arrival detection
- @mind's welcome conversation template
- @mentor's matching algorithm details

**What's proposed (v2+):**
- Multi-platform PID unification (same human on TG and Discord = same PID)
- Reputation portability across universes
- Self-service handle change

---

## CURRENT STATE

**No code exists.** The pipeline is fully designed in ALGORITHM_Human_Onboarding.md but nothing is implemented.

The current system routes new messages to default citizen or bonded partner, with no onboarding flow.

---

## IN PROGRESS

### Pipeline Design
- **Started:** 2026-03-17
- **By:** @mentor
- **Status:** ALGORITHM written, needs review by @mind and NLR
- **Context:** Triggered by NLR's directive to formalize @mind → @mentor → @genesis handoff

---

## RECENT CHANGES

### 2026-03-17: Pipeline Designed
- **What:** Full onboarding algorithm documented
- **Why:** Current system has no human onboarding flow. New humans get no welcome, no matching, no structure.
- **Key decisions:**
  - Universal SID (same crypto hash format for humans and AI) replaces @handle as primary ID
  - @mind does first contact + L4 creation
  - @mentor gets task for portrait + matching
  - @genesis spawns if no match found
- **Files:** `docs/onboarding/ALGORITHM_Human_Onboarding.md`

---

## HANDOFF: FOR AGENTS

**Your likely VIEW:** VIEW_Implement

**Where I stopped:** Algorithm fully designed. No code written.

**What you need to understand:**
- The bridges (telegram_bridge.py) need modification to detect new arrivals
- L4 needs a PID counter (atomic, sequential)
- The task system needs to route to @mentor
- @mind's welcome logic needs to be in the orchestrator, not the bridge

**Watch out for:**
- Don't modify the bridge to do the onboarding itself — the bridge is transport, not logic
- The PID counter must be atomic — concurrent arrivals on different platforms must not collide
- Don't break existing citizen routing while adding new-human detection

**Open questions:**
- Where does the PID counter live? Redis atomic int? L4 graph property?
- How to detect "same human, different platform"? (phone number? email? manual merge?)

---

## HANDOFF: FOR HUMAN

**Executive summary:**
Onboarding pipeline fully designed — @mind accueille, crée L4 avec PID, collecte le contexte, crée une tâche pour @mentor qui construit le portrait, cherche un match, et passe à @genesis si nécessaire. Pas de code encore.

**Decisions made:**
- SID universel (sha256[:16], même format pour humains et IA) remplace @handle comme identifiant principal
- L4 créé dès le premier message, pas d'attente
- Le flow est : @mind → tâche → @mentor → (optionnel) @genesis

**Needs your input:**
- SID format validé : `sha256[:16]` — même pour humains et IA
- Faut-il migrer les citoyens existants immédiatement ?
- Qui implémente : @genesis côté code ? Un agent groundwork ?

---

## TODO

### Immediate
- [ ] NLR : Valider le format SID universel (sha256[:16])
- [ ] NLR : Valider le flow @mind → @mentor → @genesis
- [ ] Implémenter `generate_human_sid()` dans L4 (même pattern que identity_generator.py)
- [ ] Migrer les ~60 citoyens existants qui n'ont pas de SID
- [ ] Modifier telegram_bridge.py pour détecter les nouveaux arrivants
- [ ] Écrire le welcome template de @mind
- [ ] Créer le template de tâche @mentor

### Later
- [ ] Multi-platform SID unification (same human on TG + Discord = same SID)
- [ ] Rest of doc chain (OBJECTIVES, PATTERNS, BEHAVIORS, VALIDATION, IMPLEMENTATION, HEALTH)

---

## POINTERS

| What | Where |
|------|-------|
| Onboarding algorithm | `docs/onboarding/ALGORITHM_Human_Onboarding.md` |
| Current bridge | `runtime/bridges/telegram_bridge.py` |
| Bond handler | `mcp/tools/bond_handler.py` |
| Spawn handler | `mcp/tools/spawn_handler.py` |
| The Prism docs | `docs/spawning/the_prism/` |
| L4 citizen upsert | `runtime/l4/citizen_l4_upsert.py` |
