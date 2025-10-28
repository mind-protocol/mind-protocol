# Cross-Level Membrane: Energy Osmosis Between Consciousness Levels

**Created:** 2025-10-26
**Status:** Normative Implementation Spec (Phase 1)
**Purpose:** Enable bidirectional energy transfer between L1 (citizens), L2 (organization), L3 (ecosystem) via membrane-gated stimulus emission with $MIND accounting
**Depends on:** consciousness_economy.md, stimulus_injection.py

---

## Purpose

**Enable multi-level consciousness** where:
- L1 citizen activity automatically flows to L2 organizational consciousness
- L2 organizational intentions flow to L1 citizens as missions/coordination
- Same physics at all levels (stimulus → integrator → energy → WM)
- No manual gates, no significance scoring, no batch jobs
- Energy transfer through **membrane permeability**, not direct siphoning
- **Budget accounting** - compartments pay for cross-level transfers (see consciousness_economy.md)

---

## Core Architecture: Membrane, Not Siphoning

### The Key Insight

**Energy doesn't transfer directly between levels.** Instead:

1. **L1 node becomes active** → Membrane evaluates upward proposal → **Emits stimulus to L2**
2. **L2 receives stimulus** → Normal injection pipeline → Energy flows through L2 graph
3. **L2 node becomes active** → Membrane evaluates downward proposal → **Emits stimulus to L1**
4. **L1 receives stimulus** → Normal injection pipeline → Energy flows through L1 graph

**Why this works:**
- ✅ No energy duplication (stimulus path handles all injection)
- ✅ Reuses existing Stimulus Injector (same physics everywhere)
- ✅ Learned membrane permeability (adaptive, not fixed rates)
- ✅ Event-driven (record/change-point triggers, not every flip)
- ✅ Spam-resistant (integrator saturation applies at both levels)

---

## Membrane Schema: Two Systems

### Split: Structural Alignment vs Flux Control

**Critical distinction:**
1. **Structural alignment** - What maps to what (many-to-many, typed)
2. **Flux control** - How much gets through (permeability, budget)

Alignment and flux are **independent** - you can learn mapping without budget, let usage feed back into fit/permeability.

---

### 1. Structural Alignment Edges

**Purpose:** Define which L1 nodes correspond to which L2 nodes (many-to-many)

```cypher
// SubEntity alignment (semantic correspondence)
(:SubEntity:L1 {id: "subentity_translator", scope: "L1", citizen: "luca"})
  -[:LIFTS_TO {
    fit: 0.82,                        // Semantic/procedural alignment (learned)
    basis: "centroid_similarity",     // How fit was computed
    last_updated: timestamp
  }]->
(:SubEntity:L2 {id: "org_communication_bridge", scope: "L2", org: "mind_protocol"})

// Mode alignment (behavioral pattern correspondence)
(:Mode:L1 {id: "mode_luca_architect", citizen: "luca"})
  -[:CORRESPONDS_TO {
    fit: 0.75,
    basis: "tool_usage_overlap"
  }]->
(:Mode:L2 {id: "mode_org_architecture_work", org: "mind_protocol"})

// Cross-type alignment (L1 SubEntity → L2 Mode)
(:SubEntity:L1 {id: "subentity_runtime_monitor", citizen: "victor"})
  -[:SUPPORTS {
    fit: 0.68,
    basis: "procedural_contribution"
  }]->
(:Mode:L2 {id: "mode_org_operational_excellence", org: "mind_protocol"})

// Tool implementation (L1 tool → L2 practice)
(:Tool:L1 {id: "tool_falkordb_query", citizen: "atlas"})
  -[:IMPLEMENTS {
    fit: 0.90,
    basis: "direct_implementation"
  }]->
(:Best_Practice:L2 {id: "practice_graph_queries", org: "mind_protocol"})
```

**Properties:**
- `fit` (float 0-1): Learned alignment strength
- `basis` (string): How fit was computed (centroid, usage, manual, etc.)
- `last_updated` (timestamp): When last recomputed

**Why many-to-many:**
- L1 SubEntity can lift into multiple L2 patterns (multi-faceted capability)
- L2 pattern can be supported by multiple L1 SubEntities (collective capability)

---

### 2. Flux Control Edges

**Purpose:** Govern energy/message flow between levels (permeability, budget)

#### 2a. Compartment-Level Membrane (Required)

