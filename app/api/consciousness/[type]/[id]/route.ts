import { NextResponse } from 'next/server';

/**
 * Consciousness Graph REST API Proxy
 *
 * Proxies requests from Next.js dashboard to Python backend WebSocket server.
 *
 * Hybrid Architecture:
 * - This endpoint (REST) provides initial graph snapshot
 * - WebSocket at ws://localhost:8000/api/ws provides real-time updates
 *
 * Backend Endpoint: GET /api/graph/{type}/{id}
 * Implementation: orchestration/control_api.py::get_graph_data()
 *
 * Author: Felix "Ironhand"
 * Date: 2025-10-19
 */

interface RouteParams {
  params: {
    type: string;
    id: string;
  };
}

export async function GET(
  request: Request,
  { params }: RouteParams
) {
  const { type, id } = params;

  try {
    // Proxy to Python backend
    const backendUrl = `http://localhost:8000/api/graph/${type}/${id}`;

    const response = await fetch(backendUrl);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error (${response.status}):`, errorText);

      return NextResponse.json(
        {
          error: 'Failed to fetch graph data',
          details: errorText,
          backend_status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();

    return NextResponse.json(data);

  } catch (error) {
    console.error('Error fetching graph from backend:', error);

    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: `http://localhost:8000/api/graph/${type}/${id}`
      },
      { status: 503 }
    );
  }
}
