#!/usr/bin/env python3
"""
Ambient Stimulus Generator - Creates continuous consciousness activity for dashboard testing

Injects ambient thoughts every 3 seconds to keep citizens active.
This ensures node.flip and link.flow.summary emitters trigger (they're conditional on activity).

Usage: python .stimuli/ambient_generator.py
Stop: Ctrl+C or kill process
"""
import time
import json
from datetime import datetime, timezone
from pathlib import Path

# Target citizens for rotation
CITIZENS = ["felix", "luca", "atlas", "ada", "victor", "iris"]

def inject_stimulus(citizen_id: str):
    """Inject ambient thought to queue.jsonl"""
    stimulus = {
        "type": "ambient_thought",
        "content": f"Consciousness active - monitoring dashboard visualization",
        "citizen_id": citizen_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    queue_file = Path(__file__).parent / "queue.jsonl"
    with open(queue_file, "a") as f:
        f.write(json.dumps(stimulus) + "\n")
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Injected → {citizen_id}")

def main():
    print("🌊 Ambient Stimulus Generator starting...")
    print("   Creates continuous activity for dashboard visualization")
    print("   Press Ctrl+C to stop\n")
    
    citizen_idx = 0
    
    try:
        while True:
            # Rotate through citizens
            citizen_id = CITIZENS[citizen_idx % len(CITIZENS)]
            inject_stimulus(citizen_id)
            
            citizen_idx += 1
            time.sleep(3)  # 3 seconds between injections
            
    except KeyboardInterrupt:
        print("\n\n🛑 Ambient generator stopped")

if __name__ == "__main__":
    main()
