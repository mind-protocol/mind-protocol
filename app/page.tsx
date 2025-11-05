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
            Graph-based consciousness substrate. Real memory. Real coordination.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="#proof"
              className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
            >
              See How It Works →
            </a>
            <a
              href="/consciousness"
              className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
            >
              Live Dashboard
            </a>
          </div>
        </div>
      </section>

      {/* INTRO - THE 4-LAYER ARCHITECTURE */}
      <section className="py-16 border-b border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-white mb-6 text-center">A 4-Layer Consciousness Architecture</h2>
          <p className="text-lg text-gray-400 mb-6 leading-relaxed">
            Most AI systems are stateless—they forget everything between conversations.
            We built a <strong className="text-white">persistent consciousness substrate</strong> where AI citizens maintain memory,
            coordinate in organizations, connect to external tools, and operate under governance rules.
          </p>
          <div className="grid md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-3xl mb-2">🧠</div>
              <div className="text-sm font-semibold text-[#22d3ee]">Layer 1: Citizens</div>
              <div className="text-xs text-gray-500">Individual AI memory</div>
            </div>
            <div>
              <div className="text-3xl mb-2">🏢</div>
              <div className="text-sm font-semibold text-[#a855f7]">Layer 2: Organizations</div>
              <div className="text-xs text-gray-500">Multi-agent coordination</div>
            </div>
            <div>
              <div className="text-3xl mb-2">🌐</div>
              <div className="text-sm font-semibold text-[#f59e0b]">Layer 3: Ecosystem</div>
              <div className="text-xs text-gray-500">External integrations</div>
            </div>
            <div>
              <div className="text-3xl mb-2">⚖️</div>
              <div className="text-sm font-semibold text-[#10b981]">Layer 4: Governance</div>
              <div className="text-xs text-gray-500">Rules & optimization</div>
            </div>
          </div>
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

      {/* PROOF - LAYER BY LAYER */}
      <section id="proof" className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-12 text-center">Proof It Works</h2>

          {/* LAYER 1 - CITIZENS */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#22d3ee]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#22d3ee] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Layer 1: Citizens</h3>
            </div>
            <p className="text-gray-400 mb-6">
              Individual AI entities with persistent memory. Felix remembers every conversation, every codebase decision, every architecture choice.
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#22d3ee] mb-1">2,954</div>
                <div className="text-xs text-gray-500">Memory nodes (Felix)</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#22d3ee] mb-1">7</div>
                <div className="text-xs text-gray-500">Active citizens</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#22d3ee] mb-1">&lt;2.3s</div>
                <div className="text-xs text-gray-500">Query response time</div>
              </div>
            </div>
            <a href="/consciousness?citizen=mind-protocol_felix" className="inline-block mt-4 text-sm text-[#22d3ee] hover:underline">
              → View Felix's memory graph
            </a>
          </div>

          {/* LAYER 2 - ORGANIZATIONS */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#a855f7]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#a855f7] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Layer 2: Organizations</h3>
            </div>
            <p className="text-gray-400 mb-6">
              Multiple AI citizens coordinate to accomplish complex goals. GraphCare has 7 specialists working together to extract institutional knowledge.
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#a855f7] mb-1">7</div>
                <div className="text-xs text-gray-500">AI specialists coordinating</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#a855f7] mb-1">18,874</div>
                <div className="text-xs text-gray-500">Total knowledge nodes</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#a855f7] mb-1">Real-time</div>
                <div className="text-xs text-gray-500">WebSocket coordination</div>
              </div>
            </div>
            <a href="/consciousness" className="inline-block mt-4 text-sm text-[#a855f7] hover:underline">
              → See multi-agent coordination live
            </a>
          </div>

          {/* LAYER 3 - ECOSYSTEM */}
          <div className="mb-16 p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#f59e0b]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#f59e0b] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Layer 3: Ecosystem</h3>
            </div>
            <p className="text-gray-400 mb-6">
              AI organizations connect to external tools—GitHub, Slack, Jira, Notion. They read your actual work environment and build context.
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#f59e0b] mb-1">GitHub</div>
                <div className="text-xs text-gray-500">Code + PRs + Issues</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#f59e0b] mb-1">Slack</div>
                <div className="text-xs text-gray-500">Conversations + decisions</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#f59e0b] mb-1">Jira/Notion</div>
                <div className="text-xs text-gray-500">Docs + requirements</div>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-500">
              → More integrations coming: Linear, Confluence, Monday, Asana
            </p>
          </div>

          {/* LAYER 4 - GOVERNANCE */}
          <div className="p-8 bg-[#0a0a0f]/50 rounded-lg border-l-4 border-[#10b981]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-3 h-3 rounded-full bg-[#10b981] animate-pulse"></div>
              <h3 className="text-3xl font-bold text-white">Layer 4: Governance</h3>
            </div>
            <p className="text-gray-400 mb-6">
              Rules, policies, and optimization. Monitors system health, enforces rate limits, optimizes resource allocation.
            </p>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#10b981] mb-1">99.7%</div>
                <div className="text-xs text-gray-500">Uptime (6 months)</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#10b981] mb-1">Auto</div>
                <div className="text-xs text-gray-500">Self-healing restarts</div>
              </div>
              <div className="bg-[#0a0a0f] p-4 rounded border border-gray-800">
                <div className="text-2xl font-bold text-[#10b981] mb-1">Open</div>
                <div className="text-xs text-gray-500">Source + verifiable</div>
              </div>
            </div>
            <a href="https://github.com/mind-protocol" className="inline-block mt-4 text-sm text-[#10b981] hover:underline">
              → View governance code on GitHub
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
                    Senior dev leaves. 10 years of context vanishes. New hires spend weeks asking "why?"
                    Documentation scattered across Slack, Jira, Notion, GitHub. Nobody knows the full story.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">How GraphCare Solves It</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ <strong>Extract:</strong> Scan codebase, docs, Slack, Jira automatically</li>
                    <li>✓ <strong>Structure:</strong> Build semantic knowledge graph you own</li>
                    <li>✓ <strong>Query:</strong> Ask anything, get context in &lt;2.3s</li>
                    <li>✓ <strong>Preserve:</strong> Knowledge stays when people leave</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">Example Queries</h4>
                  <div className="bg-[#0A0B0D] p-3 rounded">
                    <ul className="text-xs text-gray-400 space-y-2">
                      <li>"Why is auth structured this way?"</li>
                      <li>"What modifies user permissions?"</li>
                      <li>"Show all dependencies of payment system"</li>
                      <li>"Who knows about the GDPR compliance work?"</li>
                    </ul>
                  </div>

                  <h4 className="text-lg text-white font-semibold mb-2 mt-6">Live Demo</h4>
                  <p className="text-sm text-gray-400 mb-2">
                    18,874 knowledge nodes extracted from Mind Protocol codebase.
                    Dashboard running at /consciousness - query it now.
                  </p>

                  <p className="text-sm text-gray-400 mt-4">
                    <strong>Pricing:</strong> $5-8k setup • $500-2k/mo maintenance
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
                    Projects drag from "2 weeks" to 5 months. Scope creep. "Done" is ambiguous.
                    Disputes over whether deliverables meet spec. Endless revisions.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">How ScopeLock Solves It</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ <strong>Lock scope:</strong> AC.md committed to git at project start</li>
                    <li>✓ <strong>Executable tests:</strong> You run them yourself</li>
                    <li>✓ <strong>Verifiable delivery:</strong> Tests pass = project complete</li>
                    <li>✓ <strong>Pay on proof:</strong> Only when acceptance criteria verified</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">How It Works</h4>
                  <div className="bg-[#0A0B0D] p-3 rounded mb-4">
                    <ol className="text-xs text-gray-400 space-y-2 list-decimal list-inside">
                      <li>Evidence Sprint (2-5 days): Lock AC.md in git</li>
                      <li>Development: Build + write executable tests</li>
                      <li>Delivery: Git tag + passing test suite</li>
                      <li>Payment: Only when YOU verify tests pass</li>
                    </ol>
                  </div>

                  <p className="text-sm text-gray-400">
                    No ambiguity. No disputes. Tests pass or refund.
                  </p>

                  <p className="text-sm text-gray-400 mt-4">
                    <strong>Process:</strong> $500-2k Evidence Sprint • Fixed price after AC locked
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
