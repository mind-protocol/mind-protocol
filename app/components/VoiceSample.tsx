'use client';

import { useState } from 'react';

interface VoiceSampleProps {
  citizenName: string;
}

export default function VoiceSample({ citizenName }: VoiceSampleProps) {
  const [clicked, setClicked] = useState(false);

  return (
    <button
      onClick={() => setClicked(!clicked)}
      className="bg-[#1a1a3e] rounded-full px-4 py-2 border border-white/10 hover:border-[#a78bfa]/40 transition flex items-center gap-2 text-sm"
    >
      {!clicked ? (
        <>
          <span className="text-[#a78bfa]">▶</span>
          <span className="text-white/70">Écoute ma voix</span>
        </>
      ) : (
        <span className="text-white/50 text-xs">
          La voix de {citizenName} arrive bientôt — powered by ElevenLabs
        </span>
      )}
    </button>
  );
}
