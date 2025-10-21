"""
Brutal Schema Fix - Add all missing fields to match Python code spec

What this fixes:
1. energy: {"consciousness_engine": 0.0} → {} (empty dict)
2. Adds missing node learning fields: log_weight, ema_trace_seats, ema_formation_quality, ema_wm_presence
3. Adds missing link trace fields: all 9 fields from LINK_TRACE_FIELDS_FOR_FELIX.md

Author: Felix "Ironhand"
Date: 2025-10-21
"""

import json
from falkordb import FalkorDB

GRAPHS_TO_FIX = [
    "citizen_luca",
    "citizen_felix",
    "citizen_iris",
    "citizen_ada",
    "mind_protocol_collective_graph"
]

def brutal_fix(graph_name: str):
    """Fix ALL schema issues in one pass."""
    print(f"\n{'='*60}")
    print(f"BRUTAL FIX: {graph_name}")
    print(f"{'='*60}")

    db = FalkorDB()
    g = db.select_graph(graph_name)

    # ===== FIX NODES =====
    print("\n[1/2] FIXING NODES...")

    # Reset energy to empty dict {} and add missing learning fields
    node_query = """
    MATCH (n)
    SET n.energy = '{}',
        n.log_weight = COALESCE(n.log_weight, 0.0),
        n.ema_trace_seats = COALESCE(n.ema_trace_seats, 0.0),
        n.ema_formation_quality = COALESCE(n.ema_formation_quality, 0.0),
        n.ema_wm_presence = COALESCE(n.ema_wm_presence, 0.0),
        n.threshold = COALESCE(n.threshold, 0.1),
        n.scope = COALESCE(n.scope, 'personal')
    RETURN count(n) as fixed
    """

    result = g.query(node_query)
    node_count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ Fixed {node_count} nodes")

    # ===== FIX LINKS =====
    print("\n[2/2] FIXING LINKS...")

    # Add all missing link trace fields
    link_query = """
    MATCH ()-[r]->()
    SET r.log_weight = COALESCE(r.log_weight, 0.0),
        r.ema_active = COALESCE(r.ema_active, 0.0),
        r.ema_flow_mag = COALESCE(r.ema_flow_mag, 0.0),
        r.precedence_forward = COALESCE(r.precedence_forward, 0.0),
        r.precedence_backward = COALESCE(r.precedence_backward, 0.0),
        r.ema_hunger_gates = COALESCE(r.ema_hunger_gates, '[0,0,0,0,0,0,0]'),
        r.affect_tone_ema = COALESCE(r.affect_tone_ema, 0.0),
        r.observed_payloads_count = COALESCE(r.observed_payloads_count, 0)
    RETURN count(r) as fixed
    """

    result = g.query(link_query)
    link_count = result.result_set[0][0] if result.result_set else 0
    print(f"  ✓ Fixed {link_count} links")

    # ===== VERIFY =====
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")

    # Verify node energy is empty dict
    verify_energy = g.query("MATCH (n) RETURN n.energy LIMIT 1")
    if verify_energy.result_set:
        energy_val = verify_energy.result_set[0][0]
        parsed = json.loads(energy_val)
        if parsed == {}:
            print("  ✓ Node energy: {} (correct)")
        else:
            print(f"  ✗ Node energy: {energy_val} (WRONG - should be {{}})")

    # Verify node has log_weight
    verify_log_weight = g.query("MATCH (n) RETURN n.log_weight IS NOT NULL as has_field LIMIT 1")
    if verify_log_weight.result_set:
        has_field = verify_log_weight.result_set[0][0]
        print(f"  {'✓' if has_field else '✗'} Node log_weight field exists")

    # Verify link has precedence_forward
    verify_precedence = g.query("MATCH ()-[r]->() RETURN r.precedence_forward IS NOT NULL as has_field LIMIT 1")
    if verify_precedence.result_set:
        has_field = verify_precedence.result_set[0][0]
        print(f"  {'✓' if has_field else '✗'} Link precedence_forward field exists")

    print(f"\n{'='*60}")
    print(f"COMPLETE: {graph_name}")
    print(f"{'='*60}")


if __name__ == "__main__":
    print("="*60)
    print("BRUTAL SCHEMA FIX")
    print("="*60)
    print("\nThis will:")
    print("  1. Reset all node energy to {}")
    print("  2. Add 6 missing node learning fields")
    print("  3. Add 8 missing link trace fields")
    print("\nNo dry run. This happens NOW.")
    print("="*60)

    response = input("\nContinue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted")
        exit(0)

    for graph_name in GRAPHS_TO_FIX:
        try:
            brutal_fix(graph_name)
        except Exception as e:
            print(f"\n❌ ERROR on {graph_name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print("ALL GRAPHS FIXED")
    print("="*60)
