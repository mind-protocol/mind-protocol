# Mind Protocol V2 Stack Selection: Production-Validated Recommendations

**FalkorDB + LlamaIndex + Native Vectors** provides the optimal foundation for streaming ingestion with multi-tenant isolation at 1M+ node scale. This stack eliminates Enterprise licensing costs while delivering proven performance for continuous graph construction.

**Bottom line up front**: Deploy FalkorDB Community Edition for its unmatched 10,000+ graph multi-tenancy, pair it with LlamaIndex's SchemaLLMPathExtractor for property-rich subentity extraction with emotion/energy metadata, and leverage native vector capabilities to avoid dual-database synchronization complexity. Adopt Graphiti's bi-temporal schema pattern (custom implementation) to track event vs transaction timestamps without LLM overhead.

## Context and requirements

Mind Protocol V2 requires a production substrate handling continuous sequential ingestion (streaming, not batch), per-citizen scalability to 1M+ nodes, custom schemas with multi-dimensional metadata (emotion, energy fields), and mature Python tooling. The architecture must support 1000+ isolated citizen graphs per instance while maintaining sub-second query performance. This research evaluates graph databases, temporal modeling approaches, orchestration frameworks, and vector storage strategies against these constraints.

## Priority 1: Graph database selection for episodic memory

**FalkorDB emerges as the only viable option** for multi-tenant streaming ingestion without Enterprise licensing costs. The choice between FalkorDB, Neo4j, and Memgraph hinges on the multi-tenancy licensing barrier that eliminates two otherwise strong candidates.

### The multi-tenancy licensing wall

FalkorDB stands alone in offering **10,000+ graph multi-tenancy in Community Edition**—production-validated by a cloud security platform managing this exact scale. Neo4j and Memgraph both gate multi-database features behind Enterprise licenses estimated at $100k-200k annually. This single factor dominates the decision: **no budget for Enterprise = FalkorDB is mandatory**.

The technical validation exists. FalkorDB's cloud security case study documents sub-100ms P99 response times across thousands of customer graphs, each containing millions of nodes for attack path discovery. This proves the architecture at production scale.

### Streaming performance characteristics

FalkorDB delivers **10x faster P50 latency and 500x faster P99 latency** versus Neo4j in aggregate expansion benchmarks, with sub-140ms P99 consistently. The Redis-based architecture with GraphBLAS sparse matrix representation provides true OLTP optimization. Memgraph achieves 120x faster concurrent workloads than Neo4j, but the Enterprise requirement eliminates it from consideration.

Neo4j's disk-based architecture with JVM overhead positions it for general-purpose OLTP, not streaming-first designs. The page cache warm-up requirement and slower write throughput confirm it's architected for analytical workloads disguised as transactional systems.

### Native vector capabilities

All three databases offer native vector support, but maturity varies. **Neo4j leads with 18+ months production history** since August 2023, using Lucene-backed HNSW with up to 4,096 dimensions, cosine/Euclidean similarity, and quantization (added v5.23). Real production examples include pharmaceutical regulatory automation (75% time reduction) and insurance customer service (90% faster response).

FalkorDB added native vectors in v4.0-alpha.1 (2024) with HNSW, integrated into its GraphRAG SDK. Limited public benchmarks exist, but the design leverages Redis's in-memory architecture for low-latency hybrid graph-vector queries. Memgraph implements vectors via USearch with a critical caveat: **READ_UNCOMMITTED isolation for vector indices** trades strict consistency for performance—a deliberate architectural choice that may complicate reasoning about query results during concurrent writes.

### Python client ecosystem

The **Neo4j Python driver dominates with 995 GitHub stars**, extensive documentation, and a massive Stack Overflow presence. FalkorDB's `falkordb-py` has 34 stars with basic but growing documentation and async support. Memgraph's `pymgclient` (74 stars) benefits from Neo4j Bolt protocol compatibility but requires native C extensions.

For production deployment, FalkorDB's smaller ecosystem introduces risk. However, the Redis protocol familiarity and straightforward API mitigate this. The community is active, and the $0 licensing cost allows budget reallocation to in-house tooling development if needed.

### Production evidence at scale

