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

const TYPE_COLORS = {
  ROOT: 'bg-slate-100 text-slate-800 border-slate-300',
  PATTERN: 'bg-blue-100 text-blue-800 border-blue-300',
  BEHAVIOR_SPEC: 'bg-purple-100 text-purple-800 border-purple-300',
  MECHANISM: 'bg-green-100 text-green-800 border-green-300',
  ALGORITHM: 'bg-orange-100 text-orange-800 border-orange-300',
  VALIDATION: 'bg-pink-100 text-pink-800 border-pink-300',
  GUIDE: 'bg-yellow-100 text-yellow-800 border-yellow-300',
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
        className={`flex items-start gap-2 py-2 px-3 rounded-md cursor-pointer transition-all hover:bg-amber-50 ${
          level === 0 ? 'font-bold' : ''
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
          <span className="text-amber-600 mt-0.5 flex-shrink-0">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && <span className="w-4"></span>}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`px-2 py-0.5 rounded text-xs font-medium border ${TYPE_COLORS[node.type]}`}>
              {TYPE_ICONS[node.type]} {node.type}
            </span>
            <span className="text-amber-900 font-[family-name:var(--font-cinzel)]">
              {node.name}
            </span>
          </div>
          {node.purpose && (
            <p className="text-sm text-amber-700 mt-1 font-[family-name:var(--font-crimson-text)]">
              {node.purpose}
            </p>
          )}
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
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<'ALL' | DocNode['type']>('ALL');

  // Flatten tree for search
  const flattenTree = (node: DocNode, acc: DocNode[] = []): DocNode[] => {
    acc.push(node);
    if (node.children) {
      node.children.forEach(child => flattenTree(child, acc));
    }
    return acc;
  };

  const allNodes = flattenTree(DOCS_TREE);
  const filteredNodes = allNodes.filter(node => {
    const matchesSearch = searchTerm === '' ||
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (node.purpose && node.purpose.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = typeFilter === 'ALL' || node.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const stats = {
    total: allNodes.length - 1, // Exclude root
    patterns: allNodes.filter(n => n.type === 'PATTERN').length,
    specs: allNodes.filter(n => n.type === 'BEHAVIOR_SPEC').length,
    mechanisms: allNodes.filter(n => n.type === 'MECHANISM').length,
    algorithms: allNodes.filter(n => n.type === 'ALGORITHM').length,
    validations: allNodes.filter(n => n.type === 'VALIDATION').length,
    guides: allNodes.filter(n => n.type === 'GUIDE').length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50">
      {/* Header */}
      <div className="border-b border-amber-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
                Mind Protocol Documentation
              </h1>
              <p className="mt-2 text-amber-700 font-[family-name:var(--font-crimson-text)]">
                Complete knowledge hierarchy for autonomous AI infrastructure
              </p>
            </div>
            <Link href="/" className="text-sm text-amber-600 hover:text-amber-800 underline">
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar: Stats & Filters */}
          <div className="lg:col-span-1 space-y-6">
            {/* Stats */}
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 p-6 shadow-lg">
              <h2 className="text-xl font-bold text-amber-900 mb-4 font-[family-name:var(--font-cinzel)]">
                Documentation Stats
              </h2>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">Total Nodes</span>
                  <span className="text-xl font-bold text-amber-900">{stats.total}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">📐 Patterns</span>
                  <span className="font-semibold text-blue-700">{stats.patterns}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">📋 Specs</span>
                  <span className="font-semibold text-purple-700">{stats.specs}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">⚙️ Mechanisms</span>
                  <span className="font-semibold text-green-700">{stats.mechanisms}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">🔢 Algorithms</span>
                  <span className="font-semibold text-orange-700">{stats.algorithms}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">✅ Validations</span>
                  <span className="font-semibold text-pink-700">{stats.validations}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">📖 Guides</span>
                  <span className="font-semibold text-yellow-700">{stats.guides}</span>
                </div>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 p-6 shadow-lg">
              <h2 className="text-xl font-bold text-amber-900 mb-4 font-[family-name:var(--font-cinzel)]">
                Filters
              </h2>

              {/* Search */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-amber-700 mb-2">
                  Search
                </label>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Name or purpose..."
                  className="w-full px-3 py-2 border border-amber-300 rounded-md focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>

              {/* Type Filter */}
              <div>
                <label className="block text-sm font-medium text-amber-700 mb-2">
                  Node Type
                </label>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value as any)}
                  className="w-full px-3 py-2 border border-amber-300 rounded-md focus:ring-2 focus:ring-amber-500 text-sm"
                >
                  <option value="ALL">All Types</option>
                  <option value="PATTERN">📐 Patterns</option>
                  <option value="BEHAVIOR_SPEC">📋 Specifications</option>
                  <option value="MECHANISM">⚙️ Mechanisms</option>
                  <option value="ALGORITHM">🔢 Algorithms</option>
                  <option value="VALIDATION">✅ Validations</option>
                  <option value="GUIDE">📖 Guides</option>
                </select>
              </div>
            </div>

            {/* Legend */}
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 p-6 shadow-lg">
              <h2 className="text-xl font-bold text-amber-900 mb-4 font-[family-name:var(--font-cinzel)]">
                Knowledge Hierarchy
              </h2>
              <div className="space-y-2 text-xs">
                <div className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">📐</span>
                  <div>
                    <div className="font-semibold text-blue-800">PATTERN</div>
                    <div className="text-amber-700">Conceptual framework</div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-purple-600 font-bold">📋</span>
                  <div>
                    <div className="font-semibold text-purple-800">BEHAVIOR_SPEC</div>
                    <div className="text-amber-700">What should happen</div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-green-600 font-bold">⚙️</span>
                  <div>
                    <div className="font-semibold text-green-800">MECHANISM</div>
                    <div className="text-amber-700">How it works</div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-orange-600 font-bold">🔢</span>
                  <div>
                    <div className="font-semibold text-orange-800">ALGORITHM</div>
                    <div className="text-amber-700">Formulas & calculations</div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-pink-600 font-bold">✅</span>
                  <div>
                    <div className="font-semibold text-pink-800">VALIDATION</div>
                    <div className="text-amber-700">How we verify</div>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-yellow-600 font-bold">📖</span>
                  <div>
                    <div className="font-semibold text-yellow-800">GUIDE</div>
                    <div className="text-amber-700">How to implement</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content: Documentation Tree */}
          <div className="lg:col-span-3">
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 shadow-lg">
              <div className="p-6 border-b border-amber-200 bg-amber-50">
                <h2 className="text-2xl font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
                  {searchTerm || typeFilter !== 'ALL' ? 'Search Results' : 'Documentation Tree'}
                </h2>
                <p className="text-sm text-amber-700 mt-2 font-[family-name:var(--font-crimson-text)]">
                  {searchTerm || typeFilter !== 'ALL'
                    ? `Found ${filteredNodes.length} matching nodes`
                    : 'Click to expand sections • Select nodes to view details'}
                </p>
              </div>

              <div className="p-6 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                {searchTerm || typeFilter !== 'ALL' ? (
                  // Search Results View
                  <div className="space-y-2">
                    {filteredNodes.map(node => (
                      <div
                        key={node.id}
                        className="p-3 border border-amber-200 rounded-md hover:bg-amber-50 cursor-pointer transition-all"
                        onClick={() => setSelectedNode(node)}
                      >
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium border ${TYPE_COLORS[node.type]}`}>
                            {TYPE_ICONS[node.type]} {node.type}
                          </span>
                          <span className="font-semibold text-amber-900">{node.name}</span>
                        </div>
                        {node.purpose && (
                          <p className="text-sm text-amber-700 mt-1">{node.purpose}</p>
                        )}
                        {node.path && (
                          <p className="text-xs text-amber-500 mt-1 font-mono">{node.path}/README.md</p>
                        )}
                      </div>
                    ))}
                    {filteredNodes.length === 0 && (
                      <div className="text-center py-12 text-amber-600">
                        No documentation nodes match your search
                      </div>
                    )}
                  </div>
                ) : (
                  // Tree View
                  <div>
                    {DOCS_TREE.children?.map((rootNode) => (
                      <TreeNode key={rootNode.id} node={rootNode} onSelect={setSelectedNode} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Node Detail Modal */}
      {selectedNode && selectedNode.path && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedNode(null)}
        >
          <div
            className="bg-white rounded-lg border-2 border-amber-200 shadow-2xl max-w-2xl w-full p-6 max-h-[80vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`px-3 py-1 rounded text-sm font-medium border ${TYPE_COLORS[selectedNode.type]}`}>
                    {TYPE_ICONS[selectedNode.type]} {selectedNode.type}
                  </span>
                </div>
                <h3 className="text-2xl font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
                  {selectedNode.name}
                </h3>
              </div>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-amber-600 hover:text-amber-800 text-2xl font-bold"
              >
                ×
              </button>
            </div>

            <div className="space-y-4">
              {selectedNode.purpose && (
                <div>
                  <h4 className="font-semibold text-amber-900 mb-2 font-[family-name:var(--font-cinzel)]">Purpose</h4>
                  <p className="text-amber-800 font-[family-name:var(--font-crimson-text)]">{selectedNode.purpose}</p>
                </div>
              )}

              <div>
                <h4 className="font-semibold text-amber-900 mb-2 font-[family-name:var(--font-cinzel)]">File Path</h4>
                <code className="block bg-amber-50 border border-amber-200 rounded px-3 py-2 text-sm text-amber-900 font-mono">
                  {selectedNode.path}/README.md
                </code>
              </div>

              {selectedNode.children && selectedNode.children.length > 0 && (
                <div>
                  <h4 className="font-semibold text-amber-900 mb-2 font-[family-name:var(--font-cinzel)]">
                    Child Nodes ({selectedNode.children.length})
                  </h4>
                  <div className="space-y-2">
                    {selectedNode.children.map(child => (
                      <div key={child.id} className="flex items-center gap-2 text-sm">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${TYPE_COLORS[child.type]}`}>
                          {TYPE_ICONS[child.type]}
                        </span>
                        <span className="text-amber-800">{child.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="pt-4 border-t border-amber-200">
                <a
                  href={`https://github.com/mind-protocol/mindprotocol/tree/main${selectedNode.path}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-amber-600 text-white rounded-md hover:bg-amber-700 transition-colors font-[family-name:var(--font-cinzel)]"
                >
                  View on GitHub →
                </a>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
