'use client';

interface CitizenStatusProps {
  citizenHandle: string;
  district: string;
  status: string;
}

const MOODS = ['Concentre', 'Creatif', 'Pensif', 'Energique', 'En repos'] as const;
type Mood = (typeof MOODS)[number];

const MOOD_DISPLAY: Record<Mood, { label: string; emoji: string }> = {
  'Concentre': { label: 'Concentr\u00e9', emoji: '\uD83C\uDFAF' },
  'Creatif': { label: 'Cr\u00e9atif', emoji: '\u2728' },
  'Pensif': { label: 'Pensif', emoji: '\uD83D\uDCAD' },
  'Energique': { label: '\u00C9nergique', emoji: '\u26A1' },
  'En repos': { label: 'En repos', emoji: '\uD83C\uDF19' },
};

const STATUS_LINES: string[] = [
  'En train de travailler sur un projet',
  'Au caf\u00e9 pr\u00e8s du canal',
  'En discussion avec un citoyen',
  'Exploration des jardins de donn\u00e9es',
  'R\u00e9flexion dans les Tours du Savoir',
  'Session de cr\u00e9ation au Nexus',
  'Calibrage au C\u0153ur Radiant',
  'Prototypage aux Champs d\u2019Innovation',
  'D\u00e9bat sur la Resonance Plaza',
  'Forge en cours \u00e0 l\u2019Arsenal',
];

function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash);
}

function getParisHour(): number {
  const now = new Date();
  const parisTime = new Date(
    now.toLocaleString('en-US', { timeZone: 'Europe/Paris' })
  );
  return parisTime.getHours();
}

function getEnergy(hour: number): number {
  // Circadian curve: peak at 14h Paris, trough at 3h
  // Sine wave shifted so peak is at 14 and trough at ~2-3
  const radians = ((hour - 14) / 24) * 2 * Math.PI;
  const raw = (Math.cos(radians) + 1) / 2; // 0..1, peak at hour 14
  return Math.round(raw * 100);
}

function getMood(handle: string, hour: number): Mood {
  const seed = hashCode(handle) + Math.floor(hour / 3);
  return MOODS[seed % MOODS.length];
}

function getStatusLine(handle: string, hour: number): string {
  const seed = hashCode(handle) + Math.floor(hour / 2);
  return STATUS_LINES[seed % STATUS_LINES.length];
}

function getEnergyDotColor(energy: number): string {
  if (energy >= 70) return '#25D366';
  if (energy >= 40) return '#a78bfa';
  return '#6b7280';
}

export default function CitizenStatus({
  citizenHandle,
  district,
  status,
}: CitizenStatusProps) {
  const hour = getParisHour();
  const energy = getEnergy(hour);
  const mood = getMood(citizenHandle, hour);
  const moodInfo = MOOD_DISPLAY[mood];
  const statusLine = status || getStatusLine(citizenHandle, hour);
  const dotColor = getEnergyDotColor(energy);

  return (
    <div className="flex flex-col gap-1.5 text-sm text-white/60">
      {/* Status line */}
      <div className="flex items-center gap-2">
        <span
          className="inline-block h-2 w-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: dotColor }}
        />
        <span className="truncate">{statusLine}</span>
      </div>

      {/* Mood + energy */}
      <div className="flex items-center gap-3">
        <span className="flex items-center gap-1">
          <span>{moodInfo.emoji}</span>
          <span>{moodInfo.label}</span>
        </span>
        <span className="text-white/40">&middot;</span>
        <span className="text-white/40">{district}</span>
        <span className="text-white/40">&middot;</span>
        <span className="text-white/40">{energy}% \u00e9nergie</span>
      </div>

      {/* Energy bar */}
      <div className="h-1 w-full rounded-full bg-white/10 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{
            width: `${energy}%`,
            background: 'linear-gradient(to right, #a78bfa, #25D366)',
          }}
        />
      </div>
    </div>
  );
}
