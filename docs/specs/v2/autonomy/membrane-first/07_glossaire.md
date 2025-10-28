# Glossary

- **Membrane** – the strict interface between influence (`membrane.inject`) and observation (broadcast topics).  
- **StimulusEnvelope (`membrane.inject`)** – standardised envelope carrying scope, metadata, payload, signature; the only way to influence the system.  
- **Percept Frame (`percept.frame`)** – compressed subjective snapshot per subentity (valence, arousal, goal match, novelty, uncertainty, peripheral pressure, anchors).  
- **κ-learning** – adaptive adjustment of membrane permeability based on mission outcomes and telemetry.  
- **Lane / ACK Policy** – orchestrator flow-control construct: lanes group missions with capacity & acknowledgement requirements.  
- **Tool Mesh** – dynamic registry of tools; tools announce via `tool.offer`, requests travel as stimuli, results are broadcast.  
- **Emission Ledger** – membrane heuristic to prevent ping-pong exports by tracking recent cross-level emissions.  
- **Pareto / MAD Guard** – cross-level guardrails ensuring exports represent multi-axis improvements and catch outliers robustly.  
- **Sidecar** – client that signs and publishes stimuli, buffers offline, and replays once connected to the bus.  
- **Renderer** – automated publisher that turns mission outcomes & tool results into documentation (PRs, sites) referencing evidence hashes.
- **Integrator** – gateway component that enforces saturation, refractory windows, and maintains source trust scores before stimuli reach engines.  
- **Backpressure** – feedback signal (`ui.render.backpressure`) emitted by observers to request lighter percept output (reduced cadence / payload).  
- **Evidence Hash** – content-addressed URI (`local://sha256/...` or S3 CID) embedded in publications and commits to reference raw artefacts without storing them in git.  
- **Orchestrator** – L2 service that maps stimuli to intents/missions, manages lanes, and routes tool requests/results.  
- **Object Store** – externalised storage (mock folder in localhost) where binary artefacts, screenshots, and logs live; referenced by hash in events.
