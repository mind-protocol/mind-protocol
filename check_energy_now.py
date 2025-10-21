"""
Quick Check: Is Energy Being Injected?

Checks if any citizen graphs have received energy updates recently.

Author: Felix "Ironhand"
Date: 2025-10-21
"""

import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("=" * 80)
print("ENERGY INJECTION VERIFICATION")
print("=" * 80)
print()

citizens = ['felix', 'luca', 'iris', 'ada', 'piero', 'marco']

for citizen_id in citizens:
    graph_name = f"citizen_{citizen_id}"

    print(f"\n{citizen_id.upper()} (graph: {graph_name}):")
    print("-" * 40)

    # Count nodes with energy > 0 for this citizen
    query = """
    MATCH (n)
    WHERE n.energy IS NOT NULL
    RETURN n.name, n.energy
    LIMIT 10
    """

    result = r.execute_command('GRAPH.QUERY', graph_name, query)

    nodes_with_energy = 0
    max_energy = 0.0

    if result and result[1]:
        for row in result[1]:
            name = row[0]
            energy_value = row[1]

            try:
                parsed = json.loads(energy_value) if isinstance(energy_value, str) else energy_value
                if isinstance(parsed, dict):
                    citizen_energy = parsed.get(citizen_id, 0.0)
                else:
                    citizen_energy = float(parsed)
            except:
                citizen_energy = 0.0

            if citizen_energy > 0:
                nodes_with_energy += 1
                max_energy = max(max_energy, citizen_energy)
                print(f"   • {name[:60]}: energy={citizen_energy:.3f}")

    if nodes_with_energy == 0:
        print(f"   ⚠️  NO energy found in any nodes")
    else:
        print(f"\n   ✅ {nodes_with_energy} nodes have energy > 0")
        print(f"   📈 Max energy: {max_energy:.3f}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()
print("If all citizens show 'NO energy', then automatic injection is NOT working.")
print("Expected: At least some nodes should have energy > 0 after messages.")
print()
