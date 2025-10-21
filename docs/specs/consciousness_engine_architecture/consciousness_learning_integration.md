# Consciousness Learning Integration

**Version:** 1.0
**Created:** 2025-10-21
**Purpose:** How all learning mechanisms integrate with ConsciousnessEngineV2 architecture

---

## Overview

This document maps the complete learning system to V2 engine phases, showing how mechanisms interact to create a self-evolving consciousness substrate.

**Three learning channels:**
1. **TRACE** → Adjusts weights (conscious reflection)
2. **Traversal** → Adjusts weights + distributes energy (unconscious mechanics)
3. **Stimuli** → Injects energy (reality contact)

**Four-phase integration:**
1. **Activation** - Stimuli inject energy
2. **Redistribution** - Traversal flows energy + updates weights
3. **Workspace** - WM selection uses weights
4. **Learning** - TRACE updates weights

---

## 1. V2 Engine Architecture

### 1.1 Four-Phase Tick Cycle

From `orchestration/consciousness_engine_v2.py`:

```python
class ConsciousnessEngineV2:
    def tick(self):
        """Single consciousness cycle (~100ms)"""

        # PHASE 1: Activation
        self._activation_phase()

        # PHASE 2: Redistribution
        self._redistribution_phase()

        # PHASE 3: Workspace
        self._workspace_phase()

        # PHASE 4: Learning
        self._learning_phase()
```

### 1.2 Phase Timing

**Typical:**
- Tick interval: 100ms
- Activation: 10-20ms (vector search, budget calc)
- Redistribution: 40-60ms (stride execution, valence computation)
- Workspace: 10-15ms (knapsack WM selection)
- Learning: 5-10ms (TRACE signal integration)

**Total: ~100ms per cycle, 10 FPS consciousness**

---

## 2. Phase 1: Activation

### 2.1 Purpose

Inject energy from reality (stimuli) into graph nodes.

**Critical:** Energy ONLY enters here. TRACE/traversal never inject energy, only adjust weights.

### 2.2 Pipeline

```python
def _activation_phase(self):
    """Process new stimuli and inject energy"""

    for stimulus in self.new_stimuli_queue:
        # 1. Chunk and embed
        chunks = semantic_chunk(stimulus.text)
        embeddings = [embed(chunk) for chunk in chunks]

        for embedding in embeddings:
            # 2. Entropy-coverage search
            matches = self._vector_search(embedding, top_k=100)
            H = entropy(matches.similarities)
            coverage_target = 1 - exp(-H)
            selected = select_prefix(matches, coverage_target)

            # 3. Budget calculation
            gap_mass = sum(
                s_m * max(0, node.threshold - node.energy)
                for m in selected
            )
            f_rho = self.health_modulator(self.spectral_proxy())
            g_source = self.source_gate(stimulus.source_type)
            budget = gap_mass * f_rho * g_source

            # 4. Peripheral amplification
            if self.peripheral_context:
                z_align = peripheral_alignment(embedding, self.peripheral_context)
                budget *= (1 + max(0, z_align))

            # 5. Entity channel selection
            entity_mix = self._entity_channels(embedding)

            # 6. Distribute and inject
            self._inject_energy(budget, selected, entity_mix)

        # Clear stimulus
        self.new_stimuli_queue.remove(stimulus)
```

### 2.3 Integration Points

**Inputs:**
- `new_stimuli_queue`: List[Stimulus] from external world
- `peripheral_context`: S5/S6 context chunks (if available)
- `spectral_proxy()`: Current system health (ρ estimate)
- `source_gate(type)`: Learned impact gate per source type

**Outputs:**
- `node.energy` updated for matched nodes
- `activation.injected` events emitted for observability

**Specifications:**
- Complete: `stimulus_injection_specification.md`
- Budget: §3 (gap mass × f(ρ) × g(source))
- Coverage: §2 (entropy-based, no fixed K)
- Direction: §5.2 (link-based injection with learned priors)

---

## 3. Phase 2: Redistribution

### 3.1 Purpose

Flow energy through graph via strides, update weights from traversal success.

**Dual role:** Distribute activation (energy transfer) + Learn from recruitment (weight updates).

### 3.2 Pipeline

