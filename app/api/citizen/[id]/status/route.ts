import { NextResponse } from 'next/server';

/**
 * Citizen Status API Proxy
 *
 * Proxies citizen status requests from Next.js dashboard to Python backend.
 *
 * Backend Endpoint: GET /api/citizen/{citizen_id}/status
 * Implementation: orchestration/control_api.py::get_citizen_status()
 *
 * Returns detailed consciousness state:
 * - running_state: "running" | "frozen" | "slow_motion" | "turbo"
 * - tick_count, tick_interval_ms, tick_frequency_hz
 * - consciousness_state: "alert" | "engaged" | "calm" | "drowsy" | "dormant"
 * - sub_entity_count and sub_entities list
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-19
 */

interface RouteParams {
  params: Promise<{
    id: string;
  }>;
}

export async function GET(
  request: Request,
  { params }: RouteParams
) {
  const { id } = await params;

  try {
    const backendUrl = `http://localhost:8000/api/citizen/${id}/status`;
    const response = await fetch(backendUrl);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] Backend error (${response.status}):`, errorText);

      return NextResponse.json(
        {
          error: 'Failed to fetch citizen status',
          details: errorText,
          backend_status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('[API] Error fetching citizen status:', error);

    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: `http://localhost:8000/api/citizen/${id}/status`
      },
      { status: 503 }
    );
  }
}