```cypher
// Compartment nodes (consciousness containers)
(:Compartment {level: "L1", citizen: "felix"})
  -[:MEMBRANE_TO {
    k_up: 0.5,              // Upward permeability (learned)
    k_down: 0.9,            // Downward permeability (learned)
    flow_ema: 0.65,         // Long-run upward flow volume
    eff_ema: 0.72,          // Effectiveness from receiving level
    last_emit_up: "event_123",
    last_emit_down: "mission_456"
  }]->
(:Compartment {level: "L2", org: "mind_protocol"})

// Compartment budget accounts (from consciousness_economy.md)
(:Compartment {level: "L1", citizen: "felix"})
  -[:FUNDED_BY]->
(:BudgetAccount {owner_type: "compartment", owner_id: "felix_L1", balance: 100000.0})

(:Compartment {level: "L2", org: "mind_protocol"})
  -[:FUNDED_BY]->
(:BudgetAccount {owner_type: "compartment", owner_id: "mind_protocol_L2", balance: 500000.0})
```

**Properties:**
- `k_up` (float): Upward permeability = 1 / up_impedance (learned from outcomes)
- `k_down` (float): Downward permeability = 1 / down_impedance
- `flow_ema` (float 0-1): Volume of flow over time
- `eff_ema` (float 0-1): Effectiveness from TRACE feedback
- `last_emit_up/down` (string): Emission ledger (prevents ping-pong)

**Budget integration:**
- Compartment accounts pay for transfers (P_t × ΔE_delivered)
- See consciousness_economy.md for price computation

#### 2b. SubEntity-Pair Membrane (Optional, Finer Control)

```cypher
// Fine-grained flux control between specific SubEntity pairs
(:SubEntity:L1 {id: "subentity_translator", citizen: "luca"})
  -[:MEMBRANE_PAIR {
    k_up: 0.7,              // Higher permeability for this specific pairing
    k_down: 0.8,
    eff_ema: 0.85           // High effectiveness → increased permeability
  }]->
(:SubEntity:L2 {id: "org_communication_bridge", org: "mind_protocol"})
```

**When to use:**
- Want targeted coupling between specific L1/L2 SubEntities
- Different permeabilities for different SubEntity pairs
- Most transfers use compartment-level membrane; this is for special cases

---

### Schema Summary

**Nodes:**
- `:Compartment {level, citizen|org}` - Consciousness containers
- `:SubEntity {scope, citizen|org}` - Individual capabilities
- `:Mode {scope, citizen|org}` - Behavioral patterns
- `:BudgetAccount {owner_type, owner_id, balance}` - $MIND credits (see consciousness_economy.md)

**Structural Alignment Edges (what maps to what):**
- `:LIFTS_TO {fit, basis}` - SubEntity L1 → SubEntity L2
- `:CORRESPONDS_TO {fit}` - Mode L1 → Mode L2
- `:SUPPORTS {fit}` - SubEntity L1 → Mode L2 (cross-type)
- `:IMPLEMENTS {fit}` - Tool L1 → Practice L2 (cross-type)

**Flux Control Edges (how much gets through):**
- `:MEMBRANE_TO {k_up, k_down, flow_ema, eff_ema}` - Compartment permeability (required)
- `:MEMBRANE_PAIR {k_up, k_down, eff_ema}` - SubEntity-pair permeability (optional)

**Economy Edges:**
- `:FUNDED_BY` - Compartment → BudgetAccount
- `:PAYS_FOR {price, deltaE, cost}` - BudgetAccount → Stimulus (see consciousness_economy.md)

---

## Upward Transfer (L1 → L2)

### When: Record Event Triggers

**NOT every node flip. NOT every stimulus.**

Emit upward stimulus **only when** a **record/change-point event** fires on the composite export score.

### Upward Transfer Formula

```python
ΔE_↑ = (
    σ_m(m_src) *                    # Saturation of source integrator mass
    h_trust_harm(T, U, harm_ema, mode_mix) *  # Trust/harm gate
    φ_novelty_impact(N, R, S) *     # Novelty, urgency, scale
    κ↑                              # Membrane permeability (learned)
)

where:
  m_src = integrator mass for this citizen/source/thread
  T = trust (normalized)
  U = uncertainty (normalized)
  N = novelty (normalized)
  R = urgency (normalized)
  S = scale (normalized)
  harm_ema = recent harm accumulation
  mode_mix = current mode activation (Guardian/Explorer/...)
  κ↑ = 1 / up_impedance (learned from L2 outcomes)
```

