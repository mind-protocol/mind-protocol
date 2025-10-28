"""
Add/merge ecosystem (L3) node & link schemas into FalkorDB schema_registry.

The canonical schemas live inside the `schema_registry` graph. This script
updates (or inserts) the new v3 ecosystem definitions so that downstream
tooling (Complete Type Reference, citizen prompts, adapters) can rely on the
database instead of ad-hoc copies.

Usage:
    python tools/schema_registry/add_ecosystem_v3.py \
        --host localhost --port 6379 --version v3.1

The script is idempotent: it MERGEs NodeTypeSchema / LinkTypeSchema nodes,
removes previous FieldSchema attachments for those types, and re-creates the
required/optional field nodes.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import os

from falkordb import FalkorDB


ECOSYSTEM_NODE_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type_name": "Ecosystem",
        "level": "n3",
        "category": "ecosystem",
        "description": "Domain container (e.g. trading commodities)",
        "required": [
            {"name": "slug", "type": "string", "description": "URL-friendly identifier"},
            {"name": "domain", "type": "string", "description": "Domain vertical"},
            {"name": "version", "type": "string", "description": "Manifest version"},
        ],
        "optional": [],
    },
    {
        "type_name": "Org_Profile",
        "level": "n3",
        "category": "ecosystem",
        "description": "Organization profile within the ecosystem layer",
        "required": [
            {"name": "org_id", "type": "string", "description": "Organization identifier"},
            {"name": "jurisdiction", "type": "string", "description": "Primary legal jurisdiction"},
        ],
        "optional": [
            {"name": "tags", "type": "array", "description": "Free-form labels for search"},
        ],
    },
    {
        "type_name": "Public_Presence",
        "level": "n3",
        "category": "ecosystem",
        "description": "Published surface of an organization (capabilities, channels)",
        "required": [
            {"name": "channels", "type": "array", "description": "List of supported public channels"},
            {"name": "capabilities", "type": "array", "description": "Capabilities exposed publicly"},
            {"name": "visibility", "type": "enum", "enum_values": ["public", "partners", "private"], "description": "Audience scope"},
        ],
        "optional": [
            {"name": "attestations", "type": "array", "description": "Evidence node IDs backing the presence"},
        ],
    },
    {
        "type_name": "Capability_Descriptor",
        "level": "n3",
        "category": "ecosystem",
        "description": "Descriptor of a capability (mapped to L4 schema references)",
        "required": [
            {"name": "name", "type": "string", "description": "Capability name"},
            {"name": "schema_ref", "type": "string", "description": "Reference to L4 schema or SDK module"},
        ],
        "optional": [
            {"name": "cost_hint", "type": "string", "description": "Human readable pricing hint"},
        ],
    },
    {
        "type_name": "RFQ",
        "level": "n3",
        "category": "evidence",
        "description": "Structured request for quote",
        "required": [
            {"name": "commodity", "type": "string", "description": "Requested commodity / product"},
            {"name": "qty", "type": "object", "description": "Quantity object {value, unit}"},
            {"name": "incoterm", "type": "string", "description": "Incoterm (FOB, CIF, etc.)"},
            {"name": "delivery_window", "type": "object", "description": "Object {from, to} specifying delivery period"},
        ],
        "optional": [
            {"name": "counterparty_pref", "type": "array", "description": "Preferred counterparties"},
        ],
    },
    {
        "type_name": "Quote",
        "level": "n3",
        "category": "evidence",
        "description": "Offer of price responding to an RFQ",
        "required": [
            {"name": "price", "type": "float", "description": "Quoted price"},
            {"name": "currency", "type": "string", "description": "ISO currency code"},
            {"name": "valid_until", "type": "datetime", "description": "Expiration timestamp"},
            {"name": "terms", "type": "string", "description": "Key contractual terms"},
        ],
        "optional": [],
    },
    {
        "type_name": "Deal",
        "level": "n3",
        "category": "evidence",
        "description": "Business deal / transaction record",
        "required": [
            {"name": "deal_type", "type": "enum", "enum_values": ["trade", "partnership", "service"], "description": "Deal category"},
            {"name": "state", "type": "enum", "enum_values": ["Proposed", "Negotiating", "Agreed", "Settled", "Cancelled"], "description": "Lifecycle state"},
            {"name": "instrument", "type": "enum", "enum_values": ["TermSheet", "Confirmation"], "description": "Instrument used"},
        ],
        "optional": [
            {"name": "qty", "type": "float", "description": "Quantity involved"},
            {"name": "price", "type": "float", "description": "Price agreed"},
            {"name": "incoterm", "type": "string", "description": "Applicable incoterm"},
        ],
    },
    {
        "type_name": "Agreement",
        "level": "n3",
        "category": "ecosystem",
        "description": "Signed agreement associated with a deal",
        "required": [
            {"name": "agreement_type", "type": "enum", "enum_values": ["MSA", "NDA", "SLA", "Confirmation"], "description": "Agreement type"},
            {"name": "effective_at", "type": "datetime", "description": "Effective date"},
        ],
        "optional": [
            {"name": "expires_at", "type": "datetime", "description": "Expiration date, if any"},
        ],
    },
    {
        "type_name": "Instrument",
        "level": "n3",
        "category": "ecosystem",
        "description": "Negotiation instrument / template",
        "required": [
            {"name": "instrument_type", "type": "enum", "enum_values": ["TermSheet", "Confirmation"], "description": "Type of instrument"},
            {"name": "template_uri", "type": "string", "description": "URI to template or repository"},
            {"name": "version", "type": "string", "description": "Template version"},
        ],
        "optional": [],
    },
    {
        "type_name": "Info_Asset",
        "level": "n3",
        "category": "evidence",
        "description": "Shareable information asset",
        "required": [
            {"name": "title", "type": "string", "description": "Title of the asset"},
            {"name": "access", "type": "enum", "enum_values": ["public", "bilateral", "paid"], "description": "Access level"},
            {"name": "pointer", "type": "string", "description": "CID/URI reference"},
        ],
        "optional": [
            {"name": "tags", "type": "array", "description": "Classification tags"},
        ],
    },
    {
        "type_name": "Info_Offer",
        "level": "n3",
        "category": "ecosystem",
        "description": "Offer to provide access to an information asset",
        "required": [
            {"name": "price_model", "type": "enum", "enum_values": ["free", "one_off", "subscription"], "description": "Pricing model"},
            {"name": "terms", "type": "string", "description": "Key terms of access"},
        ],
        "optional": [],
    },
    {
        "type_name": "Info_Request",
        "level": "n3",
        "category": "ecosystem",
        "description": "Request for information",
        "required": [
            {"name": "topic", "type": "string", "description": "Topic of interest"},
            {"name": "deadline", "type": "datetime", "description": "Deadline for response"},
        ],
        "optional": [
            {"name": "constraints", "type": "string", "description": "Constraints / filters"},
        ],
    },
    {
        "type_name": "Market",
        "level": "n3",
        "category": "ecosystem",
        "description": "Market segment / geography",
        "required": [
            {"name": "name", "type": "string", "description": "Market name"},
        ],
        "optional": [
            {"name": "region", "type": "string", "description": "Geographical region"},
            {"name": "product_class", "type": "string", "description": "Product class or family"},
        ],
    },
    {
        "type_name": "Counterparty",
        "level": "n3",
        "category": "ecosystem",
        "description": "Counterparty participating in deals",
        "required": [
            {"name": "company_type", "type": "enum", "enum_values": ["startup", "enterprise", "dao", "protocol"], "description": "Type of counterparty"},
            {"name": "status", "type": "enum", "enum_values": ["active", "inactive", "suspended"], "description": "Status in ecosystem"},
        ],
        "optional": [
            {"name": "website", "type": "string", "description": "Website or landing page"},
        ],
    },
    {
        "type_name": "Contact_Channel",
        "level": "n3",
        "category": "ecosystem",
        "description": "Contact channel for a public presence",
        "required": [
            {"name": "channel_type", "type": "enum", "enum_values": ["email", "api", "portal"], "description": "Channel modality"},
            {"name": "address", "type": "string", "description": "Contact address / endpoint"},
        ],
        "optional": [],
    },
    {
        "type_name": "Attestation",
        "level": "n3",
        "category": "evidence",
        "description": "Signed attestation backing an artefact",
        "required": [
            {"name": "sig", "type": "string", "description": "Signature or hash"},
            {"name": "issuer", "type": "string", "description": "Issuing party"},
            {"name": "purpose", "type": "string", "description": "Purpose of the attestation"},
        ],
        "optional": [],
    },
    {
        "type_name": "Policy_Lane",
        "level": "n3",
        "category": "ecosystem",
        "description": "Lane definition used by orchestrator",
        "required": [
            {"name": "lane_id", "type": "string", "description": "Lane identifier"},
            {"name": "capacity", "type": "int", "description": "Concurrent capacity"},
            {"name": "ack_policy", "type": "enum", "enum_values": ["none", "human_required", "tool_required"], "description": "Acknowledgement policy"},
        ],
        "optional": [],
    },
    {
        "type_name": "Citizen_Template",
        "level": "n3",
        "category": "ecosystem",
        "description": "Citizen template provided by ecosystem bootstrap",
        "required": [
            {"name": "image", "type": "string", "description": "Container image or package ref"},
            {"name": "default_subscribe", "type": "array", "description": "Default broadcast topics to subscribe"},
            {"name": "default_publish", "type": "array", "description": "Default inject channels"},
        ],
        "optional": [
            {"name": "limits", "type": "object", "description": "Resource limits (cpu/mem)"},
        ],
    },
    {
        "type_name": "Tool_Template",
        "level": "n3",
        "category": "ecosystem",
        "description": "Tool runner template",
        "required": [
            {"name": "capabilities", "type": "array", "description": "Capabilities served"},
            {"name": "runner_image", "type": "string", "description": "Container image"},
        ],
        "optional": [
            {"name": "resources", "type": "object", "description": "Resource hints (cpu/mem)"},
        ],
    },
    {
        "type_name": "Renderer_Template",
        "level": "n3",
        "category": "ecosystem",
        "description": "Renderer template for publications",
        "required": [
            {"name": "triggers", "type": "array", "description": "Events that trigger rendering"},
            {"name": "output", "type": "enum", "enum_values": ["git:publications", "site:static"], "description": "Output target"},
        ],
        "optional": [
            {"name": "branch_prefix", "type": "string", "description": "Branch prefix used for PRs"},
        ],
    },
]


ECOSYSTEM_LINK_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type_name": "PUBLISHES",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org profile publishes a public presence",
        "required": [
            {"name": "audience", "type": "enum", "enum_values": ["public", "partners"], "description": "Intended audience"},
        ],
        "optional": [],
    },
    {
        "type_name": "LISTS_CAPABILITY",
        "level": "n3",
        "category": "ecosystem",
        "description": "Public presence lists a capability descriptor",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "HAS_CHANNEL",
        "level": "n3",
        "category": "ecosystem",
        "description": "Public presence exposes a contact channel",
        "required": [
            {"name": "priority", "type": "enum", "enum_values": ["primary", "secondary"], "description": "Priority of channel"},
        ],
        "optional": [],
    },
    {
        "type_name": "CONFORMS_TO",
        "level": "n3",
        "category": "ecosystem",
        "description": "Descriptor/template conforms to L4 schema",
        "required": [
            {"name": "schema_version", "type": "string", "description": "Schema version"},
        ],
        "optional": [],
    },
    {
        "type_name": "OFFERS",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org offers an info asset or info offer",
        "required": [
            {"name": "access_level", "type": "enum", "enum_values": ["public", "bilateral", "paid"], "description": "Access level granted"},
        ],
        "optional": [],
    },
    {
        "type_name": "SEEKS",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org seeks an info request",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "SHARES_WITH",
        "level": "n3",
        "category": "ecosystem",
        "description": "Info asset is shared with an org profile",
        "required": [
            {"name": "access_level", "type": "enum", "enum_values": ["trial", "full"], "description": "Granted access level"},
        ],
        "optional": [],
    },
    {
        "type_name": "RESTRICTED_BY",
        "level": "n3",
        "category": "ecosystem",
        "description": "Asset or offer restricted by lane or agreement",
        "required": [
            {"name": "restriction_type", "type": "enum", "enum_values": ["lane", "agreement"], "description": "Restriction source"},
        ],
        "optional": [],
    },
    {
        "type_name": "PROPOSES",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org proposes a deal or RFQ",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "QUOTES_FOR",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org issues a quote responding to an RFQ",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "RESPONDS_TO",
        "level": "n3",
        "category": "ecosystem",
        "description": "Quote responds to an RFQ",
        "required": [
            {"name": "response_time_ms", "type": "float", "description": "Response latency in milliseconds"},
        ],
        "optional": [],
    },
    {
        "type_name": "NEGOTIATES",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org negotiates a deal",
        "required": [
            {"name": "role", "type": "enum", "enum_values": ["buyer", "seller"], "description": "Role in negotiation"},
        ],
        "optional": [],
    },
    {
        "type_name": "USES_INSTRUMENT",
        "level": "n3",
        "category": "ecosystem",
        "description": "Deal uses a specific instrument",
        "required": [
            {"name": "version", "type": "string", "description": "Instrument version"},
        ],
        "optional": [],
    },
    {
        "type_name": "SETTLED_BY",
        "level": "n3",
        "category": "ecosystem",
        "description": "Deal settled by an agreement",
        "required": [
            {"name": "settlement_date", "type": "datetime", "description": "Settlement date"},
        ],
        "optional": [],
    },
    {
        "type_name": "REFERENCES_MARKET",
        "level": "n3",
        "category": "ecosystem",
        "description": "Deal/RFQ/Quote references market",
        "required": [],
        "optional": [],
    },
    {
        "type_name": "EVIDENCED_BY",
        "level": "n3",
        "category": "ecosystem",
        "description": "Artefact evidenced by attestation",
        "required": [
            {"name": "evidence_type", "type": "enum", "enum_values": ["doc", "hash"], "description": "Evidence modality"},
        ],
        "optional": [],
    },
    {
        "type_name": "ENDORSES",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org endorses another org/capability",
        "required": [
            {"name": "endorsement_type", "type": "enum", "enum_values": ["reputation", "capability"], "description": "Nature of endorsement"},
        ],
        "optional": [],
    },
    {
        "type_name": "TRUSTS",
        "level": "n3",
        "category": "ecosystem",
        "description": "Org trusts a reputation assessment",
        "required": [
            {"name": "context", "type": "string", "description": "Context for trust decision"},
        ],
        "optional": [],
    },
    {
        "type_name": "ACTIVATES",
        "level": "n3",
        "category": "ecosystem",
        "description": "Ecosystem activates template (citizen/tool/renderer)",
        "required": [
            {"name": "activation_id", "type": "string", "description": "Activation identifier"},
        ],
        "optional": [],
    },
    {
        "type_name": "DEPLOYS",
        "level": "n3",
        "category": "ecosystem",
        "description": "Ecosystem deploys org profile into workspace",
        "required": [
            {"name": "deployment_id", "type": "string", "description": "Deployment identifier"},
        ],
        "optional": [],
    },
    {
        "type_name": "ROUTES_VIA",
        "level": "n3",
        "category": "ecosystem",
        "description": "Lane routes requests via capability",
        "required": [
            {"name": "priority", "type": "int", "description": "Routing priority"},
        ],
        "optional": [],
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge ecosystem L3 schemas into schema_registry.")
    parser.add_argument("--host", default=os.getenv("FALKOR_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("FALKOR_PORT", "6379")))
    parser.add_argument("--version", default="v3.1", help="Schema version tag to set on nodes")
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

    # Remove previous field schemas to avoid duplicates
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
            "task_template": schema.get("task_template", "review_event"),
            "mechanisms": schema.get("mechanisms", ["membrane"]),
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
    print(f"Ingesting ecosystem schemas into schema_registry @ {args.host}:{args.port}")
    print("=" * 80)

    db = FalkorDB(host=args.host, port=args.port)
    g = db.select_graph("schema_registry")
    print("[1/3] Connected to schema_registry graph.")

    for schema in ECOSYSTEM_NODE_SCHEMAS:
        upsert_node_schema(g, schema, args.version)
        print(f"  [Node] {schema['type_name']} upserted.")

    for schema in ECOSYSTEM_LINK_SCHEMAS:
        upsert_link_schema(g, schema, args.version)
        print(f"  [Link] {schema['type_name']} upserted.")

    node_count = g.query(
        "MATCH (nt:NodeTypeSchema) WHERE nt.type_name IN $types RETURN count(nt) as c",
        params={"types": [s["type_name"] for s in ECOSYSTEM_NODE_SCHEMAS]},
    ).result_set[0][0]
    link_count = g.query(
        "MATCH (lt:LinkTypeSchema) WHERE lt.type_name IN $types RETURN count(lt) as c",
        params={"types": [s["type_name"] for s in ECOSYSTEM_LINK_SCHEMAS]},
    ).result_set[0][0]

    print(f"[2/3] Verification: {node_count} node schemas, {link_count} link schemas present.")
    print("[3/3] Done. Regenerate Complete Type Reference to propagate updates:")
    print("      python tools/generate_complete_type_reference.py > docs/COMPLETE_TYPE_REFERENCE.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI usage
        print(f"[ERROR] {exc}", file=sys.stderr)
        sys.exit(1)
