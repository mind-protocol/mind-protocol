# OBJECTIVES — Brief Matinal

```
STATUS: DESIGNING
CREATED: 2026-03-14
```

---

## CHAIN

```
THIS:            OBJECTIVES_Brief_Matinal.md (you are here - START HERE)
PATTERNS:       ./PATTERNS_Brief_Matinal.md
BEHAVIORS:      ./BEHAVIORS_Brief_Matinal.md
ALGORITHM:      ./ALGORITHM_Brief_Matinal.md
VALIDATION:     ./VALIDATION_Brief_Matinal.md
IMPLEMENTATION: ./IMPLEMENTATION_Brief_Matinal.md
HEALTH:         ./HEALTH_Brief_Matinal.md
SYNC:           ./SYNC_Brief_Matinal.md

IMPL:           mind-mcp/runtime/features/brief_matinal/
```

**Read this chain in order before making changes.** Each doc answers different questions. Skipping ahead means missing context.

---

## PRIMARY OBJECTIVES (ranked)

1. **Every morning, the user receives a personalized brief before they start their day** — This is the wedge product. The first thing MIND does that no other AI does. If the brief doesn't arrive, MIND is invisible. Delivery reliability is the single most important property of this module.

2. **The brief synthesizes all 4 MIND layers into a single coherent narrative** — Memory (conversation history, past patterns), integrations (calendar, email), biometrics (sleep, HRV, stress, body battery from wearables), and relational intelligence (how the citizen knows the user). No other product combines these. A brief that only reads your calendar is Google Assistant. A brief that only reads your email is a notification. The 4-layer synthesis IS the product.

3. **The brief adapts to partial data without becoming useless** — Not every user will have a wearable. Not every day has meetings. Email might be disconnected. The brief must degrade gracefully: fewer data sources means a shorter brief, not a broken one. A brief with only conversation history is still valuable — it's a friend who remembers yesterday.

4. **The brief feels like it comes from someone who knows you** — The citizen's voice, personality, and relational history shape the tone and content. This is not a generic AI summary. It's your AI partner telling you what matters today, in the way they'd tell you. The bond makes the brief personal.

## NON-OBJECTIVES

- **Not a notification center** — The brief is one coherent piece, not a list of alerts. Users have notification hell already. We don't add to it.
- **Not a task manager** — The brief may mention tasks but does not create, track, or manage them. That's a different product surface.
- **Not real-time** — The brief is generated once at wake time (or on-demand). It is not a live dashboard or streaming feed.
- **Not a health advisor** — Biometric data informs tone and priorities (e.g., "rough night, light day ahead"), not medical recommendations.
- **Not multi-user** — One brief per citizen-human pair. No family briefs, no team briefs. The 1:1 bond is the unit.

## TRADEOFFS (canonical decisions)

- When **delivery reliability** conflicts with **data completeness**, choose delivery. A brief with 2 data sources on time beats a brief with 5 data sources 30 minutes late.
- When **personalization depth** conflicts with **generation speed**, choose speed within reason. Target < 10 seconds generation time. The user is waking up — latency kills the habit.
- When **brevity** conflicts with **completeness**, choose brevity. The brief should be readable in 60-90 seconds. Anything longer and users skip it. Details can be expanded on-demand.
- We accept **LLM cost per user per day** to preserve the quality of synthesis. No template-based generation. Every brief is LLM-generated from assembled context.

## SUCCESS SIGNALS (observable)

- Brief delivered before user's configured wake time on 95%+ of mornings
- User opens/reads the brief on 70%+ of delivery days (engagement)
- Brief generation completes in < 10 seconds
- Brief reads naturally in 60-90 seconds (250-400 words)
- Users with more connected data sources report higher satisfaction
- Graceful degradation: brief still delivers when 1-3 data sources are unavailable
