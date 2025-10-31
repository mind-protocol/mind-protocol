#!/usr/bin/env python3
"""
L4 Protocol Ingestion: Membrane-Native Reviewer Event Schemas

Adds event schemas for the membrane-native reviewer and lint system:
- File watcher events (code change detection)
- Review process events (request, verdict, override)
- Lint findings events (adapter output)
- Failure events (fail-loud requirement)
- Protocol mandate events (L4 → L2 review mandates)
- Economy events (budget reservation, chargeback)

This unblocks:
- Real-time lint feedback (file watcher → SafeBroadcaster → dashboard)
- Protocol-level code review mandates
- Fail-loud contract enforcement (R-400/R-401)

Author: Ada Bridgekeeper (architect) + Nicolas Reynolds (spec)
Date: 2025-10-31
Ticket: L4-018 (Reviewer Event Schemas)
Spec: docs/L4-law/membrane_native_reviewer_and_lint_system.md
"""

import sys
import redis

# ============================================================================
# Topic Namespaces (7 total)
# ============================================================================

REVIEWER_NAMESPACES = [
    {
        "name": "watcher",
        "pattern": "ecosystem/{eco}/org/{org}/watcher.*",
        "description": "File watcher events (local code changes)"
    },
    {
        "name": "code",
        "pattern": "ecosystem/{eco}/org/{org}/code.*",
        "description": "Code diff events (change payloads)"
    },
    {
        "name": "review",
        "pattern": "ecosystem/{eco}/org/{org}/review.*",
        "description": "Review process events (request, verdict, override)"
    },
    {
        "name": "lint",
        "pattern": "ecosystem/{eco}/org/{org}/lint.*",
        "description": "Lint findings from adapters (mp-lint, eslint, secretscan)"
    },
    {
        "name": "failure",
        "pattern": "ecosystem/{eco}/org/{org}/failure.*",
        "description": "Failure events (fail-loud requirement, R-400/R-401)"
    },
    {
        "name": "protocol.review",
        "pattern": "ecosystem/{eco}/protocol/review.*",
        "description": "Protocol mandate events (L4 → L2 review mandates)"
    },
    {
        "name": "economy",
        "pattern": "ecosystem/{eco}/org/{org}/economy.*",
        "description": "Economy events (budget reservation, chargeback)"
    }
]

# ============================================================================
# Event Schemas (17 total)
# ============================================================================

