#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Mind Protocol — E2E Space Encryption test runner
#
# Runs the full lifecycle: private Space creation, encrypted Moments,
# access grant/revoke, and cross-language JS<->Python round-trip.
#
# Usage:
#   ./tests/crypto/run_e2e_encryption.sh          # standalone runner
#   ./tests/crypto/run_e2e_encryption.sh --pytest  # via pytest
#
# Requires: FalkorDB on localhost:6379, Python 3.10+, Node.js 18+
#
# Co-Authored-By: Tomaso Nervo (@nervo) <nervo@mindprotocol.ai>
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "=========================================="
echo "E2E Space Encryption Tests"
echo "=========================================="
echo "Repo:  $REPO_ROOT"
echo "Graph: test_e2e_encryption"
echo ""

# Check dependencies
python3 -c "from falkordb import FalkorDB" 2>/dev/null || {
    echo "SKIP: FalkorDB Python package not installed (pip install falkordb)"
    exit 0
}

python3 -c "from python.crypto import generate_space_key" 2>/dev/null || {
    echo "SKIP: mind-protocol crypto library not importable"
    exit 1
}

# Check FalkorDB connectivity
python3 -c "
from falkordb import FalkorDB
try:
    db = FalkorDB(host='localhost', port=6379)
    db.select_graph('_probe').query('RETURN 1')
except Exception as e:
    print(f'SKIP: FalkorDB not reachable: {e}')
    exit(0)
" || exit 0

if [[ "${1:-}" == "--pytest" ]]; then
    echo "Running via pytest..."
    python3 -m pytest tests/crypto/test_e2e_space_encryption.py -v --tb=short
else
    echo "Running standalone..."
    python3 tests/crypto/test_e2e_space_encryption.py
fi
