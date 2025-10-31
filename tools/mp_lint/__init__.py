"""
Membrane Linter (mp_lint) - L4 Protocol Law Enforcement

Validates code, schemas, and graph data against L4 registry rules.

The linter ensures:
1. Schema coherence: type_name matches labels
2. Universality: U3/U4 types respect level bounds
3. Registry rules: Active schemas map to topics, require signatures
4. No drift: Code schemas match L4 registry

Author: Ada "Bridgekeeper"
Date: 2025-10-31
"""

__version__ = "0.1.0"
