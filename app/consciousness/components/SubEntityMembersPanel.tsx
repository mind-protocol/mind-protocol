/**
 * SubEntity Members Panel - P1 Membership Display
 *
 * Shows nodes that belong to a subentity via MEMBER_OF relationships.
 * Consumes P1 membership API with pagination and filtering.
 *
 * Features:
 * - Live member list from P1 API
 * - Membership weights and roles
 * - Type filtering
 * - Load more pagination
 * - Click to focus node in graph
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-25
 * Priority: P1 SubEntity Layer Observability
 */

'use client';

import { useState, useEffect } from 'react';
import { normalizeNodeType } from '../utils/normalizeEvents';

interface SubEntityMember {
  name: string;
  type: string;
  membership_weight: number;
  membership_role: string;
}

interface SubEntityMembersResponse {
  subentity_id: string;
  subentity_name: string;
  graph_name: string;
  member_count: number;
  members: SubEntityMember[];
}

interface SubEntityMembersPanelProps {
  subentityId: string;
  subentityName: string;
  graphId: string;
  onFocusNode?: (nodeId: string) => void;
}

export function SubEntityMembersPanel({
  subentityId,
  subentityName,
  graphId,
  onFocusNode
}: SubEntityMembersPanelProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SubEntityMembersResponse | null>(null);
  const [limit, setLimit] = useState(20);

  useEffect(() => {
    const fetchMembers = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch(
          `/api/subentity/${subentityName}/members?limit=${limit}`
        );

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const responseData = await response.json();
        setData(responseData);
      } catch (err) {
        console.error('[SubEntityMembersPanel] Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load members');
      } finally {
        setLoading(false);
      }
    };

    fetchMembers();
  }, [subentityName, limit]);

  const handleLoadMore = () => {
    setLimit(prev => prev + 20);
  };

  const handleMemberClick = (memberName: string) => {
    if (onFocusNode) {
      onFocusNode(memberName);
    }

    // Also emit event for graph visualization
    const event = new CustomEvent('node:focus', {
      detail: { nodeId: memberName }
    });
    window.dispatchEvent(event);
  };

  if (loading && !data) {
    return (
      <div className="consciousness-panel p-4">
        <div className="text-sm text-observatory-text/60 text-center py-4">
          Loading members...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="consciousness-panel p-4">
        <div className="text-sm text-red-400 text-center py-4">
          Error: {error}
        </div>
      </div>
    );
  }

  if (!data || data.members.length === 0) {
    return (
      <div className="consciousness-panel p-4">
        <div className="text-sm text-observatory-text/60 text-center py-4">
          No members found for {subentityName}
        </div>
      </div>
    );
  }

  return (
    <div className="consciousness-panel">
      {/* Header */}
      <div className="border-b border-observatory-teal/30 p-4">
        <h3 className="text-sm font-semibold text-observatory-cyan uppercase tracking-wide">
          {subentityName}
        </h3>
        <div className="text-xs text-observatory-text/60 mt-1">
          {data.member_count} member{data.member_count !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Members List */}
      <div className="max-h-[60vh] overflow-y-auto custom-scrollbar">
        {data.members.map((member, idx) => (
          <button
            key={`${member.name}-${idx}`}
            onClick={() => handleMemberClick(member.name)}
            className="w-full px-4 py-3 hover:bg-observatory-cyan/10 transition-colors text-left border-b border-observatory-teal/20 last:border-b-0"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                {/* Node name */}
                <div className="text-sm font-medium text-observatory-text truncate">
                  {member.name}
                </div>

                {/* Node type */}
                <div className="text-xs text-observatory-text/60 mt-0.5">
                  {normalizeNodeType(member.type)}
                </div>
              </div>

              {/* Membership weight */}
              <div className="flex-shrink-0">
                <div className="text-xs font-mono text-consciousness-green">
                  {(member.membership_weight * 100).toFixed(0)}%
                </div>
                {member.membership_role && member.membership_role !== 'unknown' && (
                  <div className="text-xs text-observatory-text/50 mt-0.5">
                    {member.membership_role}
                  </div>
                )}
              </div>
            </div>

            {/* Membership strength indicator */}
            <div className="mt-2 h-1 bg-observatory-teal/20 rounded overflow-hidden">
              <div
                className="h-full bg-consciousness-green transition-all"
                style={{ width: `${member.membership_weight * 100}%` }}
              />
            </div>
          </button>
        ))}
      </div>

      {/* Load More */}
      {data.members.length < data.member_count && (
        <div className="border-t border-observatory-teal/30 p-4">
          <button
            onClick={handleLoadMore}
            disabled={loading}
            className="w-full px-4 py-2 text-sm font-medium text-observatory-cyan hover:bg-observatory-cyan/10 transition-colors rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Loading...' : `Load More (${data.member_count - data.members.length} remaining)`}
          </button>
        </div>
      )}

      {/* Footer Stats */}
      <div className="border-t border-observatory-teal/30 p-4">
        <div className="text-xs text-observatory-text/50">
          Showing {data.members.length} of {data.member_count} members
        </div>
      </div>
    </div>
  );
}
