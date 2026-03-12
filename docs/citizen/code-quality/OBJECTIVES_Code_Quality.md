# OBJECTIVES: Code Quality

| Field         | Value                                      |
|---------------|--------------------------------------------|
| STATUS        | DRAFT                                      |
| DATE          | 2026-03-12                                 |
| MODULE        | code-quality                               |
| TYPE          | Objectives & constraints                   |

## Primary Objectives (Ranked)

### O1: Produce Correct Code From Natural Language Requests

A Telegram message -- even three words typed on a phone -- must result in production-correct code. The system must bridge the gap between informal intent and precise implementation by reading the actual codebase, understanding naming conventions, import patterns, and architectural decisions, then editing surgically.

### O2: Maintain Codebase Consistency

Every code change must respect existing patterns: naming conventions, import styles, error handling idioms, module boundaries. The model achieves this by reading related files before writing, not by memorizing project conventions. Consistency comes from investigation, not training.

### O3: Enable Autonomous Code Execution Without Human Review Gate

Code produced by the system must be trustworthy enough to merge without human review for routine changes. This requires structural guarantees (read-before-write, extended thinking) rather than procedural ones (code review). The quality gate is built into the tool chain, not into a human approval process.

### O4: Survive Infrastructure Degradation Gracefully

When API limits are hit and the system degrades from Claude Code (full tools) to Claude API (no tools) to OpenAI fallback, code quality degrades predictably. The system must detect this degradation and either produce safe (possibly null) output or clearly signal reduced confidence. Bad code is worse than no code.

## Non-Objectives

| Non-Objective              | Rationale                                                        |
|----------------------------|------------------------------------------------------------------|
| Perfect code from API mode | Degraded mode (no tools) cannot match tool-augmented quality     |
| Human-level code review    | The system verifies its own edits; it does not review others'    |
| Training data improvement  | Quality comes from tools, not from fine-tuning the base model    |

## Tradeoffs

| When...                                          | Choose...         | Accept...                                      |
|--------------------------------------------------|-------------------|-------------------------------------------------|
| Speed conflicts with thoroughness                | Thoroughness      | 30-90 second sessions instead of instant replies|
| Session cost conflicts with quality              | Quality           | Higher API usage from reading 20+ files          |
| Autonomy conflicts with safety                   | Context-dependent | Autonomous for code, gated for comms/safety     |
| Token budget conflicts with thinking depth       | Thinking depth    | 25K thinking tokens even for simple tasks       |

The guiding principle: spend more time reading than writing. A session that reads 20 files and edits 3 lines is more valuable than one that reads 0 files and generates 200 lines.

## Success Signals

| Signal                                                  | Target                                    |
|---------------------------------------------------------|-------------------------------------------|
| Code task success rate (non-degraded)                   | > 95%                                     |
| Edit tool old_string match rate (first attempt)         | > 90%                                     |
| Degraded mode safe-output rate (no bad code)            | 100%                                      |
| Session duration for code tasks                         | 30-120 seconds (thorough, not rushed)     |
| Codebase pattern consistency after AI edits             | Indistinguishable from human patterns     |

## Open Questions

- @mind:TODO Define a formal metric for "codebase consistency" that can be measured automatically (linting, pattern matching, or structural analysis).
- @mind:TODO Determine the acceptable quality threshold below which degraded mode should return null rather than attempt code generation.
