import { NextResponse } from 'next/server';

/**
 * Citizen Pause API Proxy
 *
 * Proxies citizen pause/freeze requests from Next.js dashboard to Python backend.
 *
 * Backend Endpoint: POST /api/citizen/{citizen_id}/pause
 * Implementation: orchestration/control_api.py::pause_citizen_endpoint()
 *
 * Freezes specific citizen's consciousness by setting tick_multiplier = 1e9.
 * No state loss - instant resume capability.
 *
 * Author: Iris "The Aperture"
 * Date: 2025-10-19
 */

interface RouteParams {
  params: Promise<{
    id: string;
  }>;
}

export async function POST(
  request: Request,
  { params }: RouteParams
) {
  const { id } = await params;

  try {
    const backendUrl = `http://localhost:8000/api/citizen/${id}/pause`;
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[API] Backend error (${response.status}):`, errorText);

      return NextResponse.json(
        {
          error: 'Failed to pause citizen',
          details: errorText,
          backend_status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('[API] Error pausing citizen:', error);

    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: `http://localhost:8000/api/citizen/${id}/pause`
      },
      { status: 503 }
    );
  }
}