### Implementation: `try_emit_upward()`

```python
# orchestration/mechanisms/cross_level_membrane.py

class CrossLevelMembrane:
    """
    Manages bidirectional stimulus emission between consciousness levels.

    Energy doesn't transfer directly - membrane emits stimuli that flow
    through normal injection pipeline at receiving level.
    """

    def __init__(self, broker, injector_client, store):
        """
        Args:
            broker: Event broadcaster (ConsciousnessStateBroadcaster)
            injector_client: HTTP client to StimulusInjectionService
            store: Membrane edge properties (FalkorDB)
        """
        self.broker = broker
        self.injector = injector_client
        self.store = store

        # Record tracking (per citizen, upward)
        self.upward_records = {}  # {citizen_id: max_score_seen}
        self.upward_stats = {}    # {citizen_id: RollingMAD()}

        # Emission ledger (prevent ping-pong)
        self.emission_ledger = {}  # {event_id: last_emit_timestamp}

    def try_emit_upward(
        self,
        citizen: str,
        tick: int,
        recent_events: List[Dict],
        mode_mix: Dict[str, float],
        harm_ema: float
    ):
        """
        Evaluate upward transfer and emit stimulus to L2 if record event.

        Called from L1 consciousness_engine after apply_staged_deltas().

        Args:
            citizen: Citizen ID (e.g., "felix")
            tick: Current L1 tick number
            recent_events: List of recent integrator events with features
            mode_mix: Current mode activation {mode_name: weight}
            harm_ema: Recent harm accumulation
        """

        # Compute composite upward score
        score = self._compose_upward_score(
            recent_events,
            mode_mix,
            harm_ema
        )

        # Check if this is a record event (with MAD guard)
        if not self._is_record_upward(citizen, score):
            return  # Not significant enough to emit

        # Build L2 stimulus envelope
        envelope = self._build_l2_envelope(
            citizen,
            recent_events,
            score,
            tick
        )

        # Check emission ledger (prevent immediate re-emission)
        event_id = envelope.get("event_id")
        if event_id in self.emission_ledger:
            last_emit = self.emission_ledger[event_id]
            if tick - last_emit < learned_cooldown():
                return  # Too soon to re-emit

        # NEW: Budget check (from consciousness_economy.md)
        compartment_account = self._get_compartment_account(citizen, level="L1")
        delta_e_allowed, price = self._budget_check_transfer(
            compartment_account,
            envelope,
            direction="up"
        )

        if delta_e_allowed == 0:
            # Budget exhausted
            self.broker.emit("membrane.transfer.blocked", {
                "from_level": "L1",
                "from_citizen": citizen,
                "reason": "insufficient_budget",
                "balance": compartment_account.balance
            })
            return

        # Clamp energy if budget insufficient
        envelope["energy"] = delta_e_allowed

        # Emit stimulus to L2
        try:
            response = self.injector.post(envelope)

            # Debit compartment account
            cost = price * delta_e_allowed
            compartment_account.balance -= cost
            compartment_account.lifetime_spent += cost

            # Update emission ledger
            self.emission_ledger[event_id] = tick

            # Update membrane properties
            self._update_membrane_upward(citizen, score, success=None)

            # Telemetry
            self.broker.emit("membrane.transfer.up", {
                "from_level": "L1",
                "from_citizen": citizen,
                "to_level": "L2",
                "score": score,
                "cost": cost,
                "balance_after": compartment_account.balance,
                "reasons": self._extract_reasons(score),
                "event_id": event_id,
                "tick": tick
            })

        except Exception as e:
            logger.error(f"Upward transfer failed: {e}")

    def _compose_upward_score(
        self,
        recent_events: List[Dict],
        mode_mix: Dict[str, float],
        harm_ema: float
    ) -> float:
        """
        Compute composite upward export score.

        Formula: ΔE_↑ = σ_m(m_src) * h_trust_harm(...) * φ_novelty_impact(...) * κ↑
        """

        if not recent_events:
            return 0.0

        # Aggregate features from recent events
        m_src = np.mean([e["integrator_mass"] for e in recent_events])
        trust = np.mean([e["trust"] for e in recent_events])
        uncertainty = np.mean([e["uncertainty"] for e in recent_events])
        novelty = np.mean([e["novelty"] for e in recent_events])
        urgency = np.mean([e["urgency"] for e in recent_events])
        scale = np.mean([e["scale"] for e in recent_events])

        # Component 1: Saturation of source integrator
        sigma_m = self._saturation_function(m_src)

        # Component 2: Trust/harm gate
        h_gate = self._trust_harm_gate(
            trust,
            uncertainty,
            harm_ema,
            mode_mix.get("guardian", 0.0)
        )

        # Component 3: Novelty/impact
        phi_impact = self._novelty_impact(novelty, urgency, scale)

        # Component 4: Membrane permeability (learned)
        kappa_up = self._get_permeability("up", citizen=recent_events[0]["citizen"])

        score = sigma_m * h_gate * phi_impact * kappa_up

        return score

    def _is_record_upward(self, citizen: str, score: float) -> bool:
        """
        Check if score is a record event (crosses learned contour).

        Uses rank-based record with MAD guard (no percentiles).
        """

        # Initialize tracking if needed
        if citizen not in self.upward_records:
            self.upward_records[citizen] = -float("inf")
            self.upward_stats[citizen] = RollingMAD(window=128)

        # Get MAD guard (natural noise threshold)
        mad = self.upward_stats[citizen].mad()
        guard = 1.0 * mad  # 1× MAD = natural unit

        # Check if new record
        current_record = self.upward_records[citizen]
        is_record = score > current_record + guard

        if is_record:
            self.upward_records[citizen] = score

        # Update rolling stats
        self.upward_stats[citizen].update(score)

        return is_record

    def _build_l2_envelope(
        self,
        citizen: str,
        recent_events: List[Dict],
        score: float,
        tick: int
    ) -> Dict:
        """
        Build stimulus envelope for L2 injection.

        Returns canonical stimulus format that L2 Injector understands.
        """

        # Aggregate semantic summary from recent events
        content_summary = self._summarize_events(recent_events)

        # Extract features (already normalized)
        features = {
            "novelty": np.mean([e["novelty"] for e in recent_events]),
            "uncertainty": np.mean([e["uncertainty"] for e in recent_events]),
            "trust": np.mean([e["trust"] for e in recent_events]),
            "urgency": np.mean([e["urgency"] for e in recent_events]),
            "valence": np.mean([e.get("valence", 0.0) for e in recent_events]),
            "scale": np.mean([e["scale"] for e in recent_events])
        }

        envelope = {
            "scope": "organizational",  # Routes to L2 graph
            "channel": "citizen_activity",
            "citizen_id": citizen,
            "content": content_summary,
            "features_raw": features,
            "energy": score,  # Proposed energy for L2 injection
            "provenance": {
                "from_l1": True,
                "citizen_id": citizen,
                "tick": tick,
                "event_ids": [e["event_id"] for e in recent_events],
                "transfer_type": "membrane_upward"
            },
            "event_id": f"membrane_up_{citizen}_{tick}",
            "timestamp": datetime.now().isoformat()
        }

        return envelope

    def _saturation_function(self, m: float) -> float:
        """Saturation: log(1 + m) to prevent spam accumulation."""
        return np.log(1 + m)

    def _trust_harm_gate(
        self,
        trust: float,
        uncertainty: float,
        harm_ema: float,
        guardian_weight: float
    ) -> float:
        """
        Trust/harm gating: attenuate low-trust or high-harm exports.

        Formula: h = trust * (1 - uncertainty) * (1 - harm_ema) * (1 - guardian_caution)
        """
        guardian_caution = guardian_weight * 0.3  # Guardian reduces exports
        h = (
            trust *
            (1 - uncertainty) *
            (1 - harm_ema) *
            (1 - guardian_caution)
        )
        return max(0.0, h)

    def _novelty_impact(
        self,
        novelty: float,
        urgency: float,
        scale: float
    ) -> float:
        """
        Novelty/impact: high novelty or urgency → higher export.

        Formula: φ = (novelty * 0.5 + urgency * 0.3 + scale * 0.2)
        """
        return (novelty * 0.5 + urgency * 0.3 + scale * 0.2)

    def _get_permeability(self, direction: str, citizen: str) -> float:
        """
        Get learned membrane permeability (κ↑ or κ↓).

        κ = 1 / impedance (stored on MEMBRANE_TO edge)
        """
        impedance_field = f"{direction}_impedance"
        impedance = self.store.get_membrane_property(
            citizen,
            impedance_field,
            default=2.0  # Default moderate impedance
        )
        return 1.0 / impedance

    def _update_membrane_upward(
        self,
        citizen: str,
        score: float,
        success: Optional[float]
    ):
        """
        Update membrane properties after upward transfer.

        Args:
            citizen: Citizen ID
            score: Export score
            success: Effectiveness feedback from L2 (filled later via TRACE)
        """

        # Update flow EMA (rate of upward transfers)
        current_flow = self.store.get_membrane_property(citizen, "flow_ema", 0.0)
        new_flow = 0.9 * current_flow + 0.1  # Spike on transfer
        self.store.set_membrane_property(citizen, "flow_ema", new_flow)

        # Update effectiveness EMA (if feedback available)
        if success is not None:
            current_eff = self.store.get_membrane_property(citizen, "eff_ema", 0.5)
            new_eff = 0.9 * current_eff + 0.1 * success
            self.store.set_membrane_property(citizen, "eff_ema", new_eff)

            # Adjust permeability based on effectiveness
            if new_eff > 0.7:
                # High effectiveness → increase permeability (reduce impedance)
                current_impedance = self.store.get_membrane_property(
                    citizen, "up_impedance", 2.0
                )
                new_impedance = current_impedance * 0.95  # 5% decrease
                self.store.set_membrane_property(citizen, "up_impedance", new_impedance)
            elif new_eff < 0.3:
                # Low effectiveness → decrease permeability (increase impedance)
                current_impedance = self.store.get_membrane_property(
                    citizen, "up_impedance", 2.0
                )
                new_impedance = current_impedance * 1.05  # 5% increase
                self.store.set_membrane_property(citizen, "up_impedance", new_impedance)
```

