"""
Export Layer-4 (protocol) type definitions from schema_registry into a snapshot.

The snapshot captures the canonical L4 node and link type specifications
(24 node types + 21 link types) together with a manifest of SHA256 hashes.
If a definition hash changes without a version bump (same id, different hash),
the exporter fails to prevent silent drift.

Usage:
    python tools/protocol/export_protocol_snapshot.py \
        --graph schema_registry \
        --out .build/protocol_snapshot.json \
        --manifest .build/protocol_manifest.txt \
        --schema-root schemas
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

from falkordb import FalkorDB

DEFAULT_GRAPH = "schema_registry"
DEFAULT_OUT = Path(".build/protocol_snapshot.json")
DEFAULT_MANIFEST = Path(".build/protocol_snapshot_manifest.txt")
DEFAULT_SCHEMA_ROOT = Path("schemas")

NODE_TYPE_WHITELIST = {
    "Protocol_Version",
    "Event_Schema",
    "Envelope_Schema",
    "Capability",
    "Tool_Contract",
    "Topic_Namespace",
    "Topic_Route",
    "Signature_Suite",
    "Tenant",
    "Tenant_Key",
    "Governance_Policy",
    "SDK_Release",
    "Sidecar_Release",
    "Adapter_Release",
    "Conformance_Suite",
    "Conformance_Case",
    "Conformance_Result",
    "Deprecation_Notice",
    "Compatibility_Matrix",
    "Transport_Spec",
    "Bus_Instance",
    "Retention_Policy",
    "Security_Profile",
    "Schema_Bundle",
}

LINK_TYPE_WHITELIST = {
    "PUBLISHES_SCHEMA",
    "DEPRECATES",
    "SUPERSEDES",
    "GOVERNS",
    "IMPLEMENTS",
    "SUPPORTS",
    "ADAPTER_SUPPORTS",
    "COMPATIBLE_WITH",
    "REQUIRES_SIG",
    "SIGNED_WITH",
    "ASSIGNED_TO_TENANT",
    "ROUTES_OVER",
    "HOSTED_ON",
    "SERVES_NAMESPACE",
    "APPLIES_TO",
    "DEFAULTS_FOR",
    "BUNDLES",
    "TESTS",
    "CERTIFIES_CONFORMANCE",
    "MAPS_TO_TOPIC",
    "CONFORMS_TO",
}

_repo_root = Path(__file__).resolve().parents[2]


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_sha(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def resolve_schema_path(schema_uri: str, schema_root: Path) -> Path:
    uri = schema_uri.strip()
    if uri.startswith("mind://"):
        relative = uri.replace("mind://", "", 1)
        return schema_root / relative
    if uri.startswith("file://"):
        return Path(uri[7:])
    candidate = Path(uri)
    if candidate.is_absolute():
        return candidate
    return schema_root / candidate


def compute_schema_hash(node_props: Dict[str, Any], schema_root: Path) -> Optional[str]:
    schema_uri = node_props.get("schema_uri")
    if not schema_uri:
        return None
    path = resolve_schema_path(schema_uri, schema_root)
    if not path.exists():
        raise FileNotFoundError(f"Schema URI '{schema_uri}' resolved to '{path}' which does not exist.")
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    canonical = canonical_json(data)
    sha = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    stored = node_props.get("schema_hash")
    if stored and stored != sha:
        raise ValueError(
            f"Schema hash mismatch for {node_props.get('id','<unknown>')}: stored={stored}, computed={sha}"
        )
    return sha


def fetch_node_type_schemas(graph: str) -> List[Dict[str, Any]]:
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=int(os.getenv("FALKOR_PORT", "6379")))
    g = db.select_graph(graph)
    result = g.query(
        """
        MATCH (n:NodeTypeSchema)
        WHERE coalesce(n.level,'') IN ['l4','L4']
        RETURN n
        ORDER BY n.type_name
        """
    )
    nodes: List[Dict[str, Any]] = []
    for (node_obj,) in result.result_set:
        type_name = node_obj.properties.get("type_name")
        if type_name not in NODE_TYPE_WHITELIST:
            continue
        nodes.append(
            {
                "id": f"schema_registry/NodeTypeSchema/{type_name}",
                "type_name": type_name,
                "level": node_obj.properties.get("level"),
                "category": node_obj.properties.get("category"),
                "description": node_obj.properties.get("description"),
                "version": node_obj.properties.get("version"),
                "required": fetch_field_schemas(g, type_name, "HAS_REQUIRED_FIELD"),
                "optional": fetch_field_schemas(g, type_name, "HAS_OPTIONAL_FIELD"),
            }
        )
    return nodes


def fetch_field_schemas(graph, type_name: str, relationship: str) -> List[Dict[str, Any]]:
    result = graph.query(
        f"""
        MATCH (:NodeTypeSchema {{type_name:$type}})-[:{relationship}]->(f:FieldSchema)
        RETURN f
        ORDER BY f.name
        """,
        params={"type": type_name},
    )
    fields: List[Dict[str, Any]] = []
    for (field_obj,) in result.result_set:
        props = dict(field_obj.properties)
        if isinstance(props.get("enum_values"), str):
            try:
                props["enum_values"] = json.loads(props["enum_values"])
            except json.JSONDecodeError:
                pass
        fields.append(props)
    return fields


def fetch_link_type_schemas(graph: str) -> List[Dict[str, Any]]:
    db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=int(os.getenv("FALKOR_PORT", "6379")))
    g = db.select_graph(graph)
    result = g.query(
        """
        MATCH (l:LinkTypeSchema)
        WHERE coalesce(l.level,'') IN ['l4','L4']
        RETURN l
        ORDER BY l.type_name
        """
    )
    links: List[Dict[str, Any]] = []
    for (link_obj,) in result.result_set:
        type_name = link_obj.properties.get("type_name")
        if type_name not in LINK_TYPE_WHITELIST:
            continue
        links.append(
            {
                "id": f"schema_registry/LinkTypeSchema/{type_name}",
                "type_name": type_name,
                "level": link_obj.properties.get("level"),
                "category": link_obj.properties.get("category"),
                "description": link_obj.properties.get("description"),
                "required": fetch_link_fields(g, type_name, "HAS_REQUIRED_FIELD"),
                "optional": fetch_link_fields(g, type_name, "HAS_OPTIONAL_FIELD"),
                "detection_pattern": link_obj.properties.get("detection_pattern"),
                "detection_logic": _decode_json(link_obj.properties.get("detection_logic")),
                "task_template": link_obj.properties.get("task_template"),
                "mechanisms": _decode_json(link_obj.properties.get("mechanisms")),
            }
        )
    return links


def fetch_link_fields(graph, type_name: str, relationship: str) -> List[Dict[str, Any]]:
    result = graph.query(
        f"""
        MATCH (:LinkTypeSchema {{type_name:$type}})-[:{relationship}]->(f:FieldSchema)
        RETURN f
        ORDER BY f.name
        """,
        params={"type": type_name},
    )
    fields: List[Dict[str, Any]] = []
    for (field_obj,) in result.result_set:
        props = dict(field_obj.properties)
        if isinstance(props.get("enum_values"), str):
            try:
                props["enum_values"] = json.loads(props["enum_values"])
            except json.JSONDecodeError:
                pass
        fields.append(props)
    return fields


def load_existing_manifest(manifest_path: Path) -> Dict[str, str]:
    if not manifest_path.exists():
        return {}
    mapping: Dict[str, str] = {}
    with manifest_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            sha, node_id = line.split(" ", 1)
            mapping[node_id] = sha
    return mapping


def export_snapshot(
    graph: str,
    out_path: Path,
    manifest_path: Path,
    schema_root: Path,
) -> None:
    nodes = fetch_node_type_schemas(graph)
    links = fetch_link_type_schemas(graph)

    manifest_entries: List[Tuple[str, str]] = []
    enriched_nodes: List[Dict[str, Any]] = []
    enriched_links: List[Dict[str, Any]] = []
    existing_manifest = load_existing_manifest(manifest_path)

    for props in nodes:
        entry = dict(props)
        schema_sha = compute_schema_hash(entry, schema_root)
        if schema_sha:
            entry["schema_hash"] = schema_sha
        entry["layer"] = "L4"
        sha = compute_sha(entry)
        entry["content_sha"] = sha
        _enforce_no_drift(existing_manifest, entry["id"], sha)
        manifest_entries.append((sha, entry["id"]))
        enriched_nodes.append(entry)

    for props in links:
        entry = dict(props)
        entry["layer"] = "L4"
        sha = compute_sha(entry)
        entry["content_sha"] = sha
        _enforce_no_drift(existing_manifest, entry["id"], sha)
        manifest_entries.append((sha, entry["id"]))
        enriched_links.append(entry)

    manifest_entries.sort(key=lambda item: item[1])

    snapshot = {
        "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "graph": graph,
        "node_count": len(enriched_nodes),
        "link_count": len(enriched_links),
        "nodes": enriched_nodes,
        "links": enriched_links,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as fh:
        for sha, node_id in manifest_entries:
            fh.write(f"{sha} {node_id}\n")

    print(
        f"[OK] Exported {len(enriched_nodes)} node types and {len(enriched_links)} link types "
        f"from '{graph}' to '{out_path}'. Manifest written to '{manifest_path}'."
    )


def _decode_json(value: Optional[Any]) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _enforce_no_drift(existing_manifest: Dict[str, str], node_id: str, new_sha: str) -> None:
    previous = existing_manifest.get(node_id)
    if previous and previous != new_sha:
        raise ValueError(
            f"Snapshot drift detected for {node_id}: previous hash {previous} vs {new_sha}. "
            "Bump the semver before updating this definition."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Layer-4 schema_registry snapshot.")
    parser.add_argument("--graph", default=DEFAULT_GRAPH, help="Source graph name (default: schema_registry)")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Path to snapshot JSON output")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Path to manifest output")
    parser.add_argument("--schema-root", default=str(DEFAULT_SCHEMA_ROOT), help="Root directory for schema files")
    parser.add_argument("--offline-bundle", help="Optional JSON bundle to use instead of querying FalkorDB")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_path = Path(args.out).resolve()
    manifest_path = Path(args.manifest).resolve()
    schema_root = (_repo_root / args.schema_root).resolve()

    if args.offline_bundle:
        bundle_path = Path(args.offline_bundle)
        snapshot = json.loads(bundle_path.read_text())
        manifest_entries = [
            (entry["content_sha"], entry["id"])
            for entry in snapshot.get("nodes", []) + snapshot.get("links", [])
        ]
        _validate_offline_against_manifest(snapshot, manifest_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            json.dump(snapshot, fh, indent=2, ensure_ascii=False)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with manifest_path.open("w", encoding="utf-8") as fh:
            for sha, node_id in manifest_entries:
                fh.write(f"{sha} {node_id}\n")
        print(f"[OK] Offline bundle copied to '{out_path}'.")
        return

    export_snapshot(args.graph, out_path, manifest_path, schema_root)


def _validate_offline_against_manifest(snapshot: Dict[str, Any], manifest_path: Path) -> None:
    existing = load_existing_manifest(manifest_path)
    for entry in snapshot.get("nodes", []) + snapshot.get("links", []):
        node_id = entry["id"]
        sha = entry.get("content_sha")
        if not sha:
            sha = compute_sha(entry)
        _enforce_no_drift(existing, node_id, sha)


if __name__ == "__main__":
    main()