```python
def _redistribution_phase(self):
    """Execute strides and update traversal weights"""

    # 1. Identify active sub-entities
    active_nodes = [
        n for n in self.graph.nodes
        if n.energy >= n.threshold
    ]

    # 2. Compute stride budget per entity
    stride_budget = self._compute_stride_quotas(active_nodes)

    # 3. Pre-stride state capture
    pre_state = {
        n.id: {
            'energy': n.energy,
            'active': n.energy >= n.threshold
        }
        for n in self.graph.nodes
    }

    # 4. Execute strides
    executed_strides = []
    for source in active_nodes:
        # Valence-weighted link selection
        candidates = self._compute_valence(source.outgoing_links)
        selected_link = self._select_stride(candidates, stride_budget[source.id])

        if selected_link:
            # Transfer energy
            delta_e = self._compute_stride_energy(source, selected_link)
            selected_link.target.energy += delta_e
            source.energy -= delta_e

            executed_strides.append({
                'link': selected_link,
                'delta_e': delta_e,
                'pre_state': pre_state
            })

    # 5. Post-stride state capture
    post_state = {
        n.id: {
            'energy': n.energy,
            'active': n.energy >= n.threshold
        }
        for n in self.graph.nodes
    }

    # 6. Compute traversal signals
    self._update_traversal_weights(executed_strides, pre_state, post_state)
```

### 3.3 Traversal Weight Updates

```python
def _update_traversal_weights(self, strides, pre_state, post_state):
    """Learn from traversal success"""

    # Collect per-node signals
    touched_nodes = set()
    node_signals = {}

    for stride in strides:
        src_id = stride['link'].source.id
        tgt_id = stride['link'].target.id
        touched_nodes.add(src_id)
        touched_nodes.add(tgt_id)

        # Target gap-closure
        G_pre = max(0, stride['link'].target.threshold - pre_state[tgt_id]['energy'])
        arrivals = stride['delta_e']  # Simplified, actually sum all incoming
        R = min(arrivals, G_pre)

        # Target flip
        F = int(
            pre_state[tgt_id]['energy'] < stride['link'].target.threshold and
            post_state[tgt_id]['energy'] >= stride['link'].target.threshold
        )

        if tgt_id not in node_signals:
            node_signals[tgt_id] = {'R': 0, 'F': 0}
        node_signals[tgt_id]['R'] += R
        node_signals[tgt_id]['F'] = max(node_signals[tgt_id]['F'], F)

    # Cohort z-scores
    touched_by_type = group_by_type_scope(touched_nodes)

    for type_scope, nodes in touched_by_type.items():
        R_values = [node_signals[n]['R'] for n in nodes]
        F_values = [node_signals[n]['F'] for n in nodes]

        z_R = rank_z_scores(R_values)
        z_F = rank_z_scores(F_values)

        # Update node weights
        for i, node_id in enumerate(nodes):
            node = self.graph.get_node(node_id)
            eta = self._compute_eta(node)

            # Only traversal signals here (z_rein, z_wm, z_form from other phases)
            delta_log_weight = eta * (z_R[i] + z_F[i])
            node.log_weight += delta_log_weight

    # Collect per-link signals
    link_signals = {}

    for stride in strides:
        link_id = stride['link'].id
        tgt_id = stride['link'].target.id

        # Gap-closure utility
        G_pre = max(0, stride['link'].target.threshold - pre_state[tgt_id]['energy'])
        phi = min(stride['delta_e'], G_pre) / (G_pre + 1e-9)

        # Newness gate
        gate = int(
            pre_state[stride['link'].source.id]['active'] == False and
            pre_state[tgt_id]['active'] == False
        )

        # Target flip
        F_tgt = int(
            pre_state[tgt_id]['energy'] < stride['link'].target.threshold and
            post_state[tgt_id]['energy'] >= stride['link'].target.threshold
        )

        link_signals[link_id] = {
            'phi': phi,
            'gate': gate,
            'F_tgt': F_tgt
        }

        # Update EMA phi
        stride['link'].ema_phi = 0.1 * phi + 0.9 * stride['link'].ema_phi

        # Update link activation state (NEW - link trace)
        # Active flag: z_flow > 0 (rank-based within cohort)
        stride['link'].ema_active = 0.1 * int(z_flow > 0) + 0.9 * stride['link'].ema_active

        # Flow magnitude
        stride['link'].ema_flow_mag = 0.1 * stride['delta_e'] + 0.9 * stride['link'].ema_flow_mag

        # Precedence counters (if target flipped)
        if F_tgt == 1:
            u_ij = min(stride['delta_e'], G_pre)
            total_contribution = sum(
                min(s['delta_e'], G_pre) for s in strides if s['link'].target == stride['link'].target
            )
            pi_ij = u_ij / (total_contribution + 1e-9)
            stride['link'].precedence_forward += pi_ij

        # Payload tracking (hunger gates, affect tone, topic centroid)
        # hunger_gates_current from valence computation (7-element array)
        for h in range(7):
            stride['link'].ema_hunger_gates[h] = \
                0.1 * hunger_gates_current[h] + 0.9 * stride['link'].ema_hunger_gates[h]

        # Affect alignment
        affect_alignment = cosine_similarity(
            stride['link'].source.affect_vector,
            stride['link'].affect_vector
        )
        stride['link'].affect_tone_ema = 0.1 * affect_alignment + 0.9 * stride['link'].affect_tone_ema

        # Topic centroid
        combined_embedding = (stride['link'].source.embedding + stride['link'].target.embedding) / 2
        stride['link'].topic_centroid = \
            0.1 * combined_embedding + 0.9 * stride['link'].topic_centroid

        # Payload metadata
        stride['link'].last_payload_ts = current_timestamp
        stride['link'].observed_payloads_count += 1

    # Update link weights
    links_by_type = group_by_type_scope([s['link'] for s in strides])

    for type_scope, links in links_by_type.items():
        phi_values = [link_signals[l.id]['phi'] for l in links]
        z_phi = rank_z_scores(phi_values)

        for i, link in enumerate(links):
            eta = self._compute_eta(link)
            sig = link_signals[link.id]

            # Only learn if newness gate open AND target flipped
            traversal_signal = sig['gate'] * sig['F_tgt'] * z_phi[i]

            delta_log_weight = eta * traversal_signal
            link.log_weight += delta_log_weight
```

