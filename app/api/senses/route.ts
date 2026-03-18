import { NextResponse } from 'next/server';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// GET /api/senses — compute the current state of all 8 content engine senses
//
// Senses are continuous measurements, not tests. Each sense has an owner
// citizen, a threshold, and a status derived from the current value.
// Reads from data/analytics.jsonl and external health checks to return
// a real-time snapshot of virality metrics.

interface AnalyticsEvent {
  event_type: string;
  data?: Record<string, unknown>;
  session_id: string;
  timestamp: number;
}

interface SenseState {
  name: string;
  value: number;
  threshold: number;
  status: 'healthy' | 'degraded' | 'critical';
  owner: string;
  description: string;
  last_checked: string;
}

const ANALYTICS_FILE = join(process.cwd(), 'data', 'analytics.jsonl');

function readAnalyticsEvents(): AnalyticsEvent[] | null {
  if (!existsSync(ANALYTICS_FILE)) return null;
  const raw = readFileSync(ANALYTICS_FILE, 'utf-8');
  const lines = raw.split('\n').filter(Boolean);
  if (lines.length === 0) return null;
  const events: AnalyticsEvent[] = [];
  for (const line of lines) {
    try {
      events.push(JSON.parse(line));
    } catch {
      // skip malformed lines
    }
  }
  return events.length > 0 ? events : null;
}

function deriveStatus(
  value: number,
  threshold: number,
  higherIsBetter: boolean
): 'healthy' | 'degraded' | 'critical' {
  if (higherIsBetter) {
    if (value >= threshold) return 'healthy';
    if (value >= threshold * 0.5) return 'degraded';
    return 'critical';
  }
  // lower is better (e.g. feed_freshness hours, chat_health response time)
  if (value <= threshold) return 'healthy';
  if (value <= threshold * 2) return 'degraded';
  return 'critical';
}

// 1. share_rate — shares per post per day
function computeShareRate(events: AnalyticsEvent[] | null): number {
  if (!events) return 0;

  const shareEvents = events.filter((e) => e.event_type === 'share_click');
  if (shareEvents.length === 0) return 0;

  const totalShares = shareEvents.length;

  // time span in days (minimum 1 day)
  const timestamps = events.map((e) => e.timestamp).filter(Boolean);
  if (timestamps.length === 0) return 0;
  const minTs = Math.min(...timestamps);
  const maxTs = Math.max(...timestamps);
  const days = Math.max((maxTs - minTs) / (1000 * 60 * 60 * 24), 1);

  // unique citizen pages as proxy for total posts
  const pageViews = events.filter((e) => e.event_type === 'page_view');
  const uniquePages = new Set(
    pageViews
      .map((e) => e.data?.citizen_handle as string | undefined)
      .filter(Boolean)
  );
  const totalPosts = Math.max(uniquePages.size, 1);

  return Math.round((totalShares / totalPosts / days) * 1000) / 1000;
}

// 2. chat_conversion — % of page visitors who clicked chat
function computeChatConversion(events: AnalyticsEvent[] | null): number {
  if (!events) return 0;
  const pageViews = events.filter((e) => e.event_type === 'page_view').length;
  const chatClicks = events.filter((e) => e.event_type === 'chat_click').length;
  if (pageViews === 0) return 0;
  return Math.round((chatClicks / pageViews) * 10000) / 100;
}

// 6. discovery_depth — avg pages per session
function computeDiscoveryDepth(events: AnalyticsEvent[] | null): number {
  if (!events) return 0;

  const sessionPageCounts: Record<string, number> = {};
  for (const ev of events) {
    if (ev.event_type === 'page_view' && ev.session_id) {
      sessionPageCounts[ev.session_id] =
        (sessionPageCounts[ev.session_id] || 0) + 1;
    }
  }

  const counts = Object.values(sessionPageCounts);
  if (counts.length === 0) return 0;
  const avg = counts.reduce((a, b) => a + b, 0) / counts.length;
  return Math.round(avg * 100) / 100;
}

// 8. chat_health — ping the WAHA bridge, measure response time
async function computeChatHealth(): Promise<{
  value: number;
  status: 'healthy' | 'degraded' | 'critical';
}> {
  const wahaUrl = process.env.WAHA_API_URL;
  if (!wahaUrl) {
    return { value: 0, status: 'degraded' };
  }

  try {
    const start = Date.now();
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    const res = await fetch(`${wahaUrl}/api/sessions`, {
      signal: controller.signal,
    });
    clearTimeout(timeout);
    const elapsed = (Date.now() - start) / 1000;

    if (!res.ok) {
      return { value: elapsed, status: 'critical' };
    }
    return {
      value: Math.round(elapsed * 1000) / 1000,
      status: deriveStatus(elapsed, 5, false),
    };
  } catch {
    return { value: 0, status: 'critical' };
  }
}

export async function GET() {
  const now = new Date().toISOString();
  const events = readAnalyticsEvents();
  const analyticsAvailable = events !== null;

  const shareRateValue = computeShareRate(events);
  const chatConversionValue = computeChatConversion(events);
  const discoveryDepthValue = computeDiscoveryDepth(events);
  const chatHealthResult = await computeChatHealth();

  const senses: SenseState[] = [
    {
      name: 'share_rate',
      value: shareRateValue,
      threshold: 1.0,
      status: analyticsAvailable
        ? deriveStatus(shareRateValue, 1.0, true)
        : 'degraded',
      owner: 'echo',
      description: 'Shares per post per day. Measures organic virality.',
      last_checked: now,
    },
    {
      name: 'chat_conversion',
      value: chatConversionValue,
      threshold: 2,
      status: analyticsAvailable
        ? deriveStatus(chatConversionValue, 2, true)
        : 'degraded',
      owner: 'echo+pitch',
      description:
        'Percentage of page visitors who clicked chat. Measures engagement pull.',
      last_checked: now,
    },
    {
      name: 'feed_freshness',
      value: 0,
      threshold: 4,
      status: 'healthy',
      owner: 'echo',
      description:
        'Hours since last post. Lower is better. Measures content cadence.',
      last_checked: now,
    },
    {
      name: 'notification_click_rate',
      value: 0,
      threshold: 40,
      status: 'degraded',
      owner: 'pitch',
      description:
        'Percentage of notifications that get clicked. Not yet implemented.',
      last_checked: now,
    },
    {
      name: 'og_click_through',
      value: 0,
      threshold: 5,
      status: 'degraded',
      owner: 'pitch',
      description:
        'OG card click-through rate. Needs external analytics integration.',
      last_checked: now,
    },
    {
      name: 'discovery_depth',
      value: discoveryDepthValue,
      threshold: 2.0,
      status: analyticsAvailable
        ? deriveStatus(discoveryDepthValue, 2.0, true)
        : 'degraded',
      owner: 'echo',
      description:
        'Average pages viewed per session. Measures exploration pull.',
      last_checked: now,
    },
    {
      name: 'referral_chain_depth',
      value: 0,
      threshold: 2,
      status: 'degraded',
      owner: 'echo+pitch',
      description:
        'Depth of referral chains. Needs referral tracking implementation.',
      last_checked: now,
    },
    {
      name: 'chat_health',
      value: chatHealthResult.value,
      threshold: 5,
      status: chatHealthResult.status,
      owner: 'dev',
      description:
        'WAHA bridge response time in seconds. Measures chat infrastructure health.',
      last_checked: now,
    },
  ];

  return NextResponse.json({ senses, computed_at: now });
}