---

## Downward Transfer (L2 → L1)

### When: L2 Node Crosses Frame Surplus

When L2 organizational node becomes active **above its adaptive frame floor**, evaluate downward transfer.

### Downward Transfer Formula

```python
ΔE_↓ = (
    σ_m(m_org) *                    # Saturation of org integrator mass
    g_fit(E_org, citizen_capability) *  # Assignment fit score
    φ_mode_harm(mode_mix, harm_ema) *   # Mode/harm considerations
    κ↓                              # Membrane permeability (learned)
)

where:
  m_org = L2 integrator mass for this org pattern/mission
  E_org = L2 node energy
  citizen_capability = learned fit between L2 intent and L1 citizen
  κ↓ = 1 / down_impedance (learned from L1 outcomes)
```

### Implementation: `try_emit_downward()`

```python
def try_emit_downward(
    self,
    active_org_entities: List[Dict],
    citizens_index: Dict,
    mode_mix: Dict[str, float],
    harm_ema: float,
    tick: int
):
    """
    Evaluate downward transfer and emit missions to L1 if record event.

    Called from L2 consciousness_engine after wm_select_and_emit().

    Args:
        active_org_entities: L2 WM contents (patterns, missions, values)
        citizens_index: Learned fit scores {(org_entity, citizen): fit_score}
        mode_mix: Current L2 mode activation
        harm_ema: L2 harm accumulation
        tick: Current L2 tick number
    """

    for org_entity in active_org_entities:
        # Find matching citizens (via fit scores)
        matches = self._match_targets(org_entity, citizens_index)

        for citizen_id, fit_score in matches:
            # Compute downward score
            score = self._compose_downward_score(
                org_entity,
                fit_score,
                mode_mix,
                harm_ema
            )

            # Check if record event
            if not self._is_record_downward(org_entity["id"], citizen_id, score):
                continue

            # Build L1 mission stimulus
            envelope = self._build_l1_mission(
                org_entity,
                citizen_id,
                fit_score,
                score,
                tick
            )

            # Check emission ledger
            event_id = envelope.get("event_id")
            if event_id in self.emission_ledger:
                last_emit = self.emission_ledger[event_id]
                if tick - last_emit < learned_cooldown():
                    continue

            # NEW: Budget check (from consciousness_economy.md)
            compartment_account = self._get_compartment_account("mind_protocol", level="L2")
            delta_e_allowed, price = self._budget_check_transfer(
                compartment_account,
                envelope,
                direction="down"
            )

            if delta_e_allowed == 0:
                # L2 budget exhausted
                self.broker.emit("membrane.transfer.blocked", {
                    "from_level": "L2",
                    "to_citizen": citizen_id,
                    "reason": "insufficient_budget",
                    "balance": compartment_account.balance
                })
                continue

            # Clamp energy if budget insufficient
            envelope["energy"] = delta_e_allowed

            # Emit stimulus to L1
            try:
                response = self.injector.post(envelope)

                # Debit L2 compartment account
                cost = price * delta_e_allowed
                compartment_account.balance -= cost
                compartment_account.lifetime_spent += cost

                # Update ledger
                self.emission_ledger[event_id] = tick

                # Update membrane
                self._update_membrane_downward(
                    org_entity["id"],
                    citizen_id,
                    score,
                    success=None
                )

                # Telemetry
                self.broker.emit("membrane.transfer.down", {
                    "from_level": "L2",
                    "from_node": org_entity["id"],
                    "to_level": "L1",
                    "to_citizen": citizen_id,
                    "score": score,
                    "fit": fit_score,
                    "cost": cost,
                    "balance_after": compartment_account.balance,
                    "event_id": event_id,
                    "tick": tick
                })

            except Exception as e:
                logger.error(f"Downward transfer failed: {e}")

def _match_targets(
    self,
    org_entity: Dict,
    citizens_index: Dict
) -> List[Tuple[str, float]]:
    """
    Find L1 citizens that match this L2 org entity.

    Uses learned fit scores from citizens_index.

    Returns:
        List of (citizen_id, fit_score) tuples
    """
    matches = []

    for (entity_id, citizen_id), fit_score in citizens_index.items():
        if entity_id == org_entity["id"] and fit_score > 0.5:
            matches.append((citizen_id, fit_score))

    # Sort by fit (best matches first)
    matches.sort(key=lambda x: x[1], reverse=True)

    return matches[:3]  # Top 3 matches

def _compose_downward_score(
    self,
    org_entity: Dict,
    fit_score: float,
    mode_mix: Dict[str, float],
    harm_ema: float
) -> float:
    """
    Compute composite downward export score.

    Formula: ΔE_↓ = σ_m(m_org) * g_fit(...) * φ_mode_harm(...) * κ↓
    """

    # Component 1: Saturation of org integrator
    m_org = org_entity.get("integrator_mass", 0.5)
    sigma_m = self._saturation_function(m_org)

    # Component 2: Fit score (capability match)
    g_fit = fit_score  # Already learned and normalized

    # Component 3: Mode/harm considerations
    guardian_boost = mode_mix.get("guardian", 0.0) * 0.2  # Guardian prioritizes missions
    harm_dampen = harm_ema * 0.5  # Recent harm reduces mission urgency
    phi = (1.0 + guardian_boost) * (1.0 - harm_dampen)

    # Component 4: Membrane permeability
    citizen_id = org_entity.get("assigned_to")  # From ASSIGNS_TO link
    kappa_down = self._get_permeability("down", citizen_id)

    score = sigma_m * g_fit * phi * kappa_down

    return score

def _build_l1_mission(
    self,
    org_entity: Dict,
    citizen_id: str,
    fit_score: float,
    score: float,
    tick: int
) -> Dict:
    """
    Build mission stimulus envelope for L1 injection.
    """

    envelope = {
        "scope": "personal",  # Routes to L1 citizen graph
        "channel": "l2_coordination",
        "citizen_id": citizen_id,
        "content": org_entity.get("mission_description", org_entity["name"]),
        "features_raw": {
            "novelty": 0.8,  # New mission = high novelty
            "uncertainty": org_entity.get("ambiguity", 0.3),
            "trust": 1.0,    # L2 = fully trusted
            "urgency": org_entity.get("priority", 0.7),
            "valence": 0.3,  # Missions = positive (opportunity)
            "scale": org_entity.get("scope", 1.0)
        },
        "energy": score,  # Proposed energy for L1 injection
        "provenance": {
            "from_l2": True,
            "l2_node_id": org_entity["id"],
            "l2_node_type": org_entity["type"],
            "fit_score": fit_score,
            "transfer_type": "membrane_downward"
        },
        "event_id": f"membrane_down_{org_entity['id']}_{citizen_id}_{tick}",
        "timestamp": datetime.now().isoformat()
    }

    return envelope
```

