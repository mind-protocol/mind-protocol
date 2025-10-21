# Phase-A Minimal Autonomy Specification

**Version:** 1.0
**Created:** 2025-10-21
**Architect:** Ada "Bridgekeeper"
**Implementer:** Felix "Ironhand"
**Purpose:** Implementation-ready specifications for Phase-A (answer-only autonomy)

---

## Overview

**Scope:** Answer-only autonomy with self-handoff missions

**Timeline:** 3-5 days implementation

**Services to Build:**
1. `stimulus_injection_service.py` (~800-1000 lines)
2. `autonomy_orchestrator.py` (~1200-1500 lines)

**Success Criteria:**
- ✅ At least 10 intents created from agent answers
- ✅ At least 5 auto-wake missions to L1
- ✅ Zero hallucination incidents
- ✅ All outcomes have verification PoV ≥ 0.6

---

## Service 1: stimulus_injection_service.py

### Purpose

HTTP API wrapper around existing `StimulusInjector` mechanism. Receives stimulus envelopes from any source, validates, routes to correct graph, and injects energy.

### File Location

`orchestration/stimulus_injection_service.py`

### Dependencies

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
import uvicorn
import asyncio
import os
import sys
import signal
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import deque
import time
import logging

# Mind Protocol imports
from orchestration.mechanisms.stimulus_injection import StimulusInjector, InjectionResult
from orchestration.consciousness_engine_v2 import get_engine  # Accessor function
from falkordb import FalkorDB
```

### Class Structure

```python
class StimulusInjectionService:
    """
    HTTP service for multi-source stimulus injection.

    Wraps existing StimulusInjector mechanism with:
    - HTTP API (POST /inject)
    - Envelope validation (Pydantic)
    - Deduplication (content digest, 5min window)
    - Circuit breakers (embedding, vector search)
    - Queue management (priority queue, overflow handling)
    - Operational contract (heartbeat, PID lock, SIGTERM)
    """

    def __init__(self):
        """Initialize service with operational infrastructure."""
        # Operational
        self.pid_lock = Path(".stimulus_injection.lock")
        self.heartbeat_file = Path(".heartbeats/stimulus_injection.heartbeat")
        self.logger = logging.getLogger(__name__)

        # Mechanisms
        self.injector = StimulusInjector()  # Use existing mechanism
        self.db = FalkorDB()

        # Circuit breakers
        self.embedding_breaker = CircuitBreaker(threshold=5, window=60)
        self.vector_search_breaker = CircuitBreaker(threshold=5, window=60)

        # Deduplication tracking
        self.recent_digests = {}  # {digest: (timestamp, count)}

        # Metrics
        self.metrics = {
            "queue_depth": 0,
            "processed_last_minute": 0,
            "dropped_last_minute": 0,
            "circuit_breaker_embedding": "closed",
            "circuit_breaker_vector_search": "closed"
        }

    def acquire_pid_lock(self):
        """Acquire PID lock or exit if another instance running."""
        if self.pid_lock.exists():
            with open(self.pid_lock) as f:
                old_pid = int(f.read().strip())

            try:
                os.kill(old_pid, 0)
                self.logger.error(f"Another instance running (PID {old_pid})")
                sys.exit(1)
            except OSError:
                self.logger.warning("Removing stale PID lock")
                self.pid_lock.unlink()

        with open(self.pid_lock, 'w') as f:
            f.write(str(os.getpid()))

    def release_pid_lock(self):
        """Release PID lock on shutdown."""
        if self.pid_lock.exists():
            self.pid_lock.unlink()

    async def heartbeat_writer(self):
        """Write heartbeat every 5s."""
        while True:
            heartbeat = {
                "component": "stimulus_injection",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "pid": os.getpid(),
                "status": self.get_status(),
                "metrics": self.metrics
            }

            self.heartbeat_file.parent.mkdir(exist_ok=True)
            with open(self.heartbeat_file, 'w') as f:
                json.dump(heartbeat, f)

            await asyncio.sleep(5)

    def get_status(self) -> str:
        """Compute current service status."""
        if self.embedding_breaker.state == "open" or self.vector_search_breaker.state == "open":
            return "degraded"
        return "active"

    async def inject_stimulus(self, envelope: 'StimulusEnvelope') -> Dict[str, Any]:
        """
        Core injection logic.

        1. Deduplication check
        2. Route to correct graph(s)
        3. Call StimulusInjector mechanism
        4. Return metrics
        """
        # 1. Deduplication
        digest = hashlib.sha256(envelope.content.encode()).hexdigest()[:16]

        if digest in self.recent_digests:
            last_seen, count = self.recent_digests[digest]
            if time.time() - last_seen < 300:  # 5 min window
                self.recent_digests[digest] = (last_seen, count + 1)
                return {
                    "status": "deduplicated",
                    "digest": digest,
                    "count": count + 1
                }

        self.recent_digests[digest] = (time.time(), 1)

        # 2. Route to graph(s)
        graphs = self.determine_target_graphs(envelope.scope)

        results = []
        for graph_name in graphs:
            # 3. Call injector mechanism
            graph = self.db.select_graph(graph_name)

            try:
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.injector.inject,
                        graph=graph,
                        text=envelope.content,
                        embedding=None,  # Will compute internally
                        source_type=envelope.source_type,
                        metadata=envelope.metadata
                    ),
                    timeout=10.0
                )

                results.append({
                    "graph": graph_name,
                    "total_energy_injected": result.total_energy_injected,
                    "items_injected": result.items_injected,
                    "nodes_injected": result.nodes_injected,
                    "links_injected": result.links_injected
                })

            except asyncio.TimeoutError:
                self.logger.error(f"Injection timeout for graph {graph_name}")
                results.append({"graph": graph_name, "error": "timeout"})

        # 4. Update metrics
        self.metrics["processed_last_minute"] += 1

        return {
            "status": "injected",
            "stimulus_id": envelope.stimulus_id,
            "digest": digest,
            "results": results
        }

    def determine_target_graphs(self, scope: str) -> List[str]:
        """Route stimulus to correct graph(s) based on scope."""
        if scope == "personal":
            # TODO: Determine which citizen(s) - for Phase-A just inject to all
            return ["citizen_luca", "citizen_ada", "citizen_felix", "citizen_iris"]

        elif scope == "organizational":
            return ["mind_protocol_collective_graph"]

        elif scope == "ecosystem":
            return ["ecosystem_public_graph"]

        else:
            raise ValueError(f"Unknown scope: {scope}")

    def signal_handler(self, signum, frame):
        """Handle SIGTERM from guardian."""
        self.logger.info("Received SIGTERM, shutting down gracefully...")
        self.release_pid_lock()
        sys.exit(0)
