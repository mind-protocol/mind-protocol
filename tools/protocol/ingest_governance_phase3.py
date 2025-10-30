#!/usr/bin/env python3
"""
Phase 3: Governance & Identity

Adds tenant management, key rotation, and governance policies to the protocol cluster.

Nodes Added (5):
- 1 Tenant (Mind Protocol organization)
- 2 Tenant_Keys (current v2, rotated v1)
- 2 Governance_Policies (default policy, proto namespace policy)

Links Added (12):
- 5 MEMBER_OF (all nodes → proto.membrane_stack anchor)
- 2 ASSIGNED_TO_TENANT (keys → tenant)
- 2 SIGNED_WITH (keys → signature suite)
- 3 GOVERNS (policies → namespaces)
"""

import json
from datetime import datetime
from falkordb import FalkorDB


def create_governance_nodes():
    """Phase 3: Add governance infrastructure."""
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("="*80)
    print("PHASE 3: GOVERNANCE & IDENTITY")
    print("="*80)
    print()

    # ========================================================================
    # NODES
    # ========================================================================

    print("[1/3] Creating 1 Tenant...")
    g.query('''
    CREATE (t:Tenant:ProtocolNode {
        org_id: "mind-protocol",
        display_name: "Mind Protocol",
        node_type: "Tenant",
        description: "Primary organizational tenant for Mind Protocol consciousness infrastructure",
        contact_email: "ops@mindprotocol.ai",
        created_at: $now,
        layer: "L4"
    })
    ''', params={'now': now_iso})
    print("  ✅ Tenant: mind-protocol")
    print()

    print("[2/3] Creating 2 Tenant_Keys...")

    # Current key (v2)
    g.query('''
    CREATE (tk:Tenant_Key:ProtocolNode {
        key_id: "mind-protocol-key-v2",
        version: "v2",
        node_type: "Tenant_Key",
        description: "Current active signing key for Mind Protocol tenant",
        algorithm: "ed25519",
        pubkey: "base64:AAAA...ZZZZ",
        status: "active",
        issued_at: "2025-10-01T00:00:00Z",
        expires_at: "2026-10-01T00:00:00Z",
        layer: "L4",
        created_at: $now
    })
    ''', params={'now': now_iso})
    print("  ✅ Tenant_Key: v2 (active)")

    # Rotated key (v1, expired)
    g.query('''
    CREATE (tk:Tenant_Key:ProtocolNode {
        key_id: "mind-protocol-key-v1",
        version: "v1",
        node_type: "Tenant_Key",
        description: "Rotated signing key (expired) - retained for signature verification of historical events",
        algorithm: "ed25519",
        pubkey: "base64:1111...9999",
        status: "rotated",
        issued_at: "2025-01-01T00:00:00Z",
        expires_at: "2025-10-01T00:00:00Z",
        layer: "L4",
        created_at: $now
    })
    ''', params={'now': now_iso})
    print("  ✅ Tenant_Key: v1 (rotated)")
    print()

    print("[3/3] Creating 2 Governance_Policies...")

    # Default policy for broadcast namespaces
    defaults = {
        "ack_policy": "leader",
        "lanes": 3,
        "backpressure": "drop_oldest",
        "max_batch_size": 100,
        "flush_interval_ms": 50
    }

    g.query('''
    CREATE (gp:Governance_Policy:ProtocolNode {
        policy_id: "governance.default",
        name: "Default Broadcast Policy",
        node_type: "Governance_Policy",
        description: "Default governance policy for org/citizen broadcast namespaces",
        defaults: $defaults,
        scope: "org",
        layer: "L4",
        created_at: $now
    })
    ''', params={'defaults': json.dumps(defaults), 'now': now_iso})
    print("  ✅ Governance_Policy: governance.default")

    # Proto namespace policy (stricter)
    proto_defaults = {
        "ack_policy": "all",
        "lanes": 1,
        "backpressure": "block",
        "max_batch_size": 10,
        "flush_interval_ms": 0,
        "require_signature": True,
        "require_envelope_schema": True,
        "require_spec_name_rev": True,
        "idempotency_check": True,
        "evidence_max_size_kb": 64
    }

    g.query('''
    CREATE (gp:Governance_Policy:ProtocolNode {
        policy_id: "governance.proto",
        name: "Protocol Governance Policy",
        node_type: "Governance_Policy",
        description: "Strict governance policy for protocol drift prevention (org/{org_id}/proto/* namespace)",
        defaults: $defaults,
        scope: "global",
        layer: "L4",
        created_at: $now
    })
    ''', params={'defaults': json.dumps(proto_defaults), 'now': now_iso})
    print("  ✅ Governance_Policy: governance.proto")
    print()

    # ========================================================================
    # LINKS
    # ========================================================================

    print("="*80)
    print("CREATING LINKS")
    print("="*80)
    print()

    # ------------------------------------------------------------------------
    # 1. MEMBER_OF (all nodes → anchor)
    # ------------------------------------------------------------------------
    print("[Links 1/4] Creating MEMBER_OF links (all new nodes → anchor)...")

    # Tenant MEMBER_OF anchor
    result = g.query('''
    MATCH (t:Tenant {org_id: "mind-protocol"})
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (t)-[r:MEMBER_OF {
        w_semantic: 0.92,
        w_intent: 0.90,
        w_affect: 0.65,
        w_experience: 0.80,
        w_total: 0.818,
        formation_trigger: "phase3_governance",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    tenant_links = result.result_set[0][0] if result.result_set else 0

    # Tenant_Key MEMBER_OF anchor
    result = g.query('''
    MATCH (tk:Tenant_Key)
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (tk)-[r:MEMBER_OF {
        w_semantic: 0.88,
        w_intent: 0.95,
        w_affect: 0.70,
        w_experience: 0.85,
        w_total: 0.845,
        formation_trigger: "phase3_governance",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    key_links = result.result_set[0][0] if result.result_set else 0

    # Governance_Policy MEMBER_OF anchor
    result = g.query('''
    MATCH (gp:Governance_Policy)
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (gp)-[r:MEMBER_OF {
        w_semantic: 0.90,
        w_intent: 0.93,
        w_affect: 0.68,
        w_experience: 0.82,
        w_total: 0.833,
        formation_trigger: "phase3_governance",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    policy_links = result.result_set[0][0] if result.result_set else 0

    print(f"  ✅ Tenant: {tenant_links} MEMBER_OF links")
    print(f"  ✅ Tenant_Key: {key_links} MEMBER_OF links")
    print(f"  ✅ Governance_Policy: {policy_links} MEMBER_OF links")
    print(f"  Total MEMBER_OF: {tenant_links + key_links + policy_links}")
    print()

    # ------------------------------------------------------------------------
    # 2. ASSIGNED_TO_TENANT (keys → tenant)
    # ------------------------------------------------------------------------
    print("[Links 2/4] Creating ASSIGNED_TO_TENANT links (keys → tenant)...")

    result = g.query('''
    MATCH (tk:Tenant_Key)
    MATCH (t:Tenant {org_id: "mind-protocol"})
    CREATE (tk)-[r:ASSIGNED_TO_TENANT {
        assigned_at: tk.issued_at,
        created_at: $now
    }]->(t)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    assigned_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Keys assigned to tenant: {assigned_links} links")
    print()

    # ------------------------------------------------------------------------
    # 3. SIGNED_WITH (keys → signature suite)
    # ------------------------------------------------------------------------
    print("[Links 3/4] Creating SIGNED_WITH links (keys → signature suite)...")

    result = g.query('''
    MATCH (tk:Tenant_Key {algorithm: "ed25519"})
    MATCH (ss:Signature_Suite {algorithm: "ed25519"})
    CREATE (tk)-[r:SIGNED_WITH {
        created_at: $now
    }]->(ss)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    signed_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Keys signed with ed25519 suite: {signed_links} links")
    print()

    # ------------------------------------------------------------------------
    # 4. GOVERNS (policies → namespaces)
    # ------------------------------------------------------------------------
    print("[Links 4/4] Creating GOVERNS links (policies → namespaces)...")

    # Default policy governs org and citizen broadcast namespaces
    result = g.query('''
    MATCH (gp:Governance_Policy {policy_id: "governance.default"})
    MATCH (ns:Topic_Namespace)
    WHERE ns.pattern IN [
        "org/{org_id}/broadcast/*",
        "citizen/{citizen_id}/broadcast/*"
    ]
    CREATE (gp)-[r:GOVERNS {
        effective_from: "2025-08-01T00:00:00Z",
        created_at: $now
    }]->(ns)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    default_governs = result.result_set[0][0] if result.result_set else 0

    # Proto policy governs proto namespace
    result = g.query('''
    MATCH (gp:Governance_Policy {policy_id: "governance.proto"})
    MATCH (ns:Topic_Namespace {pattern: "org/{org_id}/proto/*"})
    CREATE (gp)-[r:GOVERNS {
        effective_from: "2025-10-27T00:00:00Z",
        created_at: $now
    }]->(ns)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    proto_governs = result.result_set[0][0] if result.result_set else 0

    print(f"  ✅ Default policy governs: {default_governs} namespaces")
    print(f"  ✅ Proto policy governs: {proto_governs} namespaces")
    print(f"  Total GOVERNS: {default_governs + proto_governs}")
    print()

    # ========================================================================
    # VERIFICATION
    # ========================================================================

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()

    # Count Phase 3 nodes
    result = g.query('''
    MATCH (n:ProtocolNode)
    WHERE n.node_type IN ['Tenant', 'Tenant_Key', 'Governance_Policy']
    RETURN count(n) as phase3_nodes
    ''')
    phase3_nodes = result.result_set[0][0] if result.result_set else 0

    # Count total cluster nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: "proto.membrane_stack"})
    RETURN count(n) as cluster_nodes
    ''')
    cluster_nodes = result.result_set[0][0] if result.result_set else 0

    # Count total protocol graph
    result = g.query('MATCH (n) RETURN count(n) as total_nodes')
    total_nodes = result.result_set[0][0] if result.result_set else 0

    result = g.query('MATCH ()-[r]->() RETURN count(r) as total_links')
    total_links = result.result_set[0][0] if result.result_set else 0

    total_member_of = tenant_links + key_links + policy_links
    total_phase3_links = total_member_of + assigned_links + signed_links + default_governs + proto_governs

    print(f"✅ Phase 3 complete!")
    print(f"   Phase 3 nodes: {phase3_nodes}")
    print(f"   Phase 3 links: {total_phase3_links}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {total_nodes} nodes, {total_links} links")
    print()

    # ========================================================================
    # TEST QUERIES
    # ========================================================================

    print("📊 Testing Phase 3 queries...")
    print()

    # Query 1: Active tenant keys
    result = g.query('''
    MATCH (tk:Tenant_Key {status: "active"})-[:ASSIGNED_TO_TENANT]->(t:Tenant)
    RETURN t.org_id as org, tk.version as key_version, tk.expires_at as expires
    ''')
    print("  Active tenant keys:")
    for row in result.result_set:
        print(f"    - {row[0]}: key {row[1]}, expires {row[2]}")
    print()

    # Query 2: Governance policies per namespace
    result = g.query('''
    MATCH (gp:Governance_Policy)-[:GOVERNS]->(ns:Topic_Namespace)
    RETURN ns.pattern as namespace, gp.name as policy
    ORDER BY ns.pattern
    ''')
    print("  Governance policies per namespace:")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]}")
    print()

    # Query 3: Key rotation history
    result = g.query('''
    MATCH (tk:Tenant_Key)-[:ASSIGNED_TO_TENANT]->(t:Tenant {org_id: "mind-protocol"})
    RETURN tk.version as version, tk.status as status, tk.issued_at as issued, tk.expires_at as expires
    ORDER BY tk.issued_at
    ''')
    print("  Key rotation history (mind-protocol):")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]} (issued: {row[2]}, expires: {row[3]})")
    print()

    print("="*80)
    print("✅ PHASE 3 COMPLETE - Protocol governance is now enforceable!")
    print("="*80)


if __name__ == '__main__':
    create_governance_nodes()
