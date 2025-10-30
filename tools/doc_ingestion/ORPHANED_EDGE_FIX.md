# Orphaned Edge Recovery System

**Date:** 2025-10-29
**Engineer:** Atlas (Infrastructure)
**Issue:** Edges dropped when LLM proposes node types not in filtered schema

---

## Problem

The LLM was proposing edges that referenced node types like "Concept", "Human", etc. that aren't in the n2/shared filtered schema. These edges were being silently dropped during validation with errors like:

```
[LLMClusterCreator] Invalid ref type: <class 'NoneType'>
[LLMClusterCreator] Out of range ref: _SYNC_17_10_25.md_1.Concept[0] (max: -1)
[LLMClusterCreator] Edge 4 has invalid source ref: None - DROPPING
```

**Root Cause:** Schema filtering to n2/shared node types (Principle, Best_Practice, Mechanism, Behavior, Process, Metric) means LLM proposals for other node types fail `_resolve_candidate_ref()` validation.

**Impact:** Important relationships lost because LLM tried to create nodes with invalid types.

---

## Solution

Implemented **orphaned edge tracking and recovery system** that:
1. **Captures** orphaned edges instead of dropping them
2. **Tracks** them across chunks
3. **Prompts** LLM in next chunk to either create missing nodes with valid types OR replace with valid existing nodes

---

## Implementation

### 1. Edge Validation (map_and_link.py:1423-1455)

Modified `validate_output()` to track orphaned edges:

```python
resolved_edges = []
orphaned_edges = []

for i, edge in enumerate(llm_response.get('edges', [])):
    source_id = self._resolve_candidate_ref(source_ref, existing_nodes)
    target_id = self._resolve_candidate_ref(target_ref, existing_nodes)

    if not source_id or not target_id:
        # Store orphaned edge for recovery in next chunk
        orphaned_edge = edge.copy()
        orphaned_edge['_failed_reason'] = []
        if not source_id:
            orphaned_edge['_failed_reason'].append(f"invalid_source_ref: {source_ref}")
        if not target_id:
            orphaned_edge['_failed_reason'].append(f"invalid_target_ref: {target_ref}")
        orphaned_edges.append(orphaned_edge)
        logger.warning(f"[LLMClusterCreator] Edge {i} orphaned: {', '.join(orphaned_edge['_failed_reason'])}")
        continue

    # ... resolve and append to resolved_edges
```

**Result:** Orphaned edges captured with failure reasons instead of silently dropped.

### 2. Response Tracking (map_and_link.py:1491-1497)

Store orphaned edges in validation response:

```python
# Store orphaned edges for recovery in next chunk
if orphaned_edges:
    logger.warning(f"[LLMClusterCreator] ORPHANED EDGES detected: {len(orphaned_edges)} edges failed validation")
    logger.warning("[LLMClusterCreator] Will pass orphaned edges to next chunk for node creation or replacement")
    llm_response['_orphaned_edges'] = orphaned_edges
else:
    llm_response['_orphaned_edges'] = []
```

**Result:** `_orphaned_edges` available alongside `_orphans` for chunk-by-chunk handling.

### 3. Chunk-by-Chunk Tracking (map_and_link.py:1626, 1709-1713)

Track cumulative orphaned edges across chunks:

```python
cumulative_orphaned_edges = []  # Track orphaned edges to pass to next chunk

# After each chunk validation:
chunk_orphaned_edges = validated_chunk.get('_orphaned_edges', [])
if chunk_orphaned_edges:
    logger.info(f"[process_chunks] Chunk {i+1} produced {len(chunk_orphaned_edges)} orphaned edges - will prompt for node creation in next chunk")
    cumulative_orphaned_edges.extend(chunk_orphaned_edges)
```

**Result:** Orphaned edges accumulate and pass to next chunk.

### 4. Continuation Parameter (map_and_link.py:1688-1694)

Pass orphaned edges to continuation:

```python
chunk_response = creator.call_llm_continue(
    claude_dir=claude_dir,
    chunk=chunk,
    existing_nodes=existing_nodes_for_chunk,
    schemas=schemas,
    orphans_from_prior=cumulative_orphans,
    orphaned_edges_from_prior=cumulative_orphaned_edges  # NEW
)
```

**Result:** Orphaned edges available to continuation prompt.

### 5. LLM Prompt Section (map_and_link.py:1020-1036, 1055)

Added section to DELTA_PROMPT explaining orphaned edges:

```python
# Build orphaned edges section
orphaned_edges_section = ""
if chunk_input.get('ORPHANED_EDGES_FROM_PRIOR'):
    orphaned_edges_json = json.dumps(chunk_input.get('ORPHANED_EDGES_FROM_PRIOR', []), indent=2)
    orphaned_edges_section = f"""
# ORPHANED EDGES FROM PRIOR CHUNKS

These edges from previous chunks failed validation because they referenced node types not in the filtered schema (n2/shared for nodes, l2/shared for links).

{orphaned_edges_json}

**IMPORTANT:** For each orphaned edge, you have two options:
1. **Create the missing nodes**: If the referenced concept is important, propose new nodes using ONLY the allowed node types (Principle, Best_Practice, Mechanism, Behavior, Process, Metric from n2/shared schema)
2. **Replace with valid types**: If the edge can be reformulated using existing candidates or new proposals with valid types, create the correct edge

DO NOT ignore these orphaned edges - they represent important relationships that need to be preserved.
"""
```

