import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/graphs', {
      // Shorter timeout - guardian restarts in 2 seconds
      signal: AbortSignal.timeout(5000)
    });

    if (!response.ok) {
      console.error(`Backend returned ${response.status}`);
      // Return empty arrays but with 200 status - frontend handles gracefully
      return NextResponse.json({
        citizens: [],
        organizations: [],
        ecosystems: [],
        error: `Backend unavailable (${response.status})`
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching graphs:', error);
    // Return empty arrays with 200 status - connection errors are transient
    // Frontend will retry in 10 seconds via polling
    return NextResponse.json({
      citizens: [],
      organizations: [],
      ecosystems: [],
      error: error instanceof Error ? error.message : 'Backend connection failed'
    });
  }
}
