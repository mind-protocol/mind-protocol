'use client';

import React, { useState } from 'react';
import { HealthDashboard } from '../components/health/HealthDashboard';

/**
 * Health Monitoring Page
 *
 * One-screen neurosurgeon view of consciousness graph health diagnostics.
 * Shows 10 core metrics, critical issues, historical trends, and procedure controls.
 */
export default function HealthPage() {
  // For now, default to first citizen. In production, allow graph selection.
  const [selectedGraph, setSelectedGraph] = useState('citizen_ada');

  const availableGraphs = [
    'citizen_ada',
    'citizen_felix',
    'citizen_iris',
    'citizen_luca',
    'citizen_atlas',
    'citizen_victor',
  ];

  return (
    <div className="min-h-screen bg-observatory-bg p-6">
      {/* Graph selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-observatory-silver mb-2">
          Select Graph:
        </label>
        <select
          value={selectedGraph}
          onChange={(e) => setSelectedGraph(e.target.value)}
          className="bg-observatory-bg-light border border-observatory-silver/20 rounded-lg px-4 py-2 text-observatory-silver focus:outline-none focus:border-observatory-cyan"
        >
          {availableGraphs.map((graph) => (
            <option key={graph} value={graph}>
              {graph}
            </option>
          ))}
        </select>
      </div>

      {/* Health Dashboard */}
      <HealthDashboard graph_id={selectedGraph} />
    </div>
  );
}