Inserted into continuation prompt:

```python
# ORPHANS FROM PRIOR CHUNKS (if any)

{orphans_section}
{orphaned_edges_section}  # NEW

# EXTRACTION TARGETS FOR THIS CHUNK
```

**Result:** LLM receives explicit instructions to recover orphaned edges.

---

## Example Flow

### Chunk 1:
- LLM proposes edge: `{type: "DOCUMENTS", source: {chunk_id: "doc_0", node_type: "Concept", index: 0}, target: ...}`
- **Validation:** `_resolve_candidate_ref()` fails because "Concept" not in n2/shared schema
- **Action:** Edge stored in `_orphaned_edges` with reason `"invalid_source_ref: {node_type: Concept}"`

### Chunk 2:
- **Prompt includes:**
  ```json
  {
    "type": "DOCUMENTS",
    "source": {"node_type": "Concept", ...},
    "_failed_reason": ["invalid_source_ref: {node_type: Concept}"]
  }
  ```
- **Instructions:** "Create the missing nodes using ONLY allowed types OR replace with valid existing nodes"
- **LLM options:**
  1. Create new `Principle` or `Best_Practice` node capturing the Concept
  2. Link to existing candidate instead
  3. Create different edge with valid types

---

## Files Modified

### `/home/mind-protocol/mindprotocol/tools/doc_ingestion/map_and_link.py`

**Changes:**
- **Lines 1423-1455:** Orphaned edge capture in `validate_output()`
- **Lines 1491-1497:** Store orphaned edges in response
- **Lines 1626:** Track `cumulative_orphaned_edges` across chunks
- **Lines 1686-1694:** Pass orphaned edges to `call_llm_continue()`
- **Lines 1709-1713:** Accumulate orphaned edges from each chunk
- **Lines 940-941:** Add `orphaned_edges_from_prior` parameter to `call_llm_continue()`
- **Lines 1009-1036:** Build orphaned edges section for prompt
- **Lines 1055:** Insert orphaned edges section into DELTA_PROMPT

**Total additions:** ~50 lines
**Approach:** Non-breaking - adds new functionality without changing existing behavior

---

## Verification

### Expected Logging

**When orphaned edges detected:**
```
[LLMClusterCreator] Edge 4 orphaned: invalid_source_ref: {node_type: Concept}
[LLMClusterCreator] ORPHANED EDGES detected: 7 edges failed validation
[LLMClusterCreator] Will pass orphaned edges to next chunk for node creation or replacement
[process_chunks] Chunk 1 produced 7 orphaned edges - will prompt for node creation in next chunk
```

**When passed to next chunk:**
```
[process_chunks] CHUNK 2 - continuing session...
[process_chunks] Passing 7 orphaned edges from prior chunks for recovery
[LLMClusterCreator] Including 7 orphaned edges from prior chunks for recovery
```

**When LLM recovers edges:**
- Chunk 2 returns new node proposals with valid types
- New edges link to newly created valid nodes
- Orphaned edge count decreases in subsequent chunks

---

## Testing Strategy

1. **Single document test:**
   ```bash
   cd /home/mind-protocol/mindprotocol/tools/doc_ingestion
   python3 process_corpus.py full_manifest.json --max-files 1
   ```
   - Monitor logs for "ORPHANED EDGES detected"
   - Verify orphaned edges passed to chunk 2
   - Verify chunk 2 creates nodes or replaces with valid types

2. **Log analysis:**
   ```bash
   grep "orphaned" corpus_processing.log
   grep "ORPHANED EDGES" corpus_processing.log
   ```

3. **Prompt inspection:**
   ```bash
   cat /tmp/last_llm_continue_*.txt | grep -A 20 "ORPHANED EDGES FROM PRIOR CHUNKS"
   ```

---

## Success Criteria

✅ **No silent edge drops:** All edge validation failures logged as orphaned
✅ **Cross-chunk tracking:** Orphaned edges accumulate and pass to next chunk
✅ **LLM guidance:** Prompt explicitly instructs LLM to recover orphaned edges
✅ **Two recovery paths:** LLM can create nodes OR replace with valid types
✅ **Non-breaking:** Existing functionality unchanged, only adds recovery

---

## Known Limitations

1. **Recovery not guaranteed:** LLM may not successfully recover all orphaned edges
2. **Semantic loss:** Creating valid-type nodes may not perfectly capture original intent (e.g., "Concept" → "Principle" loses some semantics)
3. **Accumulation:** If LLM consistently fails to recover, orphaned edges accumulate across all chunks
4. **No final cleanup:** Orphaned edges remaining after last chunk are not explicitly handled (future: create QA tasks?)

---

## Future Enhancements

1. **Final cleanup pass:** After all chunks, create QA tasks for unrecovered orphaned edges
2. **Schema expansion:** Consider allowing more node types (n1? l4?) if orphaned edges become common
3. **LLM feedback:** Track which recovery strategy LLM uses most successfully
4. **Metrics:** Count orphaned edges by type to identify patterns

---

**End of Orphaned Edge Fix Documentation**

*Timestamp: 2025-10-29 09:06 UTC*
*Engineer: Atlas*
*Status: ✅ Implementation Complete - Ready for Testing*
