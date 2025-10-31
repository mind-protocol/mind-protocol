### Code Quality Tools

This directory contains scripts and configurations for static code analysis and complexity measurement.

- `complexity_scan.py`: Runs `radon` and `xenon` to calculate various code complexity metrics (LOC, Cyclomatic Complexity, Maintainability Index, Churn, Fan-in) and computes a relative risk score for Python files in the repository.
- `semgrep_rules/godfile-suite.yml`: Semgrep rules designed to identify 'God-File' characteristics, adapter leaks, long methods, mega-parameters, and wildcard imports in Python code.

To run `complexity_scan.py` locally:
```bash
python complexity_scan.py
```

To run Semgrep locally with the custom rules:
```bash
semgrep --config semgrep_rules/godfile-suite.yml .
```
