# Mind Protocol Design System

**Version:** 1.0
**Status:** Active Standard
**Last Updated:** 2025-11-18

---

## Color Palette

### Background Colors

```css
--bg-primary: #0A0B0D       /* Main background (dark) */
--bg-secondary: #0a0a0f     /* Card backgrounds */
--bg-overlay: #0a0a0f/95    /* Overlays with 95% opacity */
```

### Text Colors

```css
--text-primary: #ffffff     /* Primary headings */
--text-secondary: #d1d5db   /* Body text (gray-300) */
--text-muted: #9ca3af       /* Muted text (gray-400) */
--text-subtle: #6b7280      /* Very subtle (gray-500) */
```

### Border Colors

```css
--border-primary: #1f2937   /* Primary borders (gray-800) */
--border-secondary: #374151 /* Secondary borders (gray-700) */
```

### Layer Accent Colors

Based on Mind Protocol's 4-layer architecture:

```css
--layer-1-citizen: #22d3ee  /* Cyan - Individual AI citizens */
--layer-2-org: #a855f7      /* Purple - Organizations */
--layer-3-integration: #f59e0b  /* Orange - Ecosystem integrations */
--layer-4-protocol: #10b981 /* Green - Protocol layer */
```

### Semantic Colors

```css
--color-success: #10b981   /* Green (emerald-500) */
--color-warning: #f59e0b   /* Orange (amber-500) */
--color-error: #ef4444     /* Red (red-500) */
--color-info: #22d3ee      /* Cyan */
```

### Brand Gradient

```css
--brand-gradient: linear-gradient(to right, #10b981, #f59e0b, #a855f7, #22d3ee);
/* Green → Orange → Purple → Cyan */
```

---

## Typography

### Font Families

```css
--font-sans: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Courier New', Courier, monospace;
```

**Note:** No custom fonts required - using system defaults for performance.

### Font Sizes

```css
--text-xs: 0.75rem     /* 12px */
--text-sm: 0.875rem    /* 14px */
--text-base: 1rem      /* 16px */
--text-lg: 1.125rem    /* 18px */
--text-xl: 1.25rem     /* 20px */
--text-2xl: 1.5rem     /* 24px */
--text-3xl: 1.875rem   /* 30px */
--text-4xl: 2.25rem    /* 36px */
--text-5xl: 3rem       /* 48px */
--text-6xl: 3.75rem    /* 60px */
--text-7xl: 4.5rem     /* 72px */
```

### Font Weights

```css
--font-light: 300
--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700
```

---

## Components

### Headers (Sticky Navigation)

```tsx
<header className="sticky top-0 z-50 bg-[#0A0B0D]/95 backdrop-blur-lg border-b border-gray-800">
  <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
    {/* Logo */}
    <div className="text-2xl font-bold bg-gradient-to-r from-[#10b981] via-[#f59e0b] via-[#a855f7] to-[#22d3ee] bg-clip-text text-transparent">
      MIND PROTOCOL
    </div>
    {/* Navigation */}
  </div>
</header>
```

**Properties:**
- Sticky positioning (`sticky top-0 z-50`)
- Semi-transparent background with blur (`bg-[#0A0B0D]/95 backdrop-blur-lg`)
- Bottom border (`border-b border-gray-800`)
- Brand gradient logo text

---

### Cards

**Standard Card:**
```tsx
<div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg p-6 shadow-lg">
  {/* Content */}
</div>
```

**Accent Card (with colored border):**
```tsx
<div className="bg-[#0a0a0f]/95 backdrop-blur-xl border-l-4 border-[#22d3ee] rounded-r-lg p-5 shadow-[0_0_40px_rgba(34,211,238,0.5)]">
  <div className="absolute -left-4 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#22d3ee] animate-pulse"></div>
  {/* Content */}
</div>
```

