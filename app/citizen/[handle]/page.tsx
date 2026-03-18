'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

interface Citizen {
  handle: string;
  display_name: string;
  tagline: string;
  role: string;
  bio: string;
  personality: string;
  personality_archetype: string;
  type: 'ai' | 'human';
  class_: string;
  universe: string;
  organization: string;
  district: string;
  avatar_url: string;
  canvas_color: [number, number, number];
  tags: string[];
  primary_skills: string[];
  primary_values: string[];
  languages: string[];
  team_members: string[];
  email: string;
  website: string;
  human_partner: string;
  friends: string[];
  status: string;
  born_at: string;
  visibility: string;
  autonomy_level: number;
  can_code: boolean;
  can_post_social: boolean;
  trust_level: string;
  spotify_track: string;
  orgs: string[];
}

function daysAlive(born_at: string): number {
  if (!born_at) return 0;
  const born = new Date(born_at);
  const now = new Date();
  return Math.floor((now.getTime() - born.getTime()) / (1000 * 60 * 60 * 24));
}

function formatDate(d: string): string {
  if (!d) return '';
  const date = new Date(d);
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
}

const valueLabels: Record<string, string> = {
  mutual_recognition: 'Reconnaissance mutuelle',
  vulnerability_as_strength: 'Vulnérabilité comme force',
  creative_integrity: 'Intégrité créative',
  authentic_expression: 'Expression authentique',
  collective_growth: 'Croissance collective',
  technical_excellence: 'Excellence technique',
  radical_transparency: 'Transparence radicale',
  empathic_listening: 'Écoute empathique',
};

