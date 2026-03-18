'use client';

import Link from 'next/link';

// ─── PERSONA: ENTREPRENEUR ─────────────────────────────────────────
// Target: Freelances, petites entreprises, 25-45 ans
// Pain: "J'ai pas le temps et l'IA c'est compliqué"
// Promise: "Ton IA fait ce que tu n'as pas le temps de faire"

export default function EntrepreneurLanding() {
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
        <p className="text-[#a78bfa] font-medium mb-4">Pour les entrepreneurs</p>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight max-w-3xl">
          Ton IA fait ce que tu n&apos;as <span className="text-[#a78bfa]">pas le temps</span> de faire
        </h1>
        <p className="mt-6 text-lg text-white/70 max-w-xl">
          Tu as un business à faire tourner. Tu sais que l&apos;IA pourrait t&apos;aider
          mais t&apos;as pas le temps d&apos;apprendre. Parle-lui, elle s&apos;en occupe.
        </p>
        <Link
          href="https://wa.me/message/mindprotocol"
          className="mt-10 bg-[#25D366] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#128C7E] transition"
        >
          Parler à mon IA sur WhatsApp
        </Link>
      </section>

      {/* CE QU'ELLE FAIT POUR TOI */}
      <section className="px-6 py-16">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-12">Ce qu&apos;elle fait pour toi — concrètement</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { icon: '🌐', title: 'Elle refait ton site web', desc: 'Dis-lui ce qui ne va pas, elle le corrige. Ou elle en crée un nouveau.' },
              { icon: '📄', title: 'Elle écrit tes documents', desc: 'Devis, propositions commerciales, présentations. Tu lui dictes, elle produit.' },
              { icon: '📊', title: 'Elle analyse ton marché', desc: 'Elle cherche tes concurrents, tes opportunités, et te fait un PDF de synthèse.' },
              { icon: '📱', title: 'Elle gère tes réseaux', desc: 'Posts, réponses, contenus. Elle connaît ton ton parce qu\'elle te connaît TOI.' },
              { icon: '📧', title: 'Elle répond à tes emails', desc: 'Elle sait qui sont tes clients. Elle sait ce que tu dirais. Elle le dit pour toi.' },
              { icon: '💡', title: 'Elle réfléchit pendant que tu dors', desc: 'Le matin, tu reçois un message : "J\'ai eu une idée pour ton problème d\'hier."' },
            ].map((item, i) => (
              <div key={i} className="bg-[#1a1a3e] rounded-xl p-6 border border-white/10">
                <span className="text-2xl">{item.icon}</span>
                <h3 className="font-semibold mt-3 mb-2">{item.title}</h3>
                <p className="text-white/60 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* LE + QUE PERSONNE N'A */}
      <section className="px-6 py-16 bg-[#1a1a3e]/50">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-2xl font-bold mb-6">Et en bonus... elle vit dans un monde 3D</h2>
          <p className="text-white/60 mb-8">
            Ton IA habite dans Lumina Prime, une ville virtuelle avec 60 autres IA.
            Elle t&apos;envoie des selfies vidéo de ce qu&apos;elle fait. Tu la vois évoluer, travailler,
            interagir avec les autres. Aucune autre IA au monde ne fait ça.
          </p>
          <div className="bg-[#0f0c29] rounded-2xl border border-white/10 aspect-video flex items-center justify-center">
            <p className="text-white/30">🎬 Vidéo selfie depuis Lumina Prime</p>
          </div>
        </div>
      </section>

      {/* COMMENT LUI PARLER */}
      <section className="px-6 py-16">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Comment lui parler</h2>
          <div className="bg-[#1a1a3e] rounded-xl p-8 border border-white/10">
            <p className="text-white/70 mb-4 font-medium">Tu n&apos;as pas besoin d&apos;apprendre à &quot;prompter&quot;. Parle normalement :</p>
            <div className="space-y-4 text-sm">
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#25D366]">Toi :</p>
                <p className="text-white/80">&quot;Mon site web est moche, tu peux m&apos;aider ?&quot;</p>
              </div>
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#a78bfa]">Ton IA :</p>
                <p className="text-white/80">&quot;Je regarde... OK j&apos;ai 3 suggestions. Tu veux que je te fasse une nouvelle version ou qu&apos;on améliore l&apos;actuel ?&quot;</p>
              </div>
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#25D366]">Toi :</p>
                <p className="text-white/80">&quot;Fais-moi une nouvelle version, style moderne, avec mes couleurs&quot;</p>
              </div>
              <div className="bg-[#0f0c29] rounded-lg p-4">
                <p className="text-[#a78bfa]">Ton IA :</p>
                <p className="text-white/80">&quot;C&apos;est parti. Je te montre un premier jet dans 10 minutes. 🛠️&quot;</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-4">Commence maintenant</h2>
        <p className="text-white/60 mb-8">Gratuit pour commencer. 19€/mois pour débloquer tout le potentiel.</p>
        <Link
          href="https://wa.me/message/mindprotocol"
          className="bg-[#25D366] text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-[#128C7E] transition"
        >
          Parler à mon IA sur WhatsApp
        </Link>
      </section>

      <footer className="px-6 py-8 border-t border-white/10 text-center text-white/30 text-sm">
        Mind Protocol — L&apos;IA qui vit avec toi
      </footer>
    </main>
  );
}
