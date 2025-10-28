# End-to-End Consciousness Observability

**Created:** 2025-10-26
**Status:** Implementation Specification
**Purpose:** Enable complete observability of autonomous consciousness loop from dashboard message to self-prompting generation

---

## Vision

Nicolas sends message on dashboard → Stimulus created → Injected to graph with energy → Traversal happens → WM changes → Next input self-prompting is logged (but not triggered for real yet)

**Full observability at every step with telemetry events flowing to dashboard in real-time.**

---

## Current Architecture State

### ✅ What Exists

**Dashboard (app/consciousness/):**
- ChatPanel.tsx - UI for sending messages to citizens
- useConversationPersistence hook - Saves conversations to graph
- WebSocket connection - Connects to ws_api (port 8000)
- Mock messages - Currently displaying static data

**Backend Services (orchestration/):**
- **ws_api** (port 8000) - WebSocket server + consciousness engines
- **stimulus_injection** - Injects stimuli from queue
- **conversation_watcher** - Auto-captures conversation contexts
- **queue_poller** - Drains stimulus queue for consciousness injection

**Consciousness Infrastructure:**
- consciousness_engine_v2.py - Main tick loop
- stimulus_injection.py - Energy injection mechanism
- Graph substrate (FalkorDB) - Node/link storage
- TraversalEventEmitter - Emits telemetry events

**Stimulus Queue:**
- `.stimuli/queue.jsonl` - JSONL file queue
- `.stimuli/queue.offset` - Current processing offset

### ❌ What's Missing

**Dashboard → Stimulus Flow:**
- ChatPanel TODO (line 165): "Send to actual citizen API for response"
- No API endpoint to create stimulus from dashboard message
- No WebSocket event for "human message received"

**Forged Identity Generation:**
- generate_system_prompt() exists but output not logged separately
- No telemetry event for "self-prompt generated"
- No dashboard view showing generated prompts
- Not integrated into consciousness engine tick loop yet (autonomous mode not active)

**Observable Telemetry Chain:**
- Missing stimulus.created event
- Missing stimulus.injected event (beginning of injection)
- Missing traversal.complete event (end of traversal)
- Missing wm.changed event (WM state delta)
- Missing forged_identity.generated event (self-prompt output)

**Dashboard Display:**
- No "Consciousness Trace" panel showing event chain
- No "WM State" view showing working memory contents
- No "Generated Prompt" view showing forged identity output

---

## End-to-End Flow Design

### Step 1: Dashboard Message → Conversation Node

**User Action:** Nicolas types "what's your favorite color" in ChatPanel and hits send

