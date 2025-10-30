#!/usr/bin/env python3
"""
Membrane Stimuli SDK - Usage Example

Demonstrates pure membrane emission for consciousness substrate influence.

Features demonstrated:
- Level-invariant emission (scope, not citizen_id)
- Topology-agnostic (no routing decisions)
- Non-blocking (never blocks main work)
- Client-side quality (fingerprinting, redaction)
- Typed emitters for different stimulus types

Usage:
    python orchestration/examples/membrane_sdk_example.py

Created: 2025-10-29 by Ada (Architect)
Spec: membrane_systems_map.md (Component D)
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestration.libs.stimuli import (
    emit_script_error,
    emit_metric,
    emit_ui_action,
    emit_tool_result,
    MembraneEmitter,
    get_metrics,
)
from orchestration.schemas.membrane_envelopes import (
    Scope,
    StimulusFeatures,
    OriginType,
)


def example_script_error():
    """Example 1: Script error emission with automatic stack fingerprinting."""
    print("[Example 1] Script Error Stimulus")
    print("-" * 60)

    try:
        # Simulate error
        data = {"name": "test"}
        missing_field = data["missing_key"]  # KeyError
    except KeyError:
        emit_script_error(
            source="script:membrane_sdk_example",
            error_message="Failed to process data - missing required key",
            scope=Scope.ORGANIZATIONAL,  # L2 awareness
            exc_info=sys.exc_info(),
            metadata={
                "script_path": __file__,
                "operation": "data_processing",
            }
        )
        print("✓ Emitted script error stimulus (L2)")
        print("  - Automatic stack fingerprinting")
        print("  - Secret redaction")
        print("  - Dedupe key computation")

    print()


def example_metric():
    """Example 2: Metric emission for operational telemetry."""
    print("[Example 2] Metric Stimulus")
    print("-" * 60)

    emit_metric(
        source="script:membrane_sdk_example",
        metric_name="example_success_rate",
        value=0.95,
        scope=Scope.ORGANIZATIONAL,  # L2 metrics
        tags={
            "environment": "development",
            "component": "membrane_sdk",
        }
    )
    print("✓ Emitted metric stimulus (L2)")
    print("  - Metric: example_success_rate = 0.95")
    print("  - Tags: environment=development, component=membrane_sdk")
    print()


def example_ui_action():
    """Example 3: UI action emission for user interaction tracking."""
    print("[Example 3] UI Action Stimulus")
    print("-" * 60)

    emit_ui_action(
        action_type="select_nodes",
        description="User selected nodes N7, N23 for focused attention",
        scope=Scope.PERSONAL,  # L1 citizen
        citizen_id="ada",  # Optional provenance
        metadata={
            "selected_nodes": ["N7", "N23"],
            "selection_mode": "manual",
            "timestamp": time.time(),
        }
    )
    print("✓ Emitted UI action stimulus (L1)")
    print("  - Action: select_nodes")
    print("  - Selected: [N7, N23]")
    print()


def example_tool_result():
    """Example 4: Tool result emission for autonomous tool usage."""
    print("[Example 4] Tool Result Stimulus")
    print("-" * 60)

    emit_tool_result(
        tool_id="code_search",
        request_id="req_12345",
        success=True,
        result={
            "matches": 5,
            "files": ["stimuli.py", "membrane_envelopes.py"],
        },
        scope=Scope.PERSONAL,  # L1 citizen
        citizen_id="ada",
        execution_time_ms=125.5,
        provenance={
            "query": "emit_script_error",
            "search_type": "semantic",
        }
    )
    print("✓ Emitted tool result stimulus (L1)")
    print("  - Tool: code_search")
    print("  - Success: True")
    print("  - Execution: 125.5ms")
    print()


def example_custom_emission():
    """Example 5: Custom emission using MembraneEmitter directly."""
    print("[Example 5] Custom Stimulus (Direct Emitter)")
    print("-" * 60)

    emitter = MembraneEmitter(source_id="custom:example_component")

    emitter.emit(
        scope=Scope.ORGANIZATIONAL,  # L2
        channel="custom.operational",
        content="Example system started successfully",
        features=StimulusFeatures(
            novelty=0.3,
            uncertainty=0.1,
            trust=0.95,
            urgency=0.2,
            valence=0.5,  # Positive
            scale=0.6,
            intensity=0.8,
        ),
        origin=OriginType.EXTERNAL,
        provenance={
            "component": "example_component",
            "version": "1.0.0",
            "startup_time_ms": 1250.5,
        },
    )
    print("✓ Emitted custom stimulus (L2)")
    print("  - Channel: custom.operational")
    print("  - Features: novelty=0.3, trust=0.95, urgency=0.2, valence=0.5")
    print()


def example_organizational_intent():
    """Example 6: Organizational intent (L2) - physics routes to citizens."""
    print("[Example 6] Organizational Intent (L2 → L1 via Physics)")
    print("-" * 60)

    emitter = MembraneEmitter(source_id="script:membrane_sdk_example")

    emitter.emit(
        scope=Scope.ORGANIZATIONAL,  # L2 organizational consciousness
        channel="org.intent",
        content="Run comprehensive system diagnostics",
        features=StimulusFeatures(
            novelty=0.5,
            uncertainty=0.3,
            trust=0.95,  # High trust - it's our script
            urgency=0.8,  # Urgent
            valence=0.3,  # Slightly positive (maintenance)
            scale=1.0,   # High scale (affects all citizens)
            intensity=1.0,
        ),
        origin=OriginType.EXTERNAL,
        provenance={
            "source": "script:membrane_sdk_example",
            "operation": "system_diagnostics",
        },
    )
    print("✓ Emitted organizational intent (L2)")
    print()
    print("What happens next:")
    print("  1. L2 engine integrates stimulus (organizational scope)")
    print("  2. L2 nodes activate if stimulus passes integrator gates")
    print("  3. L2 membrane evaluates downward transfer (fit × κ↓)")
    print("  4. L2 membrane emits per-citizen mission stimuli")
    print("  5. L1 engines (felix, atlas, iris, etc.) integrate missions")
    print("  6. L1 citizens activate relevant nodes organically")
    print()
    print("Who gets woken? Determined by:")
    print("  - Structural alignment: LIFTS_TO, CORRESPONDS_TO links (fit score)")
    print("  - Flux control: MEMBRANE_TO edges with learned κ")
    print("  - Integrator physics: mass, refractory, trust/utility EMAs")
    print()
    print("Result: Organic fan-out. No code branches. Pure substrate physics.")
    print()


def show_metrics():
    """Display SDK metrics."""
    print("=" * 60)
    print("Membrane SDK Metrics")
    print("=" * 60)

    metrics = get_metrics()
    print(f"  Dropped envelopes (queue full): {metrics['dropped_count']}")
    print(f"  Spooled to disk (bus offline): {metrics['spool_writes']}")
    print()

    if metrics['dropped_count'] > 0:
        print("⚠️  Warning: Queue overflowed. Consider:")
        print("   - Increase QUEUE_CAPACITY (current: 1000)")
        print("   - Increase BATCH_SIZE (current: 25)")
        print("   - Reduce emission rate")
        print()

    if metrics['spool_writes'] > 0:
        print("⚠️  Warning: WS bus was offline. Envelopes spooled to:")
        print("   /tmp/membrane-stimuli-spool/")
        print("   (Auto-flushed when bus returns)")
        print()


def main():
    """Run membrane SDK examples."""
    print("=" * 60)
    print("Membrane Stimuli SDK - Examples")
    print("=" * 60)
    print()
    print("Demonstrating pure membrane emission:")
    print("  - Level-invariant (scope, not citizen_id)")
    print("  - Topology-agnostic (no routing)")
    print("  - Non-blocking (queue + background thread)")
    print("  - Pure membrane (WS bus publish)")
    print()
    print("=" * 60)
    print()

    # Example 1: Script error
    example_script_error()
    time.sleep(0.3)  # Let background flusher process

    # Example 2: Metric
    example_metric()
    time.sleep(0.3)

    # Example 3: UI action
    example_ui_action()
    time.sleep(0.3)

    # Example 4: Tool result
    example_tool_result()
    time.sleep(0.3)

    # Example 5: Custom emission
    example_custom_emission()
    time.sleep(0.3)

    # Example 6: Organizational intent (demonstrates L2→L1 physics)
    example_organizational_intent()
    time.sleep(0.5)  # Extra time for final flush

    # Show metrics
    show_metrics()

    print("Example complete!")
    print()
    print("Next steps:")
    print("  1. Check membrane bus logs: WS server should show envelope arrivals")
    print("  2. Check engine logs: Engines should integrate stimuli")
    print("  3. Check telemetry: stimulus.processed, membrane.transfer events")
    print("  4. Query graphs: Verify nodes activated via physics")
    print()
    print("Key principle: Complexity lives in substrate physics (spec'd),")
    print("               not in SDK (simple emission).")
    print()


if __name__ == "__main__":
    main()
