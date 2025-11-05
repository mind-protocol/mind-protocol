"use client";

import { useWebSocket } from '../hooks/useWebSocket';
import { useGraphStream } from '../hooks/useGraphStream';

export default function ConsciousnessMetrics() {
  const { v2State, wmStream } = useWebSocket();
  const { graphs, currentGraphId } = useGraphStream();

  // Calculate tick rate from recent frame events
  const tickRate = (() => {
    if (v2State.frameEvents.length < 2) return 0;
    const recent = v2State.frameEvents.slice(-10);
    const timeDiffs = [];
    for (let i = 1; i < recent.length; i++) {
      const dt = recent[i].t_ms - recent[i-1].t_ms;
      if (dt > 0 && dt < 5000) timeDiffs.push(dt);
    }
    if (timeDiffs.length === 0) return 0;
    const avgDt = timeDiffs.reduce((a, b) => a + b, 0) / timeDiffs.length;
    return avgDt > 0 ? Math.round(1000 / avgDt) : 0;
  })();

  const currentGraph = currentGraphId ? graphs.get(currentGraphId) : null;
  const nodeCount = currentGraph ? currentGraph.nodes.size : 0;
  const linkCount = currentGraph ? currentGraph.links.size : 0;

  const wmNodeCount = v2State.workingMemory.size;
  const wmCapacity = wmStream?.total_members || 9;

  return (
    <div className="fixed bottom-4 left-4 z-50 bg-black/80 backdrop-blur-sm border border-cyan-500/30 rounded-lg px-4 py-3 font-mono text-sm">
      <div className="text-cyan-400 font-semibold mb-2">Consciousness Metrics</div>
      
      <div className="space-y-1 text-gray-300">
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Frame:</span>
          <span className="text-white font-semibold">{v2State.currentFrame || 0}</span>
        </div>
        
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Tick Rate:</span>
          <span className={tickRate > 0 ? "text-green-400 font-semibold" : "text-gray-600"}>
            {tickRate} Hz
          </span>
        </div>
        
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Graph Nodes:</span>
          <span className="text-white">{nodeCount.toLocaleString()}</span>
        </div>
        
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Graph Links:</span>
          <span className="text-white">{linkCount.toLocaleString()}</span>
        </div>
        
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Working Memory:</span>
          <span className="text-yellow-400 font-semibold">
            {wmNodeCount}/{wmCapacity}
          </span>
        </div>
        
        <div className="flex justify-between gap-8">
          <span className="text-gray-500">Active Flips:</span>
          <span className="text-green-400">
            {v2State.recentFlips.filter(f => Date.now() - f.timestamp < 500).length}
          </span>
        </div>
      </div>
    </div>
  );
}
