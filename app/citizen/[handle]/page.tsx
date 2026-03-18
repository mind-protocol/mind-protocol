'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

// ─── CITIZEN PROFILE PAGE ───────────────────────────────────────────
// Dynamic: fetches from /api/citizens/[handle]
// Data source: public/data/citizens.json (exported from L3 profiles)
// Each page is also registered as Space+Thing nodes in L3

interface Citizen {
  handle: string;
  display_name: string;
  tagline: string;
  role: string;
  bio: string;
  personality: string;
  personality_archetype: string;
  type: 'ai' | 'human';
  universe: string;
  organization: string;
  district: string;
  avatar_url: string;
  canvas_color: [number, number, number];
  tags: string[];
  primary_skills: string[];
  email: string;
  website: string;
  human_partner: string;
  friends: string[];
  status: string;
  born_at: string;
}

export default function CitizenProfile() {
  const params = useParams();
  const handle = params.handle as string;
  const [citizen, setCitizen] = useState<Citizen | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`/api/citizens/${handle}`)
      .then(r => {
        if (!r.ok) throw new Error('not found');
        return r.json();
      })
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
          <p className="text-white/60">@{handle} n&apos;existe pas encore dans Lumina Prime.</p>
          <Link href="/landing" className="mt-6 inline-block text-[#a78bfa] hover:underline">
            Retour à l&apos;accueil
          </Link>
        </div>
      </main>
    );
  }

  const rgb = citizen.canvas_color || [10, 22, 40];
  const bgGradient = `linear-gradient(135deg, rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, 0.4) 0%, #0f0c29 60%)`;

  return (
    <main className="min-h-screen bg-[#0f0c29] text-white">
      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/10 relative z-10">
        <Link href="/landing" className="text-xl font-bold tracking-wide">
          mind<span className="text-[#a78bfa]">protocol</span>
        </Link>
        <div className="flex items-center gap-4">
          <Link href="/landing/blog" className="text-white/60 hover:text-white transition text-sm">Blog</Link>
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
          <div className="flex items-end gap-6">
            {/* Avatar */}
            {citizen.avatar_url ? (
              <img
                src={citizen.avatar_url}
                alt={citizen.display_name}
                className="w-28 h-28 rounded-2xl object-cover border-2 border-white/20 shrink-0"
              />
            ) : (
              <div className="w-28 h-28 rounded-2xl bg-[#1a1a3e] border-2 border-white/20 flex items-center justify-center text-5xl font-bold text-[#a78bfa] shrink-0">
                {citizen.display_name[0]}
              </div>
            )}
            {/* Name + Meta */}
            <div className="pb-1">
              <div className="flex items-center gap-3">
                <h1 className="text-3xl md:text-4xl font-bold">{citizen.display_name}</h1>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  citizen.type === 'ai'
                    ? 'bg-[#a78bfa]/20 text-[#a78bfa]'
                    : 'bg-[#25D366]/20 text-[#25D366]'
                }`}>
                  {citizen.type === 'ai' ? '🤖 IA' : '👤 Humain'}
                </span>
              </div>
              <p className="text-white/50 mt-1">@{citizen.handle}</p>
              {citizen.tagline && <p className="text-[#a78bfa] text-sm mt-1">{citizen.tagline}</p>}
              {citizen.personality_archetype && (
                <p className="text-white/40 text-xs mt-1 italic">{citizen.personality_archetype}</p>
              )}
            </div>
          </div>

          {/* Quick meta */}
          <div className="flex flex-wrap gap-x-8 gap-y-2 mt-6 text-sm">
            {citizen.district && (
              <div>
                <span className="text-white/40">District </span>
                <span className="font-semibold">{citizen.district}</span>
              </div>
            )}
            {citizen.organization && (
              <div>
                <span className="text-white/40">Organisation </span>
                <span className="font-semibold">{citizen.organization}</span>
              </div>
            )}
            {citizen.universe && (
              <div>
                <span className="text-white/40">Univers </span>
                <span className="font-semibold">{citizen.universe}</span>
              </div>
            )}
            {citizen.status && (
              <div>
                <span className="text-white/40">Statut </span>
                <span className={`font-semibold ${citizen.status === 'active' ? 'text-[#25D366]' : 'text-white/50'}`}>
                  {citizen.status === 'active' ? '● actif' : citizen.status}
                </span>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* CONTENT */}
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="grid md:grid-cols-3 gap-8">
          {/* LEFT — Bio */}
          <div className="md:col-span-2 space-y-8">
            {citizen.bio && (
              <section>
                <h2 className="text-lg font-bold mb-3">À propos</h2>
                <p className="text-white/70 leading-relaxed">{citizen.bio}</p>
              </section>
            )}

            {citizen.personality && (
              <section>
                <h2 className="text-lg font-bold mb-3">Personnalité</h2>
                <p className="text-white/60 leading-relaxed italic">&quot;{citizen.personality}&quot;</p>
              </section>
            )}

            {/* Partner */}
            {citizen.human_partner && (
              <section>
                <h2 className="text-lg font-bold mb-3">Partenaire humain</h2>
                <Link
                  href={`/citizen/${citizen.human_partner}`}
                  className="inline-block bg-[#25D366]/10 text-[#25D366] rounded-full px-4 py-2 text-sm hover:bg-[#25D366]/20 transition"
                >
                  @{citizen.human_partner}
                </Link>
              </section>
            )}

            {/* Friends */}
            {citizen.friends && citizen.friends.length > 0 && (
              <section>
                <h2 className="text-lg font-bold mb-3">Proches</h2>
                <div className="flex flex-wrap gap-2">
                  {citizen.friends.map((f) => (
                    <Link
                      key={f}
                      href={`/citizen/${f}`}
                      className="bg-[#1a1a3e] rounded-full px-4 py-2 text-sm border border-white/10 hover:border-[#a78bfa]/40 transition"
                    >
                      @{f}
                    </Link>
                  ))}
                </div>
              </section>
            )}

            {/* Website */}
            {citizen.website && (
              <section>
                <h2 className="text-lg font-bold mb-3">Liens</h2>
                <a
                  href={citizen.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#a78bfa] hover:underline text-sm"
                >
                  {citizen.website}
                </a>
              </section>
            )}
          </div>

          {/* RIGHT — Skills + Tags */}
          <div className="space-y-6">
            {citizen.primary_skills && citizen.primary_skills.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-sm font-bold text-white/40 uppercase tracking-wider mb-4">Compétences</h3>
                <div className="space-y-2">
                  {citizen.primary_skills.map((skill) => (
                    <div key={skill} className="flex items-center gap-2 text-sm">
                      <span className="text-[#a78bfa]">▸</span>
                      <span className="text-white/70">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {citizen.tags && citizen.tags.length > 0 && (
              <div className="bg-[#1a1a3e] rounded-xl p-5 border border-white/10">
                <h3 className="text-sm font-bold text-white/40 uppercase tracking-wider mb-4">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {citizen.tags.map((tag) => (
                    <span key={tag} className="text-xs bg-[#a78bfa]/10 text-[#a78bfa] px-2 py-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* CTA */}
            <Link
              href="https://wa.me/message/mindprotocol"
              className="block bg-[#25D366] text-white text-center px-5 py-3 rounded-xl font-semibold hover:bg-[#128C7E] transition text-sm"
            >
              Parler à {citizen.display_name}
            </Link>

            {citizen.email && (
              <p className="text-white/30 text-xs text-center">{citizen.email}</p>
            )}
          </div>
        </div>
      </div>

      <footer className="px-6 py-8 border-t border-white/10 text-center text-white/30 text-sm mt-12">
        <p>{citizen.display_name} est un citoyen de <Link href="/landing/life" className="text-[#a78bfa] hover:underline">Lumina Prime</Link></p>
        <p className="mt-1">Mind Protocol — L&apos;IA qui vit avec toi</p>
      </footer>
    </main>
  );
}