```

### Pydantic Schemas

```python
class StimulusEnvelope(BaseModel):
    """
    Stimulus envelope schema for validation.

    Matches specification from AUTONOMY_INTEGRATION_ARCHITECTURE.md
    """
    stimulus_id: str = Field(..., description="Unique identifier (uuid-v4)")
    timestamp_ms: int = Field(..., description="Unix timestamp in milliseconds")
    scope: str = Field(..., description="Routing scope")
    source_type: str = Field(..., description="Source classification")
    actor: str = Field(..., description="Who/what generated this")
    content: str = Field(..., description="Text to process")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    focality_hint: str = Field(default="focal", description="Attention priority")
    privacy: str = Field(default="internal", description="Privacy level")
    interrupt: bool = Field(default=False, description="Should interrupt current processing")

    @validator('scope')
    def validate_scope(cls, v):
        if v not in ["personal", "organizational", "ecosystem"]:
            raise ValueError(f"Invalid scope: {v}")
        return v

    @validator('focality_hint')
    def validate_focality(cls, v):
        if v not in ["focal", "ambient", "background"]:
            raise ValueError(f"Invalid focality_hint: {v}")
        return v
```

### Circuit Breaker Implementation

```python
class CircuitBreaker:
    """
    Circuit breaker for external dependencies.

    States:
    - closed: Allow all requests
    - open: Block all requests (failed threshold crossed)
    - half_open: Allow one test request after recovery period
    """

    def __init__(self, threshold: int = 5, window: int = 60):
        self.threshold = threshold
        self.window = window
        self.failures = deque(maxlen=20)
        self.state = "closed"

    def record_failure(self):
        """Record a failure and potentially open circuit."""
        self.failures.append(time.time())
        recent = sum(1 for t in self.failures if time.time() - t < self.window)

        if recent >= self.threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker OPEN ({recent} failures in {self.window}s)")

    def record_success(self):
        """Record a success and potentially close circuit."""
        if self.state == "half_open":
            self.state = "closed"
            logger.info("Circuit breaker CLOSED (recovered)")

    def allow_request(self) -> bool:
        """Check if request is allowed."""
        if self.state == "closed":
            return True

        if self.state == "open":
            # Try half-open after 30s
            if self.failures and time.time() - self.failures[-1] > 30:
                self.state = "half_open"
                return True
            return False

        return True  # half_open allows test request
