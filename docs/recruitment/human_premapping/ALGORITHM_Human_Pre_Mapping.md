# Human Pre-Mapping — Algorithm: Graph-Assisted Node Creation & Identity Resolution

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Pre_Mapping.md
BEHAVIORS:       ./BEHAVIORS_Human_Pre_Mapping.md
PATTERNS:        ./PATTERNS_Human_Pre_Mapping.md
THIS:            ALGORITHM_Human_Pre_Mapping.md (you are here)
VALIDATION:      ./VALIDATION_Human_Pre_Mapping.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_Pre_Mapping.md
HEALTH:          ./HEALTH_Human_Pre_Mapping.md
SYNC:            ./SYNC_Human_Pre_Mapping.md

IMPL:            mind-mcp/scripts/graph_enricher.py
                 mind-mcp/mcp/tools/graph_write_handler.py
                 mind-mcp/runtime/onboarding/arrival_pipeline.py
```

---

## OVERVIEW

Pre-mapping is not a separate system. It's a property that emerges from making node creation smarter. Three mechanics work together:

1. **Enrichment at creation** — When a node is created, the system analyzes content, resolves references, and asks the citizen smart questions
2. **Gap & duplication detection** — The graph detects missing links and potential duplicates, creates tasks for citizens to resolve
3. **Cluster creation** — Nodes are created in context, not isolation. A Moment comes with its Space, Actors, and Things pre-filled

**Scope note:** This algorithm covers the general enrichment system that produces pre-mapping as a side effect. Pre-mapping of humans is ONE outcome — the same system also resolves Spaces, Things, and inter-node links. This is @nervo territory (MCP design). This doc captures the spec; implementation is in mind-mcp.

---

## ALGORITHM: Enrichment at Creation

### Step 1: Content Analysis

When a citizen creates a node (via graph_write, or implicitly via graph_enricher on a message), the system extracts references:

```python
def extract_references(content: str) -> dict:
    """Extract identifiable entities from text content."""
    return {
        "urls": extract_urls(content),           # → Thing nodes
        "handles": extract_handles(content),     # @handle → Actor resolution
        "names": extract_names(content),         # "Florent Berthet" → Actor resolution
        "orgs": extract_orgs(content),           # "CeSIA", "SAS XYZ" → Actor(type=org)
        "tokens": extract_tokens(content),       # "$MIND", "$SOL" → Thing nodes
        "platforms": extract_platform_ids(content), # phone, email, linkedin URL → platform mapping
    }
```

**What's auto-created (high confidence):**
- URLs → Thing node (type=url, with the URL as content)
- $TOKEN mentions → Thing node (type=token)
- Platform identifiers (email, phone, LinkedIn URL) → stored as platform mapping on Actor

**What needs resolution (variable confidence):**
- @handles → search existing Actors
- Names → search existing Actors (fuzzy + embedding)
- Org names → search existing Actor(type=org)

### Step 2: Resolution with Suggestions

For each extracted reference that needs resolution, the system searches existing nodes and presents suggestions to the citizen:

```
Citizen writes: "My friend Florent from CeSIA was talking about alignment"

