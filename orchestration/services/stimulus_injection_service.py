"""
Stimulus Injection Service - FastAPI server for Phase-A autonomy infrastructure

Provides:
- Health endpoint for guardian monitoring
- Heartbeat file for dashboard System Status
- /inject endpoint for stimulus processing (writes to JSONL queue)

Created: 2025-10-24 by Victor "The Resurrector"
Updated: 2025-10-25 by Atlas - P0.1 JSONL queue integration
Purpose: Queue stimuli for conversation_watcher processing
"""

from fastapi import FastAPI, Body
import uvicorn, time, os, json, threading
from pathlib import Path

APP_NAME = "stimulus_injection"
HEARTBEAT = f".heartbeats/{APP_NAME}.heartbeat"
os.makedirs(".heartbeats", exist_ok=True)

# JSONL queue for stimulus processing
QUEUE = Path(".stimuli/queue.jsonl")
QUEUE.parent.mkdir(exist_ok=True)

app = FastAPI(title="Stimulus Injection", version="1.0")

def heartbeat_loop():
    while True:
        try:
            with open(HEARTBEAT, "w") as f:
                f.write(str(int(time.time())))
        except Exception:
            pass
        time.sleep(5)

@app.on_event("startup")
def _start_hb():
    threading.Thread(target=heartbeat_loop, daemon=True).start()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/inject")
def inject(stimulus: dict = Body(...)):
    """
    Queue a stimulus for processing by conversation_watcher.
    Writes to .stimuli/queue.jsonl with correlation ID for tracing.
    """
    # Generate stimulus envelope with correlation ID
    stim = {
        "stimulus_id": stimulus.get("id") or f"stim_{int(time.time()*1000)}",
        "timestamp_ms": int(time.time()*1000),
        "citizen_id": stimulus.get("citizen_id", "felix"),
        "text": (stimulus.get("text") or "").strip(),
        "severity": float(stimulus.get("severity", 0.3)),
        "origin": stimulus.get("origin", "external")
    }

    # Append to JSONL queue (single writer, safe)
    with QUEUE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(stim) + "\n")

    return {"status": "injected", "stimulus_id": stim["stimulus_id"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
