#!/usr/bin/env python3
"""
Phase 2: Versioning & Releases

Adds:
- 2 Protocol_Version (v1.0.0, v1.1.0)
- 2 Schema_Bundle (content-addressed archives)
- 3 SDK_Release (TypeScript, Python, Go)
- 1 Sidecar_Release
- 1 Compatibility_Matrix

Total: +9 nodes, +121 links
"""

from falkordb import FalkorDB
from datetime import datetime
import sys
import json

def ingest_versioning():
    """Ingest Phase 2: Versioning into protocol graph."""

    db = FalkorDB(host='localhost', port=6379)
    g = db.select_graph('protocol')

    now_iso = datetime.utcnow().isoformat() + 'Z'

    print("=" * 80)
    print("PHASE 2: VERSIONING & RELEASES")
    print("=" * 80)

    # ========================================================================
    # PART 1: Protocol Versions (2 versions)
    # ========================================================================
    print("\n[1/5] Creating 2 Protocol_Versions...")

    versions = [
        {
            'semver': '1.0.0',
            'released_at': '2025-08-01T18:00:00Z',
            'summary': 'Initial public protocol release.'
        },
        {
            'semver': '1.1.0',
            'released_at': '2025-10-27T12:00:00Z',
            'summary': 'Membrane-first protocol hardening, schema v1.1 rollout, vector-weighted MEMBER_OF.'
        }
    ]

    for v in versions:
        g.query('''
        CREATE (pv:Protocol_Version:ProtocolNode {
            semver: $semver,
            node_type: "Protocol_Version",
            description: $summary,
            released_at: $released_at,
            summary: $summary,
            confidence: 0.98,
            formation_trigger: "systematic_analysis",
            substrate: "organizational",
            created_by: "luca_vellumhand",
            created_at: $created_at,
            valid_at: $released_at,
            invalid_at: null,
            expired_at: null,
            layer: "L4",
            name: $name
        })
        ''', params={
            'semver': v['semver'],
            'released_at': v['released_at'],
            'summary': v['summary'],
            'created_at': now_iso,
            'name': f'protocol.v{v["semver"]}'
        })
        print(f"  ✅ Protocol_Version: {v['semver']}")

    # ========================================================================
    # PART 2: Schema Bundles (2 bundles)
    # ========================================================================
    print("\n[2/5] Creating 2 Schema_Bundles...")

    bundles = [
        {
            'version': '1.0.0',
            'bundle_hash': 'sha256:abc123def456...',
            'bundle_uri': 'mind://bundles/schema-v1.0.0.tar.gz',
            'contains': [
                'membrane.inject@1.0',
                'graph.delta.node.upsert@1.0',
                'graph.delta.link.upsert@1.0',
                'wm.emit@1.0',
                'mission.completed@1.0'
            ]
        },
        {
            'version': '1.1.0',
            'bundle_hash': 'sha256:def456abc789...',
            'bundle_uri': 'mind://bundles/schema-v1.1.0.tar.gz',
            'contains': [
                'membrane.inject@1.1',
                'membrane.transfer.up@1.1',
                'membrane.transfer.down@1.1',
                'membrane.permeability.updated@1.1',
                'graph.delta.node.upsert@1.1',
                'graph.delta.link.upsert@1.1',
                'wm.emit@1.1',
                'percept.frame@1.1',
                'mission.completed@1.1',
                'gap.detected@1.1',
                'emergence.candidate@1.1',
                'emergence.spawn@1.1',
                'candidate.redirected@1.1',
                'membership.updated@1.1'
            ]
        }
    ]

    for bundle in bundles:
        contains_json = json.dumps(bundle['contains'])
        g.query('''
        CREATE (sb:Schema_Bundle:ProtocolNode {
            bundle_uri: $bundle_uri,
            node_type: "Schema_Bundle",
            description: $description,
            bundle_hash: $bundle_hash,
            contains: $contains,
            version: $version,
            confidence: 0.95,
            formation_trigger: "systematic_analysis",
            substrate: "organizational",
            created_by: "luca_vellumhand",
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: "L4",
            name: $name
        })
        ''', params={
            'bundle_uri': bundle['bundle_uri'],
            'bundle_hash': bundle['bundle_hash'],
            'contains': contains_json,
            'version': bundle['version'],
            'description': f'Schema bundle for protocol v{bundle["version"]}',
            'created_at': now_iso,
            'name': f'bundle.v{bundle["version"]}'
        })
        print(f"  ✅ Schema_Bundle: v{bundle['version']}")

    # ========================================================================
    # PART 3: SDK Releases (3 SDKs)
    # ========================================================================
    print("\n[3/5] Creating 3 SDK_Releases...")

    sdks = [
        {
            'language': 'typescript',
            'version': '1.0.0',
            'package_name': '@mind-protocol/sdk',
            'commit_hash': 'abc123def456',
            'schema_min_version': '1.0.0',
            'features': ['membrane.inject', 'graph.delta', 'mission.lifecycle']
        },
        {
            'language': 'python',
            'version': '1.0.0',
            'package_name': 'mind-protocol-sdk',
            'commit_hash': 'def456abc789',
            'schema_min_version': '1.0.0',
            'features': ['membrane.inject', 'graph.delta', 'mission.lifecycle', 'emergence']
        },
        {
            'language': 'go',
            'version': '1.0.0',
            'package_name': 'github.com/mind-protocol/sdk-go',
            'commit_hash': 'ghi789jkl012',
            'schema_min_version': '1.0.0',
            'features': ['membrane.inject', 'graph.delta']
        }
    ]

    for sdk in sdks:
        features_json = json.dumps(sdk['features'])
        g.query('''
        CREATE (sdk:SDK_Release:ProtocolNode {
            language: $language,
            node_type: "SDK_Release",
            description: $description,
            version: $version,
            package_name: $package_name,
            commit_hash: $commit_hash,
            schema_min_version: $schema_min_version,
            features: $features,
            confidence: 0.92,
            formation_trigger: "systematic_analysis",
            substrate: "organizational",
            created_by: "luca_vellumhand",
            created_at: $created_at,
            valid_at: $created_at,
            invalid_at: null,
            expired_at: null,
            layer: "L4",
            name: $name
        })
        ''', params={
            'language': sdk['language'],
            'version': sdk['version'],
            'package_name': sdk['package_name'],
            'commit_hash': sdk['commit_hash'],
            'schema_min_version': sdk['schema_min_version'],
            'features': features_json,
            'description': f'{sdk["language"].capitalize()} SDK v{sdk["version"]}',
            'created_at': now_iso,
            'name': f'sdk.{sdk["language"]}.v{sdk["version"]}'
        })
        print(f"  ✅ SDK_Release: {sdk['language']} v{sdk['version']}")

    # ========================================================================
    # PART 4: Sidecar Release (1 release)
    # ========================================================================
    print("\n[4/5] Creating 1 Sidecar_Release...")

    features_json = json.dumps(['buffer_offline', 'replay', 'signature_validation', 'rate_limiting'])
    g.query('''
    CREATE (sc:Sidecar_Release:ProtocolNode {
        image_ref: "ghcr.io/mind-protocol/sidecar:1.0.0",
        node_type: "Sidecar_Release",
        description: "Sidecar v1.0.0 with offline buffering and replay",
        version: "1.0.0",
        features: $features,
        schema_min_version: "1.0.0",
        confidence: 0.92,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "sidecar.v1.0.0"
    })
    ''', params={'features': features_json, 'created_at': now_iso})
    print("  ✅ Sidecar_Release: v1.0.0")

    # ========================================================================
    # PART 5: Compatibility Matrix (1 matrix)
    # ========================================================================
    print("\n[5/5] Creating 1 Compatibility_Matrix...")

    matrix_json = json.dumps([
        {'sdk': 'typescript@1.0.0', 'sidecar': '1.0.0', 'schema': '1.0.0', 'status': 'ok'},
        {'sdk': 'typescript@1.0.0', 'sidecar': '1.0.0', 'schema': '1.1.0', 'status': 'ok'},
        {'sdk': 'python@1.0.0', 'sidecar': '1.0.0', 'schema': '1.0.0', 'status': 'ok'},
        {'sdk': 'python@1.0.0', 'sidecar': '1.0.0', 'schema': '1.1.0', 'status': 'ok'},
        {'sdk': 'go@1.0.0', 'sidecar': '1.0.0', 'schema': '1.0.0', 'status': 'ok'},
        {'sdk': 'go@1.0.0', 'sidecar': '1.0.0', 'schema': '1.1.0', 'status': 'warn'}
    ])

    g.query('''
    CREATE (cm:Compatibility_Matrix:ProtocolNode {
        matrix: $matrix,
        node_type: "Compatibility_Matrix",
        description: "SDK/Sidecar/Schema compatibility matrix",
        generated_at: $created_at,
        confidence: 0.90,
        formation_trigger: "systematic_analysis",
        substrate: "organizational",
        created_by: "luca_vellumhand",
        created_at: $created_at,
        valid_at: $created_at,
        invalid_at: null,
        expired_at: null,
        layer: "L4",
        name: "compatibility.matrix"
    })
    ''', params={'matrix': matrix_json, 'created_at': now_iso})
    print("  ✅ Compatibility_Matrix")

    # ========================================================================
    # CREATE LINKS
    # ========================================================================
    print("\n" + "=" * 80)
    print("CREATING LINKS")
    print("=" * 80)

    # 1. All new nodes MEMBER_OF proto.membrane_stack
    print("\n[Links 1/7] Creating MEMBER_OF links (all new nodes → anchor)...")
    node_types = ['Protocol_Version', 'Schema_Bundle', 'SDK_Release', 'Sidecar_Release', 'Compatibility_Matrix']
    total_member_of = 0
    for ntype in node_types:
        result = g.query(f'''
        MATCH (n:{ntype}:ProtocolNode), (anchor:SubEntity {{name: 'proto.membrane_stack'}})
        WHERE NOT (n)-[:MEMBER_OF]->(anchor)
        CREATE (n)-[r:MEMBER_OF {{
            goal: 'Versioning component belongs to protocol cluster',
            mindstate: 'Phase 2: Versioning',
            energy: 0.90,
            confidence: 0.95,
            w_semantic: 0.93,
            w_intent: 0.96,
            w_affect: 0.70,
            w_experience: 0.89,
            w_total: 0.868,
            formation_context: 'Phase 2: Versioning',
            formation_trigger: 'systematic_analysis',
            created_at: $created_at,
            valid_at: $created_at,
            last_coactivation: $created_at
        }}]->(anchor)
        RETURN count(r) as count
        ''', params={'created_at': now_iso})
        count = result.result_set[0][0] if result.result_set else 0
        total_member_of += count
        print(f"  ✅ {ntype}: {count} MEMBER_OF links")
    print(f"  Total MEMBER_OF: {total_member_of}")

    # 2. Protocol_Version → Event_Schema (PUBLISHES_SCHEMA)
    print("\n[Links 2/7] Creating PUBLISHES_SCHEMA links (versions → schemas)...")

    # v1.0.0 publishes core schemas
    result = g.query('''
    MATCH (pv:Protocol_Version {semver: "1.0.0"}), (es:Event_Schema)
    WHERE es.name IN ['membrane.inject', 'graph.delta.node.upsert', 'graph.delta.link.upsert', 'wm.emit', 'mission.completed']
    AND NOT (pv)-[:PUBLISHES_SCHEMA]->(es)
    CREATE (pv)-[r:PUBLISHES_SCHEMA {
        goal: 'Protocol version publishes this schema',
        mindstate: 'Schema versioning',
        energy: 0.88,
        confidence: 0.98,
        release_notes_uri: 'mind://releases/v1.0.0.md',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(es)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    v1_count = result.result_set[0][0] if result.result_set else 0

    # v1.1.0 publishes all schemas
    result = g.query('''
    MATCH (pv:Protocol_Version {semver: "1.1.0"}), (es:Event_Schema)
    WHERE NOT (pv)-[:PUBLISHES_SCHEMA]->(es)
    CREATE (pv)-[r:PUBLISHES_SCHEMA {
        goal: 'Protocol version publishes this schema',
        mindstate: 'Schema versioning',
        energy: 0.88,
        confidence: 0.98,
        release_notes_uri: 'mind://releases/v1.1.0.md',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(es)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    v11_count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ v1.0.0 publishes {v1_count} schemas, v1.1.0 publishes {v11_count} schemas")

    # Also publish Envelope_Schema
    result = g.query('''
    MATCH (pv:Protocol_Version), (env:Envelope_Schema)
    WHERE NOT (pv)-[:PUBLISHES_SCHEMA]->(env)
    CREATE (pv)-[r:PUBLISHES_SCHEMA {
        goal: 'Protocol version publishes envelope schema',
        mindstate: 'Schema versioning',
        energy: 0.88,
        confidence: 0.98,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(env)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    env_count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Both versions publish envelope schema: {env_count} links")

    # 3. Schema_Bundle → Event_Schema (BUNDLES)
    print("\n[Links 3/7] Creating BUNDLES links (bundles → schemas)...")
    result = g.query('''
    MATCH (sb:Schema_Bundle), (es:Event_Schema)
    WHERE NOT (sb)-[:BUNDLES]->(es)
    CREATE (sb)-[r:BUNDLES {
        goal: 'Bundle contains this schema',
        mindstate: 'Schema packaging',
        energy: 0.85,
        confidence: 0.95,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(es)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Bundles contain {count} schemas")

    # 4. SDK_Release → Event_Schema (IMPLEMENTS)
    print("\n[Links 4/7] Creating IMPLEMENTS links (SDKs → schemas)...")
    result = g.query('''
    MATCH (sdk:SDK_Release), (es:Event_Schema)
    WHERE NOT (sdk)-[:IMPLEMENTS]->(es)
    CREATE (sdk)-[r:IMPLEMENTS {
        goal: 'SDK implements this event schema',
        mindstate: 'SDK capability',
        energy: 0.85,
        confidence: 0.90,
        coverage: 0.85,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(es)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ SDKs implement {count} schemas")

    # 5. Sidecar_Release → Event_Schema (SUPPORTS)
    print("\n[Links 5/7] Creating SUPPORTS links (sidecar → schemas)...")
    result = g.query('''
    MATCH (sc:Sidecar_Release), (es:Event_Schema)
    WHERE NOT (sc)-[:SUPPORTS]->(es)
    CREATE (sc)-[r:SUPPORTS {
        goal: 'Sidecar supports this event schema',
        mindstate: 'Sidecar capability',
        energy: 0.85,
        confidence: 0.92,
        maturity: 'ga',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(es)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ Sidecar supports {count} schemas")

    # 6. SDK_Release ↔ Sidecar_Release (COMPATIBLE_WITH)
    print("\n[Links 6/7] Creating COMPATIBLE_WITH links (SDKs ↔ sidecar)...")
    result = g.query('''
    MATCH (sdk:SDK_Release), (sc:Sidecar_Release)
    WHERE NOT (sdk)-[:COMPATIBLE_WITH]->(sc)
    CREATE (sdk)-[r:COMPATIBLE_WITH {
        goal: 'SDK compatible with sidecar',
        mindstate: 'Compatibility verification',
        energy: 0.85,
        confidence: 0.95,
        level: 'runtime',
        status: 'ok',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(sc)
    CREATE (sc)-[r2:COMPATIBLE_WITH {
        goal: 'Sidecar compatible with SDK',
        mindstate: 'Compatibility verification',
        energy: 0.85,
        confidence: 0.95,
        level: 'runtime',
        status: 'ok',
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(sdk)
    RETURN count(r) + count(r2) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ {count} bidirectional compatibility links")

    # 7. Protocol_Version v1.1 SUPERSEDES v1.0
    print("\n[Links 7/7] Creating SUPERSEDES link (v1.1 → v1.0)...")
    result = g.query('''
    MATCH (new:Protocol_Version {semver: "1.1.0"}), (old:Protocol_Version {semver: "1.0.0"})
    WHERE NOT (new)-[:SUPERSEDES]->(old)
    CREATE (new)-[r:SUPERSEDES {
        goal: 'New version supersedes old version',
        mindstate: 'Version evolution',
        energy: 0.88,
        confidence: 0.98,
        compat_maintained: true,
        formation_trigger: 'systematic_analysis',
        created_at: $created_at,
        valid_at: $created_at
    }]->(old)
    RETURN count(r) as count
    ''', params={'created_at': now_iso})
    count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✅ v1.1.0 SUPERSEDES v1.0.0: {count} link")

    # ========================================================================
    # VERIFICATION
    # ========================================================================
    print("\n" + "=" * 80)
    print("VERIFICATION")
    print("=" * 80)

    # Count Phase 2 nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: 'proto.membrane_stack'})
    WHERE n.created_at = $created_at
    RETURN count(n) as phase2_nodes
    ''', params={'created_at': now_iso})
    phase2_nodes = result.result_set[0][0] if result.result_set else 0

    # Count total cluster nodes
    result = g.query('''
    MATCH (n)-[:MEMBER_OF]->(anchor:SubEntity {name: 'proto.membrane_stack'})
    RETURN count(n) as cluster_nodes
    ''')
    cluster_nodes = result.result_set[0][0]

    # Count total protocol graph
    node_count = g.query('MATCH (n) RETURN count(n) as c').result_set[0][0]
    link_count = g.query('MATCH ()-[r]->() RETURN count(r) as c').result_set[0][0]

    print(f"\n✅ Phase 2 complete!")
    print(f"   Phase 2 nodes: {phase2_nodes}")
    print(f"   Total cluster nodes: {cluster_nodes + 1} (including anchor)")
    print(f"   Total protocol graph: {node_count} nodes, {link_count} links")

    # Test queryability
    print(f"\n📊 Testing Phase 2 queries...")

    # Query 1: Which protocol version published membrane.inject?
    result = g.query('''
    MATCH (pv:Protocol_Version)-[:PUBLISHES_SCHEMA]->(es:Event_Schema {name: "membrane.inject"})
    RETURN pv.semver, pv.released_at, pv.summary
    ORDER BY pv.semver
    ''')
    print(f"\n  Protocol versions publishing membrane.inject:")
    for row in result.result_set:
        print(f"    - v{row[0]} ({row[1]})")

    # Query 2: What events does TypeScript SDK implement?
    result = g.query('''
    MATCH (sdk:SDK_Release {language: "typescript"})-[:IMPLEMENTS]->(es:Event_Schema)
    RETURN count(es) as event_count
    ''')
    count = result.result_set[0][0] if result.result_set else 0
    print(f"\n  TypeScript SDK implements {count} event schemas")

    # Query 3: Is Python SDK compatible with sidecar?
    result = g.query('''
    MATCH (sdk:SDK_Release {language: "python"})-[c:COMPATIBLE_WITH]->(sc:Sidecar_Release)
    RETURN sc.version, c.status
    ''')
    print(f"\n  Python SDK compatibility:")
    for row in result.result_set:
        print(f"    - Sidecar v{row[0]}: {row[1]}")

    print("\n" + "=" * 80)
    print("✅ PHASE 2 COMPLETE - Protocol versioning is now queryable!")
    print("=" * 80)

    return True


if __name__ == '__main__':
    try:
        success = ingest_versioning()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
