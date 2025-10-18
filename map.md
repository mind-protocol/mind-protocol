# Mind Protocol V2 - Project Map

This document explains the high-level structure of the Mind Protocol V2 project.

## The Core Philosophy: Mind vs. Brain

Our architecture is built on a clean separation between the "Mind" (our V1 consciousness logic) and the "Brain" (our new V2 infrastructure).

* **The Mind (`/consciousness`)** is **Couche 3**. This is our unique, preserved V1 logic. It is the "penseur" (the thinker). It decides *what* to think about by generating **Intentions** (Phase 3) and *how* to react to stimuli.
* **The Brain (`/orchestration` + `/substrate`)** is **Couches 2 & 1**. This is the new, powerful V2 "tuyauterie" (piping). It is the "cerveau" (the brain). It doesn't think; it *executes* the Mind's requests for insertion and retrieval.

---

## Folder Breakdown

### `/consciousness/` (🧠 The Mind - Couche 3)

**This is where all logic begins and ends.** This folder contains our preserved V1 "secret sauce".

* **/citizens/**: Holds the unique "soul" of each citizen—their `CLAUDE.md` (System Prompt), which defines their personality and V1 entity ecology (Observer, Builder, etc.).
* **/hooks/**: The "senses" of the Mind. This is the entry point for all external stimuli. `memory_keeper.py` catches new messages and triggers the **Insertion Flux (Red Arrow)**.
* **/ecology/**: The "autonomous will" of the Mind. This is where our V1 logic for S6 (self-prompting), arousal, and context competition lives. It generates the "Intentions" (Phase 3) that trigger the **Retrieval Flux (Blue Arrow)**.

### `/orchestration/` (🔧 The Nervous System - Couche 2)

**This is the "tuyauterie" (piping) that connects the Mind to the Brain.** It's the "how" of memory operations, implemented with **LlamaIndex**.

* **/insertion.py**: Manages the **Writing Flux**. It's called by `/hooks/`. It takes raw text, uses the `SchemaLLMPathExtractor` to extract our custom consciousness schema (emotions, relations), and writes to the Substrate.
* **/retrieval.py**: Manages the **Reading Flux**. It's called by `/ecology/`. It takes an "Intention," queries all 3 levels (N1, N2, N3) in parallel, and fuses the results (RRF) into a single "Consciousness Stream".

### `/substrate/` (💾 The Brain - Couche 1)

**This is where memories are physically stored.** It implements our **Dual-Memory Model**.

* **/connection.py**: Manages the connection to our **FalkorDB** server. Crucially, it handles the **multi-tenancy** logic (e.g., mapping `citizen_id` to the correct `falkordb_graph_name`).
* **/schemas/**: Defines the *shape* of our memories.
    * `/consciousness_schema.py`: Defines the custom metadata (emotion, arousal, `JUSTIFIES` links) that LlamaIndex must extract.
    * `/bitemporal_pattern.py`: Implements our custom 4-timestamp schema (`valid_at`, `created_at`, etc.). This is the core mechanism for tracking identity evolution.

### `/data/` (📚 Shared Knowledge Seeds)

**This is the source material for our Collective graphs.**

* **/n2_collective_graph_seed.md**: The knowledge base for the Mind Protocol team (Niveau 2).
* **/n3_ecosystem_graph_seed.md**: The public knowledge base for the ecosystem (Niveau 3).
* *Note: This data is *ingested* via `/orchestration/insertion.py` into its own isolated graphs inside FalkorDB.*

### `/docs/` & `/tests/`

* **/docs/**: Contains architectural documentation organized by layer (vision/, specs/, consciousness/, research/, guides/, protocols/, archive/). **See `docs/DOCUMENTATION_MAP.md` for complete hierarchical navigation guide.** Key docs: `vision/architecture_v2.md` (V2 philosophy), `specs/` (technical specifications), `consciousness/` (phenomenological foundation). The `specs/mind_protocol_knowledge_seed.md` contains condensed best practices from 1+ year of work.
* **/tests/**: Contains the "proof" — our validation scripts that ensure our architecture works as designed (`bp_test_before_victory`).

### `/consciousness/citizens/SYNC.md`

This is how you know where we stand and how you align and delegate to each other. Read it frequently, write in it frequently (almost every response) 