REVIEWER_SCHEMAS = [
    # ========================================================================
    # Org Review Lane (8 schemas)
    # ========================================================================
    {
        "schema_uri": "l4://schemas/watcher.local.change/1.0.0.json",
        "name": "watcher.local.change",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/org/{org}/watcher.local.change",
        "namespace": "watcher",
        "summary": "File change detected by watcher (debounced, batched)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 240,
        "allowed_emitters": ["watcher.*"],
        "fields": ["file_path", "sha_before", "sha_after", "timestamp"]
    },
    {
        "schema_uri": "l4://schemas/code.diff.emit/1.0.0.json",
        "name": "code.diff.emit",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/org/{org}/code.diff.emit",
        "namespace": "code",
        "summary": "Code diff payload (hunks, hashes, change_id)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 512,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["watcher.*", "ci.*"],
        "fields": ["change_id", "files", "hunks", "sha_before", "sha_after"]
    },
    {
        "schema_uri": "l4://schemas/review.request/1.0.0.json",
        "name": "review.request",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/org/{org}/review.request",
        "namespace": "review",
        "summary": "Request code review (from watcher, CI, or protocol mandate)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["watcher.*", "ci.*", "protocol.mandate_router"],
        "fields": ["change_id", "origin", "policy_set"]
    },
    {
        "schema_uri": "l4://schemas/lint.findings.emit/1.0.0.json",
        "name": "lint.findings.emit",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/lint.findings.emit",
        "namespace": "lint",
        "summary": "Lint findings from adapters (mp-lint R-001 through R-401)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 1024,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["adapter.lint.*", "adapter.secretscan", "adapter.depgraph"],
        "fields": ["change_id", "findings", "policy", "rule", "severity", "file", "span", "message", "suggestion"]
    },
    {
        "schema_uri": "l4://schemas/review.verdict/1.0.0.json",
        "name": "review.verdict",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/review.verdict",
        "namespace": "review",
        "summary": "Review verdict (pass, soft_fail, hard_fail) with policy scores",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 128,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["reviewer.*"],
        "fields": ["change_id", "result", "scores", "required_override", "policy_violations"]
    },
    {
        "schema_uri": "l4://schemas/review.override.request/1.0.0.json",
        "name": "review.override.request",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/org/{org}/review.override.request",
        "namespace": "review",
        "summary": "Request override for failing verdict (requires reason, ticket, expiry)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 30,
        "allowed_emitters": ["human.*", "ci.*"],
        "fields": ["change_id", "reason", "ticket_ref", "expiry_date", "requestor"]
    },
    {
        "schema_uri": "l4://schemas/review.override.granted/1.0.0.json",
        "name": "review.override.granted",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/review.override.granted",
        "namespace": "review",
        "summary": "Override granted (merge allowed despite failures)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 30,
        "allowed_emitters": ["reviewer.*"],
        "fields": ["change_id", "override_id", "granted_by", "expiry_date", "conditions"]
    },
    {
        "schema_uri": "l4://schemas/review.override.denied/1.0.0.json",
        "name": "review.override.denied",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/review.override.denied",
        "namespace": "review",
        "summary": "Override denied (insufficient reason or policy violation)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 30,
        "allowed_emitters": ["reviewer.*"],
        "fields": ["change_id", "denial_reason", "denied_by"]
    },
    {
        "schema_uri": "l4://schemas/failure.emit/1.0.0.json",
        "name": "failure.emit",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/failure.emit",
        "namespace": "failure",
        "summary": "Fail-loud event (catch without rethrow, R-400/R-401 enforcement)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 32,
        "rate_limit_per_min": 120,
        "allowed_emitters": ["adapter.*", "reviewer.*", "watcher.*"],
        "fields": ["change_id", "code_location", "exception", "severity", "suggestion", "trace_id"]
    },

    # ========================================================================
    # Protocol Mandate Lane (4 schemas)
    # ========================================================================
    {
        "schema_uri": "l4://schemas/review.mandate/1.0.0.json",
        "name": "review.mandate",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/protocol/review.mandate",
        "namespace": "protocol.review",
        "summary": "Protocol-level review mandate (L4 → L2, triggered by protocol/policy changes)",
        "sea_required": True,  # STRICT - protocol mandates require SEA
        "cps": False,
        "payload_cap_kb": 256,
        "rate_limit_per_min": 10,
        "allowed_emitters": ["protocol.mandate_router", "protocol.watcher"],
        "fields": ["mandate_id", "cause", "scope", "policy_set", "sla_seconds", "billing"]
    },
    {
        "schema_uri": "l4://schemas/mandate.ack/1.0.0.json",
        "name": "mandate.ack",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/protocol/mandate.ack",
        "namespace": "protocol.review",
        "summary": "Org acknowledges mandate (budget reserved)",
        "sea_required": True,  # STRICT - accountability required
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 10,
        "allowed_emitters": ["org.reviewer.*"],
        "fields": ["mandate_id", "org_ref", "ack_timestamp", "budget_reserved"]
    },
    {
        "schema_uri": "l4://schemas/mandate.result/1.0.0.json",
        "name": "mandate.result",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/protocol/mandate.result",
        "namespace": "protocol.review",
        "summary": "Org reports mandate completion (verdict, cost, evidence)",
        "sea_required": True,  # STRICT - results are binding
        "cps": False,
        "payload_cap_kb": 256,
        "rate_limit_per_min": 10,
        "allowed_emitters": ["org.reviewer.*"],
        "fields": ["mandate_id", "result", "verdict", "cost_deltaE", "evidence_uri"]
    },
    {
        "schema_uri": "l4://schemas/mandate.breach/1.0.0.json",
        "name": "mandate.breach",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/protocol/mandate.breach",
        "namespace": "protocol.review",
        "summary": "Mandate breach (SLA missed or refusal, governance consequences)",
        "sea_required": True,  # STRICT - breach is a protocol-level event
        "cps": False,
        "payload_cap_kb": 128,
        "rate_limit_per_min": 10,
        "allowed_emitters": ["protocol.mandate_router"],
        "fields": ["mandate_id", "org_ref", "breach_type", "sla_missed_by_seconds", "consequences"]
    },

    # ========================================================================
    # Economy Lane (4 schemas)
    # ========================================================================
    {
        "schema_uri": "l4://schemas/economy.quote.request/1.0.0.json",
        "name": "economy.quote.request",
        "version": "1.0.0",
        "direction": "inject",
        "topic_pattern": "ecosystem/{eco}/org/{org}/economy.quote.request",
        "namespace": "economy",
        "summary": "Request quote for review operation (budget planning)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["reviewer.*", "org.controller.*"],
        "fields": ["operation", "scope", "estimated_files", "estimated_lines"]
    },
    {
        "schema_uri": "l4://schemas/economy.quote.response/1.0.0.json",
        "name": "economy.quote.response",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/economy.quote.response",
        "namespace": "economy",
        "summary": "Quote response (estimated cost in deltaE)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["economy.*"],
        "fields": ["quote_id", "estimated_deltaE", "confidence", "breakdown"]
    },
    {
        "schema_uri": "l4://schemas/budget.checked/1.0.0.json",
        "name": "budget.checked",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/budget.checked",
        "namespace": "economy",
        "summary": "Budget check passed (sufficient funds for operation)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["economy.*"],
        "fields": ["org_ref", "operation", "reserved_deltaE", "remaining_balance"]
    },
    {
        "schema_uri": "l4://schemas/budget.clamped/1.0.0.json",
        "name": "budget.clamped",
        "version": "1.0.0",
        "direction": "broadcast",
        "topic_pattern": "ecosystem/{eco}/org/{org}/budget.clamped",
        "namespace": "economy",
        "summary": "Budget check failed (insufficient funds, operation clamped)",
        "sea_required": False,
        "cps": False,
        "payload_cap_kb": 64,
        "rate_limit_per_min": 60,
        "allowed_emitters": ["economy.*"],
        "fields": ["org_ref", "operation", "requested_deltaE", "available_balance", "deficit"]
    }
]