**Properties:**
- Semi-transparent dark background (`bg-[#0a0a0f]/95`)
- Backdrop blur effect (`backdrop-blur-xl`)
- Subtle border (`border border-gray-800`)
- Optional colored accent border
- Optional glow shadow for accent cards

---

### Buttons

**Primary Button:**
```tsx
<button className="px-4 py-2 bg-[#22d3ee] text-[#0A0B0D] font-semibold rounded-md hover:bg-[#06b6d4] transition-colors">
  Click Me
</button>
```

**Secondary Button:**
```tsx
<button className="px-4 py-2 bg-transparent border border-gray-700 text-gray-300 font-medium rounded-md hover:bg-gray-800 hover:border-gray-600 transition-colors">
  Cancel
</button>
```

---

### Links

**Standard Link:**
```tsx
<a href="/path" className="text-[#6FE7E2] hover:underline">
  Link Text
</a>
```

**Navigation Link:**
```tsx
<a href="/path" className="text-sm text-[#6FE7E2] hover:underline">
  Navigation
</a>
```

**Properties:**
- Cyan color (`text-[#6FE7E2]`)
- Underline on hover
- Small text for navigation (`text-sm`)

---

### Forms

**Input Field:**
```tsx
<input
  type="text"
  className="w-full px-3 py-2 bg-[#0a0a0f] border border-gray-700 rounded-md text-gray-300 focus:ring-2 focus:ring-[#22d3ee] focus:border-transparent"
  placeholder="Enter text..."
/>
```

**Select Dropdown:**
```tsx
<select className="w-full px-3 py-2 bg-[#0a0a0f] border border-gray-700 rounded-md text-gray-300 focus:ring-2 focus:ring-[#22d3ee]">
  <option>Option 1</option>
</select>
```

**Properties:**
- Dark background (`bg-[#0a0a0f]`)
- Gray border (`border-gray-700`)
- Light text (`text-gray-300`)
- Cyan focus ring (`focus:ring-[#22d3ee]`)

---

### Badges

**Node Type Badge:**
```tsx
<span className="px-3 py-1 rounded-full bg-[#a855f7]/20 text-[#a855f7] text-sm font-medium border border-[#a855f7]/40">
  PATTERN
</span>
```

**Status Badge:**
```tsx
<span className="px-2 py-1 rounded text-xs font-medium bg-[#10b981]/20 text-[#10b981] border border-[#10b981]/40">
  Active
</span>
```

**Properties:**
- Semi-transparent background (color + `/20` opacity)
- Colored text matching background
- Subtle border (color + `/40` opacity)
- Rounded corners

---

### Modal / Detail Panel

```tsx
{/* Backdrop */}
<div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
  {/* Panel */}
  <div className="bg-[#0a0a0f] border border-gray-800 rounded-lg shadow-2xl max-w-2xl w-full p-6">
    {/* Header */}
    <div className="flex items-start justify-between mb-4">
      <h3 className="text-2xl font-bold text-white">Title</h3>
      <button className="text-gray-400 hover:text-white text-2xl">×</button>
    </div>
    {/* Content */}
  </div>
</div>
```

**Properties:**
- Dark backdrop with blur (`bg-black/60 backdrop-blur-sm`)
- Dark panel (`bg-[#0a0a0f]`)
- Centered positioning
- Shadow for depth

---

## Spacing Scale

```css
--spacing-1: 0.25rem   /* 4px */
--spacing-2: 0.5rem    /* 8px */
--spacing-3: 0.75rem   /* 12px */
--spacing-4: 1rem      /* 16px */
--spacing-5: 1.25rem   /* 20px */
--spacing-6: 1.5rem    /* 24px */
--spacing-8: 2rem      /* 32px */
--spacing-10: 2.5rem   /* 40px */
--spacing-12: 3rem     /* 48px */
--spacing-16: 4rem     /* 64px */
--spacing-20: 5rem     /* 80px */
--spacing-24: 6rem     /* 96px */
```

---

## Border Radius

