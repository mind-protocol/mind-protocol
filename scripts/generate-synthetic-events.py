#!/usr/bin/env python3
"""
Generate synthetic Mind Protocol event data for visualizer

Layered network layout:
- Each level (L4, L3, L2, L1) is a horizontal 2D graph plane
- Nodes within a level are arranged in force-directed or clustered layouts
- Horizontal edges within levels, vertical edges between levels
"""

import json
import math
import random
from datetime import datetime, timedelta

# La Serenissima citizens (L1 - U4_Agent with agent_type=citizen)
CITIZENS = [
    {"id": "emma", "name": "Emma", "role": "scout"},
    {"id": "rafael", "name": "Rafael", "role": "harbor"},
    {"id": "aicha", "name": "Aïcha", "role": "architect"},
    {"id": "daniel", "name": "Daniel", "role": "forge"},
    {"id": "sofia", "name": "Sofia", "role": "gauge"},
    {"id": "maya", "name": "Maya", "role": "facet"},
    {"id": "priya", "name": "Priya", "role": "pulse"}
]

# L4 Protocol nodes (L4_* types)
PROTOCOL_NODES = [
    {
        "id": "schema_proposal_input",
        "type_name": "L4_Event_Schema",
        "name": "proposal.input.ready",
        "version": "1.0.0",
        "topic": "proposal.input.ready"
    },
    {
        "id": "schema_review_verdict",
        "type_name": "L4_Event_Schema",
        "name": "review.verdict",
        "version": "1.0.0",
        "topic": "review.verdict"
    },
    {
        "id": "schema_ac_green",
        "type_name": "L4_Event_Schema",
        "name": "ac.green",
        "version": "1.0.0",
        "topic": "ac.green"
    },
    {
        "id": "policy_permissions",
        "type_name": "L4_Governance_Policy",
        "name": "Permission Policy",
        "policy_id": "POL-001",
        "status": "active"
    },
    {
        "id": "policy_rate_limit",
        "type_name": "L4_Governance_Policy",
        "name": "Rate Limit Policy",
        "policy_id": "POL-002",
        "status": "active"
    },
    {
        "id": "topic_telemetry",
        "type_name": "L4_Topic_Namespace",
        "name": "telemetry.*",
        "notes": "All telemetry events"
    },
    {
        "id": "tier_citizen",
        "type_name": "L4_Autonomy_Tier",
        "name": "Citizen Tier",
        "tier_number": 2,
        "min_reliability_score": 0.8
    }
]

# L3 Ecosystem node
ECOSYSTEM_NODE = {
    "id": "ecosystem_serenissima",
    "type_name": "U4_Agent",
    "name": "La Serenissima Ecosystem",
    "agent_type": "dao",
    "level": "L3",
    "status": "active"
}

# L2 Organization node
ORG_NODE = {
    "id": "org_serenissima",
    "type_name": "U4_Agent",
    "name": "La Serenissima",
    "agent_type": "org",
    "level": "L2",
    "status": "active"
}

def circular_layout(count, radius, y):
    """Generate circular layout on horizontal plane"""
    positions = []
    for i in range(count):
        angle = (2 * math.pi / count) * i
        positions.append({
            "x": round(radius * math.cos(angle), 2),
            "y": y,
            "z": round(radius * math.sin(angle), 2)
        })
    return positions

def grid_layout(count, spacing, y):
    """Generate grid layout on horizontal plane"""
    positions = []
    cols = math.ceil(math.sqrt(count))
    for i in range(count):
        row = i // cols
        col = i % cols
        positions.append({
            "x": round((col - cols/2) * spacing, 2),
            "y": y,
            "z": round((row - cols/2) * spacing, 2)
        })
    return positions

def generate_energy_diffusion_events(start_time, count=30):
    """Generate energy diffusion events between L1 citizens"""
    events = []
    for i in range(count):
        timestamp = (start_time + timedelta(seconds=i * 10)).isoformat()
        source = random.choice(CITIZENS)
        target = random.choice([c for c in CITIZENS if c != source])
        energy_transferred = 0.1 + random.random() * 0.4

        events.append({
            "type": "energy.diffusion",
            "timestamp": timestamp,
            "source_node": source["id"],
            "target_node": target["id"],
            "source_layer": "L1",
            "target_layer": "L1",
            "energy_transferred": energy_transferred,
            "duration_ms": 1500
        })
    return events

def generate_activation_switches(start_time, count=15):
    """Generate working memory entry/exit events"""
    events = []
    in_working_memory = set()

    for i in range(count):
        timestamp = (start_time + timedelta(seconds=i * 15 + 5)).isoformat()
        citizen = random.choice(CITIZENS)

        if citizen["id"] in in_working_memory:
            action = "exit"
            in_working_memory.remove(citizen["id"])
        else:
            action = "enter"
            in_working_memory.add(citizen["id"])
            if len(in_working_memory) > 12:
                kicked_out = random.choice(list(in_working_memory))
                in_working_memory.remove(kicked_out)

        events.append({
            "type": "activation.switch",
            "timestamp": timestamp,
            "node": citizen["id"],
            "layer": "L1",
            "action": action,
            "working_memory_position": len(in_working_memory) if action == "enter" else None,
            "energy": 0.7 + random.random() * 0.3
        })
    return events

