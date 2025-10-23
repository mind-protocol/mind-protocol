'use client';

import { useState, useRef, useEffect } from 'react';
import type { Node, Link } from '../hooks/useGraphData';

interface GraphChatInterfaceProps {
  nodes: Node[];
  links: Link[];
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

/**
 * GraphChatInterface
 *
 * Bottom-right chat interface for asking questions about the graph.
 * Has access to most recent/weighted nodes for context.
 *
 * Design: Collapsible, minimal, appears on demand.
 * Natural language Q&A about consciousness state.
 */
export function GraphChatInterface({ nodes, links }: GraphChatInterfaceProps) {
  const [expanded, setExpanded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Get graph context (top weighted nodes)
    const context = getGraphContext(nodes, links);

    try {
      // TODO: Implement actual API call to consciousness-aware LLM
      // For now, provide mock response based on graph state
      const response = await mockGraphQuery(input, context);

      const assistantMessage: Message = {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: response,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: `${Date.now()}-error`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Collapsed state - chat button */}
      {!expanded && (
        <button
          onClick={() => setExpanded(true)}
          className="consciousness-panel px-4 py-3 rounded-full
                   hover:bg-consciousness-green/10 transition-colors
                   flex items-center gap-2"
        >
          <span className="text-2xl">💬</span>
          <span className="text-sm text-gray-400">Ask about the graph</span>
        </button>
      )}

      {/* Expanded state - chat interface */}
      {expanded && (
        <div className="consciousness-panel w-96 h-[500px] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-consciousness-border">
            <h3 className="text-consciousness-green font-semibold">Graph Query</h3>
            <button
              onClick={() => setExpanded(false)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {messages.length === 0 && (
              <div className="text-gray-500 text-sm text-center mt-8">
                <p>Ask questions about the consciousness state:</p>
                <ul className="mt-3 space-y-1 text-xs text-left">
                  <li>• "Which subentity is most active?"</li>
                  <li>• "What are the strongest connections?"</li>
                  <li>• "Show me high-energy clusters"</li>
                  <li>• "What's the current focus?"</li>
                </ul>
              </div>
            )}

            {messages.map(message => (
              <div
                key={message.id}
                className={`${message.role === 'user' ? 'text-right' : 'text-left'}`}
              >
                <div
                  className={`inline-block px-3 py-2 rounded-lg text-sm max-w-[80%]
                           ${message.role === 'user'
                             ? 'bg-consciousness-green/20 text-consciousness-green'
                             : 'bg-gray-800 text-gray-200'
                           }`}
                >
                  {message.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="text-left">
                <div className="inline-block px-3 py-2 rounded-lg text-sm bg-gray-800 text-gray-400">
                  Thinking...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t border-consciousness-border">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question..."
                className="flex-1 bg-gray-800 text-white px-3 py-2 rounded-lg text-sm
                         focus:outline-none focus:ring-2 focus:ring-consciousness-green/50"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="px-4 py-2 bg-consciousness-green/20 text-consciousness-green rounded-lg
                         hover:bg-consciousness-green/30 transition-colors disabled:opacity-50
                         disabled:cursor-not-allowed text-sm font-medium"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Graph Context & Query Logic
// ============================================================================

function getGraphContext(nodes: Node[], links: Link[], limit = 20) {
  // Get top weighted nodes for context
  const weightedNodes = nodes
    .map(node => ({
      ...node,
      weight: computeNodeWeight(node)
    }))
    .sort((a, b) => b.weight - a.weight)
    .slice(0, limit);

  return {
    nodeCount: nodes.length,
    linkCount: links.length,
    topNodes: weightedNodes.map(n => ({
      id: n.id,
      text: n.text,
      // Use node_type instead of labels[0] (FalkorDB returns labels as string)
      type: n.node_type,
      weight: n.weight
    })),
    subentities: extractSubentities(nodes)
  };
}

function computeNodeWeight(node: Node): number {
  const energy = node.energy || 0;
  const confidence = node.confidence || 0.5;
  const traversalCount = node.traversal_count || 0;
  const normalizedTraversals = Math.min(1.0, Math.log10(traversalCount + 1) / 2);
  return (energy * 0.4) + (confidence * 0.3) + (normalizedTraversals * 0.3);
}

function extractSubentities(nodes: Node[]): string[] {
  const entitySet = new Set<string>();
  nodes.forEach(node => {
    if (node.entity_activations) {
      Object.keys(node.entity_activations).forEach(id => entitySet.add(id));
    }
  });
  return Array.from(entitySet);
}

async function mockGraphQuery(query: string, context: any): Promise<string> {
  // Mock response based on query keywords
  const lowerQuery = query.toLowerCase();

  if (lowerQuery.includes('most active') || lowerQuery.includes('which subentity')) {
    const subentities = context.subentities;
    if (subentities.length > 0) {
      return `Based on current activity, ${subentities[0]} appears to be the most active subentity in the graph.`;
    }
    return "No subentities are currently active in the graph.";
  }

  if (lowerQuery.includes('strongest') || lowerQuery.includes('connections')) {
    return `The graph has ${context.linkCount} connections. The strongest paths are typically between high-weight nodes.`;
  }

  if (lowerQuery.includes('high-energy') || lowerQuery.includes('clusters')) {
    const topNodes = context.topNodes.slice(0, 3);
    if (topNodes.length > 0) {
      const nodeList = topNodes.map((n: any) => `"${n.text}"`).join(', ');
      return `High-energy nodes include: ${nodeList}`;
    }
    return "No high-energy clusters detected at the moment.";
  }

  if (lowerQuery.includes('focus') || lowerQuery.includes('current')) {
    const topNode = context.topNodes[0];
    if (topNode) {
      return `Current focus appears to be on: "${topNode.text}" (${topNode.type})`;
    }
    return "No clear focus detected in the current state.";
  }

  // Default response
  return `The graph contains ${context.nodeCount} nodes and ${context.linkCount} links. ${context.subentities.length} subentities are active.`;
}
