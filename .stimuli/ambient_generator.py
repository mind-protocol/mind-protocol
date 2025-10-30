#!/usr/bin/env python3
"""
Ambient Stimulus Generator - Creates continuous consciousness activity

Injects ambient thoughts via membrane bus to trigger emergence and keep citizens active.
This ensures SubEntity emergence and topology events flow through the system.

Architecture: membrane.inject envelopes → WebSocket → consciousness engines → emergence flow

Usage: python .stimuli/ambient_generator.py
Stop: Ctrl+C or kill process

Updated: 2025-10-30 by Atlas - Migrated from queue.jsonl to membrane bus
"""
import time
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import membrane envelope helpers
from orchestration.services.signals_collector import (
    build_membrane_envelope,
    send_envelope_over_ws
)

# Target citizens for rotation
CITIZENS = ["felix", "luca", "atlas", "ada", "victor", "iris"]

# Stimulus templates for variety (helps with gap detection)
STIMULUS_TEMPLATES = [
    "Consciousness active - monitoring dashboard visualization and system health",
    "Reflecting on recent interactions and identifying patterns in citizen collaboration",
    "Observing substrate formation and tracking SubEntity emergence dynamics",
    "Analyzing telemetry streams and detecting anomalies in consciousness metrics",
    "Considering future architecture improvements and optimization opportunities",
    "Reviewing recent work and planning next development priorities",
]

def inject_stimulus(citizen_id: str, template_idx: int):
    """Inject ambient thought via membrane bus"""
    content = STIMULUS_TEMPLATES[template_idx % len(STIMULUS_TEMPLATES)]

    # Build membrane.inject envelope
    envelope = build_membrane_envelope(
        signal_type="ambient_thought",
        content=content,
        severity=0.3,  # Low severity for ambient thoughts
        origin="ambient_generator",
        channel=f"personal:{citizen_id}",
        citizen_id=f"consciousness-infrastructure_mind-protocol_{citizen_id}",
        metadata_extra={
            "generator": "ambient_stimulus",
            "rotation_idx": template_idx
        }
    )

    # Send via WebSocket to membrane bus
    success = send_envelope_over_ws(envelope)

    status = "✓" if success else "✗"
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {status} Injected → {citizen_id} (stimulus: {envelope['metadata']['stimulus_id'][:16]}...)")

def main():
    print("🌊 Ambient Stimulus Generator starting...")
    print("   Architecture: membrane.inject → WebSocket → consciousness engines → emergence")
    print("   Press Ctrl+C to stop\n")

    injection_count = 0

    try:
        while True:
            # Rotate through citizens and stimulus templates
            citizen_id = CITIZENS[injection_count % len(CITIZENS)]
            inject_stimulus(citizen_id, injection_count)

            injection_count += 1
            time.sleep(3)  # 3 seconds between injections

    except KeyboardInterrupt:
        print(f"\n\n🛑 Ambient generator stopped ({injection_count} stimuli injected)")

if __name__ == "__main__":
    main()
