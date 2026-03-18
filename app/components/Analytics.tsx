'use client';

import { useEffect } from 'react';

declare global {
  interface Window {
    trackEvent: (type: string, data?: Record<string, unknown>) => void;
  }
}

function getSessionId(): string {
  let id = sessionStorage.getItem('mp_session');
  if (!id) {
    id = crypto.randomUUID();
    sessionStorage.setItem('mp_session', id);
  }
  return id;
}

function getDiscoveryDepth(): number {
  const visited = JSON.parse(sessionStorage.getItem('mp_visited') || '[]') as string[];
  return visited.length;
}

function recordCitizenVisit(handle: string) {
  const visited = JSON.parse(sessionStorage.getItem('mp_visited') || '[]') as string[];
  if (!visited.includes(handle)) {
    visited.push(handle);
    sessionStorage.setItem('mp_visited', JSON.stringify(visited));
  }
}

function sendEvent(type: string, data?: Record<string, unknown>) {
  const sessionId = getSessionId();
  fetch('/api/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      event_type: type,
      data: { ...data, discovery_depth: getDiscoveryDepth() },
      session_id: sessionId,
      timestamp: Date.now(),
    }),
  }).catch(() => {});
}

export default function Analytics() {
  useEffect(() => {
    const path = window.location.pathname;
    const referrer = document.referrer;
    const match = path.match(/^\/citizen\/([^/]+)/);
    const citizen_handle = match ? match[1] : undefined;
    if (citizen_handle) recordCitizenVisit(citizen_handle);
    sendEvent('page_view', { path, referrer, ...(citizen_handle && { citizen_handle }) });
    window.trackEvent = sendEvent;
  }, []);
  return null;
}
