"""
P0 Diagnostic: Stimulus Injection Failure (sim_mass=0.00)

Diagnoses why stimulus injection shows zero similarity mass.
Tests encoder health, node embedding presence, and similarity kernel.

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-24
Context: Emergency diagnostic for production stimulus starvation
"""

import redis
import numpy as np
from orchestration.adapters.search.embedding_service import get_embedding_service

def diagnose_stimulus_injection(citizen_id: str = "felix"):
    """
    Run P0 diagnostics on stimulus injection system.

    Tests:
    1. Encoder health (can it generate embeddings?)
    2. Node embedding presence (do nodes have content_embedding?)
    3. PING test (can we match identical text?)
    4. Similarity kernel (is cosine working?)

    Args:
        citizen_id: Citizen to diagnose (default: felix)
    """

    print("=" * 60)
    print("P0 DIAGNOSTIC: Stimulus Injection Failure")
    print("=" * 60)

    # Use hierarchical graph name (citizen_id should be full hierarchical name)
    graph_name = citizen_id
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    # Test 1: Encoder Health
    print("\n[TEST 1] Encoder Health Check")
    print("-" * 60)

    try:
        embedding_service = get_embedding_service()
        test_text = "PING_TOKEN_123"
        test_embedding = embedding_service.embed(test_text)

        print(f"✅ Encoder UP: Generated embedding")
        print(f"   Dimension: {len(test_embedding)}")
        print(f"   Norm: {np.linalg.norm(test_embedding):.4f}")
        print(f"   First 5 values: {test_embedding[:5]}")

        # Test encoder consistency (same text should give same embedding)
        test_embedding_2 = embedding_service.embed(test_text)
        cos_self = np.dot(test_embedding, test_embedding_2) / (
            np.linalg.norm(test_embedding) * np.linalg.norm(test_embedding_2)
        )
        print(f"   Self-similarity: {cos_self:.4f} (should be ≈1.0)")

        if cos_self < 0.95:
            print("   ⚠️  WARNING: Encoder not deterministic (cos < 0.95)")

        encoder_ok = True
        embedding_dim = len(test_embedding)

    except Exception as e:
        print(f"❌ Encoder FAILED: {e}")
        encoder_ok = False
        embedding_dim = None
        return  # Can't proceed without encoder

    # Test 2: Node Embedding Presence
    print("\n[TEST 2] Node Embedding Presence")
    print("-" * 60)

    try:
        # Count total nodes
        query_total = "MATCH (n) RETURN count(n) AS total"
        result = r.execute_command('GRAPH.QUERY', graph_name, query_total)
        total_nodes = int(result[1][0][0]) if result and result[1] else 0
        print(f"Total nodes: {total_nodes}")

        # Count nodes WITH content_embedding
        query_with_emb = "MATCH (n) WHERE exists(n.content_embedding) RETURN count(n) AS with_embedding"
        result = r.execute_command('GRAPH.QUERY', graph_name, query_with_emb)
        nodes_with_embedding = int(result[1][0][0]) if result and result[1] else 0
        print(f"Nodes with content_embedding: {nodes_with_embedding}")

        if nodes_with_embedding == 0:
            print("❌ ROOT CAUSE: No nodes have content_embedding property!")
            print("   → Fix: Run embedding backfill script to populate node.content_embedding")
        elif nodes_with_embedding < total_nodes * 0.9:
            print(f"⚠️  WARNING: Only {(nodes_with_embedding/total_nodes*100):.1f}% of nodes have embeddings")
        else:
            print("✅ Embeddings present on most nodes")

        # Sample a node with embedding
        if nodes_with_embedding > 0:
            query_sample = """
            MATCH (n)
            WHERE exists(n.content_embedding)
            RETURN n.name, n.content_embedding
            LIMIT 1
            """
            result = r.execute_command('GRAPH.QUERY', graph_name, query_sample)
            if result and result[1]:
                node_name = result[1][0][0]
                node_embedding_raw = result[1][0][1]
                print(f"\nSample node: {node_name}")
                print(f"   Embedding type: {type(node_embedding_raw)}")
                print(f"   Embedding length: {len(node_embedding_raw) if isinstance(node_embedding_raw, (list, str)) else 'unknown'}")

                # Try to parse embedding
                if isinstance(node_embedding_raw, str):
                    import json
                    try:
                        parsed = json.loads(node_embedding_raw)
                        if isinstance(parsed, list):
                            print(f"   Parsed dimension: {len(parsed)}")
                            print(f"   Parsed norm: {np.linalg.norm(parsed):.4f}")
                    except json.JSONDecodeError:
                        print("   ⚠️  Cannot parse embedding as JSON")

    except Exception as e:
        print(f"❌ Query failed: {e}")
        return

    # Test 3: Vector Index Presence
    print("\n[TEST 3] Vector Index Check")
    print("-" * 60)

    try:
        # Check if vector index exists
        # FalkorDB doesn't have a direct "SHOW INDEXES" command,
        # so we test by attempting a vector query

        test_vector_str = str(test_embedding.tolist())
        for node_type in ['Realization', 'Principle', 'Mechanism', 'Concept']:
            try:
                query = f"""
                CALL db.idx.vector.queryNodes('{node_type}', 'content_embedding', 5, vecf32({test_vector_str}))
                YIELD node, score
                RETURN count(*) AS match_count
                """
                result = r.execute_command('GRAPH.QUERY', graph_name, query)
                match_count = int(result[1][0][0]) if result and result[1] else 0

                if match_count > 0:
                    print(f"✅ {node_type}: Vector index working ({match_count} matches)")
                else:
                    print(f"⚠️  {node_type}: Index exists but returned 0 matches")

            except Exception as e:
                error_str = str(e)
                if "Index not found" in error_str or "does not exist" in error_str:
                    print(f"❌ {node_type}: Vector index MISSING")
                else:
                    print(f"❌ {node_type}: Query failed - {e}")

    except Exception as e:
        print(f"❌ Index check failed: {e}")

    # Test 4: PING Test (inject known text, match identical embedding)
    print("\n[TEST 4] PING Test (Similarity Kernel)")
    print("-" * 60)

    try:
        # Create temporary PING node
        ping_text = "PING_TOKEN_123_DIAGNOSTIC"
        ping_embedding = embedding_service.embed(ping_text)
        ping_vector_str = str(ping_embedding.tolist())

        # Create node with known embedding
        create_query = f"""
        CREATE (n:Diagnostic {{
            name: 'ping_test_node',
            description: '{ping_text}',
            content_embedding: '{ping_vector_str}'
        }})
        RETURN n.name
        """
        result = r.execute_command('GRAPH.QUERY', graph_name, create_query)
        print(f"✅ Created PING test node")

        # Query with EXACT same embedding
        query_ping = f"""
        CALL db.idx.vector.queryNodes('Diagnostic', 'content_embedding', 1, vecf32({ping_vector_str}))
        YIELD node, score
        RETURN node.name, score
        """

        try:
            result = r.execute_command('GRAPH.QUERY', graph_name, query_ping)
            if result and result[1]:
                matched_name = result[1][0][0]
                similarity = float(result[1][0][1])
                print(f"✅ PING match found!")
                print(f"   Node: {matched_name}")
                print(f"   Similarity: {similarity:.4f} (should be ≈1.0)")

                if similarity < 0.95:
                    print(f"   ⚠️  WARNING: Self-match similarity too low ({similarity:.4f} < 0.95)")
                    print(f"   → Possible issue: Embedding storage/retrieval corrupted")
            else:
                print(f"❌ PING test FAILED: No match for identical embedding")
                print(f"   → Possible issue: Vector index not working or embedding format wrong")

        except Exception as e:
            print(f"❌ PING query failed: {e}")

        # Cleanup: Delete test node
        delete_query = "MATCH (n:Diagnostic {name: 'ping_test_node'}) DELETE n"
        r.execute_command('GRAPH.QUERY', graph_name, delete_query)
        print(f"   Cleaned up test node")

    except Exception as e:
        print(f"❌ PING test failed: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS SUMMARY")
    print("=" * 60)

    if nodes_with_embedding == 0:
        print("\n🔴 ROOT CAUSE: Nodes have NO embeddings")
        print("   Fix: Run embedding backfill script")
        print("   Command: python orchestration/scripts/backfill_embeddings.py")
    elif encoder_ok and nodes_with_embedding > 0:
        print("\n⚠️  PARTIAL DIAGNOSIS")
        print("   - Encoder: ✅ Working")
        print(f"   - Node embeddings: ⚠️  {nodes_with_embedding}/{total_nodes} ({(nodes_with_embedding/total_nodes*100):.1f}%)")
        print("   - Next: Check vector index and similarity calculations")
    else:
        print("\n✅ Basic components working - deeper investigation needed")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    import sys
    citizen_id = sys.argv[1] if len(sys.argv) > 1 else "felix"

    print(f"Diagnosing citizen: {citizen_id}")
    diagnose_stimulus_injection(citizen_id)
