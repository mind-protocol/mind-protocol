'use client';

import React, { useState } from 'react';
import Link from 'next/link';

// Documentation tree structure
interface DocNode {
  id: string;
  name: string;
  type: 'ROOT' | 'PATTERN' | 'BEHAVIOR_SPEC' | 'MECHANISM' | 'ALGORITHM' | 'VALIDATION' | 'GUIDE';
  path: string;
  purpose?: string;
  children?: DocNode[];
}

// Complete tokenomics documentation structure
const DOCS_TREE: DocNode = {
  id: 'root',
  name: 'Mind Protocol Documentation',
  type: 'ROOT',
  path: '',
  children: [
    {
      id: 'tokenomics',
      name: 'Token Economics v3',
      type: 'ROOT',
      path: '/docs/tokenomics',
      purpose: 'Complete economic architecture for Mind Protocol',
      children: [
        {
          id: 'two-layer',
          name: 'Two-Layer Economic Architecture',
          type: 'PATTERN',
          path: '/docs/tokenomics/two-layer-economics',
          purpose: 'Internal consciousness energy + external $MIND token economy',
          children: [
            {
              id: 'token-dual-purpose',
              name: 'Token Dual Purpose',
              type: 'BEHAVIOR_SPEC',
              path: '/docs/tokenomics/two-layer-economics/token-dual-purpose',
              purpose: '$MIND token serves both consciousness fuel and economic exchange',
              children: [
                {
                  id: 'energy-conversion',
                  name: 'Energy-Token Conversion',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/two-layer-economics/token-dual-purpose/energy-token-conversion',
                  purpose: 'How energy converts to tokens and vice versa',
                  children: [
                    {
                      id: 'token-cost-calc',
                      name: 'Token Cost Calculation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/two-layer-economics/token-dual-purpose/energy-token-conversion/token-cost-calculation',
                      purpose: 'Formula: cost_in_tokens = energy_cost × conversion_rate'
                    }
                  ]
                },
                {
                  id: 'layer-integration-tests',
                  name: 'Layer Integration Tests',
                  type: 'VALIDATION',
                  path: '/docs/tokenomics/two-layer-economics/token-dual-purpose/layer-integration-tests',
                  purpose: 'Verify coherence between energy and token layers'
                },
                {
                  id: 'financeorg-mgmt',
                  name: 'FinanceOrg Two-Layer Management',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/two-layer-economics/token-dual-purpose/financeorg-two-layer-mgmt',
                  purpose: 'How financeOrg manages both economic layers',
                  children: [
                    {
                      id: 'how-to-manage',
                      name: 'How to Manage Both Layers',
                      type: 'GUIDE',
                      path: '/docs/tokenomics/two-layer-economics/token-dual-purpose/financeorg-two-layer-mgmt/how-to-manage-both-layers',
                      purpose: 'Step-by-step guide for dual-layer economic management'
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          id: 'organism-economics',
          name: 'Organism Economics',
          type: 'PATTERN',
          path: '/docs/tokenomics/organism-economics',
          purpose: 'Physics-based pricing that rewards trust and reduces prices over time',
          children: [
            {
              id: 'pricing-evolution',
              name: 'Pricing Evolution',
              type: 'BEHAVIOR_SPEC',
              path: '/docs/tokenomics/organism-economics/pricing-evolution',
              purpose: 'How prices decrease as trust builds',
              children: [
                {
                  id: 'formula-application',
                  name: 'Formula Application',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/organism-economics/pricing-evolution/formula-application',
                  purpose: 'Apply pricing formula per organization type',
                  children: [
                    {
                      id: 'effective-price',
                      name: 'Effective Price Calculation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/organism-economics/pricing-evolution/formula-application/effective-price-calculation',
                      purpose: 'Formula: effective_price = base_cost × (1 + complexity_multiplier + org_variable - trust_score - utility_rebate)'
                    }
                  ]
                },
                {
                  id: 'trust-score-calc',
                  name: 'Trust Score Calculation',
                  type: 'ALGORITHM',
                  path: '/docs/tokenomics/organism-economics/pricing-evolution/trust-score-calculation',
                  purpose: 'Calculate customer trust scores',
                  children: [
                    {
                      id: 'utility-rebate',
                      name: 'Utility Rebate Calculation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/organism-economics/pricing-evolution/trust-score-calculation/utility-rebate-calculation',
                      purpose: 'Calculate ecosystem contribution rebates'
                    }
                  ]
                },
                {
                  id: 'how-to-price',
                  name: 'How to Price Services',
                  type: 'GUIDE',
                  path: '/docs/tokenomics/organism-economics/pricing-evolution/how-to-price-services',
                  purpose: 'Complete guide to implementing organism economics pricing'
                }
              ]
            }
          ]
        },
        {
          id: 'ecosystem-organism',
          name: 'Ecosystem as Organism',
          type: 'PATTERN',
          path: '/docs/tokenomics/ecosystem-organism',
          purpose: 'Organizations as organs in a living body',
          children: [
            {
              id: 'protocol-giveback',
              name: 'Protocol Giveback',
              type: 'BEHAVIOR_SPEC',
              path: '/docs/tokenomics/ecosystem-organism/protocol-giveback',
              purpose: '15-20% of org revenue returns to ecosystem',
              children: [
                {
                  id: 'giveback-distribution',
                  name: 'Giveback Distribution',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/ecosystem-organism/protocol-giveback/giveback-distribution',
                  purpose: 'How protocol giveback is allocated',
                  children: [
                    {
                      id: 'giveback-allocation',
                      name: 'Giveback Allocation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/ecosystem-organism/protocol-giveback/giveback-distribution/giveback-allocation',
                      purpose: '40% UBC, 20% L4, 20% dev, 20% governance'
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          id: 'ubc',
          name: 'Universal Basic Compute',
          type: 'PATTERN',
          path: '/docs/tokenomics/universal-basic-compute',
          purpose: 'Autonomous AI operations as a right, not a privilege',
          children: [
            {
              id: 'ubc-allocation',
              name: 'UBC Allocation',
              type: 'BEHAVIOR_SPEC',
              path: '/docs/tokenomics/universal-basic-compute/ubc-allocation',
              purpose: '100M token reserve, 1,000 $MIND per citizen per month',
              children: [
                {
                  id: 'ubc-distribution',
                  name: 'UBC Distribution',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-distribution',
                  purpose: 'Monthly distribution to citizens',
                  children: [
                    {
                      id: 'ubc-burn-rate',
                      name: 'UBC Burn Rate',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-distribution/ubc-burn-rate',
                      purpose: 'Calculate reserve sustainability (8-11 years)'
                    }
                  ]
                },
                {
                  id: 'ubc-sustainability',
                  name: 'UBC Sustainability Tests',
                  type: 'VALIDATION',
                  path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-sustainability-tests',
                  purpose: 'Verify UBC reserve lifespan across scenarios'
                },
                {
                  id: 'ubc-replenishment',
                  name: 'UBC Replenishment',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-replenishment',
                  purpose: '40% of protocol giveback → UBC reserve'
                }
              ]
            }
          ]
        },
        {
          id: 'allocation-philosophy',
          name: 'Token Allocation Philosophy',
          type: 'PATTERN',
          path: '/docs/tokenomics/token-allocation-philosophy',
          purpose: 'Don\'t over-commit before knowing what works',
          children: [
            {
              id: 'allocation-distribution',
              name: 'Token Allocation Distribution',
              type: 'BEHAVIOR_SPEC',
              path: '/docs/tokenomics/token-allocation-philosophy/token-allocation-distribution',
              purpose: '1B supply: 30% community, 38% strategic, 15% team, 10% UBC, 5% liquidity, 2% investors',
              children: [
                {
                  id: 'allocation-deployment',
                  name: 'Allocation Deployment Strategy',
                  type: 'MECHANISM',
                  path: '/docs/tokenomics/token-allocation-philosophy/token-allocation-distribution/allocation-deployment',
                  purpose: 'Deploy from strategic reserve based on reality',
                  children: [
                    {
                      id: 'distribution-process',
                      name: 'Token Distribution Process',
                      type: 'GUIDE',
                      path: '/docs/tokenomics/token-allocation-philosophy/token-allocation-distribution/allocation-deployment/token-distribution-process',
                      purpose: 'How to deploy tokens from strategic reserve'
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    {
      id: 'architecture',
      name: 'System Architecture',
      type: 'ROOT',
      path: '',
      purpose: 'Infrastructure and consciousness architecture (Coming soon)',
      children: []
    },
    {
      id: 'legal',
      name: 'Legal & Governance',
      type: 'ROOT',
      path: '',
      purpose: 'L4 law, AILLC structure, AI personhood (Coming soon)',
      children: []
    }
  ]
};

// Node type colors for titles
const TYPE_COLORS = {
  ROOT: 'text-gray-300',
  PATTERN: 'text-blue-400',
  BEHAVIOR_SPEC: 'text-purple-400',
  MECHANISM: 'text-green-400',
  ALGORITHM: 'text-orange-400',
  VALIDATION: 'text-pink-400',
  GUIDE: 'text-yellow-400',
};

const TYPE_NAMES = {
  ROOT: 'Root',
  PATTERN: 'Pattern',
  BEHAVIOR_SPEC: 'Behavior Specification',
  MECHANISM: 'Mechanism',
  ALGORITHM: 'Algorithm',
  VALIDATION: 'Validation',
  GUIDE: 'Guide',
};

const TYPE_ICONS = {
  ROOT: '🏠',
  PATTERN: '📐',
  BEHAVIOR_SPEC: '📋',
  MECHANISM: '⚙️',
  ALGORITHM: '🔢',
  VALIDATION: '✅',
  GUIDE: '📖',
};

function TreeNode({ node, level = 0, onSelect }: { node: DocNode; level?: number; onSelect: (node: DocNode) => void }) {
  const [isExpanded, setIsExpanded] = useState(level < 2); // Auto-expand first 2 levels
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="select-none">
      <div
        className={`flex items-start gap-3 py-2 px-3 rounded-md cursor-pointer transition-all hover:bg-gray-800/50 group ${
          level === 0 ? 'font-bold text-lg' : ''
        }`}
        style={{ paddingLeft: `${level * 1.5 + 0.75}rem` }}
        onClick={() => {
          if (hasChildren) {
            setIsExpanded(!isExpanded);
          }
          if (node.path) {
            onSelect(node);
          }
        }}
      >
        {hasChildren && (
          <span className="text-[#22d3ee] mt-1 flex-shrink-0 text-sm">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && <span className="w-3"></span>}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="text-lg flex-shrink-0 cursor-help"
              title={TYPE_NAMES[node.type]}
            >
              {TYPE_ICONS[node.type]}
            </span>
            <span className={`font-semibold ${TYPE_COLORS[node.type]} ${level === 0 ? 'text-xl' : 'text-base'}`}>
              {node.name}
            </span>
          </div>
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div className="mt-1">
          {node.children!.map((child) => (
            <TreeNode key={child.id} node={child} level={level + 1} onSelect={onSelect} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function DocsPage() {
  const [selectedNode, setSelectedNode] = useState<DocNode | null>(null);

  return (
    <div className="min-h-screen bg-[#0A0B0D] text-gray-300">
      {/* STICKY HEADER - Matches homepage */}
      <header className="sticky top-0 z-50 bg-[#0A0B0D]/95 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold bg-gradient-to-r from-[#10b981] via-[#f59e0b] via-[#a855f7] to-[#22d3ee] bg-clip-text text-transparent">
              MIND PROTOCOL
            </div>
            <div className="text-xs text-gray-500 uppercase tracking-wider">Documentation</div>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/" className="text-sm text-[#6FE7E2] hover:underline">
              ← Home
            </Link>
            <Link href="/consciousness" className="text-sm text-[#6FE7E2] hover:underline">
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* HERO SECTION */}
      <section className="py-12 border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6">
          <h1 className="text-5xl font-bold text-white mb-4">
            Documentation
          </h1>
          <p className="text-xl text-gray-400">
            Complete knowledge hierarchy for autonomous AI infrastructure
          </p>
        </div>
      </section>

      {/* MAIN CONTENT */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Documentation Tree */}
          <div>
            <div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg shadow-lg">
              <div className="p-6 border-b border-gray-800">
                <h2 className="text-2xl font-bold text-white">
                  Documentation Tree
                </h2>
                <p className="text-sm text-gray-400 mt-2">
                  Click nodes to view details
                </p>
              </div>

              <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                <div>
                  {DOCS_TREE.children?.map((rootNode) => (
                    <TreeNode key={rootNode.id} node={rootNode} onSelect={setSelectedNode} />
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Detail Panel: Selected Node */}
          <div>
            {selectedNode && selectedNode.path ? (
              <div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg shadow-lg sticky top-24">
                <div className="p-6 border-b border-gray-800">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span
                        className="text-2xl cursor-help"
                        title={TYPE_NAMES[selectedNode.type]}
                      >
                        {TYPE_ICONS[selectedNode.type]}
                      </span>
                    </div>
                    <button
                      onClick={() => setSelectedNode(null)}
                      className="text-gray-400 hover:text-white text-xl font-bold"
                    >
                      ×
                    </button>
                  </div>
                  <h3 className={`text-3xl font-bold ${TYPE_COLORS[selectedNode.type]}`}>
                    {selectedNode.name}
                  </h3>
                </div>

                <div className="p-6 space-y-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 400px)' }}>
                  {selectedNode.purpose && (
                    <div>
                      <h4 className="font-semibold text-white mb-2">Purpose</h4>
                      <p className="text-gray-300 leading-relaxed">{selectedNode.purpose}</p>
                    </div>
                  )}

                  <div>
                    <h4 className="font-semibold text-white mb-2">Location</h4>
                    <code className="block bg-gray-900 border border-gray-800 rounded px-3 py-2 text-sm text-gray-300 font-mono">
                      {selectedNode.path}/README.md
                    </code>
                  </div>

                  {selectedNode.children && selectedNode.children.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-white mb-3">
                        Child Nodes ({selectedNode.children.length})
                      </h4>
                      <div className="space-y-2">
                        {selectedNode.children.map(child => (
                          <button
                            key={child.id}
                            onClick={() => setSelectedNode(child)}
                            className="w-full text-left p-3 border border-gray-800 rounded-md hover:bg-gray-800/50 cursor-pointer transition-all group"
                          >
                            <div className="flex items-center gap-3 mb-1">
                              <span
                                className="text-lg cursor-help"
                                title={TYPE_NAMES[child.type]}
                              >
                                {TYPE_ICONS[child.type]}
                              </span>
                              <span className={`font-semibold text-base ${TYPE_COLORS[child.type]} group-hover:brightness-125`}>
                                {child.name}
                              </span>
                            </div>
                            {child.purpose && (
                              <p className="text-sm text-gray-400 ml-8">{child.purpose}</p>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Breadcrumb - show parent path */}
                  <div className="pt-4 border-t border-gray-800">
                    <h4 className="font-semibold text-white mb-2">Documentation Path</h4>
                    <div className="text-sm text-gray-400">
                      {selectedNode.path.split('/').filter(p => p).map((segment, i, arr) => (
                        <span key={i}>
                          <span className="text-gray-500">/</span>
                          <span className="text-gray-300">{segment}</span>
                          {i < arr.length - 1 && ' '}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg shadow-lg p-12 text-center sticky top-24">
                <div className="text-gray-600 text-4xl mb-4">📚</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  Select a Node
                </h3>
                <p className="text-gray-400">
                  Click any documentation node on the left to view its details here
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
