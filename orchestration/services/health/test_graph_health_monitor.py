"""
Test script for GraphHealthMonitor service.

Validates:
- Metric computation against real FalkorDB data
- Percentile calculations
- Health status judgments
- Event payload structure
"""
import asyncio
import sys
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock
import json

from orchestration.services.health.graph_health_monitor import (
    GraphHealthMonitor,
    HealthStatus,
    GraphHealthSnapshot
)


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def record_pass(self, test_name: str):
        self.passed += 1
        print(f"✓ {test_name}")

    def record_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"✗ {test_name}: {reason}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print(f"\nFailures:")
            for test_name, reason in self.errors:
                print(f"  - {test_name}: {reason}")
        print(f"{'='*60}")
        return self.failed == 0


async def test_graph_health_monitor():
    """Main test function"""
    results = TestResults()

    # Create mock WebSocket server
    mock_ws = Mock()
    mock_ws.broadcast = AsyncMock()

    print("Initializing GraphHealthMonitor...")
    try:
        monitor = GraphHealthMonitor(
            websocket_server=mock_ws,
            falkordb_host="localhost",
            falkordb_port=6379,
            interval_seconds=60,
            history_window_days=30
        )
        results.record_pass("GraphHealthMonitor initialization")
    except Exception as e:
        results.record_fail("GraphHealthMonitor initialization", str(e))
        return results.summary()

    # Test: Get active graphs
    print("\n--- Testing get_active_graphs() ---")
    try:
        graphs = await monitor.get_active_graphs()
        if len(graphs) > 0:
            results.record_pass(f"get_active_graphs() returned {len(graphs)} graphs: {graphs}")
        else:
            results.record_fail("get_active_graphs()", "No graphs found")
    except Exception as e:
        results.record_fail("get_active_graphs()", str(e))
        return results.summary()

    # Pick first graph for detailed testing
    test_graph_id = graphs[0]
    print(f"\nUsing graph '{test_graph_id}' for detailed testing...")

    # Test: Compute health snapshot
    print(f"\n--- Testing compute_health_snapshot('{test_graph_id}') ---")
    try:
        snapshot = await monitor.compute_health_snapshot(test_graph_id)
        results.record_pass("compute_health_snapshot() executed")

        # Validate snapshot structure
        if not isinstance(snapshot, GraphHealthSnapshot):
            results.record_fail("snapshot type check", f"Expected GraphHealthSnapshot, got {type(snapshot)}")
        else:
            results.record_pass("snapshot is GraphHealthSnapshot instance")

        # Check required fields
        required_fields = ['graph_id', 'timestamp', 'overall_status', 'flagged_metrics']
        for field in required_fields:
            if hasattr(snapshot, field):
                results.record_pass(f"snapshot has field '{field}'")
            else:
                results.record_fail(f"snapshot field '{field}'", "Missing field")

        # Print snapshot details
        print(f"\n  Graph ID: {snapshot.graph_id}")
        print(f"  Timestamp: {snapshot.timestamp}")
        print(f"  Overall Status: {snapshot.overall_status}")
        print(f"  Flagged Metrics: {snapshot.flagged_metrics}")

    except Exception as e:
        results.record_fail("compute_health_snapshot()", str(e))
        import traceback
        traceback.print_exc()
        return results.summary()

    # Test: Individual metrics
    print(f"\n--- Testing Individual Metrics ---")

    # Density
    if snapshot.density:
        print(f"\n  Density Metric:")
        print(f"    Subentities: {snapshot.density.entities}")
        print(f"    Nodes: {snapshot.density.nodes}")
        print(f"    Density: {snapshot.density.density:.4f}")
        print(f"    Percentile: {snapshot.density.percentile:.1f}")
        print(f"    Status: {snapshot.density.status}")

        if snapshot.density.nodes > 0:
            results.record_pass("Density metric computed")
        else:
            results.record_fail("Density metric", "No nodes found")
    else:
        results.record_fail("Density metric", "None returned")

    # Overlap
    if snapshot.overlap:
        print(f"\n  Overlap Metric:")
        print(f"    Total Nodes: {snapshot.overlap.total_nodes}")
        print(f"    Total Memberships: {snapshot.overlap.total_memberships}")
        print(f"    Overlap Ratio: {snapshot.overlap.overlap_ratio:.4f}")
        print(f"    Percentile: {snapshot.overlap.percentile:.1f}")
        print(f"    Status: {snapshot.overlap.status}")

        results.record_pass("Overlap metric computed")
    else:
        results.record_fail("Overlap metric", "None returned")

    # SubEntity Size
    if snapshot.entity_size:
        print(f"\n  SubEntity Size Metric:")
        print(f"    Median Size: {snapshot.entity_size.median_size}")
        print(f"    Mean Size: {snapshot.entity_size.mean_size:.2f}")
        print(f"    Gini Coefficient: {snapshot.entity_size.gini_coefficient:.4f}")
        print(f"    Status: {snapshot.entity_size.status}")
        if snapshot.entity_size.top_entities:
            print(f"    Top Subentities: {len(snapshot.entity_size.top_entities)}")

        results.record_pass("SubEntity size metric computed")
    else:
        results.record_fail("SubEntity size metric", "None returned")

    # Orphans
    if snapshot.orphans:
        print(f"\n  Orphans Metric:")
        print(f"    Total Nodes: {snapshot.orphans.total_nodes}")
        print(f"    Orphan Count: {snapshot.orphans.orphan_count}")
        print(f"    Orphan Ratio: {snapshot.orphans.orphan_ratio:.4f}")
        print(f"    Percentile: {snapshot.orphans.percentile:.1f}")
        print(f"    Status: {snapshot.orphans.status}")

        if snapshot.orphans.sample_orphans:
            print(f"    Sample Orphans: {len(snapshot.orphans.sample_orphans)} samples")
            for orphan in snapshot.orphans.sample_orphans[:3]:
                print(f"      - {orphan.get('name', orphan.get('id'))}")

        results.record_pass("Orphans metric computed")

        # Critical check: High orphan ratio
        if snapshot.orphans.orphan_ratio > 0.3:
            print(f"    ⚠️  HIGH ORPHAN RATIO: {snapshot.orphans.orphan_ratio:.1%}")
    else:
        results.record_fail("Orphans metric", "None returned")

    # Highways
    if snapshot.highways:
        print(f"\n  Highways Metric:")
        print(f"    Total Highways: {snapshot.highways.total_highways}")
        print(f"    Total Crossings: {snapshot.highways.total_crossings}")
        print(f"    Mean Crossings/Highway: {snapshot.highways.mean_crossings_per_highway:.2f}")
        print(f"    Status: {snapshot.highways.status}")
        if snapshot.highways.backbone_highways:
            print(f"    Backbone Highways: {len(snapshot.highways.backbone_highways)}")

        results.record_pass("Highways metric computed")
    else:
        results.record_fail("Highways metric", "None returned")

    # Test: WebSocket event emission
    print(f"\n--- Testing WebSocket Event Emission ---")
    try:
        await monitor.emit_snapshot(snapshot)

        # Check that broadcast was called
        if mock_ws.broadcast.called:
            results.record_pass("emit_snapshot() called broadcast")

            # Get the call arguments
            call_args = mock_ws.broadcast.call_args
            event_type = call_args[0][0] if call_args[0] else None
            event_data = call_args[0][1] if len(call_args[0]) > 1 else None

            if event_type == 'graph.health.snapshot':
                results.record_pass("Event type is 'graph.health.snapshot'")
            else:
                results.record_fail("Event type", f"Expected 'graph.health.snapshot', got '{event_type}'")

            if event_data and isinstance(event_data, dict):
                results.record_pass("Event data is dictionary")
                print(f"\n  Event payload keys: {list(event_data.keys())}")
            else:
                results.record_fail("Event data", "Not a dictionary")
        else:
            results.record_fail("emit_snapshot()", "broadcast not called")
    except Exception as e:
        results.record_fail("emit_snapshot()", str(e))
        import traceback
        traceback.print_exc()

    # Test: Health alert generation (if status changed)
    print(f"\n--- Testing Health Alert Generation ---")
    if snapshot.overall_status in [HealthStatus.AMBER, HealthStatus.RED]:
        try:
            alert = await monitor.generate_alert(test_graph_id, snapshot)
            results.record_pass("generate_alert() executed")

            print(f"\n  Alert Severity: {alert.severity}")
            print(f"  Flagged Metrics: {len(alert.flagged_metrics)}")
            if alert.procedures:
                print(f"  Recommended Procedures: {len(alert.procedures)}")
                for proc in alert.procedures:
                    print(f"    - {proc.procedure} ({proc.severity})")

        except Exception as e:
            results.record_fail("generate_alert()", str(e))
            import traceback
            traceback.print_exc()
    else:
        print(f"  Skipping alert test (status is GREEN)")

    # Test: History storage
    print(f"\n--- Testing History Storage ---")
    try:
        await monitor.history_store.save_snapshot(test_graph_id, snapshot)
        results.record_pass("save_snapshot() executed")

        # Check history retrieval
        percentiles = await monitor.history_store.get_percentiles(test_graph_id, 'density')
        if percentiles:
            results.record_pass("get_percentiles() returned data")
            print(f"  Density percentiles: q10={percentiles.get('q10', 0):.4f}, q90={percentiles.get('q90', 0):.4f}")
        else:
            print(f"  Note: No historical data yet (expected on first run)")
    except Exception as e:
        results.record_fail("History storage", str(e))

    return results.summary()


if __name__ == "__main__":
    print("="*60)
    print("GraphHealthMonitor Test Suite")
    print("="*60)

    success = asyncio.run(test_graph_health_monitor())
    sys.exit(0 if success else 1)
