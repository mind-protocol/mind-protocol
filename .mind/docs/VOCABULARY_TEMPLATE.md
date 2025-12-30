# {Module Name} — Vocabulary: New Terms

```
STATUS: PROPOSED
CREATED: {DATE}
MODULE: {area}/{module}
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_{name}.md
PATTERNS:        ./PATTERNS_{name}.md
THIS:            VOCABULARY_{name}.md (you are here)
BEHAVIORS:       ./BEHAVIORS_{name}.md
ALGORITHM:       ./ALGORITHM_{name}.md
```

---

## PURPOSE

New terms introduced by this module. After validation, merge into:
- `docs/TAXONOMY.md` — term definitions
- `docs/MAPPING.md` — mind translations

If this module introduces NO new terms, this file can be minimal or omitted.

---

## NEW TERMS

### {Term Name}

```yaml
id: term_{snake_case_name}
definition: |
  {Clear, precise definition}

properties:
  - {property}: {description}

_meta:
  abstraction_level: {1-5}
  literature_status: {L1-L4}
  importance: {1-5 stars}
  confidence: {%}
  precision: {%}

related_terms:
  - {existing_term}: {relationship}
```

**Mapping to mind:**

```yaml
maps_to:
  node_type: {actor | moment | narrative | space | thing}
  subtype: "{type value}"

synthesis_template: "{template}"

content_includes:
  - {what goes in content}
```

---

## NEW RELATIONSHIPS

### {Relationship Name}

```yaml
definition: |
  {What this relationship represents}

between:
  - {source_term} → {target_term}

maps_to:
  polarity: [{a_to_b}, {b_to_a}]
  hierarchy: {value}
  permanence: {value}
```

---

## TASK TYPES

Task types define work that can be done in this module.

**Template node:** `narrative` with `type: task_type`
**Instance node:** `narrative` with `type: {task_type_name}`

### {task_type_name}

```markdown
**Definition:** {What this task accomplishes}

**Executor:** agent | automated | mechanical

**Skill:** {SKILL_Name.md if executor=agent, otherwise N/A}

**Procedure:** {procedure_name}
```

---

## ACTOR TYPES

Actor types define system processes (mechanical) or roles (agent).

**Node:** `actor` with `type: {actor_type_name}`

### {actor_type_name}

```markdown
**Subtype:** mechanical | agent

**Purpose:** {What this actor does}

**Procedures:** {list of procedures this actor runs}

**Triggers:** {cron:5min | event:node_created | manual}
```

---

## TERMINOLOGY PROPOSALS

| Propose | Instead Of | Reason |
|---------|------------|--------|
| {new_term} | {existing_term} | {why change} |

---

## MERGE STATUS

- [ ] Terms reviewed
- [ ] Mappings validated
- [ ] Merged to docs/TAXONOMY.md
- [ ] Merged to docs/MAPPING.md

---

## MARKERS

<!-- @mind:todo {Term needing clarification before merge} -->
