# Auto-Resolve Missing Endpoint (ARM)

## The Problem

When the LLM creates edges, it sometimes references node IDs that don't exist in the graph. This can happen when:
- LLM invents a new ID based on context
- ID has a typo or formatting difference
- Node was supposed to be created but wasn't
- Node exists but with a different ID

**Before ARM:** Edge creation failed silently, relationship lost.

**With ARM:** Automatically search for similar nodes and surface candidates for review.

## How It Works

### 1. Detection (graph.py)
```python
ensure_edge() validates both endpoints exist
→ If missing: returns {"confirmed": False, "error": "...node does not exist"}
```

### 2. Resolution (process_corpus.py)
```python
When edge creation fails due to missing node:
→ Call auto_resolve_missing_endpoint()
→ Get top 5 candidates
→ Log candidates to console
→ Create QA task for human review
```

### 3. Search Algorithm (arm.py)

**Parse & Normalize:**
```
"mechanism:comprehensive_health_check_algorithm"
→ label_guess = "Mechanism"
→ slug = "comprehensive_health_check_algorithm"
→ query_text = "comprehensive health check algorithm"
```

**Vector Search:**
- Embed query_text
- Search label_guess first (e.g., Mechanism)
- Then search all common labels (Principle, Best_Practice, etc.)
- Get top K=10 per label

**String Similarity:**
- Token set ratio vs name
- Token set ratio vs aliases
- Max score = best match

**Combined Score:**
```
score_combined = 0.7 * score_vector + 0.3 * score_string
```

**Top 5 ranked by combined score**

## Example Output

```
⚠️  Missing node: mechanism:systematic_health_verification
    Edge: principle:reliability_through_monitoring →[IMPLEMENTS]→ mechanism:systematic_health_verification
    ARM found 3 candidates:
      1. mechanism:comprehensive_health_check (score=0.892)
      2. mechanism:health_monitor (score=0.785)
      3. mechanism:system_verification (score=0.731)
```

## Integration Points

### graph.py
- `ensure_edge()` validates node existence
- Returns error with clear message

### process_corpus.py
- Detects "does not exist" errors
- Calls ARM on missing endpoints
- Logs candidates
- Creates QA task

### arm.py
- Standalone module
- No graph modifications
- Pure search + ranking

## Usage

ARM runs automatically during corpus processing. No configuration needed.

**Candidates logged to:**
- Console (stdout)
- corpus_processing.log (arm_candidates_found events)
- QA tasks database (for human review)

## Future Enhancements

1. **Auto-correction:** If top candidate has score > 0.95, auto-replace ID
2. **Learning:** Track which corrections humans make, improve ranking
3. **Batch resolution:** Resolve multiple missing nodes in one pass
4. **Context awareness:** Use other_id to inform ranking (graph proximity)

## Testing

```bash
# Process document with likely missing node references
python3 process_corpus.py test_manifest.json

# Check for ARM events
grep "arm_candidates_found" corpus_processing.log
```

## Dependencies

- `rapidfuzz` - String similarity
- `sentence-transformers` - Vector embeddings
- FalkorDB vector search indices