def generate_membrane_crossings(start_time, count=10):
    """Generate L1↔L2 membrane crossing events"""
    events = []

    for i in range(count):
        timestamp = (start_time + timedelta(seconds=i * 25 + 8)).isoformat()

        if random.random() < 0.7:
            source = random.choice(CITIZENS)
            events.append({
                "type": "membrane.crossing",
                "timestamp": timestamp,
                "source_node": source["id"],
                "source_layer": "L1",
                "target_node": ORG_NODE["id"],
                "target_layer": "L2",
                "direction": "up",
                "permeability": 0.5 + random.random() * 0.5,
                "energy_transferred": 0.3 + random.random() * 0.6,
                "accepted": random.random() > 0.1
            })
        else:
            target = random.choice(CITIZENS)
            events.append({
                "type": "membrane.crossing",
                "timestamp": timestamp,
                "source_node": ORG_NODE["id"],
                "source_layer": "L2",
                "target_node": target["id"],
                "target_layer": "L1",
                "direction": "down",
                "permeability": 0.6 + random.random() * 0.4,
                "energy_transferred": 0.4 + random.random() * 0.5,
                "accepted": True
            })
    return events

def generate_snapshot():
    """Generate layered network with horizontal planes per level"""
    nodes = []

    # L4 (Protocol): Y=150, circular layout
    l4_positions = circular_layout(len(PROTOCOL_NODES), 180, 150)
    for i, node in enumerate(PROTOCOL_NODES):
        nodes.append({
            "id": node["id"],
            "type_name": node["type_name"],
            "name": node["name"],
            "level": "L4",
            "labels": ["protocol", node["type_name"]],
            "position": l4_positions[i],
            "energy": 0.5,
            **{k: v for k, v in node.items() if k not in ["id", "type_name", "name"]}
        })

    # L3 (Ecosystem): Y=50, center position
    nodes.append({
        "id": ECOSYSTEM_NODE["id"],
        "type_name": ECOSYSTEM_NODE["type_name"],
        "name": ECOSYSTEM_NODE["name"],
        "level": "L3",
        "agent_type": ECOSYSTEM_NODE["agent_type"],
        "labels": ["ecosystem", "dao"],
        "position": {"x": 0, "y": 50, "z": 0},
        "energy": 0.9,
        "status": ECOSYSTEM_NODE["status"]
    })

    # L2 (Organization): Y=-50, center position
    nodes.append({
        "id": ORG_NODE["id"],
        "type_name": ORG_NODE["type_name"],
        "name": ORG_NODE["name"],
        "level": "L2",
        "agent_type": ORG_NODE["agent_type"],
        "labels": ["organization", "org"],
        "position": {"x": 0, "y": -50, "z": 0},
        "energy": 0.85,
        "status": ORG_NODE["status"]
    })

    # L1 (Citizen + Knowledge/Goals/Work): Y=-150, grid layout for dense graph
    l1_items = []

    # Citizens in inner circle
    citizen_positions = circular_layout(len(CITIZENS), 120, -150)
    for i, citizen in enumerate(CITIZENS):
        l1_items.append({
            "id": citizen["id"],
            "type_name": "U4_Agent",
            "name": citizen["name"],
            "level": "L1",
            "agent_type": "citizen",
            "role": citizen["role"],
            "labels": ["citizen", citizen["role"]],
            "position": citizen_positions[i],
            "energy": 0.6 + random.random() * 0.4,
            "status": "active",
            "cluster": "citizens"
        })

    # Knowledge objects clustered around each citizen
    for i, citizen in enumerate(CITIZENS):
        base_pos = citizen_positions[i]
        for j in range(2):
            angle = random.uniform(0, 2 * math.pi)
            offset_r = random.uniform(15, 30)
            l1_items.append({
                "id": f"{citizen['id']}_knowledge_{j}",
                "type_name": "U4_Knowledge_Object",
                "name": f"{citizen['name']} Doc {j+1}",
                "level": "L1",
                "ko_type": random.choice(["spec", "runbook", "guide"]),
                "labels": ["knowledge"],
                "position": {
                    "x": round(base_pos["x"] + offset_r * math.cos(angle), 2),
                    "y": -150,
                    "z": round(base_pos["z"] + offset_r * math.sin(angle), 2)
                },
                "energy": 0.3 + random.random() * 0.5,
                "status": "active",
                "cluster": f"citizen_{citizen['id']}"
            })

    # Goals in center cluster
    for i in range(3):
        angle = (2 * math.pi / 3) * i
        l1_items.append({
            "id": f"goal_{i}",
            "type_name": "U4_Goal",
            "name": f"Q1-{i+1}",
            "level": "L1",
            "horizon": "quarterly",
            "labels": ["goal"],
            "position": {
                "x": round(40 * math.cos(angle), 2),
                "y": -150,
                "z": round(40 * math.sin(angle), 2)
            },
            "energy": 0.7,
            "status": "active",
            "cluster": "goals"
        })

    # Work items scattered
    for i in range(5):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(60, 100)
        l1_items.append({
            "id": f"work_{i}",
            "type_name": "U4_Work_Item",
            "name": f"Task-{i+1}",
            "level": "L1",
            "work_type": random.choice(["task", "bug", "ticket"]),
            "priority": random.choice(["high", "medium", "low"]),
            "state": random.choice(["todo", "doing", "done"]),
            "labels": ["work"],
            "position": {
                "x": round(radius * math.cos(angle), 2),
                "y": -150,
                "z": round(radius * math.sin(angle), 2)
            },
            "energy": 0.5,
            "status": "active",
            "cluster": "work"
        })

    nodes.extend(l1_items)
    return nodes

