"""Autonomy Orchestrator Service - FastAPI server for Phase-A autonomy infrastructure."""

import os

if not os.environ.get("ALLOW_QUARANTINED_MODULES"):
    raise ImportError("Module quarantined pending deletion")

from fastapi import FastAPI, Body
import uvicorn, time, threading

APP_NAME = "autonomy_orchestrator"
HEARTBEAT = f".heartbeats/{APP_NAME}.heartbeat"
os.makedirs(".heartbeats", exist_ok=True)

app = FastAPI(title="Autonomy Orchestrator", version="1.0")

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

@app.post("/intent")
def intent(stimulus: dict = Body(...)):
    # Phase-A: turn stimulus into a dummy IntentCard
    citizen = stimulus.get("metadata", {}).get("citizen_hint", "atlas")
    return {"intent_type": "intent.fix_incident", "assignee": citizen, "priority": 0.5}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)
