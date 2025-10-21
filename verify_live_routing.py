"""
Verify that the live TRACE format from conversation was routed correctly.
"""
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("=" * 70)
print("LIVE ROUTING VERIFICATION")
print("=" * 70)

# Check for the personal node
print("\n1. Personal Node (scope: personal)")
print("   Expected: ONLY in citizen_felix")

personal_in_felix = r.execute_command('GRAPH.QUERY', 'citizen_felix',
    'MATCH (n {name: "live_test_scope_routing_works"}) RETURN count(n)')[1][0]
personal_in_org = r.execute_command('GRAPH.QUERY', 'org_mind_protocol',
    'MATCH (n {name: "live_test_scope_routing_works"}) RETURN count(n)')[1][0]

print(f"   - citizen_felix: {personal_in_felix} (expected: 1)")
print(f"   - org_mind_protocol: {personal_in_org} (expected: 0)")

if personal_in_felix == 1 and personal_in_org == 0:
    print("   ✅ CORRECT ROUTING")
else:
    print("   ❌ ROUTING FAILED")

# Check for the organizational node
print("\n2. Organizational Node (scope: organizational)")
print("   Expected: ONLY in org_mind_protocol")

org_in_felix = r.execute_command('GRAPH.QUERY', 'citizen_felix',
    'MATCH (n {name: "use_switch_graph_for_falkordb_routing"}) RETURN count(n)')[1][0]
org_in_org = r.execute_command('GRAPH.QUERY', 'org_mind_protocol',
    'MATCH (n {name: "use_switch_graph_for_falkordb_routing"}) RETURN count(n)')[1][0]

print(f"   - citizen_felix: {org_in_felix} (expected: 0)")
print(f"   - org_mind_protocol: {org_in_org} (expected: 1)")

if org_in_felix == 0 and org_in_org == 1:
    print("   ✅ CORRECT ROUTING")
else:
    print("   ❌ ROUTING FAILED")

# Check for the link
print("\n3. ENABLES Link (scope: organizational)")
print("   Expected: ONLY in org_mind_protocol")

link_in_felix = r.execute_command('GRAPH.QUERY', 'citizen_felix',
    'MATCH ()-[r:ENABLES]->() RETURN count(r)')[1][0]
link_in_org = r.execute_command('GRAPH.QUERY', 'org_mind_protocol',
    'MATCH ()-[r:ENABLES]->() RETURN count(r)')[1][0]

print(f"   - citizen_felix: {link_in_felix} ENABLES links")
print(f"   - org_mind_protocol: {link_in_org} ENABLES links")

# Check falkor graph (should have NO new test nodes)
print("\n4. Default 'falkor' Graph")
print("   Expected: NO test nodes (old bug would put them here)")

test_in_falkor = r.execute_command('GRAPH.QUERY', 'falkor',
    'MATCH (n) WHERE n.name CONTAINS "live_test" OR n.name CONTAINS "use_switch_graph" RETURN count(n)')[1][0]

print(f"   - Test nodes in falkor: {test_in_falkor} (expected: 0)")

if test_in_falkor == 0:
    print("   ✅ NO CONTAMINATION")
else:
    print("   ❌ NODES LEAKED TO FALKOR")

# Final verdict
print("\n" + "=" * 70)
if (personal_in_felix == 1 and personal_in_org == 0 and
    org_in_felix == 0 and org_in_org == 1 and test_in_falkor == 0):
    print("✅ SUCCESS: SCOPE ROUTING WORKS IN LIVE CONVERSATIONS!")
    print("=" * 70)
    print("\nFormations are correctly routed to graphs based on scope:")
    print("  • scope: personal → citizen_felix")
    print("  • scope: organizational → org_mind_protocol")
    print("  • No cross-contamination")
    print("  • No leakage to default 'falkor' graph")
else:
    print("❌ FAILURE: Routing issues detected")
    print("=" * 70)
