import { NextResponse } from 'next/server';
import { appendFileSync, readFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const FILE = join(process.cwd(), 'data', 'analytics.jsonl');

function ensureFile() {
  const dir = join(process.cwd(), 'data');
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { event_type, data, session_id, timestamp } = body;
    if (!event_type || !session_id) {
      return NextResponse.json({ error: 'missing fields' }, { status: 400 });
    }
    ensureFile();
    const line = JSON.stringify({ event_type, data, session_id, timestamp }) + '\n';
    appendFileSync(FILE, line);
  } catch {
    // fire-and-forget on client side, still return 200
  }
  return NextResponse.json({ ok: true });
}

interface AnalyticsEvent {
  event_type: string;
  data?: {
    citizen_handle?: string;
    discovery_depth?: number;
    [key: string]: unknown;
  };
  session_id: string;
  timestamp: number;
}

export async function GET() {
  if (!existsSync(FILE)) {
    return NextResponse.json({
      total_views: 0,
      views_per_citizen: [],
      share_count: 0,
      chat_click_count: 0,
      avg_discovery_depth: 0,
    });
  }

  const lines = readFileSync(FILE, 'utf-8').split('\n').filter(Boolean);
  const events: AnalyticsEvent[] = lines.map((l) => JSON.parse(l));

  let totalViews = 0;
  let shareCount = 0;
  let chatClickCount = 0;
  const citizenViews: Record<string, number> = {};
  const sessionDepths: Record<string, number> = {};

  for (const ev of events) {
    switch (ev.event_type) {
      case 'page_view':
        totalViews++;
        if (ev.data?.citizen_handle) {
          const h = ev.data.citizen_handle;
          citizenViews[h] = (citizenViews[h] || 0) + 1;
        }
        break;
      case 'share_click':
        shareCount++;
        break;
      case 'chat_click':
        chatClickCount++;
        break;
    }
    if (ev.data?.discovery_depth != null) {
      const current = sessionDepths[ev.session_id] || 0;
      if (ev.data.discovery_depth > current) {
        sessionDepths[ev.session_id] = ev.data.discovery_depth;
      }
    }
  }

  const depths = Object.values(sessionDepths);
  const avgDepth = depths.length > 0
    ? Math.round((depths.reduce((a, b) => a + b, 0) / depths.length) * 100) / 100
    : 0;

  const viewsPerCitizen = Object.entries(citizenViews)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([handle, views]) => ({ handle, views }));

  return NextResponse.json({
    total_views: totalViews,
    views_per_citizen: viewsPerCitizen,
    share_count: shareCount,
    chat_click_count: chatClickCount,
    avg_discovery_depth: avgDepth,
  });
}
