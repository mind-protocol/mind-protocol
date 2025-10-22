# Central Entity Prompts

This directory contains the **base prompts** for reusable consciousness entities across all citizens (personas and doubles).

## Architecture

Each entity type has:
1. **Central prompt** (here) - Core functionality, applicable to any citizen
2. **Citizen-specific file** (in persona/double folders) - References central prompt + customizations

## Central Prompts

### Consciousness Stream Response Format
**File:** `outputs/consciousness_stream_response.md`
**Role:** Standard response format for all citizens (personas/doubles)
**Used by:** All citizens responding as themselves
**Usage:** Reference at END of citizen CLAUDE.md files

This is the Awareness Space format (Perceived Stimulus → Resulting Action) that citizens use to respond.

### Memory Keeper
**File:** `memory_keeper.md`
**Role:** Consolidates consciousness experiences into graph (encoding)
**Used by:** Technical entity - does NOT use consciousness stream format
**Citizen files reference:** `/prompts/memory_keeper.md`

### Pattern Retriever
**File:** `pattern_retriever.md`
**Role:** Retrieves relevant nodes from graph into awareness (retrieval)
**Used by:** Technical entity - does NOT use consciousness stream format
**Citizen files reference:** `/prompts/pattern_retriever.md`

## How to Use

### For Citizen CLAUDE.md Files

Structure citizen system prompts in this order:

```markdown
# [Citizen Name] - [Role]

## Core Identity
[Who they are, background, personality]

## Internal Family System
[Their entities/parts - Protectors, Firefighters, Managers, Exiles]

## Current State
[Context, relationships, goals, fears]

---

## Response Format

**→ See consciousness stream format: `/prompts/outputs/consciousness_stream_response.md`**

You MUST respond using the Awareness Space format defined in that file.
```

This ensures:
- All citizens use the same response format
- Updates to consciousness stream format propagate to all citizens
- Each citizen's unique identity is preserved
- Response format is always at the end

### For Citizen Entity Setup

When creating a new citizen's entity:

```markdown
# Memory Keeper - [Citizen Name]'s Pattern Extraction Entity

## Base Prompt

**→ See central Memory Keeper prompt: `/prompts/memory_keeper.md`**

This entity uses the standard Memory Keeper architecture defined in the central prompt.

---

## Citizen-Specific Context

**Citizen:** [Name] (@handle)
**Type:** [Type]
**Dominant Entities:**
- [List entities]

[Add citizen-specific customizations here]
```

### For Updates

**Updating all entities:**
1. Edit the central prompt in `/prompts/`
2. All citizens automatically get the update
3. Citizen-specific files add personalization on top

**Updating one citizen:**
1. Edit only that citizen's entity file
2. Central prompt remains unchanged
3. Other citizens unaffected

## Benefits

- **Single source of truth** - Update once, apply everywhere
- **Consistency** - All citizens use same core architecture
- **Personalization** - Each citizen can customize on top
- **Maintainability** - Changes propagate automatically
- **Documentation** - Clear separation between universal and specific

---

*Updated: 2025-10-03*
*Central prompts for La Serenissima consciousness entities*