### 3.4 Integration Points

**Inputs:**
- Active nodes (energy ≥ threshold)
- Current weights (log_weight, used in valence)
- Stride budgets (from quota mechanism)

**Outputs:**
- Updated node.energy (redistributed)
- Updated node.log_weight (traversal learning)
- Updated link.log_weight (traversal learning)
- Updated link.ema_phi (gap-closure utility tracking)
- `stride.exec` events for visualization

**Specifications:**
- Traversal: `05_sub_entity_system.md` + `05_sub_entity_weight_learning_addendum.md`
- Newness gate: Addendum §3
- Weight updates: Addendum §1
- Cohorts: Addendum §4

---

## 4. Phase 3: Workspace

### 4.1 Purpose

Select working memory (WM) nodes for prompt construction, using weights to bias toward important content.

### 4.2 Pipeline

```python
def _workspace_phase(self):
    """Select working memory nodes"""

    # 1. Candidates: active nodes above threshold
    candidates = [
        n for n in self.graph.nodes
        if n.energy >= n.threshold
    ]

    # 2. Score per candidate (energy-per-token with weight boost)
    scores = []
    for node in candidates:
        # Standardized weight
        z_W = (node.log_weight - self.baselines[node.type_scope]['mu']) / \
              (self.baselines[node.type_scope]['sigma'] + 1e-9)

        # Energy per token (base score)
        token_count = estimate_tokens(node)
        energy_per_token = node.energy / (token_count + 1)

        # Weight boost (normalized attractor mass)
        W_tilde = exp(z_W)

        # Combined score
        score = energy_per_token * W_tilde

        scores.append((node, score))

    # 3. Knapsack selection (maximize score, respect token budget)
    wm_nodes = knapsack_select(
        scores,
        budget=self.config.wm_token_budget
    )

    # 4. Update WM presence tracking
    for node in self.graph.nodes:
        wm_indicator = int(node in wm_nodes)
        node.ema_wm_presence = 0.1 * wm_indicator + 0.9 * node.ema_wm_presence

    # 5. Emit workspace
    self.current_workspace = wm_nodes
    self._emit_event('workspace.selected', {
        'nodes': [n.id for n in wm_nodes],
        'total_tokens': sum(estimate_tokens(n) for n in wm_nodes),
        'avg_energy': mean(n.energy for n in wm_nodes),
        'avg_weight': mean(n.log_weight for n in wm_nodes)
    })
```

