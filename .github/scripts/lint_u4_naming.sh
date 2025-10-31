#!/usr/bin/env bash
# U4 Naming Lint - CI Integration Script
#
# Runs U4 naming convention linter on protocol graph
# Exits with non-zero if violations found
#
# Usage:
#   .github/scripts/lint_u4_naming.sh [--graph protocol]

set -e

GRAPH=${1:-protocol}

echo "🔍 Running U4 naming lint on graph: $GRAPH"
echo

# Run linter
python3 tools/protocol/lint_u4_naming.py --graph "$GRAPH"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo
    echo "✅ U4 naming conventions: PASS"
else
    echo
    echo "❌ U4 naming conventions: FAIL"
    echo "   Fix violations before merging"
fi

exit $EXIT_CODE
