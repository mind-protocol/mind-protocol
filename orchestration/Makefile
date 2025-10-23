# Mind Protocol Orchestration Layer Makefile
# Provides convenient commands to run services individually

.PHONY: help run-ws run-api run-conv-watcher run-code-watcher run-n2-watcher run-viz-health run-heartbeat run-learning-hb run-branching test clean

help:
	@echo "Mind Protocol Orchestration Services"
	@echo ""
	@echo "24/7 Services:"
	@echo "  make run-ws              - Start WebSocket server (ws://localhost:8000)"
	@echo "  make run-api             - Start Control API (http://localhost:8788)"
	@echo "  make run-conv-watcher    - Start conversation watcher"
	@echo "  make run-code-watcher    - Start code substrate watcher"
	@echo "  make run-n2-watcher      - Start N2 activation monitor"
	@echo "  make run-viz-health      - Start visualization health monitor"
	@echo "  make run-heartbeat       - Start heartbeat writer"
	@echo "  make run-learning-hb     - Start learning heartbeat"
	@echo "  make run-branching       - Start branching ratio tracker"
	@echo ""
	@echo "Development:"
	@echo "  make test                - Run tests"
	@echo "  make clean               - Clean pycache"
	@echo ""
	@echo "Note: Guardian manages all processes. Use these for individual testing."

# === 24/7 Services ===

run-ws:
	python -m orchestration.services.websocket.main

run-api:
	python -m orchestration.services.api.main

run-conv-watcher:
	python orchestration/services/watchers/conversation_watcher.py

run-code-watcher:
	python orchestration/services/watchers/code_substrate_watcher.py

run-n2-watcher:
	python orchestration/services/watchers/n2_activation_monitor.py

run-viz-health:
	python orchestration/services/telemetry/visualization_health.py

run-heartbeat:
	python orchestration/services/telemetry/heartbeat_writer.py

run-learning-hb:
	python orchestration/services/learning/learning_heartbeat.py

run-branching:
	python orchestration/services/learning/branching_ratio_tracker.py

# === Development ===

test:
	pytest orchestration/tests/ -v

test-unit:
	pytest orchestration/tests/unit/ -v

test-integration:
	pytest orchestration/tests/integration/ -v

clean:
	find orchestration -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find orchestration -type f -name "*.pyc" -delete 2>/dev/null || true

# === Docker (future) ===

docker-build:
	docker build -t mind-protocol-orchestration .

docker-run:
	docker-compose up -d
