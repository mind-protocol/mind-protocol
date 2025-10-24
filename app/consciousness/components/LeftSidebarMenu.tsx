/**
 * LeftSidebarMenu - Organized collapsible panel menu
 *
 * Groups all left-side consciousness monitoring panels into
 * a clean, collapsible accordion interface.
 *
 * Sections:
 * - Affective Systems (emotion regulation, telemetry, coupling)
 * - Consciousness Rhythms (tick timeline, autonomy indicator)
 * - Exploration Dynamics (fanout strategy, task mode influence)
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-24
 * Purpose: Organize messy absolute-positioned panels into clean UI
 */

'use client';

import { useState } from 'react';
import { CompactRegulationIndex } from './sidebar-compact/CompactRegulationIndex';
import { CompactAffectiveTelemetry } from './sidebar-compact/CompactAffectiveTelemetry';
import { CompactTickTimeline } from './sidebar-compact/CompactTickTimeline';
import { CompactAutonomy } from './sidebar-compact/CompactAutonomy';
import { CompactExploration } from './sidebar-compact/CompactExploration';
import type { V2ConsciousnessState, StrideSelectionEvent } from '../hooks/websocket-types';

interface LeftSidebarMenuProps {
  v2State: V2ConsciousnessState;
  strideSelectionEvents: StrideSelectionEvent[];
}

type Section = 'affective' | 'rhythms' | 'exploration' | null;
type SubPanel = 'regulation' | 'telemetry' | 'autonomy' | 'timeline' | null;

export function LeftSidebarMenu({ v2State, strideSelectionEvents }: LeftSidebarMenuProps) {
  const [expandedSection, setExpandedSection] = useState<Section>('affective');
  const [expandedSubPanels, setExpandedSubPanels] = useState<Set<string>>(
    new Set(['regulation', 'telemetry'])  // Start with both expanded
  );

  const toggleSection = (section: Section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const toggleSubPanel = (panel: string) => {
    setExpandedSubPanels(prev => {
      const next = new Set(prev);
      if (next.has(panel)) {
        next.delete(panel);
      } else {
        next.add(panel);
      }
      return next;
    });
  };

  return (
    <div className="fixed left-0 top-16 bottom-0 w-[20rem] consciousness-panel border-r border-observatory-teal overflow-hidden flex flex-col z-20">
      {/* Collapsible Sections */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pt-4">

        {/* Affective Systems Section */}
        <SectionAccordion
          title="Affective Systems"
          emoji="💓"
          isExpanded={expandedSection === 'affective'}
          onToggle={() => toggleSection('affective')}
        >
          <div className="bg-slate-900/30">
            <SubPanelAccordion
              title="Regulation"
              isExpanded={expandedSubPanels.has('regulation')}
              onToggle={() => toggleSubPanel('regulation')}
            >
              <CompactRegulationIndex />
            </SubPanelAccordion>

            <SubPanelAccordion
              title="Telemetry"
              isExpanded={expandedSubPanels.has('telemetry')}
              onToggle={() => toggleSubPanel('telemetry')}
            >
              <CompactAffectiveTelemetry />
            </SubPanelAccordion>
          </div>
        </SectionAccordion>

        {/* Consciousness Rhythms Section */}
        <SectionAccordion
          title="Consciousness Rhythms"
          emoji="🌊"
          isExpanded={expandedSection === 'rhythms'}
          onToggle={() => toggleSection('rhythms')}
        >
          <div className="space-y-4 p-4 bg-slate-900/30">
            <div className="pb-3 border-b border-slate-800">
              <div className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide">
                Autonomy
              </div>
              <CompactAutonomy frameEvents={v2State.frameEvents} />
            </div>

            <div>
              <div className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wide">
                Tick Timeline
              </div>
              <CompactTickTimeline frameEvents={v2State.frameEvents} />
            </div>
          </div>
        </SectionAccordion>

        {/* Exploration Dynamics Section */}
        <SectionAccordion
          title="Exploration Dynamics"
          emoji="🧭"
          isExpanded={expandedSection === 'exploration'}
          onToggle={() => toggleSection('exploration')}
        >
          <div className="space-y-4 p-4 bg-slate-900/30">
            <CompactExploration strideSelectionEvents={strideSelectionEvents} />
          </div>
        </SectionAccordion>

      </div>
    </div>
  );
}

function SectionAccordion({
  title,
  emoji,
  isExpanded,
  onToggle,
  children
}: {
  title: string;
  emoji: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-observatory-teal/20">
      {/* Section Header */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-observatory-cyan/10 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{emoji}</span>
          <span className="text-sm font-semibold text-observatory-text/90 uppercase tracking-wide">
            {title}
          </span>
        </div>
        <span className="text-observatory-text/70 text-xs">
          {isExpanded ? '▼' : '▶'}
        </span>
      </button>

      {/* Section Content */}
      {isExpanded && (
        <div className="border-t border-observatory-teal/10">
          {children}
        </div>
      )}
    </div>
  );
}

function SubPanelAccordion({
  title,
  isExpanded,
  onToggle,
  children
}: {
  title: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border-b border-slate-800/50">
      {/* Sub-Panel Header */}
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-800/30 transition-colors"
      >
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
          {title}
        </span>
        <span className="text-slate-500 text-xs">
          {isExpanded ? '▼' : '▶'}
        </span>
      </button>

      {/* Sub-Panel Content */}
      {isExpanded && (
        <div className="px-4 pb-4">
          {children}
        </div>
      )}
    </div>
  );
}
