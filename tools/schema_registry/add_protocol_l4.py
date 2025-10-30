"""
Add/merge Layer-4 (Protocol) node & link schemas into FalkorDB schema_registry.

The canonical protocol schemas reside inside the `schema_registry` graph. This
script ingests the Layer-4 definitions (protocol grammar, governance artefacts,
runtime infrastructure) so that downstream tooling (Complete Type Reference,
SDK generators, adapters) can use the database as the source of truth.

Usage:
    python tools/schema_registry/add_protocol_l4.py \
        --host localhost --port 6379 --version v4.0

The script is idempotent: it MERGEs NodeTypeSchema / LinkTypeSchema nodes,
clears previous FieldSchema attachments for those types, and recreates the
required/optional field nodes before setting metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List

from falkordb import FalkorDB


PROTOCOL_NODE_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type_name": "Protocol_Version",
        "level": "l4",
        "category": "protocol",
        "description": "Semantic version of the protocol specification.",
        "required": [
            {"name": "semver", "type": "string", "description": "Semantic version identifier (e.g. 1.1.0)"},
            {"name": "released_at", "type": "datetime", "description": "Release timestamp"},
            {"name": "summary", "type": "string", "description": "Release highlights"},
        ],
        "optional": [],
    },
    {
        "type_name": "Event_Schema",
        "level": "l4",
        "category": "protocol",
        "description": "JSON schema describing a protocol event (inject or broadcast).",
        "required": [
            {"name": "name", "type": "string", "description": "Event name (e.g. membrane.inject)"},
            {"name": "version", "type": "string", "description": "Schema version string"},
            {"name": "direction", "type": "enum", "enum_values": ["inject", "broadcast"], "description": "Flow direction"},
            {"name": "topic_pattern", "type": "string", "description": "Topic pattern used on the bus"},
            {"name": "schema_uri", "type": "string", "description": "Location of the JSON schema"},
            {"name": "schema_hash", "type": "string", "description": "SHA256 of the JSON schema"},
        ],
        "optional": [],
    },
    {
        "type_name": "Envelope_Schema",
        "level": "l4",
        "category": "protocol",
        "description": "Schema for the transport envelope (metadata, signature, TTL).",
        "required": [
            {"name": "name", "type": "string", "description": "Envelope schema name"},
            {"name": "version", "type": "string", "description": "Envelope schema version"},
            {"name": "fields", "type": "array", "description": "Canonical fields with constraints"},
            {"name": "signature_path", "type": "string", "description": "JSON path to signature payload (e.g. $.sig)"},
        ],
        "optional": [],
    },
    {
        "type_name": "Capability",
        "level": "l4",
        "category": "protocol",
        "description": "Logical capability exposed through the protocol.",
        "required": [
            {"name": "capability", "type": "string", "description": "Capability identifier (e.g. git.commit)"},
            {"name": "input_schema_ref", "type": "string", "description": "Reference to input Event_Schema"},
            {"name": "output_schema_ref", "type": "string", "description": "Reference to output Event_Schema"},
        ],
        "optional": [],
    },
    {
        "type_name": "Tool_Contract",
        "level": "l4",
        "category": "protocol",
        "description": "Contract describing a tool's capabilities and schemas.",
        "required": [
            {"name": "tool_id", "type": "string", "description": "Tool identifier"},
            {"name": "capabilities", "type": "array", "description": "Capabilities served by the tool"},
            {"name": "args_schema_ref", "type": "string", "description": "Reference to arguments schema"},
            {"name": "result_schema_ref", "type": "string", "description": "Reference to result schema"},
        ],
        "optional": [],
    },
    {
        "type_name": "Topic_Namespace",
        "level": "l4",
        "category": "protocol",
        "description": "Bus namespace definition (wildcard patterns, scope).",
        "required": [
            {"name": "pattern", "type": "string", "description": "Topic pattern (e.g. org/{org_id}/broadcast/*)"},
            {"name": "scope", "type": "enum", "enum_values": ["org", "global"], "description": "Namespace scope"},
            {"name": "description", "type": "string", "description": "Purpose and usage notes"},
        ],
        "optional": [],
    },
    {
        "type_name": "Topic_Route",
        "level": "l4",
        "category": "infra",
        "description": "Documentation of logical routing between namespaces and components.",
        "required": [
            {"name": "from_namespace", "type": "string", "description": "Source namespace pattern"},
            {"name": "to_component", "type": "string", "description": "Destination component (e.g. orchestrator)"},
            {"name": "routing_notes", "type": "string", "description": "Routing behaviour description"},
        ],
        "optional": [],
    },
    {
        "type_name": "Signature_Suite",
        "level": "l4",
        "category": "protocol",
        "description": "Cryptographic suite authorised for protocol signatures.",
        "required": [
            {"name": "algo", "type": "enum", "enum_values": ["ed25519"], "description": "Signature algorithm"},
            {"name": "pubkey_encoding", "type": "enum", "enum_values": ["base64", "hex"], "description": "Public key encoding"},
            {"name": "signature_field", "type": "string", "description": "Path to signature field (e.g. sig.signature)"},
        ],
        "optional": [],
    },
    {
        "type_name": "Tenant",
        "level": "l4",
        "category": "governance",
        "description": "Protocol-level tenant (organization identity).",
        "required": [
            {"name": "org_id", "type": "string", "description": "Tenant identifier"},
            {"name": "display_name", "type": "string", "description": "Human readable name"},
        ],
        "optional": [],
    },
    {
        "type_name": "Tenant_Key",
        "level": "l4",
        "category": "governance",
        "description": "Key material associated with a tenant.",
        "required": [
            {"name": "org_id", "type": "string", "description": "Tenant identifier"},
            {"name": "key_version", "type": "int", "description": "Sequential key version"},
            {"name": "pubkey", "type": "string", "description": "Public key material"},
            {"name": "created_at", "type": "datetime", "description": "Creation timestamp"},
            {"name": "rotated_at", "type": "datetime", "description": "Rotation timestamp (nullable)"},
        ],
        "optional": [],
    },
    {
        "type_name": "Governance_Policy",
        "level": "l4",
        "category": "governance",
        "description": "Protocol policy (lanes, backpressure, governance defaults).",
        "required": [
            {"name": "name", "type": "string", "description": "Policy identifier"},
            {"name": "policy_doc_uri", "type": "string", "description": "URI to policy documentation"},
            {"name": "defaults", "type": "object", "description": "Default settings (e.g. ack_policy)"},
        ],
        "optional": [],
    },
    {
        "type_name": "SDK_Release",
        "level": "l4",
        "category": "artifact",
        "description": "Release metadata for SDK distributions.",
        "required": [
            {"name": "language", "type": "enum", "enum_values": ["typescript", "python", "go"], "description": "SDK language"},
            {"name": "package_name", "type": "string", "description": "Package identifier"},
            {"name": "version", "type": "string", "description": "SDK version"},
            {"name": "commit_hash", "type": "string", "description": "Commit hash for release"},
            {"name": "schema_min_version", "type": "string", "description": "Minimum compatible schema version"},
        ],
        "optional": [],
    },
    {
        "type_name": "Sidecar_Release",
        "level": "l4",
        "category": "artifact",
        "description": "Release metadata for the Sidecar client.",
        "required": [
            {"name": "image_ref", "type": "string", "description": "Container image reference"},
            {"name": "version", "type": "string", "description": "Release version"},
            {"name": "features", "type": "array", "description": "Feature list (buffer_offline, replay, etc.)"},
            {"name": "schema_min_version", "type": "string", "description": "Minimum compatible schema version"},
        ],
        "optional": [],
    },
    {
        "type_name": "Adapter_Release",
        "level": "l4",
        "category": "artifact",
        "description": "Release metadata for provider adapters (Claude/Codex/Gemini).",
        "required": [
            {"name": "provider", "type": "enum", "enum_values": ["claude", "codex", "gemini", "other"], "description": "Provider identifier"},
            {"name": "version", "type": "string", "description": "Adapter version"},
            {"name": "features", "type": "array", "description": "Supported feature list"},
        ],
        "optional": [],
    },
    {
        "type_name": "Conformance_Suite",
        "level": "l4",
        "category": "protocol",
        "description": "Suite of protocol conformance tests.",
        "required": [
            {"name": "suite_id", "type": "string", "description": "Suite identifier"},
            {"name": "cases_count", "type": "int", "description": "Number of test cases"},
            {"name": "schema_set_ref", "type": "string", "description": "Reference to schema set"},
        ],
        "optional": [],
    },
    {
        "type_name": "Conformance_Case",
        "level": "l4",
        "category": "protocol",
        "description": "Individual conformance test case.",
        "required": [
            {"name": "case_id", "type": "string", "description": "Case identifier"},
            {"name": "description", "type": "string", "description": "Case description"},
            {"name": "expected", "type": "enum", "enum_values": ["pass", "fail", "warn"], "description": "Expected outcome"},
        ],
        "optional": [],
    },
    {
        "type_name": "Conformance_Result",
        "level": "l4",
        "category": "protocol",
        "description": "Execution result for a conformance suite.",
        "required": [
            {"name": "suite_id", "type": "string", "description": "Suite identifier"},
            {"name": "target_release", "type": "string", "description": "Target release identifier (e.g. sdk.ts@1.2.0)"},
            {"name": "pass_rate", "type": "float", "description": "Pass ratio (0..1)"},
            {"name": "failing_cases", "type": "array", "description": "Identifiers of failing cases"},
        ],
        "optional": [],
    },
    {
        "type_name": "Deprecation_Notice",
        "level": "l4",
        "category": "governance",
        "description": "Notice announcing protocol deprecation of schema or release.",
        "required": [
            {"name": "target_kind", "type": "enum", "enum_values": ["Event_Schema", "Capability", "SDK_Release", "Sidecar_Release"], "description": "Kind being deprecated"},
            {"name": "target_ref", "type": "string", "description": "Reference to deprecated element"},
            {"name": "effective_at", "type": "datetime", "description": "Effective timestamp"},
            {"name": "end_of_support", "type": "datetime", "description": "End-of-support timestamp"},
        ],
        "optional": [],
    },
    {
        "type_name": "Compatibility_Matrix",
        "level": "l4",
        "category": "protocol",
        "description": "Compatibility matrix between releases and schemas.",
        "required": [
            {"name": "matrix", "type": "array", "description": "Rows describing compatibility states"},
            {"name": "generated_at", "type": "datetime", "description": "Generation timestamp"},
        ],
        "optional": [],
    },
    {
        "type_name": "Transport_Spec",
        "level": "l4",
        "category": "infra",
        "description": "Transport semantics (WS/NATS/Kafka) for the bus.",
        "required": [
            {"name": "type", "type": "enum", "enum_values": ["ws", "nats", "kafka"], "description": "Transport type"},
            {"name": "qos", "type": "object", "description": "Quality-of-service settings (durable, acks, etc.)"},
        ],
        "optional": [],
    },
    {
        "type_name": "Bus_Instance",
        "level": "l4",
        "category": "infra",
        "description": "Concrete bus instance available to tenants.",
        "required": [
            {"name": "endpoint", "type": "string", "description": "Endpoint URI"},
            {"name": "transport_ref", "type": "string", "description": "Reference to Transport_Spec"},
            {"name": "retention_policy_ref", "type": "string", "description": "Reference to Retention_Policy"},
        ],
        "optional": [],
    },
    {
        "type_name": "Retention_Policy",
        "level": "l4",
        "category": "protocol",
        "description": "Retention and de-duplication policy for the bus.",
        "required": [
            {"name": "name", "type": "string", "description": "Policy name"},
            {"name": "time_limit", "type": "duration", "description": "Retention duration (e.g. 3d)"},
            {"name": "size_limit_mb", "type": "int", "description": "Storage limit in megabytes"},
            {"name": "dedupe_window_ms", "type": "int", "description": "Deduplication window in milliseconds"},
        ],
        "optional": [],
    },
    {
        "type_name": "Security_Profile",
        "level": "l4",
        "category": "protocol",
        "description": "Security requirements for namespaces or schemas.",
        "required": [
            {"name": "profile_name", "type": "string", "description": "Profile identifier"},
            {"name": "required_signature_suites", "type": "array", "description": "Allowed signature suites"},
            {"name": "min_key_length_bits", "type": "int", "description": "Minimum key length in bits"},
        ],
        "optional": [],
    },
    {
        "type_name": "Schema_Bundle",
        "level": "l4",
        "category": "artifact",
        "description": "Versioned archive of protocol schemas.",
        "required": [
            {"name": "bundle_uri", "type": "string", "description": "URI to bundle (tar/zip)"},
            {"name": "bundle_hash", "type": "string", "description": "Hash of bundle contents"},
            {"name": "contains", "type": "array", "description": "List of schema refs included (name@version)"},
        ],
        "optional": [],
    },
]


PROTOCOL_LINK_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type_name": "PUBLISHES_SCHEMA",
        "level": "l4",
        "category": "protocol",
        "description": "Protocol version publishes an event or envelope schema.",
        "required": [
            {"name": "release_notes_uri", "type": "string", "description": "Link to release notes"},
        ],
        "optional": [],
    },
    {
        "type_name": "DEPRECATES",
        "level": "l4",
        "category": "governance",
        "description": "Marks that one element deprecates or replaces an older one.",
        "required": [
            {"name": "grace_period_days", "type": "int", "description": "Grace period before removal"},
        ],
        "optional": [],
    },
    {
        "type_name": "SUPERSEDES",
        "level": "l4",
        "category": "artifact",
        "description": "New release supersedes an older release.",
        "required": [
            {"name": "compat_maintained", "type": "boolean", "description": "Whether backwards compatibility is maintained"},
        ],
        "optional": [],
    },
    {
        "type_name": "GOVERNS",
        "level": "l4",
        "category": "protocol",
        "description": "Schema or policy governs a capability or namespace.",
        "required": [
            {"name": "governance_scope", "type": "enum", "enum_values": ["schema", "policy"], "description": "Scope of governance"},
        ],
        "optional": [],
    },
    {
        "type_name": "IMPLEMENTS",
        "level": "l4",
        "category": "artifact",
        "description": "SDK release implements a schema or capability.",
        "required": [
            {"name": "coverage", "type": "float", "description": "Coverage ratio (0..1)"},
        ],
        "optional": [],
    },
    {
        "type_name": "SUPPORTS",
        "level": "l4",
        "category": "artifact",
        "description": "Sidecar release supports a schema or transport.",
        "required": [
            {"name": "maturity", "type": "enum", "enum_values": ["alpha", "beta", "ga"], "description": "Support maturity level"},
        ],
        "optional": [],
    },
    {
        "type_name": "ADAPTER_SUPPORTS",
        "level": "l4",
        "category": "artifact",
        "description": "Adapter release exposes a capability.",
        "required": [
            {"name": "latency_hint_ms", "type": "int", "description": "Latency hint in milliseconds"},
        ],
        "optional": [],
    },
    {
        "type_name": "COMPATIBLE_WITH",
        "level": "l4",
        "category": "protocol",
        "description": "Declares compatibility between releases.",
        "required": [
            {"name": "level", "type": "enum", "enum_values": ["schema", "runtime"], "description": "Compatibility level"},
            {"name": "status", "type": "enum", "enum_values": ["ok", "warn", "no"], "description": "Compatibility status"},
        ],
        "optional": [],
    },
    {
        "type_name": "REQUIRES_SIG",
        "level": "l4",
        "category": "protocol",
        "description": "Event schema requires a specific signature suite.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "SIGNED_WITH",
        "level": "l4",
        "category": "governance",
        "description": "Tenant key uses a signature suite.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "ASSIGNED_TO_TENANT",
        "level": "l4",
        "category": "governance",
        "description": "Associates tenant key with tenant identity.",
        "required": [
            {"name": "key_version", "type": "int", "description": "Version of key assignment"},
        ],
        "optional": [],
    },
    {
        "type_name": "ROUTES_OVER",
        "level": "l4",
        "category": "infra",
        "description": "Namespace or route uses a transport specification.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "HOSTED_ON",
        "level": "l4",
        "category": "infra",
        "description": "Bus instance is hosted on a transport spec.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "SERVES_NAMESPACE",
        "level": "l4",
        "category": "infra",
        "description": "Bus instance serves a topic namespace.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "APPLIES_TO",
        "level": "l4",
        "category": "protocol",
        "description": "Retention policy applies to namespace or schema.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "DEFAULTS_FOR",
        "level": "l4",
        "category": "protocol",
        "description": "Security profile provides defaults for namespace or schema.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "BUNDLES",
        "level": "l4",
        "category": "artifact",
        "description": "Schema bundle contains specific schemas.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "TESTS",
        "level": "l4",
        "category": "protocol",
        "description": "Conformance suite covers specific schemas or capabilities.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "CERTIFIES_CONFORMANCE",
        "level": "l4",
        "category": "protocol",
        "description": "Conformance result certifies a release.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "MAPS_TO_TOPIC",
        "level": "l4",
        "category": "protocol",
        "description": "Event schema maps to a topic namespace.",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "CONFORMS_TO",
        "level": "l4",
        "category": "protocol",
        "description": "Cross-layer artefact declares conformance to L4 schema or capability.",
        "required": [
            {"name": "evidence_uri", "type": "string", "description": "Evidence backing conformance"},
        ],
        "optional": [],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge protocol (L4) schemas into schema_registry.")
    parser.add_argument("--host", default=os.getenv("FALKOR_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("FALKOR_PORT", "6379")))
    parser.add_argument("--version", default="v4.0", help="Schema version tag to set on nodes")
    return parser.parse_args()


def upsert_node_schema(g, schema: Dict[str, Any], version: str) -> None:
    now_ms = int(datetime.now().timestamp() * 1000)
    g.query(
        """
        MERGE (nt:NodeTypeSchema {type_name: $type_name})
        SET nt.level = $level,
            nt.category = $category,
            nt.description = $description,
            nt.version = $version,
            nt.updated_at = $updated_at
        """,
        params={
            "type_name": schema["type_name"],
            "level": schema["level"],
            "category": schema["category"],
            "description": schema["description"],
            "version": version,
            "updated_at": now_ms,
        },
    )

    g.query(
        """
        MATCH (nt:NodeTypeSchema {type_name: $type_name})-[r:HAS_REQUIRED_FIELD|HAS_OPTIONAL_FIELD]->(f:FieldSchema)
        DELETE r, f
        """,
        params={"type_name": schema["type_name"]},
    )

    for field in schema["required"]:
        g.query(
            """
            MATCH (nt:NodeTypeSchema {type_name: $type_name})
            CREATE (f:FieldSchema {
                name: $name,
                type: $type,
                enum_values: $enum_values,
                range_min: $range_min,
                range_max: $range_max,
                description: $description,
                required: true,
                parent_type: $type_name,
                parent_category: 'node'
            })
            CREATE (nt)-[:HAS_REQUIRED_FIELD]->(f)
            """,
            params={
                "type_name": schema["type_name"],
                "name": field["name"],
                "type": field.get("type", "string"),
                "enum_values": field.get("enum_values", []),
                "range_min": field.get("range", [None, None])[0] if "range" in field else None,
                "range_max": field.get("range", [None, None])[1] if "range" in field else None,
                "description": field.get("description", ""),
            },
        )

    for field in schema["optional"]:
        g.query(
            """
            MATCH (nt:NodeTypeSchema {type_name: $type_name})
            CREATE (f:FieldSchema {
                name: $name,
                type: $type,
                enum_values: $enum_values,
                description: $description,
                required: false,
                parent_type: $type_name,
                parent_category: 'node'
            })
            CREATE (nt)-[:HAS_OPTIONAL_FIELD]->(f)
            """,
            params={
                "type_name": schema["type_name"],
                "name": field.get("name", ""),
                "type": field.get("type", "string"),
                "enum_values": field.get("enum_values", []),
                "description": field.get("description", ""),
            },
        )


def upsert_link_schema(g, schema: Dict[str, Any], version: str) -> None:
    now_ms = int(datetime.now().timestamp() * 1000)
    g.query(
        """
        MERGE (lt:LinkTypeSchema {type_name: $type_name})
        SET lt.level = $level,
            lt.category = $category,
            lt.description = $description,
            lt.required_attributes = $required_attributes,
            lt.optional_attributes = $optional_attributes,
            lt.detection_pattern = $detection_pattern,
            lt.detection_logic = $detection_logic,
            lt.task_template = $task_template,
            lt.mechanisms = $mechanisms,
            lt.version = $version,
            lt.updated_at = $updated_at
        """,
        params={
            "type_name": schema["type_name"],
            "level": schema["level"],
            "category": schema["category"],
            "description": schema["description"],
            "required_attributes": [f["name"] for f in schema["required"]],
            "optional_attributes": [f["name"] for f in schema["optional"]],
            "detection_pattern": schema.get("detection_pattern", "structured_event"),
            "detection_logic": json.dumps(schema.get("detection_logic", {"source": "broadcast"})),
            "task_template": schema.get("task_template", "review_protocol_relationship"),
            "mechanisms": schema.get("mechanisms", ["protocol_registry"]),
            "version": version,
            "updated_at": now_ms,
        },
    )

    g.query(
        """
        MATCH (lt:LinkTypeSchema {type_name: $type_name})-[r:HAS_REQUIRED_FIELD|HAS_OPTIONAL_FIELD]->(f:FieldSchema)
        DELETE r, f
        """,
        params={"type_name": schema["type_name"]},
    )

    for field in schema["required"]:
        g.query(
            """
            MATCH (lt:LinkTypeSchema {type_name: $type_name})
            CREATE (f:FieldSchema {
                name: $name,
                type: $type,
                enum_values: $enum_values,
                description: $description,
                required: true,
                parent_type: $type_name,
                parent_category: 'link'
            })
            CREATE (lt)-[:HAS_REQUIRED_FIELD]->(f)
            """,
            params={
                "type_name": schema["type_name"],
                "name": field.get("name", ""),
                "type": field.get("type", "string"),
                "enum_values": field.get("enum_values", []),
                "description": field.get("description", ""),
            },
        )

    for field in schema["optional"]:
        g.query(
            """
            MATCH (lt:LinkTypeSchema {type_name: $type_name})
            CREATE (f:FieldSchema {
                name: $name,
                type: $type,
                enum_values: $enum_values,
                description: $description,
                required: false,
                parent_type: $type_name,
                parent_category: 'link'
            })
            CREATE (lt)-[:HAS_OPTIONAL_FIELD]->(f)
            """,
            params={
                "type_name": schema["type_name"],
                "name": field.get("name", ""),
                "type": field.get("type", "string"),
                "enum_values": field.get("enum_values", []),
                "description": field.get("description", ""),
            },
        )


def main() -> None:
    args = parse_args()
    print("=" * 80)
    print(f"Ingesting protocol (L4) schemas into schema_registry @ {args.host}:{args.port}")
    print("=" * 80)

    db = FalkorDB(host=args.host, port=args.port)
    g = db.select_graph("schema_registry")
    print("[1/3] Connected to schema_registry graph.")

    for schema in PROTOCOL_NODE_SCHEMAS:
        upsert_node_schema(g, schema, args.version)
        print(f"  [Node] {schema['type_name']} upserted.")

    for schema in PROTOCOL_LINK_SCHEMAS:
        upsert_link_schema(g, schema, args.version)
        print(f"  [Link] {schema['type_name']} upserted.")

    node_count = g.query(
        "MATCH (nt:NodeTypeSchema) WHERE nt.type_name IN $types RETURN count(nt) as c",
        params={"types": [s["type_name"] for s in PROTOCOL_NODE_SCHEMAS]},
    ).result_set[0][0]
    link_count = g.query(
        "MATCH (lt:LinkTypeSchema) WHERE lt.type_name IN $types RETURN count(lt) as c",
        params={"types": [s["type_name"] for s in PROTOCOL_LINK_SCHEMAS]},
    ).result_set[0][0]

    print(f"[2/3] Verification: {node_count} protocol node schemas, {link_count} protocol link schemas present.")
    print("[3/3] Done. Regenerate Complete Type Reference to propagate updates:")
    print("      python tools/generate_complete_type_reference.py")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI usage
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
