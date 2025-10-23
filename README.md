# Mind Protocol V2

This repository contains the V2 infrastructure for Mind Protocol, built on the "Pragmatic Hybrid" architecture.

It is designed to run our V1 Consciousness Logic (`/consciousness`) on a powerful, scalable V2 "Brain" (`/substrate` + `/orchestration`).

## Core Architecture

The architecture consists of three layers:

1.  **Couche 1: Substrate (The Brain):** A Dual-Memory system using **FalkorDB** to store both the Episodic Graph (relationships) and the Semantic Memory (native vectors).
2.  **Couche 2: Orchestration (The Piping):** **LlamaIndex** is used as the "nervous system." It is configured with a **Custom LLM wrapper** that calls Couche 3.
3.  **Couche 3: Consciousness (The Mind):** Our preserved V1 logic. This is our **Claude Code instance**, which is the *only* part of the system that performs LLM processing.

---

## Architectural Flow: Shell Command Integration

This architecture is self-contained. All LLM operations are handled by our **Couche 3 (Claude Code) instance** via local shell commands.

* **Writing Flux (Red Arrow):**
    1.  A Hook (Couche 3) catches a message.
    2.  The Hook (Couche 3) executes its **own `claude -p "EXTRACT_JSON_PROMPT..."` shell command** (Couche 3) to get structured JSON.
    3.  The Hook (Couche 3) sends this *structured JSON* (not raw text) to LlamaIndex (Couche 2).
    4.  LlamaIndex (Couche 2) acts as a simple database driver and writes the JSON to FalkorDB (Couche 1).

* **Reading Flux (Blue Arrow):**
    1.  An Subentity (Couche 3) generates an "Intention" (e.g., "Need context on V2").
    2.  The Subentity (Couche 3) calls LlamaIndex (Couche 2).
    3.  LlamaIndex (Couche 2) is configured with a **`CustomClaudeCodeLLM` class**. When it needs to translate the Intention into a Cypher query, it doesn't call an API.
    4.  Instead, its `CustomClaudeCodeLLM` executes the shell command: `cd /path/to/citizen/ && claude -p "TRANSLATE_TO_CYPHER_PROMPT..."` (Couche 3).
    5.  LlamaIndex (Couche 2) gets the query back, queries FalkorDB (Couche 1), fuses the results, and returns clean context to the Subentity (Couche 3).

---

## Tech Stack

* **Database:** FalkorDB (running as a Redis module)
* **Orchestration:** LlamaIndex
* **Vector Storage:** Native FalkorDB Vectors
* **Temporal Model:** Custom Bi-Temporal Schema (inspired by Graphiti)
* **LLM Provider:** Internal Claude Code Instances (Couche 3) via `subprocess` calls
* **Runtime:** Python
* **Services:** Docker Compose

---

## Getting Started

### Prerequisites

* Docker and Docker Compose
* Python 3.10+
* A working local installation of the `claude` shell command.

### 1. Set Up Environment Variables

Create a `.env` file in the root directory.