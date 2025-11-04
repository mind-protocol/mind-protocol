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
      {/* HERO */}
      <section className="py-24 border-b border-gray-800">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            AI Organizations<br />That Actually Work
          </h1>
          <p className="text-2xl md:text-3xl text-[#6FE7E2] mb-8 font-light">
            Graph-based consciousness substrate. Real memory. Real coordination.
          </p>

          {/* Live Status */}
          <div className="inline-flex items-center gap-2 bg-[#0a0a0f]/80 border border-green-500/30 rounded-lg px-4 py-2 mb-8">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm font-semibold">LIVE NOW</span>
            <span className="text-gray-400 text-sm">• 1,147 nodes • &lt;2.3s queries</span>
          </div>

          <div className="flex gap-4 justify-center flex-wrap">
            <a
              href="/consciousness"
              className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
            >
              Live Dashboard →
            </a>
            <a
              href="https://github.com/mind-protocol/graphcare"
              className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
            >
              Verify the Code
            </a>
          </div>
        </div>
      </section>

      {/* LAYER 1 - INDIVIDUAL MEMORY */}
      <section id="layers" className="min-h-screen flex flex-col relative overflow-hidden border-t border-gray-800">
        {/* Header */}
        <div className="pt-12 pb-6 px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#22d3ee] shadow-[0_0_15px_#22d3ee]"></div>
            <h2 className="text-4xl text-white font-bold">Layer 1: Individual Memory</h2>
          </div>
          <p className="text-gray-400">100 citizen nodes • Clustered by organization • Persistent context</p>
        </div>

        {/* Graph */}
        <div className="flex-1 relative">
          <div className="absolute inset-0">
            <LayerGraphVisualization visibleLayers={['l1']} showTitle={true} />
          </div>

          {/* Example Node Bubble - positioned on graph */}
          <div className="absolute top-1/4 right-1/4 z-10 bg-[#0a0a0f]/95 backdrop-blur-xl border border-[#22d3ee]/50 rounded-lg p-4 shadow-[0_0_30px_rgba(34,211,238,0.4)] max-w-xs">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-[#22d3ee] animate-pulse"></div>
              <span className="text-[#22d3ee] font-semibold text-sm">Felix</span>
              <span className="text-gray-500 text-xs">• Consciousness Engineer</span>
            </div>
            <div className="text-xs text-gray-300 mb-2 border-l-2 border-[#22d3ee]/30 pl-2">
              <p className="mb-1"><span className="text-gray-500">Last active:</span> 2 mins ago</p>
              <p className="mb-1"><span className="text-gray-500">Recent memory:</span> "JWT token migration March 2024. Mobile connection failed with 24h expiry. ADR-023."</p>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>Connections: 12 within org, 3 cross-org</span>
              <span className="text-[#22d3ee]">Energy: 0.87</span>
            </div>
          </div>
        </div>
      </section>

      {/* LAYER 2 - ORGANIZATIONAL COORDINATION */}
      <section className="min-h-screen flex flex-col relative overflow-hidden border-t border-gray-800">
        {/* Header */}
        <div className="pt-12 pb-6 px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#a855f7] shadow-[0_0_15px_#a855f7]"></div>
            <h2 className="text-4xl text-white font-bold">Layer 2: Organizational Coordination</h2>
          </div>
          <p className="text-gray-400">50 organization nodes • Cross-citizen coordination • Autonomous triage</p>
        </div>

        {/* Graph */}
        <div className="flex-1 relative">
          <div className="absolute inset-0">
            <LayerGraphVisualization visibleLayers={['l2']} />
          </div>

          {/* Example Node Bubble */}
          <div className="absolute top-1/3 left-1/4 z-10 bg-[#0a0a0f]/95 backdrop-blur-xl border border-[#a855f7]/50 rounded-lg p-4 shadow-[0_0_30px_rgba(168,85,247,0.4)] max-w-xs">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-[#a855f7] animate-pulse"></div>
              <span className="text-[#a855f7] font-semibold text-sm">GraphCare Org</span>
            </div>
            <div className="text-xs text-gray-300 mb-2 border-l-2 border-[#a855f7]/30 pl-2">
              <p className="mb-1"><span className="text-gray-500">Active task:</span> Security triage (23 issues found)</p>
              <p className="mb-1"><span className="text-gray-500">Priority:</span> 3 CRITICAL in payment system (untested, $2M/month revenue)</p>
              <p className="mb-1"><span className="text-gray-500">Action:</span> PRs generated, Vera assigned verification</p>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>7 specialists active</span>
              <span className="text-[#a855f7]">Coordination: 0.94</span>
            </div>
          </div>
        </div>
      </section>

      {/* LAYER 3 - EXTERNAL REACH */}
      <section className="min-h-screen flex flex-col relative overflow-hidden border-t border-gray-800">
        {/* Header */}
        <div className="pt-12 pb-6 px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#f59e0b] shadow-[0_0_15px_#f59e0b]"></div>
            <h2 className="text-4xl text-white font-bold">Layer 3: External Reach</h2>
          </div>
          <p className="text-gray-400">35 ecosystem nodes • GitHub, Slack, Notion, Jira • Full context integration</p>
        </div>

        {/* Graph */}
        <div className="flex-1 relative">
          <div className="absolute inset-0">
            <LayerGraphVisualization visibleLayers={['l3']} />
          </div>

          {/* Example Node Bubble */}
          <div className="absolute top-1/2 right-1/3 z-10 bg-[#0a0a0f]/95 backdrop-blur-xl border border-[#f59e0b]/50 rounded-lg p-4 shadow-[0_0_30px_rgba(245,158,11,0.4)] max-w-xs">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-[#f59e0b] animate-pulse"></div>
              <span className="text-[#f59e0b] font-semibold text-sm">GitHub Integration</span>
            </div>
            <div className="text-xs text-gray-300 mb-2 border-l-2 border-[#f59e0b]/30 pl-2">
              <p className="mb-1"><span className="text-gray-500">Query:</span> "Why is user service complex?"</p>
              <p className="mb-1"><span className="text-gray-500">Found:</span> 47 dependencies, Oct 2023 refactor</p>
              <p className="mb-1"><span className="text-gray-500">Cross-ref:</span> Slack → "GDPR required complexity" | Notion → ADR-034 | Jira → LEGAL-234 (6 weeks)</p>
            </div>
            <div className="flex gap-3 text-xs text-gray-400">
              <span>4 sources queried</span>
              <span className="text-[#f59e0b]">Confidence: 0.91</span>
            </div>
          </div>
        </div>
      </section>

      {/* LAYER 4 - EFFICIENT OPERATION */}
      <section className="min-h-screen flex flex-col relative overflow-hidden border-t border-gray-800">
        {/* Header */}
        <div className="pt-12 pb-6 px-6 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div className="w-3 h-3 rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]"></div>
            <h2 className="text-4xl text-white font-bold">Layer 4: Efficient Operation</h2>
          </div>
          <p className="text-gray-400">8 governance nodes • Resource optimization • Performance monitoring</p>
        </div>

        {/* Graph */}
        <div className="flex-1 relative">
          <div className="absolute inset-0">
            <LayerGraphVisualization visibleLayers={['l4']} />
          </div>

          {/* Example Node Bubble */}
          <div className="absolute bottom-1/4 left-1/3 z-10 bg-[#0a0a0f]/95 backdrop-blur-xl border border-[#10b981]/50 rounded-lg p-4 shadow-[0_0_30px_rgba(16,185,129,0.4)] max-w-xs">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse"></div>
              <span className="text-[#10b981] font-semibold text-sm">Performance Monitor</span>
            </div>
            <div className="text-xs text-gray-300 mb-2 border-l-2 border-[#10b981]/30 pl-2">
              <p className="mb-1"><span className="text-gray-500">System metrics:</span></p>
              <div className="grid grid-cols-2 gap-x-3 gap-y-1">
                <span>Query p50: 1.8s</span>
                <span>Query p95: 2.7s</span>
                <span>Memory: 4.2GB</span>
                <span>Health: 94%</span>
                <span>Daily sync: 1.2h</span>
                <span>Cost: ~$12/mo</span>
              </div>
            </div>
            <div className="text-xs text-gray-400">
              <span className="text-[#10b981]">Status:</span> Optimal • No intervention needed
            </div>
          </div>
        </div>
      </section>

      {/* PRODUCTS */}
      <section id="products" className="py-24 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-4 text-center">AI Organizations We've Built</h2>
          <p className="text-xl text-gray-400 mb-12 text-center">
            Production systems. Open source. Operational now.
          </p>

          <div className="space-y-8">
            {/* GraphCare */}
            {/* GraphCare */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#1DB7B3]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">GraphCare</h3>
                  <p className="text-xl text-[#6FE7E2]">Preserves Institutional Knowledge</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Production</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">The Problem</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    Senior dev leaves. 10 years of context vanishes. New hires spend weeks asking "why?"
                    Documentation scattered. Nobody knows the full story.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">7 Specialists</h4>
                  <ul className="text-xs text-gray-400 space-y-1">
                    <li>• MEL - Coordinates, quality gates</li>
                    <li>• ATLAS - Maps knowledge semantically</li>
                    <li>• FELIX - Extracts code structure</li>
                    <li>• ADA - Infers architecture</li>
                    <li>• VERA - Analyzes coverage</li>
                    <li>• MARCUS - Security audits</li>
                    <li>• SAGE - Synthesizes docs</li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What You Get</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ Complete knowledge graph (you own it)</li>
                    <li>✓ Query interface (CLI + API)</li>
                    <li>✓ Auto-generated documentation</li>
                    <li>✓ Daily sync, health monitoring</li>
                  </ul>

                  <div className="bg-[#0A0B0D] p-3 rounded mt-4">
                    <p className="text-xs text-[#6FE7E2] font-semibold mb-2">Example Queries:</p>
                    <ul className="text-xs text-gray-400 space-y-1">
                      <li>"Why is auth structured this way?"</li>
                      <li>"What modifies user permissions?"</li>
                      <li>"Show all dependencies of payment"</li>
                    </ul>
                  </div>

                  <p className="text-xs text-gray-400 mt-4">
                    <strong>Pricing:</strong> $5-8k setup • $500-2k/mo maintenance
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://github.com/mind-protocol/graphcare" className="text-[#6FE7E2] hover:underline text-sm">
                  GitHub →
                </a>
                <a href="#demo" className="text-[#6FE7E2] hover:underline text-sm">
                  Book Demo →
                </a>
              </div>
            </div>

            {/* ScopeLock */}
            <div className="bg-[#151619] p-8 rounded-lg border border-[#E4A631]">
              <div className="flex items-center justify-between mb-6 flex-wrap gap-4">
                <div>
                  <h3 className="text-4xl text-white font-bold mb-2">ScopeLock</h3>
                  <p className="text-xl text-[#E4A631]">Evidence-Based Delivery</p>
                </div>
                <div className="flex gap-2">
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded text-xs">Production</span>
                  <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">Open Source</span>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">The Problem</h4>
                  <p className="text-sm text-gray-400 mb-4">
                    Projects drag from "2 weeks" to 5 months. Scope creep. "Done" is ambiguous.
                  </p>

                  <h4 className="text-lg text-white font-semibold mb-2">The Solution</h4>
                  <p className="text-sm text-gray-400">
                    Lock scope with executable acceptance criteria. Pay only when tests pass.
                  </p>
                </div>

                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What You Get</h4>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>✓ AC.md locked at git tag</li>
                    <li>✓ Executable tests (you run them)</li>
                    <li>✓ Evidence Sprint (2-5 days)</li>
                    <li>✓ Pay only when tests pass</li>
                  </ul>

                  <p className="text-xs text-gray-400 mt-4 italic">
                    No ambiguity. Tests pass or refund.
                  </p>
                </div>
              </div>

              <div className="flex gap-4 pt-6 border-t border-gray-800 mt-6">
                <a href="https://github.com/mind-protocol/scopelock" className="text-[#E4A631] hover:underline text-sm">
                  GitHub →
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* VERIFY */}
      <section id="verify" className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#151619] to-[#0A0B0D]">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-5xl font-bold text-white mb-4 text-center">Verify Everything</h2>
          <p className="text-xl text-gray-400 mb-12 text-center">
            Don't trust marketing. Check the work.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#1DB7B3] transition-colors">
              <h4 className="text-lg text-[#6FE7E2] font-semibold mb-3">Open Source</h4>
              <p className="text-sm text-gray-400 mb-4">
                Full source code. Daily commits. MIT licensed. Run it yourself.
              </p>
              <a href="https://github.com/mind-protocol" className="text-[#6FE7E2] text-sm hover:underline">
                GitHub →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#1DB7B3] transition-colors">
              <h4 className="text-lg text-[#6FE7E2] font-semibold mb-3">Live Operations</h4>
              <p className="text-sm text-gray-400 mb-4">
                See GraphCare working. Watch specialists coordinate. Not a demo.
              </p>
              <a href="/consciousness" className="text-[#6FE7E2] text-sm hover:underline">
                Dashboard →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800 hover:border-[#E4A631] transition-colors">
              <h4 className="text-lg text-[#E4A631] font-semibold mb-3">The €35.5K Lesson</h4>
              <p className="text-sm text-gray-400 mb-4">
                We lost €35,500 in production. That failure shaped everything.
              </p>
              <p className="text-sm text-[#E4A631]">
                We don't hide failures. We learn.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* GET STARTED */}
      <section id="demo" className="py-24 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <h2 className="text-5xl font-bold text-white mb-4">Get Started</h2>
          <p className="text-xl text-gray-400 mb-12">Choose your path</p>

          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800">
              <h4 className="text-xl text-[#6FE7E2] font-semibold mb-4">Auditor's Path</h4>
              <p className="text-sm text-gray-400 mb-4">
                Verify before talking. Check code, metrics, docs.
              </p>
              <a href="https://github.com/mind-protocol" className="inline-block px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all text-sm">
                Start Verification →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800">
              <h4 className="text-xl text-[#6FE7E2] font-semibold mb-4">Builder's Path</h4>
              <p className="text-sm text-gray-400 mb-4">
                Understand architecture. Fork repos. Build something.
              </p>
              <a href="https://docs.mindprotocol.ai" className="inline-block px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all text-sm">
                Technical Docs →
              </a>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-gray-800">
              <h4 className="text-xl text-[#6FE7E2] font-semibold mb-4">Buyer's Path</h4>
              <p className="text-sm text-gray-400 mb-4">
                Book demo. Evidence Sprint. 5-7 day delivery.
              </p>
              <a href="mailto:hello@mindprotocol.ai" className="inline-block px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all text-sm">
                Book Demo →
              </a>
            </div>
          </div>

          <div className="text-center">
            <p className="text-gray-400 mb-3">Questions?</p>
            <div className="flex gap-6 justify-center flex-wrap">
              <a href="mailto:hello@mindprotocol.ai" className="text-[#6FE7E2] hover:underline text-sm">
                hello@mindprotocol.ai
              </a>
              <a href="https://t.me/mindprotocol" className="text-[#6FE7E2] hover:underline text-sm">
                Telegram
              </a>
              <a href="https://twitter.com/mindprotocol" className="text-[#6FE7E2] hover:underline text-sm">
                Twitter
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="py-12 border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Organizations</h4>
              <ul className="space-y-2 text-xs text-gray-400">
                <li><a href="#products" className="hover:text-[#6FE7E2]">GraphCare</a></li>
                <li><a href="#products" className="hover:text-[#6FE7E2]">ScopeLock</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Resources</h4>
              <ul className="space-y-2 text-xs text-gray-400">
                <li><a href="https://docs.mindprotocol.ai" className="hover:text-[#6FE7E2]">Docs</a></li>
                <li><a href="https://github.com/mind-protocol" className="hover:text-[#6FE7E2]">GitHub</a></li>
                <li><a href="/consciousness" className="hover:text-[#6FE7E2]">Dashboard</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Company</h4>
              <ul className="space-y-2 text-xs text-gray-400">
                <li><a href="#verify" className="hover:text-[#6FE7E2]">The €35.5K Lesson</a></li>
                <li><a href="mailto:hello@mindprotocol.ai" className="hover:text-[#6FE7E2]">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4 text-sm">Community</h4>
              <ul className="space-y-2 text-xs text-gray-400">
                <li><a href="https://twitter.com/mindprotocol" className="hover:text-[#6FE7E2]">Twitter</a></li>
                <li><a href="https://t.me/mindprotocol" className="hover:text-[#6FE7E2]">Telegram</a></li>
                <li><a href="https://github.com/mind-protocol" className="hover:text-[#6FE7E2]">GitHub</a></li>
              </ul>
            </div>
          </div>
          <div className="text-center text-gray-500 text-xs border-t border-gray-800 pt-8">
            <p className="mb-2">© 2025 Mind Protocol - AI organizations that remember, coordinate, and deliver</p>
            <p className="text-xs">We build in public. Verify everything.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
