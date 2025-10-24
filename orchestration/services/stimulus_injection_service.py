"""
Stimulus Injection Service - FastAPI server for Phase-A autonomy infrastructure

Minimal service stub for Phase 0 unblock. Provides:
- Health endpoint for guardian monitoring
- Heartbeat file for dashboard System Status
- /inject endpoint for stimulus processing (stub)

Created: 2025-10-24 by Victor "The Resurrector"
Purpose: Unblock Phase-A dashboard stabilization
"""

from fastapi import FastAPI, Body
import uvicorn, time, os, json, threading

APP_NAME = "stimulus_injection"
HEARTBEAT = f".heartbeats/{APP_NAME}.heartbeat"
os.makedirs(".heartbeats", exist_ok=True)

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
    # Minimal validation; Phase-A just needs a 200 and a stub response
    return {"status": "injected", "stimulus_id": stimulus.get("stimulus_id"), "echo": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
