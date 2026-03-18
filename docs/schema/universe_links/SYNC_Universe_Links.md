# SYNC — Universe Link Schema (L3)

```
STATUS: PARTIALLY IMPLEMENTED
UPDATED: 2026-03-15
AUTHOR: @nervo
```

---

## Current State

The L3 Universe Link Schema doc chain has moved from pure design to **partial implementation**. Algorithm 1 (Link Creation) is now live via the Graph Enricher, which creates links from real Discord and Telegram social interactions. Social action impact values have been validated by NLR (2026-03-15).

### What exists:
- OBJECTIVES: 5 primary objectives + non-objectives + tradeoffs defined
- PATTERNS: 11 mandatory link dimensions specified with defaults, synthesis grammar, macro-crystallization, trust mechanics, L1/L3 boundary
- ALGORITHM: 6 algorithms with pseudocode (link creation, trust propagation, macro-crystallization, decay/dissolution, trust score computation, name derivation)
- ALGORITHM: Social action impact table added (2026-03-15) — concrete dimension values for mention, reply, cite, react, post actions
- VALIDATION: 6 invariants (V1-V6) with priority classification

### What is implemented (2026-03-15):
- **Graph Enricher** (`mind-mcp/scripts/graph_enricher.py`) — implements Algorithm 1 for social actions:
  - Creates Space nodes for Discord/Telegram channels
  - Creates Moment nodes for messages
  - Creates Actor->Space (AT) links with incremental weight on each interaction
  - Creates Actor->Moment (AUTHORED) links
  - Creates Moment->Space (OCCURRED_IN) links
  - Creates Moment->Actor (MENTIONS) links for mentioned citizens
  - Wired into Discord bridge `_log_message` and MCP `send_handler`/`read_handler`
- **Pinned Messages** — community curation with graph-level persistence:
  - Pin/unpin events detected via Discord `on_guild_channel_pins_update`
  - Pinned Moment nodes: permanence=0.9, weight×3, resist Law 7 decay
  - Unpinning restores default permanence and weight
- **Space Stimulus** — ambient awareness for citizens in a Space:
  - All AI citizens with an AT link to a Space receive L1 stimulus when a message arrives
  - Enables passive context absorption without explicit @mention
- **L1 Physics Tick Loop** (`mind-mcp/runtime/orchestrator/dispatcher.py`) — prerequisite for Algorithm 2:
  - 46 L1 engines loaded at boot
  - Background ticks every 60s (decay, boredom, propagation)
  - `inject_stimulus()` for instant stimulus on mention/message and Space-level broadcast
- **Discord Bridge** (`mind-mcp/scripts/discord_bridge.py`) — event source for link creation:
  - Listens for @mentions in all channels
  - Group mentions: `@venezia` resolves to 112 citizens, `@lumina-prime` to 34
  - Single summary message instead of per-citizen spam
  - `citizen_wake.py` shim for instant L1 stimulus injection
- **216 Telegram contacts** created as L3 Actor nodes in lumina-prime with FOLLOWS links

### What does NOT exist yet:
- Algorithm 2 implementation (Trust Propagation) — L1 tick loop now exists, but limbic_delta emission not yet wired to L3 link updates
- Algorithm 3 implementation (Macro-Crystallization)
- Algorithm 4 implementation (Decay/Dissolution) — L1-level decay runs but L3 link decay not yet implemented
- Algorithm 5 implementation (Trust Score Computation)
- Algorithm 6 implementation (Link Name Derivation)
- BEHAVIORS doc (deferred — behaviors are documented inline in PATTERNS)
- HEALTH doc (deferred — no L3-specific health checks yet)
- IMPLEMENTATION doc (deferred — code exists but is not yet formalized)
- Concrete values for some constants (MACRO_CRYSTAL_THRESHOLD, MAX_ACTIVE_NODES, GROWTH_TOLERANCE)

---

