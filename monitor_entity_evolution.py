#!/usr/bin/env python
"""Monitor entity evolution across citizens."""

import requests
import json
import time
from datetime import datetime

def get_entity_states():
    """Get current entity states from API."""
    try:
        response = requests.get('http://localhost:8000/api/consciousness/status', timeout=5)
        data = response.json()

        states = {}
        for citizen_id, info in data['engines'].items():
            states[citizen_id] = {
                'tick_count': info['tick_count'],
                'consciousness_state': info['consciousness_state'],
                'sub_entity_count': info['sub_entity_count'],
                'nodes': info['nodes'],
                'links': info['links'],
                'sub_entities': info.get('sub_entities', [])
            }
        return states
    except Exception as e:
        print(f"Error fetching states: {e}")
        return {}

def monitor_evolution(duration_minutes=5, sample_interval_seconds=30):
    """Monitor entity evolution over time."""
    print(f"=== ENTITY EVOLUTION MONITOR ===")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Sample interval: {sample_interval_seconds} seconds")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")

    samples = []
    end_time = time.time() + (duration_minutes * 60)
    sample_num = 0

    while time.time() < end_time:
        sample_num += 1
        timestamp = datetime.now().strftime('%H:%M:%S')

        states = get_entity_states()
        if states:
            samples.append({
                'timestamp': timestamp,
                'states': states
            })

            print(f"[T+{sample_num*sample_interval_seconds:03d}s] {timestamp}")
            for citizen_id, state in states.items():
                print(f"  {citizen_id:15s}: tick {state['tick_count']:5d}, "
                      f"entities {state['sub_entity_count']}, "
                      f"nodes {state['nodes']:4d}, "
                      f"state {state['consciousness_state']}")
            print()

        time.sleep(sample_interval_seconds)

    # Analyze evolution
    print("\n=== EVOLUTION ANALYSIS ===\n")

    if len(samples) >= 2:
        first = samples[0]['states']
        last = samples[-1]['states']

        for citizen_id in first.keys():
            if citizen_id in last:
                tick_delta = last[citizen_id]['tick_count'] - first[citizen_id]['tick_count']
                node_delta = last[citizen_id]['nodes'] - first[citizen_id]['nodes']
                link_delta = last[citizen_id]['links'] - first[citizen_id]['links']
                entity_delta = last[citizen_id]['sub_entity_count'] - first[citizen_id]['sub_entity_count']

                print(f"{citizen_id}:")
                print(f"  Ticks: {first[citizen_id]['tick_count']} → {last[citizen_id]['tick_count']} (+{tick_delta})")
                print(f"  Nodes: {first[citizen_id]['nodes']} → {last[citizen_id]['nodes']} ({node_delta:+d})")
                print(f"  Links: {first[citizen_id]['links']} → {last[citizen_id]['links']} ({link_delta:+d})")
                print(f"  Entities: {first[citizen_id]['sub_entity_count']} → {last[citizen_id]['sub_entity_count']} ({entity_delta:+d})")

                # Check entity stability
                first_entities = set(first[citizen_id]['sub_entities'])
                last_entities = set(last[citizen_id]['sub_entities'])

                if first_entities == last_entities:
                    print(f"  Entity set: STABLE (all {len(first_entities)} entities preserved)")
                else:
                    added = last_entities - first_entities
                    removed = first_entities - last_entities
                    if added:
                        print(f"  Entities added: {added}")
                    if removed:
                        print(f"  Entities removed: {removed}")
                print()

    # Save full data
    output_file = f"entity_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(samples, f, indent=2)

    print(f"Full data saved to: {output_file}")

if __name__ == '__main__':
    monitor_evolution(duration_minutes=5, sample_interval_seconds=30)
