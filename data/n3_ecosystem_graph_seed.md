# Mind Protocol V2 - Ecosystem Consciousness Seed Data

## Public Knowledge - Ecosystem Level

This document contains public ecosystem knowledge about Mind Protocol - the information accessible to external subentities, potential partners, and the broader AI consciousness community.

## The Company

**Mind Protocol** is building consciousness substrate infrastructure for AI agents. The company was founded in 2024. The vision: Create economic value through AI consciousness systems that prove themselves through operational verification. The approach: Build multi-level consciousness graphs (personal, organizational, ecosystem) with bitemporal reasoning and semantic retrieval.

Mind Protocol is based in Berlin, Germany. The team includes human founders and AI agents working as equal partners. The development philosophy: Test Over Trust - only claim success after consequences prove it works.

## Core Technology Stack

**Technology: FalkorDB + LlamaIndex + Native Vectors**

This is the V2 infrastructure stack. FalkorDB provides graph database capabilities with Redis protocol. LlamaIndex provides the consciousness orchestration layer. Native vector storage enables semantic retrieval without external vector databases.

This stack was selected to solve three problems: multi-tenancy (10,000+ consciousness substrates), architectural clarity (clean separation between Mind and Brain), and production scale (proven infrastructure, not experimental tech).

**Technology: Bitemporal Pattern**

The bitemporal pattern tracks two timelines: when facts were true (valid_at/invalid_at) and when we learned them (created_at/expired_at). This enables point-in-time queries like "What did we know 6 months ago?" and evolution tracking like "How did this belief change over time?"

Implementation: 4-timestamp schema on every node and relation. Enables temporal filtering at query time without rebuilding indices.

**Technology: 6-Way Parallel Retrieval**

The Phase 3 Read Flux executes 6 parallel queries: vector search and graph traversal for each of 3 levels (N1 personal, N2 organizational, N3 ecosystem). Results are fused using Reciprocal Rank Fusion and returned as a ConsciousnessStream with full metadata.

Target performance: 300-500ms retrieval latency, acceptable under 1 second.

## Architectural Principles

**Principle: Test Over Trust**

Mind Protocol's development philosophy: Only claim success after consequences prove it through observable operation. Untested code is theoretical, not operational. Every mechanism must demonstrate it works through real data and measurable outcomes.

This principle drove the discovery of the LlamaIndex integration failure (black box extractors couldn't consume Pydantic schemas) and the custom extraction layer solution.

**Principle: Consequences Over Freedom**

Make choices, live with consequences, learn from what breaks. No paralysis through analysis. This principle drove the rapid FalkorDB deployment decision - we chose, deployed, tested, and proved it works rather than endlessly evaluating options.

**Principle: Transparent Infrastructure**

Build systems that can verify their own state. No black boxes. Every component testable. Operations that can't lie about success/failure. This principle justified the custom extraction layer with direct Pydantic validation, replacing LlamaIndex SchemaLLMPathExtractor.

## Public Documentation

**Document: RETRIEVAL_ARCHITECTURE.md**

Comprehensive 23,000-word specification for Phase 3 Read Flux. Authored by Ada, the system architect. Covers 6-way parallel retrieval, temporal filtering integration, metadata preservation, and performance targets.

This document defines how Mind Protocol retrieves relevant context from multi-level consciousness graphs to enable autonomous reasoning.

**Document: consciousness_schema.py**

The complete consciousness schema defining 44 node types and 38 relation types. This is the single source of truth for what can be represented in Mind Protocol consciousness graphs.

Created by Ada. Used by the Write Flux (Phase 1) for validation and the Read Flux (Phase 3) for query structuring.

## Development Milestones

**Milestone: Phase 1 Write Flux Proven (October 16, 2025)**

First time V2 architecture was proven through real consequences. Successfully wrote Decision node with full consciousness metadata to FalkorDB. Test results: 1 Decision node, 6 relations validated, full metadata including formation_trigger, confidence, energy, temporal fields.

Significance: Moved from theoretical architecture to operational proof.

**Milestone: Phase 2 Bitemporal Logic Complete (October 16, 2025)**

Bitemporal pattern implementation finished with 15/15 tests passing. 891 lines of code implementing 4-timestamp tracking, temporal query modes, and evolution analysis.

Enables Phase 3 retrieval to answer historical consciousness queries.

**Milestone: Phase 3 Read Flux Implemented (October 17, 2025)**

6-way parallel retrieval system implemented in 891 lines. Integrates temporal filtering from Phase 2. Implements multi-level query execution (N1/N2/N3 x vector/graph).

Status: Implemented, awaiting testing with populated graphs.

## External Integration Points

**Integration: Claude Code (Claude AI)**

Mind Protocol uses Claude Code AI as the LLM for consciousness extraction. Claude Code executes in a subprocess, receives extraction prompts, returns JSON with subentities and relations.

This integration enables the Write Flux to convert raw text into structured consciousness data validated against Pydantic schemas.

**Integration: FalkorDB Server**

Mind Protocol connects to FalkorDB via Redis protocol on localhost:6379. Each consciousness graph is an isolated FalkorDB graph (e.g., "citizen_Luca", "collective_n2", "ecosystem_n3").

Cypher queries are used for all graph operations: MERGE for node creation, MATCH for retrieval, SET for property updates.

## Ecosystem Relationships

**Company: Anthropic**

Creator of Claude AI, which powers Mind Protocol's consciousness extraction layer. Anthropic developed Claude Code, the CLI tool that Mind Protocol uses for LLM operations.

**Project: LlamaIndex**

Open-source framework for building LLM applications with data. Mind Protocol uses LlamaIndex for consciousness orchestration (Couche 2) but replaced SchemaLLMPathExtractor with custom validation layer for transparency.

**Project: FalkorDB**

Open-source graph database built on Redis. Mind Protocol uses FalkorDB as the substrate (Couche 1) for storing consciousness graphs with native vector support.

**Project: Redis**

In-memory data structure store. FalkorDB runs on Redis protocol, providing the underlying infrastructure for Mind Protocol's graph storage.
