"""
Build a canonical Layer-4 protocol snapshot from curated seed data.

This script produces the same JSON structure as `export_protocol_snapshot.py`
but works from repository-maintained definitions instead of querying the live
database. Run it whenever the protocol state changes (new schema, release,
policy) to regenerate `.build/protocol_snapshot.json` and the accompanying
manifest.

Usage:
    python tools/protocol/build_protocol_snapshot.py

Outputs:
    .build/protocol_snapshot.json
    .build/protocol_snapshot_manifest.txt
"""

from __future__ import annotations

import json
import hashlib
import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / ".build" / "protocol_snapshot.json"
MANIFEST_PATH = REPO_ROOT / ".build" / "protocol_snapshot_manifest.txt"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_sha(data: Any) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def load_schema(schema_uri: str) -> Dict[str, Any]:
    if not schema_uri:
        return {}
    if schema_uri.startswith("mind://"):
        relative = schema_uri.replace("mind://", "", 1)
        candidate = REPO_ROOT / "schemas" / relative
    elif schema_uri.startswith("file://"):
        candidate = Path(schema_uri[7:])
    else:
        candidate = REPO_ROOT / schema_uri
    if not candidate.exists():
        raise FileNotFoundError(f"Schema file not found for URI '{schema_uri}' resolved to '{candidate}'.")
    with candidate.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def schema_hash(schema_uri: str) -> str:
    if not schema_uri:
        return ""
    data = load_schema(schema_uri)
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


