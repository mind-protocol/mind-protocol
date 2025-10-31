"""
Lint Adapters - Membrane-Native Code Quality Enforcement

Wraps linting tools as membrane adapters that emit structured events.

Available adapters:
  - adapter_lint_python: Python linter (mp-lint R-100/200/300/400)
  - (future) adapter_lint_eslint: Frontend linter
  - (future) adapter_secretscan: Secrets detector
  - (future) adapter_depgraph: Dependency checker

Author: Felix "Core Consciousness Engineer"
Created: 2025-10-31
"""

from orchestration.adapters.lint.adapter_lint_python import PythonLintAdapter

__all__ = ['PythonLintAdapter']
