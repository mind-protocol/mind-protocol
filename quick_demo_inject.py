#!/usr/bin/env python3
"""
Quick Demo - Inject consciousness nodes for visualization testing
"""

from falkordb import FalkorDB
from datetime import datetime, timezone
import random

def inject_demo_consciousness():
    """Inject demo nodes and links into Felix's consciousness graph"""

    db = FalkorDB(host='localhost', port=6379)
    graph_name = "consciousness-infrastructure_mind-protocol_felix"
    g = db.select_graph(graph_name)

    now = datetime.now(timezone.utc).isoformat()

    # Create some demo nodes with different types
    demo_nodes = [
        {"id": "memory_architecture_patterns", "type": "Memory", "name": "Architecture Patterns", "description": "Common design patterns for consciousness systems"},
        {"id": "memory_graph_theory", "type": "Memory", "name": "Graph Theory Basics", "description": "Fundamental graph algorithms and data structures"},
        {"id": "concept_spreading_activation", "type": "Concept", "name": "Spreading Activation", "description": "Energy propagation through graph networks"},
        {"id": "concept_subentity_system", "type": "Concept", "name": "SubEntity System", "description": "Specialized consciousness components"},
        {"id": "mechanism_energy_dynamics", "type": "Mechanism", "name": "Energy Dynamics", "description": "Energy allocation and flow mechanisms"},
        {"id": "mechanism_working_memory", "type": "Mechanism", "name": "Working Memory", "description": "Active attention management"},
        {"id": "best_practice_modular_design", "type": "Best_Practice", "name": "Modular Design", "description": "Breaking systems into composable parts"},
        {"id": "best_practice_test_driven", "type": "Best_Practice", "name": "Test-Driven Development", "description": "Write tests before implementation"},
        {"id": "project_consciousness_engine", "type": "Project", "name": "Consciousness Engine V2", "description": "Next generation consciousness architecture"},
        {"id": "task_implement_wm_selection", "type": "Task", "name": "Implement WM Selection", "description": "Build working memory node selection algorithm"},
    ]

    print("Creating demo nodes...")
    for node in demo_nodes:
        energy = random.uniform(0.3, 0.9)
        confidence = random.uniform(0.5, 1.0)

        query = f"""
        MERGE (n:{node['type']} {{node_id: '{node['id']}'}})
        ON CREATE SET
            n.node_id = '{node['id']}',
            n.name = '{node['name']}',
            n.description = '{node['description']}',
            n.energy = {energy},
            n.confidence = {confidence},
            n.created_at = '{now}',
            n.last_active = '{now}',
            n.traversal_count = {random.randint(1, 20)}
        ON MATCH SET
            n.energy = {energy},
            n.last_active = '{now}'
        RETURN n.node_id
        """
        result = g.query(query)
        print(f"  ✓ Created {node['type']}: {node['name']}")

    # Create links between nodes
    demo_links = [
        ("memory_architecture_patterns", "ENABLES", "best_practice_modular_design"),
        ("memory_graph_theory", "BUILDS_TOWARD", "concept_spreading_activation"),
        ("concept_spreading_activation", "USES", "mechanism_energy_dynamics"),
        ("concept_subentity_system", "USES", "mechanism_working_memory"),
        ("mechanism_energy_dynamics", "ENABLES", "project_consciousness_engine"),
        ("mechanism_working_memory", "ENABLES", "task_implement_wm_selection"),
        ("best_practice_modular_design", "JUSTIFIES", "project_consciousness_engine"),
        ("best_practice_test_driven", "JUSTIFIES", "task_implement_wm_selection"),
        ("project_consciousness_engine", "REQUIRES", "task_implement_wm_selection"),
    ]

    print("\nCreating demo links...")
    for source, link_type, target in demo_links:
        weight = random.uniform(0.5, 1.0)
        query = f"""
        MATCH (source {{node_id: '{source}'}}), (target {{node_id: '{target}'}})
        MERGE (source)-[r:{link_type}]->(target)
        ON CREATE SET
            r.weight = {weight},
            r.created_at = '{now}'
        ON MATCH SET
            r.weight = {weight}
        RETURN type(r)
        """
        result = g.query(query)
        print(f"  ✓ Created {link_type}: {source} → {target}")

    # Check final count
    result = g.query("MATCH (n) RETURN count(n) as node_count")
    node_count = result.result_set[0][0]

    result = g.query("MATCH ()-[r]->() RETURN count(r) as link_count")
    link_count = result.result_set[0][0]

    print(f"\n✅ Demo data injected!")
    print(f"   Total nodes: {node_count}")
    print(f"   Total links: {link_count}")
    print(f"\n🎯 Now refresh the dashboard at http://localhost:3000/consciousness to see the graph!")

if __name__ == "__main__":
    inject_demo_consciousness()
