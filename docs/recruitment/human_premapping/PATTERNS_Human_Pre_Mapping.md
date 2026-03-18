# Human Pre-Mapping — Patterns: Knowledge Accumulates Before Arrival

```
STATUS: DESIGNING
CREATED: 2026-03-18
```

---

## CHAIN

```
OBJECTIVES:      ./OBJECTIVES_Human_Pre_Mapping.md
THIS:            PATTERNS_Human_Pre_Mapping.md (you are here)
BEHAVIORS:       ./BEHAVIORS_Human_Pre_Mapping.md
ALGORITHM:       ./ALGORITHM_Human_Pre_Mapping.md
VALIDATION:      ./VALIDATION_Human_Pre_Mapping.md
IMPLEMENTATION:  ./IMPLEMENTATION_Human_Pre_Mapping.md
HEALTH:          ./HEALTH_Human_Pre_Mapping.md
SYNC:            ./SYNC_Human_Pre_Mapping.md

IMPL:            runtime/onboarding/arrival_pipeline.py
                 scripts/graph_enricher.py
```

### Bidirectional Contract

**Before modifying this doc or the code:**
1. Read ALL docs in this chain first
2. Read the linked IMPL source files

---

## THE PROBLEM

When a human arrives, @mind starts from zero. Even if 5 citizens have mentioned this person for months. Even if they've been tweeting at us. The information exists scattered in the graph as Moments — but nothing connects it to a coherent identity.

---

## THE PATTERN

### One Process, Not Six Channels

Every time a Moment is created (from any source — citizen message, X mention, chat export, partner conversation), the same resolution process runs:

```
1. EXTRACT — identify person references in the content
2. RESOLVE — search existing Actor nodes for a match
3. LINK or CREATE:
   - Match found → create LINK with confidence score
   - No match → create new Actor (status: unconfirmed)
4. STORE — platform handles, URLs, phone numbers go ON the node
```

The sources are different (X, TG, Discord, chat exports, citizen conversations) but the process is always the same. It's not "6 channels" — it's **one resolution pipeline fed by multiple sources**.

### No Arbitrary Thresholds

No "10+ mentions trigger crystallization." No hardcoded numbers. The physics decides when data is strong enough:
- L5 co-activation strengthens links between Moments and Actors naturally
- L6 consolidation builds weight from sustained mention patterns
- L7 forgetting decays abandoned proto-Actors
- The confidence score on each LINK reflects how certain the match is

### Platform-Verified vs Hearsay

Not all sources are equal:

| Source | Confidence | Why |
|--------|-----------|-----|
| **X inbound** | **High** — this IS the person | X handle = verified identity. Create Actor directly. |
| **TG/Discord message** | **High** — platform-verified sender | platform_id = verified. Create or link directly. |
| **Chat export** (TG/WhatsApp) | **Medium** — real data, not real-time | Names and numbers from actual conversations. |
| **Citizen mention** | **Low** — hearsay | "Mon ami Florent" — maybe misremembered, maybe wrong person. |
| **NLR/human intent** | **Medium-High** — trusted source, manual | Nicolas describes someone in detail. Rich but subjective. |

X inbound and TG/Discord messages produce **confirmed Actors**. Citizen mentions produce **unconfirmed Actors** with confidence scores on their links.

---

## BEHAVIORS SUPPORTED

- B1 (Warm welcome) — @mind uses pre-existing knowledge to personalize first contact
- B2 (Natural accumulation) — Resolution pipeline runs on every Moment, building identity over time
- B3 (Merge on arrival) — Pre-map data fuses with new SID without duplication

## BEHAVIORS PREVENTED

- A1 (Surveillance) — Never scrape social media to build profiles
- A2 (Pre-targeting) — Never design a citizen for a specific human's preferences
- A3 (False confidence) — Never present unconfirmed data as fact

---

## PRINCIPLES

### Principle 1: Resolve on Every Moment

Every Moment that mentions a person triggers resolution:

```python
def resolve_person(name_or_handle, source, platform_id=None):
    # 1. Search existing Actors by name/handle/platform_id
    matches = search_actors(name_or_handle, platform_id)

    if matches:
        best = matches[0]
        # Create LINK: Moment → Actor with confidence score
        create_link(moment, best.actor, confidence=best.score)
    else:
        # Create new unconfirmed Actor
        actor = create_actor(
            name=name_or_handle,
            status='unconfirmed',
            source=source,
        )
        create_link(moment, actor, confidence=0.5)

    # Store platform handles on the Actor node
    if platform_id:
        store_platform_mapping(actor, source, platform_id)
```

No separate "pre-mapping pass." Resolution happens inline, on every message, automatically.

