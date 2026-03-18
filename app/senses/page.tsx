'use client';

import Link from 'next/link';
import { useEffect, useState, useCallback } from 'react';

/* ── Types ──────────────────────────────────────────── */

interface Sense {
  name: string;
  value: number;
  threshold: number;
  status: 'healthy' | 'degraded' | 'critical';
  owner: string;
  description: string;
  last_checked: string;
}

interface SensesResponse {
  senses: Sense[];
  computed_at: string;
}

interface AnalyticsResponse {
  total_views: number;
  views_per_citizen: { handle: string; views: number }[];
  share_count: number;
  chat_click_count: number;
  avg_discovery_depth: number;
}

/* ── Constants ──────────────────────────────────────── */

const STATUS_COLORS: Record<string, string> = {
  healthy: '#25D366',
  degraded: '#f59e0b',
  critical: '#ef4444',
};

const STATUS_LABELS: Record<string, string> = {
  healthy: 'Sain',
  degraded: 'Degrade',
  critical: 'Critique',
};

const SENSE_DISPLAY_NAMES: Record<string, string> = {
  share_rate: 'Taux de partage',
  chat_conversion: 'Conversion chat',
  feed_freshness: 'Fraicheur du flux',
  notification_click_rate: 'Taux de clic notif.',
  og_click_through: 'OG click-through',
  discovery_depth: 'Profondeur decouverte',
  referral_chain_depth: 'Chaine de referral',
  chat_health: 'Sante du chat',
};

const SENSE_UNITS: Record<string, string> = {
  share_rate: '/post/j',
  chat_conversion: '%',
  feed_freshness: 'heures',
  notification_click_rate: '%',
  og_click_through: '%',
  discovery_depth: 'pages',
  referral_chain_depth: 'niveaux',
  chat_health: 'sec',
};

// Senses where lower value = better (threshold is a ceiling, not a floor)
const LOWER_IS_BETTER = new Set(['feed_freshness', 'chat_health']);

const REFRESH_INTERVAL = 30_000;

/* ── Component ──────────────────────────────────────── */

