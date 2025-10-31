"""
Migrate Consciousness Graphs to Universal Type Schema

Maps deprecated level-specific types to new universal types:
- Memory → U4_Event
- Person → U4_Agent
- Personal_Pattern → U3_Pattern
- Personal_Goal → U4_Goal
- Relationship → U3_Relationship
- Human, AI_Agent, External_Person → U4_Agent
- Decision → U4_Decision
- Task, Milestone → U4_Work_Item
- Risk → U3_Risk
- Metric → U4_Metric
- Best_Practice, Anti_Pattern → U3_Pattern
- Event → U4_Event
- Behavioral_Pattern → U3_Pattern
- Reputation_Assessment, Psychological_Trait → U4_Assessment

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

from falkordb import FalkorDB
from datetime import datetime
import sys

# Mapping: old_type → (new_type, level, type_specific_mappings)
TYPE_MIGRATIONS = {
    # N1 → Universal
    "Memory": {
        "new_type": "U4_Event",
        "level": "L1",
        "universality": "U4",
        "field_mappings": {
            "event_kind": "percept",  # Default, could be inferred
        }
    },
    "Person": {
        "new_type": "U4_Agent",
        "level": "L1",
        "universality": "U4",
        "field_mappings": {
            "agent_type": "human",
        }
    },
    "Personal_Pattern": {
        "new_type": "U3_Pattern",
        "level": "L1",
        "universality": "U3",
        "field_mappings": {
            "pattern_type": "habit",
            "valence": "neutral",  # Default, should be inferred if possible
        }
    },
    "Personal_Goal": {
        "new_type": "U4_Goal",
        "level": "L1",
        "universality": "U4",
        "field_mappings": {
            "horizon": "monthly",  # Default
        }
    },
    "Relationship": {
        "new_type": "U3_Relationship",
        "level": "L1",
        "universality": "U3",
        "field_mappings": {
            "relationship_type": "personal",
        }
    },

    # N2 → Universal
    "Human": {
        "new_type": "U4_Agent",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {
            "agent_type": "human",
        }
    },
    "AI_Agent": {
        "new_type": "U4_Agent",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {
            "agent_type": "citizen",
        }
    },
    "Decision": {
        "new_type": "U4_Decision",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {}
    },
    "Task": {
        "new_type": "U4_Work_Item",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {
            "work_type": "task",
            "state": "todo",  # Default
            "priority": "medium",  # Default
        }
    },
    "Milestone": {
        "new_type": "U4_Work_Item",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {
            "work_type": "milestone",
            "state": "todo",
            "priority": "high",
        }
    },
    "Risk": {
        "new_type": "U3_Risk",
        "level": "L2",
        "universality": "U3",
        "field_mappings": {
            "likelihood": 0.5,  # Default
            "impact": 0.5,  # Default
        }
    },
    "Metric": {
        "new_type": "U4_Metric",
        "level": "L2",
        "universality": "U4",
        "field_mappings": {
            "unit": "count",  # Default
        }
    },
    "Best_Practice": {
        "new_type": "U3_Pattern",
        "level": "L2",
        "universality": "U3",
        "field_mappings": {
            "pattern_type": "best_practice",
            "valence": "positive",
        }
    },
    "Anti_Pattern": {
        "new_type": "U3_Pattern",
        "level": "L2",
        "universality": "U3",
        "field_mappings": {
            "pattern_type": "anti_pattern",
            "valence": "negative",
        }
    },

    # N3 → Universal
    "Event": {
        "new_type": "U4_Event",
        "level": "L3",
        "universality": "U4",
        "field_mappings": {
            "event_kind": "market",  # Default
        }
    },
    "External_Person": {
        "new_type": "U4_Agent",
        "level": "L3",
        "universality": "U4",
        "field_mappings": {
            "agent_type": "external_system",
        }
    },
    "Behavioral_Pattern": {
        "new_type": "U3_Pattern",
        "level": "L3",
        "universality": "U3",
        "field_mappings": {
            "pattern_type": "market_behavior",
            "valence": "neutral",
        }
    },
    "Reputation_Assessment": {
        "new_type": "U4_Assessment",
        "level": "L3",
        "universality": "U4",
        "field_mappings": {
            "domain": "reputation",
            "score": 0.5,  # Default
        }
    },
    "Psychological_Trait": {
        "new_type": "U4_Assessment",
        "level": "L3",
        "universality": "U4",
        "field_mappings": {
            "domain": "psychology",
            "score": 0.5,  # Default
        }
    },
}


def migrate_graph(graph_name: str, db: FalkorDB, dry_run: bool = False):
    """Migrate a single consciousness graph to universal types."""

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Migrating graph: {graph_name}")
    print("=" * 80)

    g = db.select_graph(graph_name)

    # Get citizen_id for scope_ref (from graph name)
    if "_" in graph_name:
        citizen_id = graph_name.split("_")[-1]  # Get last part after underscore
    else:
        citizen_id = "unknown"

    total_migrated = 0

    for old_type, migration in TYPE_MIGRATIONS.items():
        # Find all nodes of this old type
        result = g.query(f"MATCH (n:{old_type}) RETURN n.name as name, id(n) as node_id")

        if not result.result_set:
            continue

        count = len(result.result_set)
        print(f"\n  Found {count} nodes of type {old_type} → {migration['new_type']}")

        if dry_run:
            # Just report what would be migrated
            for record in result.result_set:
                print(f"    - {record[0]} (id: {record[1]})")
            total_migrated += count
            continue

        # Migrate each node
        for record in result.result_set:
            node_name = record[0]
            node_id = record[1]

            new_type = migration['new_type']
            level = migration['level']
            universality = migration['universality']

            # Build SET clause for new fields
            set_parts = []
            set_parts.append(f"n.node_type = '{new_type}'")
            set_parts.append(f"n.level = '{level}'")
            set_parts.append(f"n.scope_ref = '{citizen_id}'")
            set_parts.append(f"n.universality = '{universality}'")
            set_parts.append(f"n.status = 'active'")  # Default status

            # Add type-specific field mappings
            for field_name, field_value in migration['field_mappings'].items():
                if isinstance(field_value, str):
                    set_parts.append(f"n.{field_name} = '{field_value}'")
                else:
                    set_parts.append(f"n.{field_name} = {field_value}")

            set_clause = ", ".join(set_parts)

            # Update node properties
            try:
                g.query(f"""
                    MATCH (n:{old_type})
                    WHERE id(n) = {node_id}
                    SET {set_clause}
                """)

                # Update labels: remove old, add new + universality
                g.query(f"""
                    MATCH (n:{old_type})
                    WHERE id(n) = {node_id}
                    REMOVE n:{old_type}
                    SET n:{new_type}:{universality}
                """)

                print(f"    ✓ {node_name}")
                total_migrated += 1

            except Exception as e:
                print(f"    ✗ {node_name}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Total nodes migrated: {total_migrated}")
    print("=" * 80)

    return total_migrated


def verify_migration(graph_name: str, db: FalkorDB):
    """Verify migration completed successfully."""

    print(f"\nVerifying graph: {graph_name}")
    print("=" * 80)

    g = db.select_graph(graph_name)

    # Check for any remaining deprecated types
    deprecated_found = False
    for old_type in TYPE_MIGRATIONS.keys():
        result = g.query(f"MATCH (n:{old_type}) RETURN count(n) as count")
        count = result.result_set[0][0] if result.result_set else 0
        if count > 0:
            print(f"  ⚠ Still found {count} nodes of deprecated type {old_type}")
            deprecated_found = True

    if not deprecated_found:
        print("  ✓ No deprecated types found")

    # Count universal types
    universal_counts = {}
    for migration in set(m['new_type'] for m in TYPE_MIGRATIONS.values()):
        result = g.query(f"MATCH (n:{migration}) RETURN count(n) as count")
        count = result.result_set[0][0] if result.result_set else 0
        if count > 0:
            universal_counts[migration] = count

    print("\n  Universal type counts:")
    for utype, count in sorted(universal_counts.items()):
        print(f"    {utype:25s} {count:4d} nodes")

    print("=" * 80)


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 80)
    print("CONSCIOUSNESS GRAPH MIGRATION TO UNIVERSAL TYPES")
    print("=" * 80)
    if dry_run:
        print("*** DRY RUN MODE - No changes will be made ***")
        print("=" * 80)

    db = FalkorDB(host='localhost', port=6379)

    # Get list of consciousness graphs
    # Actual format: consciousness-infrastructure_mind-protocol_<citizen>
    graphs_to_migrate = [
        "consciousness-infrastructure_mind-protocol_ada",
        "consciousness-infrastructure_mind-protocol_atlas",
        "consciousness-infrastructure_mind-protocol_felix",
        "consciousness-infrastructure_mind-protocol_iris",
        "consciousness-infrastructure_mind-protocol_luca",
        "consciousness-infrastructure_mind-protocol_victor",
    ]

    total_across_all = 0

    for graph_name in graphs_to_migrate:
        try:
            migrated = migrate_graph(graph_name, db, dry_run=dry_run)
            total_across_all += migrated

            if not dry_run:
                verify_migration(graph_name, db)

        except Exception as e:
            print(f"\n✗ Error migrating {graph_name}: {e}")
            continue

    print("\n" + "=" * 80)
    print(f"{'[DRY RUN] ' if dry_run else ''}MIGRATION COMPLETE")
    print("=" * 80)
    print(f"Total nodes migrated across all graphs: {total_across_all}")

    if dry_run:
        print("\nRun without --dry-run to apply changes")
    else:
        print("\n✓ All consciousness graphs migrated to universal types")
        print("✓ Schema refactor complete")


if __name__ == "__main__":
    main()
