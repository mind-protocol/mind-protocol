# CONCEPT: Personalization — Differentiated Experience Per User

| Field | Value |
|---|---|
| **Module** | `citizen/personalization` |
| **Type** | CONCEPT (cross-cutting) |
| **Status** | DRAFT |
| **Date** | 2026-03-12 |
| **Author** | Claude (forensic analysis of Manemus system) |

---

## WHAT IT IS

Personalization is the system's ability to present a distinct, consistent experience to each user — not through model fine-tuning, but through layered prompt construction. The same underlying LLM receives radically different system prompts depending on who is talking to it. The result: each user perceives a different entity, even though the engine is the same.

The system currently implements 16 personalization mechanisms, stacked from coarse (owner vs external split) to fine (emoji usage tracking). The most impactful mechanism is the simplest: two completely different prompt templates produce two completely different personas ("Marco" for the owner, "MIND" for everyone else).

---

## WHY IT EXISTS

A single AI system serving many users faces a fundamental tension: intimacy requires depth, but depth for one user risks leaking to another. The owner needs full access — journal, biometrics, code, dialogue history. External users need warmth and usefulness without any exposure to owner data.

Without personalization, the system either treats everyone like strangers (losing the owner relationship) or treats everyone like the owner (leaking private data). The 16 layers resolve this by constructing a unique prompt per interaction that includes exactly the right context for that user and nothing more.

---

## KEY PROPERTIES

- **Dual identity.** The system has two core personas: Marco (co-creator, navigator, French, informal) for the owner, and MIND (warm, welcoming, scoped) for external users. These are not styles — they are entirely different prompt templates with different capabilities, lengths, and access levels.

- **Trust is monotonic.** Once a user reaches a trust level, they never regress. Trust gates quotas (5 to unlimited messages/day), queue priority (+0 to +50), response length (80 to 300 words), and feature access. This design reflects a rehabilitation-first philosophy: the system never punishes.

- **Organic enrichment.** User profiles grow from interactions, not forms. Language detection, interest categorization, communication style tracking, and formality assessment all happen passively. After 10 messages, the system knows enough to personalize meaningfully.

- **Zero leakage architecture.** The external user prompt explicitly states: "This is NOT Nicolas. Do NOT reference Nicolas's activities, biometrics, or personal data." This is not a convention — it is a structural boundary in prompt construction.

- **Platform-aware.** The same user on Twitter gets 270-character responses with no voice. On Telegram, they get text + voice. On the webapp, no voice separator. Personalization adapts to channel constraints.

---

## RELATIONSHIPS TO OTHER CONCEPTS

| Concept | Relationship |
|---------|--------------|
| `citizen/persistence` | Personalization depends on persistence — knowing who someone is requires remembering who they were |
| `citizen/autonomy` | Autonomous actions must respect personalization boundaries — never act on behalf of user A using user B's context |
| `economy/bonds` | Trust tiers map to economic bond depth — higher trust = deeper economic participation |
| `economy/organism-model` | Membrane permeability reflects personalization — trusted users pass through with less friction |

---

## THE CORE INSIGHT

Personalization is not about knowing the user. It is about knowing what prompt to build for them.

The 16 mechanisms are all prompt-level: they decide what gets included in the system prompt, at what length, in what language, with what persona. The LLM itself is unchanged. The "personality" each user experiences is an emergent property of the context window it receives.

This means personalization is:
- **Cheap** — no fine-tuning, no model copies
- **Instant** — new information is available in the next prompt
- **Auditable** — you can read exactly what context any user gets
- **Bounded** — you can prove what a user cannot see

---

## COMMON MISUNDERSTANDINGS

- **Not:** "The AI learns each user's personality over time" — it does track style metrics, but the dominant personalization is structural (prompt template selection), not learned
- **Not:** "Each user gets their own AI" — it is the same model, same weights, same API. The prompt is different.
- **Not:** "Trust is earned through good behavior" — trust is earned through participation. Registration = medium. Subscription = high. There is no behavioral scoring.
- **Actually:** Personalization is prompt engineering at scale, with a privacy guarantee baked into the architecture.

---

## SEE ALSO

- `citizen/persistence` — persistence is the foundation personalization builds on
- `citizen/code-quality` — code interactions are personalized differently from chat
- `economy/organism-model` — membrane physics operationalize trust tiers economically
