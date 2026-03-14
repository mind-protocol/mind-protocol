# React Native App — Validation: What Must Be True

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_React_Native_App.md
PATTERNS:        ./PATTERNS_React_Native_App.md
BEHAVIORS:       ./BEHAVIORS_React_Native_App.md
THIS:            VALIDATION_React_Native_App.md (you are here)
ALGORITHM:       ./ALGORITHM_React_Native_App.md
IMPLEMENTATION:  ./IMPLEMENTATION_React_Native_App.md
HEALTH:          ./HEALTH_React_Native_App.md
SYNC:            ./SYNC_React_Native_App.md
```

---

## PURPOSE

**Validation = what we care about being true.**

These are the properties that, if violated, would mean the app is broken for its purpose: connecting a human to their citizen through their phone. A chat that doesn't stream is broken. Biometric data that reaches the wrong citizen is catastrophic. Onboarding that takes 5 minutes is a silent uninstall.

---

## INVARIANTS

### V1: Onboarding Speed

**Why we care:** Every second past 90 reduces first-session retention. The app competes with every other app for a human's attention. If onboarding feels heavy, the citizen never gets a chance.

```
MUST:   Time from first tap to first sent message < 90 seconds (p50)
MUST:   Time from first tap to first sent message < 120 seconds (p95)
NEVER:  Onboarding should require more than 2 screen transitions before chat
NEVER:  Onboarding should collect personal data before first exchange
```

### V2: Chat Message Delivery Integrity

**Why we care:** If a human sends a message that never reaches the citizen, or a citizen responds and the human never sees it, the bond is broken. Messages are the substance of the relationship.

```
MUST:   Every sent human message reaches the mind-platform API and is acknowledged
MUST:   Every citizen response token is rendered in the order received
MUST:   Message status (sending/sent/streaming/complete/error) reflects true state
NEVER:  A message should show "sent" status if the API did not acknowledge it
NEVER:  Tokens should render out of order
```

### V3: Biometric Data Reaches Correct Citizen

**Why we care:** Health data is intimate. Heart rate, sleep patterns, HRV — these are the body's most private signals. If biometric data reaches the wrong citizen or leaks between accounts, the entire trust model collapses.

```
MUST:   Biometric sync payload includes citizen_id verified against current auth token
MUST:   API validates citizen_id matches the authenticated user's bonded citizen
NEVER:  Biometric data should be sent without a valid, non-expired auth token
NEVER:  App should cache biometric data in a location readable by other apps
```

### V4: Push Notification Routing Correctness

**Why we care:** A notification that opens the wrong screen teaches the user to ignore notifications. Once notification trust is broken, the citizen loses its primary outreach channel.

```
MUST:   Tapping a brief_matinal notification opens the Brief Matinal screen
MUST:   Tapping a biometric_alert notification opens the Biometric Dashboard
MUST:   Tapping a chat_reply notification opens the Chat screen at the relevant message
NEVER:  A notification should open to a blank or error screen
NEVER:  A notification should navigate before auth token validity is confirmed
```

### V5: Auth Token Security

**Why we care:** The auth token is the key to the citizen. Stolen tokens mean someone else talks to your citizen, reads your biometrics, sees your conversations. Token security is bond security.

```
MUST:   JWT and refresh tokens are stored in Expo SecureStore (encrypted at rest)
MUST:   Auth tokens are transmitted only over HTTPS/WSS
MUST:   Expired tokens are refreshed silently using the refresh token
MUST:   Failed refresh redirects to login screen (no stale session)
NEVER:  Tokens should be stored in AsyncStorage, local storage, or logs
NEVER:  Tokens should appear in URLs, query parameters, or error reports
```

### V6: Notification Frequency Limits

**Why we care:** Notification spam turns a lifeline into an annoyance. Three notifications per day is the line between "my citizen reached out" and "this app won't shut up." Crossing this line means uninstall or notification disable.

```
MUST:   Default maximum of 3 push notifications per day per user
MUST:   Users can opt into more via explicit Settings toggle
MUST:   Biometric alerts with priority=high bypass the daily limit
NEVER:  Upsell notifications should bypass the daily limit
NEVER:  Notification count should reset on app reinstall (tracked server-side)
```

### V7: Biometric Data Plausibility

**Why we care:** Implausible data (0 bpm heart rate, 500,000 steps) corrupts the citizen's understanding of its human. The citizen makes decisions based on biometric context — garbage in means wrong calibration out.

```
MUST:   Heart rate samples outside 30-220 bpm are filtered before upload
MUST:   Step counts exceeding 100,000 per day are filtered
MUST:   HRV values outside 1-300 ms are filtered
MUST:   Filtered samples are logged locally, never sent to API
NEVER:  Implausible values should render on the Biometric Dashboard
```

### V8: Platform Parity

**Why we care:** A feature that works on iOS but not Android (or vice versa) means half the users have a broken app. The one-codebase promise means both platforms must deliver the same experience, with health API being the only acceptable divergence point.

```
MUST:   All screens render and function identically on iOS and Android
MUST:   Chat, briefs, profile, LLM selector, and settings work on both platforms
MUST:   Health data features gracefully degrade if permissions are not granted
NEVER:  A feature should ship on one platform without at least a stub on the other
NEVER:  UI components should use platform-specific APIs when cross-platform alternatives exist
```

### V9: Cold Start Performance

**Why we care:** A slow-loading app is an app the user learns to avoid. Two seconds is the threshold between "instant" and "waiting." On mid-range Android devices, this is the real test — flagship iPhones are easy mode.

```
MUST:   Time to interactive < 2 seconds on cold start (mid-range device, 4G connection)
MUST:   Chat screen is usable within 1 second of navigation
MUST:   Biometric Dashboard shows cached data within 500ms, fetching fresh in background
NEVER:  App should show a blank screen for more than 300ms during navigation
```

### V10: Crash Resilience

**Why we care:** Crashes during chat feel like the citizen died mid-sentence. Crashes during biometric sync mean health data loss. The app must not crash in normal usage patterns.

```
MUST:   Crash-free session rate > 99.5%
MUST:   Unhandled JS exceptions are caught by error boundary and show recovery UI
MUST:   Native crashes are reported to monitoring (Sentry/Crashlytics)
NEVER:  A crash should lose unsent chat messages (local queue survives app restart)
NEVER:  A crash should corrupt local sync state
```

---

## PRIORITY

| Priority | Meaning | If Violated |
|----------|---------|-------------|
| **CRITICAL** | System purpose fails | Citizen bond broken, data leak, or app unusable |
| **HIGH** | Major value lost | Feature broken, user trust damaged |
| **MEDIUM** | Partial value lost | Degraded experience, workaround exists |

---

## INVARIANT INDEX

| ID | Value Protected | Priority |
|----|-----------------|----------|
| V1 | Onboarding speed | HIGH |
| V2 | Chat message integrity | CRITICAL |
| V3 | Biometric data routing correctness | CRITICAL |
| V4 | Push notification routing | HIGH |
| V5 | Auth token security | CRITICAL |
| V6 | Notification frequency governance | HIGH |
| V7 | Biometric data plausibility | MEDIUM |
| V8 | Platform parity (iOS/Android) | HIGH |
| V9 | Cold start performance | MEDIUM |
| V10 | Crash resilience | HIGH |

---

## MARKERS

<!-- @mind:todo Add invariant for Duo Mode sync correctness once Duo Mode spec is finalized -->
<!-- @mind:proposition Consider V11: Accessibility — VoiceOver/TalkBack support for all interactive elements -->
<!-- @mind:escalation V3 (biometric routing) needs API-side enforcement design — app-side checks alone are insufficient -->