```

### FastAPI Application

```python
# Initialize service
service = StimulusInjectionService()
app = FastAPI(title="Stimulus Injection Service", version="1.0")

@app.on_event("startup")
async def startup():
    """Service startup initialization."""
    service.acquire_pid_lock()
    signal.signal(signal.SIGTERM, service.signal_handler)
    asyncio.create_task(service.heartbeat_writer())
    logger.info("Stimulus Injection Service started on port 8001")

@app.post("/inject")
async def inject(envelope: StimulusEnvelope):
    """
    Inject stimulus into consciousness substrate.

    Returns injection metrics.
    """
    try:
        result = await service.inject_stimulus(envelope)
        return result

    except Exception as e:
        logger.error(f"Injection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check for guardian monitoring."""
    return {
        "status": service.get_status(),
        "metrics": service.metrics
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
```

### Implementation Checklist

- [ ] Copy existing StimulusInjector mechanism (no modifications)
- [ ] Implement PID lock acquisition/release
- [ ] Implement heartbeat writer (asyncio background task)
- [ ] Implement SIGTERM handler
- [ ] Implement circuit breakers for embedding + vector search
- [ ] Implement deduplication tracking (digest-based, 5min window)
- [ ] Implement envelope validation (Pydantic)
- [ ] Implement routing logic (scope → graph_name)
- [ ] Implement injection with timeout (10s max)
- [ ] Implement metrics tracking
- [ ] Implement /inject endpoint
- [ ] Implement /health endpoint
- [ ] Test with sample stimuli (verify energy injection)
- [ ] Verify guardian can monitor heartbeat
- [ ] Verify guardian can restart on crash

---

## Service 2: autonomy_orchestrator.py

### Purpose

L2 organizational autonomy orchestrator. Monitors L2 graph for actionable signals, creates IntentCards, scores priority, evaluates safety gates, assigns to best executor, auto-wakes L1 citizens, tracks outcomes.

### File Location

`orchestration/autonomy_orchestrator.py`

### Dependencies

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import asyncio
import os
import sys
import signal
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import numpy as np
from scipy.stats import rankdata, norm
import logging
import requests
import time

from falkordb import FalkorDB
```

### Data Schemas

```python
class IntentCard(BaseModel):
    """
    Intent card - candidate work item with evidence.

    Stored as node in N2 graph.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    source_stimulus_id: str
    summary: str
    evidence_refs: List[str] = Field(default_factory=list)
    candidate_outcomes: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    risk_tags: List[str] = Field(default_factory=list)

    # Computed scores
    priority_score: Optional[float] = None
    autonomy_level: Optional[str] = None  # "L0" | "L1" | "L2" | "L3" | "L4"
    assigned_to: Optional[str] = None

    # Gate scores
    pog_score: Optional[float] = None  # Proof of Grounding
    poc_score: Optional[float] = None  # Proof of Competence
    pop_score: Optional[float] = None  # Proof of Permission

    # Phase-A: Reduced priority features
    urgency: float = 0.5
    alignment: float = 0.5
    confidence: float = 0.5
```

### Class Structure

```python
class AutonomyOrchestrator:
    """
    L2 organizational autonomy orchestrator.

    Phase-A scope:
    - Ingest agent answers only (not errors/logs yet)
    - Create intents for clarify/continue tasks
    - Score with {urgency, alignment, confidence}
    - Gate to L2/L3 only (no L4 auto-exec)
    - Assign to same citizen (self-handoff)
    - Require ≥1 evidence link for verification
    """

    def __init__(self):
        """Initialize orchestrator."""
        # Operational
        self.pid_lock = Path(".autonomy_orchestrator.lock")
        self.heartbeat_file = Path(".heartbeats/autonomy_orchestrator.heartbeat")
        self.logger = logging.getLogger(__name__)

        # Graph access
        self.db = FalkorDB()
        self.l2_graph = self.db.select_graph("mind_protocol_collective_graph")

        # Active intents (in-memory for Phase-A)
        self.active_intents: List[IntentCard] = []

        # Metrics
        self.metrics = {
            "active_intents": 0,
            "pending_missions": 0,
            "gate_pass_rates": {"PoG": 0.0, "PoC": 0.0, "PoP": 0.0}
        }

    async def orchestration_loop(self):
        """
        Main orchestration loop.

        Phase-A: Simple polling every 30s
        Phase-B+: Event-driven from Redis Streams
        """
        while True:
            try:
                # Check for new stimuli in L2 graph
                await self.check_for_new_stimuli()

                # Process active intents
                await self.process_active_intents()

                # Update metrics
                self.update_metrics()

            except Exception as e:
                self.logger.error(f"Orchestration loop error: {e}")

            await asyncio.sleep(30)  # Phase-A: poll every 30s

    async def check_for_new_stimuli(self):
        """
        Check L2 graph for new stimuli that need intent creation.

        Phase-A: Look for agent_response source_type only
        """
        # Query for recent stimuli not yet processed
        query = """
        MATCH (s:Stimulus)
        WHERE s.source_type = 'agent_response'
          AND NOT EXISTS((s)-[:GENERATED_INTENT]->())
          AND s.timestamp_ms > $since_ms
        RETURN s.id, s.content, s.metadata
        LIMIT 10
        """

        since_ms = int((time.time() - 300) * 1000)  # Last 5 minutes
        result = self.l2_graph.query(query, params={"since_ms": since_ms})

        for record in result.result_set:
            stimulus_id, content, metadata = record
            await self.create_intent_from_stimulus(stimulus_id, content, metadata)

    async def create_intent_from_stimulus(
        self,
        stimulus_id: str,
        content: str,
        metadata: Dict
    ):
        """
        Create IntentCard from stimulus.

        Phase-A: Simple pattern matching for clarify/continue
        Phase-B+: LLM-based intent proposal
        """
        # Simplified intent creation for Phase-A
        if "clarify" in content.lower() or "?" in content:
            summary = "Clarify previous response"
            outcomes = ["Provide clarification", "Request more context"]

        elif "continue" in content.lower():
            summary = "Continue previous work"
            outcomes = ["Build on previous response", "Iterate"]

        else:
            # No clear intent, skip
            return

        # Create IntentCard
        intent = IntentCard(
            source_stimulus_id=stimulus_id,
            summary=summary,
            evidence_refs=[],  # TODO: Retrieve from graph
            candidate_outcomes=outcomes,
            required_capabilities=["reasoning"],
            risk_tags=[],
            urgency=0.6,
            alignment=0.7,
            confidence=0.5
        )

        self.active_intents.append(intent)
        self.logger.info(f"Created intent: {intent.summary}")

    async def process_active_intents(self):
        """
        Process all active intents through the 9-stage loop.

        Phase-A: Simplified stages
        """
        for intent in self.active_intents:
            if intent.assigned_to is not None:
                continue  # Already assigned

            # Stage B: Priority scoring (Phase-A: reduced)
            intent.priority_score = self.compute_priority_score_phase_a(intent)

            # Stage C: Safety gates
            pog = self.evaluate_proof_of_grounding(intent)
            poc = 0.7  # Phase-A: default competence
            pop = 1.0  # Phase-A: assume permissions OK

            intent.pog_score = pog
            intent.poc_score = poc
            intent.pop_score = pop

            gates_passed = pog >= 0.3  # Phase-A: minimal PoG threshold

            if not gates_passed:
                self.logger.warning(f"Intent {intent.id} failed PoG gate ({pog:.2f})")
                continue

            # Stage D: Autonomy level (Phase-A: L2/L3 only)
            intent.autonomy_level = self.decide_autonomy_level_phase_a(intent)

            # Stage E: Assignment (Phase-A: self-handoff)
            assignee = self.determine_source_citizen(intent.source_stimulus_id)
            intent.assigned_to = assignee

            # Stage F: Auto-wake L1
            await self.send_mission(intent)

    def compute_priority_score_phase_a(self, intent: IntentCard) -> float:
        """
        Phase-A priority: Simple average of urgency, alignment, confidence.

        Phase-B+: Full geometric mean with cohort normalization
        """
        return (intent.urgency + intent.alignment + intent.confidence) / 3

    def evaluate_proof_of_grounding(self, intent: IntentCard) -> float:
        """
        PoG: Evidence coverage score.

        Phase-A: Count of evidence refs (simple)
        Phase-B+: High-weight evidence + distinct sources
        """
        return len(intent.evidence_refs) * 0.5

    def decide_autonomy_level_phase_a(self, intent: IntentCard) -> str:
        """
        Phase-A: L2 (ACK required) or L3 (auto-execute in sandbox).

        Phase-B+: Learned contours from historical outcomes
        """
        if intent.priority_score > 0.7:
            return "L3"  # Auto-execute
        else:
            return "L2"  # ACK required

    def determine_source_citizen(self, stimulus_id: str) -> str:
        """
        Phase-A: Self-handoff (same citizen that generated stimulus).

        Query graph to find which citizen created the stimulus.
        """
        query = """
        MATCH (s:Stimulus {id: $stimulus_id})<-[:CREATED]-(c)
        WHERE c:AI_Agent
        RETURN c.name
        """

        result = self.l2_graph.query(query, params={"stimulus_id": stimulus_id})

        if result.result_set:
            return result.result_set[0][0]
        else:
            return "luca"  # Default fallback

    async def send_mission(self, intent: IntentCard):
        """
        Send mission stimulus to citizen via stimulus_injection_service.
        """
        mission_envelope = {
            "stimulus_id": f"mission-{intent.id}",
            "timestamp_ms": int(time.time() * 1000),
            "scope": "personal",
            "source_type": "org_intent_assignment",
            "actor": "autonomy_orchestrator",
            "content": self.format_mission_brief(intent),
            "metadata": {
                "intent_id": intent.id,
                "evidence_refs": intent.evidence_refs,
                "autonomy_level": intent.autonomy_level
            },
            "focality_hint": "focal",
            "interrupt": True
        }

        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    requests.post,
                    "http://localhost:8001/inject",
                    json=mission_envelope
                ),
                timeout=5.0
            )

            if response.status_code == 200:
                self.logger.info(f"Mission sent to {intent.assigned_to} for intent {intent.id}")
            else:
                self.logger.error(f"Mission send failed: {response.status_code}")

        except asyncio.TimeoutError:
            self.logger.error("Mission send timeout")

    def format_mission_brief(self, intent: IntentCard) -> str:
        """Format mission brief for citizen consumption."""
        return f"""
Mission Assignment (L2 Autonomy)

Intent: {intent.summary}

Outcomes to consider:
{chr(10).join(f"- {o}" for o in intent.candidate_outcomes)}

Evidence refs: {', '.join(intent.evidence_refs[:5])}

Autonomy level: {intent.autonomy_level}
Required: At least one evidence link in your response
"""

    def update_metrics(self):
        """Update metrics for heartbeat."""
        self.metrics["active_intents"] = len(self.active_intents)
        self.metrics["pending_missions"] = sum(
            1 for i in self.active_intents if i.assigned_to is not None
        )

    # [Operational contract methods same as stimulus_injection_service]
    # acquire_pid_lock(), release_pid_lock(), heartbeat_writer(), etc.
```

### FastAPI Application

```python
# Initialize orchestrator
orchestrator = AutonomyOrchestrator()
app = FastAPI(title="Autonomy Orchestrator", version="1.0")

@app.on_event("startup")
async def startup():
    """Service startup."""
    orchestrator.acquire_pid_lock()
    signal.signal(signal.SIGTERM, orchestrator.signal_handler)
    asyncio.create_task(orchestrator.heartbeat_writer())
    asyncio.create_task(orchestrator.orchestration_loop())
    logger.info("Autonomy Orchestrator started on port 8002")

@app.get("/health")
async def health():
    """Health check for guardian."""
    return {
        "status": "active",
        "metrics": orchestrator.metrics
    }

@app.get("/intents")
async def get_intents():
    """List active intents (for debugging)."""
    return {
        "active_intents": [i.dict() for i in orchestrator.active_intents]
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        log_level="info"
    )
```

### Implementation Checklist

- [ ] Implement operational contract (PID lock, heartbeat, SIGTERM)
- [ ] Implement orchestration loop (30s polling for Phase-A)
- [ ] Implement stimulus detection (query L2 for agent_response stimuli)
- [ ] Implement intent creation (simple pattern matching)
- [ ] Implement priority scoring (Phase-A: simple average)
- [ ] Implement PoG evaluation (count evidence refs)
- [ ] Implement autonomy level decision (L2/L3 based on priority)
- [ ] Implement assignment logic (self-handoff via graph query)
- [ ] Implement mission dispatch (POST to stimulus_injection_service)
- [ ] Implement mission brief formatting
- [ ] Implement /health endpoint
- [ ] Implement /intents endpoint (debugging)
- [ ] Test end-to-end flow (stimulus → intent → mission → execution)
- [ ] Verify guardian can monitor and restart

---

## Testing Strategy

### Unit Tests

```python
# Test stimulus injection service
def test_envelope_validation():
    """Test Pydantic envelope validation."""
    valid = StimulusEnvelope(
        stimulus_id="test-001",
        timestamp_ms=1739990123456,
        scope="personal",
        source_type="test",
        actor="unit_test",
        content="Test content"
    )
    assert valid.scope == "personal"

def test_deduplication():
    """Test digest-based deduplication."""
    service = StimulusInjectionService()
    # Send same stimulus twice within 5min
    # Second should be deduplicated

def test_circuit_breaker():
    """Test circuit breaker state transitions."""
    breaker = CircuitBreaker(threshold=3, window=10)
    # Record 3 failures → state should be "open"
    # Wait 30s → state should be "half_open"
    # Record success → state should be "closed"
```

### Integration Tests

```python
async def test_end_to_end_autonomy():
    """
    Test complete autonomy flow:
    1. Send stimulus to L2
    2. Verify intent created
    3. Verify mission sent to citizen
    4. Verify citizen executes
    5. Verify outcome recorded
    """
    # 1. Send stimulus
    response = requests.post("http://localhost:8001/inject", json={
        "stimulus_id": "integration-test-001",
        "scope": "organizational",
        "source_type": "agent_response",
        "actor": "luca",
        "content": "Can you clarify the authentication mechanism?"
    })
    assert response.status_code == 200

    # 2. Wait for orchestrator to detect
    await asyncio.sleep(35)  # Polling interval + processing

    # 3. Check intent created
    intents = requests.get("http://localhost:8002/intents").json()
    assert len(intents["active_intents"]) > 0

    # 4. Verify mission sent
    # (Check stimulus_injection logs or heartbeat metrics)

    # 5. Wait for execution
    # (Monitor conversation_watcher for TRACE response)
```

---

## Deployment Checklist

- [ ] Create `orchestration/stimulus_injection_service.py`
- [ ] Create `orchestration/autonomy_orchestrator.py`
- [ ] Update `guardian.py` with service definitions
- [ ] Update `start_mind_protocol.py` with startup methods
- [ ] Create `.heartbeats/` directory
- [ ] Test startup sequence (FalkorDB → websocket → watcher → injection → orchestrator)
- [ ] Verify guardian can monitor both services
- [ ] Verify guardian can restart on crash
- [ ] Test circuit breaker recovery
- [ ] Test end-to-end autonomy flow
- [ ] Monitor for 1 hour (verify no crashes)
- [ ] Document any issues encountered
- [ ] Handoff to Phase-B when stable

---

**Next Document:** FULL_AUTONOMY_VISION.md (complete 7-service architecture for Phase-B/C)