export default function SensesDashboard() {
  const [senses, setSenses] = useState<Sense[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [computedAt, setComputedAt] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [sensesRes, analyticsRes] = await Promise.all([
        fetch('/api/senses'),
        fetch('/api/analytics'),
      ]);

      if (!sensesRes.ok) throw new Error(`Senses API: ${sensesRes.status}`);
      if (!analyticsRes.ok) throw new Error(`Analytics API: ${analyticsRes.status}`);

      const sensesData: SensesResponse = await sensesRes.json();
      const analyticsData: AnalyticsResponse = await analyticsRes.json();

      setSenses(sensesData.senses);
      setComputedAt(sensesData.computed_at);
      setAnalytics(analyticsData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur inconnue');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchData]);

  /* ── Derived state ──────────────────────────────── */

  const healthySenses = senses.filter((s) => s.status === 'healthy').length;
  const totalSenses = senses.length;
  const overallHealth = totalSenses > 0
    ? Math.round((healthySenses / totalSenses) * 100)
    : 0;

  const overallStatus: 'healthy' | 'degraded' | 'critical' =
    senses.some((s) => s.status === 'critical')
      ? 'critical'
      : senses.some((s) => s.status === 'degraded')
        ? 'degraded'
        : 'healthy';

  /* ── Render ─────────────────────────────────────── */

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0f0c29] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-[#a78bfa] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-white/60">Chargement des sens...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#0f0c29] text-white">
      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <Link href="/landing" className="text-xl font-bold tracking-wide">
          mind<span className="text-[#a78bfa]">protocol</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link
            href="/landing"
            className="text-white/60 hover:text-white transition text-sm"
          >
            Retour
          </Link>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-6 py-10">
        {/* HEADER */}
        <div className="mb-10">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl md:text-4xl font-bold">Sens de la ville</h1>
            <span
              className="w-3 h-3 rounded-full mt-1"
              style={{ backgroundColor: STATUS_COLORS[overallStatus] }}
            />
          </div>
          <p className="text-white/50 text-lg">
            Mesure continue de la sante du content engine
          </p>
          <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-white/40">
            <span>
              Sante globale : {overallHealth}% ({healthySenses}/{totalSenses} sains)
            </span>
            {computedAt && (
              <span>
                Derniere mesure : {new Date(computedAt).toLocaleTimeString('fr-FR')}
              </span>
            )}
            <span>Rafraichissement : 30s</span>
          </div>
        </div>

        {/* ERROR BANNER */}
        {error && (
          <div className="mb-6 bg-[#ef4444]/10 border border-[#ef4444]/30 rounded-xl px-5 py-3 text-sm text-[#ef4444]">
            Erreur : {error}
          </div>
        )}

        {/* SENSES GRID */}
        <section className="mb-12">
          <h2 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-5">
            8 sens du content engine
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {senses.map((sense) => (
              <SenseCard key={sense.name} sense={sense} />
            ))}
          </div>
        </section>

        {/* ANALYTICS SUMMARY */}
        {analytics && (
          <section>
            <h2 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-5">
              Analytique globale
            </h2>

            {/* Metric row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <MetricCard label="Pages vues (total)" value={analytics.total_views} />
              <MetricCard label="Partages (total)" value={analytics.share_count} />
              <MetricCard label="Clics chat (total)" value={analytics.chat_click_count} />
              <MetricCard
                label="Profondeur moy."
                value={analytics.avg_discovery_depth}
                suffix=" profils"
              />
            </div>

            {/* Top visited citizens */}
            {analytics.views_per_citizen.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl border border-white/10 p-5">
                <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4">
                  Top 5 profils les plus visites
                </h3>
                <div className="space-y-3">
                  {analytics.views_per_citizen.slice(0, 5).map((citizen, index) => (
                    <div
                      key={citizen.handle}
                      className="flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-white/30 text-sm w-5 text-right">
                          {index + 1}.
                        </span>
                        <Link
                          href={`/citizen/${citizen.handle}`}
                          className="text-[#a78bfa] hover:underline text-sm"
                        >
                          @{citizen.handle}
                        </Link>
                      </div>
                      <div className="flex items-center gap-2">
                        <div
                          className="h-1.5 rounded-full bg-[#a78bfa]/40"
                          style={{
                            width: `${Math.min(
                              (citizen.views /
                                (analytics.views_per_citizen[0]?.views || 1)) *
                                120,
                              120
                            )}px`,
                          }}
                        />
                        <span className="text-white/50 text-xs w-12 text-right">
                          {citizen.views} vues
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}
      </div>

      {/* FOOTER */}
      <footer className="px-6 py-8 border-t border-white/10 text-center text-white/20 text-xs mt-8">
        <p>Dashboard interne -- Lumina Prime</p>
      </footer>
    </main>
  );
}

/* ── Sub-components ─────────────────────────────────── */

function SenseCard({ sense }: { sense: Sense }) {
  const color = STATUS_COLORS[sense.status];
  const label = STATUS_LABELS[sense.status];
  const displayName = SENSE_DISPLAY_NAMES[sense.name] || sense.name;
  const unit = SENSE_UNITS[sense.name] || '';
  const lowerIsBetter = LOWER_IS_BETTER.has(sense.name);

  // For owner links: split on + for joint ownership (e.g. "echo+pitch")
  const owners = sense.owner.split('+');

  return (
    <div className="bg-[#1a1a3e] rounded-xl border border-white/10 p-5 flex flex-col gap-3 hover:border-white/20 transition">
      {/* Header: name + status dot */}
      <div className="flex items-start justify-between">
        <h3 className="text-sm font-semibold text-white/90 leading-tight">
          {displayName}
        </h3>
        <div className="flex items-center gap-1.5 shrink-0 mt-0.5">
          <span
            className="w-2.5 h-2.5 rounded-full"
            style={{ backgroundColor: color }}
          />
          <span className="text-xs" style={{ color }}>
            {label}
          </span>
        </div>
      </div>

      {/* Value */}
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-bold tabular-nums">
          {sense.value % 1 !== 0 ? sense.value.toFixed(2) : sense.value}
        </span>
        {unit && <span className="text-xs text-white/40">{unit}</span>}
      </div>

      {/* Threshold */}
      <div className="text-xs text-white/30">
        <div className="flex justify-between">
          <span>Seuil</span>
          <span>
            {lowerIsBetter ? '<' : '>'} {sense.threshold}
            {unit === '%' ? '%' : ''}
          </span>
        </div>
      </div>

      {/* Owner */}
      <div className="pt-1 border-t border-white/5 flex items-center gap-1">
        {owners.map((owner, i) => (
          <span key={owner}>
            {i > 0 && <span className="text-white/20 mr-1">+</span>}
            <Link
              href={`/citizen/${owner.trim()}`}
              className="text-xs text-[#a78bfa] hover:underline"
            >
              @{owner.trim()}
            </Link>
          </span>
        ))}
      </div>

      {/* Description */}
      <p className="text-xs text-white/30 leading-snug">{sense.description}</p>
    </div>
  );
}

function MetricCard({
  label,
  value,
  suffix = '',
}: {
  label: string;
  value: number;
  suffix?: string;
}) {
  return (
    <div className="bg-[#1a1a3e] rounded-xl border border-white/10 p-5">
      <p className="text-xs text-white/40 mb-2">{label}</p>
      <p className="text-2xl font-bold tabular-nums">
        {typeof value === 'number' && value % 1 !== 0 ? value.toFixed(2) : value}
        {suffix && <span className="text-sm text-white/40 ml-1">{suffix}</span>}
      </p>
    </div>
  );
}