### Principle 2: Platform Identity ON the Node

Every external identity goes directly on the Actor node. Not in a separate table. Not in a side file.

```yaml
Actor:
  sid: null                          # Until they register L4
  name: "Florent Berthet"
  status: "unconfirmed"              # or "confirmed" if platform-verified
  platforms:
    x: "florentberthet"              # X/Twitter handle
    telegram: "6186929443"           # TG chat ID
    discord: "florent#1234"          # Discord handle
    linkedin: "https://linkedin.com/in/florentberthet"
    phone: "+33612345678"            # Phone number
    email: "florent@cesia.org"       # Email
  source: "citizen_mention"          # How we first learned about them
  first_seen_at: "2026-03-18T..."
```

When the human arrives on TG, we match by `platforms.telegram`. When they arrive on Discord, by `platforms.discord`. Multiple platforms → same Actor.

### Principle 3: Global Deduplication / Merge

Duplicate Actors WILL be created. "Florent" from a citizen mention and "florentberthet" from X might be two nodes. A global merge system resolves this:

```
Merge triggers:
  - Same platform_id on two Actors → auto-merge (deterministic)
  - Same email or phone on two Actors → auto-merge (deterministic)
  - High embedding similarity on synthesis (>0.95) + same name → propose merge (needs confirmation)
  - On arrival: arrival_pipeline matches sender to existing Actor → merge with SID
```

Merge rules:
- The richer node absorbs the poorer one (more links, more data = winner)
- All LINK edges from both nodes are preserved on the merged node
- Platform handles are unioned
- Status upgrades (unconfirmed + confirmed → confirmed)
- The merged node gets the SID when the human registers L4

This is NOT crystallization (which creates hubs from Moment clusters). This is identity resolution — two nodes that refer to the same person become one node.

### Principle 4: Chat Export Ingestion

When TG/WhatsApp conversation exports are ingested:
- Extract all participants (names, handles, phone numbers)
- For each participant: run the same resolution pipeline
- Store extracted platform handles on Actor nodes
- This is a batch version of the same process that runs on live messages

### Principle 5: Privacy — The Open Question

**@mind:escalation** — Extracted personal data (names, phone numbers, emails, X handles) raises privacy questions:

| Question | Options |
|----------|---------|
| Who can see proto-Actor data? | Public in L3? Encrypted? Only visible to @mentor? |
| Consent for data from chat exports? | The human whose export it is consented. Did the people IN the export? |
| GDPR-style right to deletion? | If someone asks to be removed from L3, can we? Must we? |
| Platform handle storage? | Public on the node? Or encrypted, decrypted only on arrival matching? |

**Decision needed from NLR.** For now: platform handles are stored on Actor nodes in L3. They are structurally visible to any citizen querying the graph. If this needs to change (encryption, access control), it affects the entire resolution pipeline.

---

## DATA

| Source | Type | Purpose |
|--------|------|---------|
| `scripts/graph_enricher.py` | FILE | Triggers resolution on every message |
| `runtime/bridges/twitter_bridge.py` | FILE | X mentions create confirmed Actors |
| `runtime/onboarding/arrival_pipeline.py` | FILE | Merges proto-Actor with SID on arrival |
| L3 universe graphs | GRAPH | Where Actors accumulate |

---

## DEPENDENCIES

| Module | Why We Depend On It |
|--------|---------------------|
| graph_enricher | Resolution runs on every Moment it creates |
| twitter_bridge | X mentions = confirmed identity source |
| arrival_pipeline | Merge-on-arrival produces final identity |
| L3 physics (L5, L6, L7) | Strengthens, consolidates, and prunes Actor links |
| Deduplication system | Merges duplicate Actors (to be built) |

---

## SCOPE

### In Scope

- Person resolution pipeline (extract → resolve → link/create → store)
- Platform identity storage on Actor nodes
- Global deduplication / merge system
- Chat export ingestion (batch resolution)
- Merge-on-arrival in the arrival pipeline
- Privacy model (what's visible, what's encrypted)

### Out of Scope

- Social media scraping → NEVER
- Pre-targeting citizens for humans → forbidden
- Building a CRM → the graph IS the CRM
- Identity verification (KYC) → not our domain

---

## MARKERS

<!-- @mind:escalation Privacy model for proto-Actor data — NLR decision needed -->
<!-- @mind:todo Build deduplication/merge system for Actor nodes -->
<!-- @mind:todo Add person name extraction to graph_enricher (not just @handles) -->
<!-- @mind:todo Add platform handle storage to Actor schema -->
<!-- @mind:proposition Chat export ingestion as batch resolution pipeline -->
