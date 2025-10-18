import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/api/graphs');
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching graphs:', error);
    return NextResponse.json(
      { citizens: [], organizations: [], ecosystems: [] },
      { status: 500 }
    );
  }
}
