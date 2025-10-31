#!/usr/bin/env python3
"""
tool.semgrep — publishes tool.offer on startup,
consumes tool.request.semgrep envelopes from the bus,
runs semgrep + complexity_scan, emits:
  - tool.result.semgrep (raw artifacts)
  - membrane.inject (scope: organizational, source_type: code_quality) for top suspects
"""

import asyncio, json, os, websockets, subprocess, tempfile, pathlib, time, uuid

BUS_URL = os.getenv("MEMBRANE_BUS", "ws://localhost:8000/ws")
RULES = os.getenv("SEMGREP_RULES", "semgrep_rules/godfile-suite.yml")

def now_ms(): return int(time.time()*1000)

async def bus():
    return await websockets.connect(BUS_URL, ping_interval=20)

async def publish(ws, event_type, event_spec, payload):
    full_envelope = {
        "type": event_type,
        "id": f"evt_{uuid.uuid4()}",
        "ts": now_ms(),
        "spec": event_spec,
        "provenance": {
            "actor": "tool.semgrep",
            "origin": "external",
            "chain_depth": 0
        },
        "payload": payload
    }
    await ws.send(json.dumps(full_envelope))

async def run_cmd(*cmd):
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)

async def run_semgrep(paths):
    args = ["semgrep", "--json", "--config", RULES, *paths]
    out = await run_cmd(*args)
    return json.loads(out)

async def run_complexity():
    out = await run_cmd("python3", "tools/quality/complexity_scan.py")
    return json.loads(out)

def mk_stimulus(file, risk, extras):
    return {
      "stimulus_id": str(uuid.uuid4()),
      "timestamp_ms": now_ms(),
      "scope": "organizational",
      "source_type": "code_quality",
      "actor": "tool.semgrep",
      "content": f"God-file candidate: {file}",
      "metadata": {
        "severity": "warn" if risk < 3.0 else "error",
        "file_path": file,
        "risk_score": risk,
        **extras,
        "origin": "external",
        "origin_chain_depth": 0,
        "rate_limit_bucket": "code_quality:godfile",
      },
      "focality_hint": "focal",
      "interrupt": False
    }

async def main():
    ws = await bus()
    # 1) Offer
    await publish(ws, "tool.offer@1.0", "tool.offer@1.0", {
      "name": "semgrep",
      "version": "0.1",
      "capabilities": ["maintainability","smells","adapter-leaks"]
    })

    # 2) Listen for tool.request.semgrep
    async for msg in ws:
        evt = json.loads(msg)
        if evt.get("topic") != "tool.request.semgrep":
            continue

        req = evt["payload"]
        paths = req.get("paths") or ["."]
        run_id = str(uuid.uuid4())

        # Run scanners
        semgrep_json = await run_semgrep(paths)
        complexity_json = await run_complexity()

        # Emit tool.result
        await publish(ws, "tool.result.semgrep@1.0", "tool.result@1.0", {
          "run_id": run_id,
          "paths": paths,
          "semgrep": semgrep_json,
          "complexity": complexity_json
        })

        # Emit org-scoped stimuli for top N (Q≥0.90 by risk_score)
        results = complexity_json["results"]
        if results:
            # compute 90th percentile in python for emergent gate
            scores = [r["risk_score"] for r in results]
            q90 = sorted(scores)[int(0.9*(len(scores)-1))]
            top = [r for r in results if r["risk_score"] >= q90][:10]
            for r in top:
                stim = mk_stimulus(
                    r["file"], r["risk_score"],
                    {"loc": r["loc"], "cc_max": r["cc_max"], "mi": r["mi"],
                     "churn_90d": r["churn90"], "fan_in": r["fanin"],
                     "suite": "GODFILE-1.0"}
                )
                await publish(ws, "membrane.inject@1.0", "stimulus@1.0", stim)

if __name__ == "__main__":
    asyncio.run(main())
