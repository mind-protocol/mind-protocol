'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Locale, localeDir, global_t, pricing } from './translations';
import { LangSwitcher } from './LangSwitcher';

export default function LandingPage() {
  const [locale, setLocale] = useState<Locale>('fr');
  const t = global_t[locale];
  const p = pricing[locale];
  const dir = localeDir[locale];

  return (
    <main className="min-h-screen bg-[#0f0c29] text-white" dir={dir}>

      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <div className="text-xl font-bold tracking-wide">
          mind<span className="text-[#a78bfa]">protocol</span>
        </div>
        <div className="flex items-center gap-4">
          <LangSwitcher current={locale} onChange={setLocale} />
          <div className="hidden md:flex items-center gap-6 text-sm">
            <a href="#how" className="text-white/60 hover:text-white transition">{t.nav_how}</a>
            <a href="#difference" className="text-white/60 hover:text-white transition">{t.nav_diff}</a>
            <a href="#pricing" className="text-white/60 hover:text-white transition">{t.nav_pricing}</a>
          </div>
          <Link
            href="https://wa.me/message/mindprotocol"
            className="bg-[#a78bfa] text-[#0f0c29] px-5 py-2 rounded-full font-semibold hover:bg-[#c4b5fd] transition text-sm"
          >
            {t.nav_cta}
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="flex flex-col items-center text-center px-6 pt-24 pb-16">
        <h1 className="text-5xl md:text-7xl font-bold leading-tight max-w-4xl">
          {t.hero_title}<span className="text-[#a78bfa]">{t.hero_highlight}</span>{locale === 'fr' ? ' avec toi' : locale === 'en' ? ' with you' : locale === 'es' ? ' contigo' : locale === 'pt' ? ' com você' : ' معك'}
        </h1>
        <p className="mt-6 text-xl text-white/70 max-w-2xl">{t.hero_sub}</p>
        <div className="mt-10">
          <Link
            href="https://wa.me/message/mindprotocol"
            className="bg-[#25D366] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#128C7E] transition flex items-center gap-2"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/><path d="M12 2C6.477 2 2 6.477 2 12c0 1.89.525 3.66 1.438 5.168L2 22l4.832-1.438A9.955 9.955 0 0012 22c5.523 0 10-4.477 10-10S17.523 2 12 2zm0 18a8 8 0 01-4.243-1.216l-.257-.154-2.871.853.853-2.871-.168-.268A8 8 0 1112 20z"/></svg>
            {t.hero_cta}
          </Link>
        </div>
        <p className="mt-4 text-sm text-white/40">{t.hero_free}</p>
      </section>

      {/* VIDEO PREVIEW */}
      <section className="px-6 pb-20">
        <div className="max-w-3xl mx-auto rounded-2xl bg-gradient-to-br from-[#1a1a3e] to-[#0f0c29] border border-white/10 aspect-video flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">🎬</div>
            <p className="text-white/50 text-lg">{t.video_caption}</p>
          </div>
        </div>
      </section>

      {/* WHAT MAKES US DIFFERENT */}
      <section id="difference" className="px-6 py-20 bg-[#1a1a3e]/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">{t.diff_title}</h2>
          <p className="text-center text-white/60 mb-16 max-w-2xl mx-auto">{t.diff_sub}</p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: '🧠', title: t.card1_title, desc: t.card1_desc },
              { icon: '🛠️', title: t.card2_title, desc: t.card2_desc },
              { icon: '🌆', title: t.card3_title, desc: t.card3_desc },
            ].map((card, i) => (
              <div key={i} className="bg-[#0f0c29] rounded-xl p-8 border border-white/10">
                <div className="text-4xl mb-4">{card.icon}</div>
                <h3 className="text-xl font-semibold mb-3">{card.title}</h3>
                <p className="text-white/60">{card.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="px-6 py-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-16">{t.how_title}</h2>
          <div className="space-y-12">
            {[
              { step: '01', title: t.step1_title, desc: t.step1_desc },
              { step: '02', title: t.step2_title, desc: t.step2_desc },
              { step: '03', title: t.step3_title, desc: t.step3_desc },
              { step: '04', title: t.step4_title, desc: t.step4_desc },
            ].map((s, i) => (
              <div key={i} className="flex items-start gap-6">
                <div className="text-[#a78bfa] text-2xl font-bold w-12 shrink-0">{s.step}</div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">{s.title}</h3>
                  <p className="text-white/60">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WOW EFFECTS */}
      <section className="px-6 py-20 bg-[#1a1a3e]/50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-4">{t.wow_title}</h2>
          <p className="text-center text-white/60 mb-16">{t.wow_sub}</p>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '💬', title: t.wow1_title, desc: t.wow1_desc },
              { icon: '📹', title: t.wow2_title, desc: t.wow2_desc },
              { icon: '🎨', title: t.wow3_title, desc: t.wow3_desc },
              { icon: '👋', title: t.wow4_title, desc: t.wow4_desc },
            ].map((w, i) => (
              <div key={i} className="bg-[#0f0c29] rounded-xl p-6 border border-[#a78bfa]/20">
                <p className="text-[#a78bfa] font-semibold mb-2">{w.icon} {w.title}</p>
                <p className="text-white/60 text-sm">{w.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* PRICING */}
      <section id="pricing" className="px-6 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">{t.pricing_title}</h2>
          <p className="text-white/60 mb-12">{t.pricing_sub}</p>
          <div className="grid md:grid-cols-2 gap-8 max-w-2xl mx-auto">
            <div className="bg-[#1a1a3e] rounded-xl p-8 border border-white/10">
              <h3 className="text-lg font-semibold mb-2">{t.free_label}</h3>
              <div className="text-4xl font-bold mb-4">{p.free}</div>
              <ul className="text-left text-white/60 space-y-3 text-sm">
                {t.free_features.map((f, i) => (
                  <li key={i}>{f.startsWith('○') ? f : `✓ ${f}`}</li>
                ))}
              </ul>
            </div>
            <div className="bg-gradient-to-br from-[#a78bfa]/20 to-[#0f0c29] rounded-xl p-8 border border-[#a78bfa]/40">
              <h3 className="text-lg font-semibold mb-2 text-[#a78bfa]">{t.paid_label}</h3>
              <div className="text-4xl font-bold mb-4">{p.paidAmount}</div>
              <ul className="text-left text-white/60 space-y-3 text-sm">
                {t.paid_features.map((f, i) => (
                  <li key={i} className={i > 0 ? 'text-white font-semibold' : ''}>✓ {f}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* PERSONA LINKS */}
      <section className="px-6 py-20 bg-[#1a1a3e]/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-8">{t.personas_title}</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { href: '/landing/entrepreneur', icon: '🚀', title: t.p_entrepreneur, sub: t.p_entrepreneur_sub },
              { href: '/landing/business', icon: '💼', title: t.p_business, sub: t.p_business_sub },
              { href: '/landing/curious', icon: '✨', title: t.p_curious, sub: t.p_curious_sub },
            ].map((persona, i) => (
              <Link key={i} href={persona.href} className="bg-[#0f0c29] rounded-xl p-6 border border-white/10 hover:border-[#a78bfa]/40 transition group">
                <div className="text-3xl mb-3">{persona.icon}</div>
                <h3 className="font-semibold group-hover:text-[#a78bfa] transition">{persona.title}</h3>
                <p className="text-sm text-white/50 mt-2">{persona.sub}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="px-6 py-12 border-t border-white/10 text-center text-white/30 text-sm">
        <p>{t.footer1}</p>
        <p className="mt-2">{t.footer2}</p>
      </footer>
    </main>
  );
}