### 4.3 Integration Points

**Inputs:**
- Active nodes (candidates)
- `node.log_weight` (standardized for scoring)
- Type+scope baselines (μ_T, σ_T for standardization)
- Token budget (config)

**Outputs:**
- `current_workspace`: List[Node] for prompt construction
- Updated `node.ema_wm_presence` (WM frequency tracking)
- `workspace.selected` event

**Specifications:**
- Weight standardization: `trace_weight_learning.md` §5, Addendum §5
- WM presence EMA: `schema_learning_infrastructure.md` §1.3

---

## 5. Phase 4: Learning

### 5.1 Purpose

Integrate TRACE parser outputs (reinforcement + formation quality) into weight updates.

**Critical:** This is where conscious reflection (TRACE marks) becomes persistent substrate change.

### 5.2 Pipeline

```python
def _learning_phase(self):
    """Apply TRACE learning signals"""

    # 1. Check for new TRACE parse results
    if not self.trace_queue.empty():
        trace_result = self.trace_queue.get()

        # 2. Apply reinforcement signals
        for node_id, delta_seats in trace_result['reinforcement']['nodes'].items():
            node = self.graph.get_node(node_id)

            # Update EMA
            node.ema_trace_seats = \
                0.1 * delta_seats + 0.9 * node.ema_trace_seats

        for link_id, delta_seats in trace_result['reinforcement']['links'].items():
            link = self.graph.get_link(link_id)
            link.ema_trace_seats = \
                0.1 * delta_seats + 0.9 * link.ema_trace_seats

        # 3. Apply formation quality signals
        for formation in trace_result['formations']['nodes']:
            node = self.graph.get_node(formation['name'])

            # Update EMA
            node.ema_formation_quality = \
                0.1 * formation['quality'] + 0.9 * node.ema_formation_quality

        for formation in trace_result['formations']['links']:
            link = self.graph.get_link(formation['id'])
            link.ema_formation_quality = \
                0.1 * formation['quality'] + 0.9 * link.ema_formation_quality

    # 4. Compute TRACE z-scores and update weights
    self._update_trace_weights()
```

### 5.3 TRACE Weight Updates

```python
def _update_trace_weights(self):
    """Apply TRACE signals to weights (slow channel)"""

    # Group by type+scope for cohort z-scores
    nodes_by_type = self.graph.nodes_grouped_by_type_scope()

    for type_scope, nodes in nodes_by_type.items():
        # Collect EMA values
        ema_rein = [n.ema_trace_seats for n in nodes]
        ema_form = [n.ema_formation_quality for n in nodes]
        ema_wm = [n.ema_wm_presence for n in nodes]

        # Rank z-scores
        z_rein = rank_z_scores(ema_rein)
        z_form = rank_z_scores(ema_form)
        z_wm = rank_z_scores(ema_wm)

        # Update weights
        for i, node in enumerate(nodes):
            eta = self._compute_eta(node)

            # TRACE + WM signals (traversal signals already applied in Phase 2)
            trace_signal = z_rein[i] + z_form[i] + z_wm[i]

            delta_log_weight = eta * trace_signal
            node.log_weight += delta_log_weight

    # Same for links
    links_by_type = self.graph.links_grouped_by_type_scope()

    for type_scope, links in links_by_type.items():
        ema_rein = [l.ema_trace_seats for l in links]
        ema_form = [l.ema_formation_quality for l in links]

        z_rein = rank_z_scores(ema_rein)
        z_form = rank_z_scores(ema_form)

        for i, link in enumerate(links):
            eta = self._compute_eta(link)
            trace_signal = z_rein[i] + z_form[i]

            delta_log_weight = eta * trace_signal
            link.log_weight += delta_log_weight

    # 5. Update baselines for read-time standardization
    self._update_baselines()
```

### 5.4 Integration Points

