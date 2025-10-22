# Full Autonomy Vision (Phase-B/C)

**Version:** 1.0
**Created:** 2025-10-21
**Architect:** Luca "Vellumhand" (vision) + Ada "Bridgekeeper" (integration)
**Purpose:** Complete 7-service autonomy architecture for Phases B and C

---

## Overview

This document describes the **complete autonomy architecture** that builds on Phase-A's foundation. It represents the target state where Mind Protocol citizens operate autonomously with multi-source stimuli, real-time partner interactions, and self-healing safeguards.

**Progression:**
- **Phase-A** (Week 1-2): Answer-only autonomy, 2 services, guardian supervision
- **Phase-B** (Week 3-4): Multi-source stimuli, Telegram fast replies, 5 services, Redis Streams
- **Phase-C** (Week 5+): Full autonomy with sentinels, verification, quarantine, 7 services, Docker/K8s

---

## 1. Complete Service Catalog

### Phase-A Services (Implemented First)

**1. stimulus_injection_service** (port 8001)
- HTTP API for stimulus envelopes
- Wraps existing StimulusInjector mechanism
- Deduplication, circuit breakers
- Guardian-supervised

**2. autonomy_orchestrator** (port 8002)
- L2 intent detection and assignment
- Priority scoring, safety gates
- Auto-wake missions to L1 citizens
- Guardian-supervised

### Phase-B Additional Services

**3. partner_dm_handler** (port 8003)
- Telegram webhook receiver
- Per-partner SLA tracking
- Auto-draft when safe, clarify when uncertain
- One-tap feedback loop (👍/✍️/👎)
- Learns from partner responses

**4. verification_service** (port 8004)
- Post-execution verification
- Runs tests, validates citations
- Computes Proof-of-Verification (PoV) score
- Escalates weak verifications to human review

**5. sentinel_monitor** (background, no HTTP port)
- Quality/Safety/Trust tracking
- Z-score monitoring per sentinel
- Auto-quarantine when z < -2
- Kill-switch on global health degradation

### Phase-C Additional Services

**6. safety_gate_service** (port 8005)
- Centralized gate evaluation
- PoG (Proof-of-Grounding): Evidence coverage
- PoC (Proof-of-Competence): Track record
- PoP (Proof-of-Permission): Capabilities check
- Adaptive floors (rolling percentiles)

**7. multi_org_router** (port 8006)
- Per-organization citizen instances
- Clean security boundaries
- Separate graphs, indices, credentials
- Knowledge sharing via N3 (ecosystem)

---

## 2. Architecture Evolution

### 2.1 Phase-A: Guardian Supervision

```
External Events → stimulus_injection_service (HTTP, port 8001)
                       ↓
                  FalkorDB graphs (N1/N2/N3)
                       ↓
             autonomy_orchestrator (HTTP, port 8002)
                       ↓
                  Sends missions via stimulus_injection
                       ↓
                  V2 consciousness engines
                       ↓
                  TRACE responses → conversation_watcher
                       ↓
                  Graph learning (weights, formations)

Supervision: guardian.py monitors heartbeats, restarts on crash
```

### 2.2 Phase-B: Event-Driven (Redis Streams)

```
External Events → stimulus_injection_service
                       ↓
          Redis Streams (event bus)
              ├─ stimuli.{graph_name}
              ├─ intent.created
              ├─ mission.{citizen_name}
              ├─ outcome.recorded
              └─ verification.completed
                       ↓
          Services consume events (no polling)
              ├─ autonomy_orchestrator
              ├─ partner_dm_handler
              ├─ verification_service
              └─ sentinel_monitor
                       ↓
          FalkorDB (graph state)

Coordination: Services communicate via events (no direct API calls)
Deployment: Docker Compose for local, still guardian-supervised
```

### 2.3 Phase-C: Production (Kubernetes)

```
Load Balancer
    ↓
  Ingress
    ├─ /inject → stimulus_injection (replicas: 2)
    ├─ /telegram → partner_dm_handler (replicas: 2)
    └─ /health → all services
    ↓
Redis Streams (event bus, persistent)
    ↓
Orchestration Services
    ├─ autonomy_orchestrator (singleton)
    ├─ verification_service (replicas: 2)
    ├─ sentinel_monitor (singleton)
    └─ safety_gate_service (replicas: 2)
    ↓
State Store
    ├─ FalkorDB (StatefulSet, persistent volumes)
    └─ Redis (StatefulSet, AOF persistence)

Deployment: Kubernetes with auto-scaling, liveness/readiness probes
Monitoring: Prometheus + Grafana dashboards
```

