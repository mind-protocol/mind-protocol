# L2 Stimulus Collector Specification

**Created:** 2025-10-26
**Status:** Normative
**Depends on:** cross_level_membrane.md, stimulus_injection.py
**Author:** Luca (Consciousness Architect)

---

## Purpose

**The L2 Stimulus Collector captures citizen activity and converts it into L2 stimuli.**

This enables upward flow (L1→L2): when citizens work, learn, create, and respond, those activities become stimuli for the organizational consciousness to process.

**What gets collected:**
1. **File operations** - Code/doc creates, edits, deletes
2. **TRACE formations** - New nodes and links from citizen responses
3. **Git operations** - Commits, branches, merges
4. **Conversation responses** - Completed citizen responses to humans/citizens

**Architecture principle:** Stimulus Collector feeds the normal injection pipeline. It doesn't bypass energy mechanics - it creates canonical stimulus envelopes that flow through Stimulus Integrator like any other stimulus.

---

## Why This Matters

**Without L2 Stimulus Collector:**
- L2 remains blind to citizen activity
- Upward membrane has no events to evaluate
- Organization can't learn from individual work
- Cross-level consciousness is one-way (L2→L1 only)

**With L2 Stimulus Collector:**
- Every citizen action becomes potential L2 stimulus
- Spam resistance via Stimulus Integrator mechanics (saturation, trust, novelty)
- Membrane evaluates significance and emits only record events
- Organization learns from emergent patterns across citizens

---

## Architecture Overview

```
Citizen Activity Sources:
  ├─ File Watcher (creates/edits/deletes)
  ├─ TRACE Parser (formations from responses)
  ├─ Git Hook (commits/branches)
  └─ Response Completer (conversation turns)
          ↓
L2StimulusCollector (THIS SPEC)
  ├─ Extract semantic signals
  ├─ Build canonical envelope
  ├─ Enrich with provenance
  ├─ Apply learned pre-filters (NOT spam gates - those are in Integrator)
          ↓
Stimulus Injection Service
  ├─ Routes to scope=organizational (L2 graph)
  ├─ Stimulus Integrator (saturation, trust, harm gating)
  ├─ Energy injection → L2 nodes
          ↓
CrossLevelMembrane
  ├─ Evaluates L2 node flips
  ├─ Record events → Emit upward stimulus
```

**Key insight:** L2StimulusCollector creates envelopes. Spam resistance happens in Stimulus Integrator. Significance filtering happens in Membrane. Clean separation of concerns.

---

## Event Sources

### 1. File Operations

**What to capture:**
- File creates (new scripts, specs, components)
- File edits (code changes, spec updates)
- File deletes (cleanup, deprecation)
- File renames/moves

**How to capture:**
- Existing `conversation_watcher.py` pattern (file system watching)
- Watch paths: `orchestration/**/*.py`, `app/**/*.tsx`, `docs/specs/**/*.md`

**Signal extraction:**
```python
def extract_file_op_signals(event: FileSystemEvent) -> Dict:
    """
    Extract semantic signals from file operation.

    Returns canonical features for stimulus envelope.
    """
    # Determine file importance (not arbitrary - learned from retrieval patterns)
    importance = estimate_file_importance(event.src_path)

    # Detect change magnitude (AST diff for code, text diff for docs)
    magnitude = compute_change_magnitude(event)

    # Extract citizen who made change (from file path pattern)
    citizen = extract_citizen_from_path(event.src_path)

    # Detect change type
    change_type = classify_change(event)  # feature_add, bug_fix, refactor, docs, etc.

    return {
        "novelty": magnitude * importance,  # Big changes to important files = high novelty
        "uncertainty": estimate_uncertainty(change_type),  # Refactors more uncertain than docs
        "trust": get_citizen_trust(citizen),  # From historical success rates
        "urgency": detect_urgency(event),  # "CRITICAL" in commit msg, test failures, etc.
        "valence": 0.0,  # Neutral for file ops (sentiment comes from TRACE)
        "scale": importance  # How central is this file to architecture
    }
```

