@echo off
REM Start Mind Protocol Consciousness Visualization

echo Starting Mind Protocol Visualization Server...
echo.
echo Available graphs:
docker exec mind_protocol_falkordb redis-cli GRAPH.LIST
echo.
echo Starting server on http://localhost:8000
echo.
python visualization_server.py
