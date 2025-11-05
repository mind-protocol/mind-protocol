#!/bin/bash
# Deploy graph data import to Render production
# This script provides instructions for importing data to production

set -e

echo "=========================================="
echo "Mind Protocol - Deploy Data to Production"
echo "=========================================="
echo ""

EXPORT_FILE="tools/mindprotocol_graph_export.json.gz"
if [ ! -f "$EXPORT_FILE" ]; then
    echo "❌ Export file not found: $EXPORT_FILE"
    exit 1
fi

FILE_SIZE=$(du -h "$EXPORT_FILE" | cut -f1)
echo "📦 Export file: $EXPORT_FILE ($FILE_SIZE)"
echo ""

echo "MANUAL IMPORT STEPS (Render Dashboard)"
echo "=========================================="
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Select: mind-protocol-backend service"
echo "3. Click: 'Shell' tab"
echo "4. In local terminal, prepare upload:"
echo ""
echo "   # Compress may already be done"
echo "   ls -lh $EXPORT_FILE"
echo ""
echo "5. Upload via Render shell interface or use render-cli:"
echo ""
echo "   render shell mind-protocol-backend"
echo "   # Then drag-and-drop file to upload"
echo ""
echo "6. In Render shell, run:"
echo ""
echo "   python3 tools/import_from_json.py /tmp/mindprotocol_graph_export.json.gz"
echo ""
echo "7. Wait for 'Import Complete!' message"
echo "8. Restart service to load new data:"
echo ""
echo "   # Via dashboard: Services > mind-protocol-backend > Manual Deploy > Deploy"
echo ""
echo "9. Check dashboard after 2-3 minutes:"
echo "   https://www.mindprotocol.ai/consciousness"
echo ""

