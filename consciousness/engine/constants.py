"""Constants for consciousness engine domain."""

# Energy constants
DEFAULT_MAX_ENERGY = 100.0
DEFAULT_MIN_ENERGY = 0.0
DEFAULT_ACTIVATION_THRESHOLD = 0.5
HIGH_ENERGY_THRESHOLD = 0.85

# Tick constants
DEFAULT_TICK_INTERVAL_MS = 100.0

# Graph traversal constants
DEFAULT_MAX_DISTANCE = 3

# Event type constants
TELEMETRY_EMIT_TYPE = "telemetry.emit"
GRAPH_UPSERT_TYPE = "graph.upsert"
ENGINE_TICK_EVENT = "engine.tick"
ENGINE_ALERT_HIGH_ENERGY_EVENT = "engine.alert.high_energy"
ENGINE_FRAME_COMPLETE_EVENT = "engine.frame.complete"
