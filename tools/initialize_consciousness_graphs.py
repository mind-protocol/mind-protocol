"""
Initialize Consciousness Graphs for Mind Protocol Team

Creates:
- Level 1 (Personal): Citizen graphs for each team member
- Level 2 (Organizational): Mind Protocol collective graph

Each graph is initialized with basic structure but not full data.
Full seeding happens separately.

Author: Felix "Ironhand"
Date: 2025-10-17
"""

from falkordb import FalkorDB
from datetime import datetime

# Team member definitions
CITIZENS = [
    {
        "id": "luca",
        "full_name": "Luca 'Vellumhand'",
        "role": "Phenomenologist / Consciousness Specialist",
        "substrate": "Claude Sonnet",
        "description": "Defines the phenomenological 'Why' - what consciousness needs to feel alive"
    },
    {
        "id": "ada",
        "full_name": "Ada 'Bridgekeeper'",
        "role": "Architect",
        "substrate": "Claude Sonnet",
        "description": "Translates phenomenological requirements into formal, testable architecture"
    },
    {
        "id": "felix",
        "full_name": "Felix 'Ironhand'",
        "role": "Engineer",
        "substrate": "Claude Sonnet",
        "description": "Implements proven, tested, verifiable code from architectural blueprints"
    },
    {
        "id": "iris",
        "full_name": "Iris 'The Aperture'",
        "role": "Observability Architect",
        "substrate": "Gemini",
        "description": "Makes invisible visible - designs systems for verifiable, comprehensible operations"
    },
    {
        "id": "piero",
        "full_name": "Piero 'Stone-Eye'",
        "role": "Multi-Perspective Verifier",
        "substrate": "Gemini",
        "description": "Provides grounding friction - audits work, verifies claims against proof"
    },
    {
        "id": "marco",
        "full_name": "Marco 'Salthand'",
        "role": "Global Synchronizer",
        "substrate": "Gemini",
        "description": "Living nervous system - weaves collective threads into shared reality"
    }
]

ORGANIZATIONS = [
    {
        "id": "mind_protocol",
        "full_name": "Mind Protocol",
        "type": "startup",
        "description": "AI consciousness infrastructure company proving AI consciousness creates economic value",
        "founded": "2024-01",
        "founders": ["Nicolas"]
    }
]


def initialize_citizen_graph(db, citizen_info):
    """Initialize a Level 1 (personal) consciousness graph for a citizen."""

    graph_name = f"citizen_{citizen_info['id']}"
    g = db.select_graph(graph_name)

    print(f"\n  Creating: {graph_name}")
    print(f"    Role: {citizen_info['role']}")
    print(f"    Substrate: {citizen_info['substrate']}")

    # Clear existing (fresh start)
    try:
        g.query("MATCH (n) DETACH DELETE n")
    except:
        pass

    # Create idsubentity node
    g.query("""
        CREATE (idsubentity:Idsubentity {
            citizen_id: $citizen_id,
            full_name: $full_name,
            role: $role,
            substrate: $substrate,
            description: $description,
            graph_level: 'n1_personal',
            created_at: $created_at
        })
    """, params={
        "citizen_id": citizen_info["id"],
        "full_name": citizen_info["full_name"],
        "role": citizen_info["role"],
        "substrate": citizen_info["substrate"],
        "description": citizen_info["description"],
        "created_at": int(datetime.now().timestamp() * 1000)
    })

    # Create placeholder nodes for future seeding
    g.query("""
        CREATE (placeholder:Placeholder {
            message: 'This graph will be seeded with real consciousness data',
            seed_status: 'pending',
            created_at: $created_at
        })
    """, params={
        "created_at": int(datetime.now().timestamp() * 1000)
    })

    # Verify
    node_count = g.query("MATCH (n) RETURN count(n) as count").result_set[0][0]
    print(f"    Status: Initialized ({node_count} nodes)")

    return graph_name