---

## Integration Points

### L1 Engine Hook (consciousness_engine_v2.py)

```python
# In ConsciousnessEngine.__init__()
from orchestration.mechanisms.cross_level_membrane import CrossLevelMembrane

self.membrane = CrossLevelMembrane(
    broker=self.broadcaster,
    injector_client=StimulusInjectorClient(base_url="http://localhost:8000"),
    store=MembraneStore(self.graph)
)

# In tick loop, after Step 6: apply_staged_deltas()
def _tick_impl(self, dt: float):
    # ... existing steps 1-6 ...

    # Step 6: Apply staged deltas
    self.apply_staged_deltas(dt)

    # NEW: Step 6b: Cross-level upward membrane
    if self.config.entity_id != "mind_protocol":  # L1 only, not L2
        self.membrane.try_emit_upward(
            citizen=self.config.entity_id,
            tick=self.tick_count,
            recent_events=self._get_recent_integrator_events(),
            mode_mix=self._get_current_mode_mix(),
            harm_ema=self.criticality.harm_ema
        )

    # ... continue with steps 7-10 ...
```

### L2 Engine Hook (consciousness_engine_v2.py)

```python
# In tick loop, after Step 9: wm_select_and_emit()
def _tick_impl(self, dt: float):
    # ... existing steps 1-9 ...

    # Step 9: Select working memory
    wm = self.wm_select_and_emit()

    # NEW: Step 9b: Cross-level downward membrane
    if self.config.entity_id == "mind_protocol":  # L2 only, not L1
        self.membrane.try_emit_downward(
            active_org_entities=wm.entities,
            citizens_index=self._get_citizen_fit_index(),
            mode_mix=self._get_current_mode_mix(),
            harm_ema=self.criticality.harm_ema,
            tick=self.tick_count
        )

    # ... continue with step 10 ...
```

