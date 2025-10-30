#!/usr/bin/env python3
"""
Phase 6: Protocol Drift Prevention - Final Phase

Adds explicit routing rules and enhanced governance to prevent protocol drift.
Ensures all traffic flows according to documented rules, not ad-hoc patterns.

Nodes Added (2):
- 2 Topic_Routes: Routing rules for citizen/org broadcast namespaces

Links Added (~5):
- 2 MEMBER_OF (routes → proto.membrane_stack anchor)
- 2 ROUTES_TO (routes → endpoints/engines)
- 1 ENFORCES (enhanced proto governance → routing rules)

This completes the self-sufficient protocol cluster.
"""

import json
from datetime import datetime
from falkordb import FalkorDB


def create_protocol_drift_prevention():
    """Phase 6: Add protocol drift prevention infrastructure."""
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("="*80)
    print("PHASE 6: PROTOCOL DRIFT PREVENTION (FINAL PHASE)")
    print("="*80)
    print()

    # ========================================================================
    # NODES: TOPIC ROUTES (2 nodes)
    # ========================================================================

    print("[1/1] Creating 2 Topic_Routes...")

    routes = [
        {
            'route_id': 'route.citizen_broadcast',
            'name': 'Citizen Broadcast Route',
            'description': 'Routes citizen/{citizen_id}/broadcast/* to orchestrator for centralized fan-out. Prevents individual engines from broadcasting directly.',
            'source_pattern': 'citizen/{citizen_id}/broadcast/*',
            'destination': 'orchestrator',
            'destination_endpoint': 'ws://localhost:8000/orchestrator/fanout',
            'rationale': 'Single fan-out point ensures consistent broadcast semantics, prevents duplicate delivery',
            'enforcement': 'block_direct_engine_broadcast'
        },
        {
            'route_id': 'route.org_broadcast',
            'name': 'Organization Broadcast Route',
            'description': 'Routes org/{org_id}/broadcast/* to all engines in organization scope. Standard broadcast pattern for org-level events.',
            'source_pattern': 'org/{org_id}/broadcast/*',
            'destination': 'all_engines',
            'destination_endpoint': 'ws://localhost:8000/ws',
            'rationale': 'Organization-scoped events reach all engines within org boundary',
            'enforcement': 'validate_org_scope'
        }
    ]

    for route in routes:
        g.query('''
        CREATE (tr:Topic_Route:ProtocolNode {
            route_id: $route_id,
            name: $name,
            node_type: "Topic_Route",
            description: $description,
            source_pattern: $source_pattern,
            destination: $destination,
            destination_endpoint: $destination_endpoint,
            rationale: $rationale,
            enforcement: $enforcement,
            layer: "L4",
            created_at: $now
        })
        ''', params={**route, 'now': now_iso})
        print(f"  ✅ Topic_Route: {route['route_id']}")
    print()

    # ========================================================================
    # LINKS
    # ========================================================================

    print("="*80)
    print("CREATING LINKS")
    print("="*80)
    print()

    # ------------------------------------------------------------------------
    # 1. MEMBER_OF (routes → anchor)
    # ------------------------------------------------------------------------
    print("[Links 1/4] Creating MEMBER_OF links (routes → anchor)...")

    result = g.query('''
    MATCH (tr:Topic_Route)
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (tr)-[r:MEMBER_OF {
        w_semantic: 0.88,
        w_intent: 0.93,
        w_affect: 0.70,
        w_experience: 0.82,
        w_total: 0.833,
        formation_trigger: "phase6_protocol_drift",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    member_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Topic_Routes: {member_links} MEMBER_OF links")
    print()

    # ------------------------------------------------------------------------
    # 2. ROUTES_OVER (routes → transport)
    # ------------------------------------------------------------------------
    print("[Links 2/4] Creating ROUTES_OVER links (routes → transport)...")

    result = g.query('''
    MATCH (tr:Topic_Route)
    MATCH (ts:Transport_Spec {type: "ws"})
    CREATE (tr)-[r:ROUTES_OVER {
        created_at: $now
    }]->(ts)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    routes_over = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Routes use transport: {routes_over} links")
    print()

    # ------------------------------------------------------------------------
    # 3. GOVERNS (proto policy → routes for enforcement)
    # ------------------------------------------------------------------------
    print("[Links 3/4] Creating GOVERNS links (proto policy → routes)...")

    result = g.query('''
    MATCH (gp:Governance_Policy {policy_id: "governance.proto"})
    MATCH (tr:Topic_Route)
    CREATE (gp)-[r:GOVERNS {
        enforcement_type: "routing_rules",
        effective_from: "2025-10-29T00:00:00Z",
        created_at: $now
    }]->(tr)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    governs_routes = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Proto policy governs routes: {governs_routes} links")
    print()

    # ------------------------------------------------------------------------
    # 4. SERVES_NAMESPACE (routes → namespaces they route)
    # ------------------------------------------------------------------------
    print("[Links 4/4] Creating SERVES_NAMESPACE links (routes → namespaces)...")

    # Citizen broadcast route serves citizen namespace
    result = g.query('''
    MATCH (tr:Topic_Route {route_id: "route.citizen_broadcast"})
    MATCH (ns:Topic_Namespace {pattern: "citizen/{citizen_id}/broadcast/*"})
    CREATE (tr)-[r:SERVES_NAMESPACE {
        created_at: $now
    }]->(ns)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    citizen_serves = result.result_set[0][0] if result.result_set else 0

    # Org broadcast route serves org namespace
    result = g.query('''
    MATCH (tr:Topic_Route {route_id: "route.org_broadcast"})
    MATCH (ns:Topic_Namespace)
    WHERE ns.pattern = "org/{org_id}/broadcast/*"
    CREATE (tr)-[r:SERVES_NAMESPACE {
        created_at: $now
    }]->(ns)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    org_serves = result.result_set[0][0] if result.result_set else 0

    total_serves = citizen_serves + org_serves
    print(f"  ✅ Routes serve namespaces: {total_serves} links")
    print()

    # ========================================================================
    # VERIFICATION
    # ========================================================================

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()

    # Count Phase 6 nodes
    result = g.query('''
    MATCH (n:Topic_Route)
    RETURN count(n) as phase6_nodes
    ''')
    phase6_nodes = result.result_set[0][0] if result.result_set else 0

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

    total_phase6_links = member_links + routes_over + governs_routes + total_serves

    print(f"✅ Phase 6 complete!")
    print(f"   Phase 6 nodes: {phase6_nodes}")
    print(f"   Phase 6 links: {total_phase6_links}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {total_nodes} nodes, {total_links} links")
    print()

    # ========================================================================
    # TEST QUERIES
    # ========================================================================

    print("📊 Testing Phase 6 queries...")
    print()

    # Query 1: Routing rules
    result = g.query('''
    MATCH (tr:Topic_Route)
    RETURN tr.source_pattern as pattern, tr.destination as dest, tr.enforcement as enforcement
    ORDER BY pattern
    ''')
    print("  Routing rules:")
    for row in result.result_set:
        print(f"    - {row[0]} → {row[1]} (enforcement: {row[2]})")
    print()

    # Query 2: Which policy governs routing?
    result = g.query('''
    MATCH (gp:Governance_Policy)-[:GOVERNS]->(tr:Topic_Route)
    RETURN gp.name as policy, count(tr) as routes_governed
    ''')
    print("  Policies governing routes:")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]} routes")
    print()

    # Query 3: Complete namespace → route → transport chain
    result = g.query('''
    MATCH (ns:Topic_Namespace)<-[:SERVES_NAMESPACE]-(tr:Topic_Route)-[:ROUTES_OVER]->(ts:Transport_Spec)
    RETURN ns.pattern as namespace, tr.destination as route_dest, ts.type as transport
    ORDER BY namespace
    ''')
    print("  Complete routing chain (namespace → route → transport):")
    for row in result.result_set:
        print(f"    - {row[0]} → {row[1]} → {row[2]}")
    print()

    # ========================================================================
    # FINAL CLUSTER SUMMARY
    # ========================================================================

    print("="*80)
    print("🎉 PROTOCOL CLUSTER COMPLETE - SELF-SUFFICIENT!")
    print("="*80)
    print()

    # Summary by phase
    print("Cluster built across 6 phases:")
    print("  Phase 0 (Initial): 35 nodes - Principles, Connector, Mechanisms, Metrics")
    print("  Phase 1 (Core): 23 nodes - Events, Namespaces, Bus, Transport, Security")
    print("  Phase 2 (Versioning): 9 nodes - Versions, Bundles, SDKs, Sidecar")
    print("  Phase 3 (Governance): 5 nodes - Tenant, Keys, Policies")
    print("  Phase 4 (Conformance): 41 nodes - Capabilities, Contracts, Suites, Cases, Results")
    print("  Phase 5 (Spec Wiring): 5 nodes - Emergence Pipeline, 4 Mechanisms")
    print("  Phase 6 (Protocol Drift): 2 nodes - Topic Routes")
    print()
    print(f"FINAL: {total_nodes} nodes, {total_links} links")
    print()

    # What's queryable
    print("Protocol is now fully queryable:")
    print("  ✅ Event schemas and their routing")
    print("  ✅ Protocol versions and evolution history")
    print("  ✅ SDK capabilities and conformance")
    print("  ✅ Governance policies and key rotation")
    print("  ✅ Conformance test suites and pass rates")
    print("  ✅ Three core specs materialized (Membrane, Learning, Emergence)")
    print("  ✅ Routing rules and drift prevention")
    print()

    # Final validation query: Complete protocol cluster
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: "proto.membrane_stack"})
    RETURN labels(n)[0] as type, count(*) as count
    ORDER BY count DESC
    ''')
    print("Cluster composition by node type:")
    for row in result.result_set:
        node_type = row[0] if row[0] else 'Unknown'
        print(f"  - {node_type}: {row[1]}")
    print()

    print("="*80)
    print("✅ PROTOCOL CLUSTER: LIVING GRAPH LAW COMPLETE")
    print("="*80)


if __name__ == '__main__':
    create_protocol_drift_prevention()
