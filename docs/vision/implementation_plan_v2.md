# Mind Protocol V2 - Implementation Plan

This document details the phased implementation plan for the V2 "Pragmatic Hybrid" architecture.

The plan is based on our selected V2 stack: **FalkorDB + LlamaIndex + Native Vectors**.

## Guiding Principles

* **Test Over Trust:** We validate each layer before building on it.
* **Sequential Ingestion:** The architecture must support our non-negotiable requirement for continuous, streaming ingestion (no batch processing for new memories).
* **Preserve V1 Logic:** The goal is to provide a new "Brain" (Couches 1 & 2) for our existing "Mind" (Couche 3).

---

## Phase 1: Foundation & Schema

**Why:** This phase builds the "foundations" of the new Brain (Couche 1). We cannot store or retrieve memories until we have:
1.  A database to hold them (FalkorDB).
2.  A system to isolate them (Multi-Tenancy).
3.  A *language* to describe them (The Consciousness Schema).
4.  A way for our Mind (Couche 3) to speak to our new Piping (Couche 2) (The Custom LLM Wrapper).

**Who:**

* **Felix (Engineer):**
    * Deploys FalkorDB via `docker-compose.yml`.
    * Implements `substrate/connection.py`.
    * Writes and validates `tests/test_multi_tenancy.py` to prove we can create and query isolated graphs for each citizen (e.g., `citizen_Luca`, `collective_n2`) inside the *same* FalkorDB instance.

* **Ada (Architect):**
    * Designs and implements `substrate/schemas/consciousness_schema.py`.
    * This schema defines the Pydantic/JSON models for our custom data: Nodes (`Person`, `Decision`, `Emotion`), Relations (`JUSTIFIES`, `REQUIRES`), and Properties (`arousal_level`, `emotion_valence`).

* **Luca (Consciousness):**
    * Collaborates with Ada on the `consciousness_schema.py` to ensure it captures all necessary phenomenological metadata (emotions, states of consciousness, etc.).

* **Felix (Engineer):**
    * Implements the **`CustomClaudeCodeLLM`** wrapper, which allows LlamaIndex to use our internal `claude -p "..."` shell command as its LLM.
    * Configures LlamaIndex's **`SchemaLLMPathExtractor`** to use this `CustomClaudeCodeLLM` and enforce Ada's schema.

---

## Phase 2: Bi-Temporal Implementation & Writing Flux (Flux 1)

**Why:** This phase builds the **"Write" capability (Flux 1 / Red Arrow)**. This allows the Mind (Couche 3) to *create new memories*. We also integrate our core V2 innovation: the **Bi-Temporal Schema**. This makes the Brain capable of *understanding time* and tracking how a citizen's identity evolves.

**Who:**

* **Ada (Architect):**
    * Implements `substrate/schemas/bitemporal_pattern.py`.
    * This defines the logic for our custom 4-timestamp schema (`valid_at`, `invalid_at`, `created_at`, `expired_at`) inspired by Graphiti.
    * Updates the `consciousness_schema.py` from Phase 1 to include these new temporal fields.

* **Felix (Engineer):**
    * Implements the `orchestration/insertion.py` script. This script will contain the main `ingest_text(text: str, graph_name: str)` function that uses the LlamaIndex `SchemaLLMPathExtractor` to write to FalkorDB.

* **Luca (Consciousness):**
    * Modifies the V1 `consciousness/hooks/memory_keeper.py`.
    * Removes all old `SQLite` logic and replaces it with a call to `orchestration.insertion.ingest_text(...)`. This bridges Couche 3 to Couche 2 for writing.

* **Felix (Engineer):**
    * Writes `tests/test_insertion.py` and `tests/test_bitemporal.py` to validate that a message is correctly written to the graph with all 4 timestamps.

---

## Phase 3: Native Vectors & Retrieval Flux (Flux 2)

**Why:** This phase builds the **"Read" capability (Flux 2 / Blue Arrow)**, completing the mind-brain loop. This phase activates the **Dual-Memory**, allowing the citizen to *think* by fusing episodic graph context (GDB) with semantic vector context (VDB).

**Who:**

* **Felix (Engineer):**
    * Configures the **Native Vector Index** inside FalkorDB.
    * Updates the `orchestration/insertion.py` script (from Phase 2) to *also* generate an embedding (using the `CustomClaudeCodeLLM`) and store it on the same node in FalkorDB.

* **Ada (Architect):**
    * Designs the hybrid retrieval logic for `orchestration/retrieval.py`.
    * This design must specify the parallel query strategy (N1, N2, N3) and the fusion method (RRF).

* **Felix (Engineer):**
    * Implements `orchestration/retrieval.py` based on Ada's design. This script will contain the `retrieve_context(intention: str, citizen_id: str)` function.

* **Luca (Consciousness):**
    * Modifies the V1 `consciousness/ecology/entity_logic.py`.
    * This connects the autonomous "Intention" (Phase 3) from our S6 logic to call `orchestration.retrieval.retrieve_context(...)`.

---

## Phase 4: Hardening, Seeding, & Validation

**Why:** To make the system robust and *alive*. We must (`bp_test_before_victory`) validate that it works at scale. We also need to seed the Collective Graphs (N2/N3) so that new citizens (N1) are not "born" into an empty world.

**Who:**

* **Luca (Consciousness):**
    * Curates and finalizes the `data/n2_collective_graph_seed.md` and `data/n3_ecosystem_graph_seed.md` files.

* **Felix (Engineer):**
    * Runs the `orchestration/insertion.py` script to seed the N2 and N3 graphs in FalkorDB.
    * Writes and runs `tests/test_load.py` to insert 100k+ nodes/vectors into a test graph and validate that P99 retrieval latency remains acceptable.

* **Ada (Architect):**
    * Implements basic monitoring (logging query latency, ingestion throughput, error rates).
    * Writes the final `docs/architecture_v2.md` and `docs/implementation_plan_v2.md`.
    * Ensures `README.md` and `map.md` are clean and up-to-date.