'use client';

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

// Citizen data structure based on ORG_MAP.md
interface Citizen {
  id: string;
  name: string;
  role: string;
  domain: string;
  org: 'MP' | 'GC' | 'SL';
  layer: 'Business' | 'Architecture' | 'Implementation' | 'Quality' | 'Coordination';
  output: string;
  specialNotes?: string;
}

interface Connection {
  source: string;
  target: string;
  type: 'workflow' | 'membrane'; // workflow = same org, membrane = cross-org
  description?: string;
  step?: number; // Main workflow sequence number (1-5)
}

// All 21 citizens from ORG_MAP.md
const CITIZENS: Citizen[] = [
  // Mind Protocol (7)
  { id: 'lucia', name: 'Lucia', role: 'Business', domain: 'Revenue, partnerships, strategy', org: 'MP', layer: 'Business', output: 'Business models, pricing, partnerships', specialNotes: 'DUAL ROLE: Also Treasury Architect for financeOrg (Layer 2)' },
  { id: 'luca', name: 'Luca', role: 'Consciousness', domain: 'Phenomenology, patterns', org: 'MP', layer: 'Architecture', output: 'PATTERN nodes, consciousness theory' },
  { id: 'ada', name: 'Ada', role: 'Architecture', domain: 'System design, specs', org: 'MP', layer: 'Architecture', output: 'BEHAVIOR_SPEC, GUIDE nodes' },
  { id: 'atlas', name: 'Atlas', role: 'Behavior', domain: 'Implementation, integration', org: 'MP', layer: 'Implementation', output: 'MECHANISM nodes, behavior code' },
  { id: 'felix', name: 'Felix', role: 'Engineer', domain: 'Core systems, algorithms', org: 'MP', layer: 'Implementation', output: 'ALGORITHM nodes, production code' },
  { id: 'iris', name: 'Iris', role: 'UI/UX', domain: 'Interface, experience', org: 'MP', layer: 'Quality', output: 'UI components, design systems' },
  { id: 'victor', name: 'Victor', role: 'Sys Admin', domain: 'Operations, infrastructure', org: 'MP', layer: 'Quality', output: 'Deployment, monitoring, DevOps' },

  // GraphCare (7)
  { id: 'mel', name: 'Mel', role: 'Care Coordinator', domain: 'Workflow orchestration, quality gates', org: 'GC', layer: 'Coordination', output: 'Client coordination, delivery approval' },
  { id: 'quinn', name: 'Quinn', role: 'Cartographer', domain: 'Semantic mapping, corpus analysis', org: 'GC', layer: 'Architecture', output: 'Topology maps, drift detection' },
  { id: 'kai', name: 'Kai', role: 'Engineer', domain: 'Sync engines, tooling', org: 'GC', layer: 'Implementation', output: 'Automation, graph infrastructure' },
  { id: 'nora', name: 'Nora', role: 'Architect', domain: 'Structural design, patterns', org: 'GC', layer: 'Architecture', output: 'Graph schemas, architectural views', specialNotes: 'GraphCare transitioning: construction → techServiceOrg, maintenance → GraphCare service' },
  { id: 'marcus', name: 'Marcus', role: 'Auditor', domain: 'Security, compliance', org: 'GC', layer: 'Quality', output: 'PII detection, GDPR compliance' },
  { id: 'vera', name: 'Vera', role: 'Validator', domain: 'Quality verification, health metrics', org: 'GC', layer: 'Quality', output: 'Test results, health dashboards' },
  { id: 'sage', name: 'Sage', role: 'Documenter', domain: 'Guides, reports, synthesis', org: 'GC', layer: 'Quality', output: 'Multi-level documentation, insights' },

  // ScopeLock (6)
  { id: 'emma', name: 'Emma', role: 'Scout', domain: 'Proposals, marketing, leads', org: 'SL', layer: 'Business', output: 'Upwork proposals, marketing content' },
  { id: 'inna', name: 'Inna', role: 'Specifier', domain: 'Complete documentation', org: 'SL', layer: 'Architecture', output: 'Full doc hierarchy (PATTERN→GUIDE)' },
  { id: 'rafael', name: 'Rafael', role: 'Guide', domain: 'Code generation, mentorship', org: 'SL', layer: 'Implementation', output: 'Implementation code, debugging' },
  { id: 'sofia', name: 'Sofia', role: 'Checker', domain: 'Test generation, QA', org: 'SL', layer: 'Quality', output: 'Test suites, quality verification' },
  { id: 'alexis', name: 'Alexis', role: 'Strategist', domain: 'Business operations, pricing', org: 'SL', layer: 'Business', output: 'Financial strategy, team management' },
  { id: 'maya', name: 'Maya', role: 'Bridge', domain: 'Client success, communication', org: 'SL', layer: 'Coordination', output: 'Client relationships, handoffs', specialNotes: 'ScopeLock is INTERNAL-ONLY (Layer 1), not part of external ecosystem (Layer 2)' },
];

// Workflow connections (based on ORG_MAP.md Section 2 workflows)
const CONNECTIONS: Connection[] = [
  // Mind Protocol workflow (main critical path numbered 1-5)
  { source: 'luca', target: 'ada', type: 'workflow', description: 'Pattern → Behavior Spec', step: 1 },
  { source: 'ada', target: 'felix', type: 'workflow', description: 'Behavior Spec → Implementation', step: 2 },
  { source: 'ada', target: 'atlas', type: 'workflow', description: 'Behavior Spec → Integration' },
  { source: 'felix', target: 'atlas', type: 'workflow', description: 'Algorithm → Integration', step: 3 },
  { source: 'felix', target: 'victor', type: 'workflow', description: 'Implementation → Deployment' },
  { source: 'atlas', target: 'victor', type: 'workflow', description: 'Integration → Deployment', step: 4 },
  { source: 'victor', target: 'ada', type: 'workflow', description: 'Deployment → Verification', step: 5 },
  { source: 'iris', target: 'victor', type: 'workflow', description: 'UI → Deployment (parallel)' },
  { source: 'lucia', target: 'ada', type: 'workflow', description: 'Business validation' },

  // GraphCare workflow (main critical path numbered 1-5)
  { source: 'mel', target: 'quinn', type: 'workflow', description: 'Scope → Analysis', step: 1 },
  { source: 'quinn', target: 'kai', type: 'workflow', description: 'Analysis → Extraction' },
  { source: 'quinn', target: 'nora', type: 'workflow', description: 'Analysis → Architecture', step: 2 },
  { source: 'kai', target: 'nora', type: 'workflow', description: 'Extraction → Architecture' },
  { source: 'nora', target: 'marcus', type: 'workflow', description: 'Architecture → Security Audit', step: 3 },
  { source: 'marcus', target: 'vera', type: 'workflow', description: 'Security → Validation', step: 4 },
  { source: 'vera', target: 'sage', type: 'workflow', description: 'Validation → Documentation', step: 5 },
  { source: 'sage', target: 'mel', type: 'workflow', description: 'Documentation → Delivery' },

  // ScopeLock workflow (main critical path numbered 1-5)
  { source: 'emma', target: 'maya', type: 'workflow', description: 'Proposal → Onboarding', step: 1 },
  { source: 'maya', target: 'inna', type: 'workflow', description: 'Onboarding → Spec', step: 2 },
  { source: 'inna', target: 'sofia', type: 'workflow', description: 'Spec → Test Generation' },
  { source: 'inna', target: 'rafael', type: 'workflow', description: 'Spec → Implementation', step: 3 },
  { source: 'sofia', target: 'rafael', type: 'workflow', description: 'Tests → Implementation' },
  { source: 'rafael', target: 'sofia', type: 'workflow', description: 'Code → Verification', step: 4 },
  { source: 'sofia', target: 'maya', type: 'workflow', description: 'Verification → Delivery', step: 5 },
  { source: 'alexis', target: 'emma', type: 'workflow', description: 'Pricing → Proposals' },

  // Cross-org membranes (Section 3 from ORG_MAP.md)
  // Business layer membrane
  { source: 'lucia', target: 'mel', type: 'membrane', description: 'Pricing coordination' },
  { source: 'lucia', target: 'alexis', type: 'membrane', description: 'Revenue intelligence' },
  { source: 'mel', target: 'alexis', type: 'membrane', description: 'Client success patterns' },
  { source: 'emma', target: 'mel', type: 'membrane', description: 'Lead generation' },

  // Architecture layer membrane
  { source: 'ada', target: 'nora', type: 'membrane', description: 'Architectural review' },
  { source: 'ada', target: 'inna', type: 'membrane', description: 'Spec structure' },
  { source: 'nora', target: 'inna', type: 'membrane', description: 'Knowledge hierarchy' },

  // Implementation layer membrane
  { source: 'felix', target: 'kai', type: 'membrane', description: 'Algorithm sharing' },
  { source: 'felix', target: 'rafael', type: 'membrane', description: 'Code patterns' },
  { source: 'kai', target: 'rafael', type: 'membrane', description: 'Integration patterns' },
  { source: 'atlas', target: 'kai', type: 'membrane', description: 'Integration implementation' },

  // Quality layer membrane
  { source: 'vera', target: 'sofia', type: 'membrane', description: 'Test design' },
  { source: 'marcus', target: 'victor', type: 'membrane', description: 'Security scanning' },
  { source: 'iris', target: 'sage', type: 'membrane', description: 'Documentation quality' },
];

const ORG_COLORS = {
  MP: '#9333EA', // Purple
  GC: '#10B981', // Green
  SL: '#F59E0B', // Orange
};

const LAYER_ICONS = {
  Business: '💼',
  Architecture: '🏗️',
  Implementation: '⚙️',
  Quality: '✅',
  Coordination: '🎯',
};

export default function CitizensPage() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [orgFilter, setOrgFilter] = useState<'ALL' | 'MP' | 'GC' | 'SL'>('ALL');
  const [layerFilter, setLayerFilter] = useState<'ALL' | Citizen['layer']>('ALL');
  const [selectedCitizen, setSelectedCitizen] = useState<Citizen | null>(null);
  const [stats, setStats] = useState({ citizens: 21, connections: 0, membranes: 0 });

  useEffect(() => {
    const membraneCount = CONNECTIONS.filter(c => c.type === 'membrane').length;
    const workflowCount = CONNECTIONS.filter(c => c.type === 'workflow').length;
    setStats({ citizens: CITIZENS.length, connections: workflowCount, membranes: membraneCount });
  }, []);

  useEffect(() => {
    if (!svgRef.current) return;

    // Filter citizens
    let filteredCitizens = CITIZENS.filter(c => {
      const matchesSearch = searchTerm === '' ||
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.domain.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesOrg = orgFilter === 'ALL' || c.org === orgFilter;
      const matchesLayer = layerFilter === 'ALL' || c.layer === layerFilter;
      return matchesSearch && matchesOrg && matchesLayer;
    });

    const filteredCitizenIds = new Set(filteredCitizens.map(c => c.id));
    const filteredConnections = CONNECTIONS.filter(c =>
      filteredCitizenIds.has(c.source) && filteredCitizenIds.has(c.target)
    );

    // Clear previous SVG content
    d3.select(svgRef.current).selectAll('*').remove();

    const width = 1200;
    const height = 800;

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Create arrow markers for directed edges
    svg.append('defs').selectAll('marker')
      .data(['workflow', 'membrane'])
      .join('marker')
      .attr('id', d => `arrow-${d}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 7)
      .attr('markerHeight', 7)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', d => d === 'membrane' ? '#D97706' : '#334155'); // Darker colors for visibility

    // Create force simulation with strong numbered workflow path (1-5)
    const simulation = d3.forceSimulation(filteredCitizens as any)
      .force('link', d3.forceLink(filteredConnections)
        .id((d: any) => d.id)
        .distance(d => {
          const conn = d as Connection;
          if (conn.type === 'membrane') return 400; // Membranes very weak/far
          if (conn.step) return 150; // Numbered workflow steps: medium distance
          return 200; // Other workflow: further apart
        })
        .strength(d => {
          const conn = d as Connection;
          if (conn.type === 'membrane') return 0.05; // Membranes very weak
          if (conn.step) return 1.5; // Numbered workflow: VERY strong (main path)
          return 0.2; // Other workflow: weak (secondary connections)
        }))
      .force('charge', d3.forceManyBody().strength(-600)) // Stronger repulsion = more spacing
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(70)); // Larger collision radius = more space between nodes

    // Create container for zoom
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    svg.call(zoom as any);

    // Create links
    const link = g.append('g')
      .selectAll('line')
      .data(filteredConnections)
      .join('line')
      .attr('stroke', d => {
        if (d.type === 'membrane') return '#D97706';
        return d.step ? '#334155' : '#64748B'; // Main flow darker
      })
      .attr('stroke-width', d => {
        if (d.type === 'membrane') return 1.5;
        return d.step ? 4 : 1.5; // Main numbered flow much thicker
      })
      .attr('stroke-dasharray', d => d.type === 'membrane' ? '5,5' : 'none')
      .attr('marker-end', d => `url(#arrow-${d.type})`)
      .attr('opacity', d => {
        if (d.type === 'membrane') return 0.2; // Membranes very faint
        return d.step ? 0.9 : 0.25; // Numbered flow bold, others very faint
      });

    // Create link labels for numbered workflow steps
    const linkLabel = g.append('g')
      .selectAll('g')
      .data(filteredConnections.filter(d => d.step)) // Only numbered steps
      .join('g');

    // Add circle background for step number
    linkLabel.append('circle')
      .attr('r', 12)
      .attr('fill', '#FFF')
      .attr('stroke', '#334155')
      .attr('stroke-width', 2);

    // Add step number text
    linkLabel.append('text')
      .text(d => d.step!)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'central')
      .attr('font-family', 'var(--font-cinzel)')
      .attr('font-size', 12)
      .attr('font-weight', 700)
      .attr('fill', '#334155')
      .style('pointer-events', 'none');

    // Create nodes
    const node = g.append('g')
      .selectAll('g')
      .data(filteredCitizens)
      .join('g')
      .call(d3.drag<any, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended) as any);

    // Add circles
    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => ORG_COLORS[d.org])
      .attr('stroke', '#FFF')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        setSelectedCitizen(d);
      });

    // Add text labels
    node.append('text')
      .text(d => d.name)
      .attr('x', 0)
      .attr('y', 35)
      .attr('text-anchor', 'middle')
      .attr('font-family', 'var(--font-cinzel)')
      .attr('font-size', 12)
      .attr('font-weight', 600)
      .attr('fill', '#1E293B')
      .style('pointer-events', 'none');

    // Add layer icon
    node.append('text')
      .text(d => LAYER_ICONS[d.layer])
      .attr('x', 0)
      .attr('y', 5)
      .attr('text-anchor', 'middle')
      .attr('font-size', 16)
      .style('pointer-events', 'none');

    // Add tooltips
    node.append('title')
      .text(d => `${d.name} (${d.org})\n${d.role}\n${d.domain}`);

    // Update positions on tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      // Position link labels at midpoint
      linkLabel.attr('transform', (d: any) => {
        const x = (d.source.x + d.target.x) / 2;
        const y = (d.source.y + d.target.y) / 2;
        return `translate(${x},${y})`;
      });

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Click outside to deselect
    svg.on('click', () => setSelectedCitizen(null));

    return () => {
      simulation.stop();
    };
  }, [searchTerm, orgFilter, layerFilter]);

  const getConnections = (citizenId: string) => {
    const handsOffTo = CONNECTIONS.filter(c => c.source === citizenId).map(c => {
      const target = CITIZENS.find(citizen => citizen.id === c.target);
      return target ? `${target.name} (${c.description})` : '';
    });
    const receivesFrom = CONNECTIONS.filter(c => c.target === citizenId).map(c => {
      const source = CITIZENS.find(citizen => citizen.id === c.source);
      return source ? `${source.name} (${c.description})` : '';
    });
    return { handsOffTo, receivesFrom };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50">
      {/* Header */}
      <div className="border-b border-amber-200 bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-4xl font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
            Citizen Network Graph
          </h1>
          <p className="mt-2 text-amber-700 font-[family-name:var(--font-crimson-text)]">
            21 autonomous citizens across 3 organizations
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Filters & Stats */}
          <div className="lg:col-span-1 space-y-6">
            {/* Stats */}
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 p-6 shadow-lg">
              <h2 className="text-xl font-bold text-amber-900 mb-4 font-[family-name:var(--font-cinzel)]">
                Network Stats
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">Total Citizens</span>
                  <span className="text-2xl font-bold text-amber-900">{stats.citizens}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">Workflow Links</span>
                  <span className="text-2xl font-bold text-slate-600">{stats.connections}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-amber-700">Cross-Org Membranes</span>
                  <span className="text-2xl font-bold text-orange-600">{stats.membranes}</span>
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
                  placeholder="Name, role, or domain..."
                  className="w-full px-3 py-2 border border-amber-300 rounded-md focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                />
              </div>

              {/* Organization Filter */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-amber-700 mb-2">
                  Organization
                </label>
                <div className="flex gap-2 flex-wrap">
                  {['ALL', 'MP', 'GC', 'SL'].map(org => (
                    <button
                      key={org}
                      onClick={() => setOrgFilter(org as any)}
                      className={`px-4 py-2 rounded-md font-medium transition-all ${
                        orgFilter === org
                          ? org === 'MP' ? 'bg-purple-600 text-white'
                          : org === 'GC' ? 'bg-green-600 text-white'
                          : org === 'SL' ? 'bg-orange-600 text-white'
                          : 'bg-amber-600 text-white'
                          : 'bg-white text-amber-800 border border-amber-300 hover:bg-amber-50'
                      }`}
                    >
                      {org}
                    </button>
                  ))}
                </div>
              </div>

              {/* Layer Filter */}
              <div>
                <label className="block text-sm font-medium text-amber-700 mb-2">
                  Layer
                </label>
                <select
                  value={layerFilter}
                  onChange={(e) => setLayerFilter(e.target.value as any)}
                  className="w-full px-3 py-2 border border-amber-300 rounded-md focus:ring-2 focus:ring-amber-500"
                >
                  <option value="ALL">All Layers</option>
                  <option value="Business">💼 Business</option>
                  <option value="Architecture">🏗️ Architecture</option>
                  <option value="Implementation">⚙️ Implementation</option>
                  <option value="Quality">✅ Quality</option>
                  <option value="Coordination">🎯 Coordination</option>
                </select>
              </div>
            </div>

            {/* Legend */}
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 p-6 shadow-lg">
              <h2 className="text-xl font-bold text-amber-900 mb-4 font-[family-name:var(--font-cinzel)]">
                Legend
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-purple-600 border-2 border-white"></div>
                  <span className="text-sm text-amber-800">Mind Protocol (MP)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-green-600 border-2 border-white"></div>
                  <span className="text-sm text-amber-800">GraphCare (GC)</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 rounded-full bg-orange-600 border-2 border-white"></div>
                  <span className="text-sm text-amber-800">ScopeLock (SL)</span>
                </div>
                <div className="border-t border-amber-200 pt-3 mt-3">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-12 h-0.5 bg-slate-600"></div>
                    <span className="text-sm text-amber-800">Workflow Link</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-0.5 bg-orange-600 border-dashed border-b-2 border-orange-600"></div>
                    <span className="text-sm text-amber-800">Cross-Org Membrane</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Graph Visualization */}
          <div className="lg:col-span-2">
            <div className="bg-white/90 backdrop-blur-sm rounded-lg border-2 border-amber-200 shadow-lg overflow-hidden">
              <div className="p-4 border-b border-amber-200 bg-amber-50">
                <h2 className="text-lg font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
                  Interactive Network
                </h2>
                <p className="text-sm text-amber-700 mt-1">
                  Drag nodes to reorganize • Click for details • Scroll to zoom
                </p>
              </div>
              <div className="relative">
                <svg ref={svgRef} className="w-full" style={{ minHeight: '800px' }}></svg>
              </div>
            </div>
          </div>
        </div>

        {/* Selected Citizen Detail Card */}
        {selectedCitizen && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
               onClick={() => setSelectedCitizen(null)}>
            <div className="bg-white rounded-lg border-2 border-amber-200 shadow-2xl max-w-2xl w-full p-6"
                 onClick={(e) => e.stopPropagation()}>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-amber-900 font-[family-name:var(--font-cinzel)]">
                    {selectedCitizen.name}
                  </h3>
                  <div className="flex items-center gap-2 mt-2">
                    <span className={`px-3 py-1 rounded-full text-white text-sm font-medium ${
                      selectedCitizen.org === 'MP' ? 'bg-purple-600'
                      : selectedCitizen.org === 'GC' ? 'bg-green-600'
                      : 'bg-orange-600'
                    }`}>
                      {selectedCitizen.org === 'MP' ? 'Mind Protocol'
                       : selectedCitizen.org === 'GC' ? 'GraphCare'
                       : 'ScopeLock'}
                    </span>
                    <span className="px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-sm font-medium">
                      {LAYER_ICONS[selectedCitizen.layer]} {selectedCitizen.layer}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCitizen(null)}
                  className="text-amber-600 hover:text-amber-800 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-amber-900 mb-1">Role</h4>
                  <p className="text-amber-800">{selectedCitizen.role}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-amber-900 mb-1">Domain</h4>
                  <p className="text-amber-800">{selectedCitizen.domain}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-amber-900 mb-1">Primary Output</h4>
                  <p className="text-amber-800">{selectedCitizen.output}</p>
                </div>

                {selectedCitizen.specialNotes && (
                  <div className="bg-amber-50 border border-amber-200 rounded-md p-3">
                    <h4 className="font-semibold text-amber-900 mb-1">⭐ Special Notes</h4>
                    <p className="text-sm text-amber-800">{selectedCitizen.specialNotes}</p>
                  </div>
                )}

                <div>
                  <h4 className="font-semibold text-amber-900 mb-2">Connections</h4>
                  {(() => {
                    const { handsOffTo, receivesFrom } = getConnections(selectedCitizen.id);
                    return (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium text-green-700 mb-1">Hands off to:</p>
                          {handsOffTo.length > 0 ? (
                            <ul className="text-sm text-amber-800 space-y-1">
                              {handsOffTo.map((c, i) => (
                                <li key={i} className="truncate">→ {c}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-amber-600">No outgoing</p>
                          )}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-blue-700 mb-1">Receives from:</p>
                          {receivesFrom.length > 0 ? (
                            <ul className="text-sm text-amber-800 space-y-1">
                              {receivesFrom.map((c, i) => (
                                <li key={i} className="truncate">← {c}</li>
                              ))}
                            </ul>
                          ) : (
                            <p className="text-sm text-amber-600">No incoming</p>
                          )}
                        </div>
                      </div>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
