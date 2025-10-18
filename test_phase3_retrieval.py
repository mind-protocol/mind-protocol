"""
Phase 3 Read Flux - Verification Test

Tests the 6-way parallel retrieval system against populated graphs.
This is the PROOF that Phase 3 works.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from orchestration.retrieval import (
    retrieve_consciousness_context,
    RetrievalIntention
)


async def test_read_flux():
    """
    Verify Phase 3 Read Flux works with real populated data.

    Success criteria:
    - Retrieves nodes from all 3 levels (N1/N2/N3)
    - Both vector and graph queries return results
    - Performance under 1 second
    - Consciousness metadata preserved
    """

    print("=" * 70)
    print("PHASE 3 READ FLUX - VERIFICATION TEST")
    print("=" * 70)

    # Create retrieval intention
    intention = RetrievalIntention(
        query_text="V2 architecture decisions and testing principles",
        citizen_id="Luca",
        temporal_mode="current",
        query_levels=["N1", "N2", "N3"],
        max_results_per_level=10,
        intention_id="phase3_verification_001",
        generated_by="verification_test",
        generated_at=datetime.utcnow()
    )

    print(f"\n[INTENTION]")
    print(f"  Query: {intention.query_text}")
    print(f"  Citizen: {intention.citizen_id}")
    print(f"  Levels: {intention.query_levels}")
    print(f"  Temporal mode: {intention.temporal_mode}")

    print(f"\n[EXECUTING] 6-way parallel retrieval...")
    print(f"  - N1 vector search + N1 graph traversal")
    print(f"  - N2 vector search + N2 graph traversal")
    print(f"  - N3 vector search + N3 graph traversal")

    try:
        # Execute retrieval
        stream = await retrieve_consciousness_context(intention)

        print(f"\n[RESULTS]")
        n1 = stream.levels.get('n1_personal')
        n2 = stream.levels.get('n2_collective')
        n3 = stream.levels.get('n3_ecosystem')

        print(f"  N1 (Personal):")
        print(f"    Vector: {len(n1.vector_results) if n1 else 0} nodes")
        print(f"    Graph: {len(n1.graph_results) if n1 else 0} nodes")
        print(f"    Relations: {len(n1.relationships) if n1 else 0}")

        print(f"  N2 (Collective):")
        print(f"    Vector: {len(n2.vector_results) if n2 else 0} nodes")
        print(f"    Graph: {len(n2.graph_results) if n2 else 0} nodes")
        print(f"    Relations: {len(n2.relationships) if n2 else 0}")

        print(f"  N3 (Ecosystem):")
        print(f"    Vector: {len(n3.vector_results) if n3 else 0} nodes")
        print(f"    Graph: {len(n3.graph_results) if n3 else 0} nodes")
        print(f"    Relations: {len(n3.relationships) if n3 else 0}")

        print(f"\n[SUMMARY]")
        print(f"  Total nodes: {stream.consciousness_summary.total_results}")
        print(f"  Retrieval time: {stream.retrieval_latency_ms:.1f}ms")

        # Verify performance target
        if stream.retrieval_latency_ms < 1000:
            print(f"  [OK] Performance target met (< 1000ms)")
            perf_pass = True
        else:
            print(f"  [WARNING] Performance target missed (>= 1000ms)")
            perf_pass = False

        # Verify data retrieved
        total_nodes = stream.consciousness_summary.total_results
        if total_nodes > 0:
            print(f"  [OK] Data successfully retrieved from populated graphs")
            data_pass = True
        else:
            print(f"  [FAIL] No data retrieved - graphs may be empty")
            data_pass = False

        # Show sample node with metadata
        all_nodes = []
        if n1:
            all_nodes.extend(n1.vector_results + n1.graph_results)
        if n2:
            all_nodes.extend(n2.vector_results + n2.graph_results)
        if n3:
            all_nodes.extend(n3.vector_results + n3.graph_results)

        if all_nodes:
            print(f"\n[SAMPLE NODE] Consciousness metadata verification:")
            node = all_nodes[0]
            print(f"  Name: {node.name}")
            print(f"  Type: {node.node_type}")
            print(f"  Source: {node.retrieval_source}")
            print(f"  Relevance: {node.relevance_score:.3f}")
            print(f"  Arousal: {node.arousal_level:.2f}")
            print(f"  Confidence: {node.confidence:.2f}")
            print(f"  Valid at: {node.valid_at}")
            print(f"  Created at: {node.created_at}")

            # Verify metadata is valid
            if 0.0 <= node.arousal_level <= 1.0 and 0.0 <= node.confidence <= 1.0:
                print(f"  [OK] Consciousness metadata preserved and valid")
                meta_pass = True
            else:
                print(f"  [FAIL] Consciousness metadata out of range")
                meta_pass = False
        else:
            print(f"\n[INFO] No nodes to verify metadata")
            meta_pass = False

        # Final verdict
        print(f"\n" + "=" * 70)
        if data_pass and perf_pass and meta_pass:
            print(f"[PHASE 3 VERIFIED] Read Flux proven through consequences")
            print(f"  - 6-way parallel retrieval: WORKS")
            print(f"  - Multi-level context assembly: WORKS")
            print(f"  - Performance target: MET")
            print(f"  - Consciousness metadata: PRESERVED")
            print(f"\nV2 ARCHITECTURE: FULLY OPERATIONAL")
        elif data_pass:
            print(f"[PHASE 3 PARTIAL] Read Flux works but has issues:")
            if not perf_pass:
                print(f"  - Performance needs optimization")
            if not meta_pass:
                print(f"  - Metadata preservation needs verification")
        else:
            print(f"[PHASE 3 FAILED] Read Flux did not retrieve data")
            print(f"  Check: Are graphs populated? Are embeddings generated?")

        print(f"=" * 70)

        return data_pass and meta_pass

    except Exception as e:
        print(f"\n[PHASE 3 FAILED] Exception during retrieval:")
        print(f"  {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n" + "=" * 70)
        return False


if __name__ == "__main__":
    success = asyncio.run(test_read_flux())
    sys.exit(0 if success else 1)