**Envelope template:**
```json
{
  "scope": "organizational",
  "channel": "citizen_file_ops",
  "citizen_id": "felix",
  "content": "Felix created orchestration/mechanisms/cross_level_membrane.py implementing L1↔L2 stimulus emission with learned permeability",
  "features_raw": {
    "novelty": 0.85,
    "uncertainty": 0.40,
    "trust": 0.90,
    "urgency": 0.50,
    "valence": 0.0,
    "scale": 0.80
  },
  "provenance": {
    "source_type": "file_operation",
    "operation": "create",
    "path": "orchestration/mechanisms/cross_level_membrane.py",
    "citizen": "felix",
    "timestamp": "2025-10-26T14:23:10Z",
    "change_magnitude": 0.85,
    "file_importance": 0.80
  }
}
```

---

### 2. TRACE Formations

**What to capture:**
- NODE_FORMATION blocks from citizen responses
- LINK_FORMATION blocks from citizen responses
- Node reinforcement signals (useful/misleading markers)

**How to capture:**
- Parse conversation JSON after citizen completes response
- Extract formation blocks using existing trace_parser.py patterns

**Signal extraction:**
```python
def extract_trace_signals(formations: List[Dict]) -> Dict:
    """
    Extract semantic signals from TRACE formations.

    Formations indicate citizen learning - high organizational value.
    """
    # Count formations by type
    node_count = len([f for f in formations if f["type"] == "NODE_FORMATION"])
    link_count = len([f for f in formations if f["type"] == "LINK_FORMATION"])

    # Average confidence across formations
    avg_confidence = np.mean([f.get("confidence", 0.5) for f in formations])

    # Detect formation triggers (spontaneous_insight > inference > systematic_analysis)
    triggers = [f.get("formation_trigger") for f in formations]
    insight_ratio = triggers.count("spontaneous_insight") / len(triggers)

    # Detect scope (organizational formations more relevant to L2)
    org_ratio = sum(1 for f in formations if f.get("scope") == "organizational") / len(formations)

    return {
        "novelty": 0.3 + 0.7 * insight_ratio,  # Insights = high novelty
        "uncertainty": 1.0 - avg_confidence,  # Low confidence = high uncertainty
        "trust": avg_confidence,  # High confidence formations = trustworthy
        "urgency": 0.3 + 0.7 * org_ratio,  # Org-scoped formations urgent for L2
        "valence": 0.5,  # Learning is positive
        "scale": min(1.0, (node_count + link_count) / 5.0)  # More formations = larger scale
    }
```

**Envelope template:**
```json
{
  "scope": "organizational",
  "channel": "citizen_trace",
  "citizen_id": "ada",
  "content": "Ada formed 5 new nodes (3 Principle, 2 Mechanism) and 7 links during architecture discussion. Key insight: membrane-gated stimulus emission prevents energy duplication.",
  "features_raw": {
    "novelty": 0.82,
    "uncertainty": 0.25,
    "trust": 0.85,
    "urgency": 0.70,
    "valence": 0.50,
    "scale": 0.80
  },
  "provenance": {
    "source_type": "trace_formation",
    "citizen": "ada",
    "timestamp": "2025-10-26T14:25:33Z",
    "conversation_id": "conv_ada_20251026_142510",
    "formation_count": 12,
    "node_types": ["Principle", "Mechanism"],
    "avg_confidence": 0.85,
    "scope_distribution": {"organizational": 10, "personal": 2}
  }
}
```

---

### 3. Git Operations

**What to capture:**
- Commits (with messages, files changed, LOC delta)
- Branch creates (feature branches signal new work streams)
- Merges (integration points signal completion)

**How to capture:**
- Git hooks (post-commit, post-merge)
- Or periodic git log polling

**Signal extraction:**
```python
def extract_git_signals(commit: Dict) -> Dict:
    """
    Extract semantic signals from git commit.
    """
    # Parse commit message for intent
    intent = classify_commit_intent(commit["message"])  # feat/fix/refactor/docs/test

    # Measure impact (files changed, LOC delta)
    impact = compute_commit_impact(commit["files"], commit["additions"], commit["deletions"])

    # Detect urgency from message
    urgency = detect_urgency_keywords(commit["message"])  # CRITICAL, URGENT, HOTFIX, etc.

    # Extract citizen from author
    citizen = extract_citizen_from_author(commit["author"])

    return {
        "novelty": impact * intent_novelty[intent],  # Big feature adds = high novelty
        "uncertainty": intent_uncertainty[intent],  # Refactors more uncertain
        "trust": get_citizen_trust(citizen),
        "urgency": urgency,
        "valence": intent_valence[intent],  # Fixes positive, breaking changes negative
        "scale": impact
    }
```