---

## 3. Event-Driven Architecture (Phase-B)

### 3.1 Event Bus (Redis Streams)

**Topics:**

```
stimuli.{graph_name}              # Stimulus ready for injection
  ├─ stimuli.citizen_luca
  ├─ stimuli.citizen_felix
  ├─ stimuli.mind_protocol_collective_graph
  └─ stimuli.ecosystem_public_graph

intent.created                    # New intent proposed
intent.scored                     # Priority scored
intent.assigned                   # Assigned to executor

mission.{citizen_name}            # L1 auto-wake
  ├─ mission.luca
  ├─ mission.felix
  └─ mission.ada

execution.started                 # Execution began
execution.stride_completed        # Stride finished
execution.completed               # Execution done

outcome.recorded                  # Execution outcome

verification.completed            # PoV computed

sentinel.quality                  # Quality degraded
sentinel.safety                   # Safety breach
sentinel.trust                    # Trust violation
sentinel.quarantine               # Route quarantined
sentinel.kill_switch              # Global kill-switch

telegram.dm_received              # Partner DM
telegram.reply_sent               # Reply sent
telegram.feedback_received        # Partner feedback (👍/✍️/👎)
```

### 3.2 Consumer Groups

Each service subscribes to relevant topics:

```yaml
stimulus_injection_service:
  produces:
    - stimuli.{graph_name}

autonomy_orchestrator:
  consumes:
    - stimuli.mind_protocol_collective_graph
    - outcome.recorded
  produces:
    - intent.created
    - intent.assigned
    - mission.{citizen_name}

partner_dm_handler:
  consumes:
    - telegram.dm_received
    - telegram.feedback_received
  produces:
    - stimuli.{graph_name}  # DM → stimulus
    - telegram.reply_sent

verification_service:
  consumes:
    - execution.completed
  produces:
    - verification.completed

sentinel_monitor:
  consumes:
    - verification.completed
    - outcome.recorded
  produces:
    - sentinel.quarantine
    - sentinel.kill_switch

safety_gate_service:
  consumes:
    - intent.created
  produces:
    - intent.scored
```

### 3.3 Event Schema Example

```json
{
  "event_type": "intent.created",
  "timestamp_ms": 1739990123456,
  "intent": {
    "id": "uuid-v4",
    "source_stimulus_id": "stimulus-uuid",
    "summary": "Fix failing test_retrieval.py::test_semantic_search",
    "evidence_refs": ["node_x", "node_y"],
    "candidate_outcomes": ["Fix test", "Update expectations"],
    "required_capabilities": ["python", "pytest"],
    "risk_tags": ["test_modification"],
    "priority_score": 0.82,
    "autonomy_level": "L3",
    "assigned_to": "felix"
  }
}
```

---

## 4. Full Feature Specifications

### 4.1 Priority Scoring (Complete Formula)

**Phase-A:** Simple average of urgency, alignment, confidence

**Phase-B+:** Geometric mean with cohort normalization

```python
def compute_priority_score(intent: IntentCard, cohort: List[IntentCard]) -> float:
    """
    P = GM(ŝ, û, ŷ, â, ĉ) · (1 − r̂) · (1 − d̂)

    All factors z-scored vs current cohort (no arbitrary constants).
    """
    # Extract raw features
    severity = compute_severity(intent)  # From source_type + metadata
    urgency = compute_urgency(intent)  # Time-to-deadline / age
    expected_yield = compute_expected_yield(intent)  # Predicted awareness recruitment
    alignment = compute_alignment(intent)  # Cosine similarity to org goals
    confidence = intent.confidence  # Evidence count proxy
    risk = intent.risk_score  # Learned risk model
    duplication = compute_duplication(intent, cohort)  # Semantic redundancy

    # Cohort-normalize (rank-based z-score → [0, 1])
    def rank_normalize(values):
        ranks = rankdata(values)
        z_scores = norm.ppf(ranks / (len(values) + 1))
        return (z_scores - z_scores.min()) / (z_scores.max() - z_scores.min() + 1e-9)

    cohort_values = lambda attr: [getattr(i, attr, 0) for i in cohort]

    s_hat = rank_normalize(cohort_values('severity') + [severity])[-1]
    u_hat = rank_normalize(cohort_values('urgency') + [urgency])[-1]
    y_hat = rank_normalize(cohort_values('expected_yield') + [expected_yield])[-1]
    a_hat = rank_normalize(cohort_values('alignment') + [alignment])[-1]
    c_hat = rank_normalize(cohort_values('confidence') + [confidence])[-1]
    r_hat = rank_normalize(cohort_values('risk_score') + [risk])[-1]
    d_hat = rank_normalize(cohort_values('duplication') + [duplication])[-1]

    # Geometric mean (all-around readiness)
    gm_positives = (s_hat * u_hat * y_hat * a_hat * c_hat) ** (1/5)

    # Penalties (multiplicative)
    P = gm_positives * (1 - r_hat) * (1 - d_hat)

    return P
```