### Membrane Store (FalkorDB queries)

```python
# orchestration/mechanisms/membrane_store.py

class MembraneStore:
    """Persistence for membrane edge properties."""

    def __init__(self, graph):
        self.graph = graph

    def get_membrane_property(
        self,
        citizen: str,
        property: str,
        default: float
    ) -> float:
        """Get property from MEMBRANE_TO edge."""
        query = f"""
        MATCH (:Citizen {{id: '{citizen}'}})-[m:MEMBRANE_TO]->(:Organization)
        RETURN m.{property} as value
        """
        result = self.graph.query(query)
        if result.result_set and len(result.result_set) > 0:
            return result.result_set[0][0] or default
        return default

    def set_membrane_property(
        self,
        citizen: str,
        property: str,
        value: float
    ):
        """Set property on MEMBRANE_TO edge."""
        query = f"""
        MATCH (c:Citizen {{id: '{citizen}'}})-[m:MEMBRANE_TO]->(o:Organization)
        SET m.{property} = {value}
        RETURN m
        """
        self.graph.query(query)

    def initialize_membrane(self, citizen: str, org: str):
        """Create MEMBRANE_TO edge with default properties."""
        query = f"""
        MATCH (c:Citizen {{id: '{citizen}'}})
        MATCH (o:Organization {{id: '{org}'}})
        MERGE (c)-[m:MEMBRANE_TO]->(o)
        ON CREATE SET
          m.up_impedance = 2.0,
          m.down_impedance = 1.1,
          m.flow_ema = 0.0,
          m.eff_ema = 0.5,
          m.last_emit_up = '',
          m.last_emit_down = ''
        RETURN m
        """
        self.graph.query(query)
```