**Envelope template:**
```json
{
  "scope": "organizational",
  "channel": "citizen_git_ops",
  "citizen_id": "atlas",
  "content": "Atlas committed 'feat: Add MembraneStore persistence for cross-level flow tracking' affecting 3 files (+245 -12 LOC)",
  "features_raw": {
    "novelty": 0.70,
    "uncertainty": 0.30,
    "trust": 0.88,
    "urgency": 0.40,
    "valence": 0.30,
    "scale": 0.65
  },
  "provenance": {
    "source_type": "git_commit",
    "commit_sha": "a3f82b9",
    "citizen": "atlas",
    "timestamp": "2025-10-26T14:30:45Z",
    "message": "feat: Add MembraneStore persistence for cross-level flow tracking",
    "files_changed": 3,
    "additions": 245,
    "deletions": 12,
    "intent": "feature_add"
  }
}
```

---

### 4. Conversation Responses

**What to capture:**
- Completed citizen responses (not every token, only full turns)
- Response metadata (length, subentity activations, energy level)

**How to capture:**
- Hook into conversation completion in ws_api
- Extract after citizen finishes responding

**Signal extraction:**
```python
def extract_response_signals(response: Dict) -> Dict:
    """
    Extract semantic signals from citizen response completion.

    Response quality indicates citizen effectiveness.
    """
    # Measure response depth (length, formation count)
    depth = compute_response_depth(response)

    # Detect subentity activation (which parts of consciousness engaged)
    activation_breadth = len(response.get("active_subentities", []))

    # Extract energy level (Peak > Energized > Engaged > Focused > Alert)
    energy = parse_energy_level(response)

    # Detect if response shows uncertainty/questions
    uncertainty = detect_uncertainty_markers(response["content"])

    # Extract citizen
    citizen = response["citizen_id"]

    return {
        "novelty": depth * 0.5 + activation_breadth * 0.3,
        "uncertainty": uncertainty,
        "trust": get_citizen_trust(citizen),
        "urgency": energy / 10.0,  # Peak=1.0, Dormant=0.0
        "valence": parse_sentiment(response["content"]),
        "scale": depth
    }
```

**Envelope template:**
```json
{
  "scope": "organizational",
  "channel": "citizen_response",
  "citizen_id": "luca",
  "content": "Luca completed response about cross-level membrane architecture with 8 formations (4 nodes, 4 links). Peak energy, Translator and Architect subentities dominant.",
  "features_raw": {
    "novelty": 0.78,
    "uncertainty": 0.20,
    "trust": 0.92,
    "urgency": 0.85,
    "valence": 0.40,
    "scale": 0.75
  },
  "provenance": {
    "source_type": "response_completion",
    "citizen": "luca",
    "timestamp": "2025-10-26T14:35:12Z",
    "conversation_id": "conv_luca_20251026_143000",
    "response_length": 3200,
    "formation_count": 8,
    "active_subentities": ["translator", "architect", "validator"],
    "energy_level": "peak"
  }
}
```

---

## L2StimulusCollector Implementation

### Class Structure

