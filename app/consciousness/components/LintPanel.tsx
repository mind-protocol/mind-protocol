"use client";

import { useState, useEffect, useCallback } from "react";

// Event data models from spec
interface Finding {
  policy: string;
  rule: string;
  severity: "low" | "medium" | "high" | "critical";
  file: string;
  span: { start_line: number; end_line: number };
  message: string;
  suggestion?: string;
  evidence?: string;
}

interface LintFindings {
  change_id: string;
  findings: Finding[];
}

interface ReviewVerdict {
  change_id: string;
  result: "pass" | "soft_fail" | "hard_fail";
  scores: Record<string, number>;
  required: { override: boolean; fields: string[] };
}

export default function LintPanel() {
  const [findings, setFindings] = useState<Map<string, Finding[]>>(new Map());
  const [verdict, setVerdict] = useState<ReviewVerdict | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  // Connect to membrane WebSocket
  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/api/ws';
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log("[LintPanel] WebSocket connected");
      setConnected(true);

      // Subscribe to lint and review events (following useGraphStream pattern)
      socket.send(JSON.stringify({
        type: "subscribe@1.0",
        topics: [
          "lint.findings.emit",
          "review.verdict",
          "failure.emit"  // Also listen for failure events
        ]
      }));
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === "lint.findings.emit") {
          const data = msg.payload as LintFindings;
          console.log("[LintPanel] Lint findings received:", data);

          // Group findings by file
          const byFile = new Map<string, Finding[]>();
          data.findings.forEach(finding => {
            const existing = byFile.get(finding.file) || [];
            byFile.set(finding.file, [...existing, finding]);
          });

          setFindings(byFile);
        } else if (msg.type === "review.verdict") {
          const data = msg.payload as ReviewVerdict;
          console.log("[LintPanel] Review verdict received:", data);
          setVerdict(data);
        }
      } catch (err) {
        console.error("[LintPanel] Error parsing message:", err);
      }
    };

    socket.onerror = (error) => {
      console.error("[LintPanel] WebSocket error:", error);
      setConnected(false);
    };

    socket.onclose = () => {
      console.log("[LintPanel] WebSocket closed");
      setConnected(false);
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, []);

  const getSeverityColor = (severity: Finding["severity"]) => {
    switch (severity) {
      case "critical": return "bg-red-600 text-white";
      case "high": return "bg-orange-500 text-white";
      case "medium": return "bg-yellow-500 text-black";
      case "low": return "bg-blue-500 text-white";
      default: return "bg-gray-500 text-white";
    }
  };

  const getVerdictColor = (result: ReviewVerdict["result"]) => {
    switch (result) {
      case "pass": return "bg-green-600 text-white";
      case "soft_fail": return "bg-yellow-600 text-white";
      case "hard_fail": return "bg-red-600 text-white";
      default: return "bg-gray-600 text-white";
    }
  };

  const totalFindings = Array.from(findings.values()).reduce((sum, arr) => sum + arr.length, 0);

  return (
    <div
      className="fixed bottom-4 right-4 z-50 consciousness-panel"
      style={{
        width: isExpanded ? "600px" : "280px",
        maxHeight: "600px",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between p-3 border-b border-teal-500/30 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-teal-400">Lint Review</span>
          <span
            className={`w-2 h-2 rounded-full ${connected ? "bg-green-400" : "bg-red-400"}`}
            title={connected ? "Connected" : "Disconnected"}
          />
          {totalFindings > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-orange-500/20 text-orange-400 text-xs font-mono">
              {totalFindings}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {verdict && (
            <span className={`px-3 py-1 rounded text-xs font-bold uppercase ${getVerdictColor(verdict.result)}`}>
              {verdict.result.replace("_", " ")}
            </span>
          )}
          <button className="text-teal-400 hover:text-teal-300 text-xl">
            {isExpanded ? "−" : "+"}
          </button>
        </div>
      </div>

      {/* Body */}
      {isExpanded && (
        <div className="overflow-y-auto custom-scrollbar" style={{ maxHeight: "540px" }}>
          {totalFindings === 0 ? (
            <div className="p-6 text-center text-gray-400">
              <div className="text-4xl mb-2">✓</div>
              <div className="text-sm">No lint findings</div>
              {verdict?.result === "pass" && (
                <div className="text-xs text-green-400 mt-2">All checks passed</div>
              )}
            </div>
          ) : (
            <div className="p-3 space-y-3">
              {Array.from(findings.entries()).map(([file, fileFindings]) => (
                <div key={file} className="border border-teal-500/20 rounded bg-black/20 overflow-hidden">
                  {/* File header */}
                  <div className="px-3 py-2 bg-teal-500/10 border-b border-teal-500/20">
                    <div className="font-mono text-xs text-teal-300 truncate" title={file}>
                      {file}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {fileFindings.length} issue{fileFindings.length > 1 ? "s" : ""}
                    </div>
                  </div>

                  {/* Findings for this file */}
                  <div className="divide-y divide-teal-500/10">
                    {fileFindings.map((finding, idx) => (
                      <div key={idx} className="p-3 hover:bg-teal-500/5">
                        <div className="flex items-start gap-2 mb-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-bold ${getSeverityColor(finding.severity)}`}>
                            {finding.severity.toUpperCase()}
                          </span>
                          <span className="px-2 py-0.5 rounded bg-gray-700 text-gray-200 text-xs font-mono">
                            {finding.rule}
                          </span>
                          <span className="text-xs text-gray-400 font-mono">
                            L{finding.span.start_line}
                            {finding.span.end_line !== finding.span.start_line && `–${finding.span.end_line}`}
                          </span>
                        </div>

                        <div className="text-sm text-gray-200 mb-2">{finding.message}</div>

                        {finding.suggestion && (
                          <div className="text-xs text-teal-400 bg-teal-500/10 px-2 py-1 rounded border border-teal-500/20">
                            💡 {finding.suggestion}
                          </div>
                        )}

                        {finding.evidence && (
                          <details className="mt-2">
                            <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-300">
                              Show evidence
                            </summary>
                            <pre className="text-xs text-gray-300 bg-black/40 p-2 rounded mt-1 overflow-x-auto">
                              {finding.evidence}
                            </pre>
                          </details>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Verdict scores */}
          {verdict && Object.keys(verdict.scores).length > 0 && (
            <div className="p-3 border-t border-teal-500/30 bg-black/20">
              <div className="text-xs text-gray-400 mb-2">Policy Scores:</div>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(verdict.scores).map(([policy, score]) => (
                  <div key={policy} className="flex justify-between text-xs">
                    <span className="text-gray-300">{policy.replace(/_/g, " ")}</span>
                    <span className="font-mono text-orange-400">{score}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
