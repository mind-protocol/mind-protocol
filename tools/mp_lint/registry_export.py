"""
L4 Registry Export - Public Schema Snapshot

Exports the authoritative schema registry from L4 to JSON for linting.

Output format:
{
  "version": "1.0.0",
  "exported_at": "2025-10-31T01:30:00Z",
  "bundles": [...],
  "schemas": [...],
  "topics": [...],
  "signature_suites": [...],
  "type_index": [...]
}

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

from falkordb import FalkorDB
import json
from datetime import datetime, timezone
from typing import Dict, List, Any


def export_registry(output_path: str = "build/l4_registry.json") -> Dict[str, Any]:
    """
    Export L4 schema registry to JSON for linting.

    Returns the public projection (no governance-private data).
    """

    db = FalkorDB(host='localhost', port=6379)

    # For now, export from schema_registry graph
    # Later: export from L4 consciousness graph when registry is there
    g = db.select_graph("schema_registry")

    registry = {
        "version": "1.0.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source": "schema_registry",
        "type_index": [],
        "node_types": [],
        "link_types": [],
    }

    # Export universal node types
    result = g.query("""
        MATCH (nt:NodeTypeSchema)
        WHERE nt.type_name STARTS WITH 'U3_' OR nt.type_name STARTS WITH 'U4_'
        RETURN nt.type_name as type_name,
               nt.level as level,
               nt.category as category,
               nt.description as description
        ORDER BY nt.type_name
    """)

    for record in result.result_set:
        registry["node_types"].append({
            "type_name": record[0],
            "level": record[1],
            "category": record[2],
            "description": record[3],
        })

    # Export universal link types
    result = g.query("""
        MATCH (lt:LinkTypeSchema)
        WHERE lt.type_name STARTS WITH 'U3_' OR lt.type_name STARTS WITH 'U4_'
        RETURN lt.type_name as type_name,
               lt.level as level,
               lt.category as category,
               lt.description as description
        ORDER BY lt.type_name
    """)

    for record in result.result_set:
        registry["link_types"].append({
            "type_name": record[0],
            "level": record[1],
            "category": record[2],
            "description": record[3],
        })

    # Write to file
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"✓ Exported L4 registry to {output_path}")
    print(f"  - {len(registry['node_types'])} universal node types")
    print(f"  - {len(registry['link_types'])} universal link types")

    return registry


if __name__ == "__main__":
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else "build/l4_registry.json"
    export_registry(output_path)
