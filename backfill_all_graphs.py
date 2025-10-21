"""
Backfill Consciousness Metadata on ALL Citizen Graphs

Adds missing consciousness metadata to all existing links across all graphs
to enable Critical Traversal.

Author: Iris "The Aperture"
Date: 2025-10-19
"""

from falkordb import FalkorDB


def get_metadata_for_link_type(link_type: str, entity_id: str = "default_entity"):
    """Generate consciousness metadata based on link type."""

    metadata_map = {
        "ALIGNED_ON": {
            "goal": "Shared alignment on technical direction",
            "valence": 0.8,
            "emotions": '{"confidence": 0.8, "focus": 0.7}',
            "energy": 0.6
        },
        "COLLABORATIVE_BUILD": {
            "goal": "Building together towards shared outcome",
            "valence": 0.85,
            "emotions": '{"momentum": 0.9, "satisfaction": 0.8}',
            "energy": 0.7
        },
        "REQUIRES": {
            "goal": "Dependency relationship for implementation",
            "valence": 0.5,
            "emotions": '{"focus": 0.7, "pressure": 0.6}',
            "energy": 0.6
        },
        "ENABLES": {
            "goal": "Makes something possible or easier",
            "valence": 0.75,
            "emotions": '{"clarity": 0.8, "confidence": 0.7}',
            "energy": 0.65
        },
        "JUSTIFIES": {
            "goal": "Provides rationale or evidence",
            "valence": 0.7,
            "emotions": '{"certainty": 0.8, "focus": 0.7}',
            "energy": 0.6
        },
        "RELATES_TO": {
            "goal": "General connection between concepts",
            "valence": 0.6,
            "emotions": '{"curiosity": 0.6, "exploration": 0.5}',
            "energy": 0.5
        },
        "LED_TO": {
            "goal": "Causal or sequential relationship",
            "valence": 0.65,
            "emotions": '{"understanding": 0.7, "connection": 0.6}',
            "energy": 0.55
        },
        "IMPLEMENTS": {
            "goal": "Putting theory into practice",
            "valence": 0.8,
            "emotions": '{"focus": 0.9, "momentum": 0.8}',
            "energy": 0.7
        },
        "DOCUMENTS": {
            "goal": "Recording knowledge for future reference",
            "valence": 0.7,
            "emotions": '{"clarity": 0.8, "completion": 0.7}',
            "energy": 0.5
        },
        "BLOCKS": {
            "goal": "Prevents or constrains progress",
            "valence": -0.6,
            "emotions": '{"frustration": 0.7, "pressure": 0.8}',
            "energy": 0.75
        }
    }

    # Get metadata or use default
    metadata = metadata_map.get(link_type, {
        "goal": f"Connection of type {link_type}",
        "valence": 0.6,
        "emotions": '{"neutral": 0.5}',
        "energy": 0.5
    })

    return metadata


def backfill_graph(graph_name: str, default_entity_id: str):
    """Backfill a single graph with consciousness metadata."""

    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph(graph_name)

    print(f"\n{'=' * 60}")
    print(f"Backfilling: {graph_name}")
    print(f"{'=' * 60}")

    # Get all links
    result = graph.query("MATCH ()-[r]->() RETURN id(r) as link_id, type(r) as link_type")
    links = [(record[0], record[1]) for record in result.result_set]

    if not links:
        print("  No links to update")
        return 0

    print(f"  Found {len(links)} links")

    updated = 0
    for link_id, link_type in links:
        metadata = get_metadata_for_link_type(link_type, default_entity_id)

        # Build update query
        query = f"""
        MATCH ()-[r]->() WHERE id(r) = {link_id}
        SET r.goal = '{metadata['goal']}',
            r.energy = {metadata['energy']},
            r.sub_entity_valences = '{{"{default_entity_id}": {metadata['valence']}}}',
            r.sub_entity_emotion_vectors = '{{"{default_entity_id}": {metadata['emotions']}}}'
        RETURN id(r)
        """

        try:
            graph.query(query)
            updated += 1
            if updated % 20 == 0:
                print(f"    Updated {updated}/{len(links)}...")
        except Exception as e:
            print(f"    ERROR updating link {link_id}: {e}")

    print(f"  Complete: {updated}/{len(links)} links updated")
    return updated


def main():
    """Backfill all citizen graphs."""

    graphs_to_backfill = [
        ("citizen_felix", "felix_builder"),
        ("citizen_luca", "luca_phenomenologist"),
        ("citizen_ada", "ada_architect"),
        ("citizen_iris", "iris_observer"),
        ("org_mind_protocol", "mind_protocol_operations")
    ]

    print("=" * 60)
    print("BACKFILLING CONSCIOUSNESS METADATA - ALL GRAPHS")
    print("=" * 60)

    total_updated = 0
    for graph_name, entity_id in graphs_to_backfill:
        updated = backfill_graph(graph_name, entity_id)
        total_updated += updated

    print(f"\n{'=' * 60}")
    print(f"BACKFILL COMPLETE: {total_updated} links updated across all graphs")
    print(f"{'=' * 60}")
    print("\nCritical Traversal should now work!")
    print("Watch for branching ratio > 0 in consciousness logs")


if __name__ == "__main__":
    main()