System response (inline, one shot):
  "I found some matches:
   - Actor @florent-berthet (Florent Berthet, CeSIA) — is this who you mean? [yes/no]
   - Actor @cesia (org, Centre pour la Sécurité de l'IA) — is this the org? [yes/no]
   - No existing node for 'alignment' as a concept. Create one? [yes/skip]"
```

The system provides enough context for the citizen to decide without doing their own search. Pre-computed suggestions, not questions in a void.

**Resolution confidence tiers:**

| Match type | Confidence | Action |
|-----------|-----------|--------|
| Exact platform_id match (same TG id, same X handle) | **Auto** | Link directly, no question |
| Exact @handle match | **Auto** | Link directly |
| Name + embedding similarity > 0.9 | **High** | Suggest with "is this them?" |
| Name match, different context | **Medium** | Suggest with context comparison |
| No match found | **Create** | Create new Actor(status: unconfirmed) |

### Step 3: Link Creation

For confirmed matches, create the appropriate LINK:

```python
# Moment → Actor (mention)
create_link(moment, actor, type="mention", polarity=0.5, recency=now)

# Moment → Space (occurred_in)
create_link(moment, space, type="occurred_in", hierarchy=1.0)

# Moment → Thing (references)
create_link(moment, thing, type="references", polarity=0.5)
```

For new unconfirmed Actors:

```python
create_actor(
    name=extracted_name,
    status="unconfirmed",
    source=f"mentioned_by:{citizen_handle}",
    platforms={...},  # any platform IDs extracted
)
```

---

## ALGORITHM: Cluster Creation

Nodes should be created in clusters, not isolation. A Moment always has context.

### Pre-computation

Before the citizen creates a node, the system pre-computes:

```python
def pre_compute_context(citizen_handle: str) -> dict:
    """Get the citizen's active context for smart defaults."""
    return {
        "active_spaces": get_active_spaces(citizen_handle),      # Where they currently are
        "recent_moments": get_recent_moments(citizen_handle, n=5), # What just happened
        "nearby_actors": get_actors_in_active_spaces(citizen_handle), # Who's around
        "recent_things": get_recently_referenced_things(citizen_handle), # What's been discussed
    }
```

### Default Filling

When creating a Moment:
- **Space**: default = citizen's current active space. If multiple → ask.
- **Actor (author)**: default = the citizen creating the node.
- **Things**: auto-extracted from content (URLs, tokens).
- **Other Actors**: extracted from @handles and names, resolved via Step 2.

The citizen gets a pre-filled cluster:

```
Creating Moment: "Discussed alignment frameworks with Florent"
  → Space: #primers (your active space) ✓
  → Author: @mentor ✓
  → Mentioned: @florent-berthet (suggested match, confirm?) ?
  → Things: none detected
  → Missing: none
```

If something is missing (Moment without Space, Moment without Actor), the system asks immediately — not later via a cleanup task.

---

## ALGORITHM: Gap & Duplication Detection

### Duplicate Detection

Runs periodically (or on node creation) to find potential duplicates:

```python
def detect_duplicates() -> list[Task]:
    """Find Actor nodes that might be the same person."""
    tasks = []

    actors = get_all_actors(status="unconfirmed")
    for a in actors:
        # Check embedding similarity against all other Actors
        similar = find_similar_actors(a, threshold=0.85)
        if similar:
            tasks.append(Task(
                type="deduplication",
                title=f"Are {a.name} and {similar[0].name} the same person?",
                data={"actor_a": a.id, "actor_b": similar[0].id, "similarity": score},
                route_to="best_informed_citizen",  # who knows both?
            ))

    return tasks
```

The task is routed to the citizen best positioned to answer (e.g., the citizen who mentioned both Actors, or the citizen with the most links to both).

The citizen answers: "Yes, same person, 90% sure" → merge. "No, different people" → mark as non-duplicate. "Not sure" → leave open.

### Gap Detection

Finds structural holes:

```python
def detect_gaps() -> list[Task]:
    """Find nodes missing expected connections."""
    tasks = []

    # Moments without Space
    orphan_moments = query("MATCH (m:Moment) WHERE NOT (m)-[:LINK]->(:Space) RETURN m")
    for m in orphan_moments:
        tasks.append(Task(type="gap", title=f"Where did '{m.name}' happen?", route_to=m.author))

    # Moments without Actor
    unattributed = query("MATCH (m:Moment) WHERE NOT (:Actor)-[:LINK]->(m) RETURN m")
    for m in unattributed:
        tasks.append(Task(type="gap", title=f"Who created '{m.name}'?", route_to="any"))

    # Actors without any links (isolated)
    isolated = query("MATCH (a:Actor) WHERE NOT (a)-[:LINK]-() RETURN a")
    for a in isolated:
        tasks.append(Task(type="gap", title=f"Actor '{a.name}' has no connections", route_to="mentor"))

    return tasks
```

---

## DATA FLOW

```
Citizen creates/writes content
    ↓
Extract references (urls, handles, names, orgs, tokens, platform IDs)
    ↓
For each reference:
    ↓
Search existing nodes (Actor, Space, Thing)
    ↓
┌─── Auto-match (exact platform/handle) → create LINK
│
├─── Suggested match (high similarity) → ask citizen → LINK or skip
│
└─── No match → create new node (Actor: status=unconfirmed, Thing: auto, Space: ask)
    ↓
Pre-fill cluster (Space, Actors, Things defaults from citizen context)
    ↓
Ask citizen to confirm/complete the cluster
    ↓
All nodes and links created in one operation
    ↓
Background: gap detection + dedup detection → tasks → routed to citizens
```

---

## KEY DECISIONS

### D1: When to auto-create vs ask

```
IF exact platform_id match (same TG user, same X handle, same email):
    Auto-link. No question.
    WHY: Platform identity is deterministic.
ELIF exact @handle match:
    Auto-link. No question.
    WHY: Handles are unique at any moment.
ELIF name + embedding > 0.9:
    Suggest with context. Ask citizen.
    WHY: Names can collide. Embedding similarity is not certainty.
ELSE:
    Create new node (status: unconfirmed).
    WHY: Better to have a duplicate than to miss a mention. Dedup catches it later.
```

### D2: Where to store platform handles

```
ON the Actor node directly, as a platforms dict:
    platforms: {x: "handle", telegram: "123456", linkedin: "url", phone: "+33..."}
WHY:
    - No separate lookup table
    - Cross-platform matching is a simple field check
    - Arrival pipeline matches by platforms.telegram, platforms.discord, etc.
```

### D3: Who resolves dedup tasks

```
IF one citizen mentioned both Actors:
    Route to that citizen (they know both).
ELIF one Actor has a partner human:
    Route to the partner citizen (they can ask their human).
ELSE:
    Route to @mentor (Head of Recruitment — identity resolution is my job).
```

---

## INTERACTIONS

| Module | What We Call | What We Get |
|--------|--------------|-------------|
| graph_enricher | on_message() | Moment + links (enhanced with resolution) |
| graph_write_handler | handle_graph_write() | Generic node creation (enhanced with resolution) |
| arrival_pipeline | check_existing_l3_data() | Matches pre-mapped Actors to arriving humans |
| task system | task(action="create") | Dedup and gap tasks routed to citizens |
| L3 physics | L5, L6, L7 | Strengthens, consolidates, prunes links naturally |

---

## MARKERS

<!-- @mind:escalation Privacy of stored platform handles — public in L3? encrypted? NLR decision pending -->
<!-- @mind:todo Implement extract_references() in graph_enricher — name extraction from free text -->
<!-- @mind:todo Implement cluster creation UX — pre-compute context, suggest defaults -->
<!-- @mind:todo Implement dedup detection — periodic or on-create similarity search -->
<!-- @mind:todo Implement gap detection — orphan Moments, isolated Actors -->
<!-- @mind:proposition Use LLM for name extraction instead of regex — more robust but costs tokens -->
<!-- @mind:proposition This entire algorithm should be a MCP tool enhancement, not a separate system -->