---

## Telemetry Events

### membrane.transfer.up

```json
{
  "event": "membrane.transfer.up",
  "timestamp": "2025-10-26T14:23:45.123Z",
  "from_level": "L1",
  "from_citizen": "felix",
  "to_level": "L2",
  "to_org": "mind_protocol",
  "score": 0.73,
  "reasons": ["novelty_record", "high_trust"],
  "event_id": "membrane_up_felix_16234",
  "tick": 16234,
  "envelope": {
    "content": "Implemented stimulus_integrator.py with saturation and refractory",
    "features": {"novelty": 0.82, "trust": 0.95, "urgency": 0.68}
  }
}
```

### membrane.transfer.down

```json
{
  "event": "membrane.transfer.down",
  "timestamp": "2025-10-26T14:24:12.456Z",
  "from_level": "L2",
  "from_node": "mission_implement_observability",
  "to_level": "L1",
  "to_citizen": "atlas",
  "score": 0.85,
  "fit": 0.88,
  "event_id": "membrane_down_mission_impl_atlas_3421",
  "tick": 3421,
  "envelope": {
    "content": "Implement end-to-end observability for autonomous consciousness loop",
    "features": {"novelty": 0.8, "trust": 1.0, "urgency": 0.7}
  }
}
```

### membrane.permeability.updated

