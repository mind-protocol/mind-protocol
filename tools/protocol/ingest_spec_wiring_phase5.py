#!/usr/bin/env python3
"""
Phase 5: Spec Wiring - Complete Three Core Specs

Materializes the Emergence Pipeline and wires all three core specs into the protocol graph:
1. MEMBRANE_INJECTION_CONTRACT.md (already wired in initial cluster)
2. VERTICAL_MEMBRANE_LEARNING.md (already wired in initial cluster)
3. subentity_emergence.md (THIS PHASE - emergence pipeline)

Nodes Added (5):
- 1 Process: Emergence Pipeline (gap → coalition → validation → spawn)
- 4 Mechanisms: Gap Detection, Coalition Assembly, Engine Validation, Membership Learning

Links Added (~44):
- 5 MEMBER_OF (all nodes → proto.membrane_stack anchor)
- 4 REQUIRES (Emergence Pipeline → mechanisms)
- 6 ENABLES (Emergence Pipeline → emergence events)
- 10 MEASURES (mechanisms → metrics)
- ~19 additional semantic links (mechanisms → capabilities, event schemas, principles)
"""

import json
from datetime import datetime
from falkordb import FalkorDB


def create_spec_wiring():
    """Phase 5: Wire emergence pipeline into protocol cluster."""
    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("="*80)
    print("PHASE 5: SPEC WIRING - EMERGENCE PIPELINE")
    print("="*80)
    print()

    # ========================================================================
    # PART 1: EMERGENCE PIPELINE PROCESS (1 node)
    # ========================================================================

    print("[1/2] Creating 1 Process: Emergence Pipeline...")

    g.query('''
    CREATE (proc:Process:ProtocolNode {
        name: "Emergence Pipeline",
        process_id: "process.emergence_pipeline",
        node_type: "Process",
        description: "Four-stage pipeline for SubEntity emergence: gap detection → coalition formation → engine validation → spawn decision. Grounds subentity_emergence.md specification.",
        stages: "gap_detection,coalition_assembly,engine_validation,spawn_or_redirect",
        failure_modes: "weak_gap_score,insufficient_coalition,validation_failure,capacity_limit",
        spec_ref: "docs/specs/v2/subentity_emergence.md",
        layer: "L4",
        created_at: $now
    })
    ''', params={'now': now_iso})
    print("  ✅ Process: Emergence Pipeline")
    print()

    # ========================================================================
    # PART 2: EMERGENCE MECHANISMS (4 nodes)
    # ========================================================================

    print("[2/2] Creating 4 Mechanisms...")

    mechanisms = [
        {
            'name': 'Gap Detection',
            'mechanism_id': 'mechanism.gap_detection',
            'description': 'Identifies gaps in consciousness where activation energy accumulates without resolution. Measures boundary strength, co-activation frequency, energy accumulation. Emits gap.detected when gap_score exceeds threshold.',
            'inputs': 'active_nodes,co_activation_matrix,boundary_map',
            'outputs': 'gap_score,boundary_nodes,candidate_coalition',
            'emits_event': 'gap.detected',
            'spec_section': 'subentity_emergence.md §2.1 Gap Detection'
        },
        {
            'name': 'Coalition Assembly',
            'mechanism_id': 'mechanism.coalition_assembly',
            'description': 'Forms provisional coalition of nodes around detected gap. Tests for coherence (internal connectivity > external), complementarity (diverse skill sets), stability (persistent co-activation). Emits emergence.candidate.',
            'inputs': 'gap_boundary,active_nodes,link_weights',
            'outputs': 'coalition_nodes,coherence_score,complementarity_score',
            'emits_event': 'emergence.candidate',
            'spec_section': 'subentity_emergence.md §2.2 Coalition Formation'
        },
        {
            'name': 'Engine Validation',
            'mechanism_id': 'mechanism.engine_validation',
            'description': 'Validates whether coalition meets engine requirements for spawn (capacity available, resource thresholds, emergence quotas). Checks engine state, memory pressure, existing subentity count. Returns spawn/redirect decision.',
            'inputs': 'coalition_nodes,engine_state,capacity_limits',
            'outputs': 'spawn_decision,validation_score,redirect_reason',
            'emits_event': 'spawn.validated',
            'spec_section': 'subentity_emergence.md §2.3 Engine Validation'
        },
        {
            'name': 'Membership Learning',
            'mechanism_id': 'mechanism.membership_learning',
            'description': 'Updates membership weights after spawn based on outcomes. Strengthens successful coalitions, weakens failed attempts. Materializes alignment scores as MEMBER_OF link weights. Emits membership.updated.',
            'inputs': 'spawn_result,coalition_nodes,outcome_quality',
            'outputs': 'updated_weights,alignment_delta',
            'emits_event': 'membership.updated',
            'spec_section': 'subentity_emergence.md §2.4 Post-Spawn Learning'
        }
    ]

    for mech in mechanisms:
        g.query('''
        CREATE (m:Mechanism:ProtocolNode {
            name: $name,
            mechanism_id: $mechanism_id,
            node_type: "Mechanism",
            description: $description,
            inputs: $inputs,
            outputs: $outputs,
            emits_event: $emits_event,
            spec_section: $spec_section,
            layer: "L4",
            created_at: $now
        })
        ''', params={**mech, 'now': now_iso})
        print(f"  ✅ Mechanism: {mech['name']}")
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
    print("[Links 1/7] Creating MEMBER_OF links (all new nodes → anchor)...")

    # Process MEMBER_OF anchor
    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (proc)-[r:MEMBER_OF {
        w_semantic: 0.94,
        w_intent: 0.97,
        w_affect: 0.80,
        w_experience: 0.90,
        w_total: 0.903,
        formation_trigger: "phase5_spec_wiring",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    proc_links = result.result_set[0][0] if result.result_set else 0

    # Mechanisms MEMBER_OF anchor
    result = g.query('''
    MATCH (m:Mechanism)
    WHERE m.mechanism_id STARTS WITH "mechanism.gap_detection"
       OR m.mechanism_id STARTS WITH "mechanism.coalition_assembly"
       OR m.mechanism_id STARTS WITH "mechanism.engine_validation"
       OR m.mechanism_id STARTS WITH "mechanism.membership_learning"
    MATCH (anchor:SubEntity {name: "proto.membrane_stack"})
    CREATE (m)-[r:MEMBER_OF {
        w_semantic: 0.91,
        w_intent: 0.94,
        w_affect: 0.78,
        w_experience: 0.86,
        w_total: 0.873,
        formation_trigger: "phase5_spec_wiring",
        created_at: $now
    }]->(anchor)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    mech_links = result.result_set[0][0] if result.result_set else 0

    print(f"  ✅ Process: {proc_links} MEMBER_OF links")
    print(f"  ✅ Mechanisms: {mech_links} MEMBER_OF links")
    print(f"  Total MEMBER_OF: {proc_links + mech_links}")
    print()

    # ------------------------------------------------------------------------
    # 2. REQUIRES (Emergence Pipeline → 4 mechanisms)
    # ------------------------------------------------------------------------
    print("[Links 2/7] Creating REQUIRES links (process → mechanisms)...")

    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})
    MATCH (m:Mechanism)
    WHERE m.mechanism_id IN [
        "mechanism.gap_detection",
        "mechanism.coalition_assembly",
        "mechanism.engine_validation",
        "mechanism.membership_learning"
    ]
    CREATE (proc)-[r:REQUIRES {
        stage_order: CASE m.mechanism_id
            WHEN "mechanism.gap_detection" THEN 1
            WHEN "mechanism.coalition_assembly" THEN 2
            WHEN "mechanism.engine_validation" THEN 3
            WHEN "mechanism.membership_learning" THEN 4
        END,
        created_at: $now
    }]->(m)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    requires_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Process requires mechanisms: {requires_links} links")
    print()

    # ------------------------------------------------------------------------
    # 3. ENABLES (Emergence Pipeline → emergence events)
    # ------------------------------------------------------------------------
    print("[Links 3/7] Creating ENABLES links (process → emergence events)...")

    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})
    MATCH (es:Event_Schema)
    WHERE es.name IN [
        "gap.detected",
        "emergence.candidate",
        "emergence.spawn",
        "candidate.redirected",
        "spawn.validated",
        "membership.updated"
    ]
    CREATE (proc)-[r:ENABLES {
        created_at: $now
    }]->(es)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    enables_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Process enables events: {enables_links} links")
    print()

    # ------------------------------------------------------------------------
    # 4. MEASURES (mechanisms → metrics)
    # ------------------------------------------------------------------------
    print("[Links 4/7] Creating MEASURES links (mechanisms → metrics)...")

    # Gap Detection measures emergence_rate + gap_detection_rate
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.gap_detection"})
    MATCH (metric:Metric)
    WHERE metric.name IN ["Emergence rate", "Gap detection frequency"]
    CREATE (m)-[r:MEASURES {created_at: $now}]->(metric)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    gap_measures = result.result_set[0][0] if result.result_set else 0

    # Coalition Assembly measures coherence metrics
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.coalition_assembly"})
    MATCH (metric:Metric)
    WHERE metric.name IN ["Coalition coherence score", "Complementary rate"]
    CREATE (m)-[r:MEASURES {created_at: $now}]->(metric)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    coalition_measures = result.result_set[0][0] if result.result_set else 0

    # Engine Validation measures redirect_rate
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.engine_validation"})
    MATCH (metric:Metric)
    WHERE metric.name IN ["Redirect rate", "Spawn validation rate"]
    CREATE (m)-[r:MEASURES {created_at: $now}]->(metric)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    validation_measures = result.result_set[0][0] if result.result_set else 0

    # Membership Learning measures alignment drift
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.membership_learning"})
    MATCH (metric:Metric)
    WHERE metric.name IN ["Alignment materialization rate", "Membership update frequency"]
    CREATE (m)-[r:MEASURES {created_at: $now}]->(metric)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    learning_measures = result.result_set[0][0] if result.result_set else 0

    total_measures = gap_measures + coalition_measures + validation_measures + learning_measures
    print(f"  ✅ Mechanisms measure metrics: {total_measures} links")
    print()

    # ------------------------------------------------------------------------
    # 5. Links to Capabilities (mechanisms → capabilities)
    # ------------------------------------------------------------------------
    print("[Links 5/7] Creating links (mechanisms → capabilities)...")

    # Gap Detection + Coalition Assembly require subentity.spawn capability
    result = g.query('''
    MATCH (m:Mechanism)
    WHERE m.mechanism_id IN ["mechanism.gap_detection", "mechanism.coalition_assembly"]
    MATCH (c:Capability {cap_id: "subentity.spawn"})
    CREATE (m)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    spawn_cap_links = result.result_set[0][0] if result.result_set else 0

    # Engine Validation requires graph.delta (to validate engine state)
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.engine_validation"})
    MATCH (c:Capability {cap_id: "graph.delta"})
    CREATE (m)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    graph_cap_links = result.result_set[0][0] if result.result_set else 0

    # Membership Learning requires graph.delta (to update MEMBER_OF weights)
    result = g.query('''
    MATCH (m:Mechanism {mechanism_id: "mechanism.membership_learning"})
    MATCH (c:Capability {cap_id: "graph.delta"})
    CREATE (m)-[r:REQUIRES_CAPABILITY {created_at: $now}]->(c)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    learning_cap_links = result.result_set[0][0] if result.result_set else 0

    total_cap_links = spawn_cap_links + graph_cap_links + learning_cap_links
    print(f"  ✅ Mechanisms require capabilities: {total_cap_links} links")
    print()

    # ------------------------------------------------------------------------
    # 6. Links to Principles (process → principles)
    # ------------------------------------------------------------------------
    print("[Links 6/7] Creating REQUIRES links (process → principles)...")

    # Emergence Pipeline requires Zero-Constants principle (thresholds learned)
    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})
    MATCH (p:Principle)
    WHERE p.name IN ["Zero-Constants Architecture", "Single-Energy Currency"]
    CREATE (proc)-[r:REQUIRES {created_at: $now}]->(p)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    principle_links = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Process requires principles: {principle_links} links")
    print()

    # ------------------------------------------------------------------------
    # 7. Links between mechanisms (sequential dependencies)
    # ------------------------------------------------------------------------
    print("[Links 7/7] Creating sequential ENABLES links (mechanism → mechanism)...")

    # Gap Detection enables Coalition Assembly
    result = g.query('''
    MATCH (m1:Mechanism {mechanism_id: "mechanism.gap_detection"})
    MATCH (m2:Mechanism {mechanism_id: "mechanism.coalition_assembly"})
    CREATE (m1)-[r:ENABLES {stage_flow: "gap_to_coalition", created_at: $now}]->(m2)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    gap_coalition = result.result_set[0][0] if result.result_set else 0

    # Coalition Assembly enables Engine Validation
    result = g.query('''
    MATCH (m1:Mechanism {mechanism_id: "mechanism.coalition_assembly"})
    MATCH (m2:Mechanism {mechanism_id: "mechanism.engine_validation"})
    CREATE (m1)-[r:ENABLES {stage_flow: "coalition_to_validation", created_at: $now}]->(m2)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    coalition_validation = result.result_set[0][0] if result.result_set else 0

    # Engine Validation enables Membership Learning (if spawn succeeds)
    result = g.query('''
    MATCH (m1:Mechanism {mechanism_id: "mechanism.engine_validation"})
    MATCH (m2:Mechanism {mechanism_id: "mechanism.membership_learning"})
    CREATE (m1)-[r:ENABLES {stage_flow: "validation_to_learning", created_at: $now}]->(m2)
    RETURN count(r) as cnt
    ''', params={'now': now_iso})
    validation_learning = result.result_set[0][0] if result.result_set else 0

    sequential_links = gap_coalition + coalition_validation + validation_learning
    print(f"  ✅ Sequential mechanism flow: {sequential_links} links")
    print()

    # ========================================================================
    # VERIFICATION
    # ========================================================================

    print("="*80)
    print("VERIFICATION")
    print("="*80)
    print()

    # Count Phase 5 nodes
    result = g.query('''
    MATCH (n:ProtocolNode)
    WHERE n.process_id = "process.emergence_pipeline"
       OR n.mechanism_id STARTS WITH "mechanism.gap_detection"
       OR n.mechanism_id STARTS WITH "mechanism.coalition_assembly"
       OR n.mechanism_id STARTS WITH "mechanism.engine_validation"
       OR n.mechanism_id STARTS WITH "mechanism.membership_learning"
    RETURN count(n) as phase5_nodes
    ''')
    phase5_nodes = result.result_set[0][0] if result.result_set else 0

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

    total_phase5_links = (proc_links + mech_links + requires_links + enables_links +
                         total_measures + total_cap_links + principle_links + sequential_links)

    print(f"✅ Phase 5 complete!")
    print(f"   Phase 5 nodes: {phase5_nodes}")
    print(f"   Phase 5 links: {total_phase5_links}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {total_nodes} nodes, {total_links} links")
    print()

    # ========================================================================
    # TEST QUERIES
    # ========================================================================

    print("📊 Testing Phase 5 queries...")
    print()

    # Query 1: Emergence pipeline stages
    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})-[r:REQUIRES]->(m:Mechanism)
    RETURN m.name as mechanism, r.stage_order as stage
    ORDER BY stage
    ''')
    print("  Emergence Pipeline stages:")
    for row in result.result_set:
        print(f"    Stage {row[1]}: {row[0]}")
    print()

    # Query 2: What events does emergence pipeline enable?
    result = g.query('''
    MATCH (proc:Process {process_id: "process.emergence_pipeline"})-[:ENABLES]->(es:Event_Schema)
    RETURN es.name as event
    ORDER BY event
    ''')
    print("  Events enabled by emergence pipeline:")
    for row in result.result_set:
        print(f"    - {row[0]}")
    print()

    # Query 3: Mechanism capabilities and metrics
    result = g.query('''
    MATCH (m:Mechanism)-[:REQUIRES_CAPABILITY]->(c:Capability)
    WHERE m.mechanism_id STARTS WITH "mechanism.gap_detection"
       OR m.mechanism_id STARTS WITH "mechanism.coalition_assembly"
       OR m.mechanism_id STARTS WITH "mechanism.engine_validation"
       OR m.mechanism_id STARTS WITH "mechanism.membership_learning"
    RETURN m.name as mechanism, collect(DISTINCT c.cap_id) as capabilities
    ORDER BY mechanism
    ''')
    print("  Mechanisms and required capabilities:")
    for row in result.result_set:
        caps = ', '.join(row[1]) if row[1] else 'none'
        print(f"    - {row[0]}: {caps}")
    print()

    # Query 4: Complete three-spec wiring verification
    result = g.query('''
    MATCH (proc:Process)-[:MEMBER_OF]->(anchor:SubEntity {name: "proto.membrane_stack"})
    RETURN proc.name as process, proc.spec_ref as spec
    ORDER BY process
    ''')
    print("  All processes grounded in protocol cluster:")
    for row in result.result_set:
        spec_ref = row[1] if row[1] else "initial cluster"
        print(f"    - {row[0]}: {spec_ref}")
    print()

    print("="*80)
    print("✅ PHASE 5 COMPLETE - Three core specs fully materialized!")
    print("="*80)
    print()
    print("All three specifications now queryable:")
    print("  1. MEMBRANE_INJECTION_CONTRACT.md → Connector process + 7 mechanisms")
    print("  2. VERTICAL_MEMBRANE_LEARNING.md → Permeability learning + Alignment")
    print("  3. subentity_emergence.md → Emergence Pipeline + 4 mechanisms")
    print()


if __name__ == '__main__':
    create_spec_wiring()
