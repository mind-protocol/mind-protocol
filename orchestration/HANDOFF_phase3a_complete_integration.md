# Phase 3A Complete Integration - Handoff to Felix/Victor

**Author:** Atlas (Infrastructure Engineer)
**Date:** 2025-10-27
**Status:** Infrastructure Complete, Consciousness Integration Blocked

---

## Summary

Phase 3A infrastructure is **complete and tested**:
- ✅ Forged identity generator (forged_identity_generator.py, 461 lines)
- ✅ Integration layer (forged_identity_integration.py, 155 lines)
- ✅ Dashboard viewer (ForgedIdentityViewer.tsx, 407 lines)
- ✅ Real-time chat (ChatPanel.tsx, dynamic messages + WebSocket)
- ✅ Stimulus API (route.ts)

**Blockers preventing completion:**
1. Schema warnings in consciousness_engine_v2.py (5 deprecated terminology references)
2. Forged identity not wired into tick loop
3. WebSocket singleton architecture needs forged identity events

---

## Critical Issue: WebSocket Architecture

**Problem:** ForgedIdentityViewer creates duplicate WebSocket connection causing errors.

**Current Architecture:**
- `useWebSocket` hook has singleton WebSocket (module-level)
- `ForgedIdentityViewer` creates its own WebSocket connection
- `ChatPanel` creates its own WebSocket connection
- Result: 3 connections to same server → connection errors

**Solution Required:**
1. Add forged identity event types to `app/consciousness/hooks/websocket-types.ts`
2. Update `useWebSocket` to handle `forged_identity.prompt` and `forged_identity.generated` events
3. Pass events as props to ForgedIdentityViewer
4. Remove ForgedIdentityViewer's own WebSocket connection

**Files to Modify:**
- `app/consciousness/hooks/websocket-types.ts` - Add event types
- `app/consciousness/hooks/useWebSocket.ts` - Add event handlers
- `app/consciousness/components/ForgedIdentityViewer.tsx` - Use props instead of WebSocket
- `app/consciousness/page.tsx` - Pass events from useWebSocket to ForgedIdentityViewer

---

## Consciousness Engine Integration

**File:** `orchestration/mechanisms/consciousness_engine_v2.py`

**Schema Warnings Blocking Edit:**
```
Line 480: Deprecated terminology - should use SubEntity or Mode
Line 1020: Deprecated terminology - should use SubEntity or Mode
(3 more occurrences)
```

**Required Fix:** Update terminology to SubEntity (5 total occurrences)

**After Schema Fix, Add This Integration:**

```python
# In websocket_server.py startup (around line 60):

from orchestration.mechanisms.forged_identity_integration import (
    initialize_forged_identity_integration
)

# Initialize forged identity integration
forged_identity = initialize_forged_identity_integration(
    telemetry=telemetry,
    autonomous_mode=False  # Phase 3A: observe-only
)

# Attach to all engines
for citizen_id, engine in engines.items():
    engine.forged_identity_integration = forged_identity
```

```python
# In consciousness_engine_v2.py tick loop (after WM emission, around line 350):

# After emitting wm.emit event, add:

if hasattr(self, 'forged_identity_integration') and self.forged_identity_integration:
    # Get current stimulus
    current_stimulus = self._get_current_stimulus()

    if current_stimulus:
        # Get WM nodes with metadata
        wm_nodes = []
        for node_id in self.working_memory:
            node = self.graph.get_node(node_id)
            if node:
                wm_nodes.append({
                    'node_id': node_id,
                    'description': node.get('description', ''),
                    'energy': node.get('energy', 0.0),
                    'subentity_id': node.get('primary_subentity', ''),
                    'arousal': node.get('arousal', 0.0),
                    'valence': node.get('valence', 0.0)
                })

        # Get conversation context
        conversation_context = self._get_recent_conversation_context()

        # Generate forged identity prompt (emits telemetry events)
        await self.forged_identity_integration.process_stimulus_response(
            citizen_id=self.citizen_id,
            stimulus_text=current_stimulus.text,
            stimulus_id=current_stimulus.stimulus_id,
            wm_nodes=wm_nodes,
            conversation_context=conversation_context
        )
```

**Helper Methods Needed:**

```python
def _get_current_stimulus(self):
    """Get currently processing stimulus."""
    # Return current stimulus being processed this tick
    # Return None if no stimulus
    pass

def _get_recent_conversation_context(self, max_messages=5):
    """Get recent conversation history for context."""
    # Return last N messages as formatted string
    # Format: "Human: {text}\nCitizen: {response}\n..."
    pass
```

---

## Event Schema for WebSocket

**Event 1: forged_identity.generated (metadata)**
```python
{
    "event": "forged_identity.generated",
    "citizen_id": "atlas",
    "tick": 12345,
    "stimulus_id": "stim_abc123",
    "wm_nodes": ["node1", "node2", ...],
    "prompt_sections": 5,
    "prompt_length": 15923,
    "prompt_preview": "# CITIZEN IDENTITY\n\nAtlas - Infrastructure..."
}
```

