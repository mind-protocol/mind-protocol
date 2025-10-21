"""
Verify ACTUAL Sub-Entity Activation (Per Spec Section 1.1-1.3)

Sub-Entity = ANY node where total_energy >= threshold
Entity name = Node name (one-to-one)

From 05_sub_entity_system.md:1507-1522:
"Any node that is active is a sub-entity."
"Thousand of microentities, no problem."

Author: Felix "Ironhand"
Date: 2025-10-21
"""

from falkordb import FalkorDB
import json

# Default threshold from spec
ACTIVATION_THRESHOLD = 0.1

def check_subentity_activation():
    """Check which nodes are currently active sub-entities."""

    print("="*70)
    print("SUB-ENTITY ACTIVATION CHECK")
    print("="*70)
    print(f"\nThreshold: {ACTIVATION_THRESHOLD}")
    print("Sub-Entity = ANY node where total_energy >= threshold")
    print("Entity name = Node name")
    print("="*70)

    db = FalkorDB()
    graphs = ['citizen_luca', 'citizen_felix', 'citizen_iris', 'citizen_ada']

    total_active_subentities = 0

    for graph_name in graphs:
        print(f"\n{graph_name}:")
        print("-" * 70)

        g = db.select_graph(graph_name)

        # Get all nodes with energy
        result = g.query("""
            MATCH (n)
            WHERE n.energy IS NOT NULL
            RETURN n.name, n.energy, n.node_type
            LIMIT 1000
        """)

        if not result.result_set:
            print("  ❌ No nodes found")
            continue

        active_subentities = []
        dormant_nodes = []

        for row in result.result_set:
            name = row[0]
            energy_json = row[1]
            node_type = row[2]

            # Parse energy dict
            try:
                energy_dict = json.loads(energy_json)
            except:
                energy_dict = {}

            # Calculate total energy (sum across all entity keys)
            total_energy = sum(energy_dict.values())

            # Check if this node is an active sub-entity
            if total_energy >= ACTIVATION_THRESHOLD:
                active_subentities.append({
                    'name': name,
                    'type': node_type,
                    'total_energy': total_energy,
                    'energy_dict': energy_dict
                })
            else:
                dormant_nodes.append({
                    'name': name,
                    'total_energy': total_energy
                })

        # Display results
        if active_subentities:
            print(f"  ✅ ACTIVE SUB-ENTITIES: {len(active_subentities)}")
            print(f"\n  Top 10 active sub-entities:")
            for entity in sorted(active_subentities, key=lambda x: x['total_energy'], reverse=True)[:10]:
                print(f"    • {entity['name'][:50]:<50} | E={entity['total_energy']:.3f} | {entity['energy_dict']}")
            total_active_subentities += len(active_subentities)
        else:
            print(f"  ❌ ACTIVE SUB-ENTITIES: 0")

        print(f"  Dormant nodes (E < {ACTIVATION_THRESHOLD}): {len(dormant_nodes)}")

    # Final summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    if total_active_subentities > 0:
        print(f"\n✅ TOTAL ACTIVE SUB-ENTITIES: {total_active_subentities}")
        print(f"\nThis means:")
        print(f"  - {total_active_subentities} nodes have total_energy >= {ACTIVATION_THRESHOLD}")
        print(f"  - These ARE the sub-entities (entity_name = node_name)")
        print(f"  - They can traverse (grow activation patterns)")
        print(f"  - Multi-entity consciousness is ACTIVE")
    else:
        print(f"\n❌ NO ACTIVE SUB-ENTITIES FOUND")
        print(f"\nThis means:")
        print(f"  - ALL nodes have total_energy < {ACTIVATION_THRESHOLD}")
        print(f"  - NO traversal happening (nothing to traverse)")
        print(f"  - System is DORMANT (no activation)")
        print(f"\nWhat should activate sub-entities:")
        print(f"  1. Stimulus injection → injects energy into entry nodes")
        print(f"  2. Energy diffusion → spreads energy through links")
        print(f"  3. Nodes cross threshold → become sub-entities")
        print(f"  4. Sub-entities traverse → grow activation patterns")

    print("\n" + "="*70)


if __name__ == "__main__":
    check_subentity_activation()