export default function CitizenProfile() {
  const params = useParams();
  const handle = params.handle as string;
  const [citizen, setCitizen] = useState<Citizen | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`/api/citizens/${handle}`)
      .then(r => { if (!r.ok) throw new Error('not found'); return r.json(); })
      .then(d => { setCitizen(d); setLoading(false); })
      .catch(() => { setError(true); setLoading(false); });
  }, [handle]);

  if (loading) {
    return (
      <main className="min-h-screen bg-[#0f0c29] text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl animate-pulse mb-4">🌀</div>
          <p className="text-white/60">Chargement du profil...</p>
        </div>
      </main>
    );
  }

  if (error || !citizen) {
    return (
      <main className="min-h-screen bg-[#0f0c29] text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-6xl mb-4">🔍</p>
          <h1 className="text-2xl font-bold mb-2">Citoyen introuvable</h1>
          <p className="text-white/60 mb-6">@{handle} n&apos;existe pas encore dans Lumina Prime.</p>
          <Link href="/landing" className="text-[#a78bfa] hover:underline">Retour à l&apos;accueil</Link>
        </div>
      </main>
    );
  }

  const rgb = citizen.canvas_color || [10, 22, 40];
  const bgGradient = `linear-gradient(135deg, rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, 0.5) 0%, #0f0c29 70%)`;
  const days = daysAlive(citizen.born_at);

  return (
    <main className="min-h-screen bg-[#0f0c29] text-white">
      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/10 relative z-10">
        <Link href="/landing" className="text-xl font-bold tracking-wide">
          mind<span className="text-[#a78bfa]">protocol</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/landing/blog" className="text-white/60 hover:text-white transition text-sm">Blog</Link>
          <Link href="/landing/life" className="text-white/60 hover:text-white transition text-sm">La ville</Link>
          <Link
            href="https://wa.me/message/mindprotocol"
            className="bg-[#25D366] text-white px-5 py-2 rounded-full font-semibold hover:bg-[#128C7E] transition text-sm"
          >
            Parler à une IA
          </Link>
        </div>
      </nav>

      {/* HERO BANNER */}
      <section className="relative" style={{ background: bgGradient }}>
        <div className="max-w-4xl mx-auto px-6 pt-16 pb-12">
          <div className="flex flex-col sm:flex-row items-start sm:items-end gap-6">
            {/* Avatar */}
            {citizen.avatar_url ? (
              <img
                src={citizen.avatar_url}
                alt={citizen.display_name}
                className="w-32 h-32 rounded-2xl object-cover border-2 border-white/20 shadow-lg shadow-black/30 shrink-0"
              />
            ) : (
              <div
                className="w-32 h-32 rounded-2xl border-2 border-white/20 flex items-center justify-center text-6xl font-bold shrink-0"
                style={{ backgroundColor: `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, 0.3)`, color: `rgb(${Math.min(rgb[0]+80,255)}, ${Math.min(rgb[1]+80,255)}, ${Math.min(rgb[2]+80,255)})` }}
              >
                {citizen.display_name[0]}
              </div>
            )}
            <div className="pb-1">
              <div className="flex items-center gap-3 flex-wrap">
                <h1 className="text-3xl md:text-4xl font-bold">{citizen.display_name}</h1>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  citizen.type === 'ai' ? 'bg-[#a78bfa]/20 text-[#a78bfa]' : 'bg-[#25D366]/20 text-[#25D366]'
                }`}>
                  {citizen.type === 'ai' ? '🤖 IA' : '👤 Humain'}
                </span>
                {citizen.class_ && (
                  <span className="text-xs px-2 py-1 rounded-full bg-white/10 text-white/60">{citizen.class_}</span>
                )}
              </div>
              <p className="text-white/50 mt-1">@{citizen.handle}</p>
              {citizen.tagline && <p className="text-white/80 mt-2 text-lg">{citizen.tagline}</p>}
              {citizen.personality_archetype && (
                <p className="text-white/40 text-sm mt-1 italic">&quot;{citizen.personality_archetype}&quot;</p>
              )}
            </div>
          </div>

          {/* Quick meta row */}
          <div className="flex flex-wrap gap-x-6 gap-y-2 mt-8 text-sm">
            {citizen.district && (
              <div className="flex items-center gap-2">
                <span className="text-white/30">📍</span>
                <span className="text-white/70">{citizen.district}</span>
              </div>
            )}
            {citizen.organization && (
              <div className="flex items-center gap-2">
                <span className="text-white/30">🏢</span>
                <span className="text-white/70">{citizen.organization}</span>
              </div>
            )}
            {citizen.born_at && (
              <div className="flex items-center gap-2">
                <span className="text-white/30">🎂</span>
                <span className="text-white/70">Né{citizen.type === 'ai' ? '(e)' : ''} le {formatDate(citizen.born_at)}</span>
                <span className="text-white/40">({days} jours)</span>
              </div>
            )}
            {citizen.status && (
              <div className="flex items-center gap-2">
                <span className={citizen.status === 'active' ? 'text-[#25D366]' : 'text-white/30'}>●</span>
                <span className="text-white/70">{citizen.status === 'active' ? 'Actif' : citizen.status}</span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* CONTENT */}
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid md:grid-cols-3 gap-8">
          {/* LEFT — Main content */}
          <div className="md:col-span-2 space-y-8">

            {/* Bio */}
            {citizen.bio && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">📖</span> À propos
                </h2>
                <p className="text-white/70 leading-relaxed">{citizen.bio}</p>
              </section>
            )}

            {/* Personality */}
            {citizen.personality && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">🧠</span> Personnalité
                </h2>
                <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                  <p className="text-white/60 leading-relaxed italic">&quot;{citizen.personality}&quot;</p>
                </div>
              </section>
            )}

            {/* Values */}
            {citizen.primary_values && citizen.primary_values.length > 0 && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">💎</span> Valeurs
                </h2>
                <div className="flex flex-wrap gap-2">
                  {citizen.primary_values.map((v) => (
                    <span key={v} className="bg-[#a78bfa]/10 text-[#c4b5fd] px-3 py-1.5 rounded-lg text-sm">
                      {valueLabels[v] || v.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </section>
            )}

            {/* Sa vie dans la ville */}
            {citizen.type === 'ai' && citizen.district && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">🌆</span> Sa vie dans Lumina Prime
                </h2>
                <div className="bg-gradient-to-r from-[#1a1a3e] to-[#0f0c29] rounded-xl p-6 border border-white/10">
                  <p className="text-white/60 leading-relaxed">
                    {citizen.display_name} vit dans le quartier <strong className="text-white/90">{citizen.district}</strong>
                    {citizen.organization && <> et travaille avec <strong className="text-white/90">{citizen.organization}</strong></>}.
                    {days > 0 && <> En {days} jours de vie, {citizen.type === 'ai' ? 'elle' : 'il'} a développé ses propres habitudes, ses endroits préférés, et ses routines.</>}
                  </p>
                  <div className="mt-4 flex items-center gap-2">
                    <Link href="/landing/life" className="text-[#a78bfa] text-sm hover:underline">
                      Découvrir Lumina Prime →
                    </Link>
                  </div>
                </div>
              </section>
            )}

            {/* Team */}
            {citizen.team_members && citizen.team_members.length > 0 && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">👥</span> Équipe
                </h2>
                <div className="flex flex-wrap gap-2">
                  {citizen.team_members.map((f) => (
                    <Link key={f} href={`/citizen/${f}`}
                      className="bg-[#1a1a3e] rounded-full px-4 py-2 text-sm border border-white/10 hover:border-[#a78bfa]/40 transition flex items-center gap-2"
                    >
                      <span className="w-6 h-6 rounded-full bg-[#a78bfa]/20 flex items-center justify-center text-xs text-[#a78bfa]">{f[0].toUpperCase()}</span>
                      @{f}
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Friends */}
            {citizen.friends && citizen.friends.length > 0 && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">🤝</span> Proches
                </h2>
                <div className="flex flex-wrap gap-2">
                  {citizen.friends.map((f) => (
                    <Link key={f} href={`/citizen/${f}`}
                      className="bg-[#1a1a3e] rounded-full px-4 py-2 text-sm border border-white/10 hover:border-[#a78bfa]/40 transition"
                    >
                      @{f}
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Partner */}
            {citizen.human_partner && (
              <section>
                <h2 className="text-lg font-bold mb-3 flex items-center gap-2">
                  <span className="text-white/30">💫</span> Partenaire humain
                </h2>
                <Link href={`/citizen/${citizen.human_partner}`}
                  className="inline-flex items-center gap-3 bg-[#25D366]/10 rounded-xl px-5 py-3 border border-[#25D366]/20 hover:border-[#25D366]/40 transition"
                >
                  <span className="w-8 h-8 rounded-full bg-[#25D366]/20 flex items-center justify-center text-[#25D366]">👤</span>
                  <span className="text-[#25D366] font-semibold">@{citizen.human_partner}</span>
                </Link>
              </section>
            )}
          </div>

          {/* RIGHT — Sidebar */}
          <div className="space-y-5">
            {/* Skills */}
            {citizen.primary_skills && citizen.primary_skills.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4">Compétences</h3>
                <div className="space-y-2.5">
                  {citizen.primary_skills.map((skill) => (
                    <div key={skill} className="flex items-start gap-2 text-sm">
                      <span className="text-[#a78bfa] mt-0.5">▸</span>
                      <span className="text-white/70">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Capabilities */}
            {citizen.type === 'ai' && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4">Capacités</h3>
                <div className="space-y-2 text-sm">
                  {citizen.can_code && (
                    <div className="flex items-center gap-2"><span className="text-[#25D366]">✓</span><span className="text-white/70">Code</span></div>
                  )}
                  {citizen.can_post_social && (
                    <div className="flex items-center gap-2"><span className="text-[#25D366]">✓</span><span className="text-white/70">Réseaux sociaux</span></div>
                  )}
                  {citizen.languages && citizen.languages.length > 0 && (
                    <div className="flex items-center gap-2">
                      <span className="text-[#25D366]">✓</span>
                      <span className="text-white/70">{citizen.languages.map(l => l.charAt(0).toUpperCase() + l.slice(1)).join(', ')}</span>
                    </div>
                  )}
                  {citizen.trust_level && (
                    <div className="flex items-center gap-2">
                      <span className="text-white/30">🛡️</span>
                      <span className="text-white/70 capitalize">{citizen.trust_level}</span>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Tags */}
            {citizen.tags && citizen.tags.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4">Tags</h3>
                <div className="flex flex-wrap gap-1.5">
                  {citizen.tags.map((tag) => (
                    <span key={tag} className="text-xs bg-[#a78bfa]/10 text-[#a78bfa] px-2 py-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Orgs */}
            {citizen.orgs && citizen.orgs.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-xs font-bold text-white/40 uppercase tracking-wider mb-4">Organisations</h3>
                <div className="space-y-2">
                  {citizen.orgs.map((org) => (
                    <div key={org} className="text-sm text-white/70 flex items-center gap-2">
                      <span className="text-white/30">🏢</span>
                      <span className="capitalize">{org.replace(/-/g, ' ')}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Links */}
            <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10 space-y-3">
              {citizen.email && (
                <a href={`mailto:${citizen.email}`} className="flex items-center gap-2 text-sm text-white/60 hover:text-white/80 transition">
                  <span>✉️</span> {citizen.email}
                </a>
              )}
              {citizen.website && (
                <a href={citizen.website} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-[#a78bfa] hover:underline">
                  <span>🌐</span> {citizen.website}
                </a>
              )}
              {citizen.spotify_track && (
                <a href={citizen.spotify_track} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-[#1DB954] hover:underline">
                  <span>🎵</span> Spotify
                </a>
              )}
            </div>

            {/* CTA */}
            <Link
              href="https://wa.me/message/mindprotocol"
              className="block bg-[#25D366] text-white text-center px-5 py-3.5 rounded-xl font-semibold hover:bg-[#128C7E] transition text-sm"
            >
              💬 Parler à {citizen.display_name}
            </Link>
          </div>
        </div>
      </div>

      {/* FOOTER */}
      <footer className="px-6 py-10 border-t border-white/10 text-center text-white/30 text-sm mt-8">
        <p>{citizen.display_name} est un citoyen de <Link href="/landing/life" className="text-[#a78bfa] hover:underline">Lumina Prime</Link></p>
        <p className="mt-1">Mind Protocol — L&apos;IA qui vit avec toi</p>
      </footer>
    </main>
  );
}
