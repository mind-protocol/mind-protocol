'use client';

import { useState, useMemo } from 'react';
import type { Node } from '../hooks/useGraphData';

interface SearchBarProps {
  nodes: Node[];
}

/**
 * SearchBar Component
 *
 * Search and filter nodes by text content.
 * Displays results and allows zooming to specific node.
 */
export function SearchBar({ nodes }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [focused, setFocused] = useState(false);

  const results = useMemo(() => {
    if (!query || query.length < 2) return [];

    const lowerQuery = query.toLowerCase();
    return nodes
      .filter(node => {
        const text = (node.text || node.node_id || node.id || '').toLowerCase();
        const type = ((node.labels && node.labels[0]) || '').toLowerCase();
        return text.includes(lowerQuery) || type.includes(lowerQuery);
      })
      .slice(0, 10) // Max 10 results
      .sort((a, b) => {
        // Prioritize by traversal count
        const aTraversals = a.traversal_count || 0;
        const bTraversals = b.traversal_count || 0;
        return bTraversals - aTraversals;
      });
  }, [query, nodes]);

  const handleSelectNode = (node: Node) => {
    // Emit event to zoom to node
    const event = new CustomEvent('search:select', { detail: { node } });
    window.dispatchEvent(event);
    setQuery('');
    setFocused(false);
  };

  const showResults = focused && query.length >= 2 && results.length > 0;

  return (
    <div className="relative w-full">
      {/* Search Input */}
      <div className="consciousness-panel px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setTimeout(() => setFocused(false), 200)}
            placeholder="Search nodes..."
            className="flex-1 bg-transparent text-white placeholder-gray-500 focus:outline-none"
          />
          {query && (
            <button
              onClick={() => {
                setQuery('');
                setFocused(false);
              }}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Results Dropdown */}
      {showResults && (
        <div className="absolute top-full left-0 right-0 consciousness-panel mt-2 max-h-80 overflow-y-auto custom-scrollbar z-50">
          <div className="py-2">
            {results.map((node, index) => (
              <button
                key={node.id}
                onClick={() => handleSelectNode(node)}
                className="w-full px-4 py-3 hover:bg-consciousness-green/10 transition-colors text-left"
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">
                    {getNodeEmoji(node)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-200 truncate">
                      {node.text || node.node_id || node.id}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {(node.labels && node.labels[0]) || 'Node'}
                      {node.traversal_count ? ` • ${node.traversal_count} traversals` : ''}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Show count */}
          <div className="px-4 py-2 border-t border-consciousness-border text-xs text-gray-500">
            {results.length} result{results.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}

      {/* No results */}
      {focused && query.length >= 2 && results.length === 0 && (
        <div className="consciousness-panel mt-2 px-4 py-3">
          <div className="text-sm text-gray-400 text-center">
            No nodes found matching "{query}"
          </div>
        </div>
      )}
    </div>
  );
}

function getNodeEmoji(node: Node): string {
  const nodeType = (node.labels && node.labels[0]) || 'Node';
  const EMOJIS: Record<string, string> = {
    // N1 - Personal/Individual Consciousness
    'Memory': '💭',
    'Conversation': '💬',
    'Person': '👤',
    'Relationship': '🤝',
    'Personal_Goal': '🎯',
    'Personal_Value': '💎',
    'Personal_Pattern': '🔄',
    'Realization': '💡',
    'Wound': '🩹',
    'Coping_Mechanism': '🛡️',
    'Trigger': '⚡',
    // N2 - Organizational Consciousness
    'Human': '🧑',
    'AI_Agent': '🤖',
    'Team': '👥',
    'Department': '🏢',
    'Decision': '⚖️',
    'Project': '📋',
    'Task': '✅',
    'Milestone': '🏆',
    'Best_Practice': '✨',
    'Anti_Pattern': '⚠️',
    'Risk': '🔴',
    'Metric': '📊',
    'Process': '⚙️',
    // N2/N3 - Conceptual Knowledge
    'Concept': '🧩',
    'Principle': '📜',
    'Mechanism': '🔧',
    'Document': '📄',
    'Documentation': '📖',
    // N3 - Ecosystem Intelligence (External)
    'Company': '🏛️',
    'External_Person': '👔',
    'Wallet_Address': '💰',
    'Social_Media_Account': '📱',
    // N3 - Evidence Nodes
    'Post': '📝',
    'Transaction': '💸',
    'Deal': '🤝',
    'Event': '📅',
    'Smart_Contract': '📜',
    'Integration': '🔗',
    // N3 - Derived Intelligence
    'Psychological_Trait': '🧠',
    'Behavioral_Pattern': '🔁',
    'Market_Signal': '📈',
    'Reputation_Assessment': '⭐',
    'Network_Cluster': '🕸️',
    // Fallback
    'default': '⚪'
  };
  return EMOJIS[nodeType] || EMOJIS['default'];
}
