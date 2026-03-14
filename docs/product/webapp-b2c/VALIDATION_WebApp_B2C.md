# WebApp B2C -- Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_WebApp_B2C.md
PATTERNS:        ./PATTERNS_WebApp_B2C.md
BEHAVIORS:       ./BEHAVIORS_WebApp_B2C.md
THIS:            VALIDATION_WebApp_B2C.md (you are here)
ALGORITHM:       ./ALGORITHM_WebApp_B2C.md
IMPLEMENTATION:  ./IMPLEMENTATION_WebApp_B2C.md
SYNC:            ./SYNC_WebApp_B2C.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These invariants protect the properties that make the web app worth building: that users can reach their citizen, that conversations persist, that biometric data is accurate and private, that auth is secure. If any of these fail, the product breaks in ways users will feel.

---

## INVARIANTS

### V1: Auth Boundary Is Absolute

**Why we care:** If an unauthenticated user can access any feature route, user data is exposed. This is not a UX issue -- it is a security incident.

```
MUST:   Every route under /(app) requires a valid session
MUST:   Session tokens are HTTP-only cookies (not localStorage, not URL params)
MUST:   Expired sessions redirect to sign-in without exposing any user data
NEVER:  Render user conversations, biometric data, or citizen context to unauthenticated requests
```

### V2: Chat Messages Are Never Lost

**Why we care:** The bond accumulates through conversation. A lost message is a lost piece of the relationship. Users tolerate latency; they do not tolerate data loss.

```
MUST:   Every user message is persisted before the LLM response is streamed
MUST:   Every complete LLM response is persisted after streaming finishes
MUST:   Conversation history is consistent across sessions (no phantom messages, no gaps)
NEVER:  Delete conversation data without explicit user action
```

### V3: Streaming Responses Actually Stream

**Why we care:** A chat that loads for 5 seconds then dumps text is not a conversation -- it is a search engine. Streaming is not a nice-to-have; it is the interaction model that makes the citizen feel alive.

```
MUST:   First token appears within 2 seconds of message submission
MUST:   Tokens render incrementally (at least every 100ms when available)
NEVER:  Buffer the entire response and render at once
NEVER:  Show a loading spinner longer than 2 seconds during normal operation
```

### V4: Biometric Data Belongs to the User

**Why we care:** Health data is the most sensitive data category. Users must trust that their HR, HRV, sleep, and stress data is private, accurate, and exportable. Without this trust, they will never connect their wearable.

```
MUST:   Biometric data is only accessible to the authenticated user who owns it
MUST:   Export produces complete and accurate data matching what is displayed
MUST:   Garmin OAuth tokens are stored encrypted, never logged
NEVER:  Share biometric data across users (even in aggregate, in v0)
NEVER:  Display biometric data that does not match the source (Garmin API)
```

### V5: Brief Is Available When Promised

**Why we care:** The morning brief is the daily retention hook. If the user opens the app at 7am and the brief is not there, the habit breaks. Reliability of delivery matters more than richness of content.

```
MUST:   Brief is rendered and available by the user's configured wake time on 95%+ of mornings
MUST:   Brief renders within 1 second of page load (server-side rendered)
MUST:   Missing data sources reduce brief length, not break brief rendering
NEVER:  Show an error page when the brief is missing (show yesterday's brief or a graceful fallback)
```

### V6: Model Selection Takes Effect Immediately

**Why we care:** If a user selects Claude and their next message still goes to GPT, the selector is a lie. Immediate effect builds trust that the system respects user choices.

```
MUST:   Model preference change is persisted within 1 second
MUST:   Next chat message uses the newly selected model
MUST:   BYOAI keys are encrypted at rest and in transit
NEVER:  Silently ignore a model selection (if model is unavailable, tell the user)
```

### V7: Session Continuity Across Visits

**Why we care:** The bond is long-running. A user who returns after a week should find their conversations, their settings, their connected integrations -- all intact. The citizen remembers; the app must remember too.

```
MUST:   Sessions persist for 30 days with rolling expiry
MUST:   Conversation history is available across sessions without re-authentication
MUST:   User preferences (model, timezone, Garmin connection) persist indefinitely
NEVER:  Lose user state on session refresh or token rotation
```

### V8: Error States Are Human-Readable

**Why we care:** Technical error messages destroy trust. A user who sees "500 Internal Server Error" or "TypeError: Cannot read property 'x' of undefined" will not come back. Every error the user can see must be written for a human.

```
MUST:   All user-visible errors have human-readable messages
MUST:   Errors suggest an action (retry, refresh, contact support)
NEVER:  Expose stack traces, error codes, or internal service names to the user
NEVER:  Show a blank page on error (always render error boundary with helpful message)
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
| V1 | Auth boundary security | CRITICAL |
| V2 | Chat message persistence | CRITICAL |
| V3 | Streaming interaction model | HIGH |
| V4 | Biometric data privacy and accuracy | CRITICAL |
| V5 | Brief availability and reliability | HIGH |
| V6 | Model selection integrity | MEDIUM |
| V7 | Session and state continuity | HIGH |
| V8 | Human-readable error states | MEDIUM |

---

## MARKERS

<!-- @mind:todo Add invariant for accessibility (WCAG 2.1 AA minimum) when design system is defined -->
<!-- @mind:proposition Consider V9 for performance budget: LCP < 2.5s, FID < 100ms, CLS < 0.1 -->
<!-- @mind:escalation V4 (biometric privacy) may require specific GDPR/HIPAA compliance review before launch -->
