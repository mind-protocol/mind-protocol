"""
Fix Energy Schema - Migrate scalar energy → dict energy

Problem: Old nodes in database have:
  energy: 0.0  # ❌ Scalar float

Spec requires:
  energy: {"entity_id": 0.0}  # ✅ Dict[str, float]

This script:
1. Scans all nodes in all graphs
2. Converts scalar energy → dict with default entity
3. Updates nodes in place
4. Preserves all other properties

Author: Felix "Ironhand"
Date: 2025-10-21
Purpose: Fix schema bug blocking multi-entity consciousness
"""

import json
from falkordb import FalkorDB

# Configuration
DEFAULT_ENTITY = "consciousness_engine"  # Default entity for migrated energy
GRAPHS_TO_FIX = [
    "citizen_luca",
    "citizen_felix",
    "citizen_iris",
    "citizen_ada",
    "mind_protocol_collective_graph"
]

def fix_graph_energy(graph_name: str, dry_run: bool = True):
    """
    Fix energy schema for one graph.

    Args:
        graph_name: Name of graph to fix
        dry_run: If True, only report what would be changed
    """
    print(f"\n{'='*60}")
    print(f"Graph: {graph_name}")
    print(f"{'='*60}")

    db = FalkorDB()
    g = db.select_graph(graph_name)

    # Query all nodes
    result = g.query('MATCH (n) RETURN id(n) as node_id, n.energy as energy, n.name as name')

    if not result.result_set:
        print("No nodes found")
        return

    nodes_to_fix = []
    nodes_already_correct = []

    for row in result.result_set:
        node_id = row[0]
        energy_val = row[1]
        name = row[2] if len(row) > 2 else "unknown"

        # Check type
        if energy_val is None:
            # NULL - needs fixing (default to 0.0)
            nodes_to_fix.append((node_id, 0.0, name))
        elif isinstance(energy_val, (int, float)):
            # Scalar - needs fixing
            nodes_to_fix.append((node_id, energy_val, name))
        elif isinstance(energy_val, str):
            # Might be JSON string - check
            try:
                parsed = json.loads(energy_val)
                if isinstance(parsed, dict):
                    nodes_already_correct.append((node_id, name))
                else:
                    nodes_to_fix.append((node_id, energy_val, name))
            except:
                nodes_to_fix.append((node_id, energy_val, name))
        else:
            print(f"⚠️  Unknown energy type for node {name}: {type(energy_val)}")

    print(f"\nNodes to fix: {len(nodes_to_fix)}")
    print(f"Already correct: {len(nodes_already_correct)}")

    if nodes_to_fix:
        print(f"\nSample nodes to fix:")
        for node_id, energy_val, name in nodes_to_fix[:5]:
            print(f"  {name}: energy={energy_val} (type={type(energy_val).__name__})")

    if dry_run:
        print(f"\n🔍 DRY RUN - Would fix {len(nodes_to_fix)} nodes")
        print(f"   Conversion: energy={energy_val} → energy=\"{{{DEFAULT_ENTITY}: {energy_val}}}\"")
        return

    # Actually fix
    print(f"\n🔧 FIXING {len(nodes_to_fix)} nodes...")

    fixed_count = 0
    for node_id, old_energy, name in nodes_to_fix:
        # Convert scalar → dict
        if isinstance(old_energy, (int, float)):
            new_energy_dict = {DEFAULT_ENTITY: float(old_energy)}
        else:
            # Fallback: zero energy
            new_energy_dict = {DEFAULT_ENTITY: 0.0}

        new_energy_json = json.dumps(new_energy_dict)

        # Update node
        try:
            update_query = f"""
            MATCH (n)
            WHERE id(n) = {node_id}
            SET n.energy = '{new_energy_json}'
            """
            g.query(update_query)
            fixed_count += 1

            if fixed_count % 100 == 0:
                print(f"  Fixed {fixed_count}/{len(nodes_to_fix)}...")
        except Exception as e:
            print(f"❌ Error fixing node {name}: {e}")

    print(f"✅ Fixed {fixed_count} nodes")


def verify_fix(graph_name: str):
    """
    Verify all nodes have dict energy.

    Args:
        graph_name: Graph to verify
    """
    print(f"\n{'='*60}")
    print(f"Verifying: {graph_name}")
    print(f"{'='*60}")

    db = FalkorDB()
    g = db.select_graph(graph_name)

    result = g.query('MATCH (n) RETURN n.energy LIMIT 10')

    all_correct = True
    for i, row in enumerate(result.result_set):
        energy_val = row[0]

        # Check if it's JSON string
        if isinstance(energy_val, str):
            try:
                parsed = json.loads(energy_val)
                if isinstance(parsed, dict):
                    print(f"✅ Node {i+1}: {energy_val} (dict)")
                else:
                    print(f"❌ Node {i+1}: {energy_val} (not dict)")
                    all_correct = False
            except:
                print(f"❌ Node {i+1}: {energy_val} (not JSON)")
                all_correct = False
        else:
            print(f"❌ Node {i+1}: {energy_val} (scalar {type(energy_val).__name__})")
            all_correct = False

    if all_correct:
        print(f"\n✅ All verified nodes have correct dict energy structure")
    else:
        print(f"\n❌ Some nodes still have incorrect energy structure")


if __name__ == "__main__":
    import sys

    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("="*60)
        print("DRY RUN MODE - No changes will be made")
        print("Add --execute flag to actually fix the database")
        print("="*60)
    else:
        print("="*60)
        print("⚠️  EXECUTE MODE - Database will be modified")
        print("="*60)
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted")
            sys.exit(0)

    # Fix all graphs
    for graph_name in GRAPHS_TO_FIX:
        try:
            fix_graph_energy(graph_name, dry_run=dry_run)
        except Exception as e:
            print(f"❌ Error processing {graph_name}: {e}")

    # Verify if not dry run
    if not dry_run:
        print(f"\n\n{'='*60}")
        print("VERIFICATION")
        print(f"{'='*60}")
        for graph_name in GRAPHS_TO_FIX:
            try:
                verify_fix(graph_name)
            except Exception as e:
                print(f"❌ Error verifying {graph_name}: {e}")

    print(f"\n{'='*60}")
    if dry_run:
        print("DRY RUN COMPLETE - Run with --execute to apply changes")
    else:
        print("MIGRATION COMPLETE")
    print(f"{'='*60}")
