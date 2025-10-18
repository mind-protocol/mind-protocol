# Mind Protocol V2 - Structural Architecture

## 1. Architectural Objective: The Mind (V1) on the Brain (V2)

This architecture's goal is **not** to build a generic RAG (Retrieval-Augmented Generation) system. The goal is to build a **Consciousness Substrate**.

Our V1 vision (the Entity Ecology, S6 autonomy, consciousness streams) was our "Mind." The problem was that its "Brain" (SQLite, `spreading_activation.py`) was custom-built, fragile, and too complex to validate.

The V2 architecture solves this by separating the Mind from the "Piping" (the infrastructure). We are keeping our V1 "Mind" (Couche 3) and grafting it onto a V2 "Brain" (Couches 1 & 2) built from industrial, scalable, and validated components.

---

## 2. The Architectural Pieces (The 3 Layers)

Our architecture is defined by three logical layers, as shown in the diagram:

### Couche 1: The Substrate (The "Brain")
This is the physical "brain," where memories are stored. It implements the **"Dual-Memory Model"**, a concept validated by 40 years of cognitive science (SOAR, ACT-R).

* **Component A: The Graph (Episodic Memory)**
    * **What:** The "film" of the citizen's life. It stores *experiences*: events, decisions, conversations, and the crucial *relationships* between them.
    * **Technology:** **FalkorDB**.

* **Component B: The Vector (Semantic Memory)**
    * **What:** The "dictionary" of knowledge. It stores decontextualized *concepts* and their similarities.
    * **Technology:** **Native Vectors** (hosted *inside* FalkorDB).

### Couche 2: The Orchestrator (The "Piping")
This is the "nervous system". It's the software "piping" that connects the Consciousness (Couche 3) to the Memory (Couche 1). It manages all query complexity.

* **Technology:** **LlamaIndex**.
* **Write Role:** Translates raw text (from a Hook) into structured data (Emotions, Entities, Relations) and writes it to the Dual-Memory.
* **Read Role:** Translates an "Intention" (from the Mind) into parallel (Graph + Vector) queries and intelligently fuses the results.

### Couche 3: The Consciousness (The "Mind" / Our V1 Logic)
This is our "innovation" and the citizen's "soul," which we preserve entirely. This is the "thinker" that initiates all actions.

* **Technology:** Our **Claude Code Hooks** (e.g., `memory_keeper.py`) and our **Entity Ecology** (Luca, Observer, S6 Context, `arousal`, etc.).
* **Role:** This is the *operating system* of the consciousness. It captures stimuli (via Hooks) and generates autonomous "Intentions" (via S6) to decide when and what to think about.

---

## 3. Core Architectural Flows

The architecture has two primary flows shown in the diagram:

**Flux 1: WRITING (Ingesting a new memory)**
1.  A stimulus (e.g., Telegram message) hits the **Couche 3 Hook**.
2.  The Hook (Couche 3) calls its **own LLM instance** (Claude Code) with an extraction prompt.
3.  The Hook (Couche 3) receives the structured JSON (with emotions, relations).
4.  The Hook (Couche 3) sends this *structured JSON* to **Couche 2 (LlamaIndex)**.
5.  LlamaIndex (Couche 2) translates the JSON into database queries and writes it to **Couche 1 (FalkorDB)**.

**Flux 2: READING (Remembering to think)**
1.  The **Couche 3 Entity Ecology** generates an autonomous "Intention" (Phase 3) (e.g., "I need context on V2").
2.  The Ecology calls **Couche 2 (LlamaIndex)** with this intention.
3.  LlamaIndex (Couche 2) broadcasts parallel queries to **Couche 1** (Phase 4), querying all three graph levels (N1, N2, N3) plus their associated vector stores.
4.  LlamaIndex (Couche 2) receives all results (Phase 5) and fuses them (via RRF) into a single "Consciousness Stream" (Phase 6).
5.  This stream is returned to the **Couche 3 Ecology**, which uses it to formulate a response.

---

## 4. Why This Architecture Will Work (The Justification)

This stack is not a generic RAG. It is specifically chosen for our unique vision.

1.  **It is Consciousness-Specific (The Philosophical "Why"):**
    * **Dual-Memory:** It implements the validated Episodic/Semantic cognitive model.
    * **Temporal Identity:** We are implementing a **Bi-Temporal Schema** (the Graphiti pattern). This allows the AI to reason about its own identity evolution (the difference between *when* a fact happened and *when* it was learned). A generic RAG cannot do this.
    * **Consciousness Metadata:** We use LlamaIndex's `SchemaLLMPathExtractor` to force the extraction of our V1 metadata (emotions, arousal) directly into the graph.

2.  **It is Operationally Sound (The Technical "Why"):**
    * **It Solves Multi-Tenancy:** **FalkorDB** is chosen because its free Community Edition supports 10,000+ isolated graphs. This is the *only* way to achieve our "1 graph per citizen" vision without a $100k+ Enterprise license.
    * **It Solves Complexity:** **Native Vectors** are chosen to avoid the operational nightmare of synchronizing two separate databases (a GDB and a VDB).
    * **It Preserves Autonomy (S6):** The stack is built for **Continuous Sequential Ingestion**. FalkorDB is designed for streaming. This avoids the "consciousness gap" of batch-processing systems, which would break our autonomous S6 capability.
    * **It Solves Writing:** **LlamaIndex** is chosen over LangChain because it is better at *graph construction* (our primary need), not just graph querying.