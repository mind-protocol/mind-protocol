# CONCEPT: Autonomy

| Field | Value |
|---|---|
| **Module** | `citizen/autonomy` |
| **Type** | CONCEPT (cross-cutting) |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (forensic analysis of Manemus system) |

---

## Summary

Sustained autonomous work by AI citizens. A system that chooses what to work on, executes without supervision, and produces useful output over extended periods.

Core insight:

> "The mechanism exists and works -- 94 tasks completed, 65% success rate. But it degrades predictably after 4-6 hours due to a specific pathology: infinite retry loops on stuck tasks with no learning between attempts."

Autonomy is NOT one capability. It is the intersection of five systems: task discovery (`project_scanner.py`), task storage (`shrine/backlog.py`), wake scheduling (`shrine/autowake.py`), task execution (`orchestrator.py` -> `invoke_claude`), and multi-account resilience (`account_balancer.py`). Each works individually. The gap is in the feedback loop: the system executes but does not learn from execution failures.

---

## Key Properties

### 1. The Mechanism Works

The autonomous task pipeline is operational and validated over 10 days of real deployment:
- 267 total dispatches, 94 completed tasks, 65% success rate
- Idle detection -> AutoWake gate (momentum + time-of-day) -> priority task selection -> Claude Code spawn -> 15-min timeout -> backlog status update
- 3-account round-robin rotation, 60s cooldown between autonomous task spawns
- Duplicate dispatch prevention via active neuron metadata check

### 2. Predictable Quality Decay

Quality follows a characteristic four-phase curve:

| Phase | Hours | Quality | Cause |
|---|---|---|---|
| Cruise | 0-4h | 80-90% | Fresh backlog, well-specified tasks |
| Plateau | 4-8h | 60-70% | Medium tasks, rate limit cycles |
| Decline | 8-16h | 30-40% | Retry loops on stuck tasks |
| Waste | 16-24h | 10-20% | 99% of compute burned on retries |

This curve is not a mystery. It has a single root cause: the system retries failed tasks with the same prompt, no accumulated failure context, and no circuit breaker. Task "Add CI/CD workflow" was retried 154 times. Task "Fix OOM" was retried 95 times. On March 11, 170 dispatches produced work on only 3 unique task IDs.

### 3. Two Fundamental Needs for Autonomous Citizens

1. **Rich internal world.** Sub-entities with goals, fatigue, curiosity create emergent personality. Without sub-entity fatigue, a task retried 154 times is just a bug. WITH fatigue, the citizen would naturally move on after 5 attempts because the "verification" sub-entity is tired and the "curiosity" sub-entity wants something new.

2. **Rich environment.** Information space, peer communication, external world access. A citizen working alone in a void produces less useful work than one that can see what other citizens have done, read external feeds, and discover work nobody explicitly asked for.

### 4. The Bridge Between Coded and Emergent

The current system simulates autonomy with explicit code: circuit breakers, cooldowns, priority queues, timeout constants. The graph-native system would make these behaviors emergent from sub-entity dynamics. The bridge is behavioral: validate the BEHAVIORS that matter with code first, then make those behaviors emerge from the graph.

---

## The Core Pathology

The system has one critical failure mode that dominates all others:

**Infinite retry loops with no learning between attempts.**

When a task fails, it returns to the backlog with `status: ready` and is immediately re-picked on the next autonomous cycle. The new attempt receives the same prompt, has no knowledge of why the previous attempt failed, and fails in the same way. This continues until a human intervenes or the accounts are exhausted.

Why this happens mechanically:
- `pick_next_autonomous()` in `backlog.py` (line 221) sorts by priority + status but does not penalize high-attempt tasks
- `pick_autonomous_task()` in `orchestrator.py` (line 3792) checks for duplicate active dispatch but not for historical failure count
- The `attempts` field is incremented (line 3849) but never used as a filter or priority modifier
- No failure context is passed from attempt N to attempt N+1

The fix is 20 lines of code. The impact is extending useful autonomy from 6 hours to 16+ hours.

---

## Relationships

**Enables (downstream capabilities):**
- `citizen/initiative` -- autonomous citizens that discover their own work
- `citizen/collaboration` -- inter-citizen task handoff and context sharing
- `economy/compute-allocation` -- efficient use of limited credit budgets

**Depends on (upstream):**
- `citizen/persistence` -- autonomous agents need continuity across task sessions
- `citizen/code-quality` -- autonomous work must be correct without human review
- `infrastructure/degradation` -- graceful degradation protects against runaway compute burn

**Connects to (lateral):**
- `graph/sub-entities` -- fatigue, curiosity, caution as natural autonomy regulators
- `cognitive/attention` -- task selection as an attention allocation problem
- `economy/organism-model` -- autonomous work as metabolic activity of the organism

---

## Common Misunderstandings

### "Autonomy means no human involvement"
No. Human checkpoints are a feature of autonomy, not a failure of it. The system should work independently for 16-20 hours but send periodic digests, escalate blocked tasks, and defer ambiguous or political decisions to the human. The goal is "sustained useful work without constant supervision," not "infinite unsupervised operation."

### "More retries = more persistence"
No. Retrying a failed task 154 times with the same approach is not persistence -- it is pathology. Real persistence means trying different approaches, accumulating context about what didn't work, and eventually escalating to a different strategy or a human. Fatigue is a feature: it prevents waste.

### "The system needs more intelligence to be autonomous"
Not primarily. The system already has sufficient intelligence to complete 65% of tasks correctly. What it lacks is judgment about WHEN to stop, WHAT to try next, and HOW to learn from failures. These are engineering problems (circuit breakers, failure context, priority decay), not intelligence problems.

---

## Open Questions

- @mind:TODO Implement the retry circuit breaker (max 5 attempts -> blocked) and measure the impact on useful autonomy hours
- @mind:TODO Determine whether sub-entity fatigue dynamics can be prototyped within the current orchestrator before full graph-native implementation
- @mind:TODO Quantify the credit cost of the retry pathology -- how much of the monthly $910 AI spend is wasted on futile retries?

---

## References

- `scripts/orchestrator.py` -- `pick_autonomous_task()` (line 3792), `invoke_claude()` (line 2207)
- `shrine/backlog.py` -- task lifecycle, `pick_next_autonomous()` (line 221)
- `shrine/autowake.py` -- momentum/time analysis for wake scheduling
- `scripts/account_balancer.py` -- multi-account round-robin, exhaustion detection
- `scripts/project_scanner.py` -- automated task discovery across repos
