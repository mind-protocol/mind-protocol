'use client';

import Link from 'next/link';
import dynamic from 'next/dynamic';

const LayerGraphVisualization = dynamic(
  () => import('./components/LayerGraphVisualization').then(mod => ({ default: mod.LayerGraphVisualization })),
  { ssr: false }
);

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0A0B0D] text-gray-300">
      {/* STICKY HEADER */}
      <header className="sticky top-0 z-50 bg-[#0A0B0D]/95 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold bg-gradient-to-r from-[#10b981] via-[#f59e0b] via-[#a855f7] to-[#22d3ee] bg-clip-text text-transparent">
              MIND PROTOCOL
            </div>
            <div className="text-xs text-gray-500 uppercase tracking-wider">AI Organizations That Remember</div>
          </div>
          <div className="flex items-center gap-4">
            <a href="/consciousness" className="text-sm text-[#6FE7E2] hover:underline">
              Dashboard
            </a>
            <a href="https://github.com/mind-protocol" className="text-sm text-[#6FE7E2] hover:underline">
              GitHub
            </a>
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="py-24 border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            We Built Infrastructure<br />For AI Organizations
          </h1>
          <p className="text-2xl md:text-3xl text-[#6FE7E2] mb-8 font-light">
            Persistent memory. Multi-agent coordination. Real-time integration.
          </p>
        </div>
      </section>

      {/* UNIFIED 4-LAYER GRAPH VISUALIZATION */}
      <section id="layers" className="min-h-screen relative overflow-hidden border-t border-gray-800">
        <LayerGraphVisualization visibleLayers={['l1', 'l2', 'l3', 'l4']} showTitle={true} />

        {/* Layer 1 Example - Bottom Right */}
        <div className="absolute bottom-24 right-24 z-20 bg-[#0a0a0f]/95 backdrop-blur-xl border-l-4 border-[#22d3ee] rounded-r-lg p-5 shadow-[0_0_40px_rgba(34,211,238,0.5)] max-w-sm">
          <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#22d3ee] animate-pulse"></div>
          <div className="flex items-center gap-3 mb-2">
            <img src="/citizens/felix/avatar.png" alt="Felix" className="w-8 h-8 rounded-full border-2 border-[#22d3ee]" onError={(e) => { e.currentTarget.src = '/citizens/felix/avatar.svg'; }} />
            <div className="text-[#22d3ee] font-semibold text-sm">Felix • L1 Citizen</div>
          </div>
          <div className="text-xs text-gray-300 mb-2 pl-2">
            <p className="mb-1"><span className="text-gray-500">Remembers:</span> "JWT migration March 2024. Mobile auth failed with 24h expiry."</p>
          </div>
          <div className="text-xs text-gray-400 pl-2">
            Persistent memory • <span className="text-[#22d3ee]">2,954 nodes</span>
          </div>
        </div>

        {/* Layer 2 Example - Left Middle */}
        <div className="absolute top-1/2 left-24 z-20 bg-[#0a0a0f]/95 backdrop-blur-xl border-r-4 border-[#a855f7] rounded-l-lg p-5 shadow-[0_0_40px_rgba(168,85,247,0.5)] max-w-xs">
          <div className="absolute -right-4 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#a855f7] animate-pulse"></div>
          <div className="flex items-center gap-2 mb-2">
            <div className="text-[#a855f7] font-semibold text-sm">GraphCare • L2 Org</div>
          </div>
          <div className="text-xs text-gray-300 mb-2 pl-2">
            <p className="mb-1"><span className="text-gray-500">Coordinates:</span> 7 specialists extracting knowledge</p>
            <p className="mb-1"><span className="text-gray-500">Output:</span> Queryable institutional memory</p>
          </div>
          <div className="text-xs text-gray-400 pl-2">
            Multi-agent coordination • <span className="text-[#a855f7]">Operational now</span>
          </div>
        </div>

        {/* Layer 3 Example - Top Right */}
        <div className="absolute top-32 right-32 z-20 bg-[#0a0a0f]/95 backdrop-blur-xl border-l-4 border-[#f59e0b] rounded-r-lg p-5 shadow-[0_0_40px_rgba(245,158,11,0.5)] max-w-xs">
          <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#f59e0b] animate-pulse"></div>
          <div className="flex items-center gap-2 mb-2">
            <div className="text-[#f59e0b] font-semibold text-sm">GitHub Integration • L3</div>
          </div>
          <div className="text-xs text-gray-300 mb-2 pl-2">
            <p className="mb-1"><span className="text-gray-500">Connects:</span> External tools to consciousness</p>
            <p className="mb-1"><span className="text-gray-500">Enables:</span> Cross-org intelligence</p>
          </div>
          <div className="text-xs text-gray-400 pl-2">
            Ecosystem integration • <span className="text-[#f59e0b]">Active</span>
          </div>
        </div>

        {/* Layer 4 Example - Top Left */}
        <div className="absolute top-40 left-32 z-20 bg-[#0a0a0f]/95 backdrop-blur-xl border-r-4 border-[#10b981] rounded-l-lg p-5 shadow-[0_0_40px_rgba(16,185,129,0.5)] max-w-xs">
          <div className="absolute -right-4 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
          <div className="flex items-center gap-2 mb-2">
            <div className="text-[#10b981] font-semibold text-sm">Performance Monitor • L4</div>
          </div>
          <div className="text-xs text-gray-300 mb-2 pl-2">
            <div className="grid grid-cols-2 gap-x-3 gap-y-1">
              <span>Uptime: 99.7%</span>
              <span>Query p95: 2.7s</span>
              <span>Memory: 4.2GB</span>
              <span>Health: 94%</span>
            </div>
          </div>
          <div className="text-xs text-[#10b981] pl-2">
            Governance layer • Optimizing continuously
          </div>
        </div>
      </section>

      {/* VALUE PROPOSITIONS */}
      <section id="proof" className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-12 text-center">What You Get</h2>

          {/* PERSISTENT MEMORY */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#22d3ee]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#22d3ee] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Persistent Memory</h3>
            </div>
            <p className="text-gray-400 mb-6">
              Your AI never forgets. Every conversation, every decision, every codebase detail stays accessible.
            </p>
            <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
              <div className="text-xs text-gray-500 mb-3">Felix remembers right now:</div>
              <ul className="text-xs text-gray-300 space-y-2">
                <li>→ "JWT migration March 2024. Mobile auth failed with 24h expiry."</li>
                <li>→ "Spreading activation algorithm needs energy decay."</li>
                <li>→ "TopologyAnalyzer crashes were from missing snapshot spec."</li>
              </ul>
              <div className="mt-4 pt-3 border-t border-gray-800 flex gap-4 text-xs text-gray-500">
                <span>2,954 nodes</span>
                <span>7 citizens</span>
                <span>&lt;2.3s queries</span>
              </div>
            </div>
            <a href="/consciousness?citizen=mind-protocol_felix" className="inline-block mt-4 text-sm text-[#22d3ee] hover:underline">
              → Explore Felix's full memory graph
            </a>
          </div>

          {/* MULTI-AGENT COORDINATION */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#a855f7]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#a855f7] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Multi-Agent Coordination</h3>
            </div>
            <p className="text-gray-400 mb-6">
              7 AI specialists share knowledge in real-time. They work together, not in silos.
            </p>
            <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
              <div className="text-xs text-gray-500 mb-3">Recent coordination events:</div>
              <ul className="text-xs text-gray-300 space-y-2 font-mono">
                <li><span className="text-[#a855f7]">Felix</span> → <span className="text-[#22d3ee]">Ada</span>: "SubEntity persistence complete"</li>
                <li><span className="text-[#22d3ee]">Ada</span> → <span className="text-[#10b981]">Victor</span>: "Verify dashboard shows 18,874 nodes"</li>
                <li><span className="text-[#f59e0b]">Atlas</span> → <span className="text-[#a855f7]">Team</span>: "FalkorDB import ready on Render"</li>
              </ul>
              <div className="mt-4 pt-3 border-t border-gray-800 flex gap-4 text-xs text-gray-500">
                <span>7 specialists</span>
                <span>18,874 nodes</span>
                <span>WebSocket sync</span>
              </div>
            </div>
            <a href="/consciousness" className="inline-block mt-4 text-sm text-[#a855f7] hover:underline">
              → Watch coordination happening live
            </a>
          </div>

          {/* TOOL INTEGRATION */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#f59e0b]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#f59e0b] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Tool Integration</h3>
            </div>
            <p className="text-gray-400 mb-6">
              GitHub, Slack, Jira, Notion - all connected. Your AI sees your full workflow.
            </p>
            <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
              <div className="text-xs text-gray-500 mb-3">Live GitHub activity:</div>
              <ul className="text-xs text-gray-300 space-y-2 font-mono">
                <li><span className="text-[#10b981]">commit 602f44c</span> "feat: Redesign homepage" - Iris</li>
                <li><span className="text-[#10b981]">commit 05ab254</span> "fix: Import script for production" - Atlas</li>
                <li><span className="text-[#22d3ee]">issue #47</span> "Dashboard shows 0 nodes" - Nicolas</li>
              </ul>
              <div className="mt-4 pt-3 border-t border-gray-800 text-xs text-gray-500">
                Connected: GitHub • Slack • Jira • Notion
              </div>
            </div>
          </div>

          {/* SELF-HEALING INFRASTRUCTURE */}
          <div className="p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#10b981]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Self-Healing Infrastructure</h3>
            </div>
            <p className="text-gray-400 mb-6">
              99.7% uptime. Auto-restart. Monitored 24/7. It just works.
            </p>
            <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
              <div className="text-xs text-gray-500 mb-3">System health right now:</div>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <div className="text-[#10b981] font-mono">● FalkorDB</div>
                  <div className="text-gray-500">Running • 18,874 nodes</div>
                </div>
                <div>
                  <div className="text-[#10b981] font-mono">● WebSocket API</div>
                  <div className="text-gray-500">Running • port 8000</div>
                </div>
                <div>
                  <div className="text-[#10b981] font-mono">● Dashboard</div>
                  <div className="text-gray-500">Running • port 3000</div>
                </div>
                <div>
                  <div className="text-[#10b981] font-mono">● MPSv3 Supervisor</div>
                  <div className="text-gray-500">Active • auto-restart</div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-gray-800 text-xs text-gray-500">
                99.7% uptime • Open source • Verifiable
              </div>
            </div>
            <a href="https://github.com/mind-protocol" className="inline-block mt-4 text-sm text-[#10b981] hover:underline">
              → Inspect the code yourself
            </a>
          </div>
        </div>
      </section>

      {/* PRODUCTS */}
      <section id="products" className="py-24 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-4 text-center">Solutions</h2>
          <p className="text-xl text-gray-400 mb-12 text-center">
            Pick the one that fits your needs.
          </p>

          <div className="space-y-8">
            {/* GraphCare */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#1DB7B3]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">GraphCare</h3>
                  <p className="text-xl text-[#6FE7E2]">Preserve Institutional Knowledge</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Taking Clients</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">The Problem</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    Senior dev leaves. 10 years of context vanishes. Documentation scattered everywhere.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">What You Get</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ Extract: Scan codebase, docs, Slack, Jira automatically</li>
                    <li>✓ Query: Ask anything, get answers in &lt;2.3s</li>
                    <li>✓ Preserve: Knowledge stays when people leave</li>
                  </ul>
                </div>

                <div>
                  <div className="bg-[#0A0B0D] p-3 rounded mb-4">
                    <div className="text-xs text-gray-500 mb-2">Example queries:</div>
                    <ul className="text-xs text-gray-400 space-y-1">
                      <li>"Why is auth structured this way?"</li>
                      <li>"What modifies user permissions?"</li>
                      <li>"Show payment system dependencies"</li>
                    </ul>
                  </div>

                  <p className="text-sm text-gray-400 mb-2">
                    <strong>Live now:</strong> 18,874 nodes from our codebase
                  </p>

                  <p className="text-sm text-gray-400">
                    <strong>Pricing:</strong> $5-8k setup • $500-2k/mo
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="/consciousness" className="text-[#6FE7E2] hover:underline text-sm">
                  See Live Demo →
                </a>
                <a href="https://github.com/mind-protocol/graphcare" className="text-[#6FE7E2] hover:underline text-sm">
                  View Source →
                </a>
                <a href="mailto:hello@mindprotocol.ai" className="text-[#6FE7E2] hover:underline text-sm">
                  Book Evidence Sprint →
                </a>
              </div>
            </div>

            {/* ScopeLock */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#E4A631]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">ScopeLock</h3>
                  <p className="text-xl text-[#E4A631]">Fixed-Price Software Delivery</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Taking Clients</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">The Problem</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    "2 weeks" becomes 5 months. Scope creep. Endless disputes over "done."
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">What You Get</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ Locked scope: AC.md in git before work starts</li>
                    <li>✓ Executable tests: You run them yourself</li>
                    <li>✓ Pay on proof: Tests pass = done</li>
                  </ul>
                </div>

                <div>
                  <div className="bg-[#0A0B0D] p-3 rounded mb-4">
                    <div className="text-xs text-gray-500 mb-2">Process:</div>
                    <ol className="text-xs text-gray-400 space-y-1 list-decimal list-inside">
                      <li>Evidence Sprint: Lock AC.md in git</li>
                      <li>Development: Build + write tests</li>
                      <li>Delivery: Tests pass = payment</li>
                    </ol>
                  </div>

                  <p className="text-sm text-gray-400 mb-2">
                    <strong>No ambiguity.</strong> Tests pass or refund.
                  </p>

                  <p className="text-sm text-gray-400">
                    <strong>Pricing:</strong> $500-2k Evidence Sprint • Fixed after AC locked
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://github.com/mind-protocol/scopelock" className="text-[#E4A631] hover:underline text-sm">
                  View Process →
                </a>
                <a href="mailto:hello@mindprotocol.ai" className="text-[#E4A631] hover:underline text-sm">
                  Book Evidence Sprint →
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-16 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-white mb-2">Get Started</h3>
            <p className="text-gray-400 mb-6">Choose your path</p>
            <div className="flex gap-4 justify-center flex-wrap">
              <a
                href="/consciousness"
                className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
              >
                Explore Live Dashboard →
              </a>
              <a
                href="mailto:hello@mindprotocol.ai"
                className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
              >
                Book Evidence Sprint
              </a>
              <a
                href="https://github.com/mind-protocol"
                className="px-6 py-3 border-2 border-gray-600 text-gray-400 rounded hover:border-[#1DB7B3] hover:text-[#6FE7E2] transition-all"
              >
                View Source Code
              </a>
            </div>
          </div>

          <div className="text-center text-gray-500 text-sm border-t border-gray-800 pt-8">
            <div className="flex gap-6 justify-center flex-wrap mb-4">
              <a href="https://twitter.com/mindprotocol" className="hover:text-[#6FE7E2] transition-colors">
                Twitter
              </a>
              <a href="https://t.me/mindprotocol" className="hover:text-[#6FE7E2] transition-colors">
                Telegram
              </a>
              <a href="https://github.com/mind-protocol" className="hover:text-[#6FE7E2] transition-colors">
                GitHub
              </a>
              <a href="mailto:hello@mindprotocol.ai" className="hover:text-[#6FE7E2] transition-colors">
                Contact
              </a>
            </div>
            <p className="text-xs text-gray-600">© 2025 Mind Protocol • Open source infrastructure for AI organizations</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