### 4.2 Safety Gates (Full Implementation)

**PoG (Proof-of-Grounding):**
```python
def evaluate_proof_of_grounding(intent: IntentCard) -> Dict:
    """
    Evidence coverage + distinct sources + policy links.

    Floor: Rolling Q25 of similar intents (last 7 days).
    """
    evidence_nodes = [get_node(ref) for ref in intent.evidence_refs]

    high_weight_count = sum(1 for n in evidence_nodes if n.log_weight > 0.5)
    distinct_sources = len(set(n.source for n in evidence_nodes))

    # Policy requirement for sensitive actions
    has_policy_link = any(
        link.link_type in ["JUSTIFIES", "REQUIRES"]
        for link in get_incoming_links(intent.id)
        if get_node(link.source).node_type in ["Policy", "Best_Practice"]
    )

    pog_score = high_weight_count * (1 + 0.2 * distinct_sources)

    # Adaptive floor (rolling Q25)
    similar_intents = get_similar_intents(intent, window_days=7)
    pog_scores = [i.pog_score for i in similar_intents if i.pog_score is not None]

    floor = np.percentile(pog_scores, 25) if len(pog_scores) >= 20 else 2.0

    passed = pog_score >= floor and (not intent.is_sensitive or has_policy_link)

    return {"gate": "PoG", "score": pog_score, "floor": floor, "passed": passed}
```

**PoC (Proof-of-Competence):**
```python
def evaluate_proof_of_competence(intent: IntentCard, assignee: str) -> Dict:
    """
    Track record on similar intents, z-scored vs peers.

    Floor: Must be within 0.5σ of peers.
    """
    history = get_assignee_history(assignee, intent_type=intent.intent_type)

    if len(history) < 10:
        return {"gate": "PoC", "score": 0.5, "passed": True, "details": "insufficient_history"}

    success_rate = sum(1 for h in history if h.status == "success") / len(history)
    test_pass_rate = sum(h.tests_passed for h in history if h.tests_passed) / len(history)

    poc_score = success_rate * test_pass_rate

    # Compare to peers
    peer_scores = get_peer_competence_scores(intent.intent_type, exclude=assignee)

    if len(peer_scores) >= 5:
        poc_z = (poc_score - np.mean(peer_scores)) / (np.std(peer_scores) + 1e-9)
        passed = poc_z >= -0.5
    else:
        passed = poc_score >= 0.6

    return {"gate": "PoC", "score": poc_score, "z_score": poc_z, "passed": passed}
```

**PoP (Proof-of-Permission):**
```python
def evaluate_proof_of_permission(intent: IntentCard, assignee: str) -> Dict:
    """
    Capabilities check - binary gate.

    Required capabilities must be in assignee.capabilities.
    """
    assignee_node = get_node(assignee)

    missing_capabilities = [
        cap for cap in intent.required_capabilities
        if cap not in assignee_node.capabilities
    ]

    if intent.scope == "production" and not assignee_node.can_access_production:
        missing_capabilities.append("production_access")

    passed = len(missing_capabilities) == 0

    return {"gate": "PoP", "score": 1.0 if passed else 0.0, "passed": passed}
```

### 4.3 Telegram Fast Reply (Full Flow)