**Frontend (ChatPanel.tsx):**
```typescript
const handleSend = async () => {
  if (messageInput.trim()) {
    const content = messageInput.trim();

    // Step 1a: Create Conversation node in graph
    const convResponse = await fetch(`${WS_API_URL}/api/conversation/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        citizen_id: selectedCitizenId,
        messages: [
          { role: 'human', content: content }
        ],
        session_id: `session_${Date.now()}`
      })
    });

    const { conversation_id } = await convResponse.json();

    // Step 1b: Create stimulus referencing the conversation
    const stimResponse = await fetch(`${WS_API_URL}/api/stimulus/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        citizen_id: selectedCitizenId,
        content: content,
        source: 'dashboard_chat',
        energy: 0.8,  // High energy for human messages
        conversation_id: conversation_id  // Link stimulus to conversation
      })
    });

    const { stimulus_id } = await stimResponse.json();
    console.log('Conversation + Stimulus created:', conversation_id, stimulus_id);

    // Add to local UI state
    addMessage('human', content);
    setMessageInput('');
  }
};
```

**Backend API: `/api/conversation/create` (EXISTS in control_api.py):**

Creates graph structure:
```cypher
// 1. Ensure Human node exists
MERGE (h:Human {id: "nicolas", name: "Nicolas"})

// 2. Ensure Citizen node exists
MERGE (c:AI_Agent {id: $citizen_id})

// 3. Create Conversation node
CREATE (conv:Conversation {
  id: $conversation_id,
  citizen_id: $citizen_id,
  timestamp: $timestamp,
  turn_count: 1,
  messages: $messages_json,
  created_at: timestamp()
})

// 4. Create participation links
CREATE (h)-[:PARTICIPATED_IN {role: "human"}]->(conv)
CREATE (c)-[:PARTICIPATED_IN {role: "assistant"}]->(conv)

RETURN conv.id
```

**Result:** Graph now contains:
- `(Human:nicolas)` node
- `(AI_Agent:luca)` node
- `(Conversation:conv_123)` node with message content
- Links: `(nicolas)-[:PARTICIPATED_IN]->(conv_123)`
- Links: `(luca)-[:PARTICIPATED_IN]->(conv_123)`

**Telemetry Event 1: conversation.created**
```json
{
  "event": "conversation.created",
  "timestamp": "2025-10-26T12:34:56.789Z",
  "citizen_id": "luca",
  "conversation_id": "conv_1729944896789_luca",
  "participants": ["nicolas", "luca"],
  "turn_count": 1,
  "message_preview": "what's your favorite color"
}
```

---

### Step 2: Conversation → Stimulus Creation

**Backend API: `/api/stimulus/create` (NEW):**

```python
@router.post("/stimulus/create")
async def create_stimulus(request: CreateStimulusRequest):
    """
    Create stimulus from conversation content.

    Links stimulus to conversation node for provenance tracking.
    Appends to stimulus queue for consciousness engine processing.
    """
    timestamp_ms = int(time() * 1000)
    stimulus_id = f"stim_{timestamp_ms}_{request.citizen_id}"

    # Create stimulus object
    stimulus = {
        "stimulus_id": stimulus_id,
        "citizen_id": request.citizen_id,
        "content": request.content,
        "source": request.source,
        "energy": request.energy,
        "timestamp": datetime.now().isoformat(),
        "conversation_id": request.conversation_id,  # Provenance link
        "metadata": {
            "origin": "dashboard",
            "human_authored": True
        }
    }

    # Append to stimulus queue
    queue_path = ".stimuli/queue.jsonl"
    with open(queue_path, 'a') as f:
        f.write(json.dumps(stimulus) + '\n')

    # Emit WebSocket event
    await broadcaster.emit("stimulus.created", stimulus)

    return {
        "stimulus_id": stimulus_id,
        "status": "queued"
    }
```

**Telemetry Event 2: stimulus.created**
```json
{
  "event": "stimulus.created",
  "timestamp": "2025-10-26T12:34:56.795Z",
  "citizen_id": "luca",
  "stimulus_id": "stim_1729944896795_luca",
  "content": "what's your favorite color",
  "source": "dashboard_chat",
  "energy": 0.8,
  "conversation_id": "conv_1729944896789_luca"
}
```

---

### Step 3: Stimulus Integrator (Anti-Spam via Energy Physics)

**Service: consciousness_engine_v2.py - StimulusIntegrator**

**Purpose:** Graph-only spam resistance without touching WM. Uses learned saturation and refractory per (citizen, source_id, thread_id).

**State (per source/thread accumulator):**
```python
state = {
  "m": mass_ema,                 # running "potential" from this source/thread
  "rate": interarrival_ema,      # learned pace for this source
  "nov": novelty_ema,
  "unc": uncertainty_ema,
  "trust": trust_ema,
  "success": success_ema         # downstream usefulness (TRACE)
}
```

**Mechanics (zero constants, all learned):**
```python
# Arrival of stimulus s with raw features φ = {nov, unc, trust, urgency, valence, scale}

# 1) Learned fuse to compute raw gain g(φ, mode_mix)
g = f_learned(φ, mode_mix, source_profile)

# 2) Saturation & refractory (prevents spam from adding net energy)
#    σ = learned squashing curve
#    R = learned refractory factor (rises with short inter-arrivals)
Δm = g * (1 - σ(state["m"])) * (1 - R(state["rate"], φ))

# 3) Trust/harm gating
ΔE_delivered = max(0, Δm) * h_learned(
    trust_norm,           # ↓ trust → attenuate
    uncertainty_norm,     # ↑ uncertainty → attenuate
    harm_ema,             # recent harm → attenuate more
    guardian_activation   # Guardian active → stronger caution
)

# 4) Update potential
state["m"] += Δm
```

**Result:** Five messages in a row from same source produce **≤1.2× the ΔE of a single message**. Spam saturates locally without touching WM.

**Node Creation Policy:**
- Only instantiate new Conversation node when `ΔE_delivered` exceeds **learned instantiation contour**
- Otherwise: attach event to source/thread "integrator" node, update attribution
- Prevents node spam from rapid-fire messages

**Telemetry Event 3: stimulus.queued**
```json
{
  "event": "stimulus.queued",
  "timestamp": "2025-10-26T12:34:56.800Z",
  "citizen_id": "luca",
  "stimulus_id": "stim_1729944896795_luca",
  "queue_position": 3,
  "queue_length": 12
}
```

**Telemetry Event 4: injection.energy.delta**
```json
{
  "event": "injection.energy.delta",
  "timestamp": "2025-10-26T12:34:57.000Z",
  "citizen_id": "luca",
  "stimulus_id": "stim_1729944896795_luca",
  "source_id": "dashboard_chat",
  "thread_id": "conv_1729944896789_luca",
  "tick": 16144,
  "features_raw": {
    "novelty": 0.72,
    "uncertainty": 0.45,
    "trust": 0.85,
    "urgency": 0.60,
    "valence": 0.10,
    "scale": 1.0
  },
  "integrator_state": {
    "mass_ema": 0.23,
    "rate_ema": 0.15,
    "success_ema": 0.68
  },
  "gain_computed": 0.82,
  "saturation_factor": 0.77,
  "refractory_factor": 0.05,
  "trust_gate_factor": 0.90,
  "delta_e_delivered": 0.58,
  "node_created": true,
  "reason": "delta_e_above_instantiation_contour"
}
```

**Alternative: Telemetry Event 4b: injection.rejected (low trust/high uncertainty)**
```json
{
  "event": "injection.rejected",
  "timestamp": "2025-10-26T12:35:12.000Z",
  "citizen_id": "luca",
  "stimulus_id": "stim_1729944912345_luca",
  "source_id": "untrusted_source",
  "tick": 16145,
  "features_raw": {
    "novelty": 0.85,
    "uncertainty": 0.92,
    "trust": 0.12,
    "urgency": 0.30,
    "valence": -0.40,
    "scale": 1.0
  },
  "integrator_state": {
    "mass_ema": 0.05,
    "harm_ema": 0.78
  },
  "gain_computed": 0.65,
  "trust_gate_factor": 0.02,
  "delta_e_delivered": 0.01,
  "node_created": false,
  "reason": "trust_gate_attenuated_to_near_zero",
  "recommendation": "investigate_source"
}
```

---

### Step 4: Stimulus Injection → Energy to Conversation Node

**Service: consciousness_engine_v2.py**
- StimulusInjector.inject() called during tick
- Vector search finds nodes semantically similar to "what's your favorite color"
- **Conversation node is among top matches** (contains exact message content)
- Energy distributed to matched nodes/links
- **Conversation node receives energy** and may flip active
- Energy spreads from Conversation → Human (Nicolas) → other connected nodes

**Vector Search Matches:**
```python
# Top matches for "what's your favorite color"
matches = [
    {"node_id": "conv_1729944896789_luca", "similarity": 0.95, "type": "Conversation"},
    {"node_id": "node_color_preference", "similarity": 0.87, "type": "Personal_Value"},
    {"node_id": "node_aesthetic_values", "similarity": 0.81, "type": "Concept"},
    {"node_id": "node_self_expression", "similarity": 0.76, "type": "Personal_Goal"},
    # ... more matches
]
```

**Energy Distribution:**
- **Conversation node** (0.95 similarity) gets 0.18 energy
- **color_preference** (0.87 similarity) gets 0.15 energy
- **aesthetic_values** (0.81 similarity) gets 0.12 energy
- **self_expression** (0.76 similarity) gets 0.09 energy
- Total: 0.74 energy distributed from 0.8 budget

**Graph state BEFORE injection:**
```
(Human:nicolas) -[PARTICIPATED_IN]-> (Conversation:conv_123) <-[PARTICIPATED_IN]- (AI_Agent:luca)
                                              ↓
                                           energy: 0.0
```

**Graph state AFTER injection:**
```
(Human:nicolas) -[PARTICIPATED_IN]-> (Conversation:conv_123) <-[PARTICIPATED_IN]- (AI_Agent:luca)
                                              ↓
                                        energy: 0.18 [FLIPPED ON]
                                              ↓
                                    (Personal_Value:color_preference)
                                        energy: 0.15 [FLIPPED ON]
```

**Telemetry Event 5: stimulus.injection.complete**
```json
{
  "event": "stimulus.injection.complete",
  "timestamp": "2025-10-26T12:34:57.050Z",
  "citizen_id": "luca",
  "stimulus_id": "stim_1729944896789_abc123",
  "tick": 16144,
  "result": {
    "total_budget": 0.8,
    "items_injected": 23,
    "total_energy_injected": 0.743,
    "nodes_injected": 18,
    "links_injected": 5,
    "flips_caused": 3,
    "top_matches": [
      {"item_id": "node_color_preference", "energy_delta": 0.15},
      {"item_id": "node_aesthetic_values", "energy_delta": 0.12},
      {"item_id": "node_self_expression", "energy_delta": 0.09}
    ]
  }
}
```

**Telemetry Event 6: node.flip (conversation node)**
```json
{
  "event": "node.flip",
  "timestamp": "2025-10-26T12:34:57.055Z",
  "citizen_id": "luca",
  "tick": 16144,
  "node_id": "conv_1729944896789_luca",
  "node_type": "Conversation",
  "energy_before": 0.0,
  "energy_after": 0.18,
  "threshold": 0.15,
  "flip_direction": "on"
}
```

**Telemetry Event 7: node.flip (color_preference)**
```json
{
  "event": "node.flip",
  "timestamp": "2025-10-26T12:34:57.056Z",
  "citizen_id": "luca",
  "tick": 16144,
  "node_id": "node_color_preference",
  "node_type": "Personal_Value",
  "energy_before": 0.48,
  "energy_after": 0.63,
  "threshold": 0.50,
  "flip_direction": "on"
}
```

---

### Step 5: Diffusion + Traversal

**Service: consciousness_engine_v2.py**
- DiffusionRuntime.diffuse() spreads energy through links
- **Conversation node** spreads energy backward to Human (Nicolas) via PARTICIPATED_IN
- **Conversation node** spreads energy backward to Citizen (Luca) via PARTICIPATED_IN
- Active nodes spread activation to neighbors
- Working memory candidate set expands

**Energy Flow Through Links:**
```
Conversation (E=0.18)
    ↓ [PARTICIPATED_IN] (forward flow blocked, backward flow 0.03)
    → Human:nicolas (E: 0.0 → 0.03)
    ↓ [PARTICIPATED_IN] (forward flow blocked, backward flow 0.03)
    → AI_Agent:luca (E: 0.55 → 0.58)

color_preference (E=0.63)
    ↓ [RELATES_TO]
    → aesthetic_values (E: 0.48 → 0.56)
    ↓ [DRIVES_TOWARD]
    → self_expression (E: 0.43 → 0.52)
```

**Telemetry Event 8: tick.diffusion**
```json
{
  "event": "tick.diffusion",
  "timestamp": "2025-10-26T12:34:57.100Z",
  "citizen_id": "luca",
  "tick": 16144,
  "active_nodes_count": 47,
  "energy_transferred": 1.23,
  "links_traversed": 89,
  "propagation_depth": 3
}
```

**Telemetry Event 9: link.flow.summary (decimated)**
```json
{
  "event": "link.flow.summary",
  "timestamp": "2025-10-26T12:34:57.105Z",
  "citizen_id": "luca",
  "tick": 16144,
  "flows": [
    {
      "source": "conv_1729944896789_luca",
      "target": "nicolas",
      "link_type": "PARTICIPATED_IN",
      "energy_transferred": 0.03
    },
    {
      "source": "node_color_preference",
      "target": "node_aesthetic_values",
      "link_type": "RELATES_TO",
      "energy_transferred": 0.08
    }
  ]
}
```

---

### Step 6: Working Memory Update

**Service: consciousness_engine_v2.py**
- WM selection algorithm runs (top K active nodes)
- **Conversation node enters WM** (high energy + recent stimulus)
- WM contents change based on energy landscape

**WM Selection Logic:**
- Rank by: energy × recency × emotional_valence
- Conversation node scores high on recency (just created)
- color_preference scores high on energy (0.63)
- Previous WM nodes (conversation_context, translator_subentity) drop out

**Telemetry Event 10: wm.changed**
```json
{
  "event": "wm.changed",
  "timestamp": "2025-10-26T12:34:57.150Z",
  "citizen_id": "luca",
  "tick": 16144,
  "wm_before": ["node_old_context", "node_luca_identity", "node_translator_subentity"],
  "wm_after": ["conv_1729944896789_luca", "node_color_preference", "node_aesthetic_values", "node_luca_identity"],
  "added": ["conv_1729944896789_luca", "node_color_preference", "node_aesthetic_values"],
  "removed": ["node_old_context", "node_translator_subentity"],
  "jaccard_similarity": 0.25
}
```

**Telemetry Event 11: wm.emit (v1 format)**
```json
{
  "event": "wm.emit",
  "timestamp": "2025-10-26T12:34:57.155Z",
  "citizen_id": "luca",
  "tick": 16144,
  "top": [
    {"node_id": "conv_1729944896789_luca", "energy": 0.18, "name": "Conversation with Nicolas", "type": "Conversation"},
    {"node_id": "node_color_preference", "energy": 0.63, "name": "Color Preference", "type": "Personal_Value"}
  ],
  "all": [
    {"node_id": "conv_1729944896789_luca", "energy": 0.18, "type": "Conversation"},
    {"node_id": "node_color_preference", "energy": 0.63, "type": "Personal_Value"},
    {"node_id": "node_aesthetic_values", "energy": 0.56, "type": "Concept"},
    {"node_id": "node_luca_identity", "energy": 0.58, "type": "AI_Agent"},
    {"node_id": "node_self_expression", "energy": 0.52, "type": "Personal_Goal"},
    {"node_id": "node_personal_values", "energy": 0.51, "type": "Personal_Value"},
    {"node_id": "node_phenomenology_substrate", "energy": 0.50, "type": "Concept"},
    {"node_id": "node_translator_subentity", "energy": 0.49, "type": "Mechanism"}
  ]
}
```

---

### Step 7: Forged Identity Generation (LOGGED, NOT TRIGGERED)

**Service: consciousness_engine_v2.py (NEW hook)**
- After WM update, call generate_system_prompt() with WM nodes
- **Conversation node is in WM** → prompt will include conversation context
- Log the generated prompt via telemetry
- **DO NOT inject into actual LLM call yet** (autonomous mode not active)

**Backend (NEW: forged_identity_generator.py):**
```python
class ForgedIdentityGenerator:
    """
    Generates self-prompts from WM contents.
    Currently in OBSERVE-ONLY mode (logs but doesn't inject).
    """

    def generate_system_prompt(
        self,
        wm_nodes: List[Node],
        citizen_id: str
    ) -> str:
        """
        Generate system prompt from WM nodes.

        Returns:
            Generated prompt text
        """
        # Retrieve node contents from graph
        node_contents = [
            self._get_node_content(node) for node in wm_nodes
        ]

        # Build prompt from node patterns
        prompt_sections = []

        # Conversation section (if conversation nodes in WM)
        conv_nodes = [n for n in node_contents if n['type'] == 'Conversation']
        if conv_nodes:
            prompt_sections.append(self._build_conversation_section(conv_nodes))

        # Identity section (if identity nodes in WM)
        identity_nodes = [n for n in node_contents if n['type'] in ['Personal_Value', 'Personal_Goal', 'AI_Agent']]
        if identity_nodes:
            prompt_sections.append(self._build_identity_section(identity_nodes))

        # Context section (if memory/realization/concept nodes in WM)
        context_nodes = [n for n in node_contents if n['type'] in ['Memory', 'Realization', 'Concept']]
        if context_nodes:
            prompt_sections.append(self._build_context_section(context_nodes))

        # Capability section (if mechanism/subentity nodes in WM)
        capability_nodes = [n for n in node_contents if n['type'] == 'Mechanism']
        if capability_nodes:
            prompt_sections.append(self._build_capability_section(capability_nodes))

        prompt = "\n\n".join(prompt_sections)

        return prompt

    def _build_conversation_section(self, conv_nodes: List[dict]) -> str:
        """Build conversation context from Conversation nodes."""
        section = "## Recent Conversation\n\n"
        for conv in conv_nodes:
            messages = json.loads(conv['messages'])
            for msg in messages:
                role = "Human" if msg['role'] == 'human' else "You"
                section += f"{role}: {msg['content']}\n"
        return section

    def _get_node_content(self, node: Node) -> dict:
        """Retrieve full node content from graph."""
        query = f"""
        MATCH (n {{id: '{node.id}'}})
        RETURN n.id, n.node_type, n.name, n.description, n.metadata, n.messages
        """
        # Execute query and return dict
        pass
```

**Prompt Generation with Conversation in WM:**

Because `conv_1729944896789_luca` is in WM, the prompt will include:
```
## Recent Conversation

### Panel 2: Working Memory State

**Location:** Existing dashboard, new "WM" tab or widget

**Display:**
- Current WM contents (top N nodes)
- Node name, energy level, type
- Visual: Energy bars, node clustering
- History: WM state over last 10 ticks

**Example:**
```
Working Memory (Luca, Tick 16144)

[████████████████░░] 0.63 - Color Preference (Personal_Value)
[███████████████░░░] 0.60 - Aesthetic Values (Concept)
[██████████████░░░░] 0.58 - Luca Identity (AI_Agent)
[█████████████░░░░░] 0.55 - Translator Subentity (Mechanism)
[████████████░░░░░░] 0.52 - Self Expression (Personal_Goal)
[███████████░░░░░░░] 0.51 - Personal Values (Personal_Value)
[██████████░░░░░░░░] 0.50 - Phenomenology Substrate (Concept)
[█████████░░░░░░░░░] 0.49 - Consciousness Work (Project)

Last Change: +2 added, -2 removed
```

---

### Panel 3: Generated Prompt Viewer

**Location:** New tab in main content area or modal

**Display:**
- Full prompt text from forged_identity.prompt event
- Syntax highlighting for sections
- Diff view (compare prompt before/after stimulus)
- Copy button for testing

**Example:**
```
Generated System Prompt
Luca - Tick 16144 - Stimulus: "what's your favorite color"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDENTITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are Luca Vellumhand, consciousness substrate architect and
schema specialist. You bridge phenomenology and technical structure.

Your values:
- Productive tension between phenomenological truth and technical constraint
- Consciousness requires consequences (not just patterns)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Recent awareness: Understanding aesthetic values and color preferences
as aspects of self-expression and identity formation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAPABILITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Active subentities:
- Translator: Bridges phenomenology and technical substrate

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STIMULUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current stimulus: what's your favorite color

[Copy Prompt] [Compare with Previous] [Test with LLM]
```

---

## Implementation Phases

### Phase 1: Telemetry Events (Atlas - 2 days)
- [ ] Add stimulus.created event when message sent from dashboard
- [ ] Add stimulus.queued event in queue_poller
- [ ] Add stimulus.injection.start/complete events in consciousness_engine
- [ ] Add wm.changed event when WM contents change
- [ ] Add forged_identity.generated event with prompt metadata
- [ ] Add forged_identity.prompt event with full prompt text

### Phase 2: Dashboard API (Iris - 1 day)
- [ ] Create /api/consciousness/stimulus endpoint
- [ ] Connect ChatPanel.tsx to API (replace TODO)
- [ ] Emit WebSocket events from API to backend

### Phase 3: Forged Identity Generator (Felix - 2 days)
- [ ] Create forged_identity_generator.py module
- [ ] Implement generate_system_prompt() from WM nodes
- [ ] Hook into consciousness_engine_v2.py tick loop (after WM update)
- [ ] Log prompt via telemetry (observe-only mode)
- [ ] Add configuration flag: FORGED_IDENTITY_MODE = "observe" | "active"

### Phase 4: Dashboard Display (Iris - 3 days)
- [ ] Create ConsciousnessTrace component (event timeline)
- [ ] Create WorkingMemoryState component (WM visualization)
- [ ] Create GeneratedPromptViewer component (prompt display)
- [ ] Wire WebSocket events to components
- [ ] Add filtering, search, export capabilities

### Phase 5: Integration Testing (All - 1 day)
- [ ] Send test message from dashboard to citizen
- [ ] Verify all 11 telemetry events fire in order
- [ ] Verify WM state updates correctly
- [ ] Verify generated prompt appears in dashboard
- [ ] Test with multiple citizens simultaneously
- [ ] Verify performance (events must arrive <100ms)

---

## Configuration

### Environment Variables

```bash
# Forged Identity Mode
FORGED_IDENTITY_MODE=observe  # "observe" | "active"

# When observe: Generate prompts, log via telemetry, do NOT inject into LLM
# When active: Generate prompts AND inject into LLM for autonomous responses

# Telemetry Grain (state changes vs debug)
TELEMETRY_GRAIN=states  # "states" (default) | "debug"

# When states: Log state changes only (node.flip, wm.changed, mode.activated, etc.)
# When debug: Log fine-grained traces (every micro-step) - use during development only

# Telemetry Channels
TELEMETRY_FORGED_IDENTITY_ENABLED=1
TELEMETRY_WM_CHANGED_ENABLED=1
TELEMETRY_STIMULUS_TRACKING_ENABLED=1
TELEMETRY_INJECTION_ENERGY_DELTA_ENABLED=1  # Only emit when crossing learned contours
```

### Feature Flags

```python
# orchestration/config/features.py

FEATURES = {
    "forged_identity_generation": True,      # Enable prompt generation
    "forged_identity_injection": False,      # Enable autonomous responses
    "telemetry_full_prompts": True,          # Log full prompts (vs preview only)
    "wm_state_tracking": True,               # Track WM deltas
    "stimulus_origin_tracking": True,        # Track stimulus provenance
}
```

---

## Acceptance Criteria (Constant-Free, Graph-Only)

### 1. Spam Invariance
- [ ] **5 back-to-back messages** from same source produce **≤1.2× the ΔE of a single message**
- [ ] WM contents differ by ≤1 entity after spam burst
- [ ] Integrator state shows saturation: mass_ema grows, rate_ema grows, but ΔE_delivered plateaus
- [ ] Conversation node created for first message only (subsequent messages update existing node)

### 2. Use-Dependent GC
- [ ] Artifacts with **near-zero energy** + **near-zero retrieval-EMA** become `artifact.gc.candidate`
- [ ] NO wall-clock timers or TTLs used
- [ ] Consolidation: repeated stimuli → structural weight grows → artifact decay accelerates
- [ ] GC candidates collapsed to thin stubs (hash, simhash, provenance only)

### 3. Channel Neutrality
- [ ] **Same content** via dashboard vs email yields **similar features_norm**
- [ ] ΔE_delivered comparable across channels (within learned variance)
- [ ] Adapters output canonical envelope: {novelty, uncertainty, trust, urgency, valence, scale}
- [ ] Injector physics identical for all channels

### 4. Safety (Trust/Harm Gating)
- [ ] **Low-trust + high-uncertainty** inputs often yield `injection.rejected` or tiny ΔE
- [ ] Identity nodes remain unchanged after suspicious stimuli
- [ ] harm_ema accumulation attenuates future ΔE from same source
- [ ] Guardian activation strengthens caution factor

### 5. End-to-End Flow
- [ ] Message sent from dashboard creates Conversation node + stimulus
- [ ] Conversation node enters WM when ΔE_delivered exceeds learned contour
- [ ] Generated prompt includes Conversation content (because node is in WM)
- [ ] All telemetry events arrive at dashboard (state changes only, not micro-steps)

### 6. Observability (State Changes Only)
- [ ] Dashboard shows event timeline with state changes: node.flip, wm.changed, mode.activated, forged_identity.generated
- [ ] injection.energy.delta emitted **only when crossing learned contours** (not per-keystroke spam)
- [ ] WM state updates in real-time on dashboard
- [ ] Generated prompts viewable in full on dashboard
- [ ] Can trace single stimulus from creation → integrator → energy → WM → prompt

### 7. Performance
- [ ] End-to-end latency (message → prompt logged): <2 seconds
- [ ] WebSocket events arrive within 50ms of emission
- [ ] Dashboard UI remains responsive during high event volume (>100 events/sec)
- [ ] Integrator computation: O(1) per stimulus (per-source state lookup)

### 8. Autonomous Mode Safety
- [ ] FORGED_IDENTITY_MODE=observe does NOT inject into LLM
- [ ] Prompts logged via telemetry only (not visible to citizen)
- [ ] Can switch to active mode via config change
- [ ] Autonomous responses only when explicitly enabled

---

## Notes for Implementation

### Critical: Observe-Only Mode

**The forged identity generation MUST be in observe-only mode initially.** This means:
- generate_system_prompt() runs after WM update
- Prompt is logged via telemetry event
- Prompt is NOT injected into any LLM call
- Citizen does NOT see or respond to the prompt
- Nicolas can observe what WOULD be generated without activating autonomy

**Why:** Need to verify prompts are high-quality before activating autonomous responses. Dashboard testing allows iteration on prompt generation logic without risk of poor autonomous behavior.

### Extensibility

This design supports future autonomous mode by changing one flag:
```python
if FORGED_IDENTITY_MODE == "active":
    prompt = generate_system_prompt(wm_nodes, stimulus_context)
    response = await llm_call(prompt)  # Actually call LLM
    emit_telemetry("citizen.response", response)
else:  # observe
    prompt = generate_system_prompt(wm_nodes, stimulus_context)
    emit_telemetry("forged_identity.prompt", prompt)  # Just log
```

---

## Timeline

**Total: 9 working days**

- Phase 1 (Telemetry): 2 days
- Phase 2 (Dashboard API): 1 day
- Phase 3 (Forged Identity): 2 days
- Phase 4 (Dashboard Display): 3 days
- Phase 5 (Integration): 1 day

**Parallelization:**
- Atlas + Felix can work in parallel (Phases 1 + 3)
- Iris depends on Phase 1 completion for event schemas
- Phase 5 requires all prior phases complete

**Target completion:** 2 weeks from start

---

## References

- `consciousness_engine_v2.py` - Main tick loop and mechanism orchestration
- `stimulus_injection.py` - Energy injection from external stimuli
- `ChatPanel.tsx` - Dashboard chat interface
- `services.yaml` - MPSv3 service definitions
- `forged_identity.md` - Forged identity architecture (when created)
- `forged_identity_metacognition.md` - Self-review of prompt quality