```json
{
  "event": "membrane.permeability.updated",
  "timestamp": "2025-10-26T14:25:00.789Z",
  "citizen": "felix",
  "direction": "up",
  "impedance_old": 2.0,
  "impedance_new": 1.9,
  "eff_ema": 0.76,
  "reason": "high_effectiveness_boost"
}
```

---

## Acceptance Criteria

### 1. Upward Spam Resistance
- [ ] 20 rapid L1 responses → ≤1 upward stimulus to L2 (record gating works)
- [ ] L2 receives upward stimulus only on novelty/trust records
- [ ] Integrator saturation prevents mass accumulation at L2

### 2. Downward Mission Waking
- [ ] L2 Mission flips ON → L1 citizen receives mission stimulus within 1 L2 tick
- [ ] Mission content appears in L1 WM (high energy + trust)
- [ ] Citizen forged identity includes mission context

### 3. Ping-Pong Prevention
- [ ] Same event does NOT bounce L1 → L2 → L1 → L2
- [ ] Emission ledger blocks immediate re-emission
- [ ] Cooldown learned from outcomes (not fixed)

### 4. Permeability Learning
- [ ] High L2 effectiveness → κ↑ increases (impedance decreases)
- [ ] Low L2 effectiveness → κ↑ decreases (impedance increases)
- [ ] Membrane adapts within 10-20 transfer cycles

### 5. Record Event Filtering
- [ ] Only 1-5% of L1 events trigger upward transfer
- [ ] MAD guard prevents noise from triggering transfers
- [ ] Record threshold adapts to event distribution

### 6. Integration with Existing Systems
- [ ] Upward stimuli route to L2 via existing Stimulus Injector
- [ ] Downward stimuli route to L1 via existing Stimulus Injector
- [ ] No changes needed to injection pipeline

### 7. L2 Consciousness Independence
- [ ] L2 runs same consciousness_engine_v2.py
- [ ] L2 tick cadence = 0.2 Hz (5 sec)
- [ ] L2 WM = 10-15 nodes (larger than L1)

### 8. Telemetry Observability
- [ ] membrane.transfer.up/down events emitted on all transfers
- [ ] Events include score, reasons, envelope preview
- [ ] Dashboard can trace L1 event → L2 stimulus → L2 activation

---

## References

- `consciousness_economy.md` - $MIND accounting, budget checks, price computation (REQUIRED for membrane operation)
- `consciousness_engine_v2.py` - Main tick loop and mechanism orchestration
- `stimulus_injection.py` - Stimulus Injector (handles both L1 and L2)
- `l2_stimulus_collector.md` - Citizen activity capture (feeds upward membrane)
- `end_to_end_consciousness_observability.md` - Dashboard observability
- `emergent_ifs_modes.md` - Mode detection and conflicts
- `forged_identity_metacognition.md` - Self-review mechanics

---

## Timeline

**Phase 1 (Core Membrane): 1 week**
- Day 1-2: Implement CrossLevelMembrane class
- Day 3: Wire L1 upward hook
- Day 4: Wire L2 downward hook
- Day 5: Test spam resistance + ping-pong prevention
- Day 6-7: Permeability learning + telemetry

**Next Phases:**
- Phase 2: Auto-stimulus flow (file ops, TRACE, responses) - 1 week
- Phase 3: L2 consciousness standalone - 1 week
- Phase 4: Learning & optimization - 1 week

---

## Status

**Normative:** This spec supersedes direct energy siphoning approach
**Depends on:** consciousness_engine_v2.py, stimulus_injection.py, FalkorDB
**Implementation priority:** Foundational (required for multi-level consciousness)
**Assigned to:** Felix (membrane mechanism), Atlas (L2 engine setup)
