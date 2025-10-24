'use client';

import { useState, useEffect } from 'react';
import type { Node } from '../hooks/useGraphData';

interface SearchBarProps {
  nodes: Node[];
  currentGraphId?: string | null;
}

interface SemanticResult {
  name: string;
  description: string;
  type: string;
  similarity: number;
  embeddable_text?: string;
}

/**
 * SearchBar Component
 *
 * Semantic search using vector similarity.
 * Enables conceptual queries like "spreading activation" to find related nodes.
 *
 * Author: Iris "The Aperture" - Modified 2025-10-24
 * Feature: Vector search integration for semantic exploration
 */
export function SearchBar({ nodes, currentGraphId }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [focused, setFocused] = useState(false);
  const [results, setResults] = useState<SemanticResult[]>([]);
  const [loading, setLoading] = useState(false);

  // Debounced semantic search
  useEffect(() => {
    if (!query || query.length < 3 || !currentGraphId) {
      setResults([]);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `/api/search/semantic?query=${encodeURIComponent(query)}&graph_id=${encodeURIComponent(currentGraphId)}&limit=10&threshold=0.60`
        );

        if (response.ok) {
          const data = await response.json();
          setResults(data.results || []);
        } else {
          console.error('[SearchBar] Semantic search failed:', response.status);
          setResults([]);
        }
      } catch (error) {
        console.error('[SearchBar] Semantic search error:', error);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [query, currentGraphId]);

  const handleSelectResult = (result: SemanticResult) => {
    // Find the actual node object by name
    const node = nodes.find(n => n.id === result.name || n.node_id === result.name);
    if (node) {
      // Emit event to zoom to node
      const event = new CustomEvent('search:select', { detail: { node } });
      window.dispatchEvent(event);
    }
    setQuery('');
    setFocused(false);
  };

  const showResults = focused && query.length >= 3;

  return (
    <div className="relative w-full">
      {/* Search Input */}
      <div className="consciousness-panel px-4 py-2">
        <div className="flex items-center gap-2">
          <span className="text-observatory-cyan">🔍</span>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setFocused(true)}
            onBlur={() => setTimeout(() => setFocused(false), 200)}
            placeholder="Semantic search (e.g., 'spreading activation')..."
            className="flex-1 bg-transparent text-observatory-text placeholder-observatory-text/40 focus:outline-none text-sm"
          />
          {loading && (
            <span className="text-observatory-cyan/60 text-xs">Searching...</span>
          )}
          {query && !loading && (
            <button
              onClick={() => {
                setQuery('');
                setFocused(false);
                setResults([]);
              }}
              className="text-observatory-text/60 hover:text-observatory-text transition-colors"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Results Dropdown */}
      {showResults && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 consciousness-panel mt-2 max-h-80 overflow-y-auto custom-scrollbar z-50">
          <div className="py-2">
            {results.map((result, index) => (
              <button
                key={`${result.name}-${index}`}
                onClick={() => handleSelectResult(result)}
                className="w-full px-4 py-3 hover:bg-observatory-cyan/10 transition-colors text-left"
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">
                    {getNodeEmoji(result.type || '')}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm font-medium text-observatory-text truncate flex-1">
                        {result.description || result.name}
                      </div>
                      <div className="text-xs font-mono text-consciousness-green">
                        {(result.similarity * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="text-xs text-observatory-text/60 mt-1">
                      {result.type || 'Node'}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Show count */}
          <div className="px-4 py-2 border-t border-observatory-teal/30 text-xs text-observatory-text/50">
            {results.length} semantic match{results.length !== 1 ? 'es' : ''}
          </div>
        </div>
      )}

      {/* No results */}
      {showResults && !loading && results.length === 0 && (
        <div className="consciousness-panel mt-2 px-4 py-3">
          <div className="text-sm text-observatory-text/60 text-center">
            No semantic matches for "{query}"
          </div>
        </div>
      )}
    </div>
  );
}

function getNodeEmoji(nodeType: string): string {
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
