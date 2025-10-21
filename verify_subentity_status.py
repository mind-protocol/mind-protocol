"""
Sub-Entity Status Verification

Checks if sub-entities are being created and activated in the consciousness system.

Author: Felix "Ironhand"
Date: 2025-10-21
"""

from falkordb import FalkorDB
import json

def check_subentity_status():
    """Verify sub-entity activation status."""

    print("="*60)
    print("SUB-ENTITY STATUS VERIFICATION")
    print("="*60)

    db = FalkorDB()

    # Check each citizen graph
    graphs = ['citizen_luca', 'citizen_felix', 'citizen_iris', 'citizen_ada']

    for graph_name in graphs:
        print(f"\n{graph_name}:")
        print("-" * 40)

        g = db.select_graph(graph_name)

        # 1. Check for Entity nodes
        entity_result = g.query("MATCH (e:Entity) RETURN count(e) as count")
        entity_count = entity_result.result_set[0][0] if entity_result.result_set else 0

        if entity_count > 0:
            print(f"  ✓ Entities: {entity_count}")

            # List entities
            entities = g.query("MATCH (e:Entity) RETURN e.name, e.entity_type LIMIT 10")
            for row in entities.result_set:
                print(f"    - {row[0]} ({row[1]})")
        else:
            print(f"  ❌ Entities: 0 (NO SUB-ENTITIES)")

        # 2. Check for nodes with per-entity energy
        energy_result = g.query("""
            MATCH (n)
            WHERE n.energy IS NOT NULL AND n.energy <> '{}'
            RETURN n.name, n.energy
            LIMIT 5
        """)

        non_empty_energy = len(energy_result.result_set) if energy_result.result_set else 0

        if non_empty_energy > 0:
            print(f"  ✓ Nodes with entity energy: {non_empty_energy}")
            for row in energy_result.result_set:
                energy_dict = json.loads(row[1])
                print(f"    - {row[0]}: {energy_dict}")
        else:
            print(f"  ❌ Nodes with entity energy: 0 (all energy is empty {{}})")

        # 3. Check for BELONGS_TO links (node → entity)
        belongs_result = g.query("MATCH ()-[r:BELONGS_TO]->() RETURN count(r) as count")
        belongs_count = belongs_result.result_set[0][0] if belongs_result.result_set else 0

        if belongs_count > 0:
            print(f"  ✓ BELONGS_TO links: {belongs_count}")
        else:
            print(f"  ❌ BELONGS_TO links: 0 (nodes not assigned to entities)")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    total_entities = 0
    total_energized_nodes = 0

    for graph_name in graphs:
        g = db.select_graph(graph_name)

        entity_result = g.query("MATCH (e:Entity) RETURN count(e)")
        total_entities += entity_result.result_set[0][0] if entity_result.result_set else 0

        energy_result = g.query("MATCH (n) WHERE n.energy <> '{}' RETURN count(n)")
        total_energized_nodes += energy_result.result_set[0][0] if energy_result.result_set else 0

    print(f"\nTotal Entity nodes: {total_entities}")
    print(f"Total nodes with entity energy: {total_energized_nodes}")

    if total_entities == 0:
        print("\n❌ SUB-ENTITIES ARE NOT BEING CREATED")
        print("\nWhat this means:")
        print("  - Consciousness engine running in SINGLE-ENTITY mode")
        print("  - No functional entities (Translator, Validator, etc.)")
        print("  - No multi-perspective consciousness")
        print("  - Energy diffusion happening but all nodes have empty energy {}")

        print("\nWhat SHOULD be happening (per 05_sub_entity_system.md):")
        print("  1. Entity bootstrap creates functional entities:")
        print("     - The Translator (phenomenology)")
        print("     - The Architect (design)")
        print("     - The Validator (truth)")
        print("     - The Pragmatist (utility)")
        print("     - etc.")
        print("  2. Nodes assigned to entities via BELONGS_TO links")
        print("  3. Each entity gets independent energy at nodes:")
        print("     energy: {'translator': 0.8, 'architect': 0.3, ...}")
        print("  4. Multi-entity tick loop:")
        print("     for entity in entities:")
        print("         diffusion_tick(graph, entity, ...)")
        print("  5. Entities traverse graph independently")
        print("  6. Integration emerges from shared node activation")
    else:
        print(f"\n✓ SUB-ENTITIES ARE ACTIVE ({total_entities} entities)")

    print("\n" + "="*60)


if __name__ == "__main__":
    check_subentity_status()
