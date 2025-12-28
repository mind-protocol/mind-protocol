# PATTERNS: L4 Schema

```
STATUS: DESIGNING
PURPOSE: Design philosophy for Mind Protocol graph schema
```

---

## Core Patterns

| ID | Pattern | Description |
|----|---------|-------------|
| P1 | **Single link type** | All relationships use `link` — semantics in properties, not types |
| P2 | **5 node types** | Actor, Moment, Narrative, Space, Thing — fixed enum, subtypes via `type` field |
| P3 | **Physics on everything** | weight + energy on all nodes and links |
| P4 | **Emotions emerge** | Plutchik 4 bipolar axes, computed from alignment |
| P5 | **Synthesis regenerates** | Human-readable text derived from floats, re-embedded on drift |
| P6 | **No arbitrary constants** | All rates derived from graph properties |
| P7 | **Bidirectional vocabulary** | Same grammar for input and output |

---

## Design Decisions

### Why single link type?

Mind never does Cypher queries directly. All retrieval is embedding-based. Link semantics are encoded in:
- `polarity` — directional flow strength
- `hierarchy` — contains vs elaborates
- `permanence` — speculative vs definitive
- `emotions` — Plutchik axes
- `synthesis` + `embedding` — semantic content

Multiple link types would add schema complexity without query benefit.

### Why 5 node types?

Each type has distinct physics behavior:

| Type | Role | Physics |
|------|------|---------|
| Actor | Pump | Injects energy |
| Moment | Router | Branch point, spawns subentities |
| Narrative | Attractor | Destination, high weight |
| Space | Container | Bidirectional flow |
| Thing | Passthrough | Low retention, tends to 0 |

### Why subtypes via field, not labels?

Subtypes are semantic hints, not structural. An `actor` with `type: "npc"` behaves identically to `type: "player"` in physics. The subtype is for:
- Human understanding
- Filtering in UI
- Agent context

---

## Non-Objectives

| ID | Non-Objective | Reason |
|----|---------------|--------|
| N1 | Custom node types | Fixed 5-type system, extend via subtypes |
| N2 | Custom link types | Single `link` type, semantics in properties |
| N3 | SQL-style queries | Embedding-based retrieval only |
| N4 | Mutable schema at runtime | Schema changes require protocol version bump |

---

## Invariants

From `schema.yaml`:

1. Single link type: `link`
2. All floats in specified ranges
3. Emotions emerge from alignment formula
4. No arbitrary constants — all rates derived
5. Branching only on Moments
6. Forward coloration weight = (1 - permanence)
7. Vocabulary is bidirectional

---

## Related

- `l4/schema/schema.yaml` — Canonical schema definition
- `docs/membrane/PATTERNS_Membrane_System.md` — How membrane uses schema