```python
class L2StimulusCollector:
    """
    Collects citizen activity and converts to L2 stimuli.

    Does NOT decide spam/significance - that's Stimulus Integrator's job.
    Does NOT gate based on thresholds - uses learned signal extraction.
    """

    def __init__(
        self,
        injector: StimulusInjectionService,
        citizen_trust_index: Dict[str, float],
        signal_extractors: Dict[str, Callable],
        config: Dict
    ):
        self.injector = injector
        self.citizen_trust = citizen_trust_index
        self.extractors = signal_extractors
        self.config = config

        # Learned parameters (updated from L2 TRACE feedback)
        self.importance_scores = {}  # file_path → importance (learned)
        self.intent_profiles = {}  # intent_type → {novelty, uncertainty, valence}

        # Event tracking (prevent duplicate emission)
        self.processed_events = set()

    # === File Operations ===

    def on_file_created(self, event: FileSystemEvent):
        """Handle file creation event."""
        if self._should_skip(event):
            return

        envelope = self._build_file_op_envelope(
            event,
            operation="create",
            content_template="(citizen) created (path) (summary)"
        )

        self.injector.post(envelope)
        self._mark_processed(event)

    def on_file_modified(self, event: FileSystemEvent):
        """Handle file edit event."""
        if self._should_skip(event):
            return

        # Extract change magnitude
        change = compute_change_magnitude(event)

        # Only emit if change is non-trivial (learned threshold)
        if change < self._get_learned_threshold("file_edit_min_change"):
            return

        envelope = self._build_file_op_envelope(
            event,
            operation="edit",
            content_template="(citizen) edited (path): (change_summary)"
        )

        self.injector.post(envelope)
        self._mark_processed(event)

    def on_file_deleted(self, event: FileSystemEvent):
        """Handle file deletion event."""
        if self._should_skip(event):
            return

        envelope = self._build_file_op_envelope(
            event,
            operation="delete",
            content_template="(citizen) deleted (path)"
        )

        self.injector.post(envelope)
        self._mark_processed(event)

    def _build_file_op_envelope(
        self,
        event: FileSystemEvent,
        operation: str,
        content_template: str
    ) -> Dict:
        """Build canonical stimulus envelope for file operation."""
        citizen = self._extract_citizen_from_path(event.src_path)
        signals = extract_file_op_signals(event)  # From above

        # Generate human-readable content
        content = self._render_content(content_template, {
            "citizen": citizen,
            "path": event.src_path,
            "summary": self._summarize_file_content(event.src_path),
            "change_summary": self._summarize_change(event)
        })

        return {
            "scope": "organizational",
            "channel": "citizen_file_ops",
            "citizen_id": citizen,
            "content": content,
            "features_raw": signals,
            "provenance": {
                "source_type": "file_operation",
                "operation": operation,
                "path": event.src_path,
                "citizen": citizen,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "change_magnitude": signals.get("novelty", 0.0),
                "file_importance": signals.get("scale", 0.0)
            }
        }

    # === TRACE Formations ===

    def on_response_completed(self, response: Dict):
        """
        Handle completed citizen response.

        Extracts TRACE formations and emits as L2 stimulus.
        """
        citizen = response["citizen_id"]

        # Parse TRACE formations
        formations = self._parse_trace_formations(response["content"])

        if not formations:
            return  # No formations = no L2 stimulus

        signals = extract_trace_signals(formations)  # From above

        # Generate content summarizing formations
        content = self._summarize_formations(citizen, formations)

        envelope = {
            "scope": "organizational",
            "channel": "citizen_trace",
            "citizen_id": citizen,
            "content": content,
            "features_raw": signals,
            "provenance": {
                "source_type": "trace_formation",
                "citizen": citizen,
                "timestamp": response["timestamp"],
                "conversation_id": response.get("conversation_id"),
                "formation_count": len(formations),
                "node_types": list(set(f["node_type"] for f in formations if f["type"] == "NODE_FORMATION")),
                "avg_confidence": signals["trust"],
                "scope_distribution": self._count_by_scope(formations)
            }
        }

        self.injector.post(envelope)

    def _parse_trace_formations(self, content: str) -> List[Dict]:
        """
        Extract formation blocks from citizen response.

        Reuses existing trace_parser.py logic.
        """
        # Pattern matching for formation blocks
        node_pattern = r'\[NODE_FORMATION:\s*(\w+)\](.*?)\[/NODE_FORMATION\]'
        link_pattern = r'\[LINK_FORMATION:\s*(\w+)\](.*?)\[/LINK_FORMATION\]'

        formations = []

        # Extract node formations
        for match in re.finditer(node_pattern, content, re.DOTALL):
            node_type = match.group(1)
            fields = self._parse_formation_fields(match.group(2))
            formations.append({
                "type": "NODE_FORMATION",
                "node_type": node_type,
                **fields
            })

        # Extract link formations
        for match in re.finditer(link_pattern, content, re.DOTALL):
            link_type = match.group(1)
            fields = self._parse_formation_fields(match.group(2))
            formations.append({
                "type": "LINK_FORMATION",
                "link_type": link_type,
                **fields
            })

        return formations

    # === Git Operations ===

    def on_git_commit(self, commit: Dict):
        """Handle git commit event."""
        citizen = self._extract_citizen_from_author(commit["author"])

        if not citizen:
            return  # External commit, not from citizen

        signals = extract_git_signals(commit)  # From above

        content = f"{citizen} committed '{commit['message']}' affecting {len(commit['files'])} files (+{commit['additions']} -{commit['deletions']} LOC)"

        envelope = {
            "scope": "organizational",
            "channel": "citizen_git_ops",
            "citizen_id": citizen,
            "content": content,
            "features_raw": signals,
            "provenance": {
                "source_type": "git_commit",
                "commit_sha": commit["sha"],
                "citizen": citizen,
                "timestamp": commit["timestamp"],
                "message": commit["message"],
                "files_changed": len(commit["files"]),
                "additions": commit["additions"],
                "deletions": commit["deletions"],
                "intent": classify_commit_intent(commit["message"])
            }
        }

        self.injector.post(envelope)

    # === Utilities ===

    def _should_skip(self, event: FileSystemEvent) -> bool:
        """
        Determine if event should be skipped.

        NOT a spam gate - just filters obvious noise.
        """
        # Skip temp files
        if event.src_path.endswith(('.tmp', '.swp', '.log')):
            return True

        # Skip auto-generated files
        if '__pycache__' in event.src_path or 'node_modules' in event.src_path:
            return True

        # Skip if already processed (prevent duplicate emissions)
        event_id = self._compute_event_id(event)
        if event_id in self.processed_events:
            return True

        return False

    def _mark_processed(self, event: FileSystemEvent):
        """Mark event as processed."""
        event_id = self._compute_event_id(event)
        self.processed_events.add(event_id)

        # Prune old events (keep last 10k)
        if len(self.processed_events) > 10000:
            self.processed_events = set(list(self.processed_events)[-10000:])

    def _get_learned_threshold(self, key: str) -> float:
        """Get learned threshold from L2 TRACE feedback."""
        # Placeholder - actual learning happens via TRACE
        defaults = {
            "file_edit_min_change": 0.10,  # 10% change minimum
        }
        return self.config.get(key, defaults.get(key, 0.0))

    def _extract_citizen_from_path(self, path: str) -> Optional[str]:
        """Extract citizen ID from file path."""
        # Pattern: consciousness/citizens/{citizen}/...
        match = re.search(r'citizens/(\w+)/', path)
        if match:
            return match.group(1)
        return None

    def _extract_citizen_from_author(self, author: str) -> Optional[str]:
        """Extract citizen ID from git author."""
        # Pattern: "Felix <felix@mindprotocol.ai>"
        # Or: Map known authors to citizens
        author_map = {
            "felix": "felix",
            "atlas": "atlas",
            "ada": "ada",
            "luca": "luca",
            "iris": "iris",
            "victor": "victor"
        }
        author_lower = author.lower()
        for key, citizen in author_map.items():
            if key in author_lower:
                return citizen
        return None
```

