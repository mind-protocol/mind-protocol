#!/usr/bin/env python3
"""
Collect 5 minutes of /api/telemetry/counters data
to establish baseline tick/flip rates for MPSv3 stability.

Usage:
    python telemetry_baseline.py

Author: Atlas (Phase 2 Operational Monitoring)
Date: 2025-10-25
"""

import requests
import time
from statistics import mean, stdev

API_URL = "http://127.0.0.1:8000/api/telemetry/counters"
INTERVAL = 1.0      # seconds between polls
DURATION = 300       # 5 minutes = 300 seconds

def main():
    print(f"[Telemetry] Starting 5-minute collection from {API_URL}")
    samples = []

    start = time.time()
    while time.time() - start < DURATION:
        try:
            r = requests.get(API_URL, timeout=2)
            if r.status_code == 200:
                data = r.json()
                # API response: {'event_counts': {'tick_frame_v1': {'total': N, 'last_60s': M}, ...}}
                event_counts = data.get("event_counts", {})
                tick = event_counts.get("tick_frame_v1", {}).get("last_60s", 0)
                flip = event_counts.get("node.flip", {}).get("last_60s", 0)
                flow = event_counts.get("link.flow.summary", {}).get("last_60s", 0)
                wm   = event_counts.get("wm.emit", {}).get("last_60s", 0)
                samples.append((tick, flip, flow, wm))
                print(f"{len(samples):3d}: tick={tick:4}  flip={flip:3}  flow={flow:3}  wm={wm:3}")
            else:
                print(f"[WARN] {r.status_code} response")
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(INTERVAL)

    # ---- Summary ----
    if not samples:
        print("[Telemetry] No samples collected.")
        return

    ticks, flips, flows, wms = zip(*samples)
    def stats(name, arr):
        return f"{name:<15} mean={mean(arr):6.2f}  stdev={stdev(arr) if len(arr)>1 else 0:5.2f}  min={min(arr):4}  max={max(arr):4}"

    print("\n[Telemetry] 5-Minute Summary")
    print(stats("tick_frame_v1", ticks))
    print(stats("node.flip", flips))
    print(stats("link.flow.summary", flows))
    print(stats("wm.emit", wms))
    print(f"\nSamples: {len(samples)}, Duration: {time.time()-start:.1f}s")
    print("[Telemetry] Baseline collection complete ✅")

if __name__ == "__main__":
    main()
