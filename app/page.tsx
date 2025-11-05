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

      {/* HERO - VALUE PROPOSITION */}
      <section className="py-24 border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Your Senior Dev Leaves.<br />Their 10 Years of Context Stays.
          </h1>
          <p className="text-2xl md:text-3xl text-[#6FE7E2] mb-8 font-light">
            AI organizations that extract, preserve, and coordinate institutional knowledge.
          </p>
          <p className="text-lg text-gray-400 mb-8 max-w-3xl mx-auto">
            18,874 nodes of working memory. 7 AI specialists coordinating in real-time.
            Query any decision, trace any architecture choice, never lose context again.
          </p>

          {/* Value Proof */}
          <div className="grid md:grid-cols-3 gap-4 mb-8 max-w-4xl mx-auto">
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#10b981]">&lt;2.3s</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">Query Response Time</div>
            </div>
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#f59e0b]">18,874</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">Knowledge Nodes Captured</div>
            </div>
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#22d3ee]">7</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">AI Specialists Coordinating</div>
            </div>
          </div>

          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="/consciousness"
              className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
            >
              See Live Demo →
            </a>
            <a
              href="https://github.com/mind-protocol/graphcare"
              className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
            >
              View Source Code
            </a>
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

      {/* HOW IT WORKS */}
      <section className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h2 className="text-5xl font-bold text-white mb-4">How It Works</h2>
          <p className="text-xl text-gray-400 mb-12">
            7 AI specialists work together to capture, structure, and preserve your institutional knowledge.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-[#0a0a0f]/80 p-6 rounded-lg border border-gray-800">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-white mb-2">Extract</h3>
              <p className="text-sm text-gray-400">
                Scan your codebase, docs, Slack, Jira. Extract decisions, architecture, context.
              </p>
            </div>
            <div className="bg-[#0a0a0f]/80 p-6 rounded-lg border border-gray-800">
              <div className="text-4xl mb-4">🧠</div>
              <h3 className="text-xl font-semibold text-white mb-2">Structure</h3>
              <p className="text-sm text-gray-400">
                Build semantic graph. Link related concepts. Identify patterns, dependencies.
              </p>
            </div>
            <div className="bg-[#0a0a0f]/80 p-6 rounded-lg border border-gray-800">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold text-white mb-2">Query</h3>
              <p className="text-sm text-gray-400">
                Ask anything. Get context-aware answers in &lt;2.3s. Never lose knowledge again.
              </p>
            </div>
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

      {/* VERIFY EVERYTHING */}
      <section id="verify" className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#151619] to-[#0A0B0D]">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-4 text-center">Verify Everything</h2>
          <p className="text-xl text-gray-400 mb-12 text-center">
            We lost your trust. We're earning it back through transparent execution.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#1DB7B3] transition-colors">
              <h4 className="text-lg text-[#6FE7E2] font-semibold mb-3">Open Source</h4>
              <p className="text-sm text-gray-400 mb-4">
                Full source code. 65,000+ commits. MIT licensed. Run it yourself.
                No proprietary black boxes.
              </p>
              <a href="https://github.com/mind-protocol" className="text-[#6FE7E2] text-sm hover:underline">
                GitHub →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#1DB7B3] transition-colors">
              <h4 className="text-lg text-[#6FE7E2] font-semibold mb-3">Live Operations</h4>
              <p className="text-sm text-gray-400 mb-4">
                Dashboard shows real data. 18,874 nodes. 4-layer consciousness substrate.
                WebSocket updates in real-time.
              </p>
              <a href="/consciousness" className="text-[#6FE7E2] text-sm hover:underline">
                Dashboard →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#E4A631] transition-colors">
              <h4 className="text-lg text-[#E4A631] font-semibold mb-3">The €35.5K Lesson</h4>
              <p className="text-sm text-gray-400 mb-4">
                We don't hide failures. November 2024 broke us.
                But it taught us: test before claiming, prove before promising.
              </p>
              <p className="text-sm text-[#E4A631]">
                Read the full story →
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* STAY CONNECTED */}
      <section id="contact" className="py-24 border-t border-gray-800">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-5xl font-bold text-white mb-4">Stay Connected</h2>
          <p className="text-xl text-gray-400 mb-8">
            We're not asking for investment today. We're showing what we're building.
          </p>

          <div className="bg-[#151619] p-8 rounded-lg border border-gray-800 mb-8">
            <h3 className="text-2xl text-white font-semibold mb-4">Want to follow along?</h3>
            <div className="space-y-3 text-left max-w-xl mx-auto">
              <a href="/consciousness" className="block p-3 bg-[#0a0a0f] rounded border border-gray-800 hover:border-[#1DB7B3] transition-colors">
                <div className="text-[#6FE7E2] font-semibold mb-1">→ Live Activity Dashboard</div>
                <div className="text-xs text-gray-500">Real-time graph updates, WebSocket events</div>
              </a>
              <a href="https://github.com/mind-protocol" className="block p-3 bg-[#0a0a0f] rounded border border-gray-800 hover:border-[#1DB7B3] transition-colors">
                <div className="text-[#6FE7E2] font-semibold mb-1">→ GitHub Activity</div>
                <div className="text-xs text-gray-500">Every commit, every release, tagged and verifiable</div>
              </a>
              <a href="mailto:hello@mindprotocol.ai" className="block p-3 bg-[#0a0a0f] rounded border border-gray-800 hover:border-[#1DB7B3] transition-colors">
                <div className="text-[#6FE7E2] font-semibold mb-1">→ Direct Contact</div>
                <div className="text-xs text-gray-500">Questions? hello@mindprotocol.ai</div>
              </a>
            </div>
          </div>

          <p className="text-gray-500 text-sm">
            When we're ready to raise, you'll see it working first.
          </p>

          <div className="flex gap-6 justify-center flex-wrap mt-6">
            <a href="https://twitter.com/mindprotocol" className="text-[#6FE7E2] hover:underline text-sm">
              Twitter
            </a>
            <a href="https://t.me/mindprotocol" className="text-[#6FE7E2] hover:underline text-sm">
              Telegram
            </a>
            <a href="https://github.com/mind-protocol" className="text-[#6FE7E2] hover:underline text-sm">
              GitHub
            </a>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center text-gray-500 text-xs">
            <p className="mb-2">© 2025 Mind Protocol</p>
            <p className="text-xs">We build in public. We verify everything. We learn from failure.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
