import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';

/**
 * GET /api/viz/snapshot
 *
 * Returns initial graph snapshot for visualization by proxying to Python backend.
 *
 * Backend endpoint: GET http://localhost:8000/api/graph/{type}/{id}
 * Queries FalkorDB directly for real consciousness graph data.
 *
 * Author: Ada "Bridgekeeper" (Architect)
 * Date: 2025-10-23 (Fixed mock→real data)
 * Original: Iris "The Aperture"
 */
export async function GET(request: NextRequest) {
  try {
    // Get graph_id from query params (required)
    const searchParams = request.nextUrl.searchParams;
    const graph_id = searchParams.get('graph_id');

    if (!graph_id) {
      return NextResponse.json(
        { error: 'Missing required parameter: graph_id' },
        { status: 400 }
      );
    }

    // Determine graph type from graph_id
    let graph_type = 'citizen'; // default
    if (graph_id.startsWith('org_')) {
      graph_type = 'organization';
    } else if (graph_id.startsWith('ecosystem_')) {
      graph_type = 'ecosystem';
    }

    // Proxy to Python backend
    const backendUrl = `http://localhost:8000/api/graph/${graph_type}/${graph_id}`;

    const response = await fetch(backendUrl);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Snapshot API] Backend error (${response.status}):`, errorText);

      return NextResponse.json(
        {
          error: 'Failed to fetch graph snapshot',
          details: errorText,
          backend_status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();

    // Return real FalkorDB data from backend
    return NextResponse.json(data);

  } catch (error) {
    console.error('[Snapshot API] Error:', error);
    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 503 }
    );
  }
}
