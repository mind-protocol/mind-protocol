# OBJECTIVES: Cognitive Patterns

```
STATUS: CANONICAL
PURPOSE: Define what we're optimizing for in cognitive-build isomorphism
CREATED: 2026-01-30
CONTRIBUTORS: Nicolas Lester Reynolds, Marco
```

---

## Ranked Objectives

### O1: Pattern Recognition — Make the isomorphism actionable

The cognitive model and build system follow the same patterns. Making this explicit enables:
- Predictive insights (what works for brains works for builds)
- Design guidance (cognitive science → build system design)
- Agent architecture (agents as SubEntities)

**Measure:** Engineers can apply cognitive patterns to build decisions.

### O2: Crystallization — Don't lose insights

Insights from deep work sessions (like psilocybin-assisted sessions) should become permanent. The knowledge graph should grow from every exploration.

**Measure:** New patterns are documented, not just discussed.

### O3: Practical Application — These patterns must be usable

Theory without practice is noise. Each pattern document should have:
- Clear implementation guidance
- Minimal and full implementations
- Anti-patterns to avoid

**Measure:** Teams can adopt these patterns without oral tradition.

### O4: Cognitive Isomorphism Integrity — Maintain the mapping

The isomorphism between cognitive model and build system should be accurate. When the cognitive model evolves, the build patterns should follow.

**Measure:** `cognitive-model.mermaid` and these docs stay synchronized.

---

## Non-Objectives

- **Academic rigor** — These are working patterns, not peer-reviewed papers
- **Universal applicability** — Mind Protocol specific, not general frameworks
- **Completeness** — Better to have useful patterns than exhaustive coverage

---

## Tradeoffs

| When | Prefer | Over |
|------|--------|------|
| Pattern conflicts with existing practice | Existing practice wins (they're tested) | New pattern |
| Pattern is useful but incomplete | Ship incomplete pattern | Wait for complete |
| Pattern is elegant but impractical | Practical ugly pattern | Elegant unusable |

---

## Related

- `PATTERNS_Cognitive_Build_Isomorphism.md` — The meta-pattern
- `docs/manifesto/` — Philosophy these patterns embody
- `architecture/cognitive-model.mermaid` — Visual model

---

*The goal is actionable understanding, not beautiful theory.*