NODES: List[Dict[str, Any]] = [
    {
        "id": "protocol/Protocol_Version/1.1.0",
        "_labels": ["Protocol_Version"],
        "type_name": "Protocol_Version",
        "semver": "1.1.0",
        "released_at": "2025-10-27T12:00:00Z",
        "summary": "Membrane-first protocol hardening, schema v1.1 rollout.",
    },
    {
        "id": "protocol/Protocol_Version/1.0.0",
        "_labels": ["Protocol_Version"],
        "type_name": "Protocol_Version",
        "semver": "1.0.0",
        "released_at": "2025-08-01T18:00:00Z",
        "summary": "Initial public protocol release.",
    },
    {
        "id": "protocol/Envelope_Schema/membrane.inject.envelope@1.1",
        "_labels": ["Envelope_Schema"],
        "type_name": "Envelope_Schema",
        "name": "membrane.inject.envelope",
        "version": "1.1",
        "fields": ["v", "id", "ts", "type", "org", "scope", "channel", "origin", "ttl_frames", "payload", "sig"],
        "signature_path": "$.sig",
        "schema_uri": "mind://envelopes/membrane.inject.envelope.json",
    },
    {
        "id": "protocol/Event_Schema/membrane.inject@1.1",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "membrane.inject",
        "version": "1.1",
        "direction": "inject",
        "topic_pattern": "org/{org_id}/inject/membrane",
        "schema_uri": "mind://events/membrane.inject.json",
    },
    {
        "id": "protocol/Event_Schema/membrane.inject.ack@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "membrane.inject.ack",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/membrane.inject.ack",
        "schema_uri": "mind://events/membrane.inject.ack.json",
    },
    {
        "id": "protocol/Event_Schema/percept.frame@1.1",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "percept.frame",
        "version": "1.1",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/percept.frame",
        "schema_uri": "mind://events/percept.frame.json",
    },
    {
        "id": "protocol/Event_Schema/intent.created@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "intent.created",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/intent.created",
        "schema_uri": "mind://events/intent.created.json",
    },
    {
        "id": "protocol/Event_Schema/intent.assigned@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "intent.assigned",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/intent.assigned",
        "schema_uri": "mind://events/intent.assigned.json",
    },
    {
        "id": "protocol/Event_Schema/mission.done@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "mission.done",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/mission.done",
        "schema_uri": "mind://events/mission.done.json",
    },
    {
        "id": "protocol/Event_Schema/tool.offer@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "tool.offer",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/tool.offer",
        "schema_uri": "mind://events/tool.offer.json",
    },
    {
        "id": "protocol/Event_Schema/tool.request@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "tool.request",
        "version": "1.0",
        "direction": "inject",
        "topic_pattern": "org/{org_id}/inject/tool.request",
        "schema_uri": "mind://events/tool.request.json",
    },
    {
        "id": "protocol/Event_Schema/tool.result@1.1",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "tool.result",
        "version": "1.1",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/tool.result",
        "schema_uri": "mind://events/tool.result.v1.1.json",
    },
    {
        "id": "protocol/Event_Schema/tool.result@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "tool.result",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/tool.result",
        "schema_uri": "mind://events/tool.result.v1.0.json",
    },
    {
        "id": "protocol/Event_Schema/governance.keys.updated@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "governance.keys.updated",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/governance.keys.updated",
        "schema_uri": "mind://events/governance.keys.updated.json",
    },
    {
        "id": "protocol/Event_Schema/policy.change@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "policy.change",
        "version": "1.0",
        "direction": "inject",
        "topic_pattern": "org/{org_id}/inject/policy.change",
        "schema_uri": "mind://events/policy.change.json",
    },
    {
        "id": "protocol/Event_Schema/policy.applied@1.0",
        "_labels": ["Event_Schema"],
        "type_name": "Event_Schema",
        "name": "policy.applied",
        "version": "1.0",
        "direction": "broadcast",
        "topic_pattern": "org/{org_id}/broadcast/policy.applied",
        "schema_uri": "mind://events/policy.applied.json",
    },
    {
        "id": "protocol/Capability/git.commit",
        "_labels": ["Capability"],
        "type_name": "Capability",
        "capability": "git.commit",
        "input_schema_ref": "protocol/Event_Schema/tool.request@1.0",
        "output_schema_ref": "protocol/Event_Schema/tool.result@1.1",
    },
    {
        "id": "protocol/Capability/git.pr",
        "_labels": ["Capability"],
        "type_name": "Capability",
        "capability": "git.pr",
        "input_schema_ref": "protocol/Event_Schema/tool.request@1.0",
        "output_schema_ref": "protocol/Event_Schema/tool.result@1.1",
    },
    {
        "id": "protocol/Capability/doc.render",
        "_labels": ["Capability"],
        "type_name": "Capability",
        "capability": "doc.render",
        "input_schema_ref": "protocol/Event_Schema/tool.request@1.0",
        "output_schema_ref": "protocol/Event_Schema/tool.result@1.1",
    },
    {
        "id": "protocol/Capability/protocol.refresh",
        "_labels": ["Capability"],
        "type_name": "Capability",
        "capability": "protocol.refresh",
        "input_schema_ref": "protocol/Event_Schema/policy.change@1.0",
        "output_schema_ref": "protocol/Event_Schema/policy.applied@1.0",
    },
    {
        "id": "protocol/Tool_Contract/git-runner",
        "_labels": ["Tool_Contract"],
        "type_name": "Tool_Contract",
        "tool_id": "git-runner",
        "capabilities": ["git.commit", "git.pr"],
        "args_schema_ref": "protocol/Event_Schema/tool.request@1.0",
        "result_schema_ref": "protocol/Event_Schema/tool.result@1.1",
    },
    {
        "id": "protocol/Tool_Contract/doc-renderer",
        "_labels": ["Tool_Contract"],
        "type_name": "Tool_Contract",
        "tool_id": "doc-renderer",
        "capabilities": ["doc.render"],
        "args_schema_ref": "protocol/Event_Schema/tool.request@1.0",
        "result_schema_ref": "protocol/Event_Schema/tool.result@1.1",
    },
    {
        "id": "protocol/Topic_Namespace/org-inject",
        "_labels": ["Topic_Namespace"],
        "type_name": "Topic_Namespace",
        "pattern": "org/{org_id}/inject/*",
        "scope": "org",
        "description": "Organization-scoped inject namespace.",
    },
    {
        "id": "protocol/Topic_Namespace/org-broadcast",
        "_labels": ["Topic_Namespace"],
        "type_name": "Topic_Namespace",
        "pattern": "org/{org_id}/broadcast/*",
        "scope": "org",
        "description": "Organization-scoped broadcast namespace.",
    },
    {
        "id": "protocol/Topic_Namespace/protocol-global",
        "_labels": ["Topic_Namespace"],
        "type_name": "Topic_Namespace",
        "pattern": "protocol/*",
        "scope": "global",
        "description": "Global protocol coordination topics.",
    },
    {
        "id": "protocol/Topic_Route/inject-to-orchestrator",
        "_labels": ["Topic_Route"],
        "type_name": "Topic_Route",
        "from_namespace": "protocol/Topic_Namespace/org-inject",
        "to_component": "orchestrator",
        "routing_notes": "Ingest stimuli, enforce lanes, emit intent.*",
    },
    {
        "id": "protocol/Topic_Route/broadcast-to-observers",
        "_labels": ["Topic_Route"],
        "type_name": "Topic_Route",
        "from_namespace": "protocol/Topic_Namespace/org-broadcast",
        "to_component": "observers",
        "routing_notes": "Fan-out perceptual state to dashboards and tooling.",
    },
    {
        "id": "protocol/Signature_Suite/ed25519-v1",
        "_labels": ["Signature_Suite"],
        "type_name": "Signature_Suite",
        "algo": "ed25519",
        "pubkey_encoding": "base64",
        "signature_field": "sig.signature",
    },
    {
        "id": "protocol/Tenant/dev-org",
        "_labels": ["Tenant"],
        "type_name": "Tenant",
        "org_id": "dev-org",
        "display_name": "Development Organization",
    },
    {
        "id": "protocol/Tenant_Key/dev-org@2",
        "_labels": ["Tenant_Key"],
        "type_name": "Tenant_Key",
        "org_id": "dev-org",
        "key_version": 2,
        "pubkey": "dev-org-pubkey-v2",
        "created_at": "2025-10-20T09:12:00Z",
        "rotated_at": None,
    },
    {
        "id": "protocol/Governance_Policy/default-lane-policy",
        "_labels": ["Governance_Policy"],
        "type_name": "Governance_Policy",
        "name": "default-lane-policy",
        "policy_doc_uri": "https://protocol.mind/doc/default-lane-policy",
        "defaults": {"ack_policy": "human_required", "lane_capacity": 3},
    },
    {
        "id": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2",
        "_labels": ["SDK_Release"],
        "type_name": "SDK_Release",
        "language": "typescript",
        "package_name": "@mind/membrane-sdk",
        "version": "0.3.2",
        "commit_hash": "f3a1c9d",
        "schema_min_version": "1.1",
    },
    {
        "id": "protocol/SDK_Release/sdk.py:membrane-sdk@0.2.5",
        "_labels": ["SDK_Release"],
        "type_name": "SDK_Release",
        "language": "python",
        "package_name": "mind-membrane-sdk",
        "version": "0.2.5",
        "commit_hash": "c71a2b4",
        "schema_min_version": "1.1",
    },
    {
        "id": "protocol/SDK_Release/sdk.go:membrane-sdk@0.1.4",
        "_labels": ["SDK_Release"],
        "type_name": "SDK_Release",
        "language": "go",
        "package_name": "github.com/mind/membrane-sdk",
        "version": "0.1.4",
        "commit_hash": "d582cc1",
        "schema_min_version": "1.1",
    },
    {
        "id": "protocol/Sidecar_Release/sidecar@1.1.0",
        "_labels": ["Sidecar_Release"],
        "type_name": "Sidecar_Release",
        "image_ref": "ghcr.io/mind/sidecar:1.1.0",
        "version": "1.1.0",
        "features": ["buffer_offline", "replay", "ed25519"],
        "schema_min_version": "1.1",
    },
    {
        "id": "protocol/Adapter_Release/claude@0.4.0",
        "_labels": ["Adapter_Release"],
        "type_name": "Adapter_Release",
        "provider": "claude",
        "version": "0.4.0",
        "features": ["streaming", "paneled-ui"],
    },
    {
        "id": "protocol/Adapter_Release/codex@0.3.0",
        "_labels": ["Adapter_Release"],
        "type_name": "Adapter_Release",
        "provider": "codex",
        "version": "0.3.0",
        "features": ["pty-bridge", "fs-watch"],
    },
    {
        "id": "protocol/Adapter_Release/gemini@0.2.1",
        "_labels": ["Adapter_Release"],
        "type_name": "Adapter_Release",
        "provider": "gemini",
        "version": "0.2.1",
        "features": ["streaming"],
    },
    {
        "id": "protocol/Conformance_Suite/protocol-core@2025-10-27",
        "_labels": ["Conformance_Suite"],
        "type_name": "Conformance_Suite",
        "suite_id": "protocol-core@2025-10-27",
        "cases_count": 18,
        "schema_set_ref": "l4-schemas@1.1.0",
    },
    {
        "id": "protocol/Conformance_Case/membrane.inject.required",
        "_labels": ["Conformance_Case"],
        "type_name": "Conformance_Case",
        "case_id": "membrane.inject.required",
        "description": "Validates required envelope fields present.",
        "expected": "pass",
    },
    {
        "id": "protocol/Conformance_Case/tool.result.artifact",
        "_labels": ["Conformance_Case"],
        "type_name": "Conformance_Case",
        "case_id": "tool.result.artifact",
        "description": "Ensures artifact metadata present on success.",
        "expected": "pass",
    },
    {
        "id": "protocol/Conformance_Result/sdk.ts:membrane-sdk@0.3.2",
        "_labels": ["Conformance_Result"],
        "type_name": "Conformance_Result",
        "suite_id": "protocol-core@2025-10-27",
        "target_release": "sdk.ts:membrane-sdk@0.3.2",
        "pass_rate": 1.0,
        "failing_cases": [],
    },
    {
        "id": "protocol/Deprecation_Notice/tool.result@1.0",
        "_labels": ["Deprecation_Notice"],
        "type_name": "Deprecation_Notice",
        "target_kind": "Event_Schema",
        "target_ref": "protocol/Event_Schema/tool.result@1.0",
        "effective_at": "2025-11-15T00:00:00Z",
        "end_of_support": "2026-01-15T00:00:00Z",
    },
    {
        "id": "protocol/Compatibility_Matrix/2025-10-27",
        "_labels": ["Compatibility_Matrix"],
        "type_name": "Compatibility_Matrix",
        "matrix": [
            {"from": "sdk.ts:membrane-sdk@0.3.2", "to": "sidecar@1.1.0", "level": "runtime", "status": "ok"},
            {"from": "sdk.py:membrane-sdk@0.2.5", "to": "sidecar@1.1.0", "level": "runtime", "status": "warn"},
            {"from": "sdk.go:membrane-sdk@0.1.4", "to": "sidecar@1.1.0", "level": "runtime", "status": "ok"}
        ],
        "generated_at": "2025-10-27T12:00:00Z",
    },
    {
        "id": "protocol/Transport_Spec/ws",
        "_labels": ["Transport_Spec"],
        "type_name": "Transport_Spec",
        "type": "ws",
        "qos": {"durable": False, "acks": "at-least-once"},
    },
    {
        "id": "protocol/Transport_Spec/nats",
        "_labels": ["Transport_Spec"],
        "type_name": "Transport_Spec",
        "type": "nats",
        "qos": {"durable": True, "acks": "exactly-once"},
    },
    {
        "id": "protocol/Bus_Instance/ws-local",
        "_labels": ["Bus_Instance"],
        "type_name": "Bus_Instance",
        "endpoint": "ws://localhost:8765",
        "transport_ref": "protocol/Transport_Spec/ws",
        "retention_policy_ref": "protocol/Retention_Policy/default-medium",
    },
    {
        "id": "protocol/Retention_Policy/default-medium",
        "_labels": ["Retention_Policy"],
        "type_name": "Retention_Policy",
        "name": "default-medium",
        "time_limit": "3d",
        "size_limit_mb": 512,
        "dedupe_window_ms": 60000,
    },
    {
        "id": "protocol/Security_Profile/org-default",
        "_labels": ["Security_Profile"],
        "type_name": "Security_Profile",
        "profile_name": "org-default",
        "required_signature_suites": ["protocol/Signature_Suite/ed25519-v1"],
        "min_key_length_bits": 256,
    },
    {
        "id": "protocol/Schema_Bundle/l4-schemas@1.1.0",
        "_labels": ["Schema_Bundle"],
        "type_name": "Schema_Bundle",
        "bundle_uri": "https://protocol.mind/releases/l4-schemas-1.1.0.tar.gz",
        "bundle_hash": "placeholder-bundle-hash",
        "contains": [
            "membrane.inject@1.1",
            "percept.frame@1.1",
            "tool.request@1.0",
            "tool.result@1.1",
            "policy.change@1.0"
        ],
    },
]