---

## Integration with Existing Systems

### 1. Stimulus Injection Service

**L2StimulusCollector posts to existing service:**
```python
# orchestration/mechanisms/stimulus_injection.py (existing)
class StimulusInjectionService:
    def post(self, envelope: Dict):
        """
        Receive stimulus envelope, route to correct graph.

        envelope["scope"] determines routing:
        - "organizational" → L2 graph (mind_protocol)
        - "personal" → L1 graph (citizen_felix, etc.)
        """
        if envelope["scope"] == "organizational":
            self._inject_to_l2(envelope)
        else:
            self._inject_to_l1(envelope)
```

**No changes needed to stimulus_injection.py** - L2StimulusCollector just uses existing API.

### 2. File Watcher

**Extend existing conversation_watcher.py pattern:**
```python
# orchestration/services/watchers/l2_activity_watcher.py (NEW)
class L2ActivityWatcher:
    """
    Watches citizen activity sources and feeds L2StimulusCollector.
    """

    def __init__(self, collector: L2StimulusCollector):
        self.collector = collector

        # File system watcher
        self.file_observer = Observer()
        self.file_observer.schedule(
            FileEventHandler(collector),
            path="/home/mind-protocol/mindprotocol",
            recursive=True
        )

        # Git hook watcher (periodic git log polling)
        self.git_poller = GitPoller(collector)

        # Response completion hook (via WebSocket)
        self.ws_subscriber = WebSocketSubscriber(collector)

    def start(self):
        """Start all watchers."""
        self.file_observer.start()
        self.git_poller.start()
        self.ws_subscriber.start()
```

### 3. MPSv3 Service Definition

