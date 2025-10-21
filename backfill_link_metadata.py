"""
Backfill Consciousness Metadata on Existing Links

This script adds the missing consciousness metadata (goal, sub_entity_valences,
sub_entity_emotion_vectors) to existing links in citizen graphs, enabling
Critical Traversal to function.

Author: Iris "The Aperture"
Date: 2025-10-19
"""

from falkordb import FalkorDB


def backfill_felix_links():
    """Add consciousness metadata to Felix's existing links."""

    db = FalkorDB(host='localhost', port=6379)
    graph = db.select_graph('citizen_felix')

    print("=" * 60)
    print("BACKFILLING CONSCIOUSNESS METADATA FOR citizen_felix")
    print("=" * 60)

    # Get all links
    result = graph.query("MATCH ()-[r]->() RETURN id(r) as link_id, type(r) as link_type")
    links = [(record[0], record[1]) for record in result.result_set]

    print(f"\nFound {len(links)} links to update")

    updated = 0
    for link_id, link_type in links:
        # Add consciousness metadata based on link type
        if link_type == "ALIGNED_ON":
            goal = "Shared alignment on technical direction"
            valence = 0.8
            emotions = '{"confidence": 0.8, "focus": 0.7}'
            energy = 0.6
        elif link_type == "COLLABORATIVE_BUILD":
            goal = "Building together towards shared outcome"
            valence = 0.85
            emotions = '{"momentum": 0.9, "satisfaction": 0.8}'
            energy = 0.7
        elif link_type == "REQUIRES":
            goal = "Dependency relationship for implementation"
            valence = 0.5
            emotions = '{"focus": 0.7, "pressure": 0.6}'
            energy = 0.6
        else:
            # Default consciousness metadata
            goal = f"Connection of type {link_type}"
            valence = 0.6
            emotions = '{"neutral": 0.5}'
            energy = 0.5

        # Build update query - use JSON strings for nested dicts
        query = f"""
        MATCH ()-[r]->() WHERE id(r) = {link_id}
        SET r.goal = '{goal}',
            r.energy = {energy},
            r.sub_entity_valences = '{{"felix_builder": {valence}}}',
            r.sub_entity_emotion_vectors = '{{"felix_builder": {emotions}}}'
        RETURN id(r)
        """

        try:
            graph.query(query)
            updated += 1
            if updated % 10 == 0:
                print(f"  Updated {updated}/{len(links)} links...")
        except Exception as e:
            print(f"  ERROR updating link {link_id}: {e}")

    print(f"\nBackfill complete: {updated}/{len(links)} links updated")

    # Verify
    print("\nVerifying metadata...")
    result = graph.query("""
        MATCH ()-[r]->()
        RETURN type(r), r.link_strength, r.energy, r.goal, r.sub_entity_valences
        LIMIT 5
    """)

    print("\nSample links after backfill:")
    for record in result.result_set:
        print(f"  {record[0]}")
        print(f"    strength={record[1]}, energy={record[2]}")
        print(f"    goal={record[3]}")
        print(f"    valences={record[4]}")


if __name__ == "__main__":
    backfill_felix_links()
    print("\n" + "=" * 60)
    print("Branching ratio should now increase as SubEntities traverse!")
    print("=" * 60)
