"use client";

import { useGraphStream } from "../hooks/useGraphStream";

export default function GraphDebugBadge() {
  const { graphs, currentGraphId, connected, error } = useGraphStream();

  const currentGraph = currentGraphId ? graphs.get(currentGraphId) : null;
  const nodeCount = currentGraph?.nodes instanceof Map
    ? currentGraph.nodes.size
    : Object.keys(currentGraph?.nodes || {}).length;
  const linkCount = currentGraph?.links instanceof Map
    ? currentGraph.links.size
    : Object.keys(currentGraph?.links || {}).length;

  return (
    <div
      style={{
        position: "fixed",
        top: 16,
        right: 16,
        background: "rgba(0, 0, 0, 0.85)",
        color: "#fff",
        padding: "12px 16px",
        borderRadius: 8,
        fontFamily: "monospace",
        fontSize: 12,
        zIndex: 9999,
        border: "1px solid rgba(255, 255, 255, 0.2)",
        backdropFilter: "blur(10px)",
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: 8, color: "#4EA1FF" }}>
        Graph Debug
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "auto auto", gap: "4px 12px" }}>
        <span style={{ color: "#888" }}>Status:</span>
        <span style={{ color: connected ? "#4ade80" : "#ef4444" }}>
          {connected ? "Connected" : "Disconnected"}
        </span>

        <span style={{ color: "#888" }}>Graph:</span>
        <span>{currentGraphId || "none"}</span>

        <span style={{ color: "#888" }}>Nodes:</span>
        <span style={{ color: nodeCount > 0 ? "#4ade80" : "#ef4444" }}>{nodeCount}</span>

        <span style={{ color: "#888" }}>Links:</span>
        <span style={{ color: linkCount > 0 ? "#4ade80" : "#ef4444" }}>{linkCount}</span>

        {error && (
          <>
            <span style={{ color: "#888" }}>Error:</span>
            <span style={{ color: "#ef4444" }}>{error}</span>
          </>
        )}
      </div>
    </div>
  );
}
