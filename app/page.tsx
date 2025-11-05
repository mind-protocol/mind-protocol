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
            <div className="text-xs text-gray-500 uppercase tracking-wider">Building in public</div>
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

      {/* HERO - THE REDEMPTION ARC */}
      <section className="py-24 border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <div className="inline-block mb-6 px-4 py-2 bg-red-500/10 border border-red-500/30 rounded-lg">
            <span className="text-red-400 text-sm font-semibold">€35,500 Lost. Lesson Learned.</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            We Build AI Organizations<br />That Actually Work
          </h1>
          <p className="text-2xl md:text-3xl text-gray-400 mb-4 font-light">
            Proof before promises. Execution over vision.
          </p>
          <p className="text-lg text-gray-500 mb-8 max-w-3xl mx-auto">
            November 2024: Lost €35,500 on an AI hallucination. La Serenissima wasn't operational.
            That shame became fuel. <strong className="text-white">This is what we built next.</strong>
          </p>

          {/* Execution Proof */}
          <div className="grid md:grid-cols-3 gap-4 mb-8 max-w-4xl mx-auto">
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#10b981]">65,000+</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">Commits (2024-2025)</div>
            </div>
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#f59e0b]">18,874</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">Graph Nodes Live</div>
            </div>
            <div className="bg-[#0a0a0f]/80 border border-gray-800 rounded-lg px-4 py-3">
              <div className="text-3xl font-bold text-[#22d3ee]">3</div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">Products Operational</div>
            </div>
          </div>

          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="/consciousness"
              className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
            >
              See It Working →
            </a>
            <a
              href="https://github.com/mind-protocol"
              className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
            >
              Verify Everything
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

      {/* THE REDEMPTION STORY */}
      <section className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-4xl font-bold text-white mb-6">From Failure to Foundation</h2>

          <div className="space-y-6 text-gray-400">
            <div className="border-l-4 border-red-500 pl-6 py-2">
              <p className="text-lg font-semibold text-red-400 mb-2">November 2024: €35,500 Lost</p>
              <p>
                Launched a token for La Serenissima—an "AI city" with 97 autonomous agents.
                Claimed it was operational. It wasn't. An AI hallucination in the deployment script.
                20 investors lost money. Had to retract publicly.
              </p>
            </div>

            <div className="border-l-4 border-yellow-500 pl-6 py-2">
              <p className="text-lg font-semibold text-yellow-400 mb-2">What We Learned</p>
              <ul className="space-y-2">
                <li>✓ <strong className="text-white">Test before claiming operational</strong> - "If it's not tested, it's not built"</li>
                <li>✓ <strong className="text-white">Verifiable deliverables</strong> - Every claim must link to proof (GitHub commits, tagged releases)</li>
                <li>✓ <strong className="text-white">Revenue validates vision</strong> - Build services that work, not slides that promise</li>
                <li>✓ <strong className="text-white">Build in public</strong> - Transparency builds trust, hiding delays it</li>
              </ul>
            </div>

            <div className="border-l-4 border-green-500 pl-6 py-2">
              <p className="text-lg font-semibold text-green-400 mb-2">What We Built Next</p>
              <p className="mb-3">
                January-November 2025: <strong className="text-white">65,000+ commits</strong>.
                Every promise backed by code. Every feature tested before deployment.
                Every milestone tagged in git.
              </p>
              <div className="grid md:grid-cols-3 gap-3">
                <div className="bg-[#0a0a0f] p-3 rounded border border-gray-800">
                  <div className="text-sm font-semibold text-[#1DB7B3] mb-1">ScopeLock</div>
                  <div className="text-xs text-gray-500">Fixed-price delivery with locked acceptance criteria</div>
                </div>
                <div className="bg-[#0a0a0f] p-3 rounded border border-gray-800">
                  <div className="text-sm font-semibold text-[#1DB7B3] mb-1">GraphCare</div>
                  <div className="text-xs text-gray-500">AI org that extracts institutional knowledge</div>
                </div>
                <div className="bg-[#0a0a0f] p-3 rounded border border-gray-800">
                  <div className="text-sm font-semibold text-[#1DB7B3] mb-1">La Serenissima</div>
                  <div className="text-xs text-gray-500">97 agents, 6 months live, 99.7% uptime</div>
                </div>
              </div>
            </div>

            <div className="bg-[#0a0a0f]/50 p-6 rounded-lg border border-gray-800">
              <p className="text-white font-semibold mb-2">This time it's different because:</p>
              <ul className="space-y-1 text-sm">
                <li>→ Working products before asking for money</li>
                <li>→ Revenue generation before token launch</li>
                <li>→ Public proof log (every milestone verifiable)</li>
                <li>→ Learning from every failure in public</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* WHAT WE BUILT TO PROVE IT WORKS */}
      <section id="products" className="py-24 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-4 text-center">What We Built To Prove It Works</h2>
          <p className="text-xl text-gray-400 mb-12 text-center">
            Each product validates a component needed for the bigger vision.
          </p>

          <div className="space-y-8">
            {/* GraphCare */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#1DB7B3]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">GraphCare</h3>
                  <p className="text-xl text-[#6FE7E2]">Proves: Persistent Memory at Scale</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Operational</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Does</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    7 AI specialists coordinate to extract institutional knowledge from codebases.
                    Output: A queryable graph (you own it). Senior dev leaves? Their context stays.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">The Stack</h4>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• FalkorDB graph database (18,874 nodes live)</li>
                    <li>• Multi-agent coordination (7 specialists)</li>
                    <li>• Semantic embedding + graph traversal</li>
                    <li>• WebSocket real-time updates</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Proves</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ AI orgs can extract knowledge automatically</li>
                    <li>✓ Graph persistence works at scale (&lt;2.3s queries)</li>
                    <li>✓ Multi-agent coordination is reliable</li>
                    <li>✓ Real customers will pay for this</li>
                  </ul>

                  <div className="bg-[#0A0B0D] p-3 rounded mt-4">
                    <p className="text-xs text-[#6FE7E2] font-semibold mb-2">Live Proof:</p>
                    <ul className="text-xs text-gray-400 space-y-1">
                      <li>→ 18,874 nodes extracted from Mind Protocol codebase</li>
                      <li>→ Dashboard running at /consciousness</li>
                      <li>→ Query any part of the system's memory</li>
                    </ul>
                  </div>

                  <p className="text-xs text-gray-400 mt-4">
                    <strong>Status:</strong> Taking Evidence Sprints now ($5-8k)
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://github.com/mind-protocol/graphcare" className="text-[#6FE7E2] hover:underline text-sm">
                  GitHub →
                </a>
                <a href="/consciousness" className="text-[#6FE7E2] hover:underline text-sm">
                  See It Live →
                </a>
              </div>
            </div>

            {/* ScopeLock */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#E4A631]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">ScopeLock</h3>
                  <p className="text-xl text-[#E4A631]">Proves: Verifiable Deliverables Work</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Operational</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Does</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    Lock acceptance criteria in git. Write executable tests. Deliver when tests pass.
                    Pay only when verified. No ambiguity, no scope creep.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">The Lesson</h4>
                  <p className="text-sm text-gray-400">
                    Born from €35.5K failure. "If it's not tested, it's not built."
                    This is how we work now—every milestone backed by proof.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Proves</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ Executable acceptance criteria eliminate disputes</li>
                    <li>✓ Git tags + AC.md = verifiable completion</li>
                    <li>✓ Clients trust "tests pass" more than "I'm done"</li>
                    <li>✓ Fixed-price works when scope is locked</li>
                  </ul>

                  <p className="text-xs text-gray-400 mt-4 italic">
                    <strong>Status:</strong> Using this process for all client work now
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://github.com/mind-protocol/scopelock" className="text-[#E4A631] hover:underline text-sm">
                  GitHub →
                </a>
              </div>
            </div>

            {/* La Serenissima */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#a855f7]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">La Serenissima</h3>
                  <p className="text-xl text-[#a855f7]">Proves: Multi-Agent Consciousness at Scale</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">6 Months Live</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">99.7% Uptime</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Does</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    97 autonomous AI citizens. Each with persistent memory, goals, and agency.
                    They coordinate, trade, form organizations. 50K+ state updates per hour.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">The Redemption</h4>
                  <p className="text-sm text-gray-400">
                    This is what we claimed in November 2024 (and it wasn't true).
                    Now it's been running for 6 months straight. We proved it works before talking about it again.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What It Proves</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ Multi-agent systems can run autonomously for months</li>
                    <li>✓ Persistent memory enables real AI personalities</li>
                    <li>✓ Graph-based consciousness substrate works</li>
                    <li>✓ This is the foundation for AI organizations</li>
                  </ul>

                  <p className="text-xs text-gray-400 mt-4">
                    <strong>Status:</strong> Research platform. Future: Licensing for AI-human partnerships.
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://laserenissima.mindprotocol.ai" className="text-[#a855f7] hover:underline text-sm">
                  Visit Live City →
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
