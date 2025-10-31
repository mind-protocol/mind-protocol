usage-scan:
	mkdir -p .artifacts
	coverage run -m pytest -q || true
	coverage json -o .artifacts/coverage.json || true
	python tools/quality/complexity_scan.py > .artifacts/complexity.json || true
	semgrep --config semgrep_rules/godfile-suite.yml --json > .artifacts/semgrep.json || true
	python tools/usage/import_graph.py > .artifacts/import_graph_output.json || true
	git log --since="180 days ago" --name-only --pretty=format: | rg '\.py$$' | sort | uniq -c | sort -nr > .artifacts/churn_180d.txt || true
	python tools/usage/triage.py

quality-gates:
	xenon . --max-average B --max-modules B --max-absolute C

health-report:
	python scripts/render_health_report.py

lint-mp:
	python scripts/validate_envelopes.py .artifacts/envelopes/
