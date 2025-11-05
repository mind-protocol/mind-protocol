#!/bin/bash
# Deploy graph import to Render production
#
# This script should be run FROM the Render shell environment
# where ECONOMY_REDIS_URL points to the internal FalkorDB service
#
# Usage (on Render):
#   bash tools/deploy_import_to_render.sh

set -e

echo "=================================================="
echo " Mind Protocol - Production Graph Import"
echo "=================================================="
echo ""

# Check environment
if [ -z "$ECONOMY_REDIS_URL" ]; then
    echo "❌ ECONOMY_REDIS_URL not set"
    echo "This script must run on Render with access to FalkorDB"
    exit 1
fi

echo "✅ ECONOMY_REDIS_URL detected"
echo ""

echo "🚀 Starting import..."
echo ""

# Run import (script handles .gz directly)
python3 tools/import_from_json.py tools/mindprotocol_graph_export.json.gz

echo ""
echo "=================================================="
echo " Import Complete!"
echo "=================================================="
echo ""
echo "Next: Restart the consciousness engines service to load data"
