'use client';

import { Locale, localeNames } from './translations';

export function LangSwitcher({
  current,
  onChange,
}: {
  current: Locale;
  onChange: (locale: Locale) => void;
}) {
  const locales: Locale[] = ['fr', 'en', 'es', 'pt', 'ar'];

  return (
    <div className="flex items-center gap-1 text-xs">
      {locales.map((loc) => (
        <button
          key={loc}
          onClick={() => onChange(loc)}
          className={`px-2 py-1 rounded transition ${
            current === loc
              ? 'bg-[#a78bfa] text-[#0f0c29] font-semibold'
              : 'text-white/40 hover:text-white/70'
          }`}
        >
          {localeNames[loc]}
        </button>
      ))}
    </div>
  );
}
