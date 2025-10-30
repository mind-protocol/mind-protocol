"""
Seed the dedicated `protocol` graph with Layer-4 runtime data from a snapshot.

This script consumes the deterministic snapshot produced by
`export_protocol_snapshot.py`, validates manifest hashes, and applies the
changes into the target graph using idempotent upserts. By default it performs
a dry-run (`--plan`) and prints the diff; use `--apply` to execute the changes.

Usage examples:
    python tools/protocol/seed_protocol_graph.py --snapshot .build/protocol_snapshot.json --plan
    python tools/protocol/seed_protocol_graph.py --snapshot .build/protocol_snapshot.json --apply
    python tools/protocol/seed_protocol_graph.py --snapshot snapshot.json --apply --force

Rules:
- Nodes are identified by immutable `id` (string). Any hash mismatch is treated
  as an error unless `--force` is provided, in which case the node is replaced.
- Edges are recreated per `(source_id, type)` set to avoid duplicates.
- Target graph defaults to `protocol`; a unique index on `ProtocolNode(id)` is
  created if missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set

from falkordb import FalkorDB
from redis.exceptions import ResponseError

DEFAULT_GRAPH = "protocol"
DEFAULT_SNAPSHOT = Path(".build/protocol_snapshot.json")
DEFAULT_MANIFEST = Path(".build/protocol_snapshot_manifest.txt")
NODE_LABEL = "ProtocolNode"
LAYER = "L4"


def load_snapshot(snapshot_path: Path) -> Dict[str, Any]:
    with snapshot_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_manifest(manifest_path: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not manifest_path.exists():
        return mapping
    with manifest_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            sha, node_id = line.split(" ", 1)
            mapping[node_id] = sha
    return mapping


def verify_manifest(snapshot: Dict[str, Any], manifest: Dict[str, str]) -> None:
    if not manifest:
        return
    for entry in snapshot.get("nodes", []):
        _assert_manifest_entry(entry, manifest)
    for entry in snapshot.get("edges", []):
        entry_id = f"{entry['source']}::{entry['type']}::{entry['target']}"
        content_sha = entry.get("content_sha")
        if not content_sha:
            content_sha = compute_edge_hash(entry)
        expected = manifest.get(entry_id)
        if expected and expected != content_sha:
            raise ValueError(
                f"Manifest hash mismatch for edge {entry_id}: expected {expected}, snapshot has {content_sha}."
            )


def _assert_manifest_entry(entry: Dict[str, Any], manifest: Dict[str, str]) -> None:
    node_id = entry["id"]
    content_sha = entry.get("content_sha")
    if not content_sha:
        raise ValueError(f"Snapshot node {node_id} missing content_sha.")
    expected = manifest.get(node_id)
    if expected is None:
        raise ValueError(f"Manifest missing entry for node {node_id}.")
    if expected != content_sha:
        raise ValueError(
            f"Manifest hash mismatch for {node_id}: expected {expected}, snapshot has {content_sha}."
        )


def compute_edge_hash(edge: Dict[str, Any]) -> str:
    payload = {
        "source": edge["source"],
        "target": edge["target"],
        "type": edge["type"],
        "properties": edge.get("properties", {}),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def connect_graph(graph: str):
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=int(os.getenv("FALKOR_PORT", "6379")))
    return db.select_graph(graph)


def ensure_indexes(graph) -> None:
    try:
        graph.query(f"CREATE INDEX FOR (n:{NODE_LABEL}) ON (n.id)")
    except ResponseError as exc:
        msg = str(exc).lower()
        if "already exists" not in msg and "already indexed" not in msg:
            raise
    try:
        graph.query(f"CREATE INDEX FOR (n:{NODE_LABEL}) ON (n.type_name)")
    except ResponseError as exc:
        msg = str(exc).lower()
        if "already exists" not in msg and "already indexed" not in msg:
            raise


def fetch_existing_nodes(graph) -> Dict[str, Dict[str, Any]]:
    result = graph.query(f"MATCH (n:{NODE_LABEL}) RETURN n.id, n")
    existing: Dict[str, Dict[str, Any]] = {}
    for node_id, node_obj in result.result_set:

        properties = dict(node_obj.properties)
        properties["labels"] = [label for label in (node_obj.labels or []) if label != NODE_LABEL]
        existing[node_id] = properties
    return existing


def fetch_existing_edges(graph) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    result = graph.query(
        f"""
        MATCH (s:{NODE_LABEL})-[r]->(t:{NODE_LABEL})
        RETURN s.id, TYPE(r), t.id, r
        """
    )
    edges: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for src_id, rel_type, dst_id, edge_obj in result.result_set:
        edges[(src_id, rel_type, dst_id)] = dict(edge_obj.properties)
    return edges


def diff_nodes(snapshot_nodes: List[Dict[str, Any]], existing_nodes: Dict[str, Dict[str, Any]]):
    to_create = []
    conflicts = []
    untouched = []
    for node in snapshot_nodes:
        node_id = node["id"]
        content_sha = node.get("content_sha")
        existing = existing_nodes.get(node_id)
        if not existing:
            to_create.append(node)
        else:
            if content_sha and existing.get("content_sha") != content_sha:
                conflicts.append((node, existing))
            else:
                untouched.append(node)
    return to_create, conflicts, untouched


def diff_edges(snapshot_edges: List[Dict[str, Any]], existing_edges: Dict[Tuple[str, str, str], Dict[str, Any]]):
    to_create = []
    to_delete_keys: Set[Tuple[str, str]] = set()
    existing_keys = set(existing_edges.keys())
    snapshot_keys = set()

    for edge in snapshot_edges:
        key = (edge["source"], edge["type"], edge["target"])
        snapshot_keys.add(key)
        if key not in existing_keys or existing_edges[key] != edge.get("properties", {}):
            to_create.append(edge)
        to_delete_keys.add((edge["source"], edge["type"]))

    to_delete = []
    for (src, rel_type, dst), props in existing_edges.items():
        if (src, rel_type) in to_delete_keys and (src, rel_type, dst) not in snapshot_keys:
            to_delete.append((src, rel_type, dst))

    return to_create, to_delete


def apply_nodes(graph, nodes: List[Dict[str, Any]], *, force: bool, conflicts: List[Tuple[Dict[str, Any], Dict[str, Any]]]) -> None:
    if conflicts and not force:
        conflict_ids = ", ".join(node["id"] for node, _ in conflicts)
        raise ValueError(
            f"Content hash mismatch for existing nodes: {conflict_ids}. Use --force to replace."
        )

    for node, _ in conflicts:
        node_id = node["id"]
        graph.query(
            f"""
            MATCH (n:{NODE_LABEL} {{id: $id}})
            DETACH DELETE n
            """,
            params={"id": node_id},
        )
    payload = list(nodes) + [node for node, _ in conflicts]
    created_ids: List[str] = []
    try:
        for node in payload:
            labels = node.get("_labels", [])
            props = {k: v for k, v in node.items() if k not in {"_labels"}}
            props.setdefault("layer", LAYER)
            normalised: Dict[str, Any] = {}
            for key, value in props.items():
                if isinstance(value, dict):
                    normalised[key] = json.dumps(value, sort_keys=True)
                elif isinstance(value, list):
                    if any(isinstance(item, (dict, list)) for item in value):
                        normalised[key] = json.dumps(value, sort_keys=True)
                    else:
                        normalised[key] = value
                else:
                    normalised[key] = value
            set_clause = ", ".join(f"n.{key} = ${key}" for key in props.keys())
            params = dict(normalised)
            label_clause = ":".join([NODE_LABEL] + labels)
            graph.query(
                f"""
                CREATE (n:{label_clause})
                SET {set_clause}
                """,
                params=params,
            )
            created_ids.append(node["id"])
    except Exception:
        for node_id in created_ids:
            graph.query(
                f"""
                MATCH (n:{NODE_LABEL} {{id:$id}})
                DETACH DELETE n
                """,
                params={"id": node_id},
            )
        raise


def apply_edges(graph, to_create: List[Dict[str, Any]], to_delete: List[Tuple[str, str, str]]) -> None:
    created_edges: List[Tuple[str, str, str]] = []
    try:
        for src, rel_type, dst in to_delete:
            graph.query(
                f"""
                MATCH (s:{NODE_LABEL} {{id:$src}})-[r:{rel_type}]->(t:{NODE_LABEL} {{id:$dst}})
                DELETE r
                """,
                params={"src": src, "dst": dst},
            )

        for edge in to_create:
            src = edge["source"]
            dst = edge["target"]
            rel_type = edge["type"]
            properties = edge.get("properties") or {}
            if properties:
                set_clause = ", ".join(f"r.{k} = ${k}" for k in properties.keys())
                params = {"src": src, "dst": dst, **properties}
                graph.query(
                    f"""
                    MATCH (s:{NODE_LABEL} {{id:$src}}), (t:{NODE_LABEL} {{id:$dst}})
                    CREATE (s)-[r:{rel_type}]->(t)
                    SET {set_clause}
                    """,
                    params=params,
                )
            else:
                graph.query(
                    f"""
                    MATCH (s:{NODE_LABEL} {{id:$src}}), (t:{NODE_LABEL} {{id:$dst}})
                    CREATE (s)-[:{rel_type}]->(t)
                    """,
                    params={"src": src, "dst": dst},
                )
            created_edges.append((src, rel_type, dst))
    except Exception:
        for src, rel_type, dst in created_edges:
            graph.query(
                f"""
                MATCH (s:{NODE_LABEL} {{id:$src}})-[r:{rel_type}]->(t:{NODE_LABEL} {{id:$dst}})
                DELETE r
                """,
                params={"src": src, "dst": dst},
            )
        raise


def run(snapshot_path: Path, manifest_path: Path, graph_name: str, plan: bool, apply: bool, force: bool) -> None:
    snapshot = load_snapshot(snapshot_path)
    manifest = load_manifest(manifest_path)
    verify_manifest(snapshot, manifest)

    graph = connect_graph(graph_name)
    ensure_indexes(graph)

    existing_nodes = fetch_existing_nodes(graph)
    existing_edges = fetch_existing_edges(graph)

    to_create_nodes, conflicts, untouched_nodes = diff_nodes(snapshot.get("nodes", []), existing_nodes)
    to_create_edges, to_delete_edges = diff_edges(snapshot.get("edges", []), existing_edges)

    print(f"[PLAN] Nodes to create: {len(to_create_nodes)}")
    print(f"[PLAN] Node conflicts: {len(conflicts)}")
    print(f"[PLAN] Nodes untouched: {len(untouched_nodes)}")
    print(f"[PLAN] Edges to create/update: {len(to_create_edges)}")
    print(f"[PLAN] Edges to delete: {len(to_delete_edges)}")

    if not apply:
        print("[INFO] Dry-run complete. Use --apply to execute changes.")
        return

    apply_nodes(graph, to_create_nodes, force=force, conflicts=conflicts)
    apply_edges(graph, to_create_edges, to_delete_edges)

    print("[OK] Protocol graph seeded successfully.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed the protocol (L4) graph from snapshot.")
    parser.add_argument("--snapshot", default=str(DEFAULT_SNAPSHOT), help=f"Path to snapshot JSON (default: {DEFAULT_SNAPSHOT})")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help=f"Path to manifest file (default: {DEFAULT_MANIFEST})")
    parser.add_argument("--graph", default=DEFAULT_GRAPH, help=f"Target graph name (default: {DEFAULT_GRAPH})")
    parser.add_argument("--plan", action="store_true", help="Only print the plan (default if --apply not set)")
    parser.add_argument("--apply", action="store_true", help="Apply the snapshot to the target graph.")
    parser.add_argument("--force", action="store_true", help="Allow replacements when content hashes differ.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plan = args.plan or not args.apply
    run(
        snapshot_path=Path(args.snapshot),
        manifest_path=Path(args.manifest),
        graph_name=args.graph,
        plan=plan,
        apply=args.apply,
        force=args.force,
    )


if __name__ == "__main__":
    main()