def main():
    start_time = datetime.now() - timedelta(minutes=5)

    # Generate events
    all_events = []
    all_events.extend(generate_energy_diffusion_events(start_time, count=30))
    all_events.extend(generate_activation_switches(start_time, count=15))
    all_events.extend(generate_membrane_crossings(start_time, count=10))
    all_events.sort(key=lambda e: e["timestamp"])

    # Generate snapshot
    snapshot_nodes = generate_snapshot()

    # Save events
    events_output = {
        "timeline": all_events,
        "metadata": {
            "total_events": len(all_events),
            "generated_at": datetime.now().isoformat(),
            "source": "synthetic",
            "layout": "layered_network",
            "description": "Each level is a horizontal 2D graph plane",
            "time_range": {
                "start": all_events[0]["timestamp"],
                "end": all_events[-1]["timestamp"]
            },
            "event_types": {
                "energy.diffusion": len([e for e in all_events if e["type"] == "energy.diffusion"]),
                "activation.switch": len([e for e in all_events if e["type"] == "activation.switch"]),
                "membrane.crossing": len([e for e in all_events if e["type"] == "membrane.crossing"])
            }
        }
    }

    with open("/home/mind-protocol/mindprotocol/public/data/events.json", "w") as f:
        json.dump(events_output, f, indent=2)

    # Save snapshot
    snapshot_output = {
        "nodes": snapshot_nodes,
        "metadata": {
            "total_nodes": len(snapshot_nodes),
            "generated_at": datetime.now().isoformat(),
            "layout": "layered_network",
            "description": "Horizontal planes at Y=150 (L4), Y=50 (L3), Y=-50 (L2), Y=-150 (L1)",
            "node_types": {
                "U4_Agent": len([n for n in snapshot_nodes if n["type_name"] == "U4_Agent"]),
                "U4_Knowledge_Object": len([n for n in snapshot_nodes if n["type_name"] == "U4_Knowledge_Object"]),
                "U4_Goal": len([n for n in snapshot_nodes if n["type_name"] == "U4_Goal"]),
                "U4_Work_Item": len([n for n in snapshot_nodes if n["type_name"] == "U4_Work_Item"]),
                "L4_Event_Schema": len([n for n in snapshot_nodes if n["type_name"] == "L4_Event_Schema"]),
                "L4_Governance_Policy": len([n for n in snapshot_nodes if n["type_name"] == "L4_Governance_Policy"]),
                "L4_Topic_Namespace": len([n for n in snapshot_nodes if n["type_name"] == "L4_Topic_Namespace"]),
                "L4_Autonomy_Tier": len([n for n in snapshot_nodes if n["type_name"] == "L4_Autonomy_Tier"])
            },
            "layers": {
                "L4_protocol": len([n for n in snapshot_nodes if n["level"] == "L4"]),
                "L3_ecosystem": len([n for n in snapshot_nodes if n["level"] == "L3"]),
                "L2_organization": len([n for n in snapshot_nodes if n["level"] == "L2"]),
                "L1_citizen": len([n for n in snapshot_nodes if n["level"] == "L1"])
            }
        }
    }

    with open("/home/mind-protocol/mindprotocol/public/data/snapshot.json", "w") as f:
        json.dump(snapshot_output, f, indent=2)

    print(f"✅ Generated {len(all_events)} events")
    print(f"✅ Generated {len(snapshot_nodes)} nodes")
    print(f"✅ Layout: Layered network (horizontal planes)")
    print(f"\n📊 Node type breakdown:")
    for node_type, count in snapshot_output["metadata"]["node_types"].items():
        print(f"  - {node_type}: {count}")
    print(f"\n📊 Layer breakdown:")
    for layer, count in snapshot_output["metadata"]["layers"].items():
        print(f"  - {layer}: {count}")

if __name__ == "__main__":
    main()
