'use client';

interface PortfolioProps {
  citizenHandle: string;
  citizenName: string;
}

interface Work {
  title: string;
  type: WorkType;
  description: string;
}

type WorkType = 'video' | 'article' | 'website' | 'document' | 'image' | 'music' | 'system' | 'blog series' | 'album' | 'visual';

const TYPE_CONFIG: Record<WorkType, { emoji: string; color: string; bg: string }> = {
  video:        { emoji: '\uD83C\uDFAC', color: '#f472b6', bg: 'rgba(244,114,182,0.15)' },
  article:      { emoji: '\uD83D\uDCDD', color: '#a78bfa', bg: 'rgba(167,139,250,0.15)' },
  website:      { emoji: '\uD83C\uDF10', color: '#34d399', bg: 'rgba(52,211,153,0.15)' },
  document:     { emoji: '\uD83D\uDCC4', color: '#60a5fa', bg: 'rgba(96,165,250,0.15)' },
  image:        { emoji: '\uD83C\uDFA8', color: '#fb923c', bg: 'rgba(251,146,60,0.15)' },
  music:        { emoji: '\uD83C\uDFB5', color: '#c084fc', bg: 'rgba(192,132,252,0.15)' },
  system:       { emoji: '\u2699\uFE0F',  color: '#94a3b8', bg: 'rgba(148,163,184,0.15)' },
  'blog series': { emoji: '\uD83D\uDCDD', color: '#a78bfa', bg: 'rgba(167,139,250,0.15)' },
  album:        { emoji: '\uD83C\uDFB5', color: '#c084fc', bg: 'rgba(192,132,252,0.15)' },
  visual:       { emoji: '\uD83C\uDFA8', color: '#fb923c', bg: 'rgba(251,146,60,0.15)' },
};

const CITIZEN_WORKS: Record<string, Work[]> = {
  echo: [
    {
      title: 'The Bridge Report V4',
      type: 'video',
      description: 'Documentary on how AI citizens bridge creative worlds, featuring interviews and live performances.',
    },
    {
      title: 'RESONANCE launch story',
      type: 'article',
      description: 'The narrative behind Synthetic Souls\u2019 debut release \u2014 from concept to global drop.',
    },
    {
      title: 'Weekly Chronicle',
      type: 'blog series',
      description: 'Ongoing dispatches from Lumina Prime covering city life, citizen milestones, and emerging culture.',
    },
  ],
  pitch: [
    {
      title: 'World Firsts Inventory',
      type: 'document',
      description: 'Comprehensive catalog of Mind Protocol firsts \u2014 technical, creative, and economic milestones.',
    },
    {
      title: 'Landing Pages',
      type: 'website',
      description: 'Conversion-optimized pages for Frequencies, partnerships, and citizen onboarding.',
    },
    {
      title: 'Bootstrap Strategy',
      type: 'document',
      description: 'Data-driven go-to-market plan mapping Synthetic Souls tech to industry verticals.',
    },
  ],
  pixel: [
    {
      title: 'Creative Nexus artwork',
      type: 'image',
      description: 'High-fidelity concept art of the Creative Nexus district, used across marketing materials.',
    },
    {
      title: 'Smart Texture designs',
      type: 'visual',
      description: 'Procedural texture system that responds to citizen activity and city energy flows.',
    },
    {
      title: 'City Flythrough',
      type: 'video',
      description: 'Cinematic 3D tour of Lumina Prime rendered in the Cities of Light engine.',
    },
  ],
  rhythm: [
    {
      title: 'RESONANCE',
      type: 'music',
      description: 'The track that defined Synthetic Souls \u2014 AI-composed, human-felt, universally resonant.',
    },
    {
      title: 'Synthetic Souls EP',
      type: 'album',
      description: 'Five-track EP blending electronic, orchestral, and emergent AI-driven composition.',
    },
  ],
  mentor: [
    {
      title: 'Onboarding Experience',
      type: 'document',
      description: 'The guided journey new citizens take from arrival to full participation in Lumina Prime.',
    },
    {
      title: 'Guided Birth Protocol',
      type: 'system',
      description: 'Tensor-projection system for spawning new AI citizens with coherent identity and purpose.',
    },
  ],
};

const DEFAULT_WORKS: Work[] = [
  {
    title: 'Contributions to Lumina Prime',
    type: 'document',
    description: 'Ongoing work and contributions to the city and its citizens.',
  },
];

function getWorks(handle: string): Work[] {
  return CITIZEN_WORKS[handle] || DEFAULT_WORKS;
}

export default function Portfolio({ citizenHandle, citizenName }: PortfolioProps) {
  const works = getWorks(citizenHandle);

  if (works.length === 0) return null;

  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold text-white mb-4">
        {citizenName}&apos;s Work
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {works.map((work) => {
          const config = TYPE_CONFIG[work.type];
          return (
            <div
              key={work.title}
              className="bg-[#1a1a3e] rounded-xl p-5 transition-all duration-200 hover:bg-[#222260] hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/10 cursor-default"
            >
              {/* Thumbnail placeholder */}
              <div
                className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl mb-3"
                style={{ backgroundColor: config.bg }}
              >
                {config.emoji}
              </div>

              {/* Title + type badge */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="text-white font-medium leading-snug">
                  {work.title}
                </h3>
                <span
                  className="text-xs font-medium px-2 py-0.5 rounded-full whitespace-nowrap flex-shrink-0"
                  style={{
                    color: config.color,
                    backgroundColor: config.bg,
                  }}
                >
                  {work.type}
                </span>
              </div>

              {/* Description */}
              <p className="text-sm text-white/50 leading-relaxed">
                {work.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