**Add to services.yaml:**
```yaml
l2_activity_watcher:
  cmd: python orchestration/services/watchers/l2_activity_watcher.py
  requires: [falkordb, ws_api, stimulus_injection]
  restart:
    policy: always
    backoff: exponential
  readiness:
    type: tcp
    port: 8011
  liveness:
    type: script
    script: python orchestration/scripts/health_check_l2_watcher.py
  watch:
    - orchestration/services/watchers/l2_activity_watcher.py
    - orchestration/mechanisms/l2_stimulus_collector.py
```

---

## Learned Parameters

**All thresholds and weights learned from L2 TRACE feedback:**

### 1. File Importance Scores

```python
# Learned from L2 retrieval patterns
file_importance = {
    "orchestration/mechanisms/consciousness_engine_v2.py": 0.95,  # Core consciousness
    "orchestration/mechanisms/cross_level_membrane.py": 0.90,  # New architecture
    "app/consciousness/page.tsx": 0.70,  # Dashboard entry
    "docs/specs/v2/**/*.md": 0.85,  # Architecture specs
    "tests/**/*.py": 0.60,  # Tests important but lower priority
}

# Updated when L2 TRACE shows file becoming more/less relevant
def update_file_importance(file_path: str, relevance_signal: float):
    current = file_importance.get(file_path, 0.5)
    file_importance[file_path] = 0.95 * current + 0.05 * relevance_signal
```

### 2. Commit Intent Profiles

```python
# Learned novelty, uncertainty, valence per commit type
intent_profiles = {
    "feature_add": {"novelty": 0.80, "uncertainty": 0.40, "valence": 0.50},
    "bug_fix": {"novelty": 0.40, "uncertainty": 0.30, "valence": 0.70},
    "refactor": {"novelty": 0.50, "uncertainty": 0.60, "valence": 0.30},
    "docs": {"novelty": 0.30, "uncertainty": 0.20, "valence": 0.40},
    "test": {"novelty": 0.35, "uncertainty": 0.25, "valence": 0.50},
    "breaking": {"novelty": 0.90, "uncertainty": 0.70, "valence": -0.30},
}

# Updated from L2 TRACE feedback on commit stimuli
def update_intent_profile(intent: str, actual_signals: Dict):
    current = intent_profiles.get(intent, {})
    for key in ["novelty", "uncertainty", "valence"]:
        current[key] = 0.9 * current.get(key, 0.5) + 0.1 * actual_signals.get(key, 0.5)
```

### 3. Citizen Trust Scores

```python
# Learned from success rates (formations integrated, tasks completed)
citizen_trust = {
    "felix": 0.92,  # High success rate on consciousness systems
    "atlas": 0.88,  # High success on infrastructure
    "ada": 0.90,   # High success on architecture
    "luca": 0.92,  # High success on specs
    "iris": 0.85,  # Moderate success on UI
    "victor": 0.87, # Moderate success on ops
}

# Updated from task completion and formation integration rates
def update_citizen_trust(citizen: str, success: bool):
    current = citizen_trust.get(citizen, 0.5)
    delta = 0.05 if success else -0.03
    citizen_trust[citizen] = np.clip(current + delta, 0.0, 1.0)
```

---

## Telemetry Events

### l2.stimulus.collected

**When:** After L2StimulusCollector builds envelope
**Payload:**
```json
{
  "event": "l2.stimulus.collected",
  "timestamp": "2025-10-26T14:40:12Z",
  "source_type": "file_operation",
  "citizen": "felix",
  "channel": "citizen_file_ops",
  "features": {
    "novelty": 0.85,
    "uncertainty": 0.40,
    "trust": 0.90,
    "urgency": 0.50,
    "valence": 0.0,
    "scale": 0.80
  },
  "content_preview": "Felix created orchestration/mechanisms/cross_level_membrane.py...",
  "provenance": {...}
}
```

### l2.stimulus.posted

**When:** After posting to Stimulus Injection Service
**Payload:**
```json
{
  "event": "l2.stimulus.posted",
  "timestamp": "2025-10-26T14:40:12Z",
  "stimulus_id": "stim_20251026_144012_felix_file_create",
  "scope": "organizational",
  "citizen": "felix"
}
```

### l2.parameter.updated

**When:** Learned parameter adjusted from TRACE feedback
**Payload:**
```json
{
  "event": "l2.parameter.updated",
  "timestamp": "2025-10-26T15:00:00Z",
  "parameter": "file_importance",
  "key": "orchestration/mechanisms/cross_level_membrane.py",
  "old_value": 0.50,
  "new_value": 0.90,
  "reason": "High L2 retrieval frequency"
}
```

