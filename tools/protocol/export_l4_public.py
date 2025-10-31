#!/usr/bin/env python3
"""
Export L4 Public Registry for mp-lint

Exports Event_Schema, Topic_Namespace, and Governance_Policy nodes from the
protocol graph to build/l4_public_registry.json for use by the membrane linter.

The exported JSON includes:
- event_schemas: All Event_Schema nodes with their properties and relationships
- topic_namespaces: All Topic_Namespace nodes
- governance_policies: All Governance_Policy nodes
- metadata: Export timestamp, graph hash for freshness verification

Usage:
    python tools/protocol/export_l4_public.py
    python tools/protocol/export_l4_public.py --graph protocol --output build/l4_public_registry.json

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
Architecture: mp-lint infrastructure (static + runtime validation)
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from falkordb import FalkorDB

# Import hash computation from hash_l4_graph.py to ensure consistency
_tool_dir = Path(__file__).parent
sys.path.insert(0, str(_tool_dir))
from hash_l4_graph import compute_graph_hash as compute_canonical_hash


DEFAULT_GRAPH = "protocol"
DEFAULT_OUTPUT = Path("build/l4_public_registry.json")
_repo_root = Path(__file__).resolve().parents[2]


def decode_bytes(value: Any) -> Any:
    """Decode bytes to string, handle nested structures."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    elif isinstance(value, dict):
        return {k: decode_bytes(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [decode_bytes(v) for v in value]
    return value


def fetch_event_schemas(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch all Event_Schema nodes with their relationships.

    Returns list of:
    {
        "id": "protocol/Event_Schema/presence.beacon",
        "name": "presence.beacon",
        "type_name": "Event_Schema",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/presence",
        "summary": "...",
        "schema_hash": "sha256:...",
        "version": "1.0",
        "maps_to_topic": "protocol/Topic_Namespace/ecosystem.org.citizen.presence",
        "requires_envelope": "protocol/Envelope_Schema/L4_Envelope",
        "requires_sig": "protocol/Signature_Suite/Ed25519"
    }
    """
    query = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'Event_Schema'
    OPTIONAL MATCH (es)-[:MAPS_TO_TOPIC]->(ns:ProtocolNode)
    OPTIONAL MATCH (es)-[:REQUIRES_ENVELOPE]->(env:ProtocolNode)
    OPTIONAL MATCH (es)-[:REQUIRES_SIG]->(sig:ProtocolNode)
    RETURN
        es.id as id,
        es.name as name,
        es.type_name as type_name,
        es.direction as direction,
        es.topic_pattern as topic_pattern,
        es.summary as summary,
        es.schema_hash as schema_hash,
        es.version as version,
        ns.id as maps_to_topic,
        env.id as requires_envelope,
        sig.id as requires_sig
    ORDER BY es.name
    """

    result = graph_obj.query(query)
    schemas = []

    for row in result.result_set:
        schema = {
            "id": decode_bytes(row[0]) if row[0] else None,
            "name": decode_bytes(row[1]) if row[1] else None,
            "type_name": decode_bytes(row[2]) if row[2] else "Event_Schema",
            "direction": decode_bytes(row[3]) if row[3] else None,
            "topic_pattern": decode_bytes(row[4]) if row[4] else None,
            "summary": decode_bytes(row[5]) if row[5] else None,
            "schema_hash": decode_bytes(row[6]) if row[6] else None,
            "version": decode_bytes(row[7]) if row[7] else "1.0",
            "maps_to_topic": decode_bytes(row[8]) if row[8] else None,
            "requires_envelope": decode_bytes(row[9]) if row[9] else None,
            "requires_sig": decode_bytes(row[10]) if row[10] else None,
        }
        schemas.append(schema)

    return schemas


def fetch_topic_namespaces(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch all Topic_Namespace nodes.

    Returns list of:
    {
        "id": "protocol/Topic_Namespace/ecosystem.org.citizen.presence",
        "pattern": "ecosystem/{ecosystem_id}/org/{org_id}/citizen/{citizen_id}/presence",
        "type_name": "Topic_Namespace",
        "description": "..."
    }
    """
    query = """
    MATCH (ns:ProtocolNode)
    WHERE ns.type_name = 'Topic_Namespace'
    RETURN
        ns.id as id,
        ns.pattern as pattern,
        ns.type_name as type_name,
        ns.description as description
    ORDER BY ns.id
    """

    result = graph_obj.query(query)
    namespaces = []

    for row in result.result_set:
        namespace = {
            "id": decode_bytes(row[0]) if row[0] else None,
            "pattern": decode_bytes(row[1]) if row[1] else None,
            "type_name": decode_bytes(row[2]) if row[2] else "Topic_Namespace",
            "description": decode_bytes(row[3]) if row[3] else None,
        }
        namespaces.append(namespace)

    return namespaces


def fetch_governance_policies(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch all Governance_Policy nodes with their governed namespaces.

    Returns list of:
    {
        "id": "protocol/Governance_Policy/presence-namespace",
        "name": "Presence Events Policy",
        "type_name": "Governance_Policy",
        "defaults": {"max_payload_kb": 4, "rate_limit": {...}, ...},
        "governs": ["protocol/Topic_Namespace/ecosystem.org.citizen.presence"]
    }
    """
    query = """
    MATCH (gp:ProtocolNode)
    WHERE gp.type_name = 'Governance_Policy'
    OPTIONAL MATCH (gp)-[:GOVERNS]->(ns:ProtocolNode)
    RETURN
        gp.id as id,
        gp.name as name,
        gp.type_name as type_name,
        gp.defaults as defaults,
        collect(ns.id) as governs_list
    ORDER BY gp.id
    """

    result = graph_obj.query(query)
    policies = []

    for row in result.result_set:
        # Parse defaults JSON if it's a string
        defaults_raw = decode_bytes(row[3])
        if isinstance(defaults_raw, str):
            try:
                defaults = json.loads(defaults_raw)
            except json.JSONDecodeError:
                defaults = defaults_raw
        else:
            defaults = defaults_raw

        # Filter out None values from governs_list
        governs_list = [decode_bytes(ns_id) for ns_id in row[4] if ns_id]

        policy = {
            "id": decode_bytes(row[0]) if row[0] else None,
            "name": decode_bytes(row[1]) if row[1] else None,
            "type_name": decode_bytes(row[2]) if row[2] else "Governance_Policy",
            "defaults": defaults,
            "governs": governs_list
        }
        policies.append(policy)

    return policies


def export_l4_public_registry(graph_name: str, output_path: Path) -> None:
    """
    Export L4 protocol graph to JSON for mp-lint consumption.
    """
    print(f"🔍 Exporting L4 public registry from '{graph_name}' graph...")

    # Connect to FalkorDB
    db = FalkorDB(
        host=os.getenv("FALKOR_HOST", "localhost"),
        port=int(os.getenv("FALKOR_PORT", "6379"))
    )
    graph_obj = db.select_graph(graph_name)

    # Fetch all data
    print("   📥 Fetching Event_Schema nodes...")
    event_schemas = fetch_event_schemas(graph_obj)
    print(f"      ✅ Found {len(event_schemas)} event schemas")

    print("   📥 Fetching Topic_Namespace nodes...")
    topic_namespaces = fetch_topic_namespaces(graph_obj)
    print(f"      ✅ Found {len(topic_namespaces)} topic namespaces")

    print("   📥 Fetching Governance_Policy nodes...")
    governance_policies = fetch_governance_policies(graph_obj)
    print(f"      ✅ Found {len(governance_policies)} governance policies")

    # Compute graph hash for freshness verification (uses hash_l4_graph.py directly for consistency)
    graph_hash = compute_canonical_hash(graph_name)

    # Build export
    export_data = {
        "meta": {
            "version": "1.0.0",
            "exported_at": datetime.datetime.utcnow().isoformat() + "Z",
            "source_graph": graph_name,
            "graph_hash": graph_hash,
            "exporter": "tools/protocol/export_l4_public.py"
        },
        "event_schemas": event_schemas,
        "topic_namespaces": topic_namespaces,
        "governance_policies": governance_policies,
        "counts": {
            "event_schemas": len(event_schemas),
            "topic_namespaces": len(topic_namespaces),
            "governance_policies": len(governance_policies)
        }
    }

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(export_data, fh, indent=2, ensure_ascii=False)

    print(f"\n✅ Exported L4 public registry to {output_path}")
    print(f"   📊 Summary:")
    print(f"      - Event schemas: {len(event_schemas)}")
    print(f"      - Topic namespaces: {len(topic_namespaces)}")
    print(f"      - Governance policies: {len(governance_policies)}")
    print(f"      - Graph hash: {graph_hash[:16]}...")
    print(f"\n💡 Use this file with mp-lint for schema validation")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export L4 public registry for mp-lint"
    )
    parser.add_argument(
        "--graph",
        default=DEFAULT_GRAPH,
        help="Source graph name (default: protocol)"
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Output JSON file path (default: build/l4_public_registry.json)"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = (_repo_root / args.output).resolve()

    try:
        export_l4_public_registry(args.graph, output_path)
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