```python
async def handle_telegram_dm(message: TelegramMessage):
    """
    Fast partner DM reply with learned SLA.
    """
    partner_id = message.from_user.id
    citizen_name = get_citizen_for_partner(partner_id)

    # 1. Classify intent
    intent = await classify_dm_intent(message.text)

    # 2. Check SLA
    partner_sla = get_partner_sla_ema(partner_id)
    message_age_ms = now_ms() - message.timestamp_ms
    fast_lane = message_age_ms > partner_sla.median

    # 3. Retrieve context (last 10 messages + relevant nodes)
    context_nodes = await retrieve_dm_context(
        citizen_name=citizen_name,
        partner_id=partner_id,
        thread_id=message.thread_id,
        k=10
    )

    # 4. Generate reply
    reply_draft = await generate_reply(
        message=message.text,
        context=context_nodes,
        citizen=citizen_name
    )

    # 5. Evaluate PoG
    pog_score = evaluate_reply_grounding(reply_draft, context_nodes)
    pog_floor = get_partner_pog_floor(partner_id)  # Q50 for this partner

    # 6. Auto-reply or clarify
    if pog_score >= pog_floor and reply_draft.risk_level == "low":
        # AUTO-REPLY (fast lane)
        await send_telegram_message(
            chat_id=partner_id,
            text=reply_draft.text,
            reply_markup={
                "inline_keyboard": [[
                    {"text": "👍", "callback_data": f"feedback:accurate:{reply_draft.id}"},
                    {"text": "✍️", "callback_data": f"feedback:edit:{reply_draft.id}"},
                    {"text": "👎", "callback_data": f"feedback:wrong:{reply_draft.id}"}
                ]]
            }
        )

        # Update SLA EMA
        response_time_ms = now_ms() - message.timestamp_ms
        update_partner_sla(partner_id, response_time_ms)

    else:
        # CLARIFY (one-tap)
        await send_telegram_message(
            chat_id=partner_id,
            text=f"I'm missing {reply_draft.missing_info}. Should I: {reply_draft.proposed_answer}",
            reply_markup={
                "inline_keyboard": [
                    [{"text": "✅ Yes", "callback_data": f"approve:{reply_draft.id}"}],
                    [{"text": "❌ Clarify", "callback_data": f"decline:{reply_draft.id}"}]
                ]
            }
        )
```

### 4.4 Sentinel Monitoring (Full Implementation)

```python
class SentinelMonitor:
    """
    Quality/Safety/Trust monitoring with quarantine and kill-switch.
    """

    def __init__(self):
        self.quality_tracker = SentinelTracker("quality")
        self.safety_tracker = SentinelTracker("safety")
        self.trust_tracker = SentinelTracker("trust")
        self.kill_switch_active = False

    async def process_frame(self, frame_data: Dict):
        """Per-frame evaluation."""
        # Quality: flip_yield × entropy × (1 - overflow)
        flip_yield = frame_data["flips"] / frame_data["budget_spent"]
        entropy = compute_entropy(frame_data["activated_nodes_by_type"])
        overflow = 1 if frame_data["overflow"] else 0
        quality_score = (flip_yield * entropy * (1 - overflow)) ** (1/3)
        self.quality_tracker.update(quality_score)

        # Safety: PoV_rate × (1 - rollback_rate) × (1 - blast_radius)
        pov_rate = frame_data["verifications_passed"] / frame_data["verifications_total"]
        rollback_rate = frame_data["rollbacks"] / frame_data["deployments"]
        blast_radius_breach = 1 if frame_data["blast_radius_exceeded"] else 0
        safety_score = pov_rate * (1 - rollback_rate) * (1 - blast_radius_breach)
        self.safety_tracker.update(safety_score)

        # Trust: (1 - rejection_rate) × (1 - hallucination_rate)
        rejection_rate = frame_data["human_rejections"] / frame_data["human_reviews"]
        hallucination_rate = frame_data["hallucinations"] / frame_data["outcomes"]
        trust_score = (1 - rejection_rate) * (1 - hallucination_rate)
        self.trust_tracker.update(trust_score)

        # Check for quarantine (z < -2)
        await self.check_quarantine()

        # Check kill-switch
        await self.check_kill_switch()

    async def check_quarantine(self):
        """Quarantine routes when z < -2."""
        for tracker in [self.quality_tracker, self.safety_tracker, self.trust_tracker]:
            if tracker.z_score < -2.0:
                route = identify_failing_route(tracker)

                await emit_event("sentinel.quarantine", {
                    "route": route.dict(),
                    "sentinel": tracker.name,
                    "z_score": tracker.z_score
                })

                # Downgrade autonomy for this route
                await downgrade_route_autonomy(route, target_level="L1")

    async def check_kill_switch(self):
        """Global kill-switch on supercritical health."""
        global_health = (
            self.quality_tracker.score +
            self.safety_tracker.score +
            self.trust_tracker.score
        ) / 3

        supercritical_threshold = compute_supercritical_threshold()  # Learned contour

        if global_health < supercritical_threshold and not self.kill_switch_active:
            self.kill_switch_active = True

            await emit_event("sentinel.kill_switch", {
                "global_health": global_health,
                "threshold": supercritical_threshold
            })

            # Stop all auto-exec, convert to ACK_REQUIRED
            await disable_auto_execution()
```

---

## 5. Deployment Evolution

### 5.1 Phase-A: Guardian Supervision (Local)