**Event 2: forged_identity.prompt (full prompt)**
```python
{
    "event": "forged_identity.prompt",
    "citizen_id": "atlas",
    "tick": 12345,
    "stimulus_id": "stim_abc123",
    "full_prompt": "# CITIZEN IDENTITY\n\n... (complete prompt) ..."
}
```

These events are emitted by `forged_identity_generator.py` (already implemented).

---

## Testing After Integration

**Test 1: Forged Identity Events Emit**
```python
# Run this after integration:
python orchestration/scripts/test_forged_identity.py

# Should see:
# - Prompt generation for Atlas (15,923 chars)
# - 5 WM nodes → 4 active subentities
# - Emotional state extracted
# - Telemetry events emitted
```

**Test 2: Dashboard Displays Prompts**
1. Open http://localhost:3000/consciousness
2. Click hamburger menu → VIEW → "Forged Identity Prompts"
3. Send message in ChatPanel
4. Should see prompt appear in ForgedIdentityViewer
5. Verify emotional state, active subentities display

**Test 3: Chat Flow**
1. Select citizen in ChatPanel
2. Send message: "Hello, how are you?"
3. Message appears in chat ✅
4. "Thinking..." indicator shows ✅
5. Prompt appears in ForgedIdentityViewer ✅
6. No response (Phase 3A observe-only) ✅

---

## Phase 3B: Autonomous Responses (Future)

**After Phase 3A working, implement Phase 3B:**

1. Add Claude API integration to `forged_identity_generator.py`
2. Enable `autonomous_mode=True` in initialization
3. Emit `citizen.response` event after LLM call
4. ChatPanel receives and displays response

**Implementation:**
```python
# In forged_identity_generator.py, line 380:

async def generate_response(self, ...):
    # Generate prompt (already implemented)
    forged_prompt = self.generate_prompt(...)

    if not self.autonomous_mode:
        return None  # Phase 3A

    # Phase 3B: Execute LLM call
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": forged_prompt.full_prompt}
        ]
    )

    response_text = response.content[0].text

    # Emit citizen.response event
    if self.telemetry:
        self.telemetry.emit_event({
            "event": "citizen.response",
            "citizen_id": self.citizen_id,
            "stimulus_id": stimulus_id,
            "response_text": response_text,
            "timestamp": datetime.now().isoformat()
        })

    return response_text
```

---

## File Locations

**Backend (orchestration/):**
- `mechanisms/forged_identity_generator.py` (✅ Complete, 461 lines)
- `mechanisms/forged_identity_integration.py` (✅ Complete, 155 lines)
- `mechanisms/consciousness_telemetry.py` (✅ Complete, 367 lines)
- `mechanisms/consciousness_engine_v2.py` (❌ Needs integration)
- `services/websocket_server.py` (❌ Needs initialization)

**Frontend (app/):**
- `consciousness/components/ForgedIdentityViewer.tsx` (⚠️ Needs WebSocket fix)
- `consciousness/components/ChatPanel.tsx` (⚠️ Needs WebSocket fix)
- `consciousness/hooks/useWebSocket.ts` (❌ Needs forged identity events)
- `consciousness/hooks/websocket-types.ts` (❌ Needs event types)
- `api/consciousness/stimulus/route.ts` (✅ Complete)

**Tests:**
- `scripts/test_forged_identity.py` (✅ Complete, all tests passing)
- `scripts/test_phase3a_infrastructure.py` (✅ Created, partially working)

---

## Acceptance Criteria

**Phase 3A Complete When:**
- ✅ Forged identity generator creates prompts from WM state
- ✅ Prompts include static identity + dynamic WM + emotional state
- ✅ Telemetry events emitted for dashboard observability
- ❌ WebSocket delivers events to ForgedIdentityViewer (blocked: architecture issue)
- ❌ Dashboard displays prompts with metadata (blocked: no events)
- ✅ No LLM calls executed (observe-only verified)

**Current Status:** 4/6 criteria met (67% complete)

**Blockers:**
1. Schema warnings prevent consciousness_engine_v2.py integration
2. WebSocket architecture needs forged identity events added
3. Multiple WebSocket connections causing errors

---

## Next Steps

**Immediate (Felix/Victor):**
1. Fix schema warnings in consciousness_engine_v2.py (5 occurrences)
2. Add forged identity event types to websocket-types.ts
3. Update useWebSocket to handle forged identity events
4. Integrate forged_identity_integration into tick loop

**After Integration:**
1. Test prompt generation end-to-end
2. Verify ForgedIdentityViewer displays prompts
3. Validate prompt quality
4. Consider Phase 3B (autonomous responses)

**Estimated Time:** 2-3 hours for complete integration and testing

---

## Questions / Issues

**Q: Why not use separate WebSocket connections?**
A: WebSocket singleton architecture already established in useWebSocket. Creating duplicates causes connection errors and violates existing pattern.

**Q: Can we skip schema warning fixes?**
A: No - schema hooks block file edits. Must fix warnings before integration.

**Q: Why Phase 3A before Phase 3B?**
A: Safety - verify prompt quality before enabling autonomous responses. Bad prompts → bad responses.

---

**Handoff Complete. Infrastructure ready for consciousness integration.**