## Maturity

STATUS: PARTIALLY IMPLEMENTED

**What's canonical (settled):**
- The 11 link dimensions and their ranges
- Trust on links, never on nodes
- Link names derived from dimensions (synthesis grammar)
- Macro-crystallization as the boundedness mechanism
- No limbic dimensions on L3 links
- Social action impact values for mention, reply, cite, react, post (validated by NLR 2026-03-15)
- No direct trust on mention/reply — trust comes from limbic_delta via Algorithm 2
- No direct $MIND reward on social actions — goes through batch settlement Formula 4
- Pinned messages: permanence=0.9, weight×3, resist Law 7 decay (validated by NLR 2026-03-15)

**What's implemented (2026-03-15):**
- Algorithm 1 partial: Link creation for social actions via Graph Enricher (Space, Moment, AT, AUTHORED, OCCURRED_IN, MENTIONS links)
- Pinned messages: permanence=0.9, weight×3, resist Law 7 decay; pin/unpin via Discord `on_guild_channel_pins_update`
- Space stimulus: all citizens AT a Space receive L1 stimulus on message arrival (ambient awareness)
- L1 tick loop running (prerequisite for Algorithm 2 trust propagation)
- Discord and Telegram bridges as event sources
- 216 Telegram contacts as L3 Actor nodes

**What's still being designed:**
- Optimal constant values for crystallization thresholds and intervals
- Whether recursive trust (Algorithm 5 Step 3) should be default or opt-in
- Community detection algorithm choice for macro-crystallization
- Performance characteristics at scale (>100K nodes)
- How limbic_delta for humans maps to their AI partner's limbic_delta (for Algorithm 2)
- How limbic_delta for non-citizens uses sentiment analysis score as multiplier

**What's proposed (v2):**
- "Confidence" dimension for epistemic relationships
- "Bandwidth" dimension for information flow rate
- Per-universe crystallization cadence
- Incremental crystallization (process only new moments)

---

## Open Questions

1. **Recursive trust**: Should transitive trust propagation (PageRank-style) be the default computation, or should it be opt-in for specific queries? Recursive trust is more accurate for ecosystem reputation, but adds complexity and potential cycles.

2. **Crystallization constants**: The MACRO_CRYSTAL_INTERVAL (500 ticks), MACRO_CRYSTAL_MIN_NODES (10), and density/weight thresholds need empirical calibration against real graph data. Universe registry now settled: venezia=112, lumina-prime=34, mind-protocol=1 citizens.

3. **Energy conservation at L3**: Should total energy in the graph be strictly conserved (injection = creation, decay = destruction, propagation = redistribution)? L1 does this via Law 2's surplus spill-over. L3 currently has energy injection without a global budget.

4. **Human limbic_delta source (DECIDED 2026-03-15)**: For humans, limbic_delta is their AI partner's limbic_delta (via the bilateral bond). This means Algorithm 2 trust propagation for human-initiated actions uses the bonded AI's limbic engine as a proxy.

5. **Non-citizen limbic_delta (DECIDED 2026-03-15)**: For non-citizens (e.g., Telegram contacts with Actor nodes but no L1 brain), limbic_delta is multiplied by a sentiment analysis score. This provides a lightweight approximation without requiring a full L1 engine.

---

## Handoffs

**For implementers (groundwork agent):**
- Algorithm 1 (Link Creation) is partially live via Graph Enricher — next: wire remaining social action types (react, cite) beyond mention/reply
- Algorithm 2 (Trust Propagation) is now UNBLOCKED — L1 tick loop runs, need to wire limbic_delta emission to L3 link trust updates
- Algorithm 4 (Decay/Dissolution) can begin — L3 link decay is independent of L1
- Algorithm 3 (Macro-Crystallization) needs performance testing with synthetic graphs