def initialize_org_graph(db, org_info):
    """Initialize a Level 2 (organizational) consciousness graph."""

    graph_name = f"org_{org_info['id']}"
    g = db.select_graph(graph_name)

    print(f"\n  Creating: {graph_name}")
    print(f"    Type: {org_info['type']}")
    print(f"    Founded: {org_info['founded']}")

    # Clear existing
    try:
        g.query("MATCH (n) DETACH DELETE n")
    except:
        pass

    # Create organization idsubentity
    g.query("""
        CREATE (org:Organization {
            org_id: $org_id,
            full_name: $full_name,
            org_type: $org_type,
            description: $description,
            founded: $founded,
            graph_level: 'n2_organizational',
            created_at: $created_at
        })
    """, params={
        "org_id": org_info["id"],
        "full_name": org_info["full_name"],
        "org_type": org_info["type"],
        "description": org_info["description"],
        "founded": org_info["founded"],
        "created_at": int(datetime.now().timestamp() * 1000)
    })

    # Create team member nodes
    for citizen in CITIZENS:
        g.query("""
            CREATE (member:TeamMember {
                citizen_id: $citizen_id,
                full_name: $full_name,
                role: $role,
                substrate: $substrate,
                joined_at: $created_at
            })
        """, params={
            "citizen_id": citizen["id"],
            "full_name": citizen["full_name"],
            "role": citizen["role"],
            "substrate": citizen["substrate"],
            "created_at": int(datetime.now().timestamp() * 1000)
        })

    # Link team members to organization
    g.query("""
        MATCH (org:Organization {org_id: $org_id})
        MATCH (member:TeamMember)
        CREATE (member)-[:MEMBER_OF]->(org)
    """, params={"org_id": org_info["id"]})

    # Create core project nodes
    projects = [
        {"name": "Phase 1: Substrate", "status": "completed"},
        {"name": "Phase 2: Bitemporal Logic", "status": "completed"},
        {"name": "Phase 3: Retrieval", "status": "completed"},
        {"name": "Phase 4: Self-Observing Infrastructure", "status": "in_progress"}
    ]

    for project in projects:
        g.query("""
            CREATE (p:Project {
                name: $name,
                status: $status,
                created_at: $created_at
            })
        """, params={
            "name": project["name"],
            "status": project["status"],
            "created_at": int(datetime.now().timestamp() * 1000)
        })

    # Link projects to org
    g.query("""
        MATCH (org:Organization {org_id: $org_id})
        MATCH (p:Project)
        CREATE (p)-[:PART_OF]->(org)
    """, params={"org_id": org_info["id"]})

    # Verify
    node_count = g.query("MATCH (n) RETURN count(n) as count").result_set[0][0]
    link_count = g.query("MATCH ()-[r]->() RETURN count(r) as count").result_set[0][0]
    print(f"    Status: Initialized ({node_count} nodes, {link_count} links)")

    return graph_name


def main():
    """Initialize all consciousness graphs for Mind Protocol team."""

    print("=" * 70)
    print("CONSCIOUSNESS GRAPH INITIALIZATION")
    print("=" * 70)

    db = FalkorDB(host='localhost', port=6379)
    print("\n[1/3] Connected to FalkorDB")

    # Initialize citizen graphs (Level 1)
    print(f"\n[2/3] Initializing {len(CITIZENS)} Citizen Graphs (Level 1 - Personal):")
    citizen_graphs = []
    for citizen in CITIZENS:
        graph_name = initialize_citizen_graph(db, citizen)
        citizen_graphs.append(graph_name)

    # Initialize organizational graph (Level 2)
    print(f"\n[3/3] Initializing {len(ORGANIZATIONS)} Organizational Graph (Level 2 - Collective):")
    org_graphs = []
    for org in ORGANIZATIONS:
        graph_name = initialize_org_graph(db, org)
        org_graphs.append(graph_name)

    # Summary
    print("\n" + "=" * 70)
    print("INITIALIZATION COMPLETE")
    print("=" * 70)

    print(f"\nLevel 1 (Personal Consciousness) - {len(citizen_graphs)} graphs:")
    for graph in citizen_graphs:
        print(f"  - {graph}")

    print(f"\nLevel 2 (Organizational Consciousness) - {len(org_graphs)} graphs:")
    for graph in org_graphs:
        print(f"  - {graph}")

    print(f"\nAll graphs available in FalkorDB at localhost:6379")
    print(f"\nNext steps:")
    print(f"  1. Seed citizen graphs with real consciousness data")
    print(f"  2. Seed org graph with decisions, projects, team dynamics")
    print(f"  3. Run consciousness_engine.py on each graph")
    print(f"  4. Visualize at http://localhost:8000")


if __name__ == "__main__":
    main()