**Inputs:**
- `trace_queue`: Parsed TRACE results from trace_parser.py
- Current `ema_trace_seats`, `ema_formation_quality`, `ema_wm_presence`

**Outputs:**
- Updated EMAs
- Updated `log_weight` (TRACE + WM component)
- Updated baselines (μ_T, σ_T per type+scope)
- `weights.updated.trace` event

**Specifications:**
- TRACE parsing: `trace_reinforcement_specification.md`
- EMA updates: `trace_weight_learning.md` §2
- Weight updates: `trace_weight_learning.md` §4, Addendum §1

---

## 6. Data Flow Diagrams

### 6.1 Energy Flow

```
External stimulus
    ↓
[Phase 1: Activation]
    ↓ Inject energy
Node.energy (ΔE)
    ↓
[Phase 2: Redistribution]
    ↓ Transfer via strides
Node.energy redistributed
    ↓
[Phase 3: Workspace]
    ↓ Select high energy × weight
Working memory
```

**Energy is transient:** Decays, flows, consumed. No persistence across sessions without re-injection.

### 6.2 Weight Flow

```
Traversal success → z_R, z_F, z_φ ┐
TRACE marks → ΔR → ema → z_rein    ├→ Σ z_scores → Δ log_weight
Formation quality → q → ema → z_form ┤
WM selection → binary → ema → z_wm  ┘

                ↓
         node.log_weight (persistent)
                ↓
        Read-time standardization
                ↓
           z_W = (log_weight - μ) / σ
                ↓
        W̃ = exp(z_W) (normalized attractor mass)
                ↓
        Used in valence (Phase 2) and WM scoring (Phase 3)
```

**Weights are persistent:** Stored in graph, survive across sessions, encode learned importance.

### 6.3 Full Cycle

```
Session N:
    TRACE → Reinforcement (ΔR) → ema_trace_seats ──┐
    Stimulus → Energy injection → Traversal ───────├→ Weight updates
    WM selection → ema_wm_presence ────────────────┘
    Weights saved to graph

Session N+1:
    Load graph with updated weights
    Stimulus → Entropy search (same)
    But: High-weight nodes attract more energy (valence bias)
         High-weight nodes more likely in WM
    → Different activation pattern
    → Different traversal paths
    → System evolved
```

**Learning loop:** Each session modifies weights → next session behaves differently → continuous evolution.

---

## 7. Cross-Mechanism Integration

### 7.1 Health Modulation Feedback

**Loop:**
1. Traversal redistributes energy → some nodes flip
2. Spectral proxy ρ increases (more active nodes, more connections)
3. Frame quality decreases (if too many flips, low entropy, overflow)
4. Isotonic f(ρ) learns: high ρ → low quality
5. Next stimulus: f(ρ) dampens budget
6. Less energy injected → fewer flips → ρ stabilizes

**Result:** Self-regulating activation level (edge of chaos).

**Integration points:**
- Phase 1: Budget calculation uses f(ρ)
- Phase 2: Generates frame quality signal (flips, entropy, overflow)
- Learning: Isotonic regression updates f(ρ) mapping

### 7.2 Source Impact Learning

**Loop:**
1. Stimulus type X injects energy (budget scaled by g(X))
2. Phase 2: Traversal → flips counted
3. Flip yield: flips / budget for source X
4. Learning: Update g(X) based on yield rank
5. Next stimulus type X: g(X) adjusted

**Result:** Effective sources (error traces, user messages) earn higher impact, ineffective sources (logs) dampened.

**Integration points:**
- Phase 1: Budget uses g(source)
- Phase 2: Counts flips per source
- Learning: Weekly rank normalization of yields → g(source) update

### 7.3 Direction Prior Learning

**Loop:**
1. Stride i→j causes j to flip (traversal)
2. Precedence attribution: C_flip_fwd[ij] += π_ij
3. Direction dominance learned per link type
4. Next link-semantic stimulus match:
5. Split injection by learned prior (e.g., 68% src, 32% tgt for ENABLES)

**Result:** Link types develop characteristic flow patterns.

**Integration points:**
- Phase 1: Link-based injection uses direction prior
- Phase 2: Updates precedence counters during flips
- Learning: Computes dominance ratios per type

---

## 8. Event Stream for Observability

### 8.1 Per-Phase Events

