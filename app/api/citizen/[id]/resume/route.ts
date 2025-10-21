import { NextResponse } from 'next/server';

/**
 * Citizen Resume API Proxy
 *
 * Proxies citizen resume requests from Next.js dashboard to Python backend.
 *
 * Backend Endpoint: POST /api/citizen/{citizen_id}/resume
 * Implementation: orchestration/control_api.py::resume_citizen_endpoint()
 *
 * Resumes specific citizen's consciousness by resetting tick_multiplier = 1.0.
 * Returns to normal variable frequency operation.
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
    const backendUrl = `http://localhost:8000/api/citizen/${id}/resume`;
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
          error: 'Failed to resume citizen',
          details: errorText,
          backend_status: response.status
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('[API] Error resuming citizen:', error);

    return NextResponse.json(
      {
        error: 'Backend connection failed',
        details: error instanceof Error ? error.message : 'Unknown error',
        backend_url: `http://localhost:8000/api/citizen/${id}/resume`
      },
      { status: 503 }
    );
  }
}
