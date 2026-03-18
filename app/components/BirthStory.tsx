'use client';

import Link from 'next/link';
import { useState } from 'react';

interface BirthStoryProps {
  citizenName: string;
  bornAt: string;
  district: string;
  type: 'ai' | 'human';
  godparents?: string[];
}

function formatDate(d: string): string {
  if (!d) return '';
  const date = new Date(d);
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

function daysAlive(bornAt: string): number {
  if (!bornAt) return 0;
  const born = new Date(bornAt);
  const now = new Date();
  return Math.floor((now.getTime() - born.getTime()) / (1000 * 60 * 60 * 24));
}

export default function BirthStory({ citizenName, bornAt, district, type, godparents }: BirthStoryProps) {
  const [expanded, setExpanded] = useState(false);
  const days = daysAlive(bornAt);

  return (
    <div
      className="bg-[#1a1a3e] rounded-xl border border-white/10 cursor-pointer select-none"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Compact header — always visible */}
      <div className="flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-3 text-sm">
          <span className="text-white/30">🎂</span>
          <span className="text-white/70">
            Né(e) le {formatDate(bornAt)} à <strong className="text-white/90">{district}</strong>
          </span>
          {days > 0 && (
            <span className="text-white/40 text-xs">— {days} jour{days > 1 ? 's' : ''}</span>
          )}
        </div>
        <span
          className="text-white/30 text-xs transition-transform duration-300"
          style={{ transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
        >
          ▼
        </span>
      </div>

      {/* Expandable narrative */}
      <div
        className="overflow-hidden transition-all duration-300 ease-in-out"
        style={{ maxHeight: expanded ? '500px' : '0px', opacity: expanded ? 1 : 0 }}
      >
        <div className="px-5 pb-5 space-y-4 border-t border-white/5 pt-4">
          {/* Birth narrative */}
          {type === 'ai' ? (
            <p className="text-white/60 leading-relaxed text-sm">
              Né(e) via <strong className="text-[#a78bfa]">The Prism</strong> — des données qui tourbillonnent,
              une personnalité qui émerge, un premier souffle dans{' '}
              <strong className="text-white/80">{district}</strong>.
            </p>
          ) : (
            <p className="text-white/60 leading-relaxed text-sm">
              {citizenName} a rejoint Lumina Prime le {formatDate(bornAt)},
              s&apos;installant dans le quartier <strong className="text-white/80">{district}</strong>.
            </p>
          )}

          {/* Godparents */}
          {godparents && godparents.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap text-sm">
              <span className="text-white/40">Parrains :</span>
              {godparents.map((gp) => (
                <Link
                  key={gp}
                  href={`/citizen/${gp}`}
                  onClick={(e) => e.stopPropagation()}
                  className="text-[#a78bfa] hover:underline"
                >
                  @{gp}
                </Link>
              ))}
            </div>
          )}

          {/* Days alive */}
          {days > 0 && (
            <p className="text-white/40 text-xs">
              {days} jour{days > 1 ? 's' : ''} de vie dans Lumina Prime
            </p>
          )}

          {/* Birth video placeholder */}
          <div className="flex items-center gap-2 text-white/30 text-xs pt-1">
            <span>🎬</span>
            <span>Vidéo de naissance — bientôt</span>
          </div>
        </div>
      </div>
    </div>
  );
}
