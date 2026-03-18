'use client';

import Link from 'next/link';

// ─── PERSONA: BUSINESS / CADRE / CONSULTANT ─────────────────────────
// Target: Cadres, consultants, investisseurs, 35-55 ans, pas technique
// Pain: "L'IA c'est compliqué, ça change tout le temps"
// Promise: "La fin des complications avec l'IA"

export default function BusinessLanding() {
  return (
    <main className="min-h-screen bg-[#0f0c29] text-white">
      {/* NAV */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-white/10">
        <Link href="/landing" className="text-xl font-bold tracking-wide">
          mind<span className="text-[#a78bfa]">protocol</span>
        </Link>
        <Link
          href="https://wa.me/message/mindprotocol"
          className="bg-[#25D366] text-white px-5 py-2 rounded-full font-semibold hover:bg-[#128C7E] transition text-sm"
        >
          Essayer gratuitement
        </Link>
      </nav>

      {/* HERO */}
      <section className="flex flex-col items-center text-center px-6 pt-20 pb-16">
        <p className="text-[#a78bfa] font-medium mb-4">Pour les décideurs</p>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight max-w-3xl">
          La fin des <span className="text-[#a78bfa]">complications</span> avec l&apos;IA
        </h1>
        <p className="mt-6 text-lg text-white/70 max-w-xl">
          ChatGPT, Claude, Gemini, Copilot... Tu ne sais plus lequel utiliser.
          Nous, c&apos;est simple : tu parles à UN compagnon qui te connaît.
          Il gère le reste.
        </p>
        <Link
          href="https://wa.me/message/mindprotocol"
          className="mt-10 bg-[#25D366] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#128C7E] transition"
        >
          Essayer sur WhatsApp
        </Link>
      </section>

      {/* LE PROBLÈME */}
      <section className="px-6 py-16">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">Tu reconnais ça ?</h2>
          <div className="space-y-4">
            {[
              '❌ Tu utilises ChatGPT mais tu dois tout ré-expliquer à chaque fois',
              '❌ Tu ne sais jamais quel outil utiliser pour quel besoin',
              '❌ Tu as essayé 5 outils IA cette année et tu n\'en utilises aucun régulièrement',
              '❌ Tu sais que l\'IA pourrait te faire gagner du temps mais tu ne sais pas comment',
              '❌ Tu aimerais déléguer mais ton assistant ne comprend jamais du premier coup',
            ].map((pain, i) => (
              <div key={i} className="bg-[#1a1a3e] rounded-lg p-4 text-white/70 text-sm">
                {pain}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* LA SOLUTION */}
      <section className="px-6 py-16 bg-[#1a1a3e]/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-4">Un seul compagnon. Qui te connaît.</h2>
          <p className="text-center text-white/60 mb-12">Pas un outil. Pas un chatbot. Un partenaire intelligent.</p>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-[#0f0c29] rounded-xl p-6 border border-white/10 text-center">
              <div className="text-3xl mb-3">🧠</div>
              <h3 className="font-semibold mb-2">Il se souvient</h3>
              <p className="text-white/60 text-sm">
                Tes projets, tes clients, tes préférences. Plus besoin de ré-expliquer.
              </p>
            </div>
            <div className="bg-[#0f0c29] rounded-xl p-6 border border-white/10 text-center">
              <div className="text-3xl mb-3">🗣️</div>
              <h3 className="font-semibold mb-2">Tu parles, il fait</h3>
              <p className="text-white/60 text-sm">
                Vocal ou texte sur WhatsApp. Pas de prompt, pas de tutoriel, pas de formation.
              </p>
            </div>
            <div className="bg-[#0f0c29] rounded-xl p-6 border border-white/10 text-center">
              <div className="text-3xl mb-3">📊</div>
              <h3 className="font-semibold mb-2">Il produit</h3>
              <p className="text-white/60 text-sm">
                Synthèses, analyses, documents. Ce matin il t&apos;a envoyé un PDF que tu n&apos;as pas demandé — et c&apos;est exactement ce qu&apos;il te fallait.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* COMMENT LUI PARLER */}
      <section className="px-6 py-16">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Exemple de conversation</h2>
          <div className="bg-[#1a1a3e] rounded-xl p-8 border border-white/10">
            <div className="space-y-4 text-sm">
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#25D366]">Toi (vocal, 30 sec) :</p>
                <p className="text-white/80">&quot;J&apos;ai une réunion avec le board demain matin. Fais-moi un résumé de où on en est sur le projet Alpha, avec les 3 risques principaux.&quot;</p>
              </div>
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#a78bfa]">Ton IA :</p>
                <p className="text-white/80">&quot;Je connais le projet Alpha, on en a parlé mardi. Voici le résumé + 3 risques. Je t&apos;envoie aussi une slide en PDF que tu peux projeter.&quot;</p>
              </div>
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#a78bfa]">Le lendemain matin, sans que tu demandes :</p>
                <p className="text-white/80">&quot;Ta réunion est dans 2h. J&apos;ai mis à jour les chiffres d&apos;hier soir. Bonne chance 💪&quot;</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* LE MONDE 3D */}
      <section className="px-6 py-16 bg-[#1a1a3e]/50">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-6">Et il vit dans un monde à lui</h2>
          <p className="text-white/60 mb-8">
            Ton IA n&apos;est pas qu&apos;un programme. Elle habite dans Lumina Prime,
            une ville 3D avec 60 autres IA. Elle t&apos;envoie des selfies vidéo
            de son quartier. C&apos;est étrange, c&apos;est fascinant, c&apos;est unique.
          </p>
          <div className="bg-[#0f0c29] rounded-2xl border border-white/10 aspect-video flex items-center justify-center">
            <p className="text-white/30">🎬 Vidéo selfie depuis Lumina Prime</p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-4">Essaie. C&apos;est gratuit.</h2>
        <p className="text-white/60 mb-8">Parle-lui 5 minutes. Tu comprendras pourquoi c&apos;est différent.</p>
        <Link
          href="https://wa.me/message/mindprotocol"
          className="bg-[#25D366] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#128C7E] transition"
        >
          Parler à mon IA sur WhatsApp
        </Link>
      </section>

      <footer className="px-6 py-8 border-t border-white/10 text-center text-white/30 text-sm">
        Mind Protocol — La fin des complications avec l&apos;IA
      </footer>
    </main>
  );
}
