'use client';

import { useEffect, useMemo, useState } from 'react';
import { ChevronDown, ChevronRight, Brain, Activity, Heart } from 'lucide-react';
import type {
  ForgedIdentityFrameEvent,
  ForgedIdentityMetricsEvent
} from '../hooks/websocket-types';

interface ForgedIdentityViewerProps {
  frames: ForgedIdentityFrameEvent[];
  metrics: Record<string, ForgedIdentityMetricsEvent>;
}

export function ForgedIdentityViewer({ frames, metrics }: ForgedIdentityViewerProps) {
  const [selectedFrame, setSelectedFrame] = useState<ForgedIdentityFrameEvent | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['preview']));

  const sortedFrames = useMemo(() => {
    if (frames.length === 0) return [];
    return [...frames].sort((a, b) => {
      const aTs = Date.parse(a.timestamp ?? '');
      const bTs = Date.parse(b.timestamp ?? '');
      if (!Number.isNaN(aTs) && !Number.isNaN(bTs)) {
        return bTs - aTs;
      }
      if (!Number.isNaN(bTs)) return 1;
      if (!Number.isNaN(aTs)) return -1;
      return b.frame_id - a.frame_id;
    });
  }, [frames]);

  useEffect(() => {
    if (sortedFrames.length === 0) {
      setSelectedFrame(null);
      return;
    }

    setSelectedFrame(prev => {
      if (!prev) {
        return sortedFrames[0];
      }
      const match = sortedFrames.find(
        frame => frame.citizen_id === prev.citizen_id && frame.frame_id === prev.frame_id
      );
      return match ?? sortedFrames[0];
    });
  }, [sortedFrames]);

  const selectedMetrics = selectedFrame
    ? metrics[selectedFrame.citizen_id] ?? null
    : null;

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  const sections = selectedFrame ? extractPromptSections(selectedFrame.full_prompt) : [];
  const emotionalState = selectedFrame ? extractEmotionalState(selectedFrame.full_prompt) : null;
  const wmNodes = selectedFrame?.wm_nodes ?? [];

  return (
    <div className="bg-slate-900 text-slate-100 rounded-lg shadow-2xl border border-slate-700 overflow-hidden w-[1100px] max-w-[95vw]">
      <div className="bg-gradient-to-r from-indigo-500/10 to-slate-900 px-6 py-4 flex items-center justify-between border-b border-slate-700/60">
        <div className="flex items-center gap-3">
          <Brain className="w-5 h-5 text-indigo-300" />
          <div>
            <h2 className="text-lg font-semibold">Forged Identity Prompts</h2>
            <p className="text-sm text-slate-300/80">
              Observe system prompts generated from current consciousness state
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-[320px,1fr] h-[640px]">
        <aside className="border-r border-slate-800 bg-slate-950/60">
          <div className="px-4 py-3 border-b border-slate-800/80 bg-slate-950/80">
            <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
              Recent Frames
            </h3>
          </div>
          <div className="overflow-y-auto h-[calc(640px-52px)]">
            {sortedFrames.length === 0 ? (
              <div className="p-6 text-center text-sm text-slate-500">
                Waiting for forged identity frames…
              </div>
            ) : (
              <div className="divide-y divide-slate-900/80">
                {sortedFrames.map(frame => {
                  const isSelected =
                    selectedFrame?.citizen_id === frame.citizen_id &&
                    selectedFrame?.frame_id === frame.frame_id;

                  return (
                    <button
                      key={`${frame.citizen_id}-${frame.frame_id}`}
                      onClick={() => setSelectedFrame(frame)}
                      className={`w-full text-left px-4 py-4 hover:bg-slate-900/90 transition ${
                        isSelected ? 'bg-slate-900/80 border-r-2 border-indigo-400/80' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between text-xs text-slate-400 uppercase font-medium tracking-wide">
                        <span>{frame.citizen_id}</span>
                        <span>{formatTimestamp(frame.timestamp)}</span>
                      </div>
                      <div className="mt-2 text-sm font-medium text-slate-100 line-clamp-2">
                        {frame.prompt_preview || frame.full_prompt.slice(0, 120)}
                      </div>
                      <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Activity className="w-3 h-3" />
                          Frame #{frame.frame_id}
                        </span>
                        <span>
                          {frame.prompt_length} chars · {frame.prompt_sections}{' '}
                          {frame.prompt_sections === 1 ? 'section' : 'sections'}
                        </span>
                        {frame.wm_nodes?.length ? (
                          <span className="flex items-center gap-1">
                            <Brain className="w-3 h-3" />
                            WM {frame.wm_nodes.length}
                          </span>
                        ) : null}
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        </aside>

        <section className="relative h-full bg-slate-900/40">
          {selectedFrame ? (
            <div className="flex flex-col h-full">
              <header className="px-6 py-4 border-b border-slate-800/70 bg-slate-900/80">
                <div className="flex justify-between items-start gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm text-slate-400 uppercase tracking-wide">
                      <span>{selectedFrame.citizen_id}</span>
                      <span>•</span>
                      <span>Stimulus: {selectedFrame.stimulus_id}</span>
                      <span>•</span>
                      <span>Frame #{selectedFrame.frame_id}</span>
                    </div>
                    <h3 className="mt-2 text-xl font-semibold text-slate-50">
                      Consciousness-Derived Prompt
                    </h3>
                    <p className="text-xs text-slate-400 mt-1">
                      Emitted at {formatTimestamp(selectedFrame.timestamp)}
                    </p>
                  </div>
                  <div className="text-right text-sm text-slate-300/80 space-y-1">
                    <div>{selectedFrame.prompt_length} characters</div>
                    <div>
                      {selectedFrame.prompt_sections}{' '}
                      {selectedFrame.prompt_sections === 1 ? 'section' : 'sections'}
                    </div>
                    <div>Tick: {selectedFrame.tick ?? '—'}</div>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div className="bg-slate-950/70 border border-slate-800/70 rounded-md px-3 py-2">
                    <div className="text-xs uppercase tracking-wide text-slate-400">Working Memory</div>
                    <div className="text-slate-200">
                      {wmNodes.length > 0 ? wmNodes.join(', ') : 'No nodes surfaced'}
                    </div>
                  </div>
                  {selectedMetrics && (
                    <div className="bg-slate-950/70 border border-slate-800/70 rounded-md px-3 py-2 text-right">
                      <div className="text-xs uppercase tracking-wide text-slate-400">
                        Apportionment
                      </div>
                      <div className="text-slate-200">
                        {selectedMetrics.total_frames} frames ·{' '}
                        {selectedMetrics.tokens_accumulated} tokens
                      </div>
                      <div className="text-xs text-slate-400">
                        Δ tokens {selectedMetrics.tokens_estimate} · WM {selectedMetrics.wm_node_count} ·
                        Subentities {selectedMetrics.active_subentities}
                      </div>
                    </div>
                  )}
                </div>
              </header>

              <div className="px-6 py-3 border-b border-slate-800/70 bg-slate-950/40">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Heart className="w-4 h-4 text-rose-300" />
                  Emotional State Extract
                </h4>
                {emotionalState ? (
                  <div className="grid grid-cols-2 gap-4 text-sm text-slate-300">
                    <div className="bg-rose-500/10 border border-rose-500/20 rounded-md px-3 py-2">
                      <div className="text-xs uppercase tracking-wide text-rose-200/80">Arousal</div>
                      <div className="text-lg font-semibold text-rose-200">
                        {emotionalState.arousal.toFixed(2)}
                      </div>
                    </div>
                    <div className="bg-sky-500/10 border border-sky-500/20 rounded-md px-3 py-2">
                      <div className="text-xs uppercase tracking-wide text-sky-200/80">Valence</div>
                      <div className="text-lg font-semibold text-sky-200">
                        {emotionalState.valence.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-slate-400">
                    No emotional state markers found in this prompt.
                  </p>
                )}
              </div>

              <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
                <SectionCard
                  title="Prompt Preview"
                  sectionKey="preview"
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  <pre className="text-sm leading-relaxed text-slate-200 whitespace-pre-wrap">
                    {selectedFrame.prompt_preview || selectedFrame.full_prompt.slice(0, 400)}
                    {selectedFrame.full_prompt.length > 400 ? '…' : ''}
                  </pre>
                </SectionCard>

                <SectionCard
                  title="Full Prompt"
                  sectionKey="full"
                  expandedSections={expandedSections}
                  onToggle={toggleSection}
                >
                  <div className="space-y-4">
                    {sections.map(section => (
                      <div key={section.title}>
                        <h5 className="text-sm font-semibold text-indigo-200 uppercase tracking-wide mb-1">
                          {section.title}
                        </h5>
                        <pre className="text-sm leading-relaxed text-slate-200 bg-slate-950/60 border border-slate-800/70 rounded-md px-4 py-3 whitespace-pre-wrap">
                          {section.content}
                        </pre>
                      </div>
                    ))}
                  </div>
                </SectionCard>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400">
              <Brain className="w-12 h-12 mb-4 text-indigo-400/70" />
              <h3 className="text-lg font-medium mb-2">Waiting for forged identity frames</h3>
              <p className="text-sm text-center max-w-sm">
                Frames will appear once the consciousness engine forges a new prompt. Each frame
                includes working memory context, emotional markers, and the complete system prompt.
              </p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

interface SectionCardProps {
  title: string;
  sectionKey: string;
  expandedSections: Set<string>;
  onToggle: (key: string) => void;
  children: React.ReactNode;
}

function SectionCard({
  title,
  sectionKey,
  expandedSections,
  onToggle,
  children
}: SectionCardProps) {
  const isExpanded = expandedSections.has(sectionKey);

  return (
    <div className="border border-slate-800/80 rounded-lg bg-slate-950/40 shadow-inner">
      <button
        onClick={() => onToggle(sectionKey)}
        className="w-full flex items-center justify-between px-4 py-3 text-left text-sm font-semibold text-slate-200"
      >
        <span className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-slate-500" />
          )}
          {title}
        </span>
        <span className="text-xs uppercase tracking-wide text-slate-500">
          {isExpanded ? 'Hide' : 'Show'}
        </span>
      </button>
      {isExpanded ? <div className="px-4 pb-4">{children}</div> : null}
    </div>
  );
}

function extractPromptSections(prompt: string) {
  const sections: Array<{ title: string; content: string }> = [];
  const lines = prompt.split('\n');
  let currentSection = '';
  let currentContent: string[] = [];

  for (const line of lines) {
    if (line.startsWith('# ') && !line.startsWith('## ')) {
      if (currentSection) {
        sections.push({
          title: currentSection,
          content: currentContent.join('\n').trim()
        });
      }
      currentSection = line.substring(2);
      currentContent = [];
    } else {
      currentContent.push(line);
    }
  }

  if (currentSection) {
    sections.push({
      title: currentSection,
      content: currentContent.join('\n').trim()
    });
  }

  return sections;
}

function extractEmotionalState(prompt: string) {
  const match = prompt.match(/Arousal=([\d.]+).*Valence=([\d.]+)/);
  if (!match) return null;

  return {
    arousal: parseFloat(match[1]),
    valence: parseFloat(match[2])
  };
}

function formatTimestamp(timestamp?: string) {
  if (!timestamp) return 'Unknown';
  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) {
    return timestamp;
  }
  return parsed.toLocaleString();
}
