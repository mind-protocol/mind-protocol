# OBJECTIVES: Autonomy

| Field | Value |
|---|---|
| **Module** | `citizen/autonomy` |
| **Type** | OBJECTIVES |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (forensic analysis of Manemus system) |

---

## Primary Objectives (Ranked)

### O1: Sustained useful work for 16-20+ hours without human intervention

The system must maintain productive output for at least 16 hours of continuous autonomous operation. "Productive" means completing tasks that would not need to be redone by a human. The current ceiling is 4-6 hours before quality decay makes output net-negative. The gap is not intelligence -- it is judgment about when to stop retrying and what to try next.

Success metric: tasks completed per hour remains above 2 for the first 16 hours.

### O2: Intelligent task selection

The system must choose tasks wisely, not just by static priority. This means:
- Avoid tasks that have failed repeatedly (priority decay with attempts)
- Rotate across categories (don't grind on 5 consecutive "fix" tasks)
- Estimate difficulty relative to current capability (prefer tasks with clear specifications)
- Front-load easy tasks when the backlog is fresh, defer hard tasks to human-supervised hours

Success metric: dispatch-to-unique-task ratio stays below 2.0 (currently 2.8 overall, 56.7 on worst day).

### O3: Learn from failures

Each task attempt must be richer than the last. When attempt N fails, attempt N+1 must know:
- What was tried (the approach taken)
- Why it failed (error messages, test output, architectural blockers)
- What remains untried (alternative approaches the system hasn't explored)

The prompt for attempt N+1 must include the accumulated failure context from all previous attempts. Without this, every attempt is a fresh start from the same position -- guaranteed to fail the same way.

Success metric: same-task retry success rate increases with attempt number (currently flat).

### O4: Quality gates before marking done

The system must validate its own work before marking a task as "done." Validation includes:
- Code compiles and passes linting
- Tests pass (if tests exist for the modified code)
- The change does not break existing functionality
- The task description's requirements are met

Without quality gates, autonomous work creates compounding errors: task B modifies a file that task A already broke, and task C depends on both.

Success metric: <5% of "done" tasks need human rework.

### O5: Self-replenishment

The backlog must never stay empty for more than 4 hours during autonomous operation. When the ready queue runs low, the system should:
- Run `project_scanner.py` to discover new work items
- Scan for TODOs, FIXMEs, broken tests, documentation gaps
- Generate tasks from observed patterns (e.g., "module X has tests but module Y doesn't")

Success metric: backlog depth stays above 10 ready tasks during autonomous periods.

---

## Non-Objectives

- **Infinite autonomy.** Human checkpoints are healthy, not a failure. The system should produce periodic digests (every 10 tasks or 4 hours), escalate blocked items, and defer ambiguous or politically sensitive decisions.
- **Working on ambiguous tasks.** Tasks requiring judgment about product direction, user-facing copy, or strategic priorities should be deferred to human review. The system should recognize ambiguity and flag it rather than making unilateral decisions.
- **Pushing to production without review.** Autonomous work should create commits and branches, not deploy. Production pushes require human sign-off, at least until the quality gate system (O4) is proven reliable.
- **Replacing human creativity.** The system excels at well-specified implementation tasks (docs, tests, refactoring, bug fixes). Creative tasks (new features, architecture design, communication strategy) are collaborative, not autonomous.

---

## Tradeoffs

### Thoroughness vs. Throughput

When thoroughness conflicts with throughput, **choose thoroughness.** Fewer tasks done well is better than many tasks done badly. A single bad change can infect all subsequent tasks through compounding errors. The system should complete 6 tasks correctly in 8 hours rather than attempt 20 tasks and leave 14 broken.

Rationale: compounding errors are the real danger in autonomous systems. One incorrect import path propagated across 3 files creates 3 bugs from 1 error. The cost of undoing bad work exceeds the benefit of doing more work.

### Speed vs. Sustainability

When speed conflicts with sustainability, **choose sustainability.** Burning through all 3 Max accounts in 4 hours of aggressive parallelism leaves 20 hours with no capacity. The system should pace itself to sustain operations across a full 24-hour cycle.

Rationale: the monthly budget is $910/mo across 3 Max accounts. Aggressive autonomous work can burn $50/day in credits. The system must stay within sustainable limits.

### Autonomy vs. Safety

When autonomy conflicts with safety, **choose safety.** Specifically:
- Never modify security-sensitive files (credentials, .env, auth logic) without human review
- Never make breaking API changes autonomously
- Never push to main branch without CI passing
- Never modify the orchestrator or backlog system itself (self-modification risk)

---

## Success Signals

1. **16+ useful hours.** The system produces net-positive output for 16 consecutive hours without human intervention.
2. **Retry ratio below 2.0.** Each unique task is dispatched fewer than 2 times on average.
3. **Backlog self-replenishing.** The ready queue maintains 10+ tasks through automated scanning.
4. **No compounding errors.** Task N+1 does not break what task N built.
5. **Human digest useful.** The periodic Telegram summary accurately reflects what was accomplished and what is blocked.

---

## Open Questions

- @mind:TODO Define the exact boundary between "autonomous-safe" and "needs-human-review" task categories. Current heuristic is category-based (docs/test/fix = safe, feature/refactor = review). Is this sufficient?
- @mind:TODO Determine the optimal autonomous task pacing: how many tasks per hour maximizes quality-adjusted throughput?
- @mind:TODO Establish credit budget guardrails: what daily spend limit should the system enforce to stay within the $910/mo budget?

---

## References

- `scripts/orchestrator.py` -- `pick_autonomous_task()`, `AUTONOMOUS_TASK_COOLDOWN=60`
- `shrine/backlog.py` -- task lifecycle, priority ordering
- `scripts/project_scanner.py` -- automated task discovery
- `scripts/account_balancer.py` -- credit/account management
