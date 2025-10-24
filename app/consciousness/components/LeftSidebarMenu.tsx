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
import { InstrumentPanel } from './InstrumentPanel';
import { AffectiveTelemetryPanel } from './AffectiveTelemetryPanel';
import { AffectiveCouplingPanel } from './AffectiveCouplingPanel';
import ThreeFactorTickTimeline from './ThreeFactorTickTimeline';
import AutonomyIndicator from './AutonomyIndicator';
import FanoutStrategyPanel from './FanoutStrategyPanel';
import TaskModeInfluencePanel from './TaskModeInfluencePanel';
import type { V2ConsciousnessState } from '../hooks/websocket-types';
import type { FrameStartEvent, StrideSelectionEvent } from '../hooks/websocket-types';

interface LeftSidebarMenuProps {
  v2State: V2ConsciousnessState;
  strideSelectionEvents: StrideSelectionEvent[];
}

type Section = 'affective' | 'rhythms' | 'exploration' | null;

export function LeftSidebarMenu({ v2State, strideSelectionEvents }: LeftSidebarMenuProps) {
  const [expandedSection, setExpandedSection] = useState<Section>('affective');

  const toggleSection = (section: Section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="fixed left-0 top-16 bottom-0 w-[28rem] consciousness-panel border-r border-observatory-teal overflow-hidden flex flex-col z-20">
      {/* Collapsible Sections */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pt-4">

        {/* Affective Systems Section */}
        <SectionAccordion
          title="Affective Systems"
          emoji="💓"
          isExpanded={expandedSection === 'affective'}
          onToggle={() => toggleSection('affective')}
        >
          <div className="space-y-4 p-4">
            <InstrumentPanel />
            <AffectiveTelemetryPanel />
            <AffectiveCouplingPanel />
          </div>
        </SectionAccordion>

        {/* Consciousness Rhythms Section */}
        <SectionAccordion
          title="Consciousness Rhythms"
          emoji="🌊"
          isExpanded={expandedSection === 'rhythms'}
          onToggle={() => toggleSection('rhythms')}
        >
          <div className="space-y-4 p-4">
            <AutonomyIndicator frameEvents={v2State.frameEvents} />
            <ThreeFactorTickTimeline frameEvents={v2State.frameEvents} />
          </div>
        </SectionAccordion>

        {/* Exploration Dynamics Section */}
        <SectionAccordion
          title="Exploration Dynamics"
          emoji="🧭"
          isExpanded={expandedSection === 'exploration'}
          onToggle={() => toggleSection('exploration')}
        >
          <div className="space-y-4 p-4">
            <FanoutStrategyPanel strideSelectionEvents={strideSelectionEvents} />
            <TaskModeInfluencePanel strideSelectionEvents={strideSelectionEvents} />
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
