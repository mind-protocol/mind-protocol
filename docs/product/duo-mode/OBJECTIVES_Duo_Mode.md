# OBJECTIVES -- Duo Mode

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_Duo_Mode.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Duo_Mode.md
BEHAVIORS:      ./BEHAVIORS_Duo_Mode.md
ALGORITHM:      ./ALGORITHM_Duo_Mode.md
VALIDATION:     ./VALIDATION_Duo_Mode.md
IMPLEMENTATION: ./IMPLEMENTATION_Duo_Mode.md
SYNC:           ./SYNC_Duo_Mode.md

IMPL:           mind-mcp/runtime/features/duo_mode/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Physiological awareness in conflict** -- MIND sees both partners' biometric state (HR, HRV, stress) in real time and intervenes with timing-aware guidance. A couple arguing while both at elevated cortisol gets "You're both stressed right now -- maybe wait 20 minutes before continuing this conversation." The system prevents damage that happens when people push through physiological dysregulation.

2. **Viral acquisition by structure** -- Every Duo Mode activation requires exactly 2 MIND users. If one partner has MIND and activates Duo Mode, the other partner must get MIND to participate. Every activation = 1 new user. Growth is embedded in the product shape, not in marketing spend.

3. **Co-regulation as the core loop** -- The system doesn't just flag stress. It tracks synchrony between partners over time using Pearson correlation, producing a 0-100 score that reflects how well two nervous systems are learning to co-regulate. The score surfaces patterns invisible to the couple themselves.

4. **Extension to professional coaching** -- The same biometric-synchrony engine generalizes to 1 coach working with N clients (Multi-Duo). A therapist, executive coach, or health practitioner runs a CoachSession that spawns N independent DuoSession children. Same physics, different topology.

## NON-OBJECTIVES

- **Relationship scoring or compatibility matching** -- Duo Mode is not a dating app feature. It doesn't predict compatibility. It observes what is already happening between two people who chose each other.
- **Medical diagnosis** -- Biometric signals inform timing and awareness, not clinical assessment. MIND never says "you have anxiety." It says "your HRV dropped 30% in the last 5 minutes."
- **Replacing therapy** -- The B2B coach extension exists precisely because professional guidance matters. Duo Mode augments human judgment, it doesn't substitute it.
- **Social network features** -- No group chats, no friend lists, no shared feeds. Duo is 2 people. Multi-Duo is 1 coach + N dyads. The topology is strict.

## TRADEOFFS (canonical decisions)

- When privacy conflicts with synchrony accuracy, choose privacy. Each partner controls what biometric data is shared. A partner can participate in Duo Mode with partial data sharing. Better to have an imprecise score than to coerce disclosure.
- When real-time responsiveness conflicts with correlation stability, choose stability. Pearson correlation requires a meaningful window of samples. We accept 60-90 second lag over jittery scores that fluctuate every heartbeat.
- When product simplicity conflicts with coaching flexibility, choose simplicity for v1. Multi-Duo (CoachSession) is v2. The core 2-person experience must be rock-solid before we generalize.
- When engagement conflicts with wellbeing, choose wellbeing. MIND will recommend ending a conversation even if that means less screen time. The product succeeds when couples fight less, not when they use the app more.

## SUCCESS SIGNALS (observable)

- Every Duo Mode activation involves exactly 2 MIND users with active biometric connections
- Synchrony score (0-100) updates within 90 seconds of biometric change
- MIND intervenes with timing recommendations when both partners exceed stress thresholds
- Duo Mode activations convert non-users at measurable rates (viral coefficient > 0.5)
- Partners who use Duo Mode show improved HRV coherence over 30-day windows (the co-regulation loop works)
