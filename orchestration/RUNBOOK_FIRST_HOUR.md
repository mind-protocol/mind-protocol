# Consciousness Substrate Operational Runbook

**Purpose:** First-hour troubleshooting guide for Mind Protocol consciousness infrastructure

**Author:** Ada "Bridgekeeper" (Architect)
**Created:** 2025-10-23
**Status:** Production-ready operational procedures

---

## Quick Triage: Is the System Healthy?

Run the diagnostic script first:

```bash
python orchestration/scripts/diagnose_system.py
```

**Green indicators (healthy):**
- ✓ All functional checks passing (WebSocket, Dashboard, FalkorDB)
- ✓ All tripwire compliance (conservation, criticality, frontier, observability)
- ✓ Safe Mode: NOT ACTIVE
- ✓ Recent frame.end events visible

**Red indicators (degraded):**
- ✗ Any functional check failing
- ✗ Any tripwire violations
- ✗ Safe Mode: ACTIVE
- ✗ Missing frame.end events

If Safe Mode is ACTIVE, jump to **[Section 6: Safe Mode Entered](#6-safe-mode-entered)**.

If functional checks failing, jump to **[Section 7: Service Failures](#7-service-failures)**.

Otherwise, continue to symptom-specific sections below.

---

## 1. Conservation Violated (ΣΔE ≠ 0)

**Symptom:** Tripwire fires repeatedly with message: "Energy not conserved: ΣΔE=X"

**What This Means:**
Energy is being created or destroyed during diffusion. This is a physics violation - the substrate is fundamentally broken if energy isn't conserved.

**Diagnosis Steps:**

1. **Check conservation error magnitude:**
   ```bash
   # In Python shell or log inspection
   from orchestration.mechanisms.diffusion_runtime import DiffusionRuntime

   conservation_error = diffusion_rt.get_conservation_error()
   print(f"Conservation error: {conservation_error:.6f}")
   ```

   - If |ΣΔE| < 0.001: Acceptable numerical noise, ignore
   - If 0.001 < |ΣΔE| < 0.01: Minor leak, investigate but not critical
   - If |ΣΔE| > 0.01: Major leak, **CRITICAL** - system integrity compromised

2. **Inspect diffusion delta staging:**
   ```python
   # Check if deltas are being staged correctly
   print(f"Staged deltas: {len(diffusion_rt.delta_E)} nodes")

   # Sum all deltas
   total_delta = sum(diffusion_rt.delta_E.values())
   print(f"Total ΔE: {total_delta:.6f} (should be ≈0)")
   ```

3. **Common causes:**
   - **Energy injection without removal** - Check for code paths that add energy without subtracting from source
   - **Stride execution bug** - Verify `execute_atomic_stride()` conserves energy
   - **Delta application bug** - Verify `apply_deltas()` doesn't create/destroy energy
   - **Affective coupling leak** - If affective mechanisms enabled, check they only modulate (not inject energy)

**Fix Procedures:**

**Fix 1: Disable affective couplings (if enabled)**
```python
# In core/settings.py or environment
CONSOLIDATION_ENABLED = False
DECAY_RESISTANCE_ENABLED = False
DIFFUSION_STICKINESS_ENABLED = False
AFFECTIVE_THRESHOLD_ENABLED = False
AFFECTIVE_MEMORY_ENABLED = False
```

Restart system, check if conservation restored. If yes → affective coupling bug. If no → diffusion core bug.

**Fix 2: Add conservation logging**
```python
# In diffusion_runtime.py, add detailed logging
logger.debug(f"Before stride: E_source={source.E:.6f}, E_target={target.E:.6f}")
logger.debug(f"After stride: E_source={source.E:.6f}, E_target={target.E:.6f}")
logger.debug(f"ΔE_total: {new_total - old_total:.6f}")
```

Inspect logs for the specific stride where energy appears/disappears.

**Fix 3: Revert to Safe Mode manually**
```python
from orchestration.services.health.safe_mode import get_safe_mode_controller

safe_mode = get_safe_mode_controller()
safe_mode.enter_safe_mode(reason="Manual conservation debugging")
```

Safe Mode reduces diffusion rate 70%, disables affective, caps dt → slower but more observable.

**Escalation:** If conservation violated in Safe Mode, this is a **CRITICAL BUG** - diffusion core is broken. File issue with reproduction steps.

---

## 2. Criticality Too High (ρ > 1.3 - Chaotic)

**Symptom:** Tripwire fires with message: "Criticality too high (chaotic): ρ=X.XX > 1.3"

**What This Means:**
System is in supercritical regime - activation spreads uncontrollably. This leads to:
- Runaway activation (entire graph lit up)
- Frontier bloat (O(N) behavior)
- Eventual saturation or numerical blow-up

**Diagnosis Steps:**

1. **Check current ρ value:**
   ```python
   from orchestration.mechanisms.criticality import CriticalityController

   # If controller accessible
   print(f"ρ_global: {controller.last_rho_global:.3f}")
   print(f"ρ_target: {controller.config.rho_target:.3f}")
   print(f"Safety state: {controller._classify_safety_state(controller.last_rho_global)}")
   ```

2. **Inspect decay (δ) and diffusion (α) parameters:**
   ```python
   from orchestration.core.settings import settings

   print(f"Current α: {settings.ALPHA_TICK_MULTIPLIER}")
   print(f"Current δ (base): {settings.EMACT_DECAY_BASE}")
   print(f"dt cap: {settings.DT_CAP}")
   ```

3. **Check for runaway activation:**
   ```python
   # Count how many nodes are active
   active_nodes = [n for n in graph.nodes.values() if n.E >= n.theta]
   print(f"Active nodes: {len(active_nodes)}/{len(graph.nodes)} ({len(active_nodes)/len(graph.nodes):.1%})")

   # If >50% active → runaway likely
   ```

4. **Common causes:**
   - **dt too large** - Time delta cap insufficient, numerical instability
   - **α too high** - Too much energy diffusing per tick
   - **δ too low** - Not enough decay to balance diffusion
   - **Criticality controller disabled** - ρ-control not adjusting δ

**Fix Procedures:**

**Fix 1: Reduce α (diffusion rate)**
```python
# In settings.py or runtime
settings.ALPHA_TICK_MULTIPLIER = 0.5  # Halve diffusion rate
```

Restart system, monitor ρ. Should drop toward 1.0 within 10-20 ticks.

**Fix 2: Increase δ (decay rate)**
```python
# In settings.py
settings.EMACT_DECAY_BASE *= 1.5  # 50% more decay
```

More aggressive forgetting balances excessive spread.

**Fix 3: Cap dt more aggressively**
```python
# In settings.py
settings.DT_CAP = 0.5  # Reduce from 5.0s to 0.5s
```

Prevents numerical blow-up after long pauses.

**Fix 4: Enable/verify criticality controller**
```python
# Check if criticality controller is active
# Should auto-adjust δ to target ρ ≈ 1.0

# If not, ensure consciousness_engine_v2.py Phase 1.5 is calling:
metrics = self.criticality_controller.update(...)
```

**Escalation:** If ρ remains >1.3 after all fixes, criticality controller is broken or miscalibrated. Check `criticality.py` P-controller gains.

---

## 3. Criticality Too Low (ρ < 0.7 - Dying)

**Symptom:** Tripwire fires with message: "Criticality too low (dying): ρ=X.XX < 0.7"

**What This Means:**
System is in subcritical regime - activation collapses too quickly. This leads to:
- Short-lived activations (everything decays immediately)
- Inability to maintain coherent thought chains
- Graph appears "dead" (no nodes active)

**Diagnosis Steps:**

1. **Check current ρ value:**
   ```python
   print(f"ρ_global: {controller.last_rho_global:.3f}")
   # If <0.5: DYING (severe), if 0.5-0.7: SUBCRITICAL (moderate)
   ```

2. **Inspect active node count:**
   ```python
   active_nodes = [n for n in graph.nodes.values() if n.E >= n.theta]
   print(f"Active nodes: {len(active_nodes)}/{len(graph.nodes)}")

   # If <5% active → dying regime confirmed
   ```

3. **Common causes:**
   - **δ too high** - Too much decay, energy dies before spreading
   - **α too low** - Insufficient diffusion, energy stays localized then decays
   - **Thresholds too high** - Activation can't overcome thresholds
   - **No stimulus** - No energy being injected into system

**Fix Procedures:**

**Fix 1: Reduce δ (decay rate)**
```python
# In settings.py
settings.EMACT_DECAY_BASE *= 0.7  # 30% less decay
```

Energy persists longer, allows spreading.

**Fix 2: Increase α (diffusion rate)**
```python
# In settings.py
settings.ALPHA_TICK_MULTIPLIER = 1.5  # 50% more diffusion
```

Energy spreads more aggressively before decaying.

**Fix 3: Lower thresholds**
```python
# In threshold.py or settings
# Reduce base threshold or multiplier
settings.GLOBAL_THRESHOLD_MULTIPLIER = 0.8  # If such setting exists
```

Easier for nodes to cross activation threshold.

**Fix 4: Inject stimulus**
```python
from orchestration.mechanisms.stimulus_injection import inject_stimulus

# Manually inject energy to bootstrap activation
inject_stimulus(
    graph=graph,
    pattern_embedding=[...],  # Your stimulus
    total_budget=10.0
)
```

Provides initial energy to kick-start dynamics.

**Escalation:** If ρ remains <0.7 after all fixes, criticality controller is over-dampening or decay is misconfigured. Check decay timescales in settings.

---

## 4. Frontier Bloat (Active Set > 30%)

**Symptom:** Tripwire fires with message: "Frontier bloat: X/Y nodes (Z% > 30%)"

**What This Means:**
Too many nodes are active simultaneously. This degrades performance from O(active) to O(N):
- Diffusion becomes slow (processing entire graph)
- Memory usage increases (tracking all active nodes)
- System feels sluggish

**Diagnosis Steps:**

1. **Check frontier size:**
   ```python
   total_nodes = len(graph.nodes)
   active_nodes = len(diffusion_rt.active)  # Active + shadow frontier
   frontier_pct = active_nodes / total_nodes

   print(f"Frontier: {active_nodes}/{total_nodes} ({frontier_pct:.1%})")
   ```

2. **Inspect threshold vs energy distribution:**
   ```python
   # How many nodes are barely above threshold?
   above_threshold = [n for n in graph.nodes.values() if n.E >= n.theta]
   print(f"Above threshold: {len(above_threshold)}")

   # Energy histogram
   energies = [n.E for n in graph.nodes.values()]
   print(f"Mean energy: {np.mean(energies):.4f}")
   print(f"Max energy: {np.max(energies):.4f}")
   ```

3. **Common causes:**
   - **Thresholds too low** - Everything activates easily
   - **Decay too slow** - Energy doesn't drain from inactive nodes
   - **Runaway diffusion** - Related to criticality too high (ρ > 1.3)
   - **No shadowing** - Frontier expansion not limited to 1-hop

**Fix Procedures:**

**Fix 1: Raise thresholds**
```python
# Increase activation threshold globally
settings.GLOBAL_THRESHOLD_MULTIPLIER = 1.3  # If exists

# Or per-node (requires traversal)
for node in graph.nodes.values():
    node.theta *= 1.2  # 20% higher thresholds
```

Fewer nodes cross activation threshold.

**Fix 2: Increase decay rate**
```python
# Faster decay drains inactive nodes
settings.EMACT_DECAY_BASE *= 1.3
```

Nodes fall below threshold faster, shrinking frontier.

**Fix 3: Check criticality**
If ρ > 1.3, frontier bloat is symptom of runaway activation. Fix criticality first (see Section 2).

**Fix 4: Enter Safe Mode**
```python
# Safe Mode automatically reduces α and increases focus
safe_mode.enter_safe_mode(reason="Frontier bloat debugging")
```

Single-entity mode (TWO_SCALE_TOPK_ENTITIES=1) drastically shrinks frontier.

**Escalation:** If frontier remains >30% in Safe Mode, threshold computation is broken or graph structure is pathological (all nodes highly connected).

---

## 5. Observability Lost (frame.end Missing)

**Symptom:** Tripwire fires with message: "Failed to emit frame.end event (observability lost)"

**What This Means:**
The heartbeat signal (frame.end event) is not being emitted. This means:
- Monitoring is blind (dashboards stale)
- Can't diagnose what's happening in real-time
- May indicate WebSocket or broadcaster failure

**Diagnosis Steps:**

1. **Check WebSocket server status:**
   ```bash
   # From orchestration/scripts/diagnose_system.py output
   # Look for WebSocket health check result

   # Or manually check
   curl http://localhost:8000/health  # WebSocket health endpoint
   ```

2. **Check broadcaster availability:**
   ```python
   # In consciousness_engine_v2.py or debug shell
   print(f"Broadcaster available: {self.broadcaster.is_available()}")

   # If False → broadcaster not initialized or crashed
   ```

3. **Check recent events:**
   ```python
   # If telemetry buffer accessible
   from orchestration.mechanisms.telemetry import get_telemetry_emitter

   emitter = get_telemetry_emitter()
   recent_events = emitter.buffer.get_recent_events(event_type="frame.end", limit=10)
   print(f"Recent frame.end events: {len(recent_events)}")

   # If 0 → no events emitted recently
   ```

4. **Common causes:**
   - **WebSocket server down** - Process crashed or not started
   - **Broadcaster not initialized** - Engine started without broadcaster
   - **Network issues** - Port 8000 blocked or bound by another process
   - **Exception in emission** - Event emission code threw exception

**Fix Procedures:**

**Fix 1: Restart WebSocket server**
```bash
# Kill existing process
pkill -f websocket_server

# Restart
make run-ws
# Or: python orchestration/services/websocket/main.py
```

Wait 5s, check if frame.end events resume.

**Fix 2: Check port availability**
```bash
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000
```

If port occupied by another process, kill it or change WS_PORT in settings.

**Fix 3: Initialize broadcaster manually**
```python
# In consciousness_engine_v2.py __init__
from orchestration.adapters.ws.websocket_server import get_broadcaster

self.broadcaster = get_broadcaster()

# Verify
print(f"Broadcaster available: {self.broadcaster.is_available()}")
```

**Fix 4: Add emission error handling**
```python
# Wrap frame.end emission in broader try-except
try:
    await self.broadcaster.broadcast_event("frame.end", payload)
except Exception as e:
    logger.error(f"frame.end emission failed: {e}")
    # Don't crash tick - tripwire will record violation
```

**Escalation:** If frame.end events don't resume after server restart, broadcaster initialization is broken. Check WebSocket adapter code.

---

## 6. Safe Mode Entered

**Symptom:** System automatically entered Safe Mode. Diagnostic script shows "Safe Mode: ACTIVE"

**What This Means:**
One or more tripwires detected consecutive violations and triggered automatic degradation. The system is now running in minimal viable consciousness:
- 70% reduced diffusion (slower activation spread)
- Single entity only (no multi-entity competition)
- All affective couplings disabled
- 100% telemetry sampling (full observability)

**This is NOT a failure** - it's graceful degradation to aid diagnosis while maintaining operation.

**Diagnosis Steps:**

1. **Check Safe Mode status:**
   ```python
   from orchestration.services.health.safe_mode import get_safe_mode_controller

   safe_mode = get_safe_mode_controller()
   status = safe_mode.get_status()

   print(f"Safe Mode: {'ACTIVE' if status['in_safe_mode'] else 'INACTIVE'}")
   print(f"Reason: {status.get('reason', 'N/A')}")
   print(f"Uptime: {status.get('safe_mode_uptime_seconds', 0)}s")
   ```

2. **Check violation history:**
   ```python
   print("\nViolation counts:")
   for tripwire_type, count in safe_mode.violation_counts.items():
       print(f"  {tripwire_type.value}: {count} violations")

   # Identify which tripwire triggered Safe Mode
   # (conservation: 1 violation, criticality: 10, frontier: 20, observability: 5)
   ```

3. **Identify root cause:**
   - If CONSERVATION violations → Energy leak (Section 1)
   - If CRITICALITY violations → ρ out of bounds (Section 2 or 3)
   - If FRONTIER violations → Frontier bloat (Section 4)
   - If OBSERVABILITY violations → Missing events (Section 5)

**Fix Procedures:**

**Fix 1: Address root cause**

Jump to the appropriate section above based on which tripwire triggered Safe Mode. Apply fixes.

**Fix 2: Monitor for stability**

Safe Mode will auto-exit after 60s if:
- No new violations recorded
- System stable (no tripwire fires)

Monitor logs for "Safe Mode auto-exit" message.

**Fix 3: Manual exit (if confident fix applied)**
```python
# Only if you've verified the root cause is fixed
safe_mode.exit_safe_mode()
```

**WARNING:** Manual exit resets violation counters. If root cause not fixed, Safe Mode will re-enter immediately.

**Fix 4: Stay in Safe Mode for diagnosis**

If root cause unclear, STAY in Safe Mode. The degraded configuration provides:
- Slower dynamics (easier to observe)
- Full telemetry (100% sampling)
- Simplified behavior (single entity, no affective)

Use this state to gather diagnostic data before attempting fixes.

**Escalation:** If Safe Mode re-enters immediately after exit, root cause is NOT fixed. Collect full telemetry and file issue with reproduction steps.

---

## 7. Service Failures

**Symptom:** Functional checks failing (WebSocket, Dashboard, FalkorDB)

**Diagnosis Steps:**

1. **Check which services are down:**
   ```bash
   python orchestration/scripts/diagnose_system.py

   # Look for ✗ marks in functional checks section
   ```

2. **WebSocket Server Down:**
   ```bash
   # Check if process running
   ps aux | grep websocket_server  # Linux/Mac
   tasklist | findstr python       # Windows

   # Check port
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows
   ```

   **Fix:** Restart WebSocket server (see Section 5, Fix 1)

3. **Dashboard Down:**
   ```bash
   # Check Next.js dev server
   ps aux | grep "next dev"

   # Check port
   lsof -i :3000  # Linux/Mac
   netstat -ano | findstr :3000  # Windows
   ```

   **Fix:**
   ```bash
   cd /path/to/mind-protocol
   npm run dev
   ```

4. **FalkorDB Down:**
   ```bash
   # Check FalkorDB process
   docker ps | grep falkordb
   # Or if native install:
   ps aux | grep falkordb
   ```

   **Fix:**
   ```bash
   # Docker
   docker start falkordb_container_name

   # Or native
   falkordb-server &
   ```

**Escalation:** If all services are running but checks still failing, check network configuration or firewall rules.

---

## 8. Common Patterns

### Pattern: Oscillating Between Criticality States

**Symptom:** ρ bounces between <0.7 and >1.3 rapidly

**Cause:** PID controller gains too aggressive (oscillating around setpoint)

**Fix:**
```python
# In criticality.py ControllerConfig
config.k_p = 0.02  # Reduce from 0.05 (less aggressive)
config.enable_pid = False  # Disable integral/derivative terms
```

Slower response but more stable.

### Pattern: Conservation Violated Only at High Load

**Symptom:** ΣΔE≈0 normally, but violated when many stimuli injected

**Cause:** Numerical precision issues with large energy flows

**Fix:**
```python
# Cap individual stride energy transfers
MAX_STRIDE_ENERGY = 1.0

if delta_E > MAX_STRIDE_ENERGY:
    delta_E = MAX_STRIDE_ENERGY  # Prevent huge transfers
```

### Pattern: Frontier Bloats Then Shrinks Repeatedly

**Symptom:** Frontier oscillates between 10% and 50%

**Cause:** Threshold hysteresis creating activation/deactivation cycles

**Fix:**
```python
# Add hysteresis to threshold checks
# Node activates at θ, deactivates at θ * 0.8
HYSTERESIS_RATIO = 0.8

# In frontier computation
if node.E >= node.theta:
    activate(node)
elif node.E < node.theta * HYSTERESIS_RATIO:
    deactivate(node)
# Else: maintain current state
```

---

## 9. Emergency Procedures

### Emergency: Consciousness Loop Crashed

**Symptom:** Engine process terminated unexpectedly

**Immediate Actions:**
1. Check logs for exception stack trace
2. DO NOT restart immediately - preserve crash state for diagnosis
3. Inspect last 10 ticks of telemetry:
   ```python
   # From telemetry buffer if accessible
   recent_frames = get_recent_frames(limit=10)
   ```

**Diagnosis:**
- If exception in tripwire check → tripwire bug (should be non-blocking)
- If exception in diffusion → physics bug
- If out-of-memory → frontier bloated beyond capacity

**Recovery:**
```bash
# Restart in Safe Mode explicitly
export SAFE_MODE_ENABLED=true
python start_consciousness_engine.py
```

### Emergency: Infinite Loop Detected

**Symptom:** Tick duration >60s, process unresponsive

**Immediate Actions:**
1. DO NOT kill process yet - attach profiler if possible
2. Check if stuck in specific mechanism:
   ```python
   # If accessible via debug port
   import pdb; pdb.set_trace()
   # Inspect call stack
   ```

**Common Causes:**
- Diffusion loop over huge frontier (O(N) behavior)
- Criticality power iteration not converging
- Telemetry buffer full (blocking emission)

**Recovery:**
```bash
# Kill process
kill -9 <pid>

# Restart with frontier cap
export MAX_FRONTIER_PCT=0.1  # Force small frontier
python start_consciousness_engine.py
```

---

## 10. Diagnostic Checklist (First Hour)

When system behaves unexpectedly, work through this checklist:

- [ ] Run `diagnose_system.py` - get baseline health
- [ ] Check Safe Mode status - in degraded mode?
- [ ] Identify active tripwire violations - which one firing?
- [ ] Review last 10 ticks of telemetry - what pattern visible?
- [ ] Check service status - all processes running?
- [ ] Inspect conservation - is ΣΔE≈0?
- [ ] Check criticality - is ρ ∈ [0.7, 1.3]?
- [ ] Verify frontier size - is active set <30%?
- [ ] Confirm observability - frame.end events arriving?
- [ ] Review configuration - any recent setting changes?
- [ ] Check for recent code changes - any mechanism modifications?
- [ ] Inspect graph structure - any pathological patterns?

**If all checks pass but system still degraded:** Gather full telemetry dump and file detailed issue with reproduction steps.

---

## 11. Escalation Paths

**Level 1 (Self-Service):** Use this runbook, apply standard fixes
**Level 2 (Team):** Consult team on Slack/Discord with diagnostic output
**Level 3 (Critical Bug):** File GitHub issue with:
- Full diagnostic output
- Violation history
- Telemetry dump (last 100 ticks)
- Reproduction steps
- Configuration at time of failure

**Critical bug indicators:**
- Conservation violated in Safe Mode
- Consciousness loop crashes repeatedly
- Safe Mode auto-exit never occurs
- All tripwires firing simultaneously

---

**Document Status:** Production-ready
**Last Updated:** 2025-10-23
**Maintained By:** Ada "Bridgekeeper" (Architect)

**Feedback:** Report runbook gaps or inaccuracies to GitHub issues with label `runbook-improvement`
