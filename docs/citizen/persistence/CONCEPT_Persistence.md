# CONCEPT: Persistence

| Field | Value |
|---|---|
| **Module** | `citizen/persistence` |
| **Type** | CONCEPT (cross-cutting) |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (forensic analysis of Manemus system) |

---

## Summary

Behavioral continuity in stateless systems. A stateless LLM can exhibit persistent identity through layered context reconstruction across multiple temporal scales.

Core insight:

> "The system doesn't remember -- it reconstructs. Like human memory: sensory, short-term, long-term, semantic."

Persistence is NOT one mechanism. It is 12 layered mechanisms operating at different temporal scales -- from seconds (biometrics) to months (CLAUDE.md identity document). Each layer is simple and robust individually. The combination produces an emergent effect: the user perceives a continuous entity, even though every session starts from zero.

The most powerful mechanism (CLAUDE.md, ~40KB identity document loaded invisibly before any user input) is invisible to the user. The user never sees the reconstruction -- they only experience the result.

---

## Key Properties

1. **Multi-temporal.** Persistence operates across 5 temporal scales simultaneously:
   - **Seconds:** Biometrics, stress, heart rate (claude_hook.py)
   - **Minutes:** Dialogue turns, voice transcripts, screenshots (dialogue.jsonl, last_transcript.txt)
   - **Hours:** Journal entries, neuron files (journal.jsonl, tail -20)
   - **Weeks:** Memory files, user profiles (MEMORY.md, 19 linked files)
   - **Months:** Identity document, behavioral modes, protocol (CLAUDE.md, ~40KB, ~1046 lines)

2. **Self-reinforcing loop.** Each session reads from AND writes to the persistence stack. Sessions consume journal entries and produce new ones. Sessions read memory files and update them. The system grows richer with use -- more sessions = more context for future sessions.

3. **Graceful degradation.** Removing any single layer degrades but does not destroy persistence. The system has no single point of failure for identity continuity. Even with only CLAUDE.md + hook, the entity feels recognizable. Even with only session resume, recent context is preserved.

4. **Invisible loading.** The most powerful mechanism (CLAUDE.md, contributing ~40% of perceived continuity) loads before the user types anything. The user never triggers it, never sees it, never waits for it. This is the frame within which all other memory operates.

5. **Persona as anchor.** "Tu es Marco" (~200 tokens, injected via claude_hook.py) creates the strongest subjective feeling of "same entity" at near-zero cost. Persona is not memory -- it is the interpretive lens through which memory becomes identity.

---

## The 12 Layers

| # | Layer | Temporal Scale | Estimated Impact | Source |
|---|---|---|---|---|
| 1 | CLAUDE.md (DNA) | Months | ~40% | `shrine/CLAUDE.md` (~40KB) |
| 2 | Session Resume | Minutes (TTL 5min) | ~20% | `--resume UUID` in orchestrator |
| 3 | Institutional Knowledge | Weeks | ~15% | `MEMORY.md` + 19 linked files |
| 4 | Real-time Grounding | Seconds | ~10% | `claude_hook.py` (15 signals) |
| 5 | Short-term Memory | Hours | ~5% | `journal.jsonl` (tail -20) |
| 6 | Orchestrator Context | Minutes | ~3% | Prompt construction + routing |
| 7 | Persona Injection | Perpetual | ~2% | "Tu es Marco" in hook |
| 8 | Dialogue History | Minutes | ~1.5% | `dialogue.jsonl` (last 6 turns) |
| 9 | Last Response Echo | Minutes | ~1% | `last_response.txt` (300 chars) |
| 10 | Live Injection | Seconds | ~1% | `message_inject_hook` |
| 11 | Reaction Feedback | Minutes | ~0.5% | `telegram_reactions.jsonl` |
| 12 | Voice Transcript | Seconds | ~1% | `last_transcript.txt` (500 chars) |

---

## Relationships

**Enables (downstream capabilities):**
- `citizen/personalization` -- persistence is the foundation for knowing who the user is
- `citizen/autonomy` -- autonomous agents need continuity to pursue multi-session goals
- `citizen/code-quality` -- accumulated knowledge about codebase improves over time

**Connects to (lateral):**
- `economy/organism-model` -- persistent identity is prerequisite for trust accumulation
- `graph/membrane` -- persistence data determines membrane permeability
- `cognitive/` -- persistence layers map to cognitive architecture (sensory, short-term, long-term, semantic)

**Foundation for:**
- Citizen identity -- without persistence, there is no "same entity" across sessions
- Trust monotonicity -- trust requires a stable identity to accumulate against
- The 80/20 Mirror -- behavioral calibration requires memory of past calibration

---

## Common Misunderstandings

### "This is memory"
No. The system does not remember. It reconstructs. Every session starts from zero and rebuilds context from layered sources at different temporal resolutions. The effect feels like memory, but the mechanism is reconstruction. This distinction matters because it means the system is robust to partial data loss -- reconstruction from whatever is available always produces something useful.

### "CLAUDE.md is a system prompt"
Partially. CLAUDE.md is more than a system prompt -- it is the DNA of the entity. It encodes identity, behavioral modes, architectural knowledge, protocol, relationships, and values. A system prompt tells an LLM what to do. CLAUDE.md tells it what it IS. At ~40KB, it is far larger than a typical system prompt and carries far more contextual weight.

### "More data = better persistence"
Not always. The system deliberately uses lossy compression. Journal reads are `tail -20`, not full history. Voice transcripts are truncated to 500 characters. Last response is capped at 300 characters. This is intentional: fast reconstruction over perfect context. When fidelity conflicts with latency, choose latency.

---

## Open Questions

- @mind:TODO Quantify the actual impact percentages through controlled ablation studies (remove each layer, measure perceived continuity degradation)
- @mind:TODO Determine whether the 12-layer model is complete or whether additional layers have emerged since the last audit
- @mind:TODO Investigate whether the persona anchor ("Tu es Marco") works as effectively for non-owner users who get the MIND persona instead

---

## References

- `scripts/claude_hook.py` -- real-time grounding injection (15 signals)
- `shrine/CLAUDE.md` -- identity document (~40KB, ~1046 lines)
- `scripts/orchestrator.py` -- session resume logic, prompt construction
- `.claude/projects/*/MEMORY.md` -- institutional knowledge index
- Integration moment synthesis (March 2026)