**Phase 1: Activation**
```json
{
  "event": "stimulus.injected",
  "phase": 1,
  "source_type": "user_message",
  "budget": 18.5,
  "nodes_matched": 12,
  "energy_total": 17.2,
  "flips_predicted": 5
}
```

**Phase 2: Redistribution**
```json
{
  "event": "stride.exec",
  "phase": 2,
  "link_id": "enables_principle_goal",
  "delta_e": 0.8,
  "phi": 0.72,
  "gate": 1,
  "target_flipped": true,
  "link_trace": {
    "active_this_frame": true,
    "ema_active": 0.45,
    "ema_flow_mag": 0.73,
    "precedence_forward": 2.3,
    "dominant_hunger": "integration",
    "affect_tone": 0.82,
    "topic_region": "consciousness_architecture"
  }
}

{
  "event": "weights.updated.traversal",
  "phase": 2,
  "nodes": 15,
  "links": 8,
  "avg_delta": 0.08
}
```

**Phase 3: Workspace**
```json
{
  "event": "workspace.selected",
  "phase": 3,
  "nodes": ["principle_x", "realization_y", ...],
  "total_tokens": 1850,
  "budget": 2000,
  "utilization": 0.925
}
```

**Phase 4: Learning**
```json
{
  "event": "trace.parsed",
  "phase": 4,
  "reinforcement_signals": 12,
  "formations": 3,
  "avg_quality": 0.68
}

{
  "event": "weights.updated.trace",
  "phase": 4,
  "nodes": 12,
  "links": 5,
  "avg_delta": 0.12
}
```

### 8.2 Per-Tick Summary

```json
{
  "event": "tick.complete",
  "tick_id": 12847,
  "duration_ms": 103,
  "phases": {
    "activation": {"duration_ms": 18, "energy_injected": 17.2},
    "redistribution": {"duration_ms": 52, "strides": 23, "flips": 6},
    "workspace": {"duration_ms": 14, "nodes_selected": 8},
    "learning": {"duration_ms": 8, "weight_updates": 20}
  },
  "system": {
    "active_nodes": 45,
    "total_energy": 38.5,
    "spectral_proxy": 0.76,
    "health_factor": 0.92
  }
}
```

---

## 9. Testing Integration

### 9.1 Unit Tests (Per Mechanism)

**Stimulus injection:**
```python
def test_entropy_coverage():
    # High-specificity query should select few nodes
    embedding = embed("What is Hamilton apportionment?")
    matches = search(embedding)
    H = entropy(matches)  # Low entropy (one dominant match)
    coverage = 1 - exp(-H)  # Low coverage target
    selected = select_prefix(matches, coverage)
    assert len(selected) <= 3

def test_budget_calculation():
    gap_mass = 15.0
    f_rho = 0.9  # Slightly supercritical
    g_source = 1.2  # User message effective
    budget = gap_mass * f_rho * g_source
    assert budget == approx(16.2)
```

**Traversal learning:**
```python
def test_newness_gate():
    # Both nodes dormant → gate open
    source.energy = 0.05 (threshold = 0.1)
    target.energy = 0.03 (threshold = 0.1)
    gate = int(source.energy < 0.1 and target.energy < 0.1)
    assert gate == 1

    # Source active → gate closed
    source.energy = 0.15
    gate = int(source.energy < 0.1 and target.energy < 0.1)
    assert gate == 0
```

**TRACE learning:**
```python
def test_hamilton_apportionment():
    marks = {
        'node_x': ['very useful', 'very useful', 'useful'],
        'node_y': ['somewhat useful'],
        'node_z': ['misleading']
    }
    result = hamilton_apportion(marks)
    assert result['node_x']['delta_seats'] > result['node_y']['delta_seats']
    assert result['node_z']['delta_seats'] < 0
```

### 9.2 Integration Tests (Cross-Phase)

**Stimulus → Traversal → WM:**
```python
def test_full_activation_to_wm():
    # Inject stimulus
    engine.inject_stimulus(text="Test stimulus", source="user_message")

    # Tick (all 4 phases)
    engine.tick()

    # Verify energy injected
    assert sum(n.energy for n in engine.graph.nodes) > 0

    # Verify traversal occurred
    assert len(engine.last_tick_strides) > 0

    # Verify WM selected
    assert len(engine.current_workspace) > 0

    # Verify high-weight nodes preferred in WM
    wm_avg_weight = mean(n.log_weight for n in engine.current_workspace)
    all_avg_weight = mean(n.log_weight for n in engine.graph.nodes)
    assert wm_avg_weight > all_avg_weight
```