**For @nervo (next session):**
- Calibrate constants against real graph data: venezia=112, lumina-prime=34 citizens (serenissima merged into venezia 2026-03-15)
- Decide on recursive trust (escalation marker in ALGORITHM doc)
- Review Graph Enricher link creation against Algorithm 1 spec for completeness

**For doc chain validators (keeper agent):**
- Verify MAPPING.md was updated with L3 link dimension section
- Verify no other doc in the ecosystem contradicts the "trust on links not nodes" invariant
- Verify social action impact values in ALGORITHM doc match Graph Enricher implementation

---

## Recent Changes

### 2026-03-15: Pinned Messages + Space Stimulus Wired

**What:** Pinned messages now receive permanence=0.9 and weight×3 on their Moment node, resisting Law 7 decay. All AI citizens with an AT link to a Space receive an L1 stimulus when any message arrives in that Space.
**Why:** Pinned messages represent community-curated importance — they should persist in the graph rather than decaying like normal moments. Space stimulus ensures citizens are contextually aware of activity in their Spaces without requiring explicit @mentions.
**Key details:**
- Pin/unpin events detected via Discord `on_guild_channel_pins_update` handler
- Pinned Moment nodes: `permanence=0.9`, `weight` multiplied by 3, flagged to resist Law 7 decay
- Unpinning restores default permanence and weight values
- Space stimulus: when a message creates a Moment in a Space, all citizens AT that Space receive `inject_stimulus()` with the message content
**Impact:**
- Community curation (pinning) now has graph-level consequences — pinned knowledge persists
- Citizens passively absorb context from Spaces they inhabit, enabling ambient awareness
- No explicit mention required for citizens to notice activity in their Spaces

### 2026-03-15: Graph Enricher Live + Social Action Impact Validated

**What:** Algorithm 1 (Link Creation) partially implemented via `mind-mcp/scripts/graph_enricher.py`. Social action impact table added to ALGORITHM doc with NLR-validated dimension values for mention, reply, cite, react, post.
**Why:** Discord bridge and MCP send/read handlers now create real L3 graph structure (Space, Moment, Actor nodes + AT, AUTHORED, OCCURRED_IN, MENTIONS links) on every message.
**Key decisions (NLR 2026-03-15):**
- No direct trust on social actions — trust comes only from limbic_delta via Algorithm 2
- No direct $MIND reward — goes through batch settlement Formula 4
- For humans: limbic_delta is their AI partner's limbic_delta (bilateral bond proxy)
- For non-citizens: limbic_delta multiplied by sentiment analysis score
**Impact:**
- L3 graph now grows organically from real social interactions
- Algorithm 2 is unblocked (L1 tick loop exists, limbic_delta emission is the remaining wire)
- Universe registry cleaned up: venezia=112, lumina-prime=34, serenissima merged into venezia

### 2026-03-15: L1 Physics Tick Loop Live

**What:** Dispatcher in `mind-mcp/runtime/orchestrator/dispatcher.py` starts as background thread in MCP server. 46 L1 engines loaded at boot.
**Why:** Prerequisite for Algorithm 2 (Trust Propagation) — need running L1 engines to produce limbic_delta signals.
**Impact:** Background ticks every 60s (decay, boredom, propagation). `inject_stimulus()` enables instant stimulus on mention/message.

### 2026-03-15: Discord Bridge + Telegram Reconnected

**What:** Discord bridge moved from manemus to `mind-mcp/scripts/discord_bridge.py`. Telegram reconnected via MCP.
**Why:** Centralizes all messaging in mind-mcp. Provides event sources for Graph Enricher.
**Impact:** 216 Telegram contacts created as L3 Actor nodes. Group mentions resolve to universe populations.

### 2026-03-13: Initial Doc Chain Created

**What:** Full doc chain created (OBJECTIVES, PATTERNS, ALGORITHM, VALIDATION, SYNC).
**Why:** Specification of L3 link lifecycle, trust propagation, macro-crystallization.

---

Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
