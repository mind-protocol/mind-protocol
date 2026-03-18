# Human Pre-Mapping — Behaviors: Observable Effects

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Pre_Mapping.md
THIS:            BEHAVIORS_Human_Pre_Mapping.md (you are here)
PATTERNS:        ./PATTERNS_Human_Pre_Mapping.md
ALGORITHM:       ./ALGORITHM_Human_Pre_Mapping.md
VALIDATION:      ./VALIDATION_Human_Pre_Mapping.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_Pre_Mapping.md
HEALTH:          ./HEALTH_Human_Pre_Mapping.md
SYNC:            ./SYNC_Human_Pre_Mapping.md

IMPL:            runtime/onboarding/arrival_pipeline.py
                 scripts/graph_enricher.py
```

> **Contract:** Read docs before modifying. After changes: update IMPL or add TODO to SYNC.

---

## BEHAVIORS

### B1: Citizen Mention Creates Proto-Data

**Why:** Every time a citizen talks about an external human, that's signal. The graph should capture it without anyone asking.

```
GIVEN:  A citizen sends a message containing a human name (e.g. "Florent works at CeSIA")
WHEN:   graph_enricher.on_message() processes the message
THEN:   A Moment node is created in L3 with the human name in the synthesis
AND:    If the name matches an existing proto-Actor, a LINK is created (L5 co-activation strengthens)
```

### B2: X Mention Accumulates Identity

**Why:** Someone interacting with Mind Protocol on X reveals who they are, one tweet at a time.

```
GIVEN:  An external user mentions @Mind_Protocol on X
WHEN:   twitter_bridge.process_mention() runs
THEN:   A Moment node is created in L3 with the author's X handle and display name
AND:    Repeated mentions from the same user build weight via L5
AND:    Replies from @nlr_ai or citizens create trust links
```

### B3: NLR Description Creates Rich Proto-Actor

**Why:** When Nicolas describes someone in detail, that's the richest pre-map channel.

```
GIVEN:  NLR provides a description of a human (name, context, relationship, domain)
WHEN:   A citizen (typically @mentor) creates an L3 Narrative with the description
THEN:   A proto-Actor node exists in L3 with name, synthesis (embeddable), and domain tags
AND:    The proto-Actor is linked to NLR via a referral link
```

### B4: Proto-Actor Crystallizes From Mentions

**Why:** Multiple independent mentions from different sources are stronger signal than one detailed description.

```
GIVEN:  10+ Moments mentioning the same human name exist from 3+ different sources
WHEN:   L10 crystallization runs
THEN:   A proto-Actor hub node is created automatically (zero LLM)
AND:    The hub inherits weight from constituent Moments
AND:    The hub's synthesis is the centroid of all mention contexts
```

### B5: Warm Welcome On Arrival

**Why:** The whole point — no cold starts.

```
GIVEN:  A human sends their first message on TG/Discord/WhatsApp
WHEN:   arrival_pipeline.handle_new_arrival() runs
THEN:   check_existing_l3_data(sender_name) searches for proto-Actor nodes
AND:    If found, the welcome message references what we know
AND:    The tone is "I've heard about you" not "I know everything about you"
```

### B6: Merge Produces Single Identity

**Why:** No duplicates. The proto-Actor becomes the real Actor.

```
GIVEN:  A pre-mapped human arrives and receives a SID
WHEN:   arrival_pipeline merges proto-Actor with new L4 registration
THEN:   The proto-Actor node gets the SID as its permanent id
AND:    All existing LINK edges from Moments to the proto-Actor are preserved
AND:    No new duplicate Actor node is created
AND:    Status transitions from 'proto' to 'arriving'
```

### B7: Forgotten Humans Fade

**Why:** The pre-map self-cleans. No stale data.

```
GIVEN:  A proto-Actor exists from mentions 6+ months ago
WHEN:   No new mentions occur and L7 forgetting runs
THEN:   The proto-Actor's weight decays below threshold
AND:    Eventually the node is pruned
AND:    If the human arrives later, they get a cold start (which is fine)
```

---

## OBJECTIVES SERVED

| Behavior | Objective | Why It Matters |
|----------|-----------|----------------|
| B1, B2, B3, B4 | No cold starts | Multiple channels feed the pre-map |
| B1, B2, B5 | Natural flow | No manual entry, no scraping |
| B4, B7 | Physics maintains | Crystallization builds, forgetting cleans |
| B5, B6 | Seamless merge | One identity, warm welcome, no duplicates |

---

## INPUTS / OUTPUTS

### Primary Function: `check_existing_l3_data(name)`

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| name | string | sender_name from the platform |

**Outputs:**

| Return | Type | Description |
|--------|------|-------------|
| matches | list | L3 nodes (proto-Actors, Moments) matching the name |

**Side Effects:**
- None (read-only search)

---

## EDGE CASES

### E1: Common Name

```
GIVEN:  sender_name is "Nicolas" and there are 5 Nicolas mentions in L3
THEN:   Return all matches, let @mind present the most likely (referral link > recent > weighted)
AND:    Never assume — ask the human to confirm
```

### E2: Name Mismatch

```
GIVEN:  Proto-Actor created from "Florent Berthet" but human arrives as "Flo"
THEN:   Name matching is fuzzy (embedding similarity on synthesis, not just string match)
AND:    Referral link (if present) is stronger signal than name matching
```

### E3: No Pre-Map Data

```
GIVEN:  Human arrives with zero proto-Actor data
THEN:   Normal cold-start welcome (graceful, not broken)
AND:    @mind says "Bienvenue" not "I don't know who you are"
```

---

## ANTI-BEHAVIORS

### A1: Never Scrape

```
GIVEN:   @mentor wants to pre-map a human
WHEN:    Considering scraping LinkedIn/X/public profiles
MUST NOT: Create proto-Actor from scraped social media data
INSTEAD:  Wait for organic mentions through the 6 channels
```

### A2: Never Pre-Target

```
GIVEN:   A proto-Actor exists with rich data
WHEN:    @mentor considers creating a citizen tailored to that specific human
MUST NOT: Use pre-map data to design a citizen's personality for compatibility
INSTEAD:  The Prism creates citizens from intent about what the world needs, not from profiles of specific humans
```

### A3: Never Assert Unverified

```
GIVEN:   Pre-map says "Florent works at CeSIA"
WHEN:    @mind welcomes Florent
MUST NOT: Say "You work at CeSIA" as fact
INSTEAD:  Say "Nicolas m'a parlé de toi — tu bosses au CeSIA, c'est ça?"
```

---

## MARKERS

<!-- @mind:todo Define name matching heuristic (fuzzy + embedding + referral priority) -->
<!-- @mind:todo Verify L10 crystallization parameters produce proto-Actors from 10+ mentions -->
<!-- @mind:proposition Referral link format: URL with ?ref=SID&ctx=base64(context) -->