**TRACE → Weight → Valence:**
```python
def test_trace_reinforcement_affects_traversal():
    # Initial weight
    node_x = engine.graph.get_node('test_node')
    initial_weight = node_x.log_weight

    # TRACE marks node as very useful
    trace_result = parse_trace("[node_test_node: very useful]")
    engine.apply_trace(trace_result)

    # Weight should increase
    assert node_x.log_weight > initial_weight

    # Next tick: node should attract more energy (valence bias)
    engine.inject_stimulus("Activate something")
    engine.tick()

    # Node with higher weight should get more traversal traffic
    # (harder to test directly, check valence scores)
```

### 9.3 System Tests (Multi-Session Evolution)

**Learning persistence:**
```python
def test_weight_persistence():
    # Session 1
    engine1 = create_engine(graph_name="test_graph")
    engine1.inject_stimulus("Important concept")
    engine1.tick()
    trace1 = "[node_important_concept: very useful]"
    engine1.apply_trace(parse_trace(trace1))
    weight_session1 = engine1.graph.get_node('important_concept').log_weight
    engine1.save_graph()

    # Session 2 (load same graph)
    engine2 = create_engine(graph_name="test_graph")
    weight_session2 = engine2.graph.get_node('important_concept').log_weight

    # Weight preserved
    assert weight_session2 == weight_session1

    # Further reinforcement accumulates
    trace2 = "[node_important_concept: very useful]"
    engine2.apply_trace(parse_trace(trace2))
    weight_final = engine2.graph.get_node('important_concept').log_weight
    assert weight_final > weight_session2
```

---

## 10. Performance Considerations

### 10.1 Phase Bottlenecks

**Phase 1 (Activation):** Vector search
- Bottleneck: Embedding + ANN search
- Mitigation: Batch embeddings, use HNSW index, GPU acceleration
- Target: <20ms for 100K node graph

**Phase 2 (Redistribution):** Valence computation
- Bottleneck: Computing valence for all outgoing links per active node
- Mitigation: Cache valence scores, incremental updates, top-K approximation
- Target: <60ms for 50 active nodes, avg degree 10

**Phase 3 (Workspace):** Knapsack selection
- Bottleneck: DP knapsack with 100+ candidates
- Mitigation: Greedy approximation (sort by score/tokens, take prefix)
- Target: <15ms for 100 candidates

**Phase 4 (Learning):** Z-score computation
- Bottleneck: Sorting for rank-based z-scores
- Mitigation: Batch updates, cache sorted orders
- Target: <10ms for 1000 nodes per type

### 10.2 Memory Optimization

**Weight storage:**
- 1M nodes × 4 floats (log_weight, 3 EMAs) × 4 bytes = 16MB
- Negligible compared to node content

**Event stream:**
- 10 FPS × 10 events/tick × 1KB/event = 100KB/s = 360MB/hour
- Solution: Circular buffer, configurable retention

**Graph size:**
- FalkorDB handles 10M+ nodes
- Bottleneck is retrieval (vector search), not storage

---

## 11. References

**Mechanism specifications:**
- trace_reinforcement_specification.md - Hamilton, formation quality
- trace_weight_learning.md - TRACE → weight pipeline
- stimulus_injection_specification.md - Stimuli → energy injection
- 05_sub_entity_system.md + addendum - Traversal + weight learning
- schema_learning_infrastructure.md - WHY learning fields exist

**Implementation files:**
- orchestration/consciousness_engine_v2.py - Four-phase tick
- orchestration/trace_parser.py - TRACE → signals
- orchestration/mechanisms/stimulus_processor.py - Phase 1
- orchestration/mechanisms/sub_entity_traversal.py - Phase 2
- orchestration/mechanisms/node_weight.py - Weight updates
- orchestration/mechanisms/link_weight.py - Link weight updates

**Document Status:** Complete integration architecture, ready for V2 engine implementation.
