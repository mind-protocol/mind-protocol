/**
 * System Status API Route
 *
 * Proxies backend health check to avoid CORS issues.
 * Frontend fetches from /api/system-status (same origin).
 * This route proxies to http://localhost:8000/healthz.
 */

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/healthz');

    if (!response.ok) {
      return Response.json(
        { error: 'Backend unhealthy', status: response.status },
        { status: 503 }
      );
    }

    const data = await response.json();

    // Transform backend health response to frontend format
    return Response.json({
      overall: data.status === 'healthy' ? 'healthy' : 'degraded',
      components: [
        {
          name: 'Backend API',
          status: data.status === 'healthy' ? 'running' : 'error',
          details: data.status === 'healthy' ? 'Operational' : 'Unhealthy'
        },
        ...(data.engines ? [{
          name: 'Consciousness Engines',
          status: 'running' as const,
          details: `${data.engines.count} engines running: ${data.engines.running.map((e: string) => e.split('_').pop()).join(', ')}`
        }] : [])
      ],
      timestamp: data.timestamp || new Date().toISOString()
    });
  } catch (error) {
    console.error('[system-status] Backend fetch failed:', error);

    // Return degraded status on connection failure
    return Response.json({
      overall: 'degraded',
      components: [
        {
          name: 'Backend API',
          status: 'error',
          details: 'Connection failed'
        }
      ],
      timestamp: new Date().toISOString()
    }, { status: 503 });
  }
}
