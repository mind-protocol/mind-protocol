#!/usr/bin/env python3
"""
Ingest proto.membrane_stack protocol cluster into L4 protocol graph.

This creates the first queryable protocol specification cluster with:
- 1 SubEntity (anchor)
- 4 Principles (Core Invariants)
- 1 Process (Seven-Step Connector Integration)
- 9 Mechanisms (7 steps + 2 learning)
- 5 Interfaces + 5 Events
- 7 Metrics
- 3 Tasks

Total: 35 nodes, ~60 links
"""

from falkordb import FalkorDB
from datetime import datetime
import sys

def create_protocol_cluster():
    """Ingest proto.membrane_stack cluster into protocol graph."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("=" * 80)
    print("INGESTING PROTOCOL CLUSTER: proto.membrane_stack")
    print("=" * 80)

    # Check if already exists
    result = g.query('MATCH (s:SubEntity {name: $name}) RETURN s', params={'name': 'proto.membrane_stack'})
    if result.result_set:
        print("❌ ERROR: proto.membrane_stack already exists!")
        return False

    # ========================================================================
    # PART 1: Create SubEntity Anchor
    # ========================================================================
    print("\n[1/7] Creating SubEntity anchor...")

    g.query('''
    CREATE (s:SubEntity:ProtocolNode {
        name: $name,
        node_type: 'SubEntity',
        description: $description,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        substrate: 'organizational',
        created_by: 'luca_vellumhand',
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        pattern_type: 'protocol_specification',
        intent_vector: 'enforce_architectural_contracts',
        purpose: $purpose,
        layer: 'L4'
    })
    ''', params={
        'name': 'proto.membrane_stack',
        'description': 'Normative rules for stimulus flow, cross-level membranes, κ learning, and SubEntity emergence. The protocol cluster that governs how consciousness flows between levels and how patterns emerge.',
        'created_at': now_iso,
        'purpose': 'Make Mind Protocol contracts queryable, measurable, and enforceable from within the substrate'
    })
    print("  ✅ SubEntity anchor created")

    # ========================================================================
    # PART 2: Create 4 Principles (Core Invariants)
    # ========================================================================
    print("\n[2/7] Creating 4 Principles (Core Invariants)...")

    principles = [
        {
            'name': 'Membrane-First',
            'statement': 'All cross-boundary flow via membrane.inject → engine validation → broadcast. No direct graph writes from external sources.',
            'why': 'Ensures single point of validation, enables replay, prevents corruption, maintains audit trail',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §Core Invariants'
        },
        {
            'name': 'Single-Energy',
            'statement': 'No separate energy buffers. SubEntity activation = read-out from member node energies via MEMBER_OF traversal.',
            'why': 'Prevents energy accounting drift, ensures consciousness grounded in graph state, enables deterministic replay',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §Core Invariants'
        },
        {
            'name': 'Zero-Constants',
            'statement': 'All thresholds learned per-citizen/org via percentile gates. No hard-coded constants in connectors or engines.',
            'why': 'Enables per-citizen adaptation, prevents one-size-fits-all failures, makes system self-tuning',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §Core Invariants + CONNECTOR_BLUEPRINT.md Rule 3'
        },
        {
            'name': 'Broadcast-Only',
            'statement': 'No REST writes to graph. Engines emit graph.delta.* events on state changes. All graph mutations via event bus.',
            'why': 'Ensures observable changes, enables event replay, maintains single writer (engine), prevents race conditions',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §Core Invariants'
        }
    ]

    for p in principles:
        g.query('''
        CREATE (pr:Principle:ProtocolNode {
            name: $name,
            node_type: 'Principle',
            principle_statement: $statement,
            why_it_matters: $why,
            confidence: 0.98,
            formation_trigger: 'systematic_analysis',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            grounded_in: $grounded_in,
            layer: 'L4',
            description: $statement
        })
        ''', params={
            'name': f'principle.{p["name"].lower().replace("-", "_")}',
            'statement': p['statement'],
            'why': p['why'],
            'created_at': now_iso,
            'grounded_in': p['grounded_in']
        })
        print(f"  ✅ Principle: {p['name']}")

    # ========================================================================
    # PART 3: Create Process (Seven-Step Connector Integration)
    # ========================================================================
    print("\n[3/7] Creating Process (Seven-Step Connector Integration)...")

    g.query('''
    CREATE (proc:Process:ProtocolNode {
        name: 'process.connector_seven_step',
        node_type: 'Process',
        description: 'Canonical process for adding ANY external integration to Mind Protocol. Always the same 7 steps, regardless of source.',
        steps: ['Intent & Channel Declaration', 'Envelope Contract Conformance', 'Safety Filters (Client-side)', 'Rate-limit & Backpressure', 'Membrane Admission (Server-side)', 'Record-Gated Alignment & κ Initialization', 'Outcome-Driven Learning & Observability'],
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        substrate: 'organizational',
        created_by: 'luca_vellumhand',
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        grounded_in: 'CONNECTOR_BLUEPRINT.md §Seven-Step Process',
        layer: 'L4'
    })
    ''', params={'created_at': now_iso})
    print("  ✅ Process created")

    # ========================================================================
    # PART 4: Create 9 Mechanisms (7 steps + 2 learning)
    # ========================================================================
    print("\n[4/7] Creating 9 Mechanisms (7 steps + 2 learning)...")

    mechanisms = [
        # 7 Process Steps
        {
            'name': 'mechanism.intent_declaration',
            'how': 'Choose channel taxonomy (signals.script.X, signals.ui.X, signals.tool.X), declare purpose and harm model',
            'inputs': 'Connector proposal (what integrates, why, risks)',
            'outputs': 'Interface spec with channel, purpose, harm_model',
            'grounded_in': 'CONNECTOR_BLUEPRINT.md Step 1: Capability Card'
        },
        {
            'name': 'mechanism.envelope_conformance',
            'how': 'Validate structure conforms to membrane.inject (scope, channel, content, features_raw, provenance). Include proof fields if available.',
            'inputs': 'Raw connector payload',
            'outputs': 'Normalized membrane.inject envelope',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §Normative Event Envelope'
        },
        {
            'name': 'mechanism.safety_filters',
            'how': 'Redaction (PII, secrets, tokens), truncation (size limits ≤64KB), fingerprinting (stable hash), deduplication',
            'inputs': 'Raw event data',
            'outputs': 'Sanitized event with fingerprint',
            'grounded_in': 'CONNECTOR_BLUEPRINT.md Rule 1 + MEMBRANE_INJECTION_CONTRACT.md §Evidence Size Limits'
        },
        {
            'name': 'mechanism.rate_limit_backpressure',
            'how': 'Client-side rate caps, collector-side per-fingerprint caps (≥10s between identical), spill-to-disk, jitter',
            'inputs': 'Event stream with fingerprints',
            'outputs': 'Rate-limited stream with backpressure signals',
            'grounded_in': 'CONNECTOR_BLUEPRINT.md §Backpressure'
        },
        {
            'name': 'mechanism.membrane_admission',
            'how': 'Collector validates contract, applies gating, emits membrane.inject. NO direct graph writes.',
            'inputs': 'Validated envelope',
            'outputs': 'membrane.inject event on bus',
            'grounded_in': 'MEMBRANE_INJECTION_CONTRACT.md §1 + CONNECTOR_BLUEPRINT.md Rule 1'
        },
        {
            'name': 'mechanism.record_gated_alignment',
            'how': 'Post-ΔE: seed alignment proposals from 5 signals. Materialize only on record frames (Pareto + MAD). Initialize κ to neutral (median).',
            'inputs': 'Staged ΔE, L1 & L2 node activations',
            'outputs': 'Alignment edges + MEMBRANE_TO with neutral κ',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Alignment Edge Materialization'
        },
        {
            'name': 'mechanism.outcome_driven_learning',
            'how': 'Update κ ONLY on outcome events. Broadcast permeability.updated. Monitor redirect/complementary/reject rates.',
            'inputs': 'Outcome events with utility signals',
            'outputs': 'Updated κ values, permeability events, metrics',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Permeability Learning + MEMBRANE_INJECTION_CONTRACT.md §κ Updates'
        },
        # 2 Learning Mechanisms
        {
            'name': 'mechanism.permeability_learning',
            'how': 'Update κ via zero-constants rule: κ_new = κ_old + η * sign(outcome) * g(utility, latency) - λ * overdrive. Learn κ_up/κ_down independently.',
            'inputs': 'Outcome events, current κ values, EMA baselines',
            'outputs': 'Updated κ_up/κ_down values',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Permeability Learning (Outcomes-Only)'
        },
        {
            'name': 'mechanism.alignment_materialization',
            'how': 'Seed proposals from 5 signals during post-ΔE. Accumulate evidence. Materialize edges ONLY at record frames.',
            'inputs': 'Post-ΔE activations, alignment proposals, record frame signals',
            'outputs': 'Alignment edges (LIFTS_TO, CORRESPONDS_TO, SUPPORTS, IMPLEMENTS), MEMBRANE_TO with initial κ',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Alignment Edge Materialization'
        }
    ]

    for m in mechanisms:
        g.query('''
        CREATE (mech:Mechanism:ProtocolNode {
            name: $name,
            node_type: 'Mechanism',
            how_it_works: $how,
            inputs: $inputs,
            outputs: $outputs,
            confidence: 0.93,
            formation_trigger: 'systematic_analysis',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            grounded_in: $grounded_in,
            layer: 'L4',
            description: $how
        })
        ''', params={
            'name': m['name'],
            'how': m['how'],
            'inputs': m['inputs'],
            'outputs': m['outputs'],
            'created_at': now_iso,
            'grounded_in': m['grounded_in']
        })
        print(f"  ✅ Mechanism: {m['name']}")

    # ========================================================================
    # PART 5: Create 5 Interfaces + 5 Events
    # ========================================================================
    print("\n[5/7] Creating 5 Interfaces + 5 Events...")

    interfaces = [
        {
            'name': 'interface.membrane_inject',
            'description': 'Standard envelope for all external stimuli entering consciousness substrate',
            'schema_ref': 'MEMBRANE_INJECTION_CONTRACT.md §Normative Event Envelope',
            'required_fields': ['type', 'id', 'ts', 'spec', 'provenance', 'channel', 'content', 'features_raw']
        },
        {
            'name': 'interface.membrane_transfer_up',
            'description': 'L1→L2 upward stimulus when L1 episode crosses record threshold',
            'schema_ref': 'MEMBRANE_INJECTION_CONTRACT.md §2 L1→L2 Awareness',
            'required_fields': ['type', 'id', 'provenance', 'content']
        },
        {
            'name': 'interface.membrane_transfer_down',
            'description': 'L2→L1 downward stimulus when L2 mission activates citizen context',
            'schema_ref': 'MEMBRANE_INJECTION_CONTRACT.md §5 Citizen Activation',
            'required_fields': ['type', 'id', 'provenance', 'content', 'kappa_down']
        },
        {
            'name': 'interface.membrane_permeability_updated',
            'description': 'Broadcast when κ_up or κ_down changes due to outcome learning',
            'schema_ref': 'VERTICAL_MEMBRANE_LEARNING.md §Permeability Learning',
            'required_fields': ['membrane_id', 'k_up_old', 'k_up_new', 'k_down_old', 'k_down_new', 'outcome_event']
        },
        {
            'name': 'interface.mission_completed',
            'description': 'Engine decision that mission objectives satisfied, triggers κ learning',
            'schema_ref': 'MEMBRANE_INJECTION_CONTRACT.md §3 Task Completion',
            'required_fields': ['mission_id', 'outcome', 'usefulness', 'validated_by']
        }
    ]

    for iface in interfaces:
        # Create Interface
        g.query('''
        CREATE (i:Interface:ProtocolNode {
            name: $name,
            node_type: 'Interface',
            description: $description,
            schema_ref: $schema_ref,
            required_fields: $required_fields,
            confidence: 0.95,
            formation_trigger: 'systematic_analysis',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: 'L4'
        })
        ''', params={
            'name': iface['name'],
            'description': iface['description'],
            'schema_ref': iface['schema_ref'],
            'required_fields': iface['required_fields'],
            'created_at': now_iso
        })

        # Create corresponding Event
        event_name = iface['name'].replace('interface.', 'event.') + '.observed'
        g.query('''
        CREATE (e:Event:ProtocolNode {
            name: $name,
            node_type: 'Event',
            description: $description,
            channel: $channel,
            confidence: 0.90,
            formation_trigger: 'systematic_analysis',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: 'L4'
        })
        ''', params={
            'name': event_name,
            'description': f'Observability event when {iface["name"].split(".")[1].replace("_", " ")} processed',
            'channel': f'telemetry.{iface["name"].split(".")[1]}',
            'created_at': now_iso
        })

        print(f"  ✅ Interface + Event: {iface['name']}")

    # ========================================================================
    # PART 6: Create 7 Metrics
    # ========================================================================
    print("\n[6/7] Creating 7 Metrics...")

    metrics = [
        {
            'name': 'metric.record_gate_hit_rate',
            'description': 'Fraction of frames where Pareto + MAD both fire (record frames)',
            'measurement_method': 'count(record_frames) / count(all_frames)',
            'target_value': '5-15% (prevents thrash, ensures significance)',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Alignment Edge Materialization'
        },
        {
            'name': 'metric.redirect_rate',
            'description': 'Fraction of spawn candidates redirected to existing SubEntity (high S_red)',
            'measurement_method': 'count(subentity.candidate.redirected) / count(spawn_attempts)',
            'target_value': '30-50% (prevents redundant SubEntities)',
            'grounded_in': 'subentity_emergence.md §Validation & Gates'
        },
        {
            'name': 'metric.complementary_rate',
            'description': 'Fraction of spawn candidates accepted despite high S_red because S_use is high',
            'measurement_method': 'count(accepted AND S_red >= Q90 AND S_use >= Q80) / count(spawn_attempts)',
            'target_value': '5-10% (rare but valuable differentiation)',
            'grounded_in': 'subentity_emergence.md §Validation & Gates'
        },
        {
            'name': 'metric.kappa_up_drift',
            'description': 'EMA of κ_up changes over time. Detects overdrive or restrictiveness.',
            'measurement_method': 'ema(κ_up_t - κ_up_t-1)',
            'target_value': 'Near zero (stable permeability)',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Permeability Learning'
        },
        {
            'name': 'metric.kappa_down_drift',
            'description': 'EMA of κ_down changes over time. Detects spam or neglect.',
            'measurement_method': 'ema(κ_down_t - κ_down_t-1)',
            'target_value': 'Near zero (stable permeability)',
            'grounded_in': 'VERTICAL_MEMBRANE_LEARNING.md §Permeability Learning'
        },
        {
            'name': 'metric.emergence_rate',
            'description': 'Rate of new SubEntity spawns per citizen per week',
            'measurement_method': 'count(subentity.spawned) / weeks / citizens',
            'target_value': '1-3 per citizen per week (responsive but not chaotic)',
            'grounded_in': 'subentity_emergence.md §Emergence Trigger'
        },
        {
            'name': 'metric.rejection_breakdown',
            'description': 'Breakdown of rejection reasons (persistence/cohesion/boundary gate fails)',
            'measurement_method': 'histogram(rejection_reason)',
            'target_value': 'No single gate failing >60% (balanced validation)',
            'grounded_in': 'subentity_emergence.md §Validation & Gates'
        }
    ]

    for m in metrics:
        g.query('''
        CREATE (met:Metric:ProtocolNode {
            name: $name,
            node_type: 'Metric',
            description: $description,
            measurement_method: $measurement_method,
            target_value: $target_value,
            confidence: 0.88,
            formation_trigger: 'systematic_analysis',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            grounded_in: $grounded_in,
            layer: 'L4'
        })
        ''', params={
            'name': m['name'],
            'description': m['description'],
            'measurement_method': m['measurement_method'],
            'target_value': m['target_value'],
            'created_at': now_iso,
            'grounded_in': m['grounded_in']
        })
        print(f"  ✅ Metric: {m['name']}")

    # ========================================================================
    # PART 7: Create 3 Tasks
    # ========================================================================
    print("\n[7/7] Creating 3 Tasks (Conformance Examples)...")

    tasks = [
        {
            'name': 'task.wire_fe_errors',
            'description': 'Implement FE error connector conforming to 7-step process',
            'estimated_hours': 8.0,
            'priority': 'high',
            'grounded_in': 'fe_errors_capability_card.md'
        },
        {
            'name': 'task.wire_logs',
            'description': 'Implement structured logs connector (script logs, service logs)',
            'estimated_hours': 12.0,
            'priority': 'medium',
            'grounded_in': 'CONNECTOR_BLUEPRINT.md desired connectors'
        },
        {
            'name': 'task.wire_telegram',
            'description': 'Implement Telegram listener for external messages',
            'estimated_hours': 16.0,
            'priority': 'medium',
            'grounded_in': 'CONNECTOR_BLUEPRINT.md desired connectors'
        }
    ]

    for t in tasks:
        g.query('''
        CREATE (task:Task:ProtocolNode {
            name: $name,
            node_type: 'Task',
            description: $description,
            estimated_hours: $estimated_hours,
            priority: $priority,
            status: 'planning',
            confidence: 0.80,
            formation_trigger: 'direct_experience',
            substrate: 'organizational',
            created_by: 'luca_vellumhand',
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            grounded_in: $grounded_in,
            layer: 'L4'
        })
        ''', params={
            'name': t['name'],
            'description': t['description'],
            'estimated_hours': t['estimated_hours'],
            'priority': t['priority'],
            'created_at': now_iso,
            'grounded_in': t['grounded_in']
        })
        print(f"  ✅ Task: {t['name']}")

    # ========================================================================
    # CREATE LINKS
    # ========================================================================
    print("\n" + "=" * 80)
    print("CREATING LINKS")
    print("=" * 80)

    # All nodes MEMBER_OF anchor
    print("\n[Links 1/5] Creating MEMBER_OF links (all nodes → anchor)...")
    node_patterns = [
        'Principle', 'Process', 'Mechanism', 'Interface',
        'Event', 'Metric', 'Task'
    ]
    for pattern in node_patterns:
        result = g.query(f'''
        MATCH (n:{pattern}:ProtocolNode), (anchor:SubEntity {{name: 'proto.membrane_stack'}})
        WHERE NOT (n)-[:MEMBER_OF]->(anchor)
        CREATE (n)-[r:MEMBER_OF {{
            goal: 'Node belongs to protocol cluster',
            mindstate: 'Systematic protocol encoding',
            energy: 0.90,
            confidence: 0.95,
            w_semantic: 0.90,
            w_intent: 0.92,
            w_affect: 0.70,
            w_experience: 0.85,
            w_total: 0.847,
            formation_context: 'Protocol cluster assembly',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at,
            last_coactivation: $created_at
        }}]->(anchor)
        RETURN count(r) as count
        ''', params={'created_at': now_iso})
        count = result.result_set[0][0] if result.result_set else 0
        print(f"  ✅ {pattern}: {count} MEMBER_OF links created")

    # Process REQUIRES Principles
    print("\n[Links 2/5] Creating REQUIRES links (process → principles)...")
    principle_names = [
        'principle.membrane_first',
        'principle.single_energy',
        'principle.zero_constants',
        'principle.broadcast_only'
    ]
    for pname in principle_names:
        g.query('''
        MATCH (proc:Process {name: 'process.connector_seven_step'}), (p:Principle {name: $pname})
        CREATE (proc)-[r:REQUIRES {
            goal: 'Process must enforce this invariant',
            mindstate: 'Architectural constraint enforcement',
            energy: 0.88,
            confidence: 0.98,
            validation_status: 'proven',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at
        }]->(p)
        ''', params={'pname': pname, 'created_at': now_iso})
    print(f"  ✅ Process REQUIRES 4 Principles")

    # Process REQUIRES Mechanisms
    print("\n[Links 3/5] Creating REQUIRES links (process → mechanisms)...")
    mechanism_names = [
        'mechanism.intent_declaration',
        'mechanism.envelope_conformance',
        'mechanism.safety_filters',
        'mechanism.rate_limit_backpressure',
        'mechanism.membrane_admission',
        'mechanism.record_gated_alignment',
        'mechanism.outcome_driven_learning'
    ]
    for mname in mechanism_names:
        g.query('''
        MATCH (proc:Process {name: 'process.connector_seven_step'}), (m:Mechanism {name: $mname})
        CREATE (proc)-[r:REQUIRES {
            goal: 'Process requires this step',
            mindstate: 'Process dependency',
            energy: 0.85,
            confidence: 0.95,
            validation_status: 'proven',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at
        }]->(m)
        ''', params={'mname': mname, 'created_at': now_iso})
    print(f"  ✅ Process REQUIRES 7 step Mechanisms")

    # Process ENABLES Events
    print("\n[Links 4/5] Creating ENABLES links (process → events)...")
    event_names = [
        'event.membrane_inject.observed',
        'event.membrane_transfer_up.observed',
        'event.membrane_transfer_down.observed',
        'event.membrane_permeability_updated.observed',
        'event.mission_completed.observed'
    ]
    for ename in event_names:
        g.query('''
        MATCH (proc:Process {name: 'process.connector_seven_step'}), (e:Event {name: $ename})
        CREATE (proc)-[r:ENABLES {
            goal: 'Process emits observability events',
            mindstate: 'Observability enablement',
            energy: 0.82,
            confidence: 0.92,
            validation_status: 'tested',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at
        }]->(e)
        ''', params={'ename': ename, 'created_at': now_iso})
    print(f"  ✅ Process ENABLES 5 Events")

    # Mechanisms MEASURES Metrics
    print("\n[Links 5/5] Creating MEASURES links (mechanisms → metrics)...")
    measures_pairs = [
        ('mechanism.permeability_learning', 'metric.kappa_up_drift'),
        ('mechanism.permeability_learning', 'metric.kappa_down_drift'),
        ('mechanism.record_gated_alignment', 'metric.record_gate_hit_rate'),
        ('mechanism.outcome_driven_learning', 'metric.redirect_rate'),
        ('mechanism.outcome_driven_learning', 'metric.complementary_rate'),
        ('mechanism.outcome_driven_learning', 'metric.emergence_rate'),
        ('mechanism.outcome_driven_learning', 'metric.rejection_breakdown')
    ]
    for mech_name, metric_name in measures_pairs:
        g.query('''
        MATCH (mech:Mechanism {name: $mech}), (met:Metric {name: $metric})
        CREATE (mech)-[r:MEASURES {
            goal: 'Mechanism produces this metric',
            mindstate: 'Measurement relationship',
            energy: 0.80,
            confidence: 0.90,
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at
        }]->(met)
        ''', params={'mech': mech_name, 'metric': metric_name, 'created_at': now_iso})
    print(f"  ✅ {len(measures_pairs)} MEASURES links created")

    # Tasks IMPLEMENTS Process
    print("\n[Links 6/6] Creating IMPLEMENTS links (tasks → process)...")
    task_names = ['task.wire_fe_errors', 'task.wire_logs', 'task.wire_telegram']
    for tname in task_names:
        g.query('''
        MATCH (task:Task {name: $tname}), (proc:Process {name: 'process.connector_seven_step'})
        CREATE (task)-[r:IMPLEMENTS {
            goal: 'Task implements canonical process',
            mindstate: 'Implementation conformance',
            energy: 0.85,
            confidence: 0.85,
            test_status: 'planning',
            formation_trigger: 'direct_experience',
            created_at: $created_at,
            valid_at: $created_at
        }]->(proc)
        ''', params={'tname': tname, 'created_at': now_iso})
    print(f"  ✅ 3 Tasks IMPLEMENT Process")

    # ========================================================================
    # VERIFICATION
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Count cluster nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: 'proto.membrane_stack'})
    RETURN count(n) as cluster_nodes
    ''')
    cluster_nodes = result.result_set[0][0]

    # Count cluster links
    result = g.query('''
    MATCH (anchor:SubEntity {name: 'proto.membrane_stack'})<-[:MEMBER_OF]-(n)
    MATCH (n)-[r]-()
    WHERE type(r) IN ['MEMBER_OF', 'REQUIRES', 'ENABLES', 'MEASURES', 'IMPLEMENTS']
    RETURN count(DISTINCT r) as cluster_links
    ''')
    cluster_links = result.result_set[0][0]

    print(f"\n✅ Protocol cluster created successfully!")
    print(f"   Nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Links: {cluster_links}")

    # Test queryability
    print(f"\n📊 Testing queryability...")

    # Query invariants
    result = g.query('''
    MATCH (p:Principle)-[:MEMBER_OF]->(proto:SubEntity {name: 'proto.membrane_stack'})
    RETURN p.name as name, p.principle_statement as statement
    ''')
    print(f"\n  Invariants query returned {len(result.result_set)} principles:")
    for row in result.result_set:
        print(f"    - {row[0]}")

    # Query process requirements
    result = g.query('''
    MATCH (proc:Process {name: 'process.connector_seven_step'})-[:REQUIRES]->(x)
    RETURN labels(x)[0] as type, count(*) as count
    ''')
    print(f"\n  Process requirements:")
    for row in result.result_set:
        print(f"    - {row[0]}: {row[1]}")

    print("\n" + "=" * 80)
    print("✅ INGESTION COMPLETE - Protocol cluster is now queryable!")
    print("=" * 80)

    return True


if __name__ == '__main__':
    try:
        success = create_protocol_cluster()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
