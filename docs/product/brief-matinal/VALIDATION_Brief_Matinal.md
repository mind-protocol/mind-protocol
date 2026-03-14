# Brief Matinal — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Brief_Matinal.md
PATTERNS:        ./PATTERNS_Brief_Matinal.md
BEHAVIORS:       ./BEHAVIORS_Brief_Matinal.md
THIS:            VALIDATION_Brief_Matinal.md (you are here)
ALGORITHM:       ./ALGORITHM_Brief_Matinal.md
IMPLEMENTATION:  ./IMPLEMENTATION_Brief_Matinal.md
HEALTH:          ./HEALTH_Brief_Matinal.md
SYNC:            ./SYNC_Brief_Matinal.md
```

---

## PURPOSE

**Validation = what we care about being true.**

Not mechanisms. Not test paths. Not how things work.

What properties, if violated, would mean the Brief Matinal has failed its purpose?

These are the value-producing invariants — the things that make the wedge product worth building.

---

## INVARIANTS

### V1: Brief Always Delivered by Wake Time

**Why we care:** The brief's value is entirely temporal. A brief delivered 30 minutes after the user wakes up is worthless — they've already checked email, opened their calendar, looked at their wearable app. If this invariant fails, the product has no reason to exist. Users will stop looking for it after 2-3 missed mornings.

```
MUST:   A brief (full, partial, or structured fallback) is delivered to at least one surface
        before the user's configured wake time on every day the user has brief delivery enabled
NEVER:  A scheduled brief fails to deliver entirely (no surface reached, no retry, no fallback)
```

### V2: Missing Data Never Prevents Brief Delivery

**Why we care:** Users have different integration profiles. A user with only conversation history is still a valid user. If the wearable API is down at 6am, that's not the user's problem. The brief must always arrive, even if it's shorter. Coupling brief delivery to external service availability makes the product fragile in exactly the wrong way — the user sees the failure, not the engineering team.

```
MUST:   The pipeline produces a brief from any combination of available data sources,
        including zero external sources (conversation memory alone is sufficient)
NEVER:  A single data source failure (timeout, error, disconnected) causes the entire
        pipeline to fail or delay beyond the wake time deadline
```

### V3: No Duplicate Briefs

**Why we care:** Getting the same brief twice signals a broken product. It breaks trust — "is this yesterday's? did I already read this?" — and on messaging surfaces it's visually disruptive. Worse, in retry/failure scenarios, duplicates can cascade.

```
MUST:   Exactly one alarm-triggered brief per citizen per calendar day
        (idempotency key: date + citizen_id)
NEVER:  Two alarm-triggered briefs delivered for the same citizen on the same day
```

### V4: Brief Reflects the Citizen's Voice

**Why we care:** If the brief sounds like a generic AI assistant, the user has no reason to use MIND over Apple Intelligence or Google's notification summary. The citizen's voice IS the product differentiation. A brief without personality is a feature, not a product.

```
MUST:   Every LLM-generated brief includes the citizen's personality context in the prompt
NEVER:  A brief is generated without citizen personality and relational context loaded from the graph
```

### V5: Brief Does Not Give Medical or Health Advice

**Why we care:** Biometric data (sleep, HRV, stress) is informational context, not diagnostic input. A brief that says "you should rest today" based on HRV data crosses a line MIND must not cross — both for liability and for user trust. The user decides what to do with their body. The citizen reports, not prescribes.

```
MUST:   Biometric data is expressed in everyday language ("rough night", "fully charged")
        without recommendations, diagnoses, or suggestions
NEVER:  The brief includes phrases like "you should", "consider resting", "your HRV suggests",
        or any language that could be interpreted as health advice
```

### V6: Brief Respects Word Count Bounds

**Why we care:** Too short and the brief is a notification, not a synthesis. Too long and the user skips it. The 250-400 word range corresponds to 60-90 seconds of reading — the sweet spot for a morning ritual. Consistently violating this means the brief doesn't fit the user's attention.

```
MUST:   LLM-generated briefs contain between 200 and 500 words
        (soft bounds — hard enforcement at 150 and 600)
NEVER:  A brief exceeds 600 words (user will not read it)
        or falls below 150 words (not enough synthesis to justify the product)
```

### V7: Email Content Stays at Metadata Level

**Why we care:** The brief mentions emails — sender, subject, urgency. It does NOT contain email body text. This is a privacy boundary. Users consented to MIND seeing email metadata, not reading their emails. Violating this boundary breaks trust and potentially legal compliance.

```
MUST:   Email data in the brief is limited to: sender name, subject line, unread count,
        and whether the message is starred/flagged
NEVER:  Email body content, attachment contents, or quoted reply text appears in the brief
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Unusable |
| **HIGH** | Major value lost | Degraded severely |
| **MEDIUM** | Partial value lost | Works but worse |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Brief delivered on time | CRITICAL |
| V2 | Graceful degradation with missing sources | CRITICAL |
| V3 | No duplicate briefs | HIGH |
| V4 | Citizen's personal voice | HIGH |
| V5 | No health advice | HIGH |
| V6 | Readable word count | MEDIUM |
| V7 | Email privacy boundary | HIGH |

---

## MARKERS

<!-- @mind:todo V5 enforcement — should this be a post-generation filter or prompt-level instruction only? Prompt-level is cheaper but less reliable. -->
<!-- @mind:todo V6 word count enforcement — LLM output length is non-deterministic. Need to decide: truncate? regenerate? accept soft violations? -->
<!-- @mind:proposition V8 candidate — Brief generation time < 10 seconds. Currently an objective signal, not a validated invariant. Promote if latency becomes a real problem. -->
<!-- @mind:escalation V7 email privacy boundary — need legal review on whether subject lines alone can contain sensitive information (e.g., "Your HIV test results"). May need subject line filtering. -->
