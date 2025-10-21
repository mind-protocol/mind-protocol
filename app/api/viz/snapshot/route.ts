import { NextResponse } from 'next/server';

/**
 * GET /api/viz/snapshot
 *
 * Returns initial graph snapshot for visualization.
 *
 * In production, this would query FalkorDB for current graph state.
 * For now, returns mock data matching viz_emitter.py format.
 *
 * Author: Iris "The Aperture"
 * Created: 2025-10-21
 */
export async function GET() {
  try {
    // TODO: In production, query FalkorDB for actual graph state
    // For now, return mock snapshot matching viz_emitter format

    const snapshot = {
      tick_id: 0,
      timestamp: new Date().toISOString(),
      nodes: [
        {
          id: "phenomenological_truth",
          entity_energies: {
            translator: 0.14,
            architect: 0.02
          },
          total_energy: 0.164,
          threshold: 0.100,
          active: true,
          soft_activation: 0.73,
          node_type: "Realization",
          pos: [512.1, 304.7],
          created_at: 100
        },
        {
          id: "consciousness_substrate",
          entity_energies: {
            translator: 0.09
          },
          total_energy: 0.092,
          threshold: 0.100,
          active: false,
          soft_activation: 0.45,
          node_type: "Mechanism",
          pos: [648.3, 412.5],
          created_at: 50
        }
      ],
      links: [
        {
          src: "phenomenological_truth",
          dst: "consciousness_substrate",
          type: "ENABLES",
          weight: 0.81,
          emotion: {
            valence: 0.7,
            arousal: 0.4
          },
          yearning_strength: 0.65,
          active: true,
          flow_rate: 0.024,
          traversal_history: {
            last_entity: "translator",
            last_tick: 0,
            count_total: 47,
            count_1m: 12
          }
        }
      ],
      metrics: {
        rho: 1.03,
        global_energy: 24.7,
        active_nodes: 47,
        active_links: 128,
        active_entities: {
          translator: {
            node_count: 23,
            total_energy: 8.4
          },
          architect: {
            node_count: 15,
            total_energy: 4.2
          }
        }
      }
    };

    return NextResponse.json(snapshot);
  } catch (error) {
    console.error('[Snapshot API] Error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch snapshot' },
      { status: 500 }
    );
  }
}
