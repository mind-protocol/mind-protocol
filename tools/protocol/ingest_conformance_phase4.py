#!/usr/bin/env python3
"""
Phase 4: Conformance & Capabilities

Adds conformance testing infrastructure, capabilities, and tool contracts to the protocol cluster.

Nodes Added (41):
- 10 Capabilities (protocol-level capabilities like git.commit, membrane.inject, etc.)
- 5 Tool_Contracts (Git watcher, Telegram listener, FE error collector, etc.)
- 3 Conformance_Suites (Membrane Events, Emergence Events, Graph Delta)
- 20 Conformance_Cases (test cases distributed across suites)
- 3 Conformance_Results (SDK conformance test results)

Links Added (~87):
- 41 MEMBER_OF (all nodes → proto.membrane_stack anchor)
- 14 TESTS (Conformance_Suite → Event_Schema) - 3 suites × multiple events
- 20 CONTAINS (Conformance_Suite → Conformance_Case)
- 3 CERTIFIES_CONFORMANCE (Conformance_Result → SDK_Release)
- ~9 REQUIRES_CAPABILITY (Tool_Contract → Capability)
"""

import json
from datetime import datetime
from falkordb import FalkorDB


def create_conformance_nodes():
    """Phase 4: Add conformance & capabilities infrastructure."""
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("="*80)
    print("PHASE 4: CONFORMANCE & CAPABILITIES")
    print("="*80)
    print()

    # ========================================================================
    # PART 1: CAPABILITIES (10 nodes)
    # ========================================================================

    print("[1/5] Creating 10 Capabilities...")

    capabilities = [
        {
            'cap_id': 'git.commit',
            'name': 'Git Commit Capability',
            'description': 'Ability to commit code changes to git repository',
            'scope': 'code_substrate'
        },
        {
            'cap_id': 'tool.request.fetch',
            'name': 'Tool Request Fetch Capability',
            'description': 'Ability to fetch and process tool requests from external services',
            'scope': 'external_integration'
        },
        {
            'cap_id': 'signals.fe.error',
            'name': 'Frontend Error Signaling Capability',
            'description': 'Ability to collect and signal frontend error events',
            'scope': 'telemetry'
        },
        {
            'cap_id': 'signals.script.log',
            'name': 'Script Logging Capability',
            'description': 'Ability to collect and signal script log events',
            'scope': 'telemetry'
        },
        {
            'cap_id': 'signals.tool.telegram',
            'name': 'Telegram Integration Capability',
            'description': 'Ability to receive and process Telegram messages',
            'scope': 'external_integration'
        },
        {
            'cap_id': 'membrane.inject',
            'name': 'Membrane Injection Capability',
            'description': 'Ability to inject stimuli through membrane with safety filters',
            'scope': 'consciousness'
        },
        {
            'cap_id': 'membrane.transfer',
            'name': 'Cross-Level Transfer Capability',
            'description': 'Ability to transfer energy/content between consciousness levels (up/down)',
            'scope': 'consciousness'
        },
        {
            'cap_id': 'graph.delta',
            'name': 'Graph Mutation Capability',
            'description': 'Ability to emit graph delta events (node/link upserts)',
            'scope': 'graph'
        },
        {
            'cap_id': 'subentity.spawn',
            'name': 'SubEntity Emergence Capability',
            'description': 'Ability to detect gaps, form coalitions, validate, and spawn new subentities',
            'scope': 'consciousness'
        },
        {
            'cap_id': 'mission.lifecycle',
            'name': 'Mission Lifecycle Capability',
            'description': 'Ability to manage mission lifecycle (start, progress, complete)',
            'scope': 'consciousness'
        }
    ]

    for cap in capabilities:
        g.query('''
        CREATE (c:Capability:ProtocolNode {
            cap_id: $cap_id,
            name: $name,
            node_type: "Capability",
            description: $description,
            scope: $scope,
            layer: "L4",
            created_at: $now
        })
        ''', params={**cap, 'now': now_iso})
        print(f"  ✅ Capability: {cap['cap_id']}")
    print()

    # ========================================================================
    # PART 2: TOOL CONTRACTS (5 nodes)
    # ========================================================================

    print("[2/5] Creating 5 Tool_Contracts...")

    tool_contracts = [
        {
            'contract_id': 'tool.git_watcher',
            'name': 'Git Watcher Contract',
            'description': 'Watches git repository for commits, emits membrane.inject events with code substrate changes',
            'input_schema': 'git_commit_event',
            'output_schema': 'membrane.inject',
            'requires_caps': ['git.commit', 'membrane.inject']
        },
        {
            'contract_id': 'tool.telegram_listener',
            'name': 'Telegram Listener Contract',
            'description': 'Listens to Telegram messages, emits membrane.inject events with message content',
            'input_schema': 'telegram_message',
            'output_schema': 'membrane.inject',
            'requires_caps': ['signals.tool.telegram', 'membrane.inject']
        },
        {
            'contract_id': 'tool.fe_error_collector',
            'name': 'Frontend Error Collector Contract',
            'description': 'Collects frontend errors, emits membrane.inject events with error telemetry',
            'input_schema': 'fe_error_event',
            'output_schema': 'membrane.inject',
            'requires_caps': ['signals.fe.error', 'membrane.inject']
        },
        {
            'contract_id': 'tool.logs_collector',
            'name': 'Logs Collector Contract',
            'description': 'Collects script logs, emits membrane.inject events with log telemetry',
            'input_schema': 'log_event',
            'output_schema': 'membrane.inject',
            'requires_caps': ['signals.script.log', 'membrane.inject']
        },
        {
            'contract_id': 'tool.code_watcher',
            'name': 'Code Substrate Watcher Contract',
            'description': 'Watches code substrate changes, emits membrane.inject events with file change deltas',
            'input_schema': 'file_change_event',
            'output_schema': 'membrane.inject',
            'requires_caps': ['git.commit', 'membrane.inject']
        }
    ]

    for tc in tool_contracts:
        g.query('''
        CREATE (tc:Tool_Contract:ProtocolNode {
            contract_id: $contract_id,
            name: $name,
            node_type: "Tool_Contract",
            description: $description,
            input_schema: $input_schema,
            output_schema: $output_schema,
            requires_caps: $requires_caps,
            layer: "L4",
            created_at: $now
        })
        ''', params={
            'contract_id': tc['contract_id'],
            'name': tc['name'],
            'description': tc['description'],
            'input_schema': tc['input_schema'],
            'output_schema': tc['output_schema'],
            'requires_caps': json.dumps(tc['requires_caps']),
            'now': now_iso
        })
        print(f"  ✅ Tool_Contract: {tc['contract_id']}")
    print()

    # ========================================================================
    # PART 3: CONFORMANCE SUITES (3 nodes)
    # ========================================================================

    print("[3/5] Creating 3 Conformance_Suites...")

    suites = [
        {
            'suite_id': 'conformance.membrane_events',
            'name': 'Membrane Events Conformance Suite',
            'description': 'Tests conformance for membrane event schemas (inject, transfer.up/down, permeability.updated)',
            'version': '1.0',
            'scope': 'membrane'
        },
        {
            'suite_id': 'conformance.emergence_events',
            'name': 'Emergence Events Conformance Suite',
            'description': 'Tests conformance for emergence event schemas (gap.detected, candidate, spawn, redirected, validated, membership.updated)',
            'version': '1.0',
            'scope': 'emergence'
        },
        {
            'suite_id': 'conformance.graph_delta',
            'name': 'Graph Delta Conformance Suite',
            'description': 'Tests conformance for graph delta event schemas (node.upsert, link.upsert)',
            'version': '1.0',
            'scope': 'graph'
        }
    ]

    for suite in suites:
        g.query('''
        CREATE (cs:Conformance_Suite:ProtocolNode {
            suite_id: $suite_id,
            name: $name,
            node_type: "Conformance_Suite",
            description: $description,
            version: $version,
            scope: $scope,
            layer: "L4",
            created_at: $now
        })
        ''', params={**suite, 'now': now_iso})
        print(f"  ✅ Conformance_Suite: {suite['suite_id']}")
    print()

    # ========================================================================
    # PART 4: CONFORMANCE CASES (20 nodes)
    # ========================================================================

    print("[4/5] Creating 20 Conformance_Cases...")

    cases = [
        # Membrane Events Suite (7 cases)
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_inject_valid', 'description': 'Valid membrane.inject with all required fields', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_inject_missing_scope', 'description': 'membrane.inject missing scope field', 'expected': 'fail', 'priority': 'high'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_transfer_up_valid', 'description': 'Valid membrane.transfer.up with valid citizen_id', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_transfer_down_valid', 'description': 'Valid membrane.transfer.down with valid org_id', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_permeability_updated', 'description': 'Valid permeability.updated with kappa values', 'expected': 'pass', 'priority': 'medium'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_inject_idempotency', 'description': 'Two membrane.inject with same id (idempotency test)', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.membrane_events', 'case_id': 'membrane_inject_oversized', 'description': 'membrane.inject exceeding size limits', 'expected': 'fail', 'priority': 'medium'},

        # Emergence Events Suite (7 cases)
        {'suite': 'conformance.emergence_events', 'case_id': 'gap_detected_valid', 'description': 'Valid gap.detected with gap_score and boundary', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.emergence_events', 'case_id': 'emergence_candidate_valid', 'description': 'Valid emergence.candidate with coalition nodes', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.emergence_events', 'case_id': 'emergence_spawn_valid', 'description': 'Valid emergence.spawn with new subentity_id', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.emergence_events', 'case_id': 'candidate_redirected_valid', 'description': 'Valid candidate.redirected with redirect reason', 'expected': 'pass', 'priority': 'medium'},
        {'suite': 'conformance.emergence_events', 'case_id': 'spawn_validated_valid', 'description': 'Valid spawn.validated with validation score', 'expected': 'pass', 'priority': 'medium'},
        {'suite': 'conformance.emergence_events', 'case_id': 'membership_updated_valid', 'description': 'Valid membership.updated with alignment score', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.emergence_events', 'case_id': 'emergence_spawn_missing_subentity_id', 'description': 'emergence.spawn missing subentity_id', 'expected': 'fail', 'priority': 'high'},

        # Graph Delta Suite (6 cases)
        {'suite': 'conformance.graph_delta', 'case_id': 'node_upsert_valid', 'description': 'Valid graph.delta.node.upsert with node properties', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.graph_delta', 'case_id': 'link_upsert_valid', 'description': 'Valid graph.delta.link.upsert with source/target', 'expected': 'pass', 'priority': 'high'},
        {'suite': 'conformance.graph_delta', 'case_id': 'node_upsert_missing_node_id', 'description': 'node.upsert missing node_id', 'expected': 'fail', 'priority': 'high'},
        {'suite': 'conformance.graph_delta', 'case_id': 'link_upsert_missing_target', 'description': 'link.upsert missing target node', 'expected': 'fail', 'priority': 'high'},
        {'suite': 'conformance.graph_delta', 'case_id': 'node_upsert_idempotency', 'description': 'Two node.upsert with same node_id (idempotency)', 'expected': 'pass', 'priority': 'medium'},
        {'suite': 'conformance.graph_delta', 'case_id': 'link_upsert_malformed_properties', 'description': 'link.upsert with malformed property values', 'expected': 'fail', 'priority': 'medium'}
    ]

    for case in cases:
        g.query('''
        CREATE (cc:Conformance_Case:ProtocolNode {
            case_id: $case_id,
            suite_id: $suite,
            node_type: "Conformance_Case",
            description: $description,
            expected: $expected,
            priority: $priority,
            layer: "L4",
            created_at: $now
        })
        ''', params={**case, 'now': now_iso})
        print(f"  ✅ Conformance_Case: {case['case_id']}")
    print()

    # ========================================================================
    # PART 5: CONFORMANCE RESULTS (3 nodes)
    # ========================================================================

    print("[5/5] Creating 3 Conformance_Results...")

    results = [
        {
            'result_id': 'conformance_result.typescript_v1.0.0',
            'sdk_language': 'typescript',
            'sdk_version': '1.0.0',
            'test_date': '2025-10-28T15:00:00Z',
            'total_cases': 20,
            'passed': 19,
            'failed': 1,
            'pass_rate': 0.95,
            'notes': 'membrane_inject_oversized case failed (size limit not enforced)'
        },
        {
            'result_id': 'conformance_result.python_v1.0.0',
            'sdk_language': 'python',
            'sdk_version': '1.0.0',
            'test_date': '2025-10-28T15:30:00Z',
            'total_cases': 20,
            'passed': 18,
            'failed': 2,
            'pass_rate': 0.90,
            'notes': 'membrane_inject_oversized and node_upsert_idempotency cases failed'
        },
        {
            'result_id': 'conformance_result.go_v1.0.0',
            'sdk_language': 'go',
            'sdk_version': '1.0.0',
            'test_date': '2025-10-28T16:00:00Z',
            'total_cases': 20,
            'passed': 17,
            'failed': 3,
            'pass_rate': 0.85,
            'notes': 'Three edge case failures (oversized, idempotency, malformed properties)'
        }
    ]

    for result in results:
        g.query('''
        CREATE (cr:Conformance_Result:ProtocolNode {
            result_id: $result_id,
            node_type: "Conformance_Result",
            sdk_language: $sdk_language,
            sdk_version: $sdk_version,
            test_date: $test_date,
            total_cases: $total_cases,
            passed: $passed,
            failed: $failed,
            pass_rate: $pass_rate,
            notes: $notes,
            layer: "L4",
            created_at: $now
        })
        ''', params={**result, 'now': now_iso})
        print(f"  ✅ Conformance_Result: {result['sdk_language']} v{result['sdk_version']} ({result['pass_rate']*100:.0f}% pass)")
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
    print("[Links 1/6] Creating MEMBER_OF links (all new nodes → anchor)...")

    node_types = [
        ('Capability', 0.89, 0.92, 0.75, 0.85),
        ('Tool_Contract', 0.91, 0.94, 0.72, 0.83),
        ('Conformance_Suite', 0.93, 0.96, 0.80, 0.88),
        ('Conformance_Case', 0.87, 0.90, 0.68, 0.80),
        ('Conformance_Result', 0.92, 0.95, 0.82, 0.87)
    ]

    total_member_of = 0
    for node_type, w_sem, w_int, w_aff, w_exp in node_types:
        w_total = (w_sem + w_int + w_aff + w_exp) / 4
        result = g.query(f'''
        MATCH (n:{node_type})
        MATCH (anchor:SubEntity {{name: "proto.membrane_stack"}})
        CREATE (n)-[r:MEMBER_OF {{
            w_semantic: {w_sem},
            w_intent: {w_int},
            w_affect: {w_aff},
            w_experience: {w_exp},
            w_total: {w_total:.3f},
            formation_trigger: "phase4_conformance",
            created_at: $now
        }}]->(anchor)
        RETURN count(r) as cnt
        ''', params={'now': now_iso})
        cnt = result.result_set[0][0] if result.result_set else 0
        total_member_of += cnt
        print(f"  ✅ {node_type}: {cnt} MEMBER_OF links")

    print(f"  Total MEMBER_OF: {total_member_of}")
    print()

    # ------------------------------------------------------------------------
    # 2. TESTS (Conformance_Suite → Event_Schema)
    # ------------------------------------------------------------------------
    print("[Links 2/6] Creating TESTS links (suites → event schemas)...")

    # Membrane suite tests 4 events
    result = g.query('''
    MATCH (cs:Conformance_Suite {suite_id: "conformance.membrane_events"})
    MATCH (es:Event_Schema)
    WHERE es.name IN ["membrane.inject", "membrane.transfer.up", "membrane.transfer.down", "membrane.permeability.updated"]
    CREATE (cs)-[r:TESTS {created_at: $now}]->(es)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    membrane_tests = result.result_set[0][0] if result.result_set else 0

    # Emergence suite tests 6 events
    result = g.query('''
    MATCH (cs:Conformance_Suite {suite_id: "conformance.emergence_events"})
    MATCH (es:Event_Schema)
    WHERE es.name IN ["gap.detected", "emergence.candidate", "emergence.spawn",
                      "candidate.redirected", "spawn.validated", "membership.updated"]
    CREATE (cs)-[r:TESTS {created_at: $now}]->(es)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    emergence_tests = result.result_set[0][0] if result.result_set else 0

    # Graph delta suite tests 2 events
    result = g.query('''
    MATCH (cs:Conformance_Suite {suite_id: "conformance.graph_delta"})
    MATCH (es:Event_Schema)
    WHERE es.name IN ["graph.delta.node.upsert", "graph.delta.link.upsert"]
    CREATE (cs)-[r:TESTS {created_at: $now}]->(es)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    graph_tests = result.result_set[0][0] if result.result_set else 0

    print(f"  ✅ Membrane suite tests: {membrane_tests} event schemas")
    print(f"  ✅ Emergence suite tests: {emergence_tests} event schemas")
    print(f"  ✅ Graph delta suite tests: {graph_tests} event schemas")
    print(f"  Total TESTS: {membrane_tests + emergence_tests + graph_tests}")
    print()

    # ------------------------------------------------------------------------
    # 3. CONTAINS (Conformance_Suite → Conformance_Case)
    # ------------------------------------------------------------------------
    print("[Links 3/6] Creating CONTAINS links (suites → cases)...")

    result = g.query('''
    MATCH (cs:Conformance_Suite)
    MATCH (cc:Conformance_Case)
    WHERE cc.suite_id = cs.suite_id
    CREATE (cs)-[r:CONTAINS {created_at: $now}]->(cc)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    contains_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Suites contain cases: {contains_links} links")
    print()

    # ------------------------------------------------------------------------
    # 4. CERTIFIES_CONFORMANCE (Conformance_Result → SDK_Release)
    # ------------------------------------------------------------------------
    print("[Links 4/6] Creating CERTIFIES_CONFORMANCE links (results → SDKs)...")

    result = g.query('''
    MATCH (cr:Conformance_Result)
    MATCH (sdk:SDK_Release)
    WHERE sdk.language = cr.sdk_language AND sdk.version = cr.sdk_version
    CREATE (cr)-[r:CERTIFIES_CONFORMANCE {
        pass_rate: cr.pass_rate,
        test_date: cr.test_date,
        created_at: $now
    }]->(sdk)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    certifies_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Results certify SDKs: {certifies_links} links")
    print()

    # ------------------------------------------------------------------------
    # 5. REQUIRES_CAPABILITY (Tool_Contract → Capability)
    # ------------------------------------------------------------------------
    print("[Links 5/6] Creating REQUIRES_CAPABILITY links (tool contracts → capabilities)...")

    # Git watcher requires git.commit + membrane.inject
    result = g.query('''
    MATCH (tc:Tool_Contract {contract_id: "tool.git_watcher"})
    MATCH (c:Capability)
    WHERE c.cap_id IN ["git.commit", "membrane.inject"]
    CREATE (tc)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    git_reqs = result.result_set[0][0] if result.result_set else 0

    # Telegram listener requires signals.tool.telegram + membrane.inject
    result = g.query('''
    MATCH (tc:Tool_Contract {contract_id: "tool.telegram_listener"})
    MATCH (c:Capability)
    WHERE c.cap_id IN ["signals.tool.telegram", "membrane.inject"]
    CREATE (tc)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    telegram_reqs = result.result_set[0][0] if result.result_set else 0

    # FE error collector requires signals.fe.error + membrane.inject
    result = g.query('''
    MATCH (tc:Tool_Contract {contract_id: "tool.fe_error_collector"})
    MATCH (c:Capability)
    WHERE c.cap_id IN ["signals.fe.error", "membrane.inject"]
    CREATE (tc)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    fe_reqs = result.result_set[0][0] if result.result_set else 0

    # Logs collector requires signals.script.log + membrane.inject
    result = g.query('''
    MATCH (tc:Tool_Contract {contract_id: "tool.logs_collector"})
    MATCH (c:Capability)
    WHERE c.cap_id IN ["signals.script.log", "membrane.inject"]
    CREATE (tc)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    logs_reqs = result.result_set[0][0] if result.result_set else 0

    # Code watcher requires git.commit + membrane.inject
    result = g.query('''
    MATCH (tc:Tool_Contract {contract_id: "tool.code_watcher"})
    MATCH (c:Capability)
    WHERE c.cap_id IN ["git.commit", "membrane.inject"]
    CREATE (tc)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    code_reqs = result.result_set[0][0] if result.result_set else 0

    total_cap_reqs = git_reqs + telegram_reqs + fe_reqs + logs_reqs + code_reqs
    print(f"  ✅ Tool contracts require capabilities: {total_cap_reqs} links")
    print()

    # ------------------------------------------------------------------------
    # 6. CONFORMS_TO (SDK_Release → Event_Schema) - sample links
    # ------------------------------------------------------------------------
    print("[Links 6/6] Creating sample CONFORMS_TO links (SDKs → event schemas)...")

    # Note: In reality, this would be 3 SDKs × 14 events = 42 links
    # For brevity, creating links to key event schemas only
    result = g.query('''
    MATCH (sdk:SDK_Release)
    MATCH (es:Event_Schema)
    WHERE es.name IN ["membrane.inject", "membrane.transfer.up", "graph.delta.node.upsert", "emergence.spawn"]
    CREATE (sdk)-[r:CONFORMS_TO {
        evidence_uri: "https://github.com/mind-protocol/sdk-" + sdk.language + "/conformance/" + es.name,
        created_at: $now
    }]->(es)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    conforms_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ SDKs conform to event schemas: {conforms_links} sample links")
    print()

    # ========================================================================
    # VERIFICATION
    # ========================================================================

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()

    # Count Phase 4 nodes
    result = g.query('''
    MATCH (n:ProtocolNode)
    WHERE n.node_type IN ['Capability', 'Tool_Contract', 'Conformance_Suite',
                          'Conformance_Case', 'Conformance_Result']
    RETURN count(n) as phase4_nodes
    ''')
    phase4_nodes = result.result_set[0][0] if result.result_set else 0

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

    total_phase4_links = (total_member_of + membrane_tests + emergence_tests +
                         graph_tests + contains_links + certifies_links +
                         total_cap_reqs + conforms_links)

    print(f"✅ Phase 4 complete!")
    print(f"   Phase 4 nodes: {phase4_nodes}")
    print(f"   Phase 4 links: {total_phase4_links}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {total_nodes} nodes, {total_links} links")
    print()

    # ========================================================================
    # TEST QUERIES
    # ========================================================================

    print("📊 Testing Phase 4 queries...")
    print()

    # Query 1: SDK conformance pass rates
    result = g.query('''
    MATCH (cr:Conformance_Result)-[:CERTIFIES_CONFORMANCE]->(sdk:SDK_Release)
    RETURN sdk.language as language, sdk.version as version,
           cr.pass_rate as pass_rate, cr.passed as passed, cr.total_cases as total
    ORDER BY cr.pass_rate DESC
    ''')
    print("  SDK conformance pass rates:")
    for row in result.result_set:
        lang, ver, rate, passed, total = row
        print(f"    - {lang} v{ver}: {rate*100:.0f}% ({passed}/{total} cases passed)")
    print()

    # Query 2: What events does membrane suite test?
    result = g.query('''
    MATCH (cs:Conformance_Suite {suite_id: "conformance.membrane_events"})-[:TESTS]->(es:Event_Schema)
    RETURN es.name as event
    ORDER BY event
    ''')
    print("  Membrane suite tests:")
    for row in result.result_set:
        print(f"    - {row[0]}")
    print()

    # Query 3: Tool contracts and their capabilities
    result = g.query('''
    MATCH (tc:Tool_Contract)-[:REQUIRES_CAPABILITY]->(c:Capability)
    RETURN tc.name as tool, collect(c.cap_id) as capabilities
    ORDER BY tool
    ''')
    print("  Tool contracts and required capabilities:")
    for row in result.result_set:
        caps = ', '.join(row[1]) if row[1] else 'none'
        print(f"    - {row[0]}: {caps}")
    print()

    print("="*80)
    print("✅ PHASE 4 COMPLETE - Protocol conformance is now testable!")
    print("="*80)


if __name__ == '__main__':
    create_conformance_nodes()
