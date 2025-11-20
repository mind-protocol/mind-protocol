'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

// Documentation tree structure
interface DocNode {
  id: string;
  name: string;
  type: 'ROOT' | 'PATTERN' | 'BEHAVIOR_SPEC' | 'MECHANISM' | 'ALGORITHM' | 'VALIDATION' | 'GUIDE';
  path: string;
  purpose?: string;
  children?: DocNode[];
  content?: string; // Loaded markdown content
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
                }
              ]
            },
            {
              id: 'financeorg-mgmt',
              name: 'FinanceOrg Two-Layer Management',
              type: 'MECHANISM',
              path: '/docs/tokenomics/two-layer-economics/financeorg-two-layer-mgmt',
              purpose: 'How financeOrg manages both economic layers',
              children: [
                {
                  id: 'how-to-manage',
                  name: 'How to Manage Both Layers',
                  type: 'GUIDE',
                  path: '/docs/tokenomics/two-layer-economics/financeorg-two-layer-mgmt/how-to-manage-both-layers',
                  purpose: 'Step-by-step guide for dual-layer economic management'
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
                    },
                    {
                      id: 'trust-score-calc',
                      name: 'Trust Score Calculation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/organism-economics/pricing-evolution/formula-application/trust-score-calculation',
                      purpose: 'Calculate customer trust scores'
                    },
                    {
                      id: 'utility-rebate',
                      name: 'Utility Rebate Calculation',
                      type: 'ALGORITHM',
                      path: '/docs/tokenomics/organism-economics/pricing-evolution/formula-application/utility-rebate-calculation',
                      purpose: 'Calculate ecosystem contribution rebates'
                    },
                    {
                      id: 'how-to-price',
                      name: 'How to Price Services',
                      type: 'GUIDE',
                      path: '/docs/tokenomics/organism-economics/pricing-evolution/formula-application/how-to-price-services',
                      purpose: 'Complete guide to implementing organism economics pricing'
                    }
                  ]
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
                    },
                    {
                      id: 'how-to-allocate-ubc',
                      name: 'How to Allocate UBC',
                      type: 'GUIDE',
                      path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-distribution/how-to-allocate-ubc',
                      purpose: 'Step-by-step guide for UBC allocation'
                    }
                  ]
                },
                {
                  id: 'ubc-sustainability',
                  name: 'UBC Sustainability Tests',
                  type: 'VALIDATION',
                  path: '/docs/tokenomics/universal-basic-compute/ubc-allocation/ubc-sustainability-tests',
                  purpose: 'Verify UBC reserve lifespan across scenarios'
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

// Strip metadata envelope from markdown content
function stripEnvelope(markdown: string): string {
  // Remove everything up to and including the "---" after Purpose section
  // The content we want starts after the metadata sections

  // Split by "---" separators
  const parts = markdown.split(/^---$/m);

  if (parts.length < 5) {
    // If structure is unexpected, return everything after first heading
    const lines = markdown.split('\n');
    const firstHeadingIndex = lines.findIndex(line => line.startsWith('## '));
    return firstHeadingIndex >= 0 ? lines.slice(firstHeadingIndex).join('\n') : markdown;
  }

  // Skip: [0] = title + metadata, [1] = navigation, [2] = relationships, [3] = purpose
  // Keep: [4] = actual content onwards (Core Insight, Pattern Description, etc.)
  return parts.slice(4).join('---').trim();
}

function ContentNode({
  node,
  level = 0,
  expandedNodes,
  toggleExpanded
}: {
  node: DocNode;
  level?: number;
  expandedNodes: Record<string, boolean>;
  toggleExpanded: (id: string) => void;
}) {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const isExpanded = expandedNodes[node.id] ?? false;
  const hasChildren = node.children && node.children.length > 0;

  // Load markdown content from file
  useEffect(() => {
    if (node.path) {
      // Fetch directly from public directory
      fetch(`${node.path}/README.md`)
        .then(res => {
          if (res.ok) return res.text();
          throw new Error('File not found');
        })
        .then(text => {
          setContent(text);
          setLoading(false);
        })
        .catch(err => {
          console.error('Failed to load content:', err);
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, [node.path]);

  return (
    <div id={node.id} className={`${level === 0 ? 'mb-12' : 'mb-6'}`}>
      {/* Node Header */}
      <div className={`${level === 0 ? 'mb-6' : 'mb-4'}`}>
        <div className="flex items-center gap-3 mb-3">
          {/* Chevron for collapsing (only show if has children or content) */}
          {(hasChildren || node.path) && (
            <button
              onClick={() => toggleExpanded(node.id)}
              className="text-[#22d3ee] hover:text-[#6FE7E2] transition-colors flex-shrink-0"
              title={isExpanded ? 'Collapse' : 'Expand'}
            >
              <span className={`${level === 0 ? 'text-2xl' : level === 1 ? 'text-xl' : 'text-lg'}`}>
                {isExpanded ? '▼' : '▶'}
              </span>
            </button>
          )}
          <span
            className={`${level === 0 ? 'text-3xl' : level === 1 ? 'text-2xl' : 'text-xl'} flex-shrink-0 cursor-help`}
            title={TYPE_NAMES[node.type]}
          >
            {TYPE_ICONS[node.type]}
          </span>
          <h2 className={`font-bold ${TYPE_COLORS[node.type]} ${
            level === 0 ? 'text-4xl' : level === 1 ? 'text-3xl' : 'text-2xl'
          }`}>
            {node.name}
          </h2>
        </div>

        {node.purpose && (
          <p className={`text-gray-300 leading-relaxed ${level === 0 ? 'text-lg' : 'text-base'}`}>
            {node.purpose}
          </p>
        )}
      </div>

      {/* Markdown Content */}
      {node.path && isExpanded && (
        <div className="mb-8">
          {loading ? (
            <div className="text-sm text-gray-500 italic">Loading content...</div>
          ) : content ? (
            <div className="bg-[#0a0a0f]/50 border border-gray-800 rounded-lg p-8">
              <div className="prose prose-invert prose-lg max-w-none
                prose-headings:text-white prose-headings:font-semibold prose-headings:tracking-tight
                prose-h1:text-2xl prose-h1:mb-4 prose-h1:mt-0
                prose-h2:text-xl prose-h2:mb-3 prose-h2:mt-6
                prose-h3:text-lg prose-h3:mb-2 prose-h3:mt-4
                prose-p:text-gray-200 prose-p:leading-relaxed prose-p:my-3
                prose-ul:text-gray-200 prose-ul:my-3 prose-ul:space-y-1
                prose-ol:text-gray-200 prose-ol:my-3 prose-ol:space-y-1
                prose-li:text-gray-200 prose-li:my-0
                prose-strong:text-white prose-strong:font-semibold
                prose-code:text-[#22d3ee] prose-code:bg-gray-900/50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:font-mono
                prose-pre:bg-gray-900/80 prose-pre:border prose-pre:border-gray-700/50 prose-pre:p-4 prose-pre:rounded-lg prose-pre:overflow-x-auto
                prose-a:text-[#22d3ee] prose-a:no-underline hover:prose-a:underline hover:prose-a:text-[#6FE7E2]
                prose-blockquote:border-l-4 prose-blockquote:border-l-[#22d3ee] prose-blockquote:pl-4 prose-blockquote:italic prose-blockquote:text-gray-300
                prose-hr:border-gray-700 prose-hr:my-6">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {stripEnvelope(content)}
                </ReactMarkdown>
              </div>
            </div>
          ) : null}
        </div>
      )}

      {/* Children - Conditionally Expanded, No Indentation */}
      {hasChildren && isExpanded && (
        <div className="space-y-8 mt-8">
          {node.children!.map((child) => (
            <ContentNode
              key={child.id}
              node={child}
              level={level + 1}
              expandedNodes={expandedNodes}
              toggleExpanded={toggleExpanded}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Navigation tree node (simplified, just for navigation)
function NavNode({
  node,
  level = 0,
  onNavigate,
  expandedNodes,
  toggleExpanded
}: {
  node: DocNode;
  level?: number;
  onNavigate: (id: string) => void;
  expandedNodes: Record<string, boolean>;
  toggleExpanded: (id: string) => void;
}) {
  const isExpanded = expandedNodes[node.id] ?? false;
  const hasChildren = node.children && node.children.length > 0;

  return (
    <div className="select-none">
      <div
        className={`flex items-start gap-2 py-1.5 px-2 rounded cursor-pointer transition-all hover:bg-gray-800/50 ${
          level === 0 ? 'font-semibold' : ''
        }`}
        style={{ paddingLeft: `${level * 1 + 0.5}rem` }}
        onClick={() => {
          if (hasChildren) toggleExpanded(node.id);
          onNavigate(node.id);
        }}
      >
        {hasChildren && (
          <span className="text-[#22d3ee] mt-0.5 flex-shrink-0 text-xs">
            {isExpanded ? '▼' : '▶'}
          </span>
        )}
        {!hasChildren && <span className="w-3"></span>}

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm" title={TYPE_NAMES[node.type]}>
              {TYPE_ICONS[node.type]}
            </span>
            <span className={`text-sm ${TYPE_COLORS[node.type]}`}>
              {node.name}
            </span>
          </div>
        </div>
      </div>

      {hasChildren && isExpanded && (
        <div>
          {node.children!.map((child) => (
            <NavNode
              key={child.id}
              node={child}
              level={level + 1}
              onNavigate={onNavigate}
              expandedNodes={expandedNodes}
              toggleExpanded={toggleExpanded}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// Helper to initialize expanded state for all nodes
function initializeExpandedState(node: DocNode, expandedMap: Record<string, boolean> = {}): Record<string, boolean> {
  // Expand PATTERNS, BEHAVIOR_SPECS, MECHANISMS, and ROOT by default
  expandedMap[node.id] = node.type === 'PATTERN' ||
                          node.type === 'BEHAVIOR_SPEC' ||
                          node.type === 'MECHANISM' ||
                          node.type === 'ROOT';

  if (node.children) {
    node.children.forEach(child => initializeExpandedState(child, expandedMap));
  }

  return expandedMap;
}

export default function DocsPage() {
  const [isNavCollapsed, setIsNavCollapsed] = useState(false);
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>(() =>
    initializeExpandedState(DOCS_TREE)
  );

  const toggleExpanded = (id: string) => {
    setExpandedNodes(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleNavigate = (id: string) => {
    // Expand the node if it's collapsed
    setExpandedNodes(prev => ({ ...prev, [id]: true }));

    // Scroll to the element
    setTimeout(() => {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 100); // Small delay to allow expansion animation
  };

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

      {/* MAIN CONTENT - Two Column Layout */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex gap-8">
          {/* Left Navigation - Collapsible */}
          {!isNavCollapsed && (
            <div className="w-80 flex-shrink-0">
              <div className="sticky top-24">
                <div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg p-4 shadow-lg">
                  <div className="flex items-center justify-between mb-3 px-2">
                    <h2 className="text-sm font-bold text-white">Navigation</h2>
                    <button
                      onClick={() => setIsNavCollapsed(true)}
                      className="text-gray-400 hover:text-white text-xs px-2 py-1 rounded hover:bg-gray-800 transition-colors"
                      title="Collapse navigation"
                    >
                      ◀
                    </button>
                  </div>
                  <div className="space-y-1 overflow-y-auto" style={{ maxHeight: 'calc(100vh - 300px)' }}>
                    {DOCS_TREE.children?.map((rootNode) => (
                      <NavNode
                        key={rootNode.id}
                        node={rootNode}
                        level={0}
                        onNavigate={handleNavigate}
                        expandedNodes={expandedNodes}
                        toggleExpanded={toggleExpanded}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Collapsed Navigation Toggle */}
          {isNavCollapsed && (
            <div className="fixed left-6 top-32 z-40">
              <button
                onClick={() => setIsNavCollapsed(false)}
                className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 text-gray-400 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors shadow-lg"
                title="Show navigation"
              >
                ▶ Nav
              </button>
            </div>
          )}

          {/* Right Content */}
          <div className="flex-1">
            <div className="space-y-16">
              {DOCS_TREE.children?.map((rootNode) => (
                <ContentNode
                  key={rootNode.id}
                  node={rootNode}
                  level={0}
                  expandedNodes={expandedNodes}
                  toggleExpanded={toggleExpanded}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
