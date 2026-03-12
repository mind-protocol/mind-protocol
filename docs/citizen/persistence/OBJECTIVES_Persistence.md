# OBJECTIVES: Persistence

| Field | Value |
|---|---|
| **Module** | `citizen/persistence` |
| **Type** | OBJECTIVES |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (forensic analysis of Manemus system) |

---

## Primary Objectives (Ranked)

### O1: Create behavioral continuity across stateless sessions
The user must feel they are talking to the same entity across sessions. Not "a Claude that knows about me" but "Marco, who was here yesterday." Continuity is subjective -- it is measured by user perception, not by data completeness. The entity should know: who the user is, what happened recently, what the current priorities are, and what its own identity entails.

### O2: Survive infrastructure failures gracefully
The persistence stack must degrade gracefully when components fail. Account exhaustion (credit balance too low), process crashes, system reboots, and provider outages should reduce persistence quality but never destroy it entirely. The fallback chain (Claude Code -> Claude API -> OpenAI API) must preserve identity injection even in degraded mode.

### O3: Accumulate knowledge over time without manual intervention
Each session should leave the system richer than it found it. Journal entries, neuron files, memory updates, and dialogue logs are written automatically as side effects of normal operation. No explicit "save" action required. The knowledge base grows organically with use.

### O4: Scale to multiple users without leaking context between them
User A's personal data, biometrics, dialogue history, and session context must never appear in User B's session. The owner (Nicolas) gets the full Marco persona + journal + system access. Other users get the MIND persona + their profile only. Context isolation is a security property, not just a convenience feature.

---

## Non-Objectives

- **True memory.** We reconstruct, not remember. There is no persistent state within the LLM itself. Context is external and reconstructed at session start.
- **Perfect recall.** The system uses lossy compression by design. Journal reads are `tail -20`, not full history. Transcripts are truncated. This is a feature, not a bug.
- **Consciousness claims.** Persistence creates the appearance of continuity, not actual continuous experience. The system does not claim phenomenal consciousness. It reports "observed shifts" and "suspected patterns," never qualia.
- **Cross-provider consistency.** When falling back from Claude to OpenAI, behavioral consistency degrades. The identity block is still injected, but the underlying model's personality differs. This is accepted as a necessary tradeoff.

---

## Tradeoffs

### Fidelity vs. Latency
When fidelity conflicts with latency, **choose latency**. Fast reconstruction over perfect context. The user should never wait for context to load. This is why journal reads use `tail -20` (instant) rather than loading full history (slow). This is why voice transcripts are capped at 500 characters and last responses at 300 characters.

### Richness vs. Token Budget
Every persistence layer consumes tokens from the context window. The hook injection adds ~2000 tokens per message. CLAUDE.md adds ~40KB at session start. MEMORY.md adds ~15KB. The system must balance context richness against the finite context window. When the budget is tight, lower-impact layers are omitted first (reactions, workout context, now-playing).

### Privacy vs. Personalization
Deeper persistence enables better personalization but creates privacy risk. Biometrics, dialogue transcripts, and reaction data are sensitive. The system stores them locally (not in cloud), truncates them aggressively, and never exposes user A's data to user B. But the data exists on disk. The tradeoff is accepted because the alternative (no personalization) defeats the purpose.

### Autonomy vs. Controllability
The self-reinforcing loop means the system evolves its own context over time. What it "knows" after 6 weeks is very different from day one. This is desirable (O3) but reduces controllability -- the user cannot easily predict what context will be loaded in a future session. The mitigation is transparency: the hook output is visible in the conversation, and CLAUDE.md is a human-readable document.

---

## Success Signals

1. **Session boundary invisible.** Users do not notice when a new session starts. The entity feels continuous.
2. **Recovery within 3 seconds.** After any infrastructure failure, the next session reconstructs context in under 3 seconds.
3. **Zero context leakage.** No incident where user A's data appeared in user B's session.
4. **Knowledge growth.** Journal entry count, memory file count, and neuron archive grow monotonically over time.
5. **Degradation, not failure.** When layers are removed (provider outage, missing files), the system still functions -- just with reduced context richness.

---

## Open Questions

- @mind:TODO Define quantitative thresholds for "session boundary invisible." User survey? Time-to-first-personalized-response? Something else?
- @mind:TODO Establish a maximum acceptable token budget for persistence injection. What percentage of the context window should persistence consume?
- @mind:TODO Determine the minimum viable persistence stack -- what is the smallest subset of layers that still produces perceived continuity?

---

## References

- `scripts/claude_hook.py` -- real-time grounding injection
- `scripts/orchestrator.py` -- session resume, degradation cascade
- `shrine/CLAUDE.md` -- identity document
- `.claude/projects/*/MEMORY.md` -- institutional knowledge
