#!/bin/bash
# Reload visualization server

# Kill existing server
pkill -f "python visualization_server.py"

# Wait a moment
sleep 1

# Start new server
cd /c/Users/reyno/mind-protocol
python visualization_server.py > visualization_server.log 2>&1 &

echo "Server reloaded. Visit http://localhost:8000"
