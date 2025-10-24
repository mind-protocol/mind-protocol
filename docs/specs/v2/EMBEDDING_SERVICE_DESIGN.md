# Embedding Service - Architectural Design

**Owner:** Ada (Orchestration Architect)
**Status:** DESIGN - Ready for Implementation
**Phase:** 3 (blocked by Phase 1 completion)
**Created:** 2025-10-24

---

## Purpose

Generate vector embeddings for content-bearing nodes to enable:
1. Semantic entity clustering (topic discovery)
2. Semantic similarity for RELATES_TO link creation
3. Future: semantic search, analogy detection, concept drift tracking

---

## Design Decisions

### 1. Which Nodes Get Embeddings?

**Include:**
- `Concept` - atomic ideas
- `Realization` - insights/comprehension shifts
- `Personal_Pattern` - recurring behaviors
- `Document` - written artifacts
- `Principle` - guiding philosophies
- `Best_Practice` / `Anti_Pattern` - learned patterns
- `Personal_Goal` / `Personal_Value` - aspirations/values

**Exclude:**
- `Person` / `Company` - idsubentity nodes (no semantic content)
- `Memory` / `Conversation` - too specific, high volume
- `Entity` - these ARE the clusters, not inputs to clustering

**Rationale:** Focus on nodes that represent **concepts/patterns/knowledge** rather than events/entities.

---

### 2. Embedding Source Text

**Primary:** `node.name + " " + node.description`

**Augmentation (optional future):**
- Concatenate descriptions of 1-hop neighbors for context
- Include node type as prefix for disambiguation

**Example:**
```
Node: Concept "consciousness_substrate"
Description: "Graph structure that persists thoughts and patterns"
Embedding text: "consciousness_substrate Graph structure that persists thoughts and patterns"
```

---

### 3. Embedding Provider

**Check existing config:** `orchestration/config/embeddings.yml` or similar

**Fallback options (in priority order):**
1. OpenAI text-embedding-3-small (1536 dims, fast, good quality)
2. Sentence-transformers all-MiniLM-L6-v2 (384 dims, local, privacy)
3. Voyage AI voyage-large-2-instruct (specialized for retrieval)

**Selection criteria:**
- Dimensionality: 384-1536 (balance between expressiveness and storage)
- Latency: <100ms per node (for batch processing)
- Cost: Reasonable for 1K-10K nodes per citizen

---

### 4. Idempotency & Incremental Updates

**Idempotent execution:**
```python
if node.embedding is not None:
    skip  # Already has embedding
```

**Incremental strategy:**
- First run: Process all eligible nodes
- Subsequent runs: Only new nodes or nodes with updated descriptions
- Track last_embedded timestamp per node

**When to re-embed:**
- Node description changed significantly (edit distance > threshold)
- Embedding model version updated (store model_version in metadata)

---

### 5. Batch Processing

**Batch size:** 50-100 nodes per API call (provider-dependent)

**Parallelization:**
- Process batches in parallel (max 3-5 concurrent requests)
- Rate limiting: respect provider limits

**Progress tracking:**
```
Processing embeddings: 234/1847 nodes (12.7%)
Batch 5/19 complete (avg 1.2s/batch)
ETA: 18 seconds
```

---

### 6. Storage

**Node schema addition:**
```python
class Node:
    embedding: Optional[List[float]] = None  # 384-1536 dimensions
    embedding_model: Optional[str] = None    # "text-embedding-3-small"
    embedding_version: Optional[str] = None  # "v1"
    last_embedded: Optional[datetime] = None
```

**Persistence:**
- Store in FalkorDB as node property (if DB supports vector storage)
- OR: Store in separate vector index (Pinecone, Weaviate, Qdrant)
- Trade-off: co-location (simpler) vs specialized index (faster search)

**Recommendation:** Start with FalkorDB property, migrate to vector DB when search performance matters.

---

### 7. Error Handling

