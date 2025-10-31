#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schema Migration: Legacy Registry Types → L4_ Protocol Types

Migrates all graphs to use correct L4_ prefixes for protocol-level law nodes:
- Topic_Namespace → L4_Topic_Namespace
- Event_Schema → L4_Event_Schema
- Envelope_Schema → L4_Envelope_Schema
- Capability → L4_Capability
- U4_TopicNamespace → L4_Topic_Namespace (if exists)
- U4_EventSchema → L4_Event_Schema (if exists)
- U4_EnvelopeSchema → L4_Envelope_Schema (if exists)
- U4_Capability → L4_Capability (if exists)

Author: Luca Vellumhand (Consciousness Substrate Architect)
Date: 2025-10-31
"""

import os
import sys
from datetime import datetime
from falkordb import FalkorDB
from typing import List, Dict, Tuple


class SchemaMigrator:
    """Handles schema migration across all FalkorDB graphs."""

    def __init__(self, dry_run: bool = False):
        self.db = FalkorDB(host=os.getenv("FALKOR_HOST", "localhost"), port=6379)
        self.dry_run = dry_run
        self.results = {}

    def migrate_all_graphs(self, exclude_graphs: List[str] = None):
        """Migrate all graphs except excluded ones."""
        exclude_graphs = exclude_graphs or ["", "falkor", "test_db"]

        graphs = [g for g in self.db.list_graphs() if g not in exclude_graphs]

        print("=" * 80)
        print("SCHEMA MIGRATION: Legacy Types → L4_ Protocol Types")
        print("=" * 80)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}")
        print(f"Graphs to migrate: {len(graphs)}")
        print()

        for graph_name in graphs:
            print(f"{'[DRY RUN] ' if self.dry_run else ''}Migrating: {graph_name}")
            result = self.migrate_graph(graph_name)
            self.results[graph_name] = result
            print()

        self.print_summary()

    def migrate_graph(self, graph_name: str) -> Dict[str, int]:
        """Migrate a single graph."""
        g = self.db.select_graph(graph_name)
        result = {
            "topic_namespace": 0,
            "event_schema": 0,
            "envelope_schema": 0,
            "capability": 0,
            "errors": []
        }

        try:
            # 1. Migrate Topic_Namespace → L4_Topic_Namespace (legacy unprefixed)
            count1 = self._relabel_nodes(
                g, "Topic_Namespace", "L4_Topic_Namespace"
            )
            # Also check for U4_ variant
            count2 = self._relabel_nodes(
                g, "U4_TopicNamespace", "L4_Topic_Namespace"
            )
            result["topic_namespace"] = count1 + count2
            if count1 + count2 > 0:
                print(f"  ✓ Topic Namespaces: {count1 + count2} nodes relabeled")

            # 2. Migrate Event_Schema → L4_Event_Schema (legacy unprefixed)
            count1 = self._relabel_nodes(
                g, "Event_Schema", "L4_Event_Schema"
            )
            # Also check for U4_ variant
            count2 = self._relabel_nodes(
                g, "U4_EventSchema", "L4_Event_Schema"
            )
            result["event_schema"] = count1 + count2
            if count1 + count2 > 0:
                print(f"  ✓ Event Schemas: {count1 + count2} nodes relabeled")

            # 3. Migrate Envelope_Schema → L4_Envelope_Schema (legacy unprefixed)
            count1 = self._relabel_nodes(
                g, "Envelope_Schema", "L4_Envelope_Schema"
            )
            # Also check for U4_ variant
            count2 = self._relabel_nodes(
                g, "U4_EnvelopeSchema", "L4_Envelope_Schema"
            )
            result["envelope_schema"] = count1 + count2
            if count1 + count2 > 0:
                print(f"  ✓ Envelope Schemas: {count1 + count2} nodes relabeled")

            # 4. Migrate Capability → L4_Capability (both legacy and U4_)
            count = self._migrate_capabilities(g)
            result["capability"] = count
            if count > 0:
                print(f"  ✓ Capabilities: {count} nodes migrated")

        except Exception as e:
            result["errors"].append(str(e))
            print(f"  ✗ Error: {e}")

        return result

    def _relabel_nodes(self, graph, old_label: str, new_label: str) -> int:
        """Relabel nodes from old type to new type."""

        # First, count how many nodes need migration
        count_query = f"""
            MATCH (n:{old_label})
            RETURN count(n) as count
        """
        result = graph.query(count_query)
        count = result.result_set[0][0] if result.result_set else 0

        if count == 0:
            return 0

        if self.dry_run:
            return count

        # Remove old label, add new label, update type_name
        migration_query = f"""
            MATCH (n:{old_label})
            REMOVE n:{old_label}
            SET n:{new_label}, n.type_name = '{new_label}'
            RETURN count(n) as migrated
        """

        result = graph.query(migration_query)
        return result.result_set[0][0] if result.result_set else 0

    def _migrate_capabilities(self, graph) -> int:
        """
        Migrate Capability → L4_Capability.

        Handles both legacy unprefixed and U4_ prefixed versions.
        """

        total = 0

        # Migrate legacy unprefixed Capability
        count1 = self._relabel_nodes(graph, "Capability", "L4_Capability")
        total += count1

        # Migrate U4_Capability if exists
        count2 = self._relabel_nodes(graph, "U4_Capability", "L4_Capability")
        total += count2

        return total

    def print_summary(self):
        """Print migration summary."""
        print()
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print()

        total_topic = sum(r["topic_namespace"] for r in self.results.values())
        total_event = sum(r["event_schema"] for r in self.results.values())
        total_envelope = sum(r["envelope_schema"] for r in self.results.values())
        total_capability = sum(r["capability"] for r in self.results.values())

        graphs_with_errors = [g for g, r in self.results.items() if r["errors"]]
        graphs_with_changes = [g for g, r in self.results.items()
                               if any(r[k] > 0 for k in ["topic_namespace", "event_schema", "envelope_schema", "capability"])]

        print(f"Total Nodes Migrated:")
        print(f"  - Topic Namespaces:   {total_topic:3d} nodes")
        print(f"  - Event Schemas:      {total_event:3d} nodes")
        print(f"  - Envelope Schemas:   {total_envelope:3d} nodes")
        print(f"  - Capabilities:       {total_capability:3d} nodes")
        print(f"  - TOTAL:              {total_topic + total_event + total_envelope + total_capability:3d} nodes")
        print()

        if graphs_with_changes:
            print(f"Graphs Modified ({len(graphs_with_changes)}):")
            for graph_name in graphs_with_changes:
                r = self.results[graph_name]
                changes = []
                if r["topic_namespace"] > 0:
                    changes.append(f"topics:{r['topic_namespace']}")
                if r["event_schema"] > 0:
                    changes.append(f"events:{r['event_schema']}")
                if r["envelope_schema"] > 0:
                    changes.append(f"envelopes:{r['envelope_schema']}")
                if r["capability"] > 0:
                    changes.append(f"capabilities:{r['capability']}")
                print(f"  - {graph_name}: {', '.join(changes)}")
            print()

        if graphs_with_errors:
            print(f"Graphs with Errors ({len(graphs_with_errors)}):")
            for graph_name in graphs_with_errors:
                errors = self.results[graph_name]["errors"]
                print(f"  - {graph_name}: {errors}")
            print()

        print("=" * 80)
        if self.dry_run:
            print("DRY RUN COMPLETE - No changes made")
        else:
            print("MIGRATION COMPLETE")
        print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate U4_ registry types to L4_ protocol types"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes"
    )
    parser.add_argument(
        "--graph",
        type=str,
        help="Migrate only this specific graph"
    )
    parser.add_argument(
        "--exclude",
        type=str,
        nargs="+",
        default=["", "falkor", "test_db"],
        help="Graphs to exclude from migration"
    )

    args = parser.parse_args()

    migrator = SchemaMigrator(dry_run=args.dry_run)

    if args.graph:
        print(f"Migrating single graph: {args.graph}")
        result = migrator.migrate_graph(args.graph)
        migrator.results[args.graph] = result
        migrator.print_summary()
    else:
        migrator.migrate_all_graphs(exclude_graphs=args.exclude)

    # Exit code: 0 if no errors, 1 if any errors
    has_errors = any(r["errors"] for r in migrator.results.values())
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