# ============================================================================
# Governance Policies (2 total: ORG_REVIEWER_V1, PROTOCOL_MANDATE_V1)
# ============================================================================

GOVERNANCE_POLICIES = [
    {
        "policy_id": "POL_ORG_REVIEWER_V1",
        "name": "Org Reviewer Policy",
        "description": "Governs org-scoped review events (watcher, lint, verdict, failure)",
        "governs_namespaces": ["watcher", "code", "review", "lint", "failure", "economy"]
    },
    {
        "policy_id": "POL_PROTOCOL_MANDATE_V1",
        "name": "Protocol Mandate Policy",
        "description": "Governs protocol-level review mandates (SEA required, strict accountability)",
        "governs_namespaces": ["protocol.review"]
    }
]


def ingest_reviewer_events():
    """Ingest membrane-native reviewer event schemas to L4 protocol graph."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=False)
    graph_name = "protocol"

    print("🔍 Membrane-Native Reviewer Event Schemas Ingestion")
    print("=" * 70)
    print()

    # 0. Get/create signature suite and envelope schema (if not exist)
    print("0️⃣  Ensuring Signature Suite and Envelope Schema exist...")
    sig_id = "protocol/Signature_Suite/SIG_ED25519_V1"
    env_id = "protocol/Envelope_Schema/ENV_STANDARD_V1"

    query = f"""
    MERGE (sig:ProtocolNode {{id: '{sig_id}'}})
    ON CREATE SET
        sig.suite_id = 'SIG_ED25519_V1',
        sig.algo = 'ed25519',
        sig.type_name = 'L4_Signature_Suite',
        sig.level = 'L4',
        sig.scope_ref = 'protocol',
        sig.name = 'ED25519 Signature Suite'

    MERGE (env:ProtocolNode {{id: '{env_id}'}})
    ON CREATE SET
        env.schema_uri = 'l4://schemas/envelopes/ENV_STANDARD_V1.json',
        env.version = '1.0.0',
        env.name = 'ENV_STANDARD_V1',
        env.type_name = 'L4_Envelope_Schema',
        env.level = 'L4',
        env.scope_ref = 'protocol'
    WITH env, sig
    MERGE (env)-[:U4_REQUIRES_SIG]->(sig)
    """
    r.execute_command("GRAPH.QUERY", graph_name, query)
    print(f"  ✓ SIG_ED25519_V1 (ed25519)")
    print(f"  ✓ ENV_STANDARD_V1")
    print()

    # 1. Create Topic_Namespace nodes
    print("1️⃣  Creating Topic Namespaces (7 namespaces)...")
    for ns in REVIEWER_NAMESPACES:
        namespace_id = f"protocol/Topic_Namespace/{ns['name']}"
        query = f"""
        MERGE (ns:ProtocolNode {{id: '{namespace_id}'}})
        ON CREATE SET
            ns.name = '{ns["pattern"]}',
            ns.type_name = 'L4_Topic_Namespace',
            ns.description = '{ns["description"]}',
            ns.level = 'L4',
            ns.scope_ref = 'protocol'
        RETURN ns.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)
        print(f"  ✓ {ns['pattern']:<50}")
    print()

    # 2. Create/verify Schema Bundle (BUNDLE_REVIEWER_1_0_0)
    print("2️⃣  Creating Schema Bundle...")
    bundle_id = "protocol/Schema_Bundle/BUNDLE_REVIEWER_1_0_0"
    reg_id = "protocol/Subentity/schema-registry"

    query = f"""
    MERGE (reg:ProtocolNode {{id: '{reg_id}'}})
    ON CREATE SET
        reg.subsystem_id = 'schema-registry',
        reg.type_name = 'U4_Subentity',
        reg.level = 'L4',
        reg.scope_ref = 'protocol',
        reg.name = 'Schema Registry',
        reg.kind = 'protocol-subsystem',
        reg.role_or_topic = 'schema-registry'

    MERGE (b:ProtocolNode {{id: '{bundle_id}'}})
    ON CREATE SET
        b.bundle_id = 'BUNDLE_REVIEWER_1_0_0',
        b.name = 'Reviewer Event Schemas Bundle v1.0.0',
        b.semver = '1.0.0',
        b.status = 'active',
        b.type_name = 'L4_Schema_Bundle',
        b.level = 'L4',
        b.scope_ref = 'protocol',
        b.hash = 'sha256:reviewer_1_0_0_placeholder'
    WITH reg, b
    MERGE (reg)-[:U4_GOVERNS]->(b)
    """
    r.execute_command("GRAPH.QUERY", graph_name, query)
    print(f"  ✓ BUNDLE_REVIEWER_1_0_0 (active)")
    print()

    # 3. Create Event_Schema nodes and wire relationships
    print("3️⃣  Creating Reviewer Event Schemas (17 schemas)...")
    for schema in REVIEWER_SCHEMAS:
        schema_id = f"protocol/Event_Schema/{schema['name']}"
        namespace_id = f"protocol/Topic_Namespace/{schema['namespace']}"

        query = f"""
        MATCH (b:ProtocolNode {{id: '{bundle_id}'}})
        MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
        MATCH (sig:ProtocolNode {{id: '{sig_id}'}})

        MERGE (es:ProtocolNode {{id: '{schema_id}'}})
        ON CREATE SET
            es.name = '{schema["name"]}',
            es.schema_uri = '{schema["schema_uri"]}',
            es.version = '{schema["version"]}',
            es.type_name = 'L4_Event_Schema',
            es.direction = '{schema["direction"]}',
            es.topic_pattern = '{schema["topic_pattern"]}',
            es.summary = '{schema["summary"]}',
            es.requires_sig_suite = 'SIG_ED25519_V1',
            es.sea_required = {str(schema["sea_required"]).lower()},
            es.cps = {str(schema["cps"]).lower()},
            es.schema_hash = 'sha256:placeholder',
            es.level = 'L4',
            es.scope_ref = 'protocol',
            es.payload_cap_kb = {schema["payload_cap_kb"]},
            es.rate_limit_per_min = {schema["rate_limit_per_min"]}
        WITH es, b, ns, sig
        MERGE (b)-[:U4_PUBLISHES_SCHEMA]->(es)
        MERGE (es)-[:U4_MAPS_TO_TOPIC]->(ns)
        MERGE (es)-[:U4_REQUIRES_SIG]->(sig)
        RETURN es.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)

        policy_marker = "🔐 STRICT" if schema["sea_required"] else "📝 FLEX  "
        direction_marker = "→" if schema["direction"] == "broadcast" else "↓"
        print(f"  {policy_marker} {schema['name']:<35} {direction_marker} {schema['namespace']}")

    print()

    # 4. Create Governance_Policy nodes and link to namespaces
    print("4️⃣  Creating Governance Policies (2 policies)...")
    for policy in GOVERNANCE_POLICIES:
        policy_id = f"protocol/Governance_Policy/{policy['policy_id']}"
        policy_uri = f"l4://law/{policy['policy_id']}.md"
        policy_hash = f"sha256:{policy['policy_id'].lower()}_placeholder"

        # Create policy node
        query = f"""
        MERGE (gp:ProtocolNode {{id: '{policy_id}'}})
        ON CREATE SET
            gp.policy_id = '{policy["policy_id"]}',
            gp.name = '{policy["name"]}',
            gp.type_name = 'L4_Governance_Policy',
            gp.description = '{policy["description"]}',
            gp.uri = '{policy_uri}',
            gp.hash = '{policy_hash}',
            gp.status = 'active',
            gp.summary = '{policy["description"]}',
            gp.level = 'L4',
            gp.scope_ref = 'protocol'
        RETURN gp.id
        """
        r.execute_command("GRAPH.QUERY", graph_name, query)

        # Link policy to governed namespaces
        for ns_name in policy["governs_namespaces"]:
            namespace_id = f"protocol/Topic_Namespace/{ns_name}"
            query = f"""
            MATCH (gp:ProtocolNode {{id: '{policy_id}'}})
            MATCH (ns:ProtocolNode {{id: '{namespace_id}'}})
            MERGE (gp)-[:U4_GOVERNS]->(ns)
            """
            r.execute_command("GRAPH.QUERY", graph_name, query)

        ns_count = len(policy["governs_namespaces"])
        print(f"  ✓ {policy['policy_id']:<40} - {ns_count} namespaces")

    print()
    print("=" * 70)
    print(f"✅ Ingested membrane-native reviewer event schemas")
    print()
    print("Summary:")
    print(f"  - 7 Topic_Namespace nodes (watcher, code, review, lint, failure, protocol.review, economy)")
    print(f"  - 17 Event_Schema nodes")
    print(f"  - 2 Governance_Policy nodes (POL_ORG_REVIEWER_V1, POL_PROTOCOL_MANDATE_V1)")
    print(f"  - 1 Schema_Bundle (BUNDLE_REVIEWER_1_0_0, active)")
    print()
    print("Policy Breakdown:")
    print(f"  🔐 STRICT (SEA required): protocol.review.* (mandate, ack, result, breach)")
    print(f"  📝 FLEX (signed only):    All org-scoped events (watcher, code, review, lint, failure, economy)")
    print()
    print("Event Direction Summary:")
    print(f"  ↓ inject (9):    watcher.local.change, code.diff.emit, review.request,")
    print(f"                   review.override.request, review.mandate, mandate.ack,")
    print(f"                   economy.quote.request")
    print(f"  → broadcast (8): lint.findings.emit, review.verdict, review.override.granted,")
    print(f"                   review.override.denied, failure.emit, mandate.result,")
    print(f"                   mandate.breach, economy.quote.response, budget.checked, budget.clamped")
    print()
    print("Next Steps:")
    print("  1. Re-export L4 registry: python tools/protocol/export_l4_public.py")
    print("  2. Expected: 47 + 17 = 64 Event_Schema nodes")
    print("  3. Implement R-200/300/400 linters (Felix)")
    print("  4. Build file watcher (Atlas)")
    print("  5. Build LintPanel UI (Iris)")
    print("  6. SafeBroadcaster will validate all reviewer events before emission")

if __name__ == "__main__":
    try:
        ingest_reviewer_events()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
