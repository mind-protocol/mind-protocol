import { NextResponse } from 'next/server';

const MESSAGE =
  'Stimulus REST API has been retired. Publish `membrane.inject` envelopes over the WebSocket bus (ws://localhost:8000/api/ws).';

export async function POST() {
  return NextResponse.json({ error: MESSAGE }, { status: 410 });
}

export async function GET() {
  return NextResponse.json({ error: MESSAGE }, { status: 410 });
}