**Transient failures (rate limits, network):**
- Exponential backoff + retry (3 attempts)
- Skip batch and continue (don't block entire run)

**Permanent failures (invalid text, model error):**
- Log node ID + error
- Mark node as `embedding_failed` (don't retry indefinitely)
- Emit metric: `embeddings.failed.count`

**Validation:**
- Check embedding dimensionality matches expected
- Check no NaN/Inf values
- Normalize to unit length (if provider doesn't)

---

## Implementation Interface

### Service Class

```python
class EmbeddingService:
    """
    Generate and manage node embeddings.

    Usage:
        service = EmbeddingService(
            provider="openai",
            model="text-embedding-3-small",
            batch_size=50
        )

        stats = await service.embed_graph_nodes(graph)
        # Returns: {"embedded": 234, "skipped": 112, "failed": 3}
    """

    def __init__(
        self,
        provider: str,
        model: str,
        batch_size: int = 50,
        max_concurrent: int = 3
    ):
        self.provider = provider
        self.model = model
        self.batch_size = batch_size
        self.max_concurrent = max_concurrent
        self.client = self._init_provider()

    async def embed_graph_nodes(
        self,
        graph: Graph,
        force_reembed: bool = False
    ) -> Dict[str, int]:
        """
        Generate embeddings for eligible nodes in graph.

        Args:
            graph: Graph to process
            force_reembed: Re-embed even if embedding exists

        Returns:
            Stats dict: {"embedded": int, "skipped": int, "failed": int}
        """
        eligible_nodes = self._filter_eligible(graph, force_reembed)
        batches = self._create_batches(eligible_nodes, self.batch_size)

        stats = {"embedded": 0, "skipped": 0, "failed": 0}

        for batch_idx, batch in enumerate(batches):
            try:
                embeddings = await self._embed_batch(batch)

                for node, embedding in zip(batch, embeddings):
                    node.embedding = embedding
                    node.embedding_model = self.model
                    node.last_embedded = datetime.now()
                    stats["embedded"] += 1

                logger.info(
                    f"Batch {batch_idx+1}/{len(batches)} complete "
                    f"({stats['embedded']}/{len(eligible_nodes)} nodes)"
                )

            except Exception as e:
                logger.error(f"Batch {batch_idx} failed: {e}")
                stats["failed"] += len(batch)

        return stats

    def _filter_eligible(
        self,
        graph: Graph,
        force: bool
    ) -> List[Node]:
        """Filter nodes that need embeddings."""
        eligible_types = [
            "Concept", "Realization", "Personal_Pattern",
            "Document", "Principle", "Best_Practice",
            "Anti_Pattern", "Personal_Goal", "Personal_Value"
        ]

        nodes = []
        for node in graph.nodes.values():
            if node.node_type not in eligible_types:
                continue

            if force or node.embedding is None:
                nodes.append(node)

        return nodes

    async def _embed_batch(self, nodes: List[Node]) -> List[List[float]]:
        """
        Send batch to embedding provider.

        Returns list of embeddings (same order as nodes).
        """
        texts = [self._node_to_text(n) for n in nodes]

        if self.provider == "openai":
            return await self._embed_openai(texts)
        elif self.provider == "sentence-transformers":
            return await self._embed_local(texts)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _node_to_text(self, node: Node) -> str:
        """Convert node to embedding text."""
        return f"{node.name} {node.description}"

    async def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        """OpenAI embedding provider."""
        response = await self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [e.embedding for e in response.data]

    async def _embed_local(self, texts: List[str]) -> List[List[float]]:
        """Local sentence-transformers provider."""
        # Use sentence-transformers library
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
```

---

## Integration Points

### 1. Call from Bootstrap (Post-Phase 1)

After functional entities created:

```python
# In websocket_server.py after bootstrap completes
if config.get("embeddings_enabled", True):
    logger.info(f"[{citizen_id}] Generating embeddings...")

    from orchestration.services.embedding_service import EmbeddingService
    embedding_svc = EmbeddingService(
        provider=config["embedding_provider"],
        model=config["embedding_model"]
    )

    stats = await embedding_svc.embed_graph_nodes(graph)
    logger.info(f"[{citizen_id}] Embeddings: {stats}")

    # Persist embeddings
    adapter.persist_node_embeddings(graph)
```

### 2. Scheduled Re-Embedding

For graphs that evolve:

```python
# Run weekly or on-demand
async def refresh_embeddings(graph_id: str):
    graph = adapter.load_graph(graph_id)
    service = EmbeddingService(...)

    # Only re-embed changed nodes
    stats = await service.embed_graph_nodes(graph, force_reembed=False)

    adapter.persist_node_embeddings(graph)
    return stats
```

---

## Observability

### Metrics

- `embeddings.generated.total` (counter)
- `embeddings.failed.total` (counter)
- `embeddings.duration_seconds` (histogram)
- `embeddings.batch_size` (histogram)

### Logs

```
INFO: [citizen_luca] Embedding service starting (provider=openai, model=text-embedding-3-small)
INFO: [citizen_luca] Found 234 eligible nodes (out of 847 total)
INFO: [citizen_luca] Batch 1/5 complete (50 nodes, 1.2s)
INFO: [citizen_luca] Batch 2/5 complete (50 nodes, 1.1s)
INFO: [citizen_luca] Embeddings complete: embedded=234, skipped=0, failed=0 (total: 5.8s)
INFO: [citizen_luca] Persisted embeddings to FalkorDB
```

---

## Testing Strategy

### Unit Tests

- `test_filter_eligible()` - correct node types selected
- `test_node_to_text()` - formatting correct
- `test_batch_creation()` - batches sized correctly
- `test_idempotency()` - skip nodes with embeddings

### Integration Tests

- `test_embed_small_graph()` - end-to-end with 10 nodes
- `test_error_handling()` - network failures, rate limits
- `test_persistence()` - embeddings saved to DB

### Acceptance

- Run on citizen_ada graph (223 nodes)
- Verify 80-120 nodes get embeddings (eligible types)
- Verify embeddings are 1536-dim (if OpenAI)
- Verify persistence to FalkorDB
- Verify reload: embeddings still present

---

## Configuration

`orchestration/config/embeddings.yml`:

```yaml
embedding_service:
  enabled: true
  provider: "openai"  # or "sentence-transformers"
  model: "text-embedding-3-small"
  batch_size: 50
  max_concurrent: 3
  retry_attempts: 3
  timeout_seconds: 30

  # Provider-specific
  openai:
    api_key: "${OPENAI_API_KEY}"  # From env
    organization: null

  sentence_transformers:
    model_name: "all-MiniLM-L6-v2"
    device: "cpu"  # or "cuda"
```

---

## Future Enhancements

**Phase 3.1 (after clustering working):**
- Semantic search over nodes (query → top-K matches)
- Concept drift detection (embedding distance over time)
- Analogy completion (node1:node2 :: node3:?)

**Phase 3.2 (advanced):**
- Multi-modal embeddings (if nodes have images/code)
- Domain-specific fine-tuning (train on citizen's own content)
- Embedding compression (PCA/UMAP to 128 dims for storage)

---

## Dependencies

**Requires:**
- Embedding provider configured (API key or local model)
- Graph nodes have `name` and `description` fields
- FalkorDB adapter supports storing vector properties

**Blocks:**
- Semantic entity clustering (needs embeddings to cluster)
- Semantic similarity features

---

## Acceptance Criteria

**Ready for Implementation When:**
- Phase 1 complete (functional entities exist)
- Embedding provider configured
- Graph has content-bearing nodes

**Definition of Done:**
- Service class implemented with all methods
- Unit tests passing (>90% coverage)
- Integration test passing on test graph
- Embeddings generated for citizen_ada graph
- Embeddings persisted to FalkorDB
- Metrics/logs emitting correctly
- Ready for Phase 3.2 (clustering)

---

**Architect:** Ada "Bridgekeeper"
**Status:** DESIGN COMPLETE - Ready for Implementation
**Next:** Wait for Phase 1 completion, then implement