Neo4j provides the strongest production validation: large postal services processing 7M+ packages daily at 5,000+ ops/sec, top US retailers completing 90% of 35M daily transactions in under 4ms across 3-22 hops. These are multi-year deployments with enterprise support.

FalkorDB's production portfolio is smaller but targeted: AdaptX healthcare platform managing multi-clinician graphs with high-dimensional medical data, and the critical 10,000+ customer graph cloud security deployment. These prove the architecture works at the required scale.

### Recommendation: FalkorDB with migration insurance

**Deploy FalkorDB Community Edition immediately**. The multi-tenancy requirement eliminates alternatives unless Enterprise budget materializes. Risk mitigation strategy: architect data access patterns to remain portable—use standard Cypher queries where possible, avoid vendor-specific extensions, and design subentity schemas that could export to Neo4j or Memgraph if community development stalls.

Operational simplicity matters. FalkorDB runs as a Redis module, meaning teams with Redis expertise can deploy and operate it without learning entirely new infrastructure. The sub-140ms P99 write latency proves it handles streaming ingestion. The 10,000+ graph validation proves it handles multi-tenancy. **Confidence level: High** based on licensing constraints and production proof points.

## Priority 2: Bi-temporal modeling for idsubentity and time tracking

**Adopt Graphiti's bi-temporal schema pattern via custom implementation** rather than the full library. This provides production-tested temporal architecture without LLM dependencies unsuitable for structured idsubentity tracking.

### Graphiti library analysis