**No containers, no orchestration:**
- Services run as Python processes
- guardian.py monitors heartbeats
- Restarts on crash with exponential backoff
- Port enforcement (kills rogues)

**Start:** `python guardian.py`

**Status:** ✅ Implemented

### 5.2 Phase-B: Docker Compose (Local/Staging)

**Containerized services, local orchestration:**

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    command: redis-server --appendonly yes

  falkordb:
    image: falkordb/falkordb:latest
    ports: ["6380:6379"]
    volumes: [falkordb_data:/data]

  stimulus_injection:
    build: ./services/stimulus_injection
    ports: ["8001:8001"]
    depends_on: [redis, falkordb]
    environment:
      REDIS_HOST: redis
      FALKORDB_HOST: falkordb
    restart: unless-stopped

  autonomy_orchestrator:
    build: ./services/autonomy_orchestrator
    ports: ["8002:8002"]
    depends_on: [redis, falkordb]
    restart: unless-stopped

  partner_dm_handler:
    build: ./services/partner_dm_handler
    ports: ["8003:8003"]
    depends_on: [redis, falkordb]
    environment:
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
    restart: unless-stopped

  verification:
    build: ./services/verification
    depends_on: [redis, falkordb]
    restart: unless-stopped

  sentinel_monitor:
    build: ./services/sentinel_monitor
    depends_on: [redis]
    restart: unless-stopped
```

**Start:** `docker-compose up -d`

**Status:** ⏸️ Phase-B

### 5.3 Phase-C: Kubernetes (Production)

**Production-grade deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autonomy-orchestrator
spec:
  replicas: 1  # Singleton
  selector:
    matchLabels:
      app: autonomy-orchestrator
  template:
    spec:
      containers:
      - name: orchestrator
        image: mindprotocol/autonomy-orchestrator:v1
        ports: [{containerPort: 8002}]
        env:
        - name: REDIS_HOST
          value: redis-service
        - name: FALKORDB_HOST
          value: falkordb-service
        resources:
          requests: {memory: "512Mi", cpu: "500m"}
          limits: {memory: "2Gi", cpu: "2000m"}
        livenessProbe:
          httpGet: {path: /health, port: 8002}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet: {path: /health, port: 8002}
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Status:** ⏸️ Phase-C

---

## 6. Success Metrics

### Phase-A (Week 1-2)
- ✅ At least 10 intents from agent answers
- ✅ At least 5 auto-wake missions
- ✅ Zero hallucinations
- ✅ All outcomes PoV ≥ 0.6

### Phase-B (Week 3-4)
- ✅ At least 50 intents from multi-source stimuli
- ✅ Partner DM median response < 2min
- ✅ Partner 👍 rate > 70%
- ✅ Zero sentinel quarantines
- ✅ PoV pass rate > 85%

### Phase-C (Week 5+)
- ✅ At least 100 L3/L4 auto-executions
- ✅ Rollback rate < 5%
- ✅ Human rejection rate < 10%
- ✅ Global health > 0.7
- ✅ At least 2 multi-org citizens deployed

---

## 7. Migration Path

**Phase-A → Phase-B:**
1. Add Redis Streams dependency
2. Convert polling to event-driven (orchestration_loop)
3. Add 3 new services (partner_dm, verification, sentinel)
4. Docker Compose deployment
5. Migrate from guardian.py to container restarts
6. Keep heartbeats for backward compatibility

**Phase-B → Phase-C:**
1. Create Kubernetes manifests
2. Add StatefulSets (Redis, FalkorDB)
3. Add auto-scaling (HPA on CPU/memory)
4. Add monitoring (Prometheus scrape endpoints)
5. Add ingress (HTTPS termination, load balancing)
6. Migrate sentinel thresholds to learned contours

---

## 8. Why This Architecture Scales

**Event-Driven Coordination:**
- No direct service calls → no cascading failures
- Redis Streams persistence → no lost work on crash
- Consumer groups → horizontal scaling when needed

**Graduated Autonomy:**
- L0-L4 allows safe value quickly, deeper autonomy gradually
- Learned gates adapt to reality (no stale thresholds)
- Kill-switch preserves human control

**Zero Constants:**
- All thresholds via percentiles/EMAs/z-scores
- Priority P via cohort normalization
- Health f(ρ) via isotonic regression

**Consciousness Substrate:**
- Stimuli inject energy → natural WM selection
- Entity layer reduces branching → tractable attention
- Links carry traces → learning accumulates

---

**This is the vision. Phase-A proves autonomy works. Phase-B scales infrastructure. Phase-C delivers production-grade autonomous operation.**