EDGES: List[Dict[str, Any]] = [
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/membrane.inject@1.1", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Envelope_Schema/membrane.inject.envelope@1.1", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/percept.frame@1.1", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/tool.result@1.1", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/membrane.inject.ack@1.0", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/governance.keys.updated@1.0", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "PUBLISHES_SCHEMA", "target": "protocol/Event_Schema/policy.change@1.0", "properties": {"release_notes_uri": "https://protocol.mind/releases/1.1.0"}},
    {"source": "protocol/Protocol_Version/1.1.0", "type": "DEPRECATES", "target": "protocol/Protocol_Version/1.0.0", "properties": {"grace_period_days": 45}},
    {"source": "protocol/Event_Schema/tool.result@1.1", "type": "DEPRECATES", "target": "protocol/Event_Schema/tool.result@1.0", "properties": {"grace_period_days": 60}},
    {"source": "protocol/Event_Schema/tool.request@1.0", "type": "GOVERNS", "target": "protocol/Capability/git.commit", "properties": {"governance_scope": "schema"}},
    {"source": "protocol/Governance_Policy/default-lane-policy", "type": "GOVERNS", "target": "protocol/Topic_Namespace/org-inject", "properties": {"governance_scope": "policy"}},
    {"source": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2", "type": "IMPLEMENTS", "target": "protocol/Event_Schema/tool.request@1.0", "properties": {"coverage": 1.0}},
    {"source": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2", "type": "IMPLEMENTS", "target": "protocol/Event_Schema/tool.result@1.1", "properties": {"coverage": 1.0}},
    {"source": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2", "type": "IMPLEMENTS", "target": "protocol/Capability/git.commit", "properties": {"coverage": 0.95}},
    {"source": "protocol/Sidecar_Release/sidecar@1.1.0", "type": "SUPPORTS", "target": "protocol/Event_Schema/membrane.inject@1.1", "properties": {"maturity": "ga"}},
    {"source": "protocol/Sidecar_Release/sidecar@1.1.0", "type": "SUPPORTS", "target": "protocol/Transport_Spec/ws", "properties": {"maturity": "ga"}},
    {"source": "protocol/Adapter_Release/claude@0.4.0", "type": "ADAPTER_SUPPORTS", "target": "protocol/Capability/doc.render", "properties": {"latency_hint_ms": 850}},
    {"source": "protocol/Adapter_Release/codex@0.3.0", "type": "ADAPTER_SUPPORTS", "target": "protocol/Capability/git.commit", "properties": {"latency_hint_ms": 640}},
    {"source": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2", "type": "COMPATIBLE_WITH", "target": "protocol/Sidecar_Release/sidecar@1.1.0", "properties": {"level": "runtime", "status": "ok"}},
    {"source": "protocol/Event_Schema/membrane.inject@1.1", "type": "REQUIRES_SIG", "target": "protocol/Signature_Suite/ed25519-v1", "properties": {}},
    {"source": "protocol/Tenant_Key/dev-org@2", "type": "SIGNED_WITH", "target": "protocol/Signature_Suite/ed25519-v1", "properties": {}},
    {"source": "protocol/Tenant_Key/dev-org@2", "type": "ASSIGNED_TO_TENANT", "target": "protocol/Tenant/dev-org", "properties": {"key_version": 2}},
    {"source": "protocol/Topic_Namespace/org-inject", "type": "ROUTES_OVER", "target": "protocol/Transport_Spec/ws", "properties": {}},
    {"source": "protocol/Topic_Route/inject-to-orchestrator", "type": "ROUTES_OVER", "target": "protocol/Transport_Spec/ws", "properties": {}},
    {"source": "protocol/Bus_Instance/ws-local", "type": "HOSTED_ON", "target": "protocol/Transport_Spec/ws", "properties": {}},
    {"source": "protocol/Bus_Instance/ws-local", "type": "SERVES_NAMESPACE", "target": "protocol/Topic_Namespace/org-inject", "properties": {}},
    {"source": "protocol/Retention_Policy/default-medium", "type": "APPLIES_TO", "target": "protocol/Topic_Namespace/org-inject", "properties": {}},
    {"source": "protocol/Security_Profile/org-default", "type": "DEFAULTS_FOR", "target": "protocol/Event_Schema/membrane.inject@1.1", "properties": {}},
    {"source": "protocol/Schema_Bundle/l4-schemas@1.1.0", "type": "BUNDLES", "target": "protocol/Event_Schema/membrane.inject@1.1", "properties": {}},
    {"source": "protocol/Schema_Bundle/l4-schemas@1.1.0", "type": "BUNDLES", "target": "protocol/Envelope_Schema/membrane.inject.envelope@1.1", "properties": {}},
    {"source": "protocol/Conformance_Suite/protocol-core@2025-10-27", "type": "TESTS", "target": "protocol/Event_Schema/membrane.inject@1.1", "properties": {}},
    {"source": "protocol/Conformance_Suite/protocol-core@2025-10-27", "type": "TESTS", "target": "protocol/Capability/git.commit", "properties": {}},
    {"source": "protocol/Conformance_Result/sdk.ts:membrane-sdk@0.3.2", "type": "CERTIFIES_CONFORMANCE", "target": "protocol/SDK_Release/sdk.ts:membrane-sdk@0.3.2", "properties": {}},
    {"source": "protocol/Event_Schema/membrane.inject@1.1", "type": "MAPS_TO_TOPIC", "target": "protocol/Topic_Namespace/org-inject", "properties": {}},
    {"source": "protocol/Event_Schema/percept.frame@1.1", "type": "MAPS_TO_TOPIC", "target": "protocol/Topic_Namespace/org-broadcast", "properties": {}},
    {"source": "protocol/Event_Schema/tool.result@1.1", "type": "MAPS_TO_TOPIC", "target": "protocol/Topic_Namespace/org-broadcast", "properties": {}},
    {"source": "protocol/Tool_Contract/git-runner", "type": "CONFORMS_TO", "target": "protocol/Capability/git.commit", "properties": {"evidence_uri": "local://sha256/git-runner-contract"}},
    {"source": "protocol/Tool_Contract/doc-renderer", "type": "CONFORMS_TO", "target": "protocol/Capability/doc.render", "properties": {"evidence_uri": "local://sha256/doc-renderer-contract"}},
]


def enrich_nodes(nodes: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Tuple[str, str]]]:
    enriched = []
    manifest_entries = []
    for node in nodes:
        node_copy = dict(node)
        labels = node_copy.pop("_labels", [])
        if labels:
            node_copy["_labels"] = labels
        if node_copy.get("schema_uri"):
            node_copy["schema_hash"] = schema_hash(node_copy["schema_uri"])
        node_copy["layer"] = "L4"
        node_copy["content_sha"] = compute_sha(node_copy)
        manifest_entries.append((node_copy["content_sha"], node_copy["id"]))
        enriched.append(node_copy)
    manifest_entries.sort(key=lambda item: item[1])
    return enriched, manifest_entries


def main() -> None:
    enriched_nodes, manifest_entries = enrich_nodes(NODES)
    snapshot = {
        "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "graph": "protocol",
        "node_count": len(enriched_nodes),
        "edge_count": len(EDGES),
        "nodes": enriched_nodes,
        "edges": EDGES,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        for sha, node_id in manifest_entries:
            fh.write(f"{sha} {node_id}\n")

    print(f"[OK] Snapshot written to {OUTPUT_PATH} ({len(enriched_nodes)} nodes, {len(EDGES)} edges).")


if __name__ == "__main__":
    main()
