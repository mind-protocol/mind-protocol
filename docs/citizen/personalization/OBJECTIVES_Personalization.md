# OBJECTIVES: Personalization

```
STATUS: DRAFT
DATE: 2026-03-12
PURPOSE: How the system differentiates experience per user
```

---

## Goals (Ranked)

| Rank | ID | Goal | Rationale |
|------|----|----|-----------|
| 1 | G1 | **Each user experiences a distinct, consistent personality adapted to them** | A single AI system serving many users must not feel generic. Nicolas gets Marco (co-creator, French, tutoiement). External users get MIND (warm, scoped, match-language). The personality sticks across sessions. |
| 2 | G2 | **Trust ladder provides progressive access and intimacy** | Not all users are equal. A stranger who just discovered the bot gets 5 messages/day and 80-word replies. A paying Builder subscriber gets 300/day, code access, and autonomous sessions. Trust gates features, quota, prompt depth, and queue priority. |
| 3 | G3 | **Owner gets full co-creator experience; external users get welcoming MIND persona** | Nicolas sees biometrics, journal history, dialogue continuity, all modes, unlimited quota. External users never see any of that. The system switches entirely based on `OWNER_CHAT_ID` / `OWNER_IDS` match. |
| 4 | G4 | **Per-user data enriches over time without manual intervention** | Profiles grow organically: every interaction updates avg message length, interest counts, language detection, formality, voice/emoji usage. No forms required beyond initial registration. |
| 5 | G5 | **No context leakage between users** | External user sessions must never reference Nicolas's journal, biometrics, personal data, or code access. The prompt explicitly states "This is NOT {HUMAN_NAME}" and blocks owner data injection. |

---

## Tradeoffs

| If... | Then sacrifice... | Because... |
|-------|------------------|------------|
| Profile enrichment is too slow (needs many messages) | Immediate personalization depth | Organic data is more reliable than questionnaires |
| Owner prompt is too long (300 words + bio + journal + music) | Token budget for response generation | Owner context richness is worth the cost |
| Trust never decreases | Ability to revoke access from misbehaving users | Rehabilitation-first philosophy; admin_flags handle edge cases |
| Per-user sessions have 5-min TTL | Long conversation continuity for external users | Cost and complexity; owner gets journal as memory substitute |

---

## Non-Goals

- **Per-user model fine-tuning** -- all personalization is prompt-level, not weight-level
- **Cross-platform identity merging** -- `linked_ids` field exists but is not actively resolved at routing time
- **User-facing profile editor** -- profiles are built from interactions, not self-service forms
- **Trust demotion** -- trust is monotonic by design; no mechanism to lower it

<!-- @mind:TODO Determine whether cross-platform identity linking (linked_ids) should be activated at routing time or remain passive -->

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Owner data leakage incidents | 0 (zero tolerance) |
| Profile enrichment rate | >80% of profiles with >=2 interest categories after 10 messages |
| Language detection accuracy | >95% for French/English |
| Trust promotion latency | <1 second from registration completion to medium trust |
| Quota enforcement accuracy | 100% -- no user exceeds their tier limit |

---

## CHAIN

- **Next:** PATTERNS_Personalization.md (design philosophy)
- **Validates:** VALIDATION_Personalization.md
- **Implements:** IMPLEMENTATION_Personalization.md
