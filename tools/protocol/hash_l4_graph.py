#!/usr/bin/env python3
"""
Compute L4 Protocol Graph Hash

Computes a deterministic hash of the protocol graph state for freshness verification.
Used by mp-lint to detect when exported registry is stale.

The hash is computed from:
- All Event_Schema nodes (name, direction, topic_pattern, version)
- All Topic_Namespace nodes (pattern, description)
- All Governance_Policy nodes (name, defaults)

Usage:
    python tools/protocol/hash_l4_graph.py
    python tools/protocol/hash_l4_graph.py --graph protocol

Returns:
    Prints SHA256 hash to stdout (for use in CI scripts)

Author: Atlas (Infrastructure Engineer)
Date: 2025-10-31
Architecture: mp-lint infrastructure (freshness verification)
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List

from falkordb import FalkorDB


DEFAULT_GRAPH = "protocol"


def decode_bytes(value: Any) -> Any:
    """Decode bytes to string, handle nested structures."""
    if isinstance(value, bytes):
        return value.decode("utf-8")
    elif isinstance(value, dict):
        return {k: decode_bytes(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [decode_bytes(v) for v in value]
    return value


def fetch_event_schema_hashes(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch minimal data from Event_Schema nodes for hashing.
    """
    query = """
    MATCH (es:ProtocolNode)
    WHERE es.type_name = 'Event_Schema'
    RETURN
        es.name as name,
        es.direction as direction,
        es.topic_pattern as topic_pattern,
        es.version as version
    ORDER BY es.name
    """

    result = graph_obj.query(query)
    schemas = []

    for row in result.result_set:
        schema = {
            "name": decode_bytes(row[0]) if row[0] else None,
            "direction": decode_bytes(row[1]) if row[1] else None,
            "topic_pattern": decode_bytes(row[2]) if row[2] else None,
            "version": decode_bytes(row[3]) if row[3] else "1.0",
        }
        schemas.append(schema)

    return schemas


def fetch_topic_namespace_hashes(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch minimal data from Topic_Namespace nodes for hashing.
    """
    query = """
    MATCH (ns:ProtocolNode)
    WHERE ns.type_name = 'Topic_Namespace'
    RETURN
        ns.pattern as pattern,
        ns.description as description
    ORDER BY ns.pattern
    """

    result = graph_obj.query(query)
    namespaces = []

    for row in result.result_set:
        namespace = {
            "pattern": decode_bytes(row[0]) if row[0] else None,
            "description": decode_bytes(row[1]) if row[1] else None,
        }
        namespaces.append(namespace)

    return namespaces


def fetch_governance_policy_hashes(graph_obj) -> List[Dict[str, Any]]:
    """
    Fetch minimal data from Governance_Policy nodes for hashing.
    """
    query = """
    MATCH (gp:ProtocolNode)
    WHERE gp.type_name = 'Governance_Policy'
    RETURN
        gp.name as name,
        gp.defaults as defaults
    ORDER BY gp.name
    """

    result = graph_obj.query(query)
    policies = []

    for row in result.result_set:
        # Parse defaults JSON if it's a string
        defaults_raw = decode_bytes(row[1])
        if isinstance(defaults_raw, str):
            try:
                defaults = json.loads(defaults_raw)
            except json.JSONDecodeError:
                defaults = defaults_raw
        else:
            defaults = defaults_raw

        policy = {
            "name": decode_bytes(row[0]) if row[0] else None,
            "defaults": defaults,
        }
        policies.append(policy)

    return policies


def compute_graph_hash(graph_name: str) -> str:
    """
    Compute deterministic hash of protocol graph state.
    """
    # Connect to FalkorDB
    db = FalkorDB(
        host=os.getenv("FALKOR_HOST", "localhost"),
        port=int(os.getenv("FALKOR_PORT", "6379"))
    )
    graph_obj = db.select_graph(graph_name)

    # Fetch data (already sorted by queries)
    event_schemas = fetch_event_schema_hashes(graph_obj)
    topic_namespaces = fetch_topic_namespace_hashes(graph_obj)
    governance_policies = fetch_governance_policy_hashes(graph_obj)

    # Build canonical representation
    data = {
        "event_schemas": event_schemas,
        "topic_namespaces": topic_namespaces,
        "governance_policies": governance_policies
    }

    # Canonical JSON (sorted keys, no whitespace)
    canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))

    # Compute SHA256
    hash_hex = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    return hash_hex


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute L4 protocol graph hash for freshness verification"
    )
    parser.add_argument(
        "--graph",
        default=DEFAULT_GRAPH,
        help="Source graph name (default: protocol)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show counts and summary"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        if args.verbose:
            print(f"🔍 Computing hash of '{args.graph}' graph...")

        hash_hex = compute_graph_hash(args.graph)

        if args.verbose:
            print(f"✅ Graph hash: {hash_hex}")
        else:
            # Just print hash for use in scripts
            print(hash_hex)

    except Exception as e:
        if args.verbose:
            print(f"❌ Hash computation failed: {e}")
            import traceback
            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