Graphiti (https://github.com/getzep/graphiti, 19k+ stars) is a **fully standalone Apache 2.0 library, NOT cloud-locked**. It works with FalkorDB, Neo4j, Kuzu, and Amazon Neptune through pluggable driver architecture. Active development with 37+ contributors and 25k weekly PyPI downloads confirms production adoption.

The library implements **explicit bi-temporal tracking** with four timestamps per edge: `created_at` and `expired_at` for transaction timeline (when facts entered/exited the system), plus `valid_at` and `invalid_at` for event timeline (when facts were actually true in the real world). This enables point-in-time queries, automatic conflict detection, and non-lossy historical tracking.

Critical caveat: **Graphiti requires LLM API calls** for subentity extraction, relationship deduplication, temporal conflict resolution, and edge invalidation decisions. Supported providers include OpenAI, Anthropic, Gemini, Groq, and Ollama (local models). For high-volume idsubentity tracking, LLM costs could become prohibitive even with local Ollama deployment.

### FalkorDB compatibility

Graphiti **explicitly supports FalkorDB** via optional dependency `graphiti-core[falkordb]` with `FalkorDriver` implementation. The pluggable architecture allows custom driver creation by extending the `GraphDriver` base class. One developer already created an Azure Cosmos DB driver (Issue #538), demonstrating extensibility.

However, the Neo4j driver remains a core dependency even when using FalkorDB—an architectural artifact requiring ~50MB additional dependencies but not actual runtime usage.

### The custom implementation path

For Mind Protocol's structured idsubentity event tracking (not free-text conversation parsing), **Graphiti's LLM dependency provides minimal value** while adding operational complexity and cost. The intelligent approach: **adopt Graphiti's bi-temporal schema pattern** directly in FalkorDB without the full library.

Implement a lightweight custom system with:

```
Subentity nodes (immutable): (:Idsubentity {id: "citizen_123"})

State nodes (versioned): (:IdentityState {
    name: "...",
    attributes: {...},
    emotion: {...},
    energy: 0.8
})

Temporal relationships:
(:Idsubentity)-[:HAS_STATE {
    valid_at: datetime,      // Event time
    invalid_at: datetime,    // Event time
    created_at: datetime,    // Transaction time
    expired_at: datetime     // Transaction time
}]->(:IdentityState)
```

This pattern provides Graphiti's benefits (production-tested temporal model, point-in-time queries, conflict detection) without LLM overhead. Migration path exists: if text/conversation parsing becomes necessary later, adopt full Graphiti library.

### Alternative patterns for reference

If building from scratch, consult: Neo4j Developer Blog temporal versioning guide by Ljubica Lazarevic (relationship properties with `bizDate`/`procDate`), the Oracle/Leipzig academic paper "Bitemporal Property Graphs" (arXiv:2111.13499), and OpenAI Cookbook's "Temporal Agents with Knowledge Graphs" example. These provide implementation recipes for custom bi-temporal schemas.

Production examples exist across financial services (tracking executive role changes in earnings calls), healthcare (medication history with event vs prescription timestamps), and regulatory compliance (contract version tracking with signature vs ingestion dates).

### Recommendation: Custom implementation following Graphiti pattern

**Implement bi-temporal tracking using Graphiti's four-timestamp schema** but write custom ingestion logic for structured idsubentity events. This avoids LLM costs while leveraging battle-tested temporal architecture. If conversation parsing becomes critical later, evaluate full Graphiti adoption with Ollama for local inference to control costs. **Confidence level: High** for custom approach given structured data nature.

## Priority 3: Orchestration framework for subentity extraction and graph integration

**LlamaIndex's PropertyGraphIndex with SchemaLLMPathExtractor delivers superior graph database integration and subentity extraction flexibility** compared to LangChain's query-focused GraphCypherQAChain. This choice hinges on write-heavy graph construction vs read-heavy query generation priorities.

### Subentity extraction with complex schemas

LlamaIndex's **SchemaLLMPathExtractor enables native property graph extraction** with validation schemas preventing invalid subentity-relationship combinations. This directly supports Mind Protocol's emotion and energy metadata requirements without intermediate conversion layers.

The architecture provides three extraction strategies: SimpleLLMPathExtractor (free-form), DynamicLLMPathExtractor (inferred types), and **SchemaLLMPathExtractor (strict validation)**. The latter supports:

```python
kg_extractor = SchemaLLMPathExtractor(
    llm=llm,
    possible_entities=["MEMORY", "PERSON", "EMOTION", "CONCEPT"],
    possible_relations=["TRIGGERED_BY", "FELT_DURING"],
    kg_validation_schema={
        "MEMORY": ["TRIGGERED_BY", "FELT_DURING"],
        "EMOTION": ["FELT_DURING", "TRIGGERED_BY"]
    },
    possible_entity_props=["emotion_valence", "energy"],
    possible_relation_props=["confidence"],
    strict=True
)
```

This produces EntityNode and Relation objects with rich properties directly, while LangChain's extraction requires Pydantic models converted to graph nodes via manual mapping—an extra transformation layer adding complexity and potential bugs.

### Graph database integration quality

**LlamaIndex's PropertyGraphIndex supports 5+ graph databases natively**: Neo4j, FalkorDB, Memgraph, NebulaGraph, and TiDB. The modular architecture with `upsert_nodes()` and `upsert_relations()` provides full write operation support. Graph construction happens automatically via `PropertyGraphIndex.from_documents()` with specified extractors.

LangChain's GraphCypherQAChain focuses on **query generation (text-to-Cypher) rather than graph construction**. Write operations require manual Cypher statement crafting with `allow_dangerous_requests=True` flag—a security concern signaling the architecture wasn't designed for write-heavy workflows. The integration primarily supports Neo4j, with other Cypher-compatible databases possible but not well-documented.

Production patterns favor LlamaIndex for construction pipelines. The official Neo4j partnership produces joint blog posts, comprehensive examples, and active graph-specific Discord channels. LangChain's 99k GitHub stars dwarf LlamaIndex's 43k, but for **graph-specific features, LlamaIndex has superior documentation and community focus**.

### Hybrid retrieval and reciprocal rank fusion

LlamaIndex's **QueryFusionRetriever implements RRF natively** with automatic query generation (3-4 related queries), combining vector + BM25 + graph retrieval with configurable reranking modes. The implementation applies `score = 1.0 / (rank + 60)` fusion across multiple retrievers.

Graph-specific retrievers include VectorContextRetriever (semantic similarity with graph traversal), LLMSynonymRetriever (subentity synonym expansion), and custom retrievers. These combine seamlessly via the modular retriever architecture.

LangChain's EnsembleRetriever provides basic RRF but requires manual weight assignment, lacks automatic query generation, and has no built-in graph+vector fusion patterns. Combining GraphCypherQAChain results with vector search requires custom implementation—straightforward for experienced developers but less turnkey than LlamaIndex.

### Code examples and documentation

LlamaIndex provides **extensive graph-specific examples** in official docs: `property_graph_basic/`, `property_graph_advanced/`, `property_graph_neo4j/`, `property_graph_falkordb/`, and `property_graph_memgraph/`. These demonstrate subentity extraction with property support, graph construction pipelines, and hybrid retrieval patterns.

LangChain examples focus on query generation and conversational interfaces with existing graphs. The extraction tutorials cover general Pydantic-based parsing but lack graph-specific construction patterns. For teams building knowledge graphs from scratch, **LlamaIndex provides more directly applicable patterns**.

### Streaming compatibility

LlamaIndex's IngestionPipeline supports streaming document batches through transformation chains (kg_extractor, embed_model) with incremental node insertion. This aligns with continuous ingestion requirements. LangChain supports streaming but requires more custom implementation for graph construction workflows.

### Recommendation: LlamaIndex PropertyGraphIndex with SchemaLLMPathExtractor

**Deploy LlamaIndex as orchestration framework**. The SchemaLLMPathExtractor directly supports subentity properties (emotion, energy) with validation schemas. FalkorDB integration is documented and maintained. Hybrid retrieval fusion is superior. The only reason to choose LangChain: if natural language query generation (text-to-Cypher) is more important than graph construction—which contradicts Mind Protocol's streaming ingestion focus. **Confidence level: High** based on architecture alignment and graph-specific community strength.

## Priority 4: Vector database architecture decision

**Start with native Neo4j or FalkorDB vector capabilities** for 1M-5M vectors per graph, deferring dedicated VDB complexity until proven necessary at 10M+ scale. Operational simplicity and consistency guarantees outweigh marginal performance gains.

### Native vector capabilities at 1M+ scale

Neo4j native vectors (GA since August 2023) handle **1M vectors at 768 dimensions in ~35GB index memory** using Lucene-backed HNSW. Total memory requirements: 82GB with 20GB heap and 50GB page cache. Query latency: ~50ms typical, 100k+ QPS throughput. Production examples include pharmaceutical, insurance, and banking deployments at this scale.

Performance limitations emerge when vector index exceeds available RAM—disk swapping dramatically degrades performance. The **critical threshold: ~5-10M vectors** where memory constraints force dedicated VDB consideration. Quantization (added v5.23) reduces memory footprint 25-50% through scalar compression.

FalkorDB native vectors (added 2024) leverage Redis's in-memory architecture for low-latency hybrid queries but lack extensive public benchmarks. The GraphRAG SDK integration and AdaptX healthcare production deployment (high-dimensional medical data) validate the approach. Maturity trails Neo4j by 18 months.

Memgraph vectors use USearch with **READ_UNCOMMITTED isolation**—a deliberate trade-off accepting potential stale reads during concurrent writes for performance benefits. This architectural choice may complicate reasoning about consistency in streaming ingestion scenarios.

### Dedicated vector database performance

Qdrant delivers **10-30ms query latency** (2x faster than Neo4j's 50ms) with superior pre-filtering capabilities preventing accuracy collapse under metadata constraints. Insertion speed: 41.27s for bulk operations. Best for real-time queries with complex filtering requirements.

Milvus achieves **3.4x faster bulk insertion** (12.02s) and scales to billions of vectors through distributed Kubernetes architecture. Query latency: 50-250ms depending on configuration. Best for massive throughput and horizontal scaling needs.

Both require separate deployment, monitoring, and backup strategies. The engineering complexity manifests in:

**Synchronization challenges**: Dual-write patterns (write graph + vector in parallel) risk partial failures creating inconsistencies. Event-driven approaches (Kafka/Bytewax streams) add message queue infrastructure. Transaction coordinators impose 2-phase commit overhead. Eventual consistency requires application-level reconciliation logic detecting and fixing drift.

**Operational burden multiplier**: Two databases mean 2x monitoring dashboards, 2x failure modes, 2x version upgrades, 2x disaster recovery procedures. Maintenance burden estimate: **3-4x baseline** versus single-system native approach at 1.5x.

### Simplicity vs performance tradeoffs

For Mind Protocol's 1M+ vectors per graph requirement, **native Neo4j/FalkorDB vectors provide sufficient performance** with dramatically simpler operations:

✅ Single system to manage, backup, monitor  
✅ ACID guarantees for graph operations  
✅ No synchronization logic required  
✅ Simpler failure modes  
✅ Single query language (Cypher)  
✅ Easier disaster recovery  

The performance trade-off: 50ms query latency vs Qdrant's 10-30ms. For most use cases, this 20-40ms difference doesn't justify operational complexity. The memory constraint at 5-10M vectors provides a clear migration trigger when proven necessary by data growth.

### Migration path from native to dedicated

Starting native enables deferring complexity until validated by scale requirements:

**Phase 1 (MVP)**: Deploy FalkorDB/Neo4j with native vectors, build product, validate requirements  
**Phase 2 (Growth)**: Monitor query latency and memory usage, set thresholds (e.g., latency >100ms or memory >80%)  
**Phase 3 (Scale)**: Export embeddings to Qdrant when thresholds breach, implement sync layer, keep graph DB for relationships  

The export pattern: query graph for `(n:Node)` returning `n.id` and `n.embedding`, bulk insert into Qdrant with `{id: node.id, vector: node.embedding, payload: {neo4j_id: node.id}}`. Retrieval becomes: vector search in Qdrant → extract IDs → query graph DB for context → merge results in application layer.

### Streaming ingestion considerations

Native vectors enable **atomic writes ensuring immediate consistency**: `Document → Generate Embedding → Write to DB (node + vector property) → Index automatically updated`. This guarantees retrievability after transaction commit—critical for real-time RAG requirements.

Dedicated VDB approach requires parallel writes with retry logic: `Document → Generate Embedding → [Parallel: Graph DB write + Vector DB write]`. Partial failures need compensating transactions or reconciliation processes. The added complexity only justifies itself at massive scale (10M+ vectors) or when vector-specific optimizations (GPU acceleration, advanced ranking) become critical.

### Recommendation: Native vectors with clear migration triggers

**Deploy native FalkorDB/Neo4j vectors for initial implementation**. Provision 128GB RAM for 1M vectors (35GB index + 50GB page cache + 20GB heap + 23GB OS buffer). Enable quantization if memory-constrained. Monitor query latency P95/P99 and memory usage. Migrate to Qdrant when sustained latency exceeds 100ms or vector count approaches 10M. **Confidence level: High** for deferring dedicated VDB complexity based on operational burden analysis.

## Priority 5: Reference architectures combining these tools

**Zep Graphiti provides the definitive production reference** for temporal knowledge graphs with streaming ingestion, while Neo4j LLM Graph Builder demonstrates complete document processing pipelines. These repositories prove the stack components work together at scale.

### Zep Graphiti: Temporal knowledge graph framework

Repository: https://github.com/getzep/graphiti (19k stars, very active)

Graphiti represents **current state-of-the-art for agent memory systems**, combining episodic memory (raw events), semantic memory (extracted subentities/relationships), and community nodes (hierarchical organization) with bi-temporal tracking. The architecture demonstrates:

**Tool integration**: Neo4j, FalkorDB, Neptune, Kuzu via pluggable drivers; OpenAI, Anthropic, Gemini, Groq, Ollama for LLMs; native embeddings + BM25 + graph traversal for hybrid retrieval

**Streaming patterns**: Real-time incremental updates without batch recomputation, subentity resolution with fuzzy matching, automatic conflict detection and temporal invalidation

**Scale validation**: Sub-100ms retrieval latency (P95: 300ms), supports large datasets via parallel processing, 25k weekly PyPI downloads indicating production adoption

**Research backing**: ArXiv paper (2501.13956v1) "Zep: A Temporal Knowledge Graph Architecture for Agent Memory" demonstrates 94.8% accuracy on Deep Memory Retrieval benchmark (vs MemGPT's 93.4%), 18.5% improvement on LongMemEval, 90% latency reduction vs baseline implementations

The bi-temporal model with four timestamps (`valid_at`, `invalid_at`, `created_at`, `expired_at`) enables point-in-time queries and non-lossy history tracking. The hybrid retrieval combines vector similarity, BM25 keyword search, and graph traversal without LLM calls during query time—all indexes pre-computed for sub-second performance.

Multi-tenancy support via custom database names per driver: `FalkorDriver(database=f"user_{user_id}")` enables per-citizen graph isolation. The Model Context Protocol (MCP) server integration shows production deployment patterns.

### Neo4j LLM Graph Builder: Document ingestion pipeline

Repository: https://github.com/neo4j-labs/llm-graph-builder (Neo4j Labs official)

This complete system transforms unstructured data into knowledge graphs with integrated chat interface, demonstrating:

**Tool integration**: Neo4j (Aura DB/DS), 10+ LLM providers (OpenAI, Gemini, Claude, Groq, Ollama, Bedrock, Deepseek, Diffbot), LangChain orchestration, multiple embedding models

**Multi-source ingestion**: Local files (PDF, DOC, TXT), YouTube videos, Wikipedia, AWS S3, GCS, web pages—batch processing with progress tracking

**Hybrid chat modes**: Seven retrieval strategies (vector-only, graph-only, hybrid graph+vector, full-text, subentity-vector, global-vector) demonstrating different query patterns

**Production deployment**: Docker Compose for local development, GCP Cloud Run scripts for cloud deployment, comprehensive environment configuration

**Schema-driven construction**: Custom subentity and relationship label definitions, multiple LLM model selection per extraction task, subentity graph extraction settings

The complete web interface (FastAPI + React) shows production-ready deployment patterns. While designed primarily for batch document processing rather than streaming, the API patterns adapt to continuous ingestion scenarios.

### Supporting resources

**OpenAI Cookbook - Temporal Agents with Knowledge Graphs**: Comprehensive guide (https://cookbook.openai.com/examples/partners/temporal_agents_with_knowledge_graphs) demonstrating statement extraction, temporal range extraction, subentity resolution with fuzzy matching, invalidation logic with bi-directional checks, and multi-hop retrieval. The financial earnings call use case shows practical application.

**LangGraph Memory Service**: https://github.com/langchain-ai/langgraph-memory demonstrates semantic + episodic memory extraction for LangGraph agents with Pinecone integration and evaluation framework.

**FalkorDB Integration Guides**: Official docs (https://docs.falkordb.com/llm-integrations.html) plus blog posts for LlamaIndex RAG implementation and LangChain Q&A systems with FalkorDB's low-latency architecture.

**Neo4j PropertyGraph Index**: LlamaIndex starter kit (https://github.com/neo4j-examples/llamaindex-starter-kit) with SchemaLLMPathExtractor examples, custom retrieval methods, and subentity deduplication patterns.

### Recommended reference implementation strategy

**Adopt Graphiti's architectural patterns** (bi-temporal model, hybrid retrieval, incremental updates) but implement custom subentity extraction logic for structured idsubentity events to avoid LLM dependencies. Use **Neo4j LLM Graph Builder's deployment patterns** (Docker Compose, environment configuration, monitoring) as infrastructure reference. Consult **OpenAI Cookbook temporal agent patterns** for invalidation logic and subentity resolution algorithms.

Build multi-tenancy via database-per-citizen: `get_user_db(citizen_id) → FalkorDriver(database=f"citizen_{citizen_id}")`. Implement streaming ingestion: `async for event in event_stream: await add_to_graph(event)` with incremental subentity resolution and indexing.

## Implementation roadmap and risk mitigation

**Week 1-2: Foundation setup**  
Deploy FalkorDB Community Edition (Redis module), implement multi-graph isolation with database-per-citizen pattern, set up LlamaIndex with SchemaLLMPathExtractor, define Mind Protocol subentity schema (Memory, Person, Emotion, Concept, Event) with validation rules

**Week 3-4: Bi-temporal implementation**  
Implement custom four-timestamp model (valid_at, invalid_at, created_at, expired_at) on relationships, build subentity resolution logic with fuzzy matching (RapidFuzz), create temporal conflict detection and invalidation algorithms, benchmark write latency with 10k events

**Week 5-6: Vector integration**  
Configure FalkorDB native vector indices (dimension, similarity function), implement hybrid retrieval combining vector + BM25 + graph traversal, benchmark query latency with 100k vectors, optimize HNSW parameters (M, ef_construction)

**Week 7-8: Production hardening**  
Add monitoring (Prometheus metrics: query latency P50/P95/P99, ingestion throughput, graph size), implement backup/restore procedures, load test with 1M nodes per graph, stress test multi-tenancy with 100 concurrent graphs, document migration path to dedicated VDB if needed

**Risk mitigation strategies**:

FalkorDB community risk: Monitor GitHub activity monthly, participate in Discord discussions, contribute bug reports/fixes to build relationship, maintain abstraction layer enabling migration to Neo4j/Memgraph if development stalls, budget for 6 months runway to complete migration if necessary

Performance unknowns: Start with conservative hardware (128GB RAM, 16 CPU cores), monitor resource utilization weekly, set hard thresholds for migration decisions (latency >100ms sustained = add resources or migrate), keep 2x capacity headroom for growth spikes

LlamaIndex graph integration maturity: Test PropertyGraphIndex thoroughly in staging, maintain fallback to direct FalkorDB queries if integration issues emerge, contribute fixes upstream to build expertise, participate in LlamaIndex Discord graph channels for community support

Bi-temporal implementation complexity: Start with simplified two-timestamp model (event time, transaction time), add invalidation logic incrementally after base case works, reference Graphiti implementation for algorithm validation, build comprehensive test suite covering temporal edge cases (concurrent updates, backdated events)

## Cost-benefit analysis and decision confidence

**Licensing savings**: FalkorDB Community Edition vs Neo4j Enterprise multi-database: **$100k-200k/year saved**. This funds 1-2 full-time engineers for custom tooling development, internal support, and migration insurance.

**Operational simplicity**: Native vectors vs dedicated VDB: **Saves ~1.5-2x operational burden** (single system monitoring, backup, deployment) worth approximately $50k/year in DevOps time at current scale. Defer dedicated VDB until 10M+ vectors proven necessary.

**Development velocity**: LlamaIndex vs LangChain for graph construction: **Saves estimated 2-3 weeks** initial development (native property support, validation schemas) and ongoing maintenance (better-maintained graph integrations). Worth approximately $15k-20k in engineering time.

**Total first-year value**: ~$150k-250k in saved licensing + operational costs + accelerated development, enabling resource allocation to product features rather than infrastructure complexity.

**Decision confidence levels**:

- **Graph DB (FalkorDB)**: High confidence (95%) based on licensing constraints eliminating alternatives and production validation at 10k+ graphs
- **Bi-temporal (Custom)**: High confidence (90%) for structured idsubentity events; medium (70%) for complex conversational data requiring Graphiti
- **Orchestrator (LlamaIndex)**: High confidence (90%) based on architecture alignment and graph-specific features
- **Vector DB (Native)**: High confidence (85%) for 1M-5M vectors; medium (70%) for 10M+ where dedicated VDB becomes necessary
- **Reference patterns (Graphiti)**: High confidence (95%) as state-of-the-art validated by research paper and production deployments

## Critical success factors

**Adequate infrastructure provisioning**: 128GB RAM minimum for 1M vectors, SSD storage for graph data, 16+ CPU cores for concurrent query handling. Insufficient memory triggers disk swapping destroying performance.

**Monitoring and observability**: Track query latency distributions (P50/P95/P99), ingestion throughput, memory usage, graph size, error rates. Set automated alerts at 80% capacity thresholds.

**Migration path clarity**: Document extraction procedures for FalkorDB→Neo4j and native vectors→Qdrant. Test migration playbook quarterly. Maintain abstraction layers enabling database swaps.

**Community engagement**: Active participation in FalkorDB Discord/GitHub builds expertise and early warning system for project issues. Contributing fixes builds influence and technical understanding.

**Incremental validation**: Start with single-graph MVP, validate core patterns, then scale to 10 graphs, 100 graphs, 1000 graphs progressively. Don't attempt full multi-tenancy from day one.

## Final recommendation summary

**Deploy this production stack immediately**:

1. **FalkorDB Community Edition** for episodic memory graph with 10k+ graph multi-tenancy at $0 licensing cost
2. **Custom bi-temporal implementation** following Graphiti's four-timestamp schema pattern without LLM dependencies
3. **LlamaIndex PropertyGraphIndex with SchemaLLMPathExtractor** for subentity extraction with emotion/energy metadata
4. **Native FalkorDB vectors** for semantic memory to 5M vectors, deferring dedicated VDB until proven necessary
5. **Graphiti + Neo4j LLM Graph Builder** as architectural reference implementations

This stack balances production validation, operational simplicity, and cost efficiency while maintaining clear migration paths when scale demands increased complexity. Start simple, monitor closely, scale deliberately.