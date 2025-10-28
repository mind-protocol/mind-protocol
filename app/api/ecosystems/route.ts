import { NextResponse } from 'next/server';
import { fetchGraphHierarchy } from '../_lib/graphHierarchy';

const BACKEND_BASE_URL = process.env.CONSCIOUSNESS_BACKEND_URL || 'http://localhost:8000';

export async function GET() {
  try {
    const hierarchy = await fetchGraphHierarchy();
    return NextResponse.json(hierarchy, { status: 200 });
  } catch (error) {
    console.error('[EcosystemsAPI] Redis hierarchy fetch failed, attempting backend fallback:', error);

    try {
      const response = await fetch(`${BACKEND_BASE_URL}/api/ecosystems`, {
        method: 'GET',
        signal: AbortSignal.timeout(15000)
      });

      const bodyText = await response.text();
      const contentType = response.headers.get('content-type') || 'application/json';

      if (contentType.includes('application/json')) {
        try {
          const data = bodyText ? JSON.parse(bodyText) : {};
          return NextResponse.json(data, { status: response.status });
        } catch (err) {
          console.warn('[EcosystemsAPI] Backend JSON parse failed, returning raw text:', err);
        }
      }

      return new NextResponse(bodyText, {
        status: response.status,
        headers: { 'Content-Type': contentType }
      });
    } catch (fallbackError) {
      console.error('[EcosystemsAPI] Backend fallback failed:', fallbackError);
      return NextResponse.json(
        {
          error: 'Failed to list ecosystems',
          details: fallbackError instanceof Error ? fallbackError.message : 'Unknown error'
        },
        { status: 503 }
      );
    }
  }
}
