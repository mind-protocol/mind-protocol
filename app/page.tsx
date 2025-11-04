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
      {/* HERO SECTION WITH GRAPH */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        {/* Graph Background */}
        <div className="absolute inset-0 z-0">
          <LayerGraphVisualization />
        </div>

        {/* Hero Content Overlays */}
        <div className="relative z-10 max-w-7xl mx-auto px-6 pt-20">
          {/* Main Message Bubble - Center */}
          <div className="text-center mb-12 bg-[#0a0a0f]/90 backdrop-blur-xl border border-[#1DB7B3]/30 rounded-2xl p-12 shadow-[0_0_50px_rgba(29,183,179,0.3)]">
            <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
              AI Organizations<br />That Actually Work
            </h1>
            <p className="text-2xl md:text-3xl text-[#6FE7E2] mb-6 font-light">
              Not agents. Not teams. Complete AI organizations<br />
              with persistent memory, coordination, and real capability.
            </p>
            <div className="flex gap-4 justify-center mt-8 flex-wrap">
              <a
                href="https://github.com/mind-protocol/graphcare"
                className="px-6 py-3 border-2 border-[#1DB7B3] text-[#6FE7E2] rounded hover:bg-[#1DB7B3] hover:text-[#0A0B0D] transition-all"
              >
                Verify the Code
              </a>
              <a
                href="#layers"
                className="px-6 py-3 bg-[#1DB7B3] text-[#0A0B0D] font-semibold rounded hover:bg-[#6FE7E2] transition-all"
              >
                How It Works ↓
              </a>
              <a
                href="#demo"
                className="px-6 py-3 border-2 border-[#6FE7E2] text-white rounded hover:bg-[#6FE7E2] hover:text-[#0A0B0D] transition-all"
              >
                Book Demo
              </a>
            </div>
          </div>

          {/* Status Bubble - Bottom Right */}
          <div className="fixed bottom-8 right-8 bg-[#0a0a0f]/95 backdrop-blur-xl border border-green-500/30 rounded-xl p-4 shadow-[0_0_30px_rgba(34,197,94,0.2)] max-w-sm z-50">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 text-sm font-semibold">LIVE NOW</span>
            </div>
            <p className="text-xs text-gray-400">
              GraphCare operational • 347 files • 1,147 nodes<br />
              6 specialists • &lt;2.3s queries • 94% health
            </p>
            <a href="/consciousness" className="text-[#6FE7E2] text-xs mt-2 inline-block hover:underline">
              Dashboard →
            </a>
          </div>

          {/* Open Source Badge - Bottom Left */}
          <div className="fixed bottom-8 left-8 bg-[#0a0a0f]/95 backdrop-blur-xl border border-[#E4A631]/30 rounded-xl p-4 shadow-[0_0_30px_rgba(228,166,49,0.2)] z-50">
            <p className="text-xs text-gray-400 mb-2">Open Source:</p>
            <a href="https://github.com/mind-protocol/graphcare" className="text-[#6FE7E2] text-sm hover:underline block">
              GraphCare →
            </a>
            <a href="https://github.com/mind-protocol/scopelock" className="text-[#6FE7E2] text-sm hover:underline block">
              ScopeLock →
            </a>
          </div>
        </div>
      </section>

      {/* WHY ORGANIZATIONS NOT AGENTS */}
      <section id="layers" className="py-24 border-t border-gray-800 bg-gradient-to-b from-[#0A0B0D] to-[#151619]">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold text-white mb-4">Why Organizations, Not Just Agents</h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Most AI tools are single agents that reset every session.<br />
              We build complete organizations with four critical capabilities.
            </p>
          </div>

          {/* The 4 Layers */}
          <div className="space-y-16">
            {/* LAYER 1 - INDIVIDUAL MEMORY */}
            <div className="relative bg-[#151619] p-8 rounded-lg border-l-4 border-[#22d3ee]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 rounded-full bg-[#22d3ee] shadow-[0_0_15px_#22d3ee]"></div>
                <h3 className="text-3xl text-[#22d3ee] font-semibold">Layer 1: Individual Memory</h3>
              </div>
              <p className="text-xl text-gray-300 mb-6">
                Each specialist remembers, learns, adapts
              </p>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What This Means For You</h4>
                  <ul className="space-y-2 text-gray-400">
                    <li>• Felix remembers your debugging patterns from 6 months ago</li>
                    <li>• Ada recalls your architecture preferences from past projects</li>
                    <li>• Marcus learns which security issues matter most</li>
                    <li>• They don't reset—they accumulate knowledge</li>
                  </ul>
                </div>

                <div className="bg-[#0A0B0D] p-6 rounded">
                  <h4 className="text-[#22d3ee] font-semibold mb-3">Real Example</h4>
                  <p className="text-sm text-gray-400 mb-3">
                    Your team refactored authentication in March 2024. New contractor 6 months later proposes:
                    "Why don't we just use JWT tokens? Simpler."
                  </p>
                  <div className="bg-[#22d3ee]/10 border border-[#22d3ee]/30 p-3 rounded">
                    <p className="text-xs text-[#22d3ee] font-semibold mb-1">WITH LAYER 1 MEMORY:</p>
                    <p className="text-xs text-gray-300">
                      Felix: "We moved away from JWT in March 2024. Mobile app's background sync broke with 24-hour expiration.
                      OAuth refresh tokens solved it. See ADR-023."
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 italic">
                    The organization remembers why decisions were made.
                  </p>
                </div>
              </div>
            </div>

            {/* LAYER 2 - ORGANIZATIONAL COORDINATION */}
            <div className="relative bg-[#151619] p-8 rounded-lg border-l-4 border-[#a855f7]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 rounded-full bg-[#a855f7] shadow-[0_0_15px_#a855f7]"></div>
                <h3 className="text-3xl text-[#a855f7] font-semibold">Layer 2: Organizational Coordination</h3>
              </div>
              <p className="text-xl text-gray-300 mb-6">
                Specialists coordinate, prioritize, align
              </p>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What This Means For You</h4>
                  <ul className="space-y-2 text-gray-400">
                    <li>• Mel coordinates without you managing handoffs</li>
                    <li>• Atlas and Felix work in parallel</li>
                    <li>• When Marcus finds issues, Vera verifies fixes</li>
                    <li>• Priorities adjust to what matters</li>
                  </ul>
                </div>

                <div className="bg-[#0A0B0D] p-6 rounded">
                  <h4 className="text-[#a855f7] font-semibold mb-3">Real Example</h4>
                  <p className="text-sm text-gray-400 mb-3">
                    Marcus finds 23 security issues.
                  </p>
                  <div className="bg-[#a855f7]/10 border border-[#a855f7]/30 p-3 rounded">
                    <p className="text-xs text-[#a855f7] font-semibold mb-1">WITH LAYER 2 COORDINATION:</p>
                    <p className="text-xs text-gray-300 mb-2">
                      Checks payment code (from Felix), sees Ada's notes ($2M/month), queries past incidents, coordinates with Vera on tests.
                    </p>
                    <p className="text-xs text-gray-300">
                      Result: "3 CRITICAL in payment (untested). PRs generated. 20 medium for next sprint."
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 italic">
                    You spent 0 minutes triaging.
                  </p>
                </div>
              </div>
            </div>

            {/* LAYER 3 - EXTERNAL REACH */}
            <div className="relative bg-[#151619] p-8 rounded-lg border-l-4 border-[#f59e0b]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 rounded-full bg-[#f59e0b] shadow-[0_0_15px_#f59e0b]"></div>
                <h3 className="text-3xl text-[#f59e0b] font-semibold">Layer 3: External Reach</h3>
              </div>
              <p className="text-xl text-gray-300 mb-6">
                Organization accesses tools, data, services
              </p>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What This Means For You</h4>
                  <ul className="space-y-2 text-gray-400">
                    <li>• Pulls from GitHub, Slack, Notion, Jira</li>
                    <li>• Queries production systems</li>
                    <li>• Integrates with your tools</li>
                    <li>• Reaches out without constant prompting</li>
                  </ul>
                </div>

                <div className="bg-[#0A0B0D] p-6 rounded">
                  <h4 className="text-[#f59e0b] font-semibold mb-3">Real Example</h4>
                  <p className="text-sm text-gray-400 mb-2">
                    "Why is our user service so complex?"
                  </p>
                  <div className="bg-[#f59e0b]/10 border border-[#f59e0b]/30 p-3 rounded">
                    <p className="text-xs text-[#f59e0b] font-semibold mb-1">WITH LAYER 3:</p>
                    <ul className="text-xs text-gray-300 space-y-1">
                      <li>• GitHub: 47 dependencies, Oct 2023 refactor</li>
                      <li>• Slack: "Tried to simplify, GDPR required complexity"</li>
                      <li>• Notion: ADR-034 "EU data residency rules"</li>
                      <li>• Jira: LEGAL-234 took 6 weeks</li>
                    </ul>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 italic">
                    Reaches across your entire knowledge ecosystem.
                  </p>
                </div>
              </div>
            </div>

            {/* LAYER 4 - EFFICIENT OPERATION */}
            <div className="relative bg-[#151619] p-8 rounded-lg border-l-4 border-[#10b981]">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-4 h-4 rounded-full bg-[#10b981] shadow-[0_0_15px_#10b981]"></div>
                <h3 className="text-3xl text-[#10b981] font-semibold">Layer 4: Efficient Operation</h3>
              </div>
              <p className="text-xl text-gray-300 mb-6">
                Organization runs efficiently at scale
              </p>

              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-lg text-white font-semibold mb-3">What This Means For You</h4>
                  <ul className="space-y-2 text-gray-400">
                    <li>• Predictable performance (&lt;3s queries)</li>
                    <li>• Reliable scheduling (daily syncs)</li>
                    <li>• Resource optimization</li>
                    <li>• Quality guarantees (&gt;90% coverage)</li>
                  </ul>
                </div>

                <div className="bg-[#0A0B0D] p-6 rounded">
                  <h4 className="text-[#10b981] font-semibold mb-3">From Production</h4>
                  <div className="bg-[#10b981]/10 border border-[#10b981]/30 p-3 rounded">
                    <div className="grid grid-cols-2 gap-2 text-xs text-gray-300">
                      <div><span className="text-[#10b981]">Query p50:</span> 1.8s</div>
                      <div><span className="text-[#10b981]">Query p95:</span> 2.7s</div>
                      <div><span className="text-[#10b981]">Daily sync:</span> 1.2h</div>
                      <div><span className="text-[#10b981]">Health:</span> 94%</div>
                      <div><span className="text-[#10b981]">Memory:</span> 4GB</div>
                      <div><span className="text-[#10b981]">Cost:</span> ~$12/mo</div>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-2 italic">
                    Reliably. Efficiently. Without monitoring.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Comparison */}
          <div className="mt-16 grid md:grid-cols-2 gap-8">
            <div className="bg-[#151619] p-6 rounded-lg border border-red-600/30">
              <h4 className="text-xl text-white font-semibold mb-4">Single AI Agents</h4>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start">
                  <span className="mr-2 text-red-500">❌</span>
                  <span>No Memory: Every chat starts fresh</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-red-500">❌</span>
                  <span>No Coordination: One agent, one task</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-red-500">❌</span>
                  <span>Limited Reach: Only what you paste</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-red-500">❌</span>
                  <span>Inconsistent: Speed varies wildly</span>
                </li>
              </ul>
              <p className="mt-4 text-gray-500 italic text-sm">Result: You work faster</p>
            </div>

            <div className="bg-[#151619] p-6 rounded-lg border border-[#1DB7B3]">
              <h4 className="text-xl text-[#6FE7E2] font-semibold mb-4">AI Organizations</h4>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start">
                  <span className="mr-2 text-[#1DB7B3]">✓</span>
                  <span>Persistent Memory (L1): Years of context</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-[#1DB7B3]">✓</span>
                  <span>Coordination (L2): 7 specialists parallel</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-[#1DB7B3]">✓</span>
                  <span>Full Access (L3): GitHub+Slack+Notion+Jira</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-[#1DB7B3]">✓</span>
                  <span>Reliable (L4): &lt;3s queries, SLAs</span>
                </li>
              </ul>
              <p className="mt-4 text-[#6FE7E2] font-semibold text-sm">Result: You work less</p>
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