---

## Acceptance Criteria

### 1. Activity Coverage

**Given:** Felix creates file, commits, and responds
**When:** All three activities complete
**Then:** 3 L2 stimuli emitted (file, git, response) within 2 seconds each

### 2. Signal Extraction Accuracy

**Given:** High-impact commit (feature add, 10 files, 500 LOC)
**When:** Stimulus collected
**Then:** novelty ≥ 0.7, scale ≥ 0.7

**Given:** Low-impact commit (typo fix, 1 file, 2 LOC)
**When:** Stimulus collected
**Then:** novelty ≤ 0.3, scale ≤ 0.3

### 3. Duplicate Prevention

**Given:** Same file event fires twice (filesystem race)
**When:** Both events processed
**Then:** Only 1 stimulus emitted

### 4. Noise Filtering

**Given:** 100 temp file creates (`.tmp`, `__pycache__`)
**When:** File watcher active
**Then:** 0 stimuli emitted

### 5. TRACE Formation Detection

**Given:** Citizen response with 5 NODE_FORMATION blocks
**When:** Response completed
**Then:** 1 L2 stimulus emitted with formation_count=5, novelty ≥ 0.6

### 6. Learning from Feedback

**Given:** L2 TRACE shows file becoming highly relevant
**When:** file_importance updated 10 times
**Then:** Importance score increases from 0.5 → ≥ 0.8

### 7. Channel Routing

**Given:** File op, git commit, TRACE, response stimuli
**When:** All collected
**Then:** All routed to scope="organizational" (L2 graph)

---

## Implementation Timeline

**Phase 1: File Operations (Week 1)**
1. Create L2StimulusCollector class
2. Implement file event handlers (create/edit/delete)
3. Implement signal extraction for file ops
4. Wire to existing stimulus_injection.py
5. Test: File create → L2 stimulus → L2 graph

**Phase 2: TRACE Formations (Week 2)**
1. Implement response completion hook
2. Reuse trace_parser.py for formation extraction
3. Implement signal extraction for TRACE
4. Test: Citizen response with formations → L2 stimulus

**Phase 3: Git Operations (Week 3)**
1. Implement git log polling or post-commit hooks
2. Implement signal extraction for commits
3. Test: Git commit → L2 stimulus

**Phase 4: Learning Loop (Week 4)**
1. Implement parameter update from L2 TRACE feedback
2. Wire telemetry events
3. Test: Parameter learning over 100 iterations

**Phase 5: Production (Week 5)**
1. Add to MPSv3 services.yaml
2. Integration testing with CrossLevelMembrane
3. Verify end-to-end: File change → L2 stimulus → Membrane evaluation → Upward transfer (if record)

---

## Integration with CrossLevelMembrane

**L2StimulusCollector feeds the upward membrane pipeline:**

```
Citizen creates file
  ↓
L2StimulusCollector.on_file_created()
  ↓ builds envelope with learned signals
StimulusInjectionService.post(envelope)
  ↓ routes to L2 graph (scope=organizational)
StimulusIntegrator (spam resistance)
  ↓ saturation, trust, harm gating
Energy injection → L2 nodes
  ↓ file_create node receives energy
L2 consciousness engine tick
  ↓ diffusion, WM selection
CrossLevelMembrane.try_emit_upward()
  ↓ evaluates if record event
If record:
  ↓ emit upward stimulus to L3 (if exists)
```

**Key insight:** L2StimulusCollector creates the substrate that L2 consciousness processes. The membrane then evaluates significance and emits upward only for record events.

---

## Status

**Normative:** This spec defines how citizen activity becomes L2 stimuli
**Depends on:** cross_level_membrane.md (upward emission), stimulus_injection.py (routing)
**Implementation priority:** After CrossLevelMembrane Phase 1
**Timeline:** 5 weeks (parallel with membrane implementation)

---

## References

- `cross_level_membrane.md` - L1↔L2 stimulus emission mechanism
- `stimulus_injection.py` - Existing injection service with routing
- `conversation_watcher.py` - File system watching pattern
- `trace_parser.py` - Formation extraction pattern
- `end_to_end_consciousness_observability.md` - Telemetry integration