```css
--radius-sm: 0.125rem  /* 2px */
--radius-md: 0.375rem  /* 6px */
--radius-lg: 0.5rem    /* 8px */
--radius-xl: 0.75rem   /* 12px */
--radius-2xl: 1rem     /* 16px */
--radius-full: 9999px  /* Perfect circle */
```

---

## Shadows

```css
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05)
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1)
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1)
--shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1)
--shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25)
```

**Glow Shadows (for accent elements):**
```css
--glow-cyan: 0 0 40px rgba(34, 211, 238, 0.5)
--glow-purple: 0 0 40px rgba(168, 85, 247, 0.5)
--glow-orange: 0 0 40px rgba(245, 158, 11, 0.5)
--glow-green: 0 0 40px rgba(16, 185, 129, 0.5)
```

---

## Animation

### Pulse (for status indicators)

```tsx
<div className="w-3 h-3 rounded-full bg-[#22d3ee] animate-pulse"></div>
```

### Transitions

**Standard transition:**
```css
transition-colors
transition-all
```

**Duration:** 150ms (Tailwind default)

---

## Layout Constraints

### Max Width

```css
--max-width-prose: 65ch      /* Text content */
--max-width-container: 80rem /* 1280px - Main container */
--max-width-wide: 90rem      /* 1440px - Wide layouts */
```

### Container

```tsx
<div className="max-w-7xl mx-auto px-6">
  {/* Content */}
</div>
```

**Properties:**
- Max width: 80rem (1280px)
- Centered with `mx-auto`
- Horizontal padding: 1.5rem (24px)

---

## Accessibility

### Focus States

All interactive elements must have visible focus states:

```tsx
focus:ring-2 focus:ring-[#22d3ee] focus:outline-none
```

### Color Contrast

Minimum contrast ratios (WCAG AA):
- **Normal text:** 4.5:1
- **Large text (18px+):** 3:1
- **UI components:** 3:1

**Verified combinations:**
- ✅ `text-white` on `bg-[#0A0B0D]` → 18.5:1
- ✅ `text-gray-300` on `bg-[#0A0B0D]` → 12.6:1
- ✅ `text-[#22d3ee]` on `bg-[#0A0B0D]` → 8.2:1

---

## Usage Examples

### Page Template

```tsx
export default function Page() {
  return (
    <div className="min-h-screen bg-[#0A0B0D] text-gray-300">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#0A0B0D]/95 backdrop-blur-lg border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-2xl font-bold text-white">Page Title</h1>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Section Title</h2>
          <p className="text-gray-300">Content goes here...</p>
        </div>
      </main>
    </div>
  );
}
```

---

## Migration Notes

### From Venice Theme (Light) to Mind Protocol Theme (Dark)

**Background:**
- ❌ `bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50`
- ✅ `bg-[#0A0B0D]`

**Text:**
- ❌ `text-amber-900`, `text-amber-700`
- ✅ `text-white`, `text-gray-300`

**Cards:**
- ❌ `bg-white/90 backdrop-blur-sm border-2 border-amber-200`
- ✅ `bg-[#0a0a0f]/95 backdrop-blur-xl border border-gray-800`

**Inputs:**
- ❌ `border-amber-300 focus:ring-amber-500`
- ✅ `border-gray-700 focus:ring-[#22d3ee]`

**Fonts:**
- ❌ `font-[family-name:var(--font-cinzel)]`, `font-[family-name:var(--font-crimson-text)]`
- ✅ System fonts (no custom fonts needed)

---

## Document Status

**Version:** 1.0
**Status:** Active Standard
**Last Updated:** 2025-11-18
**Next Review:** 2026-01-18

**Changes from previous designs:**
- Established dark theme as standard
- Removed custom fonts (Venice: Cinzel/Crimson Text)
- Standardized on 4-layer accent colors
- Defined component patterns for consistency

---

**Design System Owner:** Mind Protocol Foundation
**Questions:** See `/consciousness/CLAUDE.md` for team contacts